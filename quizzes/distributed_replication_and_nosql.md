# Distributed Databases, Replication and NoSQL Quiz

Notes: [Distributed Database Systems](../notes/06_distributed_databases/01_distributed_database_systems.md), [Sharding](../notes/06_distributed_databases/03_sharding.md), [Partitioning vs Sharding](../notes/06_distributed_databases/04_partitioning_vs_sharding.md), [Consistent Hashing](../notes/06_distributed_databases/05_consistent_hashing.md), [CAP Theorem](../notes/06_distributed_databases/06_cap_theorem.md), [Eventual Consistency](../notes/06_distributed_databases/07_eventual_consistency.md), [Replication Introduction](../notes/09_database_replication/01_intro_to_replication.md), [Primary–Standby Replication](../notes/09_database_replication/02_master_standby_replication.md), [Multi-Primary Replication](../notes/09_database_replication/03_multi_master_replication.md), [Sync vs Async Replication](../notes/09_database_replication/04_synchronous_vs_asynchronous_replication.md), [Querying NoSQL](../notes/10_nosql_databases/03_querying_nosql_databases.md), [Document Modeling](../notes/10_nosql_databases/05_document_modeling.md), [Key-Value Modeling](../notes/10_nosql_databases/06_key_value_modeling.md), [Wide-Column Modeling](../notes/10_nosql_databases/07_wide_column_modeling.md), [Graph Modeling](../notes/10_nosql_databases/08_graph_modeling.md), [NoSQL Consistency and Replication](../notes/10_nosql_databases/09_consistency_transactions_and_replication.md), [Polyglot Persistence](../notes/10_nosql_databases/10_operating_nosql_and_polyglot_persistence.md)

Test how data is split, copied and kept consistent across machines, and how NoSQL models follow access patterns.

#### Q. How do sharding and replication differ?

* [ ] Sharding copies all data to every node; replication splits it
* [x] Sharding splits data across nodes; replication keeps copies of it
* [ ] Sharding applies only to NoSQL; replication only to SQL
* [ ] They are two names for the same technique

> **Explanation:** Sharding places different subsets of data on different nodes, while replication keeps the same data on several nodes. They are orthogonal and are often combined.

#### Q. What distinguishes sharding from table partitioning on a single server?

* [ ] Partitions cannot be defined by a hash function
* [x] Shards live on separate servers across a network
* [ ] Partitioning always needs distributed transactions
* [ ] Sharded tables are not allowed to have indexes

> **Explanation:** Partitioning divides a table within one database instance. Sharding distributes those pieces across machines, adding routing, cross-shard queries and resharding as new problems.

#### Q. Orders are range-sharded by `created_at`. What happens to new inserts?

* [ ] They spread evenly across all of the shards
* [x] They all land on the shard holding the newest range
* [ ] They are rejected until a new shard is created
* [ ] They are copied to every shard

> **Explanation:** A monotonically increasing range key sends every new row to the latest range, creating a write hotspot. Hashing spreads writes but makes range scans span shards.

#### Q. Users and their orders and sessions are sharded by `user_id`. Which query must be sent to every shard?

* [ ] `SELECT * FROM orders WHERE user_id = 42;`
* [x] `SELECT * FROM orders WHERE product_id = 7;`
* [ ] `UPDATE users SET name = 'A' WHERE user_id = 42;`
* [ ] `DELETE FROM sessions WHERE user_id = 42;`

> **Explanation:** A query without the shard key cannot be routed to one shard, so it becomes a scatter-gather across all of them. Choose the shard key from the most important access patterns.

#### Q. With simple modulo hashing (`hash(key) % N`), adding one server remaps most keys. What does consistent hashing change?

* [ ] No keys ever move when nodes change
* [x] Only keys in the new node's arc of the ring move
* [ ] Every key moves exactly once to the new node
* [ ] Keys are reassigned randomly across all nodes

> **Explanation:** On a hash ring, a new node takes over only part of one neighbour's interval. Keys elsewhere on the ring keep their assignments.

#### Q. What do virtual nodes add to consistent hashing?

* [ ] They make a single hot key spread across many servers
* [x] Each server gets many ring points, smoothing load
* [ ] They remove the need for replication
* [ ] They guarantee no key ever moves

