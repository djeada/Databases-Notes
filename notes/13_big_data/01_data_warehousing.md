# Data Warehousing

A data warehouse is an analytical system built to answer questions across large amounts of historical data. Operational databases are optimized for day-to-day application work such as creating an order, updating inventory, or authenticating a user. Warehouses are optimized for scans, joins, aggregations, trends, dashboards, and repeated reporting.

A useful rule of thumb is:

```text
OLTP database                         Data warehouse / OLAP
-------------------------------       --------------------------------
"What is this customer's order?"      "How did revenue change by region?"
small reads and writes                large scans and aggregations
current application state             historical, integrated data
many concurrent transactions          fewer, heavier analytical queries
normalized schemas are common         star / dimensional models are common
```

Separating these workloads keeps a dashboard that scans a year of sales from competing with checkout transactions on the production database.

## Typical analytical architecture

Modern data platforms usually have several stages rather than one database receiving everything directly.

```text
┌─────────────────────┐
│ Operational sources │
│ Postgres, MySQL,     │
│ SaaS APIs, logs      │
└──────────┬──────────┘
           │ batch files / CDC / events
           ▼
┌─────────────────────┐
│ Ingestion layer     │
│ Airbyte, Fivetran,  │
│ Debezium, Kafka     │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ Raw / staging data  │
│ object storage or   │
│ warehouse staging   │
└──────────┬──────────┘
           │ SQL / Spark / dbt transformations
           ▼
┌─────────────────────┐
│ Curated models      │
│ facts, dimensions,  │
│ data marts          │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ BI and analytics    │
│ dashboards, ad-hoc  │
│ SQL, ML features    │
└─────────────────────┘
```

The exact products vary, but the responsibilities remain similar: ingest, validate, transform, model, serve, and observe.

## ETL and ELT

**ETL (Extract, Transform, Load)** transforms data before it enters the analytical store. This was common when warehouse compute was expensive or when data had to be heavily cleaned before loading.

**ELT (Extract, Load, Transform)** first loads raw or lightly processed data, then transforms it inside the warehouse or lakehouse. ELT is common today because managed analytical systems can scale compute independently and SQL transformation tools make transformations easier to version and test.

```text
ETL: source ──► transform engine ──► warehouse
ELT: source ──► warehouse/raw zone ──► SQL transformations ──► marts
```

Neither approach removes the need for data quality, reproducibility, lineage, and access control.

## Start with the grain

The most important modeling decision is the **grain**: what exactly does one row represent?

For sales, a good grain might be:

> One row in `fact_sales` represents one line item in one customer order.

That statement determines which columns are valid and which joins are safe.

| Table | Role | Example columns |
| --- | --- | --- |
| `fact_sales` | Measurable business event | order ID, line number, date key, product key, quantity, net amount |
| `dim_product` | Describes a product | product key, SKU, category, brand |
| `dim_customer` | Describes a customer | customer key, country, segment |
| `dim_date` | Calendar attributes | date key, date, week, month, quarter, year |

A **fact table** normally contains keys plus measurements. A **dimension table** contains descriptive attributes used to filter, group, and label those facts.

## Star schema

A star schema keeps the fact table in the center and joins dimensions directly to it.

```text
                   ┌───────────────┐
                   │ dim_customer  │
                   └───────┬───────┘
                           │
┌─────────────┐    ┌───────▼───────┐    ┌─────────────┐
│ dim_product │◄───│  fact_sales   │───►│  dim_date   │
└─────────────┘    └───────┬───────┘    └─────────────┘
                           │
                   ┌───────▼───────┐
                   │ dim_store     │
                   └───────────────┘
```

A **snowflake schema** normalizes some dimensions into extra related tables. Star schemas are often easier for analysts because fewer joins are needed; snowflaking can reduce repeated descriptive data but increases query complexity.

## Runnable local example

