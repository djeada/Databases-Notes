# Materialized Views

A materialized view stores a query result so readers can reuse work already done. It trades storage and maintenance cost for cheaper reads. Unlike an ordinary view, its data can be older than the underlying tables, depending on the engine's maintenance model.

## Choose a maintenance model

| Model | Behavior | Cost |
| --- | --- | --- |
| Complete refresh | Recompute the result from the base tables. | Potentially expensive reads and replacement work. |
| Incremental refresh | Apply changes to an existing result when supported. | Change tracking and query eligibility restrictions. |
| Synchronous maintenance | Update the result as part of base-table changes. | Extra write work and restrictions on the view definition. |

These options are not supported uniformly. PostgreSQL's built-in refresh recomputes the query; SQL Server indexed views are maintained during writes; Oracle supports eligible fast-refresh materialized views.

## PostgreSQL example

This complete example keeps one total per required region:

```sql
CREATE TABLE sales (
    sale_id INTEGER PRIMARY KEY,
    region VARCHAR(50) NOT NULL,
    amount NUMERIC(12, 2) NOT NULL
);
INSERT INTO sales VALUES (1, 'North', 100), (2, 'North', 50), (3, 'South', 80);

CREATE MATERIALIZED VIEW sales_summary AS
SELECT region, SUM(amount) AS total_sales
FROM sales
GROUP BY region;

SELECT region, total_sales FROM sales_summary ORDER BY region;
```

The result is North = 150 and South = 80. Insert another North sale for 20: the base-table total becomes 170, while the materialized view remains 150 until refreshed.

```sql
INSERT INTO sales VALUES (4, 'North', 20);
REFRESH MATERIALIZED VIEW sales_summary;
```

A normal refresh can block readers of the view. To allow reads during refresh, create an eligible unique index and use concurrent refresh:

```sql
CREATE UNIQUE INDEX idx_sales_summary_region ON sales_summary (region);
REFRESH MATERIALIZED VIEW CONCURRENTLY sales_summary;
```

The view must already be populated. The unique index must cover all rows and use plain columns, rather than a partial or expression index. Concurrent refresh still recomputes the result and only one refresh of a particular view can run at once. See [PostgreSQL REFRESH MATERIALIZED VIEW](https://www.postgresql.org/docs/current/sql-refreshmaterializedview.html).

## Scheduling and freshness

An external scheduler can issue refreshes. Track the last successful completion, refresh duration, and failures; a schedule alone does not prove that the data is fresh. The result represents the snapshot used by the refresh, so completion time alone is not necessarily its exact data cutoff.

Readers should know whether their use case permits delayed data. Inventory decisions and payments may require source-table transactions rather than a periodically refreshed summary.

## Oracle fast refresh

Fast refresh has query-specific requirements. For a supported grouped aggregate, create the change log **before** the materialized view and include the required counts:

```sql
CREATE MATERIALIZED VIEW LOG ON sales
WITH ROWID, SEQUENCE (region, amount)
INCLUDING NEW VALUES;

CREATE MATERIALIZED VIEW sales_summary
BUILD IMMEDIATE
REFRESH FAST ON DEMAND
AS
SELECT region, COUNT(*) AS sale_count,
       SUM(amount) AS total_sales, COUNT(amount) AS amount_count
FROM sales
GROUP BY region;
```

Assume `sales` exists in this separate Oracle example. Check the definition's eligibility with Oracle's materialized-view diagnostics; adding a log does not make every query fast-refreshable.

## SQL Server indexed views

An indexed view uses `WITH SCHEMABINDING` and a unique clustered index. Definitions must satisfy deterministic-expression, ownership, required session-option, and query-shape rules. Grouped definitions need `COUNT_BIG(*)`; nullable aggregates have further restrictions.

Because SQL Server maintains the view as the base tables change, this moves work into the write path instead of a scheduled refresh. Evaluate both read savings and write overhead, and check edition and optimizer requirements for view use.

## When materialization helps

Use it when an expensive, reusable result is much smaller or cheaper to scan than its source and its freshness model fits the application. Avoid creating overlapping summaries without a demonstrated workload. Keep the source of truth, refresh method, and failure behavior explicit.

## Related notes

- [Data warehousing](../13_big_data/01_data_warehousing.md)
- [Database caching](03_database_caching.md)
- [Query optimization](01_query_optimization_techniques.md)