> **Explanation:** Many points per physical server even out arc sizes and let bigger servers take proportionally more. A single hot key still lands on one owner.

#### Q. What does "consistency" mean in the CAP theorem?

* [ ] Every transaction preserves the database's constraints
* [x] Operations behave as if on one up-to-date copy (linearizability)
* [ ] All replicas store their data in the same on-disk format
* [ ] Every write eventually becomes visible to all readers

> **Explanation:** CAP consistency is a linearizability-style guarantee about reads and writes. It is unrelated to ACID consistency, which means preserving declared rules and invariants.

#### Q. Three replicas are split into `A | B–C` by a network partition. A consistency-first system uses majority quorums. What happens on A's side?

* [ ] A keeps accepting authoritative writes
* [x] A refuses or delays operations that need a quorum
* [ ] A becomes the new primary because it is isolated
* [ ] A merges its writes with B and C later

> **Explanation:** A alone cannot form a majority of two, so it must fail or wait for strongly consistent operations. That is exactly the consistency-over-availability choice CAP predicts; quorums implement the trade-off rather than beat it.

#### Q. A Cassandra table has replication factor 3, and both reads and writes use `QUORUM`. Why does a read meet the latest acknowledged write under the documented model?

* [ ] `QUORUM` waits for all three replicas
* [x] $R + W = 4 > 3$, so the read and write sets overlap
* [ ] `QUORUM` always reads from the coordinator node
* [ ] Writes at `QUORUM` are applied synchronously everywhere

> **Explanation:** A quorum of 3 is 2. Any two replicas read and any two written must share at least one node. With `ONE` for both, $R + W = 2$ and a read can miss the write.

#### Q. Why is a single PostgreSQL server not a counterexample to CAP?

* [ ] Its MVCC snapshots remove network partitions
* [x] It has no replicas; if it fails, it is unavailable
* [ ] It gives up consistency in order to stay available
* [ ] It runs consensus internally between its processes

> **Explanation:** CAP concerns replicated copies during a network partition. A lone server is simply a different failure model: if it is unreachable, availability disappears.

#### Q. Two replicas accept concurrent updates to the same cart during a partition. After reconnecting, they resolve with last-write-wins. What is the risk?

* [ ] The replicas can never converge again
* [x] One acknowledged update is silently discarded
* [ ] Both updates are applied twice
* [ ] Reads block until an operator picks a winner

> **Explanation:** Last-write-wins converges by keeping the update with the later timestamp, which can drop the other change. Convergence and preserving every update are different properties.

#### Q. What do vector clocks let a replicated store detect?

* [ ] The physical time of every write
* [x] That two versions were written concurrently
* [ ] Which replica has the most free disk space
* [ ] Whether a network partition has ended yet

> **Explanation:** Vector clocks track causal history, distinguishing "one version supersedes the other" from "neither saw the other". Concurrent versions then need an application or CRDT-style merge.

#### Q. Under eventual consistency, what is guaranteed?

* [ ] Every read returns the latest write
* [x] If updates stop, replicas converge to the same value
* [ ] Writes are rejected during a partition
* [ ] Replicas agree within a fixed number of milliseconds

> **Explanation:** Eventual consistency promises convergence, not freshness at any moment or a time bound. Applications must tolerate stale reads in between.

#### Q. A user updates their profile on the primary and the next page reads from an asynchronous replica. What can happen?

* [ ] The write is rolled back on the primary
* [x] The page shows the old profile because of replication lag
* [ ] The replica rejects the read until it has fully caught up
* [ ] The replica forwards the write back to the primary

> **Explanation:** Asynchronous replicas apply changes after the primary commits, so an immediate read may be stale. Read-your-writes needs routing that user's reads to the primary or waiting for the replica to reach the write's position.

#### Q. With asynchronous replication, the primary crashes and a replica is promoted. What can be lost?

* [ ] Nothing, because every commit waits for the replica
* [x] Acknowledged commits not yet sent to the replica
* [ ] Only uncommitted transactions running on the replica
* [ ] Every transaction since the last full backup

> **Explanation:** The primary acknowledges before replicas confirm, leaving a data-loss window. Synchronous replication narrows it at the cost of commit latency.

