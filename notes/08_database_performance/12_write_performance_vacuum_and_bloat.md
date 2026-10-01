# Write Performance, Vacuum, Bloat, and Maintenance

Read performance is only half of database performance.

Every extra index, materialized result, and replica can add work to INSERT, UPDATE, and DELETE.

A healthy design balances read speed with sustainable writes and maintenance.

## Write amplification

One logical row insert may require:

~~~text
table page write
+ primary-key index
+ secondary indexes
+ WAL/redo
+ replica traffic
+ CDC
+ materialized structures
~~~

The application issued one INSERT, but the storage system performs more work.

## Index write cost

Each secondary index must be updated when relevant columns change.

Suppose a table has eight indexes.

One insert may update all eight index trees.

This can reduce write throughput and increase:

- WAL/redo,
- page splits,
- cache churn,
- disk usage.

## Runnable index write-cost demo

The repository adds:

scripts/performance/sqlite_index_write_cost_demo.py

Run:

~~~bash
python scripts/performance/sqlite_index_write_cost_demo.py
~~~

It inserts the same synthetic workload into:

- a minimally indexed table,
- a table with several secondary indexes,

then reports local insert time and database size.

The exact numbers are machine-specific. The point is to make index maintenance cost visible.

## Updating indexed columns

An UPDATE to an indexed column can require new index entries.

If a frequently changing field is indexed only for a rare query, the write cost may not be justified.

Review indexes against both reads and writes.

## PostgreSQL MVCC

PostgreSQL uses multiversion concurrency control.

An UPDATE generally creates a new row version rather than overwriting in place.

Old versions remain until no transaction needs them and vacuum can reclaim/reuse space.

~~~text
old tuple version
      |
      v
new tuple version
      |
old becomes dead later
~~~

This supports concurrency but creates maintenance work.

## Dead tuples

Frequent UPDATE/DELETE workloads produce dead tuples.

Symptoms can include:

- table/index growth,
- more pages scanned,
- vacuum work,
- cache inefficiency.

Monitor n_dead_tup as a signal, not a perfect measure.

## Vacuum

Vacuum makes dead tuple space reusable and performs visibility/freeze maintenance.

Autovacuum is essential in PostgreSQL.

Do not disable it as a performance "optimization" without deep understanding.

## Vacuum does not always shrink files

Normal vacuum can mark space reusable inside the table without returning it to the operating system.

This is often desirable because future writes reuse the space.

File shrink/rewrite operations are more disruptive.

## Bloat

Bloat broadly means physical storage substantially exceeds useful live data due to churn and page behavior.

But:

~~~text
large table != bloated table
~~~

A large healthy table can be correctly sized.

Investigate with:

- live/dead rows,
- object size,
- workload churn,
- engine-specific bloat tools.

## Long transactions block cleanup

A long transaction can keep old row versions visible.

~~~text
long snapshot
      |
      v
vacuum cannot remove versions it might still need
      |
      v
bloat grows
~~~

Monitor transaction age.

## Idle in transaction

An application that starts a transaction and waits can be particularly harmful.

Fix application transaction boundaries rather than increasing vacuum aggressiveness alone.

## HOT updates

PostgreSQL can sometimes perform Heap-Only Tuple updates when indexed columns are unchanged and page conditions allow it.

This can reduce index maintenance.

Designing indexes carefully can therefore improve write performance indirectly.

## Fillfactor

Lower fillfactor leaves space on pages for future updates.

Trade-off:

- more storage,
- potentially fewer page splits/moves for update-heavy tables.

Tune only for measured workloads.

## Page splits

B-tree inserts into full pages can split pages.

Random key distributions and monotonic keys behave differently depending on engine/storage architecture.

Do not assume one primary-key style is always fastest.

## Sequential versus random keys

Monotonic IDs can improve locality in many B-tree engines.

But in distributed range-sharded databases they can create a hot range.

Physical architecture matters.

## WAL/redo

Durable writes generate transaction log records.

Monitor:

- WAL bytes/sec,
- archive backlog,
- replica lag,
- checkpoint pressure.

A bulk update can saturate log/storage even when CPU is low.

## fsync and durability

Disabling durable flushes can make benchmarks look faster by weakening durability.

Do not compare durable production configuration with unsafe benchmark settings.

Performance is meaningless if the guarantee changed.

