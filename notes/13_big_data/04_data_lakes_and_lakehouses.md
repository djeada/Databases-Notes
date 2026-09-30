# Data Lakes and Lakehouses

A **data lake** stores large analytical datasets as files, usually in object storage. A **lakehouse** keeps that open-file storage model but adds table metadata so readers and writers can treat groups of files more like database tables.

The distinction matters because a directory full of Parquet files is useful, but it does not automatically provide safe concurrent updates, snapshots, schema evolution, or table-level transactions.

## From files to managed tables

A plain data lake often looks like this:

```text
applications / databases / logs
              │
              ▼
      object storage
   S3 / GCS / ADLS / MinIO
              │
      ┌───────┼────────┐
      ▼       ▼        ▼
   Parquet   JSON      CSV
      │
      ▼
 Spark / Trino / DuckDB / Athena
```

A lakehouse adds a table layer:

```text
                  catalog
                    │
                    ▼
            table metadata
          Iceberg / Delta / Hudi
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
     data files          delete/index/
     usually Parquet     manifest metadata
          │
          ▼
       object storage
```

The files remain in object storage, but the table metadata defines which files belong to a consistent table snapshot.

## Why object storage is used

Cloud object stores such as Amazon S3, Google Cloud Storage, and Azure Data Lake Storage are common because they provide durable storage independently from compute.

That separation lets multiple engines operate over the same data:

```text
                object storage
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
     Spark          Trino         DuckDB
       │             │             │
     ETL          ad-hoc SQL    local analysis
```

Compute clusters can scale up, scale down, or disappear while the data remains.

## File formats

### CSV

CSV is convenient for interchange and debugging.

Advantages:
- human-readable,
- supported almost everywhere,
- easy to generate.

Limitations:
- no strong schema,
- poor compression compared with columnar formats,
- every query may need to parse text,
- reading one column still normally requires scanning complete rows.

### JSON

JSON is useful for semi-structured records, APIs, and event payloads.

Limitations for analytics:
- verbose,
- repeated field names increase storage,
- nested structures can be expensive to scan,
- weak schema discipline can create inconsistent records.

### Parquet

Parquet is the most common general-purpose analytical file format.

It is:
- columnar,
- typed,
- compressed,
- splittable for parallel reads,
- able to store statistics useful for pruning.

A table with these columns:

```text
event_time | user_id | country | device | revenue
```

may be queried only for `country` and `revenue`. A columnar reader can avoid loading the other columns.

## Runnable Parquet example

The repository includes:

[`scripts/big_data/parquet_lake_demo.py`](../../scripts/big_data/parquet_lake_demo.py)

Install the Big Data demo dependencies:

```bash
cd scripts
python -m pip install -r big_data/requirements.txt
cd ..
```

Run:

```bash
python scripts/big_data/parquet_lake_demo.py
```

The script:

1. creates a small events table in DuckDB,
2. writes it as partitioned Parquet files,
3. queries only one partition,
4. runs an aggregation directly over the files,
5. prints the generated directory layout.

Conceptually the dataset becomes:

```text
lake/
└── events/
    ├── event_date=2026-09-29/
    │   └── data_0.parquet
    └── event_date=2026-09-30/
        └── data_0.parquet
```

A query can then read only the relevant date:

```sql
SELECT event_type, COUNT(*) AS events
FROM read_parquet(
  'lake/events/event_date=2026-09-30/*.parquet'
)
GROUP BY event_type
ORDER BY event_type;
```

This local demo uses DuckDB, but the same storage ideas apply to Spark, Trino, Athena, BigQuery external tables, and other analytical engines.

## Partitioning

Partitioning places related files into groups based on one or more values.

Typical example:

```text
events/
├── event_date=2026-09-28/
├── event_date=2026-09-29/
└── event_date=2026-09-30/
```

A date-filtered query can skip unrelated directories or files.

Good partition keys:
- appear frequently in filters,
- have a manageable number of values,
- distribute data reasonably.

Poor partition keys:
- user ID with millions of values,
- UUID,
- timestamp down to the second,
- fields rarely used for filtering.

Over-partitioning creates many tiny files and large metadata overhead.

## The small-file problem

A lake with millions of tiny files can perform badly even when the total data volume is moderate.

```text
efficient:
  100 files × 512 MB

problematic:
  5,000,000 files × 10 KB
```

The engine must list, open, plan, and schedule work for each file.

Common remedies:
- periodic compaction,
- larger writer batch sizes,
- fewer output partitions,
- table-format maintenance procedures.

## Why plain Parquet is not enough

Suppose two jobs update a table stored as loose Parquet files.

```text
Job A reads files: A.parquet, B.parquet
Job B reads files: A.parquet, B.parquet

Job A writes C.parquet
Job B writes D.parquet

Which set now represents the table?
```

The file format itself has no transaction coordinator.

A table format solves this by committing metadata that points to a consistent set of files.

## Apache Iceberg

Apache Iceberg represents table state through metadata and snapshots. Changes create a new table state rather than relying on directory naming conventions alone.

Simplified structure:

