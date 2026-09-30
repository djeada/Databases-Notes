# Spark SQL

Spark SQL processes structured data with SQL and DataFrame operations. Spark is a processing engine: it can read databases and files, but a DataFrame alone is not a durable database table.

## How a query runs

The driver builds a plan; executors process partitions of data. Transformations are usually lazy: Spark does not perform the work until an action, such as writing output or collecting results, requests it. Spark SQL can optimize relational operations before execution. See the [Spark SQL guide](https://spark.apache.org/docs/latest/sql-programming-guide.html).

## A small PySpark example

This example needs PySpark and a compatible Java installation. It runs locally and writes Parquet to a new directory named `category_totals`.

```python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.builder.master("local[*]").appName("sales-notes").getOrCreate()
try:
    sales = spark.createDataFrame(
        [("Books", 2, 15), ("Books", 1, 20), ("Games", 3, 10)],
        ["category", "quantity", "unit_price"],
    )
    sales.createOrReplaceTempView("sales")

    totals = spark.sql("""
        SELECT category, SUM(quantity * unit_price) AS revenue
        FROM sales
        GROUP BY category
    """)
    totals.orderBy("category").show()

    equivalent = sales.groupBy("category").agg(
        F.sum(F.col("quantity") * F.col("unit_price")).alias("revenue")
    )
    equivalent.explain()
    totals.write.mode("errorifexists").parquet("category_totals")
finally:
    spark.stop()
```

The totals are Books = 50 and Games = 30. The temporary view lasts only for the Spark session. The Parquet output persists independently of that view. In financial workloads, use an explicit decimal schema and defined rounding rules.

## Why distributed queries can be expensive

Grouping and many joins require a **shuffle**, which transfers data between executors. Uneven key frequencies can cause **skew**: one partition takes much longer than others. Filter early, read only needed columns, inspect the plan, and choose partition sizes for the workload.

A small dimension table may be suitable for a broadcast join, but broadcasting a large table can exhaust executor memory. Cache data only when it will be reused enough to offset memory and materialization costs.

## Common mistakes

- Calling `collect()` on a large result moves all rows to the driver's memory.
- Assuming output is globally sorted without requesting an order.
- Treating a temporary view as permanent storage.
- Producing many tiny output files through excessive partitioning.
- Assuming plain Parquet files provide transactional table updates. A compatible table format and catalog are needed for those guarantees.

## Related notes

- [Hadoop and HDFS](02_hadoop_and_hdfs.md)
- [Aggregate functions](../03_sql/10_aggregate_functions.md)
- [Window functions](../03_sql/11_window_functions.md)