## Checkpoints

Checkpoints bound recovery work but can create write pressure.

Too frequent:

- repeated page writes,
- I/O spikes.

Too infrequent:

- more recovery/log retention.

Use measured checkpoint/WAL behavior.

## Batch writes

Batching reduces round trips, but giant batches can create:

- long transactions,
- large WAL bursts,
- lock duration,
- replication lag.

Use bounded batches.

## Delete versus partition drop

Deleting billions of expired rows can generate enormous work.

For time-partitioned retention:

~~~text
drop old partition
~~~

can be dramatically cheaper and simpler.

See the partitioning note.

## Soft deletes

A column such as:

~~~text
deleted_at
~~~

preserves rows logically.

But if most queries filter active rows, the table keeps growing.

Consider:

- partial indexes,
- archival,
- retention cleanup.

Soft delete is a product/audit decision with performance cost.

## Tombstone-style patterns

Different engines handle deletes differently.

LSM/wide-column stores may retain tombstones until compaction/repair rules allow cleanup.

High TTL/delete rates can hurt read performance.

Maintenance behavior is engine-specific.

## Autovacuum tuning

PostgreSQL autovacuum thresholds depend on table change volume and configuration.

Large/high-churn tables may need table-specific tuning.

Tune based on:

- dead tuple growth,
- vacuum duration,
- transaction age,
- workload.

Do not copy settings blindly.

## Analyze

Vacuum and ANALYZE solve related but different problems.

ANALYZE updates statistics for the optimizer.

Vacuum handles dead tuple/reuse/visibility maintenance.

Both matter.

## Reindex

Indexes can sometimes benefit from rebuild/reindex due to corruption or significant bloat/pathology.

Routine scheduled rebuilds without evidence create unnecessary load.

Measure first.

## Online/concurrent maintenance

Production systems may need concurrent/online forms of:

- index creation,
- index rebuild,
- schema migration.

These reduce blocking but often take longer and consume more background resources.

Understand the engine's locking behavior.

## Materialized view refresh

Refreshing a materialized result is write work.

A large refresh can:

- scan source tables,
- write the full result,
- create WAL,
- compete with user traffic.

Schedule and monitor it like a batch workload.

## Replication lag from write bursts

A primary may accept a write burst faster than replicas can replay it.

Monitor lag during:

- backfills,
- imports,
- index builds,
- large updates.

Throttle if read freshness/failover readiness matters.

## CDC and downstream cost

Change-data capture sends write volume downstream.

One bulk update of 100 million rows can create 100 million change events.

Coordinate with:

- Kafka,
- search indexers,
- warehouses,
- caches.

The database may survive while downstream systems fail.

## Archival

Move cold data when:

- operational queries rarely need it,
- retention requires preservation,
- active indexes become too large.

Possible targets:

- partition archive,
- object storage,
- warehouse.

Keep restore/query requirements explicit.

## Maintenance windows

Not every operation can be invisible.

Plan windows for:

- major version upgrades,
- table rewrites,
- large reindex operations,
- storage migrations.

Test duration on representative data.

## Write performance checklist

1. How many indexes does each hot table maintain?
2. Which indexed columns change frequently?
3. What WAL/redo rate do writes generate?
4. Is replication keeping up?
5. Are transactions short?
6. Is autovacuum/cleanup healthy?
7. Is table/index growth expected or bloat?
8. Can retention use partition drop?
9. Do bulk jobs need throttling?
10. Will CDC/downstream systems survive backfills?
11. Are durability settings equivalent in benchmarks?
12. Are maintenance operations tested at scale?

## Common mistakes

- Adding indexes without measuring write cost.
- Disabling autovacuum.
- Treating every large file as bloat.
- Keeping transactions open during external calls.
- Giant backfills with no replication/CDC monitoring.
- Routine reindexing without evidence.
- Benchmarking with weakened durability.
- Row-by-row retention deletes when partition lifecycle fits.

## Related notes

- [Indexing strategies](02_indexing_strategies.md)
- [Materialized views](04_materialized_views.md)
- [Partitioning and sharding](10_partitioning_sharding_and_data_locality.md)
- [Performance monitoring](../11_security_best_practices/05_performance_monitoring_and_tuning.md)
- [PostgreSQL engine note](../12_database_engines/03_postgresql.md)
