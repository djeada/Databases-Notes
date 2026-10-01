# Materialized Views and Precomputed Results

A materialized view stores the result of a query so readers can reuse work that has already been performed.

It trades:

~~~text
more storage + refresh/maintenance work
for
cheaper repeated reads
~~~

The main design question is not "can this query be materialized?" It is:

> How stale may the result be, and what will maintain it?

## View versus materialized view

Ordinary view:

~~~text
query view
   |
   v
execute underlying query now
~~~

Materialized view:

~~~text
refresh/precompute
      |
      v
stored result
      |
      v
read stored rows
~~~

A normal view mainly stores SQL definition.

A materialized view stores data.

## Good candidates

Materialization is useful when:

- the source query is expensive,
- many readers reuse the same result,
- the result is much smaller than source data,
- freshness can be defined clearly.

Examples:

- daily revenue by region,
- product popularity summary,
- customer lifetime totals,
- expensive joins for reporting.

## Poor candidates

Avoid materializing when:

- source query is already cheap,
- each request has unique filters,
- result changes on every write and must be exact immediately,
- refresh cost is comparable to just running the query,
- overlapping materialized summaries proliferate without ownership.

## PostgreSQL example

Create sample data:

~~~sql
CREATE TABLE sales (
    sale_id bigint PRIMARY KEY,
    region text NOT NULL,
    sold_at timestamptz NOT NULL,
    amount numeric(12, 2) NOT NULL
);

INSERT INTO sales VALUES
    (1, 'North', '2026-10-01 10:00+00', 100),
    (2, 'North', '2026-10-01 11:00+00', 50),
    (3, 'South', '2026-10-01 12:00+00', 80);
~~~

Create summary:

~~~sql
CREATE MATERIALIZED VIEW daily_region_sales AS
SELECT
    sold_at::date AS sale_date,
    region,
    count(*) AS sale_count,
    sum(amount) AS total_sales
FROM sales
GROUP BY sold_at::date, region;
~~~

Read it:

~~~sql
SELECT *
FROM daily_region_sales
ORDER BY sale_date, region;
~~~

## Staleness is explicit

Insert a new row:

~~~sql
INSERT INTO sales
VALUES (4, 'North', '2026-10-01 13:00+00', 20);
~~~

The materialized view does not automatically change in PostgreSQL.

~~~text
base table North total = 170
materialized result    = 150
~~~

until refresh.

That is not a bug. It is the maintenance model.

## Complete refresh

PostgreSQL:

~~~sql
REFRESH MATERIALIZED VIEW daily_region_sales;
~~~

This recomputes and replaces the contents.

For a large result, refresh can consume:

- CPU,
- reads,
- writes,
- WAL,
- temporary memory/disk.

Treat refresh as a production workload.

## Concurrent refresh

PostgreSQL supports:

~~~sql
REFRESH MATERIALIZED VIEW CONCURRENTLY daily_region_sales;
~~~

This allows concurrent readers to continue querying the materialized view while refresh runs.

Current PostgreSQL requires at least one qualifying UNIQUE index covering all rows with plain column names.

Example:

~~~sql
CREATE UNIQUE INDEX ux_daily_region_sales
ON daily_region_sales(sale_date, region);
~~~

Then:

~~~sql
REFRESH MATERIALIZED VIEW CONCURRENTLY daily_region_sales;
~~~

Concurrent refresh can have different resource/latency behavior from a normal refresh and only one refresh may run at a time for a given materialized view.

## WITH NO DATA

PostgreSQL can create or refresh a materialized view without populating it:

~~~sql
CREATE MATERIALIZED VIEW daily_region_sales AS
SELECT ...
WITH NO DATA;
~~~

or:

~~~sql
REFRESH MATERIALIZED VIEW daily_region_sales
WITH NO DATA;
~~~

An unpopulated PostgreSQL materialized view cannot be queried until populated.

This can be useful during deployment/setup.

## ORDER BY is not storage guarantee

Even if the materialized-view definition contains ORDER BY, readers should still use ORDER BY when they require a specific result order.

Physical/stored ordering is not an API contract.

## Index the materialized result

Materialized views can have their own indexes.

If readers ask:

~~~sql
SELECT *
FROM daily_region_sales
WHERE region = 'North'
  AND sale_date >= DATE '2026-09-01';
~~~

an index such as:

~~~sql
CREATE INDEX idx_daily_region_sales_region_date
ON daily_region_sales(region, sale_date);
~~~

may be useful.

Now there are two performance questions:

1. cost to build/refresh the result,
2. cost to query the stored result.

## Freshness contract

Define freshness as a product requirement.

Examples:

~~~text
finance dashboard: refresh by 06:00 daily
operations dashboard: under 5 minutes stale
homepage ranking: under 30 minutes stale
~~~

Then design refresh accordingly.

"Refresh periodically" is too vague.

## Refresh scheduling

Options include:

- cron/system scheduler,
- workflow orchestrator,
- database scheduling extension/service,
- event-driven refresh,
- application job.

The database feature stores the result; scheduling is an operational concern.

## Refresh after every write?

If the result must change synchronously with every source write, a periodically refreshed materialized view may be the wrong abstraction.

Alternatives include:

- trigger-maintained summary table,
- engine-specific indexed view,
- incremental view maintenance feature,
- transactional counter/summary,
- application-maintained projection.

## Incremental maintenance

Incremental maintenance updates only affected result rows.

Conceptually:

~~~text
new sale
   |
   v
update North/2026-10-01 summary
~~~

