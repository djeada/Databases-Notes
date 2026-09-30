# Data Pipelines, Orchestration, and Data Quality

A data platform is more than storage and queries. Data has to move from sources to destinations reliably, transformations must run in the correct order, failures must be retried safely, and downstream users need to know whether the resulting tables are fresh and trustworthy.

That collection of work is a **data pipeline**.

## Pipeline mental model

A simple pipeline might be:

```text
PostgreSQL
    │
    ▼
extract orders
    │
    ▼
raw storage
    │
    ▼
clean / deduplicate
    │
    ▼
build fact_sales
    │
    ▼
run quality checks
    │
    ▼
publish dashboard tables
```

The important point is that each stage has inputs, outputs, dependencies, and failure behavior.

## Batch pipeline example

Suppose a daily sales report needs yesterday's completed orders.

A naive process could be:

```text
02:00 export orders
02:10 transform CSV
02:20 load warehouse
02:30 refresh dashboard
```

This works until the export is late. If the later steps run only according to wall-clock time, they may process incomplete data.

A dependency-aware workflow is better:

```text
extract_orders
      │
      ▼
validate_raw
      │
      ▼
load_staging
      │
      ▼
build_sales_mart
      │
      ▼
test_sales_mart
      │
      ▼
refresh_bi
```

The next task runs because its dependency succeeded, not merely because a clock reached a specific minute.

## Orchestration

An orchestrator coordinates pipeline tasks.

Common responsibilities include:

- scheduling,
- dependency management,
- retries,
- task state,
- parameter passing,
- backfills,
- logging,
- alerting,
- concurrency limits.

Common tools include:

| Tool | Typical use |
| --- | --- |
| Apache Airflow | general batch workflow orchestration |
| Dagster | asset-oriented data orchestration |
| Prefect | Python-oriented workflow orchestration |
| cloud-native schedulers | managed integration with one cloud platform |
| dbt Cloud jobs | SQL transformation workflows centered on dbt |

The orchestrator should not usually contain all transformation logic itself. It should coordinate tools that perform the work.

## DAGs

A workflow is often represented as a **directed acyclic graph (DAG)**.

```text
          ┌──► customer_dimension ──┐
extract ──┤                         ├──► sales_mart
          └──► product_dimension ───┘
                    ▲
                    │
                 orders_fact
```

"Directed" means dependencies have direction.

"Acyclic" means tasks cannot depend on themselves through a loop.

A cycle would be impossible to schedule:

```text
A depends on B
B depends on C
C depends on A
```

## Airflow-style example

A simplified workflow can look like:

```python
from airflow.sdk import DAG, task
from datetime import datetime


with DAG(
    dag_id="daily_sales",
    schedule="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
) as dag:

    @task
    def extract():
        print("extract orders")

    @task
    def transform():
        print("build fact_sales")

    @task
    def validate():
        print("run quality checks")

    validate(transform(extract()))
```

The important idea is the dependency graph, not the exact API syntax. Airflow versions and deployment styles evolve, so production projects should follow the documentation matching their installed version.

A useful local debugging pattern is to test a DAG before relying on a scheduler. Modern Airflow documentation provides a `dag.test()` workflow for executing a DAG run locally after the metadata database is initialized.

## Scheduling versus event-driven execution

Not every pipeline should run at midnight.

### Schedule-driven

```text
every hour
   │
   ▼
load new events
```

Good for:
- reports,
- periodic synchronization,
- bounded batch workloads.

### Event-driven

```text
new file lands
      │
      ▼
trigger processing
```

Good for:
- unpredictable arrival times,
- low-latency ingestion,
- workflows where completion of one system should immediately trigger another.

### Continuous streaming

```text
events arrive continuously
        │
        ▼
stream processor remains running
```

Good for:
- real-time processing,
- high-volume event flows.

The scheduling model should match the business latency requirement.

## Idempotency

Retries are unavoidable.

A pipeline task should ideally produce the same final state when repeated with the same input.

Bad pattern:

```sql
INSERT INTO daily_sales
SELECT *
FROM staging_sales;
```

If the task retries, rows may duplicate.

Safer options include:

- delete-and-replace one known partition,
- `MERGE` by stable key,
- load into a temporary table then swap,
- write immutable partitions,
- enforce unique constraints where appropriate.

Example partition replacement:

```sql
BEGIN;

DELETE FROM daily_sales
WHERE sales_date = DATE '2026-09-30';

INSERT INTO daily_sales
SELECT *
FROM staging_sales
WHERE sales_date = DATE '2026-09-30';

COMMIT;
```

