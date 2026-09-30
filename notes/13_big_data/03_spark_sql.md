# Spark SQL

Spark SQL is Apache Spark's structured-data engine. It lets you express work with SQL or DataFrame operations while Spark distributes the computation across partitions.

Spark is a **processing engine**, not a database by itself. A DataFrame can be created from Parquet files, HDFS, object storage, JDBC sources, or a table catalog, but the DataFrame is not durable storage unless you write the result somewhere.

## Mental model

A Spark application has a **driver** and one or more **executors**.

```text
                 ┌──────────────────────┐
                 │ Driver               │
                 │ builds query plan    │
                 │ schedules tasks      │
                 └──────────┬───────────┘
                            │
             task scheduling / metadata
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│ Executor 1     │ │ Executor 2     │ │ Executor 3     │
│ partition A    │ │ partition B    │ │ partition C    │
└────────────────┘ └────────────────┘ └────────────────┘
```

The driver plans the work. Executors process partitions in parallel.

## Lazy execution

Most DataFrame transformations are lazy.

This code:

```python
filtered = sales.filter(sales.quantity > 1)
grouped = filtered.groupBy("category").sum("revenue")
```

describes a computation but does not necessarily run it immediately.

An **action** triggers execution, for example:

```python
grouped.show()
grouped.count()
grouped.write.parquet("output")
```

This lets Spark optimize a larger query plan instead of executing each line independently.

## SQL and DataFrames use the same engine

A temporary view lets SQL operate on a DataFrame.

```python
sales.createOrReplaceTempView("sales")
result = spark.sql("""
    SELECT category, SUM(quantity * unit_price) AS revenue
    FROM sales
    GROUP BY category
""")
```

The equivalent DataFrame expression is:

```python
from pyspark.sql import functions as F

result = sales.groupBy("category").agg(
    F.sum(F.col("quantity") * F.col("unit_price")).alias("revenue")
)
```

The choice between SQL and DataFrames is often about readability and team preference rather than a completely different execution engine.

## Runnable local example

The repository contains a complete example at
[`scripts/big_data/spark_sql_demo.py`](../../scripts/big_data/spark_sql_demo.py).

### 1. Check Java

PySpark needs a compatible Java runtime.

```bash
java -version
```

### 2. Create an environment

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install pyspark
```

### 3. Run the script

```bash
python scripts/big_data/spark_sql_demo.py
```

The script:

1. starts Spark in local mode,
2. builds a small sales DataFrame,
3. registers it as a SQL temporary view,
4. runs a grouped SQL query,
5. prints the physical plan,
6. writes the result as Parquet,
7. reads the Parquet result back.

Expected business result:

```text
+--------+-------+
|category|revenue|
+--------+-------+
|   Books|     50|
|   Games|     30|
+--------+-------+
```

The exact execution-plan text can vary by Spark version, but it should show aggregation stages and an exchange/shuffle for the grouped result.

## Why the shuffle matters

Many distributed operations require rows with the same key to meet on the same executor.

Suppose the input is split like this:

```text
Partition 1: Books, Games
Partition 2: Books
Partition 3: Games, Books
```

A `GROUP BY category` must reorganize the data:

```text
before shuffle                     after shuffle

P1: Books, Games   ─────┐          P1: Books, Books, Books
P2: Books          ─────┼────────► P2: Games, Games
P3: Games, Books   ─────┘
```

That network transfer and disk spill can be much more expensive than local computation.

Operations that often trigger shuffles include:

- `GROUP BY`,
- `DISTINCT`,
- many joins,
- repartitioning,
- global sorting,
- window operations with partitioning.

## Inspecting the plan

Use:

```python
result.explain()
```

or:

```python
result.explain("formatted")
```

The plan helps answer questions such as:

- Is Spark scanning all columns?
- Is a filter applied early?
- Is the join broadcast?
- Is there an expensive exchange?
- Are Python UDFs blocking optimizations?

Reading plans is one of the most useful Spark performance skills.

## Partitioning

A Spark DataFrame is divided into partitions. Each task processes one partition.

Too few partitions:
- not enough parallelism,
- individual tasks may become very large.

Too many partitions:
- excessive scheduling overhead,
- many tiny output files,
- more metadata work.

Useful operations:

```python
df.rdd.getNumPartitions()
df.repartition(20, "customer_id")
df.coalesce(4)
```

`repartition()` normally performs a shuffle and can increase or decrease partition count. `coalesce()` is often used to reduce partitions with less movement.

Do not choose a partition count only from CPU cores. Data volume, file sizes, skew, and cluster resources matter too.

## Join strategies

### Shuffle join

Large tables are repartitioned on the join key.

```text
large fact table ─┐
                  ├── shuffle by key ──► join
large dimension ──┘
```

This is scalable but network-intensive.

### Broadcast join

A small table is copied to executors so the large table does not need to shuffle.

```text
small dimension ─────► copied to every executor
large fact data ─────► stays partitioned
```

Example:

```python
from pyspark.sql.functions import broadcast

