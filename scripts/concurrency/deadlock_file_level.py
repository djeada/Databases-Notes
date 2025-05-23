#!/usr/bin/env python3
import sqlite3
import multiprocessing
import argparse
import os
import time

DB1 = 'db1.sqlite'
DB2 = 'db2.sqlite'


def setup_databases():
    """Create two databases with the same schema and one row each."""
    for db in (DB1, DB2):
        try:
            os.remove(db)
        except FileNotFoundError:
            pass
        conn = sqlite3.connect(db)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS test (
                id    INTEGER PRIMARY KEY,
                value TEXT
            );
        """)
        conn.execute("DELETE FROM test;")
        conn.execute("INSERT INTO test (id, value) VALUES (?, ?);", (1, 'init'))
        conn.commit()
        conn.close()
    print("Databases initialized.\n")


def worker(name, first_db, second_db, evt_first_done, evt_second_done, deadlock_mode):
    """Each worker locks first_db then second_db."""
    # very large timeout = effectively infinite; small timeout = quick exception
    busy_ms = 10 ** 9 if deadlock_mode else 100
    conn = sqlite3.connect(DB1, timeout=30, isolation_level=None)
    conn.execute(f"PRAGMA busy_timeout = {busy_ms};")
    conn.execute("ATTACH DATABASE ? AS db2;", (DB2,))
    try:
        # always start DEFERRED
        conn.execute("BEGIN DEFERRED;")
        print(f"[{name}] BEGIN DEFERRED on {first_db}")
        conn.execute(f"UPDATE {first_db}.test SET value='{name}-step1' WHERE id=1;")
        print(f"[{name}] Locked {first_db} and updated step1")
        evt_first_done.set()  # signal the other
        print(f"[{name}] Waiting for other to lock {second_db}...")
        evt_second_done.wait()
        print(f"[{name}] Now trying to update {second_db}.test (step2)")

        # attempt second update (may block or raise)
        conn.execute(f"UPDATE {second_db}.test SET value='{name}-step2' WHERE id=1;")
        conn.commit()
        print(f"[{name}] Committed both updates successfully!\n")

    except sqlite3.OperationalError as e:
        print(f"[{name}] OperationalError: {e}")
        if not deadlock_mode:
            # handle the “deadlock/busy” by rolling back and retrying immediately
            print(f"[{name}] Handling lock contention: rolling back and retrying with IMMEDIATE transaction")
            conn.rollback()
            time.sleep(0.1)
            conn.execute("BEGIN IMMEDIATE;")
            conn.execute(f"UPDATE {first_db}.test SET value='{name}-retry1' WHERE id=1;")
            conn.execute(f"UPDATE {second_db}.test SET value='{name}-retry2' WHERE id=1;")
            conn.commit()
            print(f"[{name}] Retry succeeded under IMMEDIATE mode!\n")
    finally:
        conn.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Demonstrate SQLite deadlock vs. handling"
    )
    parser.add_argument(
        '--deadlock', action='store_true',
        help='If set, simulate an indefinite deadlock (DEFERRED + infinite timeout)'
    )
    args = parser.parse_args()

    setup_databases()

    # events for sync
    e1 = multiprocessing.Event()
    e2 = multiprocessing.Event()

    # worker1 locks main then db2
    p1 = multiprocessing.Process(
        target=worker,
        args=('W1', 'main', 'db2', e1, e2, args.deadlock)
    )
    # worker2 locks db2 then main
    p2 = multiprocessing.Process(
        target=worker,
        args=('W2', 'db2', 'main', e2, e1, args.deadlock)
    )

    p1.start()
    p2.start()
    p1.join()
    p2.join()

    # show final state
    for db in (DB1, DB2):
        conn = sqlite3.connect(db)
        val = conn.execute("SELECT value FROM test WHERE id=1;").fetchone()[0]
        conn.close()
        print(f"Final {db}.test.value = {val!r}")