A production warehouse may be Snowflake, BigQuery, Redshift, ClickHouse, or a lakehouse platform. For learning, [DuckDB](https://duckdb.org/) is convenient because it runs locally and supports analytical SQL without a server.

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install duckdb
python scripts/big_data/warehouse_demo.py
```

The script creates a tiny star schema, inserts sample data, and runs a reporting query. It is intentionally small enough to inspect end to end.

The important query is equivalent to:

```sql
SELECT
    d.year,
    p.category,
    SUM(s.quantity * s.unit_price) AS revenue
FROM fact_sales AS s
JOIN dim_date AS d
  ON d.date_key = s.date_key
JOIN dim_product AS p
  ON p.product_key = s.product_key
GROUP BY d.year, p.category
ORDER BY d.year, revenue DESC;
```

Expected result:

```text
year  category  revenue
2026  Books     50.00
2026  Games     30.00
```

Notice that the fact table stores keys and numeric measures, while category and calendar year come from dimensions. This is the core pattern behind many BI models.

See the runnable example: [`scripts/big_data/warehouse_demo.py`](../../scripts/big_data/warehouse_demo.py).

## Slowly changing dimensions

Dimensions change over time. A customer moves country, a product changes category, or a sales territory is reorganized. The model must decide whether historical reports should show the old or current attribute.

### Type 1

Overwrite the old value.

```text
Before: product 42 -> category = "Books"
After:  product 42 -> category = "Education"
```

Historical facts now appear under `Education`. This is appropriate when old values were simply incorrect or history is not needed.

### Type 2

Insert a new version of the dimension row.

```text
product_key  sku   category    valid_from   valid_to
-----------  ----  ----------  -----------  ----------
101          A12   Books       2024-01-01   2026-04-30
205          A12   Education   2026-05-01   NULL
```

Facts from April reference key `101`; facts from May onward reference `205`. This preserves the historical classification.

## Incremental loading

Reloading every source table from scratch is simple but expensive. Production systems usually load incrementally using one of these patterns:

- a monotonically increasing ID or timestamp,
- database change data capture (CDC),
- append-only event streams,
- source-system export partitions,
- merge/upsert logic based on a stable business key.

A robust incremental pipeline is **idempotent**: retrying the same batch should not duplicate data or change the result unexpectedly.

A common load pattern is:

```text
extract new rows
      │
      ▼
validate schema + required fields
      │
      ▼
load staging table
      │
      ▼
MERGE / deduplicate / apply business rules
      │
      ▼
publish curated table
      │
      ▼
record checkpoint + metrics
```

## Data quality checks

A pipeline that finishes successfully can still load bad data. Useful checks include:

- required fields are not null,
- dimension keys are unique,
- foreign keys in facts resolve to dimensions,
- row counts stay within expected ranges,
- revenue totals reconcile with the source,
- timestamps are not implausibly old or in the future,
- accepted-value columns only contain known categories,
- freshness is within the promised SLA.

Tools such as dbt tests, Great Expectations, Soda, and custom SQL checks are commonly used to automate these validations.

## Storage layout matters

Analytical engines often use **columnar** formats because a query may need only a few columns from millions of rows.

Common file formats:

| Format | Typical use | Why |
| --- | --- | --- |
| Parquet | general analytics | columnar, compressed, predicate pushdown |
| ORC | Hadoop/Hive ecosystems | columnar, strong compression and statistics |
| CSV | interchange and debugging | universally readable, but larger and weakly typed |
| JSON | semi-structured interchange | flexible, but verbose and expensive for large scans |

Partitioning can reduce I/O when queries repeatedly filter by the partition key.

For example:

```text
sales/
├── year=2025/
│   ├── month=11/
│   └── month=12/
└── year=2026/
    ├── month=01/
    └── month=02/
```

Too many tiny partitions or files are harmful, so partitioning should follow real query patterns rather than every possible field.

## Warehouse, lake, and lakehouse

These terms describe different architectures.

### Data warehouse

Data is loaded into a database designed for analytics.

Typical technologies:
- Snowflake
- Google BigQuery
- Amazon Redshift
- Azure Synapse Analytics
- ClickHouse

Why teams choose them:
- managed scaling,
- SQL-first analytics,
- strong integration with BI tools,
- workload management,
- governance and access controls.

### Data lake

Raw and curated files live in object storage such as S3, GCS, or Azure Data Lake Storage. Engines such as Spark, Trino, Athena, or BigQuery external tables read those files.

Why teams choose it:
- cheap durable storage,
- open file formats,
- many processing engines can share the same data,
- suitable for very large or semi-structured datasets.

### Lakehouse

A lakehouse adds table-management features to object storage, including schema evolution, snapshots, and transactional updates.

Common table formats:
- Apache Iceberg
- Delta Lake
- Apache Hudi

The storage may still be S3/GCS/ADLS, but the table format adds metadata that makes files behave more like managed database tables.

## Technologies commonly used together

A realistic platform often combines several specialized tools.

| Responsibility | Common technologies | Why they are used |
| --- | --- | --- |
| Source databases | PostgreSQL, MySQL, SQL Server | transactional application state |
| CDC / ingestion | Debezium, Kafka, Airbyte, Fivetran | move changes reliably from sources |
| Object storage | S3, GCS, ADLS | low-cost durable storage |
| Warehouse | Snowflake, BigQuery, Redshift | managed analytical SQL |
| Distributed processing | Spark | large transformations and mixed SQL/code workloads |
| SQL transformation | dbt | versioned, testable SQL models |
| Orchestration | Airflow, Dagster | schedules and dependencies |
| Table formats | Iceberg, Delta Lake, Hudi | ACID-style tables on object storage |
| BI | Power BI, Tableau, Looker, Metabase | dashboards and self-service analysis |

No production team needs all of them. A smaller system might only need PostgreSQL plus a managed warehouse and dbt.

## Query correctness pitfalls

### Fan-out joins

If one fact row accidentally matches multiple dimension rows, totals are multiplied.

```text
1 fact row × 3 matching dimension rows = value counted 3 times
```

Validate dimension uniqueness before trusting aggregates.

### Non-additive measures

Revenue can usually be summed across products and dates. Ratios and snapshots often cannot.

Examples:
- average price should usually be calculated from totals, not averaged from averages,
- inventory snapshots should not be summed across dates,
- conversion rate should be recomputed from numerator and denominator.

### Late-arriving data

An event may arrive after a daily report was already built. Pipelines need a policy for reprocessing recent partitions or merging corrections.

## Choosing an approach

A practical decision path is:

```text
Need analytics on modest relational data?
        │
        ├─ yes ─► start with a managed warehouse + SQL/dbt
        │
        └─ no
            │
            ▼
Need large-scale file processing or ML pipelines?
        │
        ├─ yes ─► object storage + Spark/lakehouse
        │
        └─ no
            │
            ▼
Need only lightweight local analytics?
        └────────► DuckDB / SQLite may be enough
```

Start with the smallest architecture that meets the workload. Distributed systems add operational cost and should solve a measured problem.

## Related notes

- [Row and column storage](../05_storage_and_indexing/02_row_based_vs_column_based_databases.md)
- [Materialized views](../08_database_performance/04_materialized_views.md)
- [Hadoop and HDFS](02_hadoop_and_hdfs.md)
- [Spark SQL](03_spark_sql.md)
- [Data lakes and lakehouses](04_data_lakes_and_lakehouses.md)
- [Streaming, Kafka, and CDC](05_streaming_kafka_and_cdc.md)
- [Pipelines, orchestration, and data quality](06_data_pipelines_orchestration_and_quality.md)
