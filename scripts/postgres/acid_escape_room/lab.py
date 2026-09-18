#!/usr/bin/env python3
"""ACID Escape Room: deliberately broken workflows vs database-backed fixes.

Requires a disposable PostgreSQL database named acid_lab and psycopg2.
Each worker is a separate spawned Python process with its own DB connection.
"""

import argparse
import multiprocessing as mp
import os
import time
from pathlib import Path

import psycopg2

DEFAULT_DSN = "postgresql://acid:local_only_secret@127.0.0.1:55432/acid_lab"
SCHEMA = "acid_escape_room"
PROPERTIES = ("atomicity", "consistency", "isolation", "durability")
CRASH_EXIT_CODE = 17
MAX_WORKERS = 16

DDL = """
CREATE SCHEMA IF NOT EXISTS acid_escape_room;
CREATE TABLE IF NOT EXISTS acid_escape_room.seats (
    seat_id integer PRIMARY KEY, label text NOT NULL
);
CREATE TABLE IF NOT EXISTS acid_escape_room.payments (
    worker_id integer PRIMARY KEY,
    seat_id integer NOT NULL REFERENCES acid_escape_room.seats(seat_id),
    cents integer NOT NULL CHECK (cents > 0)
);
CREATE TABLE IF NOT EXISTS acid_escape_room.atomic_bookings (
    worker_id integer PRIMARY KEY,
    seat_id integer NOT NULL REFERENCES acid_escape_room.seats(seat_id)
);
CREATE TABLE IF NOT EXISTS acid_escape_room.bookings (
    booking_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    worker_id integer NOT NULL,
    seat_id integer NOT NULL REFERENCES acid_escape_room.seats(seat_id)
);
CREATE TABLE IF NOT EXISTS acid_escape_room.doctors (
    worker_id integer PRIMARY KEY, on_call boolean NOT NULL
);
CREATE TABLE IF NOT EXISTS acid_escape_room.receipts (
    mode text NOT NULL CHECK (mode IN ('bad', 'good')),
    worker_id integer NOT NULL,
    PRIMARY KEY (mode, worker_id)
);
"""


class InjectedFailure(Exception):
    """An application exception, deliberately raised between two writes."""


def require(condition, message):
    """Unlike assert, this also runs with python -O."""
    if not condition:
        raise AssertionError(message)


def validate_workers(workers):
    if not 2 <= workers <= MAX_WORKERS:
        raise ValueError("--workers must be between 2 and %s" % MAX_WORKERS)


def connect(dsn):
    return psycopg2.connect(
        dsn,
        connect_timeout=5,
        application_name="acid_escape_room",
        options=("-c statement_timeout=15000 -c lock_timeout=10000 "
                 "-c idle_in_transaction_session_timeout=40000"),
    )


def guard_database(connection):
    with connection.cursor() as cursor:
        cursor.execute("SELECT current_database()")
        database = cursor.fetchone()[0]
    require(database == "acid_lab",
            "Refusing to change database %r: use an isolated database named acid_lab" % database)
    connection.rollback()


def seed(dsn, workers):
    validate_workers(workers)
    connection = connect(dsn)
    try:
        guard_database(connection)
        with connection.cursor() as cursor:
            cursor.execute(DDL)
            cursor.execute("DROP INDEX IF EXISTS acid_escape_room.one_booking_per_seat")
            cursor.execute("""TRUNCATE acid_escape_room.payments,
                acid_escape_room.atomic_bookings, acid_escape_room.bookings,
                acid_escape_room.doctors, acid_escape_room.receipts,
                acid_escape_room.seats RESTART IDENTITY""")
            cursor.execute("""INSERT INTO acid_escape_room.seats(seat_id, label)
                SELECT n, 'SEAT-' || n FROM generate_series(1, %s) AS n""", (workers,))
            cursor.execute("""INSERT INTO acid_escape_room.doctors(worker_id, on_call)
                SELECT n, TRUE FROM generate_series(1, %s) AS n""", (workers,))
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    print("Seeded %s seats and %s on-call doctors; other lab tables empty." % (workers, workers))


