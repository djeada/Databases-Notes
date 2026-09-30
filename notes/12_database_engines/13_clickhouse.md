# ClickHouse

ClickHouse is a column-oriented SQL database designed for analytical workloads over large datasets. It is commonly used for:

- real-time analytics,
- product/application analytics,
- observability data,
- event analytics,
- large aggregations,
- analytical APIs,
- data warehousing.

It is optimized for scans and aggregations over many rows rather than OLTP-style point updates and row-by-row transactional workflows.

Official resources:

- [ClickHouse documentation](https://clickhouse.com/docs/)
- [ClickHouse overview](https://clickhouse.com/clickhouse)
- [Getting started with ClickHouse](https://clickhouse.com/learn)

## OLTP versus OLAP

A transactional database often handles:

```text
INSERT one order
UPDATE one account
SELECT one customer by primary key
```

ClickHouse is designed for workloads like:

```text
scan 2 billion events
filter one month
group by country + device
compute count, revenue, percentile
return result quickly
```

Conceptually:

```text
OLTP
row -> row -> row

OLAP
column scans over huge ranges
      │
      ▼
vectorized aggregation
```

## Columnar storage

Suppose a table has:

```text
event_time | user_id | country | device | revenue
```

A query asks:

```sql
SELECT country, SUM(revenue)
FROM events
GROUP BY country;
```

A row-oriented engine reads row structures containing all fields.

A column-oriented engine can focus primarily on:

```text
country column
revenue column
```

This reduces I/O for analytical queries that touch only a subset of columns.

Columnar layouts also compress similar values efficiently.

## Local setup

The repository includes:

[`scripts/clickhouse/docker-compose.yml`](../../scripts/clickhouse/docker-compose.yml)

Start:

```bash
cd scripts/clickhouse
docker compose up -d
docker compose ps
```

Open the client:

```bash
docker exec -it clickhouse-notes clickhouse-client
```

Check version:

```sql
SELECT version();
```

Stop:

```bash
docker compose down
```

Use `docker compose down -v` only if you want to remove the demo volume.

## Runnable demo

The repository includes:

[`scripts/clickhouse/demo.sql`](../../scripts/clickhouse/demo.sql)

Run:

```bash
docker exec -i clickhouse-notes   clickhouse-client   --multiquery < demo.sql
```

The script:

1. creates an events table,
2. inserts sample rows,
3. performs grouped analytics,
4. demonstrates the effect of the sorting key.

## MergeTree

The most important ClickHouse table-engine family is **MergeTree**.

Example:

```sql
CREATE TABLE events (
    event_time DateTime,
    user_id UInt64,
    country LowCardinality(String),
    event_type LowCardinality(String),
    revenue Decimal(12, 2)
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(event_time)
ORDER BY (country, event_type, event_time);
```

The two clauses most beginners need to reason about are:

- `PARTITION BY`,
- `ORDER BY`.

They solve different problems.

## ORDER BY

In MergeTree tables, `ORDER BY` defines the physical sort key and sparse primary index behavior.

Example:

```sql
ORDER BY (customer_id, event_time)
```

is useful for queries like:

```sql
SELECT *
FROM events
WHERE customer_id = 42
  AND event_time >= now() - INTERVAL 7 DAY;
```

Conceptually:

```text
sorted data parts

customer 1  ...
customer 1  ...
customer 2  ...
customer 2  ...
customer 42 ...
customer 42 ...
```

The engine can skip large ranges that cannot contain the requested key prefix.

The sort key should follow important filtering and grouping patterns.

## Sparse primary index

ClickHouse's primary index is not a traditional one-entry-per-row B-tree.

It stores marks over data granules.

Conceptually:

```text
rows 0..8191       -> mark
rows 8192..16383   -> mark
rows 16384..24575  -> mark
...
```

The index helps skip granules.

This design is efficient for analytical scans but behaves differently from an OLTP B-tree.

Do not expect arbitrary point lookup patterns to perform like PostgreSQL/MySQL indexes.

## PARTITION BY

Partitions group data into larger management units.

Example:

```sql
PARTITION BY toYYYYMM(event_time)
```

creates monthly partitions.

```text
202608
202609
202610
```

Partitioning is useful for:

- dropping old data,
- retention management,
- moving/detaching data,
- reducing some scans.

Do not partition by highly cardinal values such as user ID.

Too many partitions create metadata and merge overhead.

## Data parts

Writes create immutable **parts**.

```text
INSERT batch A -> part A
INSERT batch B -> part B
INSERT batch C -> part C
```

Background merges combine them:

```text
part A ─┐
part B ─┼──► larger part
part C ─┘
```

This is why insert batching matters.

Thousands of tiny inserts can produce too many small parts and overwhelm merge work.

## Insert in batches

Bad pattern:

```text
INSERT one row
INSERT one row
INSERT one row
...
millions of times
```

Better:

```text
batch thousands of rows
      │
      ▼
one INSERT
```

For streaming ingestion, use a buffering/connector strategy that sends reasonable blocks.

The exact optimal batch size depends on row size, latency requirements, and deployment.

## Example analytical query

```sql
SELECT
    country,
    event_type,
    count() AS events,
    sum(revenue) AS revenue,
    uniqExact(user_id) AS users
FROM events
WHERE event_time >= now() - INTERVAL 30 DAY
GROUP BY
    country,
    event_type
ORDER BY revenue DESC;
```

This is the kind of scan/aggregate workload ClickHouse is built around.

## Approximate aggregates

At large scale, exact distinct counts can be expensive.

ClickHouse offers approximate aggregation functions for many use cases.

For example, distinct-user counting can use approximate algorithms when the product can tolerate small error.

Conceptually:

```text
exact:
store/compare many distinct values

approximate:
compact probabilistic state
       │
       ▼
small error, much lower memory
```

Choose exactness based on business requirements.

## LowCardinality

Columns with repeated string values such as:

```text
country
device_type
event_type
status
```

can benefit from `LowCardinality(String)`.

Conceptually:

```text
dictionary:
1 -> DE
2 -> US
3 -> FR

column:
1 1 2 1 3 2 ...
```

This can reduce storage and improve some operations.

Use it for genuinely low-cardinality values, not unique IDs.

## Compression

Columnar data with similar adjacent values compresses well.

Good sort-key design can improve compression because related values become physically close.

Example:

```text
sorted by country:
DE DE DE DE FR FR FR US US US
```

often compresses better than:

```text
DE US FR DE US DE FR ...
```

Storage design and query design are connected.

## Materialized views

ClickHouse materialized views can transform/aggregate data during ingestion.

Example architecture:

```text
raw events
    │
INSERT
    ▼
source table
    │
    └──► materialized view
              │
              ▼
       aggregated table
```

This is useful for:

- pre-aggregated dashboards,
- rollups,
- derived table pipelines.

It shifts computation from read time toward ingestion time.

## AggregatingMergeTree

Specialized MergeTree engines can store intermediate aggregate states.

This supports incremental rollups.

Use specialized engines only after understanding merge semantics; they are not interchangeable with normal relational tables.

## ReplacingMergeTree

`ReplacingMergeTree` can help deduplicate versions during merges.

Important:

> Background deduplication is not immediate.

A query can temporarily see multiple versions unless it uses the appropriate querying strategy.

Do not treat `ReplacingMergeTree` as a traditional uniqueness constraint.

## Updates and deletes

ClickHouse historically emphasized append-heavy analytical workloads.

Modern versions provide mutation and lightweight-update capabilities, but frequent OLTP-style updates remain a different workload from its core design.

If the application needs:

- constant row-by-row updates,
- strict uniqueness constraints,
- foreign keys,
- many small transactions,

use an OLTP database as the source of truth and replicate events/data into ClickHouse.

## Common architecture

```text
PostgreSQL / MySQL
       │
       │ CDC
       ▼
Kafka / connector
       │
       ▼
ClickHouse
       │
       ├── dashboards
       ├── analytical APIs
       └── data science
```

The relational database handles transactions.

ClickHouse handles large analytical reads.

## Kafka integration

ClickHouse can consume data from event pipelines through connectors and Kafka-related integration patterns.

A typical design:

```text
application
    │
    ▼
Kafka
    │
    ▼
ingestion layer
    │
    ▼
ClickHouse MergeTree tables
```

Operationally, ensure:

- replay is safe,
- duplicate events are handled,
- schema changes are controlled,
- batch sizes are reasonable.

## TTL

Retention can be expressed in table definitions.

Conceptually:

```text
events older than 90 days
       │
       ▼
expire / move according to TTL
```

This is useful for logs, telemetry, and product analytics.

Retention should align with:

- compliance,
- debugging needs,
- storage cost,
- backup strategy.

## Sharding

A large deployment can shard data across nodes.

```text
client
  │
  ▼
distributed table
  │
  ├──► shard 1
  ├──► shard 2
  └──► shard 3
```

Queries can fan out across shards and merge results.

Sharding introduces network and distributed-query cost.

Scale vertically first when one node still comfortably meets requirements.

## Replication

Replicated MergeTree-family engines maintain copies across replicas in self-managed deployments.

```text
shard 1
├── replica A
└── replica B
```

Replication improves availability.

It does not replace backups or disaster recovery.

## ClickHouse Keeper

ClickHouse Keeper provides coordination for replicated/distributed ClickHouse deployments.

It serves a role similar to ZooKeeper-style coordination.

A single-node local demo does not need the same topology as a production replicated cluster.

## ClickHouse Cloud

Managed ClickHouse reduces infrastructure work such as cluster operation, scaling, and platform maintenance.

Self-managed ClickHouse provides more infrastructure control.

The trade-off is:

```text
managed:
less operations, service cost/platform constraints

self-managed:
more control, more operational responsibility
```

Evaluate workload cost, compliance, cloud placement, and team expertise.

## ClickHouse versus a warehouse

Managed warehouses such as BigQuery, Snowflake, and Redshift also target analytics.

ClickHouse is often attractive when:

- low-latency analytical APIs matter,
- event/log analytics dominate,
- high query concurrency is important,
- teams want an open-source analytical engine,
- cost/performance on large scans is important.

A warehouse may be simpler when:

- BI/ELT workflows dominate,
- fully managed SQL is the priority,
- the existing analytics stack is already warehouse-centric.

Benchmark representative queries.

## ClickHouse versus OpenSearch

ClickHouse:
- strong at structured aggregations,
- columnar scans,
- numerical/event analytics.

OpenSearch:
- strong at full-text search,
- relevance,
- document search,
- faceting.

For logs, either may be valid depending on query shape.

```text
"find logs containing this phrase"
        -> search engine strength

"p95 latency by service for 90 days"
        -> columnar analytics strength
```

## ClickHouse versus PostgreSQL

Use PostgreSQL for:

- transactional state,
- constraints,
- frequent updates,
- relational application logic.

Use ClickHouse for:

- very large analytical scans,
- event data,
- real-time dashboards,
- aggregation-heavy APIs.

Many systems use both.

## Observability

Monitor:

- query latency,
- insert throughput,
- active parts,
- merge backlog,
- disk usage,
- memory,
- query memory failures,
- replication queue,
- rejected/failed inserts,
- background pool saturation.

A `Too many parts` error is usually a sign that inserts are producing parts faster than merges can consolidate them.

## Query profiling

Use system tables and query logs to inspect:

- rows read,
- bytes read,
- memory,
- duration,
- selected parts,
- selected granules.

A fast-looking SQL statement may still scan far more data than necessary because of a poor sorting key.

## Common mistakes

### Choosing ORDER BY randomly

It is the core physical design decision.

### Over-partitioning

Thousands or millions of partitions create overhead.

### One-row inserts

Batch writes.

### Treating ReplacingMergeTree as immediate uniqueness

Merge-based deduplication has different semantics.

### Using ClickHouse as OLTP by default

It is an analytical database.

### Storing data without retention planning

Event tables can grow extremely quickly.

## Design checklist

Before creating a table:

1. What are the most important queries?
2. Which filters appear first?
3. What should the `ORDER BY` key be?
4. Is partitioning needed, and at what granularity?
5. What is expected insert batch size?
6. How long is data retained?
7. Is data append-only or frequently updated?
8. Is replication required?
9. Will data come from Kafka/CDC?
10. What query latency and concurrency are expected?

## Related notes

- [OpenSearch and Elasticsearch](12_elasticsearch_and_opensearch.md)
- [Data warehousing](../13_big_data/01_data_warehousing.md)
- [Spark SQL](../13_big_data/03_spark_sql.md)
- [Data lakes and lakehouses](../13_big_data/04_data_lakes_and_lakehouses.md)
- [Choosing a database](07_choosing_database.md)