instead of recomputing every region/date.

Whether this is supported automatically depends on the engine and query.

PostgreSQL built-in REFRESH recomputes the materialized-view query; it does not provide general built-in incremental refresh.

## Summary table pattern

A normal table can hold precomputed aggregates:

~~~sql
CREATE TABLE daily_region_sales_summary (
    sale_date date NOT NULL,
    region text NOT NULL,
    sale_count bigint NOT NULL,
    total_sales numeric(14, 2) NOT NULL,
    PRIMARY KEY (sale_date, region)
);
~~~

A job can update only affected partitions/dates.

This provides more control but shifts correctness to your code/pipeline.

## Event/CDC-maintained projection

Architecture:

~~~text
source database
      |
      v
CDC/event stream
      |
      v
summary consumer
      |
      v
precomputed table/store
~~~

This can maintain near-real-time projections.

Now you must handle:

- duplicate events,
- ordering,
- replay,
- lag,
- rebuild.

## Idempotent refresh

Refresh jobs can fail midway.

Design jobs so they can safely retry.

Patterns include:

- build new data then swap,
- transactional replacement for one bucket,
- UPSERT by deterministic key,
- staging table then validation.

## Time-bucket refresh

For a large event table, rebuilding all history every five minutes is wasteful.

Refresh recent mutable windows:

~~~text
today
yesterday if late arrivals exist
~~~

Leave closed historical partitions unchanged.

This is a common warehouse/analytics pattern.

## Late-arriving data

If yesterday's records can arrive today, a "refresh today only" job is wrong.

Define how far back data can change.

Example:

~~~text
refresh last 3 days each run
~~~

The window should come from real data behavior.

## Materialized view versus cache

Materialized view:

- stored in/near database,
- structured relational result,
- refreshed by database/job rules,
- queryable with SQL.

Application cache:

- key/value/object lookup,
- application-defined key/freshness,
- often evictable,
- can skip database query entirely.

Use the model matching the access pattern.

## Materialized view versus index

Index stores an access structure over source rows.

Materialized view stores a derived query result.

If the slow query is:

~~~text
filter/sort existing rows
~~~

an index may be enough.

If it repeatedly performs:

~~~text
large join + group + expensive aggregate
~~~

materialization can remove more work.

## Materialized view versus warehouse

If reporting requires:

- large history,
- many ad-hoc dimensions,
- heavy scans,
- many concurrent analysts,

a warehouse/OLAP system may be a better destination than many materialized views on the production OLTP database.

## Write amplification

A precomputed result moves work.

~~~text
less work at read time
more work during refresh/maintenance
~~~

Measure:

- source write overhead if synchronous,
- refresh duration,
- WAL/log volume,
- disk usage,
- replica lag.

## Locking and availability

Understand what readers/writers can do during refresh.

For PostgreSQL, a normal REFRESH can block readers; CONCURRENTLY keeps reads available under its requirements.

Other engines have different semantics.

Test with production-scale data.

## Failure handling

Questions:

1. What if refresh fails?
2. Does old data remain readable?
3. Is partially refreshed data visible?
4. Who alerts on stale data?
5. How is the job retried?
6. Can the result be rebuilt from source?

A stale-but-complete result may be preferable to a partial result.

## Freshness metadata

Expose refresh time:

~~~text
last_refreshed_at = 2026-10-01 15:00 UTC
~~~

Dashboards can display it and alerts can check it.

Users need to know when derived data is stale.

## Monitoring

Track:

- refresh duration,
- rows/result size,
- refresh failures,
- time since successful refresh,
- query latency,
- source-table growth,
- WAL/I/O during refresh.

A refresh job that slowly grows from 2 minutes to 50 minutes is a capacity signal.

## Oracle fast refresh

Oracle supports fast-refresh materialized views for eligible definitions when the required logs/conditions are satisfied.

This is an example of engine-specific incremental maintenance.

Eligibility matters; creating a materialized-view log does not make every query incrementally refreshable.

## SQL Server indexed views

SQL Server indexed views are maintained as base tables change.

That moves maintenance into the write path.

They have definition, session-option, determinism, and indexing requirements.

Evaluate both:

~~~text
read savings
vs
write overhead
~~~

## Derived-table alternative

Sometimes a manually maintained table is clearer than an engine-specific materialized-view feature.

Advantages:

- explicit refresh logic,
- engine portability,
- custom incremental rules.

Costs:

- more application/pipeline code,
- correctness responsibility,
- operational monitoring.

## When to use materialization

Good fit:

- expensive repeated query,
- bounded reusable result,
- clear freshness target,
- affordable refresh.

Poor fit:

- unique per-user query,
- strict immediate consistency,
- cheap source query,
- uncontrolled proliferation of summaries.

## Design checklist

1. What query work is being reused?
2. How much smaller is the stored result?
3. What freshness is required?
4. Complete or incremental maintenance?
5. Can readers tolerate refresh locking?
6. Does the result need indexes?
7. What happens if refresh fails?
8. Is refresh idempotent?
9. How are late-arriving changes handled?
10. What are WAL/I/O/storage costs?
11. Can the result be rebuilt?
12. Should this workload live in a warehouse instead?

## Related notes

- [Query optimization](01_query_optimization_techniques.md)
- [Database caching](03_database_caching.md)
- [Write performance and maintenance](12_write_performance_vacuum_and_bloat.md)
- [Data warehousing](../13_big_data/01_data_warehousing.md)
- [Data pipelines](../13_big_data/06_data_pipelines_orchestration_and_quality.md)