def prepare(dsn, property_name, mode, workers):
    connection = connect(dsn)
    try:
        guard_database(connection)
        with connection.cursor() as cursor:
            cursor.execute("SELECT count(*) FROM acid_escape_room.seats")
            count = cursor.fetchone()[0]
            require(count >= workers, "Only %s seats seeded; rerun seed --workers %s" % (count, workers))
            if property_name == "atomicity":
                cursor.execute("TRUNCATE acid_escape_room.payments, acid_escape_room.atomic_bookings")
            elif property_name == "consistency":
                cursor.execute("DROP INDEX IF EXISTS acid_escape_room.one_booking_per_seat")
                cursor.execute("TRUNCATE acid_escape_room.bookings RESTART IDENTITY")
                if mode == "good":
                    cursor.execute("""CREATE UNIQUE INDEX one_booking_per_seat
                        ON acid_escape_room.bookings(seat_id)""")
            elif property_name == "isolation":
                cursor.execute("TRUNCATE acid_escape_room.doctors")
                cursor.execute("""INSERT INTO acid_escape_room.doctors(worker_id, on_call)
                    SELECT n, TRUE FROM generate_series(1, %s) AS n""", (workers,))
            elif property_name == "durability":
                cursor.execute("DELETE FROM acid_escape_room.receipts WHERE mode = %s", (mode,))
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def atomicity_worker(connection, mode, worker_id, barrier):
    barrier.wait(timeout=25)
    with connection.cursor() as cursor:
        cursor.execute("""INSERT INTO acid_escape_room.payments(worker_id, seat_id, cents)
            VALUES (%s, %s, 2500)""", (worker_id, worker_id))
        if mode == "bad":
            connection.commit()  # BUG: payment is committed before booking starts.
        try:
            if worker_id % 2 == 0:
                raise InjectedFailure("booking service failed after payment")
            cursor.execute("""INSERT INTO acid_escape_room.atomic_bookings(worker_id, seat_id)
                VALUES (%s, %s)""", (worker_id, worker_id))
            connection.commit()
            return {"action": "booked"}
        except InjectedFailure:
            connection.rollback()  # Cannot undo the already committed BAD payment.
            return {"action": "injected_failure"}


def consistency_worker(connection, mode, worker_id, barrier):
    connection.set_session(isolation_level="READ COMMITTED")
    with connection.cursor() as cursor:
        cursor.execute("SELECT count(*) FROM acid_escape_room.bookings WHERE seat_id = 1")
        require(cursor.fetchone()[0] == 0, "Fixture was not reset")
        barrier.wait(timeout=25)  # Every buyer observes the same free seat.
        try:
            cursor.execute("""INSERT INTO acid_escape_room.bookings(worker_id, seat_id)
                VALUES (%s, 1)""", (worker_id,))
            connection.commit()
            return {"action": "booked"}
        except psycopg2.Error as error:
            connection.rollback()
            if mode == "good" and error.pgcode == "23505":
                return {"action": "rejected", "sqlstate": error.pgcode}
            raise


def isolation_worker(connection, mode, worker_id, barrier, workers):
    connection.set_session(isolation_level=(
        "REPEATABLE READ" if mode == "bad" else "SERIALIZABLE"))
    retries = 0
    for attempt in range(workers * 8 + 10):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT count(*) FROM acid_escape_room.doctors WHERE on_call")
                active = cursor.fetchone()[0]
                if attempt == 0:
                    barrier.wait(timeout=25)  # All see the same initial on-call count.
                if active > 1:
                    cursor.execute("""UPDATE acid_escape_room.doctors SET on_call = FALSE
                        WHERE worker_id = %s AND on_call""", (worker_id,))
                    require(cursor.rowcount == 1, "Unexpected doctor fixture")
                    action = "stepped_down"
                else:
                    action = "stayed_on_call"
            connection.commit()
            return {"action": action, "retries": retries}
        except psycopg2.Error as error:
            connection.rollback()
            if mode != "good" or error.pgcode != "40001":
                raise
            retries += 1  # Retry the ENTIRE read/check/update transaction.
            time.sleep(min(0.025 * retries, 0.2) + worker_id * 0.002)
    raise RuntimeError("Serializable retry budget exhausted for worker %s" % worker_id)


def durability_worker(connection, mode, worker_id, barrier, sender):
    barrier.wait(timeout=25)
    with connection.cursor() as cursor:
        if mode == "good":
            cursor.execute("SET LOCAL synchronous_commit = on")
        cursor.execute("""INSERT INTO acid_escape_room.receipts(mode, worker_id)
            VALUES (%s, %s)""", (mode, worker_id))
    if mode == "good":
        connection.commit()  # COMMIT response arrives before acknowledgement.
        sender.send({"action": "ack_after_commit"})
    else:
        sender.send({"action": "ack_before_commit"})  # BUG: lie to the caller.
    os._exit(CRASH_EXIT_CODE)  # Abrupt *client* crash; not a server/power failure.


