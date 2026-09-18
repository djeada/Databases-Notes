# ACID Escape Room: a compliant database, a broken application

**Eight runnable labs: four ACID properties × BAD and GOOD.** Every run starts
8 independent Python **processes** by default, gives each process its own
PostgreSQL connection, coordinates the interesting interleaving with a
`multiprocessing.Barrier`, and checks final database state. The BAD runs **pass
only if their deliberately broken outcome is observed**; an unexpected result
exits nonzero. This is an application-correctness exercise, not a demonstration
of PostgreSQL violating a guarantee it made.

> Destructive teaching exercise. Only run against a disposable database named
> `acid_lab`. `seed` resets the `acid_escape_room` schema's lab tables; `cleanup
> --yes` drops that schema. The included Compose stack uses a dedicated volume
> and binds to loopback. Do not reuse it for real payments or bookings.

## 1. Setup (from the repository root)

Requires Docker with Compose v2, Python 3.9+, and `psycopg2-binary` (already
listed in `scripts/requirements.txt`). The dedicated `compose.yaml` uses
PostgreSQL 16 on **127.0.0.1:55432**, not the repository's older
`setup/start_postgres.sh` container on port 5432. It will not install system
packages or remove existing containers. Check that 55432 is unused first.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r scripts/requirements.txt
docker compose -f scripts/postgres/acid_escape_room/compose.yaml -p acid-escape-room up -d --wait
```

The script defaults to the local connection
`postgresql://acid:local_only_secret@127.0.0.1:55432/acid_lab`.
You can override it with `ACID_LAB_DSN` or a global `--dsn` placed **before**
the subcommand. For safety, it refuses to make changes unless the current
database is literally named `acid_lab`. Credentials are for loopback-only
educational use, not production.

## 2. Fill sample data

```bash
python scripts/postgres/acid_escape_room/lab.py seed --workers 8
```

`seed` creates only schema `acid_escape_room`, resets its demo tables, inserts
8 seats (`SEAT-1` ... `SEAT-8`) and 8 initially on-call doctors, and clears
payments, bookings and receipts. It also removes the optional seat-uniqueness
index so the BAD consistency round can demonstrate the missing invariant.
Re-running `seed` **destroys previous lab data**. If you want 12 concurrent
clients instead, seed and run with `--workers 12` (supported: 2–16).

## 3. Run all eight demonstrations

```bash
python scripts/postgres/acid_escape_room/lab.py run --property all --mode both --workers 8
```

Or concentrate on a single property and inspect both variants:

```bash
python scripts/postgres/acid_escape_room/lab.py run --property atomicity --mode both --workers 8
python scripts/postgres/acid_escape_room/lab.py run --property consistency --mode both --workers 8
python scripts/postgres/acid_escape_room/lab.py run --property isolation --mode both --workers 8
python scripts/postgres/acid_escape_room/lab.py run --property durability --mode both --workers 8
```

Choose `--mode bad` or `--mode good` to run just one side. The runner resets
*only that round's fixture* before each variant. Thus, the outputs for BAD and
GOOD are comparable rather than contaminated by a previous run. It prints
one outcome per worker, relevant counts, PostgreSQL version and settings, and
`PASS` only after verifying the relevant invariant or intended breakage.