joined = facts.join(broadcast(products), "product_id")
```

Broadcasting helps only when the small side is genuinely small enough for executor memory.

## Data skew

A join key is **skewed** when one value appears far more frequently than others.

Example:

```text
customer_id = 1       -> 80,000,000 rows
customer_id = 2..N    -> 20,000,000 rows total
```

One partition may receive most of the data, causing one task to run much longer than the others.

Symptoms:
- most tasks finish quickly,
- one or a few tasks remain running,
- executor memory or spill is concentrated on those tasks.

Possible remedies depend on the workload:
- filter irrelevant hot keys,
- aggregate before joining,
- use adaptive query execution,
- split/salt extreme keys,
- broadcast the other side if appropriate,
- redesign the data model.

## Column pruning and predicate pushdown

Columnar formats allow Spark to read only needed columns.

```python
events = spark.read.parquet("events/")
result = events.select("event_date", "user_id").where(
    "event_date >= DATE '2026-01-01'"
)
```

With suitable Parquet metadata and partitioning, Spark may avoid reading unrelated columns and files.

This is one reason Parquet is usually preferable to raw CSV for large analytical workloads.

## Temporary views versus durable tables

A temporary view exists only in the Spark session:

```python
df.createOrReplaceTempView("sales")
```

It disappears when the application ends.

Durable storage requires writing data:

```python
df.write.mode("overwrite").parquet("warehouse/sales")
```

or writing through a catalog/table format.

Do not confuse:
- a DataFrame,
- a temporary SQL view,
- a catalog table,
- raw Parquet files,
- a transactional lakehouse table.

They have different lifecycles and guarantees.

## Parquet is not a transaction system

Plain Parquet files are an efficient storage format, but the file format alone does not provide database-style transactional table management.

For concurrent writes, schema evolution, snapshots, and reliable updates, teams commonly use table formats such as:

- Apache Iceberg,
- Delta Lake,
- Apache Hudi.

The files may still be Parquet underneath, while the table format manages metadata and commits.

## Where Spark is used in practice

Spark is commonly used for:

- large ETL/ELT transformations,
- lakehouse pipelines,
- batch feature generation,
- joining very large datasets,
- SQL analytics on files,
- some streaming workloads,
- machine-learning data preparation.

Common deployment environments include:

| Environment | Typical reason |
| --- | --- |
| Databricks | managed Spark/lakehouse platform |
| Amazon EMR | managed big-data clusters on AWS |
| Google Dataproc | managed Spark/Hadoop on GCP |
| Kubernetes | shared container orchestration |
| Standalone/YARN clusters | existing enterprise infrastructure |

Spark is usually unnecessary when a single database or local engine can process the data comfortably.

## Spark versus a warehouse

A warehouse such as BigQuery, Snowflake, or Redshift is often a simpler choice for SQL-heavy analytics.

Spark is attractive when:
- transformations require general-purpose code,
- datasets are stored in open files,
- processing is too large for one machine,
- pipelines mix SQL with custom logic,
- teams need one engine across batch, streaming, and ML-oriented workflows.

A warehouse is attractive when:
- analysts mostly use SQL,
- managed operations are important,
- BI concurrency matters,
- the workload fits warehouse semantics well.

Many organizations use both.

## UDFs

Built-in Spark SQL functions are usually preferable to custom Python UDFs.

Prefer:

```python
from pyspark.sql import functions as F

df.withColumn("normalized", F.lower(F.trim("name")))
```

over a Python UDF that does the same thing.

Built-in functions are visible to the optimizer and avoid extra Python serialization overhead.

Use UDFs when the operation truly cannot be expressed with native functions.

## Caching

Caching can help if the same expensive intermediate result is reused.

```python
prepared = expensive_transform(df).cache()
prepared.count()      # materialize cache
query_a(prepared)
query_b(prepared)
prepared.unpersist()
```

Caching everything is a mistake. It consumes executor memory and can increase garbage collection or spill.

## Common mistakes

### Calling `collect()` on large data

```python
rows = huge_df.collect()
```

This moves every row to driver memory and can crash the application.

Use `show()`, `limit()`, aggregation, or distributed writes instead.

### Assuming order is preserved

Distributed data has no guaranteed global order unless you request one.

```python
df.orderBy("timestamp")
```

Even then, sorting is expensive and may trigger a full shuffle.

### Writing thousands of tiny files

Excessive partitions create tiny output files that hurt later queries.

### Using `repartition(1)` on large data

This forces all data through one partition and removes parallelism.

### Treating Spark as a low-latency API database

Spark is optimized for analytical processing, not millisecond point lookups or transactional request handling.

## Practical debugging checklist

When a Spark SQL job is slow:

1. inspect `explain("formatted")`,
2. check whether filters and column pruning occur early,
3. look for large shuffles,
4. check data skew,
5. inspect partition counts and output file sizes,
6. confirm whether a join should be broadcast,
7. remove unnecessary UDFs,
8. avoid repeated recomputation or pointless caching,
9. compare the workload with a warehouse or local analytical engine before adding cluster complexity.

## Related notes

- [Data warehousing](01_data_warehousing.md)
- [Hadoop and HDFS](02_hadoop_and_hdfs.md)
- [Aggregate functions](../03_sql/10_aggregate_functions.md)
- [Window functions](../03_sql/11_window_functions.md)