def worker_entry(dsn, property_name, mode, worker_id, workers, barrier, sender):
    connection = None
    try:
        connection = connect(dsn)  # Never share a psycopg2 connection across processes.
        if property_name == "atomicity":
            outcome = atomicity_worker(connection, mode, worker_id, barrier)
        elif property_name == "consistency":
            outcome = consistency_worker(connection, mode, worker_id, barrier)
        elif property_name == "isolation":
            outcome = isolation_worker(connection, mode, worker_id, barrier, workers)
        else:
            durability_worker(connection, mode, worker_id, barrier, sender)
            raise AssertionError("Crash injection returned unexpectedly")
        sender.send(outcome)
    except Exception as error:
        if connection is not None:
            connection.rollback()
        sender.send({"action": "error", "detail": repr(error),
                     "sqlstate": getattr(error, "pgcode", None)})
        raise
    finally:
        if connection is not None:
            connection.close()
        sender.close()


def spawn_workers(dsn, property_name, mode, workers):
    context = mp.get_context("spawn")
    barrier = context.Barrier(workers, timeout=25)
    jobs = []
    try:
        for worker_id in range(1, workers + 1):
            receiver, sender = context.Pipe(duplex=False)
            process = context.Process(
                target=worker_entry,
                args=(dsn, property_name, mode, worker_id, workers, barrier, sender),
                name="acid-%s-%s-%s" % (property_name, mode, worker_id),
            )
            process.start()
            sender.close()
            jobs.append((worker_id, process, receiver))
        deadline = time.monotonic() + 75
        for _, process, _ in jobs:
            process.join(max(0, deadline - time.monotonic()))
        hanging = [process for _, process, _ in jobs if process.is_alive()]
        if hanging:
            for process in hanging:
                process.terminate()
            for process in hanging:
                process.join(timeout=2)
                if process.is_alive():
                    process.kill()
                    process.join(timeout=2)
            raise TimeoutError("Workers exceeded 75-second watchdog: %s" %
                               [process.name for process in hanging])
        results = []
        expected_exit = CRASH_EXIT_CODE if property_name == "durability" else 0
        for worker_id, process, receiver in jobs:
            require(process.exitcode == expected_exit,
                    "Worker %s exited %s (expected %s)" %
                    (worker_id, process.exitcode, expected_exit))
            require(receiver.poll(3), "Worker %s sent no result" % worker_id)
            result = receiver.recv()
            require(result["action"] != "error", "Worker %s: %s" % (worker_id, result))
            result["worker"] = worker_id
            results.append(result)
        return results
    finally:
        for _, process, receiver in jobs:
            if process.is_alive():
                process.terminate()
                process.join(timeout=2)
                if process.is_alive():
                    process.kill()
                    process.join(timeout=2)
            receiver.close()


def query_one(connection, sql, params=()):
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        return cursor.fetchone()[0]


def verify_receipts(connection, workers):
    with connection.cursor() as cursor:
        cursor.execute("SELECT mode, worker_id FROM acid_escape_room.receipts")
        rows = cursor.fetchall()
    good = {worker_id for mode, worker_id in rows if mode == "good"}
    bad = {worker_id for mode, worker_id in rows if mode == "bad"}
    require(good == set(range(1, workers + 1)),
            "Committed acknowledgements missing: %s" % sorted(good))
    require(not bad, "Uncommitted BAD receipts unexpectedly visible: %s" % sorted(bad))
    return {"good_persisted": len(good), "bad_persisted": len(bad)}


def check_round(dsn, property_name, mode, workers, outcomes):
    connection = connect(dsn)
    try:
        if property_name == "atomicity":
            payments = query_one(connection, "SELECT count(*) FROM acid_escape_room.payments")
            bookings = query_one(connection, "SELECT count(*) FROM acid_escape_room.atomic_bookings")
            orphans = query_one(connection, """SELECT count(*) FROM acid_escape_room.payments p
                LEFT JOIN acid_escape_room.atomic_bookings b USING (worker_id)
                WHERE b.worker_id IS NULL""")
            successes = workers // 2
            expected_payments = workers if mode == "bad" else successes
            require((payments, bookings, orphans) ==
                    (expected_payments, successes, expected_payments - successes),
                    "Atomicity counts unexpected: %s" % ((payments, bookings, orphans),))
            require(sum(o["action"] == "injected_failure" for o in outcomes) ==
                    workers - successes, "Failure injection was not exercised")
            return {"payments": payments, "bookings": bookings, "orphan_payments": orphans}
        if property_name == "consistency":
            bookings = query_one(connection, "SELECT count(*) FROM acid_escape_room.bookings")
            expected = workers if mode == "bad" else 1
            require(bookings == expected, "Expected %s bookings, got %s" % (expected, bookings))
            if mode == "good":
                require(sum(o["action"] == "rejected" and o.get("sqlstate") == "23505"
                            for o in outcomes) == workers - 1,
                        "Expected unique-key failures for all losing buyers")
            return {"bookings_for_one_seat": bookings, "unique_constraint": mode == "good"}
        if property_name == "isolation":
            on_call = query_one(connection, """SELECT count(*)
                FROM acid_escape_room.doctors WHERE on_call""")
            retries = sum(o["retries"] for o in outcomes)
            expected = 0 if mode == "bad" else 1
            require(on_call == expected, "Expected %s on-call doctor(s), got %s" %
                    (expected, on_call))
            if mode == "good":
                require(retries > 0, "Expected at least one observed SQLSTATE 40001 retry")
            return {"doctors_on_call": on_call, "serialization_retries": retries}
        expected_action = "ack_before_commit" if mode == "bad" else "ack_after_commit"
        require(all(o["action"] == expected_action for o in outcomes),
                "Unexpected acknowledgement timing")
        count = query_one(connection,
                          "SELECT count(*) FROM acid_escape_room.receipts WHERE mode = %s", (mode,))
        require(count == (0 if mode == "bad" else workers),
                "Durability outcome unexpected: persisted %s" % count)
        return {"acknowledged": len(outcomes), "persisted": count,
                "client_exit_code": CRASH_EXIT_CODE}
    finally:
        connection.close()