Now rerunning the same date produces the same logical result.

## Checkpoints

Incremental pipelines need to remember progress.

Possible checkpoints include:

- maximum processed ID,
- source timestamp,
- Kafka offset,
- CDC log position,
- completed partition,
- object-storage file manifest.

A timestamp-only checkpoint can be dangerous if several records share the same timestamp or clocks are inconsistent.

Safer patterns often combine:

```text
(updated_at, primary_key)
```

or use a source-native change position.

## Backfills

A **backfill** reruns historical periods.

Example:

```text
normal daily run:
2026-09-30

backfill:
2026-09-01
2026-09-02
...
2026-09-29
```

A well-designed pipeline separates **logical data date** from the current wall-clock time.

Bad:

```python
date = datetime.now().date()
```

Better:

```text
task receives partition_date = 2026-09-14
```

Then the same code can process today or a historical date.

## Raw, staging, and curated layers

A common pattern is:

```text
raw
 │
 ├── close to source representation
 │
 ▼
staging
 │
 ├── cleaned types and standardized names
 │
 ▼
curated
 │
 ├── business logic and shared definitions
 │
 ▼
marts
    └── consumer-oriented reporting tables
```

Different organizations use names such as:

- bronze / silver / gold,
- raw / refined / curated,
- staging / intermediate / marts.

The names matter less than having clear responsibilities.

## dbt

dbt is commonly used to transform warehouse or lakehouse data with version-controlled SQL.

A model might be:

```sql
-- models/orders_daily.sql

SELECT
    CAST(created_at AS DATE) AS order_date,
    COUNT(*) AS orders,
    SUM(total_amount) AS revenue
FROM {{ ref('stg_orders') }}
WHERE status = 'completed'
GROUP BY 1
```

The `ref()` call establishes a dependency.

Conceptually:

```text
source orders
     │
     ▼
stg_orders
     │
     ▼
orders_daily
```

dbt is popular because analysts and analytics engineers can express transformations in SQL while gaining dependency graphs, testing, documentation, and reproducible builds.

## Data quality

A pipeline is not successful merely because every task returned exit code zero.

Example failure:

```text
extract task      SUCCESS
transform task    SUCCESS
load task         SUCCESS

but revenue = 0 because source field changed
```

This is why data tests are necessary.

## Common quality dimensions

### Completeness

Are required records or fields present?

```sql
SELECT COUNT(*)
FROM orders
WHERE order_id IS NULL;
```

Expected: zero.

### Uniqueness

```sql
SELECT order_id, COUNT(*)
FROM orders
GROUP BY order_id
HAVING COUNT(*) > 1;
```

Expected: no rows.

### Referential integrity

```sql
SELECT COUNT(*)
FROM fact_sales f
LEFT JOIN dim_product p
  ON p.product_key = f.product_key
WHERE p.product_key IS NULL;
```

Expected: zero.

### Accepted values

```sql
SELECT DISTINCT status
FROM orders
WHERE status NOT IN (
  'pending',
  'paid',
  'shipped',
  'cancelled'
);
```

### Freshness

```sql
SELECT MAX(loaded_at)
FROM fact_sales;
```

The result should be within the promised freshness window.

### Volume anomaly

If a table normally gets 2 million rows per day and today gets 18, the pipeline probably should not silently publish.

## Quality tools

Teams commonly use:

- dbt tests,
- Great Expectations,
- Soda,
- Deequ,
- custom SQL assertions,
- warehouse monitoring platforms.

The important feature is automated enforcement at the right point in the pipeline.

## Fail closed versus fail open

Suppose one data-quality test fails.

Two policies are possible:

### Fail closed

Do not publish the new table.

Useful when:
- financial reporting,
- regulatory data,
- downstream automation,
- correctness matters more than freshness.

### Fail open

Publish but alert.

Useful when:
- data is advisory,
- freshness matters strongly,
- the test has occasional false positives.

This is a business decision, not only a technical one.

## Data contracts

A **data contract** describes expectations between producers and consumers.

It may specify:

- field names,
- types,
- nullability,
- semantic meaning,
- allowed values,
- freshness,
- ownership,
- compatibility rules.

Example:

```text
orders.order_id
type: integer
nullable: false
meaning: immutable source order identifier
owner: commerce-platform
```

Contracts reduce accidental breaking changes.

## Lineage

Lineage answers:

> Where did this column come from?

Example:

```text
postgres.orders.total
        │
        ▼
raw_orders.total
        │
        ▼
stg_orders.total_amount
        │
        ▼
fact_sales.net_amount
        │
        ▼
dashboard.revenue
```