#### Q. With a synchronous standby configured, which PostgreSQL `synchronous_commit` level waits until the standby has replayed the change so it is visible to standby queries?

* [ ] `local`
* [ ] `remote_write`
* [ ] `on`
* [x] `remote_apply`

> **Explanation:** `on` waits for a durable WAL flush on the standby, which is not the same as replay. `remote_apply` waits for replay, giving read visibility on that standby.

#### Q. What is a cost of synchronous replication to a standby in another region?

* [ ] Replicas can no longer be promoted
* [x] Each commit waits for a network round trip to the standby
* [ ] The primary stops writing WAL locally
* [ ] It allows more committed data to be lost on failover

> **Explanation:** Commit latency includes the round trip, and an unavailable synchronous standby can stall commits. Durability improves while latency and availability dependencies grow.

#### Q. After a network split, an old primary and a newly promoted replica both accept writes. What is this called and what prevents it?

* [ ] Replication lag; a larger WAL buffer
* [x] Split brain; fencing the old primary
* [ ] Write skew; Serializable isolation
* [ ] Read repair; anti-entropy

> **Explanation:** Two nodes acting as primary create divergent histories. Fencing excludes the old primary, through storage, network or power controls, before the new one takes writes.

#### Q. A standby with a PostgreSQL physical replication slot goes offline for 10 hours. What risk does the primary face?

* [ ] The slot silently drops and the standby resyncs automatically
* [x] Retained WAL accumulates and can fill the primary's disk
* [ ] The primary stops accepting writes immediately
* [ ] The slot replays WAL to the primary itself

> **Explanation:** A slot keeps WAL until its consumer receives it. Monitor slot lag and consider `max_slot_wal_keep_size` to cap retention.

#### Q. You need to replicate only two tables into a database running a newer PostgreSQL major version. Which kind of replication fits?

* [ ] Physical WAL streaming replication to a standby
* [x] Logical replication (publications/subscriptions)
* [ ] A block-level copy of the data directory
* [ ] Synchronous physical streaming replication

> **Explanation:** Logical replication sends row changes and can select tables and cross versions. Physical replication copies storage-level changes for a whole cluster and is tightly coupled to the engine version.

#### Q. What can happen to MySQL semisynchronous replication when no replica acknowledges within the timeout?

* [ ] The source rolls back every pending transaction
* [x] It can fall back to asynchronous replication
* [ ] The source shuts down to protect the data
* [ ] It promotes the slowest replica automatically

> **Explanation:** After the timeout, the source can continue without acknowledgement, so the durability guarantee quietly weakens until a replica catches up. Monitor for this state.

#### Q. In a Galera cluster, two nodes update the same row concurrently. What typically happens at commit?

* [ ] Both commits succeed and the values are merged
* [x] The later-certified transaction fails and must be retried
* [ ] The node with the higher ID always wins
* [ ] Both transactions are blocked until an operator intervenes

> **Explanation:** Galera executes locally and certifies write sets in a global order. A conflicting later write set is aborted, so applications need retry logic, especially around hot rows.

#### Q. Why are `AUTO_INCREMENT` values not contiguous in a multi-primary Galera cluster?

* [ ] Galera reuses freed IDs after rows are deleted
* [x] Nodes use interleaved offsets to avoid collisions
* [ ] IDs are generated from node timestamps instead
* [ ] Galera disables `AUTO_INCREMENT` on all tables

> **Explanation:** Automatic increment control adjusts the increment and offset by cluster size, so three nodes might generate 1, 4, 7 and 2, 5, 8. Gaps are expected.

#### Q. A Cassandra table is declared `PRIMARY KEY ((customer_id), event_time, event_id)`. Which query fits it?

* [ ] All events of a given type across every customer
* [x] One customer's events within a time range
* [ ] All events in a time range across every customer
* [ ] Customers ordered by their total number of events

> **Explanation:** `customer_id` is the partition key, and the clustering columns order rows inside each partition. Queries should target one partition and read a range of clustering keys.

#### Q. A Cassandra partition keyed only by `sensor_id` grows without bound as readings accumulate. What is the usual fix?

* [ ] Add `ALLOW FILTERING` to the read queries
* [x] Partition by `(sensor_id, day)` instead
* [ ] Create a secondary index on `sensor_id`
* [ ] Lower the replication factor to 1