def describe_server(dsn):
    connection = connect(dsn)
    try:
        guard_database(connection)
        with connection.cursor() as cursor:
            cursor.execute("""SELECT version(), current_setting('fsync'),
                current_setting('synchronous_commit'), current_setting('default_transaction_isolation')""")
            version, fsync, sync_commit, isolation = cursor.fetchone()
        print("Server: %s" % version.splitlines()[0])
        print("Settings: fsync=%s synchronous_commit=%s default_isolation=%s" %
              (fsync, sync_commit, isolation))
        if fsync != "on":
            print("WARNING: fsync is off; do not infer power-loss durability from this lab")
    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dsn", default=os.environ.get("ACID_LAB_DSN", DEFAULT_DSN),
                        help="Disposable acid_lab connection string (or ACID_LAB_DSN)")
    commands = parser.add_subparsers(dest="command", required=True)
    seed_cmd = commands.add_parser("seed", help="Reset ONLY acid_escape_room schema data")
    seed_cmd.add_argument("--workers", type=int, default=8)
    run_cmd = commands.add_parser("run", help="Execute and assert expected BAD / GOOD results")
    run_cmd.add_argument("--property", choices=(*PROPERTIES, "all"), default="all")
    run_cmd.add_argument("--mode", choices=("bad", "good", "both"), default="both")
    run_cmd.add_argument("--workers", type=int, default=8)
    verify_cmd = commands.add_parser("verify-durability", help="Verify after DB container restart")
    verify_cmd.add_argument("--workers", type=int, default=8)
    cleanup_cmd = commands.add_parser("cleanup", help="Drop ONLY acid_escape_room schema")
    cleanup_cmd.add_argument("--yes", action="store_true", help="Confirm dropping the lab schema")
    args = parser.parse_args()
    dsn = args.dsn
    try:
        if args.command == "seed":
            seed(dsn, args.workers)
        elif args.command == "run":
            validate_workers(args.workers)
            describe_server(dsn)
            selected = PROPERTIES if args.property == "all" else (args.property,)
            modes = ("bad", "good") if args.mode == "both" else (args.mode,)
            for property_name in selected:
                for mode in modes:
                    print("\n=== %s / %s / %s processes ===" %
                          (property_name.upper(), mode.upper(), args.workers), flush=True)
                    prepare(dsn, property_name, mode, args.workers)
                    outcomes = spawn_workers(dsn, property_name, mode, args.workers)
                    for outcome in outcomes:
                        print("  worker %02d: %s" % (outcome["worker"], outcome), flush=True)
                    summary = check_round(dsn, property_name, mode, args.workers, outcomes)
                    print("PASS: expected %s scenario observed: %s" % (mode.upper(), summary),
                          flush=True)
        elif args.command == "verify-durability":
            validate_workers(args.workers)
            connection = connect(dsn)
            try:
                guard_database(connection)
                print("PASS: receipts after restart: %s" % verify_receipts(connection, args.workers))
            finally:
                connection.close()
        else:
            require(args.yes, "Add --yes to drop the disposable lab schema")
            connection = connect(dsn)
            try:
                guard_database(connection)
                with connection.cursor() as cursor:
                    cursor.execute("DROP SCHEMA IF EXISTS acid_escape_room CASCADE")
                connection.commit()
                print("Removed acid_escape_room schema only")
            finally:
                connection.close()
    except (psycopg2.Error, AssertionError, ValueError, TimeoutError) as error:
        parser.exit(1, "LAB FAILED: %s\n" % error)


if __name__ == "__main__":
    mp.freeze_support()
    main()