```text
table
 │
 ├── snapshot 101
 │     ├── file A
 │     └── file B
 │
 └── snapshot 102
       ├── file A
       ├── file C
       └── file D
```

Readers can use one consistent snapshot while a writer prepares the next one.

Iceberg is commonly chosen when teams want:
- open table metadata,
- multiple compatible compute engines,
- snapshot-based reads,
- schema evolution,
- partition evolution,
- time travel.

Apache Iceberg's specification explicitly tracks table state in metadata and supports schema and partition evolution without requiring readers to depend directly on physical partition directories.

## Delta Lake

Delta Lake also adds a transaction log and table semantics over object-storage files.

It is widely associated with Spark and the Databricks ecosystem.

Teams commonly use it for:
- Spark-heavy data platforms,
- merge/upsert workloads,
- lakehouse pipelines,
- streaming plus batch processing over the same tables.

## Apache Hudi

Apache Hudi focuses strongly on incremental data processing and frequently changing datasets.

It is commonly considered for:
- CDC ingestion,
- upserts,
- incremental queries,
- large mutable analytical datasets.

## Choosing a table format

The important questions are not only feature checkboxes.

Ask:

1. Which compute engines must read and write the table?
2. Which catalog will store table identities?
3. Do you need frequent `MERGE` or upserts?
4. Do you need time travel?
5. How will compaction and metadata cleanup run?
6. What schema changes must be supported?
7. Can the team's cloud platform manage the operational pieces?

A table format does not remove maintenance. Snapshot expiry, compaction, orphan-file cleanup, and catalog operations still matter.

## Catalogs

A catalog maps logical names to table metadata.

```text
analytics.sales.events
        │
        ▼
      catalog
        │
        ▼
metadata location
        │
        ▼
object storage files
```

Common catalog choices include:
- AWS Glue Data Catalog,
- Hive Metastore,
- JDBC-backed catalogs,
- REST catalogs,
- platform-specific managed catalogs.

Without a shared catalog, different tools can disagree about where a table lives or which metadata is current.

## Schema evolution

Analytical schemas change.

Examples:
- add `campaign_id`,
- rename `customer` to `customer_id`,
- widen an integer type,
- add fields inside nested records.

A managed table format records schema identities so evolution is safer than rewriting file headers ad hoc.

Still, compatibility must be considered:

```text
producer starts writing new field
       │
       ▼
old consumers still running?
       │
       ├── yes -> must tolerate new schema
       └── no  -> migration can be stricter
```

## Time travel and snapshots

Snapshot-based tables can preserve earlier table states.

Conceptually:

```text
10:00 snapshot A
10:15 snapshot B
10:30 bad DELETE
10:31 snapshot C
```

A time-travel query can inspect snapshot B to understand or recover from the bad change.

Snapshots are not free backups. Retention policies may delete old data files, and disaster recovery still requires separate storage/account-level protection.

## Lakehouse architecture in practice

A common architecture is:

```text
PostgreSQL / SaaS / logs
          │
          ▼
 ingestion / CDC
 Airbyte / Fivetran / Debezium
          │
          ▼
 object storage
 S3 / GCS / ADLS
          │
          ▼
 Iceberg / Delta / Hudi tables
          │
    ┌─────┼────────────┐
    ▼     ▼            ▼
  Spark  Trino       warehouse
    │     │            │
    └─────┴──────┬─────┘
                 ▼
              BI / ML
```

A smaller team may not need this. A managed warehouse can be much simpler when most workloads are SQL analytics.

## Data lake versus warehouse

| Question | Warehouse | Lake / lakehouse |
| --- | --- | --- |
| Storage | managed database storage | object storage files |
| Query interface | usually SQL-first | many engines |
| Open formats | varies by platform | usually central |
| Operations | highly managed | more components |
| ML/file access | sometimes indirect | natural fit |
| BI simplicity | strong | depends on engine/catalog |
| Multi-engine access | platform-dependent | common design goal |

The architectures often coexist rather than replace one another.

## When a lakehouse is justified

A lakehouse becomes more attractive when:
- data volume is very large,
- object storage is already the system of record,
- many engines need shared access,
- the team wants open table formats,
- batch and streaming pipelines share datasets,
- compute/storage independence is important.

Avoid building one only because it is fashionable. For moderate SQL analytics, a managed warehouse is often easier to operate.

## Common mistakes

### Treating a folder as a database table

Files alone do not guarantee atomic table updates.

### Partitioning by high-cardinality values

This produces a huge directory/file count.

### Never compacting

Streaming or incremental writers often produce small files over time.

### Keeping snapshots forever

Old metadata and files accumulate storage and planning cost.

### Mixing writers with incompatible assumptions

All writers must understand the same table format and catalog semantics.

## Related notes

- [Data warehousing](01_data_warehousing.md)
- [Hadoop and HDFS](02_hadoop_and_hdfs.md)
- [Spark SQL](03_spark_sql.md)
- [Streaming, Kafka, and CDC](05_streaming_kafka_and_cdc.md)
- [Pipelines, orchestration, and data quality](06_data_pipelines_orchestration_and_quality.md)