| Round | BAD: intentionally broken workflow | GOOD: fix and required result |
| --- | --- | --- |
| **A · Atomicity** | Each buyer commits a payment **before** booking. Inject a booking failure for even-numbered workers. Expect 8 payments, 4 bookings and 4 paid-but-unbooked buyers. Both individual transactions are atomic; the **workflow boundary** is wrong. | Payment and booking share **one transaction**. Inject the same failures; rollback both changes. Expect 4 matching payments/bookings and **zero** orphans. A real external payment provider cannot be rolled back by PostgreSQL: use an outbox/saga and idempotent reconciliation for that case. |
| **C · Consistency** | All 8 buyers see the last seat as free, then insert separate booking IDs without any unique seat constraint. Expect **8 bookings for one seat**. The database cannot enforce a business rule that was never declared. | Create a unique index on `seat_id`; identical requests race. Expect exactly **one** booking and seven explicit `23505` rejections. App-side read-before-insert is *not* the protection. |
| **I · Isolation** | All 8 on-call doctors read that others are on call under PostgreSQL `REPEATABLE READ`, then each updates a **different** row to go off duty. Expect **zero** doctors left (write skew). A stable snapshot is not the same as serializability. | Repeat under `SERIALIZABLE`. Catch `40001`, roll back and retry the **entire read/check/update transaction**. Expect exactly **one** doctor left and at least one logged serialization retry. |
| **D · Durability** | Each process inserts a receipt, tells its caller `ACK`, then deliberately calls `os._exit(17)` **without committing**. Expect 8 misleading ACKs and **zero** persisted receipts. This is an app acknowledgement bug; the database correctly rolls back. | Each process commits with `synchronous_commit=on`, then acknowledges and crashes. Expect all **8** receipts present. Restart the database container and verify them again below. |

The consistency round is explicitly about **missing constraints**, while the
isolation round is a separate **write-skew** example that cannot be fixed just
by taking stable snapshots. These are not four mechanisms for "turning off
ACID"; the checks identify precisely where the application misused the DB.

### Deterministic concurrency and safety

The children use `spawn`, fresh connections, and a start/read barrier (not
`sleep()` as a concurrency schedule). A 25-second barrier deadline and a
75-second parent watchdog terminate/reap stuck workers. SQL statement, lock,
idle-in-transaction and connection timeouts prevent unbounded waits. A worker
that crashes unexpectedly, misses a barrier, fails to produce an expected
`23505` or `40001` outcome, or produces unexpected database state makes the
whole command fail. In the durability round, exit code **17** is expected and
verified; elsewhere exit code **0** is mandatory. The SERIALIZABLE round uses
bounded retries with backoff and will fail rather than pretend progress if
its retry budget is exhausted.

## 4. Prove the good receipts survive a server restart

Run **both durability variants** last, or run all eight as above. Then:

```bash
docker compose -f scripts/postgres/acid_escape_room/compose.yaml -p acid-escape-room restart db
docker compose -f scripts/postgres/acid_escape_room/compose.yaml -p acid-escape-room up -d --wait
python scripts/postgres/acid_escape_room/lab.py verify-durability --workers 8
```

This verifies committed receipt IDs `1..8` exist and no BAD uncommitted receipt
survived. The Compose volume persists through `restart`. This proves the
**scenario observed** (client crash and a normal DB container restart); it is
**not** a power-loss simulation or proof about arbitrary hardware. PostgreSQL
`fsync`, `synchronous_commit`, the filesystem and storage hardware determine
stronger crash/power-loss promises. The runner displays actual settings and
warns when `fsync` is off. Do not use `docker compose down -v` before this
verification: it intentionally deletes the lab's database volume.

## 5. Tests and cleanup

```bash
python -m unittest discover -s scripts/postgres/acid_escape_room/tests -v
# Run integration assertions (needs the running disposable PostgreSQL instance):
python scripts/postgres/acid_escape_room/lab.py run --property all --mode both --workers 8
# Explicitly remove just the lab schema, if desired:
python scripts/postgres/acid_escape_room/lab.py cleanup --yes
# Remove only this Compose project's container/network/volume (deletes acid_lab):
docker compose -f scripts/postgres/acid_escape_room/compose.yaml -p acid-escape-room down -v
```

If connection fails, check `docker compose ... ps` and the loopback port. If a
BAD run does not reproduce the expected failure, it is a **failed test**, not
a success; inspect per-worker errors. The PostgreSQL `SERIALIZABLE` conflict is
an expected abort-and-retry mechanism, not a sign of a broken database.

### References

- [PostgreSQL isolation and serialization anomalies](https://www.postgresql.org/docs/16/transaction-iso.html)
- [Retry the complete transaction on serialization failures](https://www.postgresql.org/docs/16/mvcc-serialization-failure-handling.html)
- [WAL, synchronous commit and durability settings](https://www.postgresql.org/docs/16/runtime-config-wal.html)
