# Distributed Databases: Put Data on More Than One Machine

A **distributed database** stores or processes database data across multiple networked machines. A machine participating in the system is often called a **node**. Distribution can help with capacity, availability, or geographic access, but it introduces communication and coordination problems.

Before this chapter, understand [transactions](../04_acid_properties_and_transactions/01_transactions_intro.md) and [indexes](../05_storage_and_indexing/05_indexing.md). Distribution changes where work happens; it does not remove the need to model data or make queries efficient.

## Begin with one bookstore database

With one database server, the application sends a query to one place. That server manages its data, indexes, and transactions. If it stops, the application may lose access even when the stored data is intact.

Two ways to add machines solve different problems:

| Approach | What changes | Main purpose |
|---|---|---|
| Replication | Multiple nodes keep copies of the same data | Additional read capacity and copies available for recovery or failover |
| Sharding | Different nodes own different subsets of the data | Divide storage and work across machines |

A system can use both: each shard can have its own replicas.

## Copies introduce a timing question

Suppose the primary accepts order 104, then sends its changes to a replica. A query reaching the replica before it applies the change may not see that order yet. This delay is **replication lag**.

**Synchronous replication** waits for specified replica acknowledgements before considering a write complete. **Asynchronous replication** allows the primary to acknowledge before all replicas have caught up. The exact meaning of an acknowledgement varies: receiving, persisting, and applying a change are separate stages.

The application must know what a successful write and a later read promise. See the [replication introduction](../09_database_replication/01_intro_to_replication.md) for a complete example.

## Subsets introduce a routing question

Suppose customers are assigned to shards by customer identifier. The application must route each customer's order to the shard that owns that identifier. A **shard key** is the value used to make that assignment.

One customer's orders can then be found on one shard. A report covering all customers may need results from every shard. A transaction touching customers on different shards may need distributed coordination, which is more expensive and can fail in more ways than local work.

A popular customer or a badly chosen key can overload one shard while others are idle. This is a **hotspot**. Adding nodes does not automatically distribute existing data evenly; moving data and updating routing is part of the design.

## A network failure is ambiguous

If node A does not hear from node B, B might have crashed, a link might be broken, or a message might merely be delayed. A **timeout** means a response did not arrive in time; it does not prove that the remote operation failed.

This matters during writes. Retrying an order request after a timeout can create a duplicate if the first request succeeded. A stable request identifier and duplicate detection make retry behavior safer.

A **network partition** separates nodes that cannot communicate. During it, the system must decide which nodes may accept work and which guarantees they can preserve. [CAP](06_cap_theorem.md) explains a particular tradeoff between responding to requests and maintaining a single-copy view during partitions.

## Make guarantees explicit

Instead of saying “the distributed database is reliable,” ask concrete questions:

- Which node accepts a write, and what must happen before it acknowledges success?
- Can a read return an older value, and does the application need to read its own recent writes?
- What happens when the current writer fails? **Failover** means transferring its role to another node.
- Can one transaction change data on multiple shards?
- How are timed-out operations retried without applying them twice?

Products answer these questions differently. Replication, sharding, and stronger coordination each add operating costs, so start with the requirement that justifies them.

## Check your understanding

1. How do replication and sharding distribute data differently?
2. Why might a replica miss an order that the primary has accepted?
3. Why does a timeout not tell you whether a write committed?
4. What makes a cross-shard report more complicated than a single-customer lookup?

Continue with [Partitioning](02_partitioning.md), [Sharding](03_sharding.md), and their [comparison](04_partitioning_vs_sharding.md). The later [distributed systems note](08_distributed_database_systems.md) covers coordination mechanisms in more detail.
