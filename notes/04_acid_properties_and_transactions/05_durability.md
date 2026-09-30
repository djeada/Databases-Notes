# Durability

Durability means that a successfully committed transaction survives the failures covered by the database's configuration and storage assumptions. It is the reason an application can rely on a successful commit acknowledgment after a crash. It does not promise survival after every durable copy is destroyed.

## Follow an acknowledged order

The bookstore commits order 104 and tells Bob that the order was accepted. If the database process crashes immediately afterward, Bob expects the order to exist when service returns. Durability is the guarantee that connects that acknowledgement to recovery.

A process crash, an operating-system crash, and loss of every storage device are different failures. A database can protect against some without surviving all of them. Backups and replicated copies expand recovery options, with their own limits.

**Persistent storage** retains information when the process or machine stops, subject to the device's guarantees. **Buffered data** is a working copy in memory. A **log** stores recovery information; it is distinct from diagnostic messages written by application code. The next section explains why committing need not immediately copy every changed data page from memory to its final file location.

## Why a committed change can survive a crash

Database engines commonly use write-ahead logging (WAL). They may change buffered data pages before those pages reach disk, but must make the corresponding log records durable before writing the changed pages to durable storage. A durable commit acknowledgment also requires the relevant commit records to be safely persisted according to the configuration.

```text
Change buffered pages and generate log records
                  |
Persist required log, including commit
                  |
Acknowledge durable commit to the client
                  |
Write data pages later; recovery can replay the durable log
```

The exact implementation varies. The key is persistence ordering, not a claim that every data page must be written before commit returns.

## Recovery and checkpoints

After a crash, recovery uses the durable log and engine metadata to recover committed changes and handle incomplete transactions. A checkpoint bounds or reduces recovery work by advancing a known recovery position and coordinating page writes.

A checkpoint is not universally a transaction-consistent snapshot of all data pages. Modern engines can use fuzzy checkpoints while transactions continue.

## PostgreSQL settings

With normal durable settings, PostgreSQL flushes the commit's WAL before acknowledging it. `synchronous_commit = off` can acknowledge a transaction before its WAL is durably flushed, permitting loss of recent acknowledged commits after a crash while preserving database consistency.

