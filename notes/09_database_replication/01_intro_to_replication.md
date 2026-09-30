# Replication: Maintain Another Copy of Database Changes

**Replication** maintains database data on more than one node by transferring changes between them. A **replica** is one of those copies. Replication can support reads and recovery from a failed node, but the copies are not necessarily identical at every instant.

Read [Transactions](../04_acid_properties_and_transactions/01_transactions_intro.md) first. Replication adds a question to commit: which other nodes, if any, must receive or persist a transaction before the client hears that it succeeded?

## Follow one new order

In a common single-writer design, the **primary** accepts writes and replicas receive its changes. For an asynchronous setup, the sequence might be:

```text
1. Primary commits order 104.
2. Primary acknowledges success to the application.
3. Replica receives the change.
4. Replica applies the change so its queries can see order 104.
```

A read from the replica between steps 2 and 4 may not find the order. This is **replication lag**: the replica has not yet reached the primary's state. Network delays, a busy replica, or slow storage can increase it.

Applications sometimes route an immediate confirmation read to the primary so users can see their own writes. Other designs wait for a replica to reach a known replication position. A **position** identifies progress through the stream of changes.

## Separate receiving, persisting, and applying

These events give different guarantees:

| Replica event | What it means |
|---|---|
| Receive | The change has arrived, possibly only in memory |
| Persist | Recovery information for the change has reached durable storage |
| Apply | The replica has incorporated the change into the state it serves |

Synchronous replication waits for specified acknowledgements before returning success. It does not automatically mean every replica has applied the change or every possible read will see it. Check the engine's acknowledgement policy and the nodes required to acknowledge. See [synchronous versus asynchronous replication](04_synchronous_vs_asynchronous_replication.md).

## Creating a replica requires a starting point

A new replica usually needs an initial copy of the data and a way to continue from that copy's replication position. Copying arbitrary files while writes are occurring can produce an inconsistent starting point; use the engine's supported snapshot or backup procedure.

After initialization, replication can transfer storage-level changes or logical changes to records and tables. These approaches are commonly called **physical** and **logical** replication. Physical replication is closely tied to engine storage formats. Logical replication exposes a different set of compatibility, schema, and object-coverage concerns. Neither term means that every database object is always copied automatically.

## Failover is more than starting another process

**Failover** promotes or selects another node to accept the primary's work after failure. The system needs to determine which copy is suitable, route clients to it, and prevent the old primary from continuing to accept conflicting writes.

If an asynchronous primary dies before sending an acknowledged transaction to a surviving replica, that transaction can be missing after failover. How much acknowledged data may be lost is part of the recovery requirement, often expressed as a **recovery point objective (RPO)**. How long service may take to return is the **recovery time objective (RTO)**.

If two nodes both believe they are the primary, they can accept incompatible changes. This situation is called **split brain**. Preventing an excluded writer from continuing is often called **fencing**. These details explain why simply having two servers does not prove safe automatic failover.

## Replication is not a historical backup

A mistakenly deleted order can be deleted on the replicas too. Replication preserves copies of ongoing changes; it does not necessarily preserve an earlier state you can restore.

Backups and retained recovery logs provide recovery options for accidental deletion, corruption, or other events that replication can propagate. Restore procedures must be tested. See [backup and recovery](../11_security_best_practices/01_backup_and_recovery_strategies.md).

## Choose the job for each copy

A reporting replica may tolerate some lag. An immediate order-confirmation page may require a current read. A failover replica may need stricter durability and monitoring than a disposable analytical copy.

Also distinguish replication from sharding: replicas copy overlapping data; shards own different subsets. A sharded system can replicate each shard independently.

## Check your understanding

1. At which point in the example can the application hear success while the replica still lacks the order?
2. How do receipt, persistence, and application differ?
3. Why can asynchronous failover lose an acknowledged write?
4. Why does another copy fail to protect against every accidental deletion?

Next: [primary–standby replication](02_master_standby_replication.md), then [multi-primary replication](03_multi_master_replication.md).
