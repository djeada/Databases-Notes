# Synchronous and Asynchronous Replication

The distinction is what a commit waits for. **Synchronous replication** waits for a configured replica acknowledgment. **Asynchronous replication** can acknowledge a local commit before replicas have caught up.

## Follow one transaction

```text
Synchronous:  local commit work --> required replica acknowledgment --> client success
Asynchronous: local commit work --> client success
                         \-------> replicas receive and apply changes independently
```

Transmission can overlap transaction processing. Asynchronous replication does not require sending every change only after commit; it means replica progress is not required for the client acknowledgment.

## An acknowledgment has a specific meaning

Depending on the engine and settings, it can mean that a replica has received, durably flushed, or applied the transaction. The primary may wait for one replica, a chosen set, or a quorum, rather than every replica.

Receiving or flushing a log record is different from making it visible to a query. A synchronous commit does not automatically make every replica read fresh. Check the acknowledgment level and route reads accordingly.

## Compare the trade-offs

| Concern | Synchronous | Asynchronous |
| --- | --- | --- |
| Commit latency | Includes required replica progress and network delay. | Does not wait for replica progress. |
| Replica failure | Can block commits if the acknowledgment requirement cannot be met. | Primary commits can continue while replicas lag. |
| Primary loss | Required durable replicas can protect acknowledged commits, subject to the failure model and promotion choice. | An acknowledged commit may be absent from the promoted replica. |
| Reads from replicas | Freshness depends on replay and read-routing guarantees. | Stale reads are expected while replicas lag. |
| Failover | Still needs leader selection, fencing, and a safe promotion policy. | Also needs an explicit decision about possible lost transactions. |

Neither mode guarantees survival of every possible failure. Losing all durable copies, promoting an unsuitable replica, or allowing two writable primaries can invalidate assumptions.

## PostgreSQL example

PostgreSQL's `synchronous_standby_names` identifies the acknowledgment requirement. Its `synchronous_commit` settings distinguish acknowledgment levels, including remote flush and remote apply. `remote_apply` waits for the synchronous standby to replay the commit, which is useful when visibility there matters. See [PostgreSQL synchronous replication](https://www.postgresql.org/docs/current/warm-standby.html#SYNCHRONOUS-REPLICATION).

These settings are different from enabling replication in the first place. Verify the actual synchronous standby status and expected behavior when a standby disconnects.

## Define the recovery requirements

A **recovery point objective (RPO)** states how much data loss is acceptable. A **recovery time objective (RTO)** states how long service recovery may take. Choose a replication and failover policy against both requirements, then test primary failure, replica lag, and network interruption.

Monitor received, flushed, and replayed positions where available. A lag duration by itself can conceal a large pending data volume or an idle workload.

Replication is not a backup: accidental deletion and corruption can reach replicas. Keep independently recoverable backups and test restoration.

## Related notes

- [Primary and standby replication](02_master_standby_replication.md)
- [CAP theorem](../06_distributed_databases/06_cap_theorem.md)
- [Backup and recovery](../11_security_best_practices/01_backup_and_recovery_strategies.md)