Disabling `fsync` is a different, more dangerous change: it can allow storage ordering failures that leave the database unrecoverably corrupted after an operating-system crash. Do not treat these settings as interchangeable performance switches. See [PostgreSQL WAL reliability](https://www.postgresql.org/docs/current/wal-reliability.html).

## Replication and backups

Replication can preserve another copy, but asynchronous replicas may lack a recently acknowledged commit. Synchronous replication protects the configured acknowledgment targets and failure model; it does not make every replica equally safe to promote.

Backups address a different problem: recovering from deletion, corruption, or the loss of live copies. Keep the required transaction logs for point-in-time recovery and test a full restoration.

## An ambiguous client result

If a connection drops during commit, the client may not know whether the transaction committed. Blindly repeating an order or payment can duplicate it. Use a stable request identifier enforced by a unique constraint, and query its outcome when reconnecting.

## Observe persistence through a reopened SQLite file

An in-memory database cannot demonstrate persistence after the connection closes. This independent Python exercise uses a temporary disk-backed file and deliberately reopens it:

```python
import sqlite3
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as directory:
    database_path = Path(directory) / 'durability_demo.db'
    connection = sqlite3.connect(database_path)
    connection.execute('PRAGMA journal_mode = WAL')
    connection.execute('PRAGMA synchronous = FULL')
    connection.execute('CREATE TABLE accepted_orders (order_id INTEGER PRIMARY KEY)')
    connection.commit()

    connection.execute('BEGIN')
    connection.execute('INSERT INTO accepted_orders VALUES (104)')
    connection.commit()
    connection.close()

    reopened = sqlite3.connect(database_path)
    print(reopened.execute('SELECT order_id FROM accepted_orders').fetchall())
    reopened.execute('BEGIN')
    reopened.execute('INSERT INTO accepted_orders VALUES (105)')
    reopened.close()  # No commit: this pending transaction is rolled back.

    final_connection = sqlite3.connect(database_path)
    print(final_connection.execute('SELECT order_id FROM accepted_orders').fetchall())
    final_connection.close()
```

Both prints are `[(104,)]`. Committed order 104 survives closing and reopening the file. Uncommitted order 105 does not. The temporary directory is removed after the exercise, so this is a repeatable demonstration rather than a permanent order store.

This verifies ordinary persistence and close-time rollback. It does **not** simulate an operating-system crash or a power loss. A crash test needs a disposable environment, controlled interruption, reopening, and validation of acknowledged operation IDs against the configured failure guarantee.

## Separate SQLite's journal mode from its synchronization policy

`journal_mode = WAL` selects the write-ahead journal mechanism. `synchronous = FULL` controls when SQLite requests synchronization with storage. In WAL mode, FULL synchronizes the WAL at commit; NORMAL avoids some commit-time sync work and can lose recently acknowledged transactions after a power or operating-system failure while retaining the WAL mode's consistency protections.

A main database file with a WAL beside it is one live database state. Committed changes may still reside in the WAL until checkpointing copies their pages into the main file. Copying only the main file during live activity can omit accepted changes. Use SQLite's backup API or another documented consistent backup process rather than treating whichever file happens to be largest as the complete state.

Inspect a practice connection with:

```sql
-- SQLite; use a disk-backed practice database
PRAGMA journal_mode;
PRAGMA synchronous;
PRAGMA wal_checkpoint(PASSIVE);
```

The journal result depends on the selected mode, and the sync result is a numeric policy value. A passive WAL checkpoint returns counters describing its progress; an active reader can prevent it from checkpointing all frames. A checkpoint is maintenance of already committed state, not a substitute for committing a transaction.

## Inspect PostgreSQL settings without changing the guarantee

Use a PostgreSQL connection to read the server's actual configuration:

```sql
-- PostgreSQL
SELECT name, setting
FROM pg_settings
WHERE name IN ('fsync', 'synchronous_commit', 'full_page_writes')
ORDER BY name;
```

A normally durable local configuration commonly reports each setting as `on`. `fsync` requests reliable persistence ordering. `synchronous_commit` controls the point at which a successful commit acknowledgment is sent, including replication behavior when configured. `full_page_writes` protects against partial page writes by logging a full page image on the relevant first change after a checkpoint.

Do not infer a complete disaster-recovery policy from those three values. Storage must honor synchronization, replicas need explicit acknowledgment targets, and backups need restore testing. PostgreSQL can also override `synchronous_commit` for particular transactions; a service that relaxes it for disposable analytics should not accidentally use that policy for accepted orders.

## Decide how much loss and downtime the service can tolerate

Two operational targets make the durability discussion concrete:

| Target | Question | Example requirement |
| --- | --- | --- |
| Recovery point objective (RPO) | How much accepted data may be lost? | Orders must be recoverable through the last acknowledged commit under the planned failure model. |
| Recovery time objective (RTO) | How long can recovery take? | Restore checkout service within 30 minutes of a storage failure. |

A nightly backup by itself can leave nearly a day of changes unrecoverable. Continuous log archiving or other replication and backup mechanisms can reduce that gap. A second asynchronous database may improve availability yet still be missing the final seconds of commits. An RPO of zero for site loss needs a design that has already persisted accepted work in an appropriate other failure domain before acknowledging it.

Measure recovery time through restoration, log replay, validation, and application reconnection. A backup job's success status is not evidence that the application can resume from it. Include credentials, schema, required extensions, and the retained log chain in the restore procedure.

## Replication does not preserve an older correct state automatically

An accidental `DELETE` can be durably committed and promptly replicated everywhere. Durability faithfully preserves the mistake. Backups and point-in-time recovery provide access to an earlier state, while replication usually propagates the current accepted state.

For point-in-time recovery, retain a usable base backup and the required logs through the intended recovery point. Restore to a separate environment, choose a point before the destructive operation, validate the result, and plan how to reconcile legitimate later work. Restoring an entire database backward can discard valid transactions made after the chosen time; it is not an isolated undo of one bad statement.

Place redundant copies where the expected failure does not destroy them together. Two files on one disk do not address disk loss. Two servers in one power or administrative failure domain may not address the site's failure. Retention and access controls also matter when the failure is accidental or malicious deletion of backups.

## Connect acknowledgment, retry, and recovery

When a customer receives “order accepted,” the service needs a precise persistence contract. If the commit reply is lost, query the stable request ID after reconnecting. If the order exists, report its accepted outcome; if its absence is authoritative under the recovery and replication policy, retry according to the operation's idempotency design.

Reading an asynchronous replica that has not caught up is not authoritative proof that the primary never committed. Failover can also lose recent commits if the promoted target was behind. The application's recovery procedure must therefore specify which copy can resolve an uncertain operation and what the configured loss policy permits.

References: [SQLite WAL](https://www.sqlite.org/wal.html), [SQLite synchronous pragma](https://www.sqlite.org/pragma.html#pragma_synchronous), [PostgreSQL WAL settings](https://www.postgresql.org/docs/current/runtime-config-wal.html), and [PostgreSQL continuous archiving](https://www.postgresql.org/docs/current/continuous-archiving.html).

## What to verify

1. Understand what a successful commit acknowledgment means with the selected settings.
2. Check that storage correctly honors flush requests and that redundant copies occupy suitable failure domains.
3. Test crash recovery and failover in a disposable environment.
4. Validate backup restoration against the recovery point and recovery time requirements.

## Related notes

- [Crash recovery](../11_security_best_practices/07_crash_recovery_in_databases.md)
- [Synchronous and asynchronous replication](../09_database_replication/04_synchronous_vs_asynchronous_replication.md)
- [Backup and recovery](../11_security_best_practices/01_backup_and_recovery_strategies.md)