> **Explanation:** Bucketing bounds each partition's size while keeping a sensor's recent data together. `ALLOW FILTERING` permits unsupported queries but does not fix the model.

#### Q. Why does Cassandra write a tombstone when data is deleted instead of erasing it immediately?

* [ ] To let users undo deletes for a fixed period
* [x] So an offline replica cannot resurrect the data
* [ ] Because SSTable files can never be modified
* [ ] To keep deleted data visible to later reads

> **Explanation:** A deletion marker lets replicas that missed the delete learn about it during repair. Large numbers of tombstones can slow reads until compaction removes them.

#### Q. A MongoDB customer document stores every login event in one ever-growing array. What do the notes recommend?

* [ ] Keep the array and raise the document size limit
* [x] Store events as separate documents or bounded buckets
* [ ] Move the array into a nested object
* [ ] Index the array to keep writes cheap

> **Explanation:** Unbounded arrays cause document growth, expensive rewrites, large payloads and size-limit problems. Separate event documents or month buckets give each document a planned upper size.

#### Q. An order always shows its few shipping addresses, which are read together and rarely change. Which document design fits?

* [x] Embed the addresses in the order document
* [ ] Store each address in a separate collection by reference
* [ ] Store addresses in a key-value cache only
* [ ] Duplicate the addresses into every product document

> **Explanation:** One-to-few, bounded data read with its parent suits embedding and loads in one read. References suit large, unbounded or widely shared data.

#### Q. Inventory must keep `available` and `reserved` consistent. Why do the notes suggest storing both in one MongoDB document?

* [ ] Documents cannot hold more than one counter
* [x] Updates to a single document are atomic
* [ ] It removes the need for any index
* [ ] Separate documents cannot be updated at all

> **Explanation:** Document databases commonly guarantee atomicity per document, so the document boundary is a correctness decision. Updating several documents together needs multi-document transactions where the engine supports them.

#### Q. In MongoDB, which documents does the filter `{nickname: null}` match?

* [ ] Only documents where `nickname` is explicitly `null`
* [x] Documents where `nickname` is `null` or missing
* [ ] Only documents without a `nickname` field
* [ ] No documents, because null never compares equal

> **Explanation:** The null filter is broader than many expect. Add `$exists: true` for explicit nulls only, or use `$exists: false` for missing fields only.

#### Q. A client calls MongoDB `replaceOne` with only `{name: "Ana"}` for a user document that also had `email`. What happens to `email`?

* [ ] It is kept unchanged alongside the new name
* [x] It is removed, since the whole body is replaced
* [ ] It is kept, but its value becomes `null`
* [ ] The call fails because `email` is missing

> **Explanation:** Replacement writes a new document body except `_id`. A partial update with `updateOne` and `$set` changes only the named fields.

#### Q. A popular Redis cache key expires and thousands of requests miss at once, all querying the database. Which mitigation targets this?

* [ ] Removing the TTL from every cached key
* [x] Single-flight rebuilds with jittered TTLs
* [ ] Storing the value in a larger Redis hash
* [ ] Switching the cache to write-behind mode

> **Explanation:** This is a cache stampede. Letting one request rebuild the value while others wait, and spreading expiry times with jitter, prevents a burst of identical database queries.

#### Q. In a Neo4j graph, a `Country {name: "US"}` node connects to hundreds of millions of users. Why is traversing through it a problem?

* [ ] Nodes cannot have more than one label
* [x] It is a supernode, so traversals fan out enormously
* [ ] Relationships pointing to it cannot carry properties
* [ ] Cypher cannot match nodes by a property

> **Explanation:** A very high-degree node makes any path through it expensive. Alternatives include filtering by property, partitioning relationships or avoiding traversal through global hubs.

#### Q. Code writes an order to PostgreSQL and then indexes it in a search engine. The second write fails. What pattern do the notes recommend?

* [ ] Swap the order: write the search index first
* [x] Record the change in an outbox or CDC stream and project it
* [ ] Retry the search write forever inside the web request
* [ ] Wrap both writes in a database savepoint

> **Explanation:** This is the dual-write problem; reversing the order only reverses the failure. Deriving the search index from a durable change log, plus reconciliation, keeps one source of truth.
