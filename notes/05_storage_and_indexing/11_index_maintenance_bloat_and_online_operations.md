# Index Maintenance, Bloat, Redundancy, and Online Operations

Indexes have a lifecycle:

~~~text
design
  |
build
  |
observe
  |
maintain
  |
replace or drop
~~~

The difficult part is not creating an index. It is knowing whether the index still earns its write, storage, and operational cost.

## Index maintenance is workload-specific

Avoid rules such as:

~~~text
rebuild every index every Sunday
~~~

or:

~~~text
rebuild when fragmentation > X%
~~~

without understanding the engine and workload.

Different databases expose different concepts:

- PostgreSQL index bloat/page density,
- SQL Server fragmentation/page fullness,
- InnoDB B-tree organization and online DDL,
- SQLite file/page behavior.

The same percentage does not mean the same thing everywhere.

## Index bloat

Bloat broadly means an index occupies substantially more space than its useful entries require.

Causes can include:

- heavy insert/delete churn,
- page splits,
- old/dead entries,
- low page density,
- update patterns.

But:

~~~text
large index != bloated index
~~~

A large healthy index can be completely justified.

## Why files do not shrink immediately

Deletes can make space reusable inside an index without returning the underlying file space to the operating system.

Reusing free pages is often cheaper than shrinking and regrowing the index.

Therefore:

~~~text
delete many rows
~~~

does not imply:

~~~text
index file becomes small immediately
~~~

## PostgreSQL and MVCC

PostgreSQL indexes can contain entries pointing to row versions that are no longer visible to normal queries until cleanup can remove or recycle them.

Long transactions can delay cleanup because old snapshots may still need row versions.

## Monitor object size

PostgreSQL example:

~~~sql
SELECT
    schemaname,
    relname AS table_name,
    indexrelname AS index_name,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
    idx_scan
FROM pg_stat_user_indexes
ORDER BY pg_relation_size(indexrelid) DESC;
~~~

Size and scan count are clues, not verdicts.

## Zero scans does not automatically mean unused

Index statistics can reset.

An index may still be needed for:

- a rare monthly job,
- failover/reporting path,
- uniqueness constraint,
- foreign-key checks,
- incident workflow.

Understand the observation period and purpose before dropping it.

## Constraint-backed indexes

Primary keys and unique constraints are often enforced by indexes.

Do not drop an index simply because application SELECT queries do not use it.

Ask:

~~~text
does this index enforce correctness?
~~~

before treating it as optional.

## Redundant indexes

Examples:

~~~text
index A: (customer_id)
index B: (customer_id, order_date)
~~~

Index B may make A redundant for some workloads, but not always.

Differences include:

- index width,
- scan cost,
- uniqueness,
- sort direction,
- INCLUDE columns,
- partial predicate,
- operator class.

Use plans and workload evidence.

## Duplicate indexes

Two indexes with identical key, predicate, and operator behavior can appear after migrations or tooling mistakes.

They create duplicate write and storage cost.

Inventory schema definitions periodically.

## Write amplification

Every index can add work to:

- INSERT,
- DELETE,
- UPDATE of indexed columns,
- vacuum/cleanup,
- backups,
- replication/WAL.

This is why "just add another index" is not free.

## Building an index on a live table

A normal index build may block writes depending on engine.

On a large table, the build can also consume:

- I/O,
- CPU,
- memory,
- WAL/redo,
- cache capacity.

Plan index deployment as an operational change.

## PostgreSQL CREATE INDEX CONCURRENTLY

PostgreSQL supports:

~~~sql
CREATE INDEX CONCURRENTLY idx_orders_customer_date
ON orders(customer_id, order_date DESC);
~~~

This avoids taking locks that block normal inserts, updates, and deletes for the duration of the build.

Trade-offs include:

- more total work,
- longer build duration,
- multiple scans/waits,
- additional caveats on failure.

It cannot run inside a transaction block.

## Failed concurrent build

A failed concurrent PostgreSQL build can leave an invalid index object.

Invalid indexes are not used for normal queries but can still need cleanup.

After failure:

1. inspect validity,
2. understand the error,
3. drop or rebuild the invalid object as appropriate.

Do not assume failure cleaned up everything.

## Progress monitoring

PostgreSQL exposes:

~~~text
pg_stat_progress_create_index
~~~

for index-build progress.

Production migrations should monitor long-running builds instead of treating them as a black box.

## REINDEX

PostgreSQL can rebuild an index:

~~~sql
REINDEX INDEX idx_orders_customer_date;
~~~

Use cases include:

