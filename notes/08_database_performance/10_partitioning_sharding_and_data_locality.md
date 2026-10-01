# Partitioning, Sharding, and Data Locality for Performance

Large datasets can be divided so queries touch less data and maintenance works on smaller units. The terms are related but not interchangeable.

## Partitioning versus sharding

Partitioning usually means dividing one logical table into pieces.

~~~text
orders
├── orders_2026_01
├── orders_2026_02
└── orders_2026_03
~~~

Sharding usually means distributing data across independent servers or database instances.

~~~text
tenant A-C -> shard 1
tenant D-M -> shard 2
tenant N-Z -> shard 3
~~~

Partitioning can exist on one server. Sharding introduces distributed-system costs.

## Why partition

Useful goals include:

- partition pruning,
- smaller indexes,
- easier archival/drop,
- lower maintenance scope,
- time-based lifecycle management.

Partitioning does not automatically make every query faster.

## Partition pruning

Suppose events are partitioned by month.

Query:

~~~sql
WHERE event_time >= '2026-10-01'
  AND event_time <  '2026-11-01'
~~~

A compatible partition key can let the engine avoid unrelated months.

~~~text
12 monthly partitions
query needs October
        |
        v
scan October only
~~~

This reduces work when pruning is effective.

## Partition key must match access patterns

If most queries filter by tenant but the table is partitioned only by year, pruning may not help tenant queries.

Choose from real access patterns and lifecycle requirements.

## Range partitioning

Natural for:

- time,
- ordered numeric ranges,
- archival windows.

Example:

~~~text
2026-01
2026-02
2026-03
~~~

Advantages:

- simple retention,
- easy time-window pruning.

Risk:

- hottest writes may concentrate in newest partition.

## Hash partitioning

Hashing a key can spread rows more evenly.

~~~text
hash(customer_id) % 16
~~~

Advantages:

- distribution.

Trade-off:

- range/time pruning may be weaker,
- reading one time window may touch many partitions.

## List partitioning

Useful for discrete groups:

~~~text
region = EU
region = US
region = APAC
~~~

Be careful with uneven groups.

## Too many partitions

Thousands of tiny partitions can increase:

- planning overhead,
- metadata overhead,
- maintenance complexity,
- open-file/object count.

A partitioning scheme needs a bounded lifecycle.

## Too few partitions

One giant partition defeats many benefits.

Estimate:

- rows per partition,
- bytes per partition,
- index size,
- maintenance duration.

## Local indexes versus global indexes

Index behavior differs by engine.

Some systems maintain indexes per partition; others support global structures.

Operational implications include:

- partition detach/drop behavior,
- unique constraints,
- rebuild cost.

Check exact engine semantics.

## Unique constraints across partitions

A uniqueness rule such as:

~~~text
email must be unique globally
~~~

may be difficult if the partition key does not participate in the unique index.

Partitioning is a correctness/schema decision too.

## Partition maintenance

Time-based retention can be cheap:

~~~text
DROP old partition
~~~

instead of:

~~~text
DELETE billions of old rows
~~~

Dropping a partition can avoid enormous row-by-row delete and vacuum work.

## Partitioning is not sharding

Partitioning a PostgreSQL table into 100 pieces on one host does not create 100 machines.

CPU, memory, and storage limits still belong to that server.

## Sharding

Sharding routes each row/entity to one database node or group.

Common shard keys:

- tenant ID,
- customer ID,
- account ID,
- hashed identifier.

Good shard keys provide:

- balanced load,
- data locality,
- predictable routing.

## Data locality

If one transaction needs rows that share a shard key, those rows can stay together.

~~~text
customer 42
├── profile
├── cart
└── orders
       |
       v
same shard
~~~

This reduces distributed coordination.

## Cross-shard query

Global query:

~~~text
top 100 products across all shards
~~~

may require:

1. query each shard,
2. transfer partial results,
3. merge/sort globally.

Distributed data movement can dominate local SQL time.

## Cross-shard transaction

A transaction spanning shards requires coordination.

~~~text
shard A
   \
    coordinator
   /
shard B
~~~

This increases latency and failure handling complexity.

Design shard boundaries around high-value transaction locality when possible.

