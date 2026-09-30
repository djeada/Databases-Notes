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

## What to verify

1. Understand what a successful commit acknowledgment means with the selected settings.
2. Check that storage correctly honors flush requests and that redundant copies occupy suitable failure domains.
3. Test crash recovery and failover in a disposable environment.
4. Validate backup restoration against the recovery point and recovery time requirements.

## Related notes

- [Crash recovery](../11_security_best_practices/07_crash_recovery_in_databases.md)
- [Synchronous and asynchronous replication](../09_database_replication/04_synchronous_vs_asynchronous_replication.md)
- [Backup and recovery](../11_security_best_practices/01_backup_and_recovery_strategies.md)