- corruption recovery,
- significant bloat/pathology,
- applying some storage-parameter changes.

REINDEX is not a routine cure for every slow query.

## REINDEX CONCURRENTLY

For production systems where blocking writes is unacceptable:

~~~sql
REINDEX INDEX CONCURRENTLY idx_orders_customer_date;
~~~

This performs more work and has additional restrictions, but reduces write blocking.

It cannot run inside a transaction block.

## Rebuild versus drop/create

A rebuild can preserve the logical definition while writing a fresh physical structure.

Drop/create can introduce an interval where the access path or constraint is absent unless carefully staged.

For unique or constraint-backed indexes, correctness implications matter.

## Replace-index migration pattern

A safe production pattern can be:

~~~text
create new index concurrently
        |
validate query plans
        |
deploy code if needed
        |
drop old index safely
~~~

This avoids an all-at-once replacement.

## Fillfactor changes

Changing an index storage parameter does not necessarily rewrite existing pages immediately.

A rebuild may be required for the new layout to apply fully.

Do not change fillfactor without a measured write or page-density problem.

## Online operations are not free

Online or concurrent usually means foreground reads and writes can continue, not that the operation has zero impact.

It can still increase:

- disk throughput,
- WAL/log rate,
- CPU,
- replica lag,
- query latency.

Run large builds during controlled periods and monitor them.

## Replica impact

Index creation or rebuild can generate changes that replicas must receive or replay depending on engine.

Large maintenance can increase replication lag.

Check failover and read-replica health during the operation.

## Indexes and backups

More indexes increase backup size or restore/rebuild time depending on backup method.

For logical backups, indexes may be rebuilt during restore.

For physical backups, index files are often included.

Storage cost extends beyond the primary server.

## Statistics after index creation

A new ordinary index can be considered immediately, but table and expression statistics still influence plan choice.

After major data/index changes, ensure statistics describe the current workload.

## Validate with plans

After creating an index:

~~~text
index exists
~~~

does not imply:

~~~text
important query uses it
~~~

Inspect EXPLAIN and actual plans.

If the optimizer ignores the index, investigate:

- selectivity,
- expression mismatch,
- stale statistics,
- ordering,
- result size,
- cost model.

Do not force the index automatically.

## Dropping an index

Before dropping:

1. identify constraint ownership,
2. inspect usage over a meaningful period,
3. search application/report queries,
4. consider rare jobs,
5. estimate rollback/recreate time.

On large tables, recreating a dropped index can be expensive.

## PostgreSQL DROP INDEX CONCURRENTLY

PostgreSQL supports concurrent index drop for eligible cases:

~~~sql
DROP INDEX CONCURRENTLY idx_old;
~~~

This can reduce blocking on a live system.

Restrictions apply, so use current engine documentation for production migrations.

## Index inventory

A useful inventory records:

- index name,
- definition,
- size,
- uniqueness,
- constraint ownership,
- partial predicate,
- scan count,
- validity,
- last review/change.

This helps prevent years of accidental index accumulation.

## Migration review checklist

When a pull request adds an index, ask:

1. Which query requires it?
2. What plan exists before?
3. What plan is expected after?
4. How large will the index be?
5. What writes become more expensive?
6. Is a similar index already present?
7. Can it be partial or covering instead?
8. How is it built safely in production?
9. How is rollback handled?
10. How will usefulness be measured after deployment?

## Runnable PostgreSQL inventory exercise

This chapter adds:

~~~text
scripts/indexing/postgres_index_inventory.sql
~~~

Run:

~~~bash
docker exec -i postgres-local \
  psql -U demo -d test \
  < scripts/indexing/postgres_index_inventory.sql
~~~

It reports user indexes with definitions, sizes, uniqueness, validity, and scan counters.

The exercise is read-only.

## Common mistakes

- Scheduled rebuilds with no measured problem.
- Dropping an index based only on zero scan count.
- Forgetting constraint-backed indexes.
- Adding duplicate or overlapping indexes through separate migrations.
- Assuming concurrent/online builds have no production impact.
- Creating an index without validating the query plan.
- Dropping an index without estimating recreate time.

## Related notes

- [B-tree internals](06_btree_internals_and_page_splits.md)
- [Composite indexes](07_composite_indexes_and_column_order.md)
- [Covering, partial, and expression indexes](08_covering_partial_and_expression_indexes.md)
- [Write performance, vacuum, and bloat](../08_database_performance/12_write_performance_vacuum_and_bloat.md)
- [Performance monitoring](../11_security_best_practices/05_performance_monitoring_and_tuning.md)
