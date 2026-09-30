# Apache Cassandra

Apache Cassandra is a distributed wide-column database designed for high write throughput, horizontal scale, multi-node availability, and predictable key-oriented access.

It is not a relational database with fewer features. Cassandra's data model is built around a different rule:

> Design tables from the queries you need to execute.

Cassandra deliberately avoids cross-partition joins, foreign keys, and general multi-partition transactions because those operations require expensive coordination across the cluster.

Official documentation:

- [Cassandra architecture overview](https://cassandra.apache.org/doc/latest/cassandra/architecture/overview.html)
- [Cassandra quickstart](https://cassandra.apache.org/doc/latest/cassandra/getting-started/cassandra-quickstart.html)
- [CQL data definition](https://cassandra.apache.org/doc/latest/cassandra/developing/cql/ddl.html)

## Where Cassandra is used

Common workloads include:

- very large write-heavy event datasets,
- time-series-style records,
- IoT telemetry,
- per-user activity history,
- geographically replicated application data,
- high-throughput keyed lookups,
- systems where adding nodes should increase capacity.

It is a poor fit when the application depends heavily on:

- arbitrary joins,
- frequent ad-hoc query patterns,
- cross-row relational constraints,
- multi-table transactions,
- global aggregates without a separate analytics layer.

## Architecture

Cassandra is decentralized: there is no single permanent primary node for the whole database.

```text
                 client
                   │
                   ▼
            any Cassandra node
              coordinator
             /     |      \
            /      |       \
           ▼       ▼        ▼
        node A   node B    node C
          │        │         │
       replicas for the partition
```

A client can contact a node, which acts as the **coordinator** for that request.

The coordinator:

1. hashes the partition key,
2. determines which nodes own the token range,
3. contacts replicas,
4. waits for enough responses to satisfy the requested consistency level.

## Partitioning

Every Cassandra table has a partition key.

Example:

```sql
CREATE TABLE messages_by_user (
    user_id uuid,
    sent_at timestamp,
    message_id uuid,
    body text,
    PRIMARY KEY ((user_id), sent_at, message_id)
) WITH CLUSTERING ORDER BY (sent_at DESC);
```

The primary key contains:

```text
PRIMARY KEY (
  (user_id),             <- partition key
  sent_at, message_id    <- clustering columns
)
```

Rows for one `user_id` are colocated logically in one partition and ordered by the clustering columns.

```text
user_id = A
┌─────────────────────────────────────┐
│ newest message                      │
│ older message                       │
│ older message                       │
└─────────────────────────────────────┘

user_id = B
┌─────────────────────────────────────┐
│ newest message                      │
│ older message                       │
└─────────────────────────────────────┘
```

The partition key determines where data lives.

## Why query-first modeling matters

This query is efficient because it supplies the partition key:

```sql
SELECT *
FROM messages_by_user
WHERE user_id = ?
LIMIT 50;
```

Cassandra can route directly to the replicas that own that user's partition.

A query such as:

```sql
SELECT *
FROM messages_by_user
WHERE body LIKE '%database%';
```

does not match the table's access pattern.

In Cassandra, the normal solution is not "let the database scan everything." It is often:

- create another table for another query,
- use a secondary/indexing feature if appropriate,
- send search workloads to a search system,
- send global analytics to Spark/ClickHouse/a warehouse.

## Denormalization

Relational design often avoids duplicated data.

Cassandra frequently duplicates data intentionally so each query can read one well-designed table.

For example:

```text
messages_by_user
messages_by_conversation
recent_messages_by_team
```

One logical message can be written to several tables.

This moves complexity from reads to writes.

```text
relational:
write once -> join at read time

Cassandra:
write multiple query-shaped copies -> simple keyed reads
```

## Local setup

The repository includes:

[`scripts/cassandra/docker-compose.yml`](../../scripts/cassandra/docker-compose.yml)

Start the local node:

```bash
cd scripts/cassandra
docker compose up -d
docker compose ps
```

Wait until Cassandra is ready:

```bash
docker logs -f cassandra-notes
```

Open CQL shell:

```bash
docker exec -it cassandra-notes cqlsh
```

Stop the demo:

```bash
docker compose down
```

## Runnable CQL demo

The repository also includes:

[`scripts/cassandra/demo.cql`](../../scripts/cassandra/demo.cql)

Load it:

```bash
docker exec -i cassandra-notes cqlsh < demo.cql
```

Then query:

```bash
docker exec -it cassandra-notes   cqlsh   -e "SELECT * FROM notes.events_by_user WHERE user_id = 'user-42';"
```

The demo uses replication factor 1 because it is a single-node learning environment.

That is not a production topology.

## Keyspaces

A keyspace is the top-level namespace and replication configuration.

Development example:

```sql
CREATE KEYSPACE notes
WITH replication = {
  'class': 'SimpleStrategy',
  'replication_factor': 1
};
```

For production, Cassandra's documentation recommends topology-aware replication rather than `SimpleStrategy`.

A typical multi-datacenter shape is:

```sql
CREATE KEYSPACE app
WITH replication = {
  'class': 'NetworkTopologyStrategy',
  'dc1': 3,
  'dc2': 3
};
```

This describes how many replicas should exist in each datacenter.

## Token ring

Cassandra hashes partition keys into tokens.

```text
                   token space

              node A       node B
                             /
                            /
                           /
             ----- ring -----
                  /         \
                 /           \
              node D       node C
```

Modern Cassandra commonly uses virtual nodes so each physical node owns many token ranges.

When a node is added, ranges can be redistributed rather than manually assigning one huge contiguous section.

## Replication factor

Replication factor is the number of copies of a partition.

For:

```text
RF = 3
```

a partition is stored on three replicas.

```text
partition P
   │
   ├── replica on node A
   ├── replica on node C
   └── replica on node F
```

Replication improves availability and durability.

It also increases storage and network cost.

## Consistency levels

Cassandra supports tunable consistency per request.

Common levels include:

- `ONE`,
- `LOCAL_ONE`,
- `QUORUM`,
- `LOCAL_QUORUM`,
- `ALL`.

Suppose:

```text
replication factor = 3
```

A quorum requires two replicas.

```text
write at QUORUM:
replica A  ACK
replica B  ACK
replica C  slow

client can succeed after A+B
```

Using quorum reads and writes creates overlapping replica sets, which provides stronger read-after-write behavior than using one replica for both.

The right consistency level depends on latency, availability, topology, and business correctness.

## Multi-datacenter consistency

For globally distributed deployments, `LOCAL_QUORUM` is often important because it requires a majority only inside the local datacenter rather than waiting across long inter-region links.

Conceptually:

```text
Europe application
      │
      ▼
EU Cassandra DC
  local quorum
      │
      └──── async replication ───► US Cassandra DC
```

This can give local-region latency while maintaining copies in multiple locations.

The exact guarantees must be evaluated carefully for the application's read/write patterns.

## Storage engine

Cassandra uses an LSM-tree-style storage design.

Writes roughly flow through:

```text
write
 │
 ├──► commit log
 │
 └──► memtable
        │
        ▼ flush
      SSTable
        │
        ▼
    compaction
```

### Commit log

Sequential durable write record.

### Memtable

In-memory sorted structure.

### SSTable

Immutable on-disk sorted table.

New writes do not update an old SSTable in place.

Instead, newer values are written into newer structures and resolved during reads/compaction.

## Compaction

Over time, many SSTables accumulate.

Compaction merges them:

```text
SSTable 1 ─┐
SSTable 2 ─┼──► merged SSTable
SSTable 3 ─┘
```

Compaction:

- removes obsolete values,
- consolidates files,
- affects read amplification,
- consumes CPU and disk I/O.

Different workloads can benefit from different compaction strategies.

Do not tune compaction without measuring actual data shape and read/write behavior.

## Tombstones

Cassandra does not immediately erase deleted data from every replica.

A delete creates a tombstone.

```text
old value
   │
DELETE
   ▼
tombstone
   │
   ▼
eventual compaction removes old data
```

Tombstones are required because an offline replica might otherwise later reintroduce deleted data.

Too many tombstones can make reads expensive.

Common causes:

- heavy TTL use,
- repeated deletes,
- poorly bounded partitions,
- modeling frequently changing data as append/delete patterns.

## TTL

Rows or columns can expire:

```sql
INSERT INTO notes.sessions (
    session_id,
    user_id,
    payload
)
VALUES (
    'abc',
    'user-42',
    '...'
)
USING TTL 3600;
```

TTL is useful for expiring:

- sessions,
- telemetry,
- event retention,
- temporary state.

Expiration creates tombstone/compaction implications, so very high-volume TTL workloads require deliberate design.

## Clustering columns

Clustering columns define order inside a partition.

```sql
PRIMARY KEY ((device_id), event_time)
```

This makes queries such as:

```sql
SELECT *
FROM readings_by_device
WHERE device_id = ?
  AND event_time >= ?
  AND event_time < ?
ORDER BY event_time DESC;
```

natural and efficient.

The table is designed for that exact query family.

## Bucketed partitions

An unbounded partition can become too large.

Bad design:

```text
partition key = customer_id
customer has 10 years of billions of events
```

Better:

```text
partition key = (customer_id, month)
```

Example:

```sql
PRIMARY KEY ((customer_id, bucket_month), event_time, event_id)
```

Now data is split:

```text
(customer 42, 2026-08)
(customer 42, 2026-09)
(customer 42, 2026-10)
```

Bucket size should follow expected partition size and query windows.

## Lightweight transactions

Cassandra supports compare-and-set style operations for single-partition coordination.

Example:

```sql
UPDATE usernames
SET user_id = ?
WHERE username = ?
IF user_id = null;
```

Lightweight transactions require consensus and are more expensive than normal Cassandra writes.

Use them for specific correctness requirements, not every write.

## Secondary indexing

Cassandra offers secondary-index mechanisms, including Storage-Attached Indexing in modern versions.

Indexes can be useful, but they do not turn Cassandra into a general relational/ad-hoc query system.

Start from primary access patterns.

Use indexes only after understanding:

- selectivity,
- data distribution,
- query fan-out,
- operational cost.

## Joins

Cassandra does not provide relational distributed joins.

Instead of:

```sql
SELECT *
FROM orders
JOIN customers ...
```

model the read directly:

```text
orders_by_customer
┌─────────────────────────────────┐
│ customer fields needed by query │
│ order fields                    │
└─────────────────────────────────┘
```

Duplicating a customer display name into a query table can be normal Cassandra modeling.

## Repair

Replicas can temporarily diverge.

Cassandra uses mechanisms such as:

- hinted handoff,
- read repair behavior,
- anti-entropy repair.

Operational repair is important for replica convergence.

A cluster that "looks healthy" but is never repaired can accumulate consistency risk depending on failures and workload.

## Backups

Snapshots capture SSTables at a point in time.

Backups must include:

- data,
- schema,
- recovery procedures,
- off-cluster storage.

Replication is not a backup.

An accidental application delete can be replicated to every replica.

## Monitoring

Important Cassandra signals include:

- read/write latency,
- pending compactions,
- dropped messages,
- disk utilization,
- heap/GC pressure,
- tombstone warnings,
- partition size,
- repair status,
- coordinator timeouts,
- node availability.

Cassandra operations require cluster awareness; adding more nodes is not a substitute for monitoring.

## Cassandra versus DynamoDB

Both are commonly used for key-oriented, horizontally scalable workloads, but they differ operationally.

Cassandra:
- self-managed or managed through various providers,
- CQL data model,
- tunable consistency,
- explicit cluster operations.

DynamoDB:
- AWS-managed service,
- capacity/billing/service limits controlled by AWS,
- different API/index/transaction model.

The choice often comes down to cloud strategy, operational ownership, API requirements, and existing expertise.

## Cassandra versus PostgreSQL

Choose PostgreSQL when:

- joins matter,
- transactions span many related rows,
- constraints are important,
- query patterns evolve frequently,
- one relational model serves the workload well.

Choose Cassandra when:

- data and request volume justify distribution,
- query patterns are known in advance,
- keyed/partitioned access dominates,
- high write throughput and multi-node availability matter.

Do not choose Cassandra merely because the dataset is "big."

## Common mistakes

### Modeling like a relational database

Normalization and join-dependent schemas work against Cassandra's strengths.

### Poor partition key

A bad key creates hot nodes or huge partitions.

### Unbounded partitions

Partitions should have a planned upper size.

### `ALLOW FILTERING` as a design strategy

If a query needs filtering across large unrelated data ranges, the table model is probably wrong.

### Using lightweight transactions everywhere

Consensus has a cost.

### Ignoring repair

Replication systems require operational maintenance.

### One-node production cluster

The architecture assumes redundancy.

## Practical design workflow

For every feature:

1. Write the exact query.
2. Identify the partition key.
3. Determine desired ordering inside the partition.
4. Estimate partition size over time.
5. Decide whether bucketing is required.
6. Choose replication topology.
7. Choose consistency levels.
8. Estimate write amplification from denormalized tables.
9. Define TTL/tombstone behavior.
10. Test failure and recovery.

## Related notes

- [Redis](10_redis.md)
- [Choosing a database](07_choosing_database.md)
- [Distributed SQL](14_distributed_sql.md)
- [Partitioning](../06_distributed_databases/02_partitioning.md)
- [Eventual consistency](../06_distributed_databases/07_eventual_consistency.md)
