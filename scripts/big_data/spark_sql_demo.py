"""Local Spark SQL demonstration.

Prerequisites:
    java -version
    python -m pip install pyspark

Run:
    python scripts/big_data/spark_sql_demo.py
"""

from pathlib import Path
from tempfile import TemporaryDirectory

from pyspark.sql import SparkSession


def main() -> None:
    spark = (
        SparkSession.builder
        .master("local[*]")
        .appName("databases-notes-spark-sql")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    try:
        sales = spark.createDataFrame(
            [
                ("Books", 2, 15),
                ("Books", 1, 20),
                ("Games", 3, 10),
            ],
            ["category", "quantity", "unit_price"],
        )
        sales.createOrReplaceTempView("sales")

        totals = spark.sql("""
            SELECT
                category,
                SUM(quantity * unit_price) AS revenue
            FROM sales
            GROUP BY category
            ORDER BY category
        """)

        print("Business result:")
        totals.show()

        print("Formatted execution plan:")
        totals.explain("formatted")

        with TemporaryDirectory(prefix="spark_sql_demo_") as tmpdir:
            output = Path(tmpdir) / "category_totals"
            totals.write.mode("overwrite").parquet(str(output))

            print("Read the persisted Parquet result back:")
            spark.read.parquet(str(output)).orderBy("category").show()
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
