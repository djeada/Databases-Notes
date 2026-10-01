# Database Systems Notes

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![GitHub stars](https://img.shields.io/github/stars/djeada/Databases-Notes?style=social)](https://github.com/djeada/Databases-Notes/stargazers) [![GitHub forks](https://img.shields.io/github/forks/djeada/Databases-Notes?style=social)](https://github.com/djeada/Databases-Notes/network/members)

Practical notes on database design, SQL, transactions, storage, indexing, distributed systems, performance, security, and database operations.

The opening chapters build a bookstore example from tables and relationships to working SQL and checkout transactions. Later chapters explain storage, concurrency, distribution, and operations. Use the glossary when a term is unfamiliar and the review questions to check what you can explain.

![Database Systems Notes cover](https://github.com/user-attachments/assets/038d51ed-75bb-4f0c-ab98-1ead881f729d)

## Contents

- [Getting started](#getting-started)
- [Notes](#notes)
- [References](#references)
- [Contributing](#contributing)
- [License](#license)

## Getting started

If you are new to databases, follow this route:

1. [Introduction](notes/01_introduction_to_databases/01_databases_intro.md): read a customer table, distinguish a database from its software, and try a first query.
2. [Data models](notes/01_introduction_to_databases/04_data_models.md) and [design](notes/02_database_design/01_requirements_analysis.md): decide which facts belong together and which rules they must obey.
3. [SQL introduction](notes/03_sql/01_intro_to_sql.md): create the shared SQLite bookstore. Work through data changes, transactions, joins, aggregates, and window functions. Start each note from a fresh setup unless it explicitly continues an exercise.
4. [ACID](notes/04_acid_properties_and_transactions/01_transactions_intro.md): understand why checkout needs more than individually valid statements.
5. [Storage](notes/05_storage_and_indexing/01_how_tables_and_indexes_are_stored_on_disk.md) and [concurrency](notes/07_concurrency_control/01_shared_vs_exclusive_locks.md): learn how reads, writes, and competing operations work underneath SQL.
6. [Distributed databases](notes/06_distributed_databases/01_distributed_database_systems.md) and [replication](notes/09_database_replication/01_intro_to_replication.md): add machines only after understanding the new routing, timing, and failure questions.

Then explore performance, security, engine choices, analytics, and ORMs according to your needs. The numbered contents are a reference map; you do not need to read every engine or cloud-service chapter before writing useful SQL.

The introductory exercises use SQLite. Procedure and permission exercises explicitly switch to PostgreSQL; later notes use several named engines. Run code in its stated engine, because syntax and guarantees differ. A code fragment illustrating a concept is not always a complete setup script. Expected failures are marked in the text.

Use the [glossary](notes/01_introduction_to_databases/05_glossary.md) as a reference rather than a prerequisite. For each exercise, predict the result, run it, and explain why those rows appear before moving on.

### SQL playgrounds

- [SQLite Online](https://sqliteonline.com/) — Run SQLite queries in the browser.
- [SQL Practice](https://www.sql-practice.com/) — Practice queries with immediate feedback.
- [SQL Forever](http://sqlforever.com/) — Use a lightweight online SQL interpreter.
- [DB Fiddle](https://dbfiddle.uk/) — Test queries across several database engines.

### Sample databases

- [PostgreSQL sample databases](https://wiki.postgresql.org/wiki/Sample_Databases) — Community-maintained datasets for PostgreSQL.
- [MySQL sample databases](https://dev.mysql.com/doc/index-other.html) — Official example datasets and supplementary downloads.
- [Sakila](https://dev.mysql.com/doc/sakila/en/) — A small video-rental database for learning SQL and schema design.

## Notes

### 1. Introduction to Databases

- [Databases Introduction](notes/01_introduction_to_databases/01_databases_intro.md) — Overview of database fundamentals and core concepts.
- [Types of Databases](notes/01_introduction_to_databases/02_types_of_databases.md) — Exploring relational, NoSQL, and other database types.
- [Database Management Systems](notes/01_introduction_to_databases/03_database_management_systems_dbms_.md) — Understanding DBMS functions and types.
- [Data Models](notes/01_introduction_to_databases/04_data_models.md) — Methods of structuring and representing data.
- [Glossary](notes/01_introduction_to_databases/05_glossary.md) — Key terms and definitions.

### 2. Database Design

- [Requirements Analysis](notes/02_database_design/01_requirements_analysis.md) — Determining user needs for database development.
- [Normalization](notes/02_database_design/02_normalization.md) — Minimizing redundancy through proper organization.
- [Denormalization](notes/02_database_design/03_denormalization.md) — Optimizing performance through strategic redundancy.
- [Indexing Strategies](notes/02_database_design/04_indexing_strategies.md) — Optimizing query performance with indexes.
- [Data Integrity](notes/02_database_design/05_data_integrity.md) — Ensuring accuracy and consistency of data.

### 3. SQL

- [Introduction to SQL](notes/03_sql/01_intro_to_sql.md) — Build the SQLite bookstore and learn queries from expected results.
- [DDL - Data Definition](notes/03_sql/02_data_definition_language_ddl.md) — CREATE, ALTER, DROP commands.
- [DML - Data Manipulation](notes/03_sql/03_data_manipulation_language_dml.md) — SELECT, INSERT, UPDATE, DELETE.
- [DCL - Data Control](notes/03_sql/04_data_control_language_dcl.md) — GRANT and REVOKE permissions.
- [TCL - Transaction Control](notes/03_sql/05_transaction_control_language_tcl.md) — COMMIT, ROLLBACK, SAVEPOINT.
- [Joins, Subqueries & Views](notes/03_sql/06_joins_subqueries_and_views.md) — Combining data from multiple tables.
- [Stored Procedures](notes/03_sql/07_stored_procedures_and_functions.md) — Reusable SQL code blocks.
- [Triggers](notes/03_sql/08_triggers.md) — Automated database actions.
- [Hierarchical Data](notes/03_sql/09_hierarchical_data.md) — Managing tree-like structures.

- [Aggregate Functions](notes/03_sql/10_aggregate_functions.md) — Grouping, totals, and null handling.
- [Window Functions](notes/03_sql/11_window_functions.md) — Ranking and calculations without collapsing rows.

### 4. ACID Properties and Transactions

- [What is a Transaction](notes/04_acid_properties_and_transactions/01_transactions_intro.md) — Overview of database transactions.
- [Atomicity](notes/04_acid_properties_and_transactions/02_atomicity.md) — All-or-nothing transaction property.
- [Consistency](notes/04_acid_properties_and_transactions/03_consistency.md) — Maintaining database integrity.
- [Isolation](notes/04_acid_properties_and_transactions/04_isolation.md) — Independent transaction execution.
- [Durability](notes/04_acid_properties_and_transactions/05_durability.md) — Permanent transaction results.

### 5. Database Storage and Indexing

- [Storage on Disk](notes/05_storage_and_indexing/01_how_tables_and_indexes_are_stored_on_disk.md) — How logical tables, indexes, pages, files, caches, and recovery logs reach storage.
- [Row vs Column Storage](notes/05_storage_and_indexing/02_row_based_vs_column_based_databases.md) — Compare row-oriented transactional layouts with column-oriented analytical storage.
- [Primary vs Secondary Keys](notes/05_storage_and_indexing/03_primary_key_vs_secondary_key.md) — Separate logical identification rules from physical access structures.
- [Database Pages](notes/05_storage_and_indexing/04_database_pages.md) — Understand pages, buffer caches, row layout, free space, and I/O.
- [Indexing Overview](notes/05_storage_and_indexing/05_indexing.md) — B-tree, composite, covering, partial, expression, specialized, and maintenance concepts.
- [B-Tree Internals & Page Splits](notes/05_storage_and_indexing/06_btree_internals_and_page_splits.md) — Tree levels, leaf pages, key width, insert patterns, fill factor, and page splits.
- [Composite Indexes & Column Order](notes/05_storage_and_indexing/07_composite_indexes_and_column_order.md) — Leading prefixes, equality/range ordering, sorting, joins, and workload-driven column order.
- [Covering, Partial & Expression Indexes](notes/05_storage_and_indexing/08_covering_partial_and_expression_indexes.md) — INCLUDE/index-only access, filtered subsets, function indexes, and combined designs.
- [Clustered Indexes, Heaps & Row Locality](notes/05_storage_and_indexing/09_clustered_indexes_heap_tables_and_row_locality.md) — Compare PostgreSQL heaps, InnoDB clustering, SQL Server clustering, and SQLite WITHOUT ROWID.
- [Specialized Index Structures](notes/05_storage_and_indexing/10_specialized_index_structures.md) — Hash, bitmap, inverted/GIN, GiST, SP-GiST, BRIN, spatial, and data-skipping structures.
- [Index Maintenance, Bloat & Online Operations](notes/05_storage_and_indexing/11_index_maintenance_bloat_and_online_operations.md) — Index lifecycle, redundancy, concurrent builds/rebuilds, monitoring, and safe removal.

### 6. Distributed Databases

- [Distributed DB Introduction](notes/06_distributed_databases/01_distributed_database_systems.md) — Basic concepts and architectures overview.
- [Partitioning](notes/06_distributed_databases/02_partitioning.md) — Methods of dividing and distributing data.
- [Sharding](notes/06_distributed_databases/03_sharding.md) — Breaking tables into distributed chunks.
- [Partitioning vs Sharding](notes/06_distributed_databases/04_partitioning_vs_sharding.md) — Understanding the differences.
- [Consistent Hashing](notes/06_distributed_databases/05_consistent_hashing.md) — Distributing data with minimal rehashing.
- [CAP Theorem](notes/06_distributed_databases/06_cap_theorem.md) — Consistency, availability, partition tolerance.
- [Eventual Consistency](notes/06_distributed_databases/07_eventual_consistency.md) — Convergence model for distributed systems.
- [Advanced Distributed Systems](notes/06_distributed_databases/08_distributed_database_systems.md) — Load balancing, replication, and sharding patterns.

### 7. Concurrency Control and Locking

- [Shared vs Exclusive Locks](notes/07_concurrency_control/01_shared_vs_exclusive_locks.md) — Different locking mechanisms.
- [Deadlocks](notes/07_concurrency_control/02_deadlocks.md) — Understanding and resolving deadlock situations.
- [Two-Phase Locking](notes/07_concurrency_control/03_two_phase_locking.md) — Lock acquisition and release protocol.
- [Double Booking Problem](notes/07_concurrency_control/04_double_booking_problem.md) — Concurrent resource booking challenges.
- [Isolation Levels](notes/07_concurrency_control/05_serializable_vs_repeatable_read.md) — Serializable vs Repeatable Read.

### 8. Database Performance and Optimization

- [Query Optimization](notes/08_database_performance/01_query_optimization_techniques.md) — Diagnose and reduce unnecessary query work with measured plans.
- [Indexing Strategies](notes/08_database_performance/02_indexing_strategies.md) — Choose index access methods while accounting for write and maintenance cost.
- [Database Caching](notes/08_database_performance/03_database_caching.md) — Reuse application results with explicit freshness and invalidation.
- [Materialized Views](notes/08_database_performance/04_materialized_views.md) — Precompute expensive reusable results with explicit refresh and staleness rules.
- [Database Access in Code](notes/08_database_performance/05_accessing_database_in_code.md) — Efficient drivers, transactions, parameters, streaming, timeouts, and retries.
- [Working with a Billion-Row Table](notes/08_database_performance/06_working_with_billion_row_table.md) — Workload-driven strategies for very large tables.
- [Execution Plans, Statistics & Cardinality](notes/08_database_performance/07_execution_plans_statistics_and_cardinality.md) — Read plans, diagnose estimate errors, skew, joins, sorts, and access paths.
- [Connection Pooling, Batching & N+1](notes/08_database_performance/08_connection_pooling_batching_and_n_plus_one.md) — Reduce setup and round-trip overhead while bounding concurrency.
- [Pagination & Large Result Sets](notes/08_database_performance/09_pagination_and_large_result_sets.md) — Offset vs keyset pagination, projection, streaming, and stable cursors.
- [Partitioning, Sharding & Data Locality](notes/08_database_performance/10_partitioning_sharding_and_data_locality.md) — Pruning, shard keys, hotspots, cross-shard work, and locality.
- [Benchmarking, Load Testing & Capacity](notes/08_database_performance/11_benchmarking_load_testing_and_capacity.md) — Build representative workloads, find saturation, and plan headroom.
- [Write Performance, Vacuum & Bloat](notes/08_database_performance/12_write_performance_vacuum_and_bloat.md) — Understand index write cost, MVCC cleanup, WAL, maintenance, and backfills.

### 9. Database Replication

- [Replication Introduction](notes/09_database_replication/01_intro_to_replication.md) — Overview of database replication concepts.
- [Master-Standby](notes/09_database_replication/02_master_standby_replication.md) — Primary-replica replication model.
- [Multi-Master](notes/09_database_replication/03_multi_master_replication.md) — Multiple active nodes replication.
- [Sync vs Async](notes/09_database_replication/04_synchronous_vs_asynchronous_replication.md) — Replication timing strategies.

### 10. NoSQL Databases

- [NoSQL Introduction](notes/10_nosql_databases/01_nosql_databases_intro.md) — Choose models from access patterns rather than the NoSQL label.
- [NoSQL Types](notes/10_nosql_databases/02_types_of_nosql_databases.md) — Key-value, document, wide-column, and graph model overview.
- [Querying NoSQL](notes/10_nosql_databases/03_querying_nosql_databases.md) — Compare MongoDB, Redis, Cassandra, and Neo4j query shapes with runnable examples.
- [CRUD: SQL vs NoSQL](notes/10_nosql_databases/04_crud_in_sql_vs_nosql.md) — Compare relational CRUD with MongoDB document operations.
- [Document Modeling](notes/10_nosql_databases/05_document_modeling.md) — Embedding vs references, bounded aggregates, schema evolution, indexes, and concurrency.
- [Key-Value Modeling](notes/10_nosql_databases/06_key_value_modeling.md) — Key design, TTLs, caching, atomic commands, idempotency, and hotspots.
- [Wide-Column Modeling](notes/10_nosql_databases/07_wide_column_modeling.md) — Query-first tables, partition keys, clustering, bucketing, denormalization, and tombstones.
- [Graph Modeling](notes/10_nosql_databases/08_graph_modeling.md) — Nodes, relationships, path traversal, supernodes, graph projections, and Cypher.
- [Consistency, Transactions & Replication](notes/10_nosql_databases/09_consistency_transactions_and_replication.md) — Atomicity boundaries, replication, quorums, conflicts, retries, and multi-region trade-offs.
- [Operating NoSQL & Polyglot Persistence](notes/10_nosql_databases/10_operating_nosql_and_polyglot_persistence.md) — Source-of-truth design, CDC/projections, backups, capacity, observability, and operational ownership.

### 11. Database Security and Best Practices

- [Backup & Recovery](notes/11_security_best_practices/01_backup_and_recovery_strategies.md) — Backup types, RPO/RTO, point-in-time recovery, restore validation, and recovery planning.
- [Database Security](notes/11_security_best_practices/02_database_security.md) — Defense-in-depth overview across identity, networks, data, monitoring, and operations.
- [Capacity Planning](notes/11_security_best_practices/03_capacity_planning.md) — Workload growth, resource forecasting, headroom, scaling, and cost.
- [Database Migration](notes/11_security_best_practices/04_database_migration.md) — Moving schemas/data safely with validation, synchronization, rollback, and decommissioning.
- [Performance Monitoring & Tuning](notes/11_security_best_practices/05_performance_monitoring_and_tuning.md) — SLOs, query plans, waits, connections, indexes, storage, replication lag, and measured tuning.
- [SQL Injection](notes/11_security_best_practices/06_sql_injection.md) — Parameter binding, safe dynamic SQL, ORM/raw-query pitfalls, testing, and least-privilege containment.
- [Crash Recovery](notes/11_security_best_practices/07_crash_recovery_in_databases.md) — WAL/redo, checkpoints, recovery, and durability after process or host failure.
- [Identity, Authentication & Access Control](notes/11_security_best_practices/08_identity_authentication_and_access_control.md) — Roles, least privilege, workload identities, RLS, service accounts, and privilege reviews.
- [Encryption, Secrets & Key Management](notes/11_security_best_practices/09_encryption_secrets_and_key_management.md) — TLS, encryption at rest/in the application, password hashing, KMS, rotation, and secret injection.
- [Auditing, Compliance & Data Governance](notes/11_security_best_practices/10_auditing_compliance_and_data_governance.md) — Audit layers, data classification, retention, masking, log integrity, and governance evidence.
- [Database Hardening & Patch Management](notes/11_security_best_practices/11_database_hardening_and_patch_management.md) — Network/host/container hardening, supported versions, patching, baselines, and resource limits.
- [Incident Response & DR Drills](notes/11_security_best_practices/12_incident_response_and_disaster_recovery_drills.md) — Containment, evidence, failover versus restore, RPO/RTO, restore tests, tabletops, and game days.

### 12. Database Engines

- [SQLite](notes/12_database_engines/01_sqlite.md) — Lightweight, serverless SQL database.
- [MySQL](notes/12_database_engines/02_mysql.md) — Popular open-source RDBMS.
- [PostgreSQL](notes/12_database_engines/03_postgresql.md) — Advanced open-source database system.
- [MongoDB](notes/12_database_engines/04_mongodb.md) — Document-oriented NoSQL database.
- [Neo4j](notes/12_database_engines/05_neo4j.md) — Property-graph database and Cypher query model.
- [AWS Database Services](notes/12_database_engines/06_aws_services.md) — Choosing managed database services on AWS.
- [Choosing a Database](notes/12_database_engines/07_choosing_database.md) — Selection criteria, workload patterns, scaling, availability, and cost.
- [GCP Database Services](notes/12_database_engines/08_gcp_services.md) — Choosing managed database services on Google Cloud.
- [Microsoft SQL Server](notes/12_database_engines/09_sql_server.md) — SQL Server setup, T-SQL, indexing, concurrency, columnstore, HA, and Microsoft ecosystem use.
- [Redis](notes/12_database_engines/10_redis.md) — In-memory data structures, caching, TTLs, persistence, replication, and clustering.
- [Apache Cassandra](notes/12_database_engines/11_cassandra.md) — Wide-column modeling, partition keys, tunable consistency, replication, and LSM storage.
- [OpenSearch and Elasticsearch](notes/12_database_engines/12_elasticsearch_and_opensearch.md) — Full-text search, mappings, analyzers, shards, replicas, and search-engine architecture.
- [ClickHouse](notes/12_database_engines/13_clickhouse.md) — Columnar OLAP, MergeTree design, sorting keys, partitions, and real-time analytics.
- [Distributed SQL](notes/12_database_engines/14_distributed_sql.md) — Consensus, distributed transactions, ranges, multi-region placement, and CockroachDB examples.
- [Azure Database Services](notes/12_database_engines/15_azure_services.md) — Choosing Azure SQL, PostgreSQL, MySQL, Cosmos DB, Managed Redis, and related services.

### 13. Big Data and Data Warehousing

- [Data Warehousing](notes/13_big_data/01_data_warehousing.md) — Architectures for large-scale analytics.
- [Hadoop & HDFS](notes/13_big_data/02_hadoop_and_hdfs.md) — Distributed file system for big data.
- [Spark SQL](notes/13_big_data/03_spark_sql.md) — Large-scale data processing with SQL.
- [Data Lakes and Lakehouses](notes/13_big_data/04_data_lakes_and_lakehouses.md) — Object storage, Parquet, table formats, catalogs, snapshots, and lakehouse trade-offs.
- [Streaming, Kafka, and CDC](notes/13_big_data/05_streaming_kafka_and_cdc.md) — Event logs, partitions, consumer groups, delivery semantics, CDC, and the outbox pattern.
- [Data Pipelines, Orchestration, and Data Quality](notes/13_big_data/06_data_pipelines_orchestration_and_quality.md) — DAGs, retries, backfills, dbt, lineage, quality tests, and production pipeline design.

### 14. Object-Relational Mapping (ORM)

- [ORM Introduction](notes/14_orm/01_introduction_to_orm.md) — Bridging OOP and relational databases.
- [Popular ORM Tools](notes/14_orm/02_popular_orm_tools.md) — Hibernate, Entity Framework, SQLAlchemy, Django ORM, Prisma, and related approaches.
- [Schema Migrations](notes/14_orm/03_schema_migrations.md) — Alembic-style migrations, expand-and-contract deployments, backfills, and production safety.
- [Relationship Loading and Query Performance](notes/14_orm/04_relationship_loading_and_query_performance.md) — N+1 queries, eager loading, projections, pagination, generated SQL, and execution plans.
- [Transactions, Concurrency, and Unit of Work](notes/14_orm/05_transactions_concurrency_and_unit_of_work.md) — Flush/commit semantics, optimistic and pessimistic locking, retries, and concurrency-safe writes.

## Exercises and demonstrations

- [Review quiz](notes/quizes.md) — Questions and worked SQL exercises.
- [Runnable database demonstrations](scripts/README.md) — Engine-specific examples and setup instructions.
- [SQL Server indexing walkthrough](projectes/indexes_in_microsoft_sql_server.md) — A practical indexing project.

## References

### Books

- [Database System Concepts, 7th Edition](https://amzn.to/4jrbQPX) by Abraham Silberschatz, Henry Korth, and S. Sudarshan — A broad introduction to database theory and implementation.
- [Database Systems: The Complete Book](https://amzn.to/4j3Qati) by Hector Garcia-Molina, Jeffrey Ullman, and Jennifer Widom — A detailed treatment of database systems and internals.
- [SQL and Relational Theory](https://amzn.to/42myfag) by C. J. Date — A rigorous discussion of relational principles and SQL.
- [Seven Databases in Seven Weeks](https://amzn.to/3R2vl5c) by Luc Perkins, Eric Redmond, and Jim R. Wilson — A practical survey of different database models.
- [NoSQL Distilled](https://amzn.to/4i54Oiu) by Pramod Sadalage and Martin Fowler — A concise introduction to polyglot persistence and NoSQL systems.

### Courses

- [Cornell CS4320: Introduction to Database Systems](https://www.cs.cornell.edu/courses/cs4320/)
- [CMU 15-445/645: Database Systems](https://15445.courses.cs.cmu.edu/fall2023/)

### Practice and visual guides

- [PostgreSQL Exercises](https://pgexercises.com/) — Practical SQL exercises.
- [SQLZoo](https://sqlzoo.net/wiki/SQL_Tutorial) — Interactive SQL tutorials.
- [Understanding Joins](https://joins.spathon.com/) — A visual guide to SQL joins.
- [DataLemur SQL interview questions](https://datalemur.com/sql-interview-questions) — Query practice for technical interviews.

### Further reading

- [How Databases Work](http://coding-geek.com/how-databases-work/) — An introduction to database internals.
- [SQL Tutorial in Russian](http://www.sql-tutorial.ru/) — A comprehensive Russian-language SQL tutorial.
- [Discussion: why NoSQL databases can scale differently](https://softwareengineering.stackexchange.com/questions/194340/why-are-nosql-databases-more-scalable-than-sql/194408#194408)

## Contributing

Corrections, examples, and new topics are welcome.

1. Fork the repository.
2. Create a focused branch, for example `git checkout -b improve/indexing-notes`.
3. Make and review your changes.
4. Commit with a clear message.
5. Push the branch and open a pull request.

Please keep contributions accurate, concise, and consistent with the surrounding notes. Include practical examples and references where they improve clarity.

## License

This project is available under the [MIT License](license).
