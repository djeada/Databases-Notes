# Execution Plans, Statistics, and Cardinality Estimation

A database optimizer estimates costs from table metadata, statistics, predicates, indexes, join algorithms, and its cost model. It does not execute every possible plan and pick the fastest one.

## Logical query versus physical plan

SQL describes a result:

~~~sql
SELECT o.order_id, o.order_date
FROM orders AS o
WHERE o.customer_id = 42
  AND o.status = 'open'
ORDER BY o.order_date DESC
LIMIT 20;
~~~

The optimizer chooses physical work:

~~~text
possible plan A
index lookup by customer/status
        |
        v
already ordered rows
        |
        v
LIMIT 20

possible plan B
table scan
   |
filter
   |
sort
   |
LIMIT 20
~~~

The SQL text does not require either plan.

## Estimated versus actual rows

Cardinality is the number of rows a plan node is expected to produce.

Suppose the optimizer estimates:

~~~text
10 rows
~~~

but the operation actually returns:

~~~text
2,000,000 rows
~~~

That error can change join order, join algorithm, memory allocation, parallelism, and index/scan choice.

A large estimated-versus-actual mismatch is often more informative than the name of a plan node.

## PostgreSQL EXPLAIN

Plan without executing:

~~~sql
EXPLAIN
SELECT *
FROM orders
WHERE customer_id = 42;
~~~

Plan with runtime information:

~~~sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT *
FROM orders
WHERE customer_id = 42;
~~~

ANALYZE executes the statement. Use caution with UPDATE, DELETE, and expensive production reads.

## SQLite query plan

SQLite exposes:

~~~sql
EXPLAIN QUERY PLAN
SELECT ...;
~~~

The repository adds a runnable exercise:

scripts/performance/sqlite_query_plan_demo.py

Run:

~~~bash
python scripts/performance/sqlite_query_plan_demo.py
~~~

The script creates synthetic orders, shows the plan before an index, creates a composite index, shows the changed plan, and times repeated lookups. The local timings are evidence for that machine only; the important lesson is the changed access path.

## Scan does not mean bad

A table or sequential scan can be correct when:

- the table is small,
- most rows are needed,
- the filter is not selective,
- random index access costs more than scanning.

Do not optimize for the word "scan." Optimize measured work.

## Index scan does not mean good

An index can still be expensive when it returns a huge fraction of the table.

Example:

~~~text
status = 'active'
~~~

If 98 percent of rows are active, a scan may be cheaper.

## Selectivity

A predicate is selective when it matches a small fraction of rows.

Examples:

~~~text
order_id = 918273        -> highly selective
country = 'US'           -> maybe not selective
is_deleted = false       -> often not selective
~~~

Selectivity depends on actual data distribution.

## Histograms and frequency statistics

Optimizers maintain summaries rather than remembering every value.

Statistics can include:

- distinct-value counts,
- null fraction,
- frequent values,
- histograms/ranges,
- multicolumn correlation depending on engine.

These statistics drive row-count estimates.

## Skew

Uniform assumptions fail on skewed data.

~~~text
tenant A -> 70 percent of rows
tenant B -> 10 percent
others   -> 20 percent
~~~

The same query template can behave very differently for the largest tenant and a tiny tenant.

Test representative parameters.

## Correlated columns

Columns can be strongly related.

Example:

~~~text
country = DE
currency = EUR
~~~

An optimizer may estimate independent probabilities when the columns are correlated. Some engines support extended/multicolumn statistics to improve these cases.

## Stale statistics

After a bulk load, archive, migration, or large backfill, statistics may no longer describe the table.

Symptoms include:

- sudden plan changes,
- estimated/actual row mismatch,
- unexpected join order.

PostgreSQL can refresh statistics with:

~~~sql
ANALYZE orders;
~~~

Normal auto-analyze usually handles ordinary workloads; unusual bulk changes can justify explicit maintenance.

## Join order

A filtered small input joined to a large table is often cheaper than joining large unfiltered inputs first.

The optimizer uses cardinality estimates to choose the join tree. Bad estimates can therefore cause bad join order.

## Nested loop

Conceptually:

~~~text
for each row in outer input:
    find matching rows in inner input
