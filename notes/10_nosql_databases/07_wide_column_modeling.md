# Wide-Column Modeling: Query-First Tables, Partitions, and Bucketing

Wide-column databases such as Cassandra and HBase are designed around partitioned,
distributed access patterns. The central modeling rule is different from a
relational database:

> Start from the query, then design the table that answers it directly.

Normalization is not the primary goal. Predictable partition-key access is.

## Query-first design

Suppose the bookstore needs:

> Show the latest 50 events for one customer.

A query-shaped table can be:

```text
events_by_customer
partition key: customer_id
clustering: event_time DESC, event_id
```

Conceptually:

```text
customer 42 partition
├── 2026-10-01 15:10 purchase
├── 2026-10-01 14:55 login
└── ...
```

The query can route to one partition.

## Partition key

The partition key decides where data lives.

Good partition keys usually provide:

- predictable routing,
- balanced distribution,
- bounded partition size,
- useful locality.

Bad key:

```text
country
```

if 80% of all users are in one country.

That creates skew.

## Clustering columns

Clustering columns organize rows inside a partition.

Example:

```text
PRIMARY KEY ((customer_id), event_time, event_id)
```

The partition key is:

```text
customer_id
```

The clustering columns are:

```text
event_time, event_id
```

That shape supports ordered range reads within one customer.

## Runnable Cassandra example

The repository already contains:

[`scripts/cassandra/demo.cql`](../../scripts/cassandra/demo.cql)

This chapter adds:

[`scripts/cassandra/nosql_bucketed_events.cql`](../../scripts/cassandra/nosql_bucketed_events.cql)

The additional demo shows a time-bucketed partition key.

Run after starting the local Cassandra container:

```bash
cd scripts/cassandra
docker compose up -d
docker exec -i cassandra-notes cqlsh < nosql_bucketed_events.cql
```

## Unbounded partitions

Bad design:

```text
partition key = customer_id
```

if one customer can accumulate billions of events over many years.

The partition keeps growing.

Use bucketing.

## Time bucket

Partition key:

```text
(customer_id, month)
```

Example partitions:

```text
(customer 42, 2026-08)
(customer 42, 2026-09)
(customer 42, 2026-10)
```

Now each partition has a planned lifetime/size.

## Bucket granularity

Choose bucket size from:

- write rate,
- row size,
- retention,
- query window.

High-volume telemetry may need:

```text
hourly buckets
```

Lower-volume application events may use:

```text
monthly buckets
```

Do not choose a calendar bucket without estimating partition size.

## Estimate partition size

Approximate:

```text
rows per period
× average row size
= partition data size
```

Then include indexing/storage overhead.

The exact acceptable size depends on the engine and workload.

## Duplicate tables for duplicate queries

Suppose you need:

1. latest events by customer,
2. all failures by service,
3. events by device and hour.

A wide-column model may maintain:

```text
events_by_customer
failures_by_service
events_by_device_hour
```

The same logical event is duplicated.

This is intentional query-driven denormalization.

## Write fan-out

One logical event may produce several writes:

```text
new event
  │
  ├──► events_by_customer
  ├──► failures_by_service
  └──► events_by_device_hour
```

That shifts work from read time to write time.

The application must define what happens when only some writes succeed.

## Materialized projections

Possible strategies:

- application writes every table,
- asynchronous event/CDC pipeline updates projections,
- database-managed materialized view where supported.

Each has different consistency and failure behavior.

## No joins by default

A wide-column database generally expects the read model to already contain the
fields needed by the query.

Instead of:

```sql
SELECT ...
FROM orders
JOIN customers ...
```

store a query-shaped row.

That may include copied display fields.

## Historical versus current copied values

As with document modeling, duplicated values need semantics.

Example:

```text
customer_name_at_order
```

can be intentionally historical.

But:

```text
current_customer_plan
```

may need propagation if the customer changes plan.

Name the field to make the meaning explicit.

## Cassandra CQL example

```sql
CREATE TABLE events_by_customer_month (
    customer_id text,
    bucket_month text,
    event_time timestamp,
    event_id uuid,
    event_type text,
    payload text,
    PRIMARY KEY (
        (customer_id, bucket_month),
        event_time,
        event_id
    )
) WITH CLUSTERING ORDER BY (event_time DESC);
```

Query:

```sql
SELECT *
FROM events_by_customer_month
WHERE customer_id = 'customer-42'
  AND bucket_month = '2026-10'
LIMIT 50;
```

The query supplies the full partition key.

## Partition-local range query

Because `event_time` is a clustering column, a time range can be efficient:

```sql
SELECT *
FROM events_by_customer_month
WHERE customer_id = 'customer-42'
  AND bucket_month = '2026-10'
  AND event_time >= '2026-10-01T00:00:00Z'
  AND event_time <  '2026-10-02T00:00:00Z';
```

The table exists for this query pattern.

## Query not supported by the table

Suppose you ask:

```text
find every event where payload contains "database"
```

The partition key does not help.

Possible solutions:

- search engine,
- dedicated query table,
- supported secondary-index feature,
- analytics pipeline.

Do not force a full-cluster filtering query into the transactional path.

## ALLOW FILTERING

In Cassandra, `ALLOW FILTERING` can permit queries the normal primary-key model
does not support.