## Hot shards

A shard key can be logically correct but uneven.

Example:

~~~text
tenant_id
~~~

when one tenant represents 60 percent of traffic.

That tenant becomes a hot shard.

Possible solutions:

- dedicated shard for large tenant,
- sub-shard by another key,
- workload isolation,
- rebalance.

## Hash distribution trade-off

Hashing often improves balance.

But it can destroy locality for range queries.

~~~text
good:
point lookup by customer_id

harder:
scan customers 1000 through 2000 in key order
~~~

Choose based on workload.

## Time-series write hotspot

Partitioning by event date can place all current writes in one partition.

That may be fine on one database if the partition is not itself a separate node.

In distributed systems, monotonically increasing range keys can create a single hot range/node.

Understand the engine's physical distribution.

## Secondary indexes in sharded systems

An index lookup may need to fan out if the shard key is unknown.

Example:

~~~text
WHERE email = ?
~~~

but shards are routed by:

~~~text
customer_id
~~~

Possible strategies:

- global secondary index,
- lookup directory,
- duplicate mapping table,
- broadcast query.

Each adds maintenance or coordination cost.

## Resharding

Data distribution changes as the system grows.

Plan for:

- adding shards,
- moving ranges/tenants,
- balancing,
- routing updates,
- background copy/replay,
- validation.

A shard key that cannot be changed may become a long-term constraint.

## Replication and sharding

Each shard often has replicas.

~~~text
shard 1 -> primary + replicas
shard 2 -> primary + replicas
~~~

Sharding solves capacity distribution.

Replication solves availability/read scaling.

They are separate dimensions.

## Read replicas

Read replicas can offload some reads without sharding.

This is often simpler when the primary can still handle writes.

Trade-off:

- replica lag,
- read-after-write semantics.

Do not shard before simpler scaling options are exhausted.

## Vertical scaling first?

Larger CPU/RAM/storage can be the simplest performance improvement.

Vertical scaling has limits, but it preserves operational simplicity.

Compare:

~~~text
bigger single system
vs
distributed sharded system
~~~

including engineering cost.

## Table partitioning and query design

A query must expose the partition predicate.

Less useful:

~~~sql
WHERE DATE(event_time) = '2026-10-01'
~~~

Potentially better:

~~~sql
WHERE event_time >= '2026-10-01'
  AND event_time <  '2026-10-02'
~~~

The second form is easier for many optimizers to prune.

## Partition-wise joins

Some engines can join matching partitions independently when partition schemes align.

This can reduce memory/data movement.

It requires compatible partition keys and engine support.

## Locality in warehouses

Analytical systems also use:

- partitioning,
- clustering/sort keys,
- distribution keys.

The goal is the same:

~~~text
read less data
move less data
~~~

but the physical implementation differs from OLTP systems.

## When partitioning helps

Good candidates:

- very large time-series tables,
- retention by time window,
- maintenance that needs smaller units,
- queries that filter strongly by partition key.

## When partitioning may not help

If:

- table is small,
- queries need all partitions,
- partition key is rarely filtered,
- partition count is excessive,

partitioning can add complexity without reducing work.

## Sharding decision checklist

Before sharding:

1. Is the current bottleneck measured?
2. Can indexes/query changes fix it?
3. Can vertical scaling help?
4. Can caching or read replicas help?
5. What is the natural shard key?
6. Are writes evenly distributed?
7. Which transactions cross shards?
8. Which queries need global fan-out?
9. How will uniqueness work?
10. How will resharding work?
11. What happens during partial shard failure?
12. Can the team operate distributed backups/restores?

## Common mistakes

- Partitioning with no pruning benefit.
- Thousands of tiny partitions.
- Calling partitioning "horizontal scaling" when still on one host.
- Sharding by tenant without accounting for giant tenants.
- Ignoring cross-shard transactions.
- No resharding plan.
- Assuming replicas replace sharding or backups.

## Related notes

- [Working with billion-row tables](06_working_with_billion_row_table.md)
- [Partitioning](../06_distributed_databases/02_partitioning.md)
- [Replication](../06_distributed_databases/03_replication.md)
- [Query optimization](01_query_optimization_techniques.md)
