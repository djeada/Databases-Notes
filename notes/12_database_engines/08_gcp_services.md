# Choosing a Database on Google Cloud

Match the workload to a data model and consistency requirement before selecting a managed product. Relational transactions, large analytical scans, document queries, and cached state have different needs. Managed operations reduce some administrative work but do not remove schema design, capacity planning, or recovery requirements.

## Workload map

| Need | Candidate | What to investigate |
| --- | --- | --- |
| Managed MySQL, PostgreSQL, or SQL Server | Cloud SQL | Engine compatibility, availability topology, read replicas, backups. |
| PostgreSQL-compatible managed relational workload | AlloyDB | Extension and feature coverage, primary/read architecture, workload cost. |
| Horizontally distributed relational transactions | Spanner | Schema and key design, transaction semantics, topology, latency. |
| Document-oriented application data | Firestore | Query/index requirements, transaction limits, chosen edition and mode. |
| Large keyed wide-column workloads | Bigtable | Row-key distribution, access ranges, atomicity and replication configuration. |
| Analytical warehouse | BigQuery | Data layout, scan volume, compute allocation, loading and freshness. |
| Managed cache or in-memory state | Memorystore | Engine, persistence, eviction, failover, and availability tier. |
| Files, backups, or lake objects | Cloud Storage | Object layout, lifecycle, location and access policy. |

The [Google Cloud database catalog](https://cloud.google.com/products/databases) provides current product coverage. Engine compatibility and regional availability require product-specific verification.

## Cloud SQL, AlloyDB, and Spanner

Cloud SQL is a managed option for supported conventional relational engines. AlloyDB provides PostgreSQL compatibility with its own architecture and operational model. Test compatibility rather than assuming every PostgreSQL extension or administrative operation works identically.

Spanner is relevant when relational transactions and horizontal distribution are explicit requirements. Its consistency guarantees depend on coordinated transaction and replication protocols; “global” does not imply zero network latency or unlimited availability during partitions.

Choose the deployment against write distribution, transaction shape, regional needs, and measured cost. A small application with ordinary relational requirements does not need a globally distributed design solely because it may grow.

## Firestore and Bigtable

Firestore models data as documents and supports indexed queries and transactions subject to the selected product's rules. A flexible schema still needs validation, consistent field meanings, and a plan for evolution. Define security rules and authorization independently of convenience in the client SDK.

Bigtable uses keyed wide-column data. It can fit telemetry and time-series workloads when row keys and access patterns are designed accordingly. An increasing timestamp at the start of every key can concentrate writes. It is different from a columnar analytical warehouse and does not provide arbitrary multi-row relational transactions. See the [Bigtable overview](https://docs.cloud.google.com/bigtable/docs/overview).

“Document” and “time-series” are starting clues; query shape and consistency requirements decide whether the product fits.

## BigQuery and Cloud Storage

BigQuery executes analytical SQL over large datasets. It is suited to reporting and aggregation, while Cloud Storage holds objects and commonly supplies input to analytical systems. Cloud Storage is not an SQL database.

For BigQuery, partitioning and clustering can reduce work when filters match the layout. They do not make every query cheap. Inspect scanned data, execution details, concurrency, and the chosen billing model.

A reporting copy can lag behind an operational database. Define data ingestion, deduplication, late-arrival handling, and reconciled business measures.

## Memorystore and caching

A cache should have a defined source of truth and failure behavior. Plan expiration, invalidation, eviction, and cache misses during failover or restart. Persistence capabilities depend on the selected engine and tier; do not infer primary-database suitability merely from low latency.

## Availability and recovery

Read replicas and standby instances have different purposes. A replica can have stale data, and failover can break connections. Backups and point-in-time recovery address failures that replication alone cannot solve, including unwanted application changes.

Use tested recovery point and recovery time objectives. Include regional placement, encryption, authentication, network access, and resource limits in the deployment design.

## A practical selection sequence

1. Classify the main workload: OLTP, OLAP, keyed access, document access, cache, or objects.
2. Identify required queries, transactions, and consistency guarantees.
3. Define data size, growth, write concentration, latency, and regional requirements.
4. Check product compatibility, version support, availability, and recovery features.
5. Benchmark with representative data and compare total costs.

For exam revision, a large reporting warehouse suggests BigQuery; conventional managed relational engines suggest Cloud SQL; distributed relational transactions suggest Spanner. Treat these as clues and read the rest of the requirements rather than applying a “bulletproof” keyword rule.

## Related notes

- [Choosing a database](07_choosing_database.md)
- [AWS database services](06_aws_services.md)
- [Data warehousing](../13_big_data/01_data_warehousing.md)
- [Partitioning and sharding](../06_distributed_databases/04_partitioning_vs_sharding.md)