It is not a replacement for data modeling.

Use it only when the data volume/query behavior is understood.

## Secondary indexes

Modern wide-column systems provide secondary indexing options.

Use them selectively.

Ask:

- how selective is the field?
- does the query still fan out?
- what write/index cost exists?
- is the index supported for the exact workload?

The primary partition model remains fundamental.

## Consistency levels

Wide-column systems often let clients choose consistency per request.

Example concepts:

```text
ONE
LOCAL_QUORUM
QUORUM
ALL
```

The choice affects:

- latency,
- availability,
- read freshness.

See the dedicated consistency note for deeper treatment.

## Replication factor

Replication factor controls how many replicas store a partition.

Example:

```text
RF = 3
```

Each partition has three copies.

This improves fault tolerance but increases storage/network work.

## Quorum intuition

For three replicas:

```text
quorum = 2
```

A quorum write waits for two acknowledgements.

A quorum read consults enough replicas to provide overlapping read/write sets.

Real behavior depends on topology and engine rules.

## Multi-datacenter design

A production cluster may replicate across regions/datacenters.

Prefer topology-aware consistency such as local-quorum concepts when low
cross-region latency matters.

The exact design must follow business consistency requirements.

## Hot partitions

A partition key can be logically correct but operationally hot.

Example:

```text
partition key = global_event_type
```

if every checkout writes:

```text
event_type = purchase
```

One partition/node range becomes overloaded.

Split by:

- tenant,
- time,
- random shard,
- natural entity,

when semantics allow.

## Write sharding

A synthetic shard can spread writes:

```text
partition key = (service, minute, shard)
```

where:

```text
shard = hash(event_id) % 16
```

Reads must query all 16 shards and merge results.

Trade-off:

```text
better write distribution
vs
more read fan-out
```

Use only when the hotspot is real.

## Time-series modeling

A common shape:

```text
(device_id, day) -> timestamp-ordered readings
```

This supports:

- one device,
- one bounded period,
- chronological reads.

It is very different from a warehouse query:

```text
average temperature across every device for 3 years
```

Send global analytics to an analytical system.

## TTL and retention

Wide-column systems often support per-row/cell TTL.

Useful for:

- telemetry retention,
- temporary events,
- session-like records.

High-volume expiration has storage-engine consequences such as tombstones and
compaction work.

Retention is part of physical design.

## Tombstones

A delete/expiration may create a tombstone rather than immediately erasing data
from every replica.

Why:

```text
replica A sees delete
replica B temporarily offline
```

Without a deletion marker, replica B might later reintroduce old data.

Too many tombstones can hurt reads.

## Compaction

LSM-style engines create immutable files over time.

```text
memtable
   │ flush
   ▼
SSTables
   │
   ▼
compaction
```

Compaction:

- merges files,
- removes obsolete values,
- consumes I/O/CPU.

Write-heavy/TTL-heavy workloads need operational planning.

## Read amplification

A read may consult several SSTables/structures.

Compaction strategy and bloom filters can reduce unnecessary work.

This is why "writes are fast" does not mean read cost is free.

## Lightweight transactions

Cassandra provides compare-and-set style lightweight transactions.

They use consensus and cost more than normal writes.

Use them for narrow correctness requirements such as:

- claim a unique name,
- update only if version matches.

Do not make every write an LWT by default.

## Idempotency

Retries can produce repeated writes.

Choose stable identifiers:

```text
event_id
```

so a retried operation can overwrite/deduplicate the same logical record where
appropriate.

## Batch statements

A batch does not automatically make unrelated writes faster.

Use batches for semantic grouping where the database documents that behavior.

Cross-partition batches can increase coordination.

## Clock/time semantics

If time controls clustering and retention:

- use UTC internally,
- define event time versus ingestion time,
- use stable tie-breakers such as event ID.

Two events can share the same timestamp.

## Query-first workflow

For every required query:

1. Write the exact WHERE conditions.
2. Identify the partition key.
3. Decide clustering order.
4. Estimate partition growth.
5. Add time/random bucketing if needed.
6. Decide copied fields.
7. Define write fan-out.
8. Choose consistency level.
9. Define retention/TTL.
10. Test skew and hotspot cases.

## When not to use a wide-column store

A relational database may be simpler when:

- joins are central,
- transactions span many entities,
- query patterns change frequently,
- constraints must be enforced relationally,
- data volume fits conventional scaling.

A wide-column system is not required merely because data is "large."

## Common mistakes

### Relational normalization carried over unchanged

Queries require joins the system is not designed to perform.

### Partition key has low cardinality

Hotspots appear.

### Partition grows forever

Reads/maintenance degrade.

### Every new query uses filtering

Schema does not match access patterns.

### Duplicated data has no ownership rule

Copies drift.

### Global analytics run on transactional partitions

The wrong engine is doing the work.

## Related notes

- [Types of NoSQL databases](02_types_of_nosql_databases.md)
- [Querying NoSQL databases](03_querying_nosql_databases.md)
- [Key-value modeling](06_key_value_modeling.md)
- [Consistency, transactions, and replication](09_consistency_transactions_and_replication.md)
- [Cassandra engine note](../12_database_engines/11_cassandra.md)
- [Partitioning](../06_distributed_databases/02_partitioning.md)