Lineage is valuable during incidents.

If a source field is wrong, engineers can identify affected downstream models.

## Observability

Pipeline observability should answer:

- Did it run?
- Did it finish?
- How long did it take?
- How much data moved?
- Is the result fresh?
- Did quality change unexpectedly?
- Which downstream assets are affected?

Useful signals include:

```text
task duration
retry count
rows read
rows written
bytes processed
freshness delay
test failures
schema changes
consumer lag
```

## Retry strategy

Not every failure should retry identically.

### Transient failures

Examples:
- temporary network error,
- rate limit,
- database connection timeout.

Use retries with backoff.

```text
attempt 1 -> fail
wait 30 s
attempt 2 -> fail
wait 2 min
attempt 3
```

### Deterministic failures

Examples:
- SQL syntax error,
- missing required column,
- invalid credentials.

Blind retries waste time. Fail and alert.

## Dependency failure

If `stg_orders` fails, `fact_sales` should not run using stale or partial data unless that behavior is explicitly intended.

```text
stg_orders  FAILED
    │
    └────X──► fact_sales
```

A pipeline should make stale-data behavior visible rather than accidental.

## Incremental transformation

Full rebuild:

```sql
CREATE OR REPLACE TABLE fact_sales AS
SELECT ...
FROM all_orders;
```

Simple but expensive.

Incremental model:

```text
existing table
      +
new/changed source rows
      │
      ▼
MERGE
```

Incremental models require careful handling of:

- updates,
- deletes,
- late events,
- schema changes,
- retries,
- reprocessing.

The optimization is only worthwhile when the additional state complexity is justified.

## Batch size

Very small batches:

- high scheduling overhead,
- many small files,
- too many commits.

Very large batches:

- long recovery time,
- large transactions,
- poor latency.

Choose batch size from actual workload and SLA.

## Common production architecture

```text
Operational DBs / APIs / events
             │
             ▼
      ingestion layer
 Airbyte / Fivetran / CDC
             │
             ▼
    raw warehouse/lake
             │
             ▼
      dbt / Spark jobs
             │
             ▼
  quality tests + contracts
             │
             ▼
     curated datasets
             │
             ▼
       BI / ML / APIs

        orchestration
     Airflow / Dagster
       coordinates all
```

Not every project needs every box.

A small analytics project may only need:

```text
PostgreSQL -> warehouse -> dbt -> BI
```

## Choosing technologies

### Managed ingestion

Tools such as Fivetran or managed cloud connectors reduce operational effort.

Useful when:
- standard SaaS/database connectors exist,
- engineering time is expensive,
- managed retries and schema handling are valuable.

### Open-source ingestion

Tools such as Airbyte or Debezium give more control.

Useful when:
- custom deployment requirements exist,
- CDC is important,
- cost/control trade-offs favor self-management.

### Airflow

Useful when:
- workflows have many heterogeneous tasks,
- scheduling and backfills matter,
- the organization already operates it.

### Dagster

Useful when:
- teams prefer data-asset-oriented modeling,
- software-defined assets and testability fit the development style.

### dbt

Useful when:
- most transformations are SQL,
- models live in a warehouse/lakehouse,
- testing and documentation should be close to SQL.

### Spark

Useful when:
- transformations exceed single-engine SQL comfort,
- processing very large files,
- workloads mix SQL and general code.

## Practical pipeline checklist

Before calling a pipeline production-ready, answer:

1. What is the input boundary?
2. What makes a retry safe?
3. How is progress checkpointed?
4. Can one historical partition be rerun?
5. How are deletes handled?
6. What happens when the source schema changes?
7. Which quality checks block publication?
8. How is freshness measured?
9. Who owns the dataset?
10. What downstream systems depend on it?
11. How is failure alerted?
12. How can a bad deployment be rolled back or repaired?

## Common mistakes

### Scheduling everything by clock time

Dependencies should express readiness.

### Retrying non-idempotent loads

Retries can duplicate data.

### No backfill path

Eventually historical corrections will be required.

### Tests only in application code

Data can become wrong after extraction, transformation, or manual changes.

### Silent stale data

A dashboard that shows yesterday's data without warning can be worse than one that clearly reports a failed refresh.

### Too much orchestration logic

Keep business transformations in testable SQL or application code, not buried inside scheduler configuration.

## Related notes

- [Data warehousing](01_data_warehousing.md)
- [Data lakes and lakehouses](04_data_lakes_and_lakehouses.md)
- [Streaming, Kafka, and CDC](05_streaming_kafka_and_cdc.md)
- [Spark SQL](03_spark_sql.md)