~~~

Good when the outer input is small and inner lookup is cheap/indexed.

Bad when the outer input is unexpectedly huge.

## Hash join

A hash join builds an in-memory hash structure from one input and probes it with the other.

It is common for equality joins. Memory pressure can cause spill/extra I/O.

## Merge join

A merge join works with sorted inputs and can be efficient when both sides are already ordered or cheaply scanned in order.

No join algorithm is universally best.

## Sorts

A plan may sort because ordering, grouping, a window function, or a merge join requires it.

Check:

- rows sorted,
- memory used,
- whether it spills to disk.

Sorting 20 rows is irrelevant. Sorting 200 million rows may dominate the query.

## Rows removed by filter

A plan that reads 10,000,000 rows and returns 50 is doing substantial extra work.

Possible improvements include:

- better index,
- partition pruning,
- query rewrite,
- precomputed result.

## Buffers

PostgreSQL buffer information helps show work volume.

At a high level:

- shared hit means a page was already in PostgreSQL shared buffers,
- shared read means a page was read into those buffers.

Operating-system and storage caches also affect elapsed time.

## Cold versus warm cache

The first run may read storage; later runs may reuse memory.

Do not compare a cold "before" run with a warm "after" run and attribute the full difference to an index or query rewrite.

## Prepared statements and parameter sensitivity

The same prepared query can receive dramatically different parameters.

~~~text
tenant = tiny_customer
tenant = largest_customer
~~~

Some engines choose generic or cached plans. If latency varies strongly by parameter, investigate parameter sensitivity rather than assuming random slowness.

## Sargable predicates

Index-friendly range:

~~~sql
WHERE created_at >= '2026-10-01'
  AND created_at <  '2026-10-02'
~~~

Potentially less friendly:

~~~sql
WHERE DATE(created_at) = '2026-10-01'
~~~

A function on an indexed column can prevent a normal range access path unless a matching expression index exists.

## Expression indexes

PostgreSQL example:

~~~sql
CREATE INDEX idx_users_lower_email
ON users (lower(email));
~~~

This can support a genuine lower(email) access pattern.

## Partial indexes

A partial index stores only rows matching a predicate.

~~~sql
CREATE INDEX idx_open_orders_customer_date
ON orders(customer_id, order_date DESC)
WHERE status = 'open';
~~~

Useful when the subset is frequently queried and much smaller than the whole table.

## Covering/index-only access

An index containing all required columns can sometimes avoid base-table access.

That can improve reads but increases index size, cache pressure, and write cost.

Use it for demonstrated hot queries.

## Parallel plans

Parallelism can reduce one large query's latency but consumes more shared resources.

A plan that is faster in isolation may reduce total throughput under concurrency. Benchmark under realistic load.

## Plan changes after deployment

Plans can change after:

- database upgrades,
- statistics refresh,
- data growth,
- index changes,
- configuration changes.

Keep representative performance tests for important queries and monitor regressions.

## Plan hints

Hints can be useful after diagnosis, but they freeze assumptions.

Prefer accurate statistics, suitable indexes, clear predicates, and representative data first.

## Plan-reading workflow

1. State the slow user-visible operation.
2. Capture exact SQL and representative parameters.
3. Get an actual plan safely.
4. Compare estimated and actual rows.
5. Find the first large estimate divergence.
6. Inspect scan/filter/sort/join work.
7. Check indexes and statistics.
8. Check spills, buffers, and waits.
9. Change one thing.
10. Rerun with comparable cache/load.
11. Verify result correctness.

## Common mistakes

- Treating every sequential scan as a problem.
- Treating every index scan as optimized.
- Reading only total execution time.
- Ignoring estimated versus actual rows.
- Updating statistics as a ritual without diagnosis.
- Comparing different parameter values.
- Running EXPLAIN ANALYZE on destructive production SQL.

## Related notes

- [Query optimization](01_query_optimization_techniques.md)
- [Indexing strategies](02_indexing_strategies.md)
- [Database indexing internals](../05_storage_and_indexing/05_indexing.md)
- [Performance monitoring](../11_security_best_practices/05_performance_monitoring_and_tuning.md)
