# Data Warehousing

A data warehouse combines historical data from operational systems for analysis. An order database answers “can we sell this item now?”; a warehouse answers “how did sales change by region over the last year?” Separating these workloads prevents large reporting scans from competing with checkout transactions.

## From source data to a report

```text
Operational systems --> Ingestion --> Staging --> Curated tables --> Reports
                                         |              |
                                  validate inputs   shared definitions
```

**ETL** transforms data before loading it into the analytical store. **ELT** loads it first and performs transformations there. Either approach needs validation, repeatable processing, and a way to track where each result came from.

## Start with the grain

The grain states what one fact row represents. For sales, choose one order line rather than vaguely “a sale.” Then define measures and dimensions at that grain.

| Table | Role | Example columns |
| --- | --- | --- |
| `fact_sales` | One row per order line | order ID, line number, date key, product key, quantity, net amount |
| `dim_product` | Describes a product | product key, SKU, category |
| `dim_date` | Describes a calendar date | date key, calendar date, month, year |

A **star schema** joins the fact table directly to dimensions. A **snowflake schema** normalizes some dimensions into additional tables. Star schemas simplify many reporting queries; normalized dimensions can reduce repeated attributes.

## Example: sales by category

Assume `net_amount` is the line total in one reporting currency, and each fact references exactly one product dimension row. This SQL uses PostgreSQL date syntax.

```sql
SELECT p.category, SUM(s.net_amount) AS revenue
FROM fact_sales AS s
JOIN dim_product AS p ON p.product_key = s.product_key
JOIN dim_date AS d ON d.date_key = s.date_key
WHERE d.calendar_date >= DATE '2025-01-01'
  AND d.calendar_date < DATE '2026-01-01'
GROUP BY p.category;
```

Joining a fact to multiple matching dimension rows inflates totals. Validate uniqueness and reconcile loaded amounts with the source. Ratios and balances need care: average prices should often be weighted, and inventory snapshots generally cannot be summed across dates.

## Preserving history

If a product changes category, decide whether past sales should use the current category or the category at sale time. A type 1 dimension overwrites the attribute. A type 2 dimension stores dated versions with distinct surrogate keys; facts must reference the appropriate version.

## Reliable loading

- Use a stable source identifier to make retries idempotent.
- Track ingestion progress and handle late records and corrections.
- Check row counts, required fields, uniqueness, and reconciled totals.
- Define freshness expectations and expose the last successful refresh.

Partitioning and columnar storage can reduce analytical I/O, but query performance still depends on the data layout and access pattern. A warehouse, a data lake, and a lakehouse describe different architectural choices; none removes the need for consistent business definitions.

## Related notes

- [Row and column storage](../05_storage_and_indexing/02_row_based_vs_column_based_databases.md)
- [Materialized views](../08_database_performance/04_materialized_views.md)
- [Spark SQL](03_spark_sql.md)
