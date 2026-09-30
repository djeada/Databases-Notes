# Choosing a Database on AWS

Choose a service by data model, access pattern, transaction requirements, and operational constraints. A keyword such as “financial,” “serverless,” or “high scale” is a clue, not a complete architecture decision. Check service availability and compatibility before designing a new deployment.

## Workload map

| Need | Candidate | What to investigate |
| --- | --- | --- |
| Managed relational database | RDS | Engine and version support, extensions, availability topology, backups. |
| MySQL- or PostgreSQL-compatible relational service | Aurora | Compatibility differences, writer/read architecture, capacity mode, cost. |
| Distributed serverless relational workload | Aurora DSQL | SQL and feature coverage, concurrency behavior, supported regions. |
| Key-value or document access by planned keys | DynamoDB | Partition-key distribution, secondary indexes, consistency, transactions. |
| Analytical warehouse | Redshift | Data loading, distribution, columnar scans, query concurrency. |
| Cache or transient low-latency state | ElastiCache | Engine, eviction, persistence, failover, and stale-data handling. |
| Durable in-memory primary store | MemoryDB | Durability model, engine compatibility, capacity and failover. |
| MongoDB-compatible document workloads | DocumentDB | API and feature compatibility; test the application's actual operations. |
| Graph traversal | Neptune | Query model, graph shape, indexes, and supported query languages. |
| Cassandra-compatible workloads | Keyspaces | CQL compatibility, partition design, consistency and operational limits. |
| Time-series workloads | Timestream offerings | Product edition, customer eligibility, query model, and retention. |
| Files, backups, or lake data | S3 | Object layout, lifecycle, access controls, and a separate query engine when needed. |

These candidates span transactional databases, analytical systems, caches, and object storage. They are not substitutes merely because each can store data. Use the [AWS database catalog](https://aws.amazon.com/products/databases/) to check the current offerings.

## Relational choices: RDS and Aurora

RDS manages supported relational engines. Aurora supplies MySQL-compatible and PostgreSQL-compatible editions with a different managed storage architecture. Aurora DSQL is a separate distributed SQL offering; do not assume that it exposes all Aurora PostgreSQL features.

Compatibility is a migration starting point. Check SQL behavior, types, extensions, administration requirements, and the workload's performance before choosing a service.

### Availability is different from read scaling

An RDS **Multi-AZ DB instance** uses a standby for failover; that standby does not serve application reads. An RDS **Multi-AZ DB cluster** is a different deployment type with readable instances. Read replicas are another mechanism and can lag. Specify the deployment type instead of saying that every “Multi-AZ” configuration works the same way. See [RDS Multi-AZ instance deployments](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZSingleStandby.html).

Replica promotion and automatic failover can interrupt connections. Applications need reconnection logic and a way to resolve transactions whose commit outcome is unknown.

## DynamoDB: design from access patterns

DynamoDB fits access patterns that can be expressed through partition keys, sort keys, and secondary indexes. A hot key can limit a workload even when the service scales aggregate capacity. Plan common queries before committing to the key design.

Consistency is operation-specific. Strong reads are available for supported table and local secondary index operations; global secondary indexes use eventual reads. Transactions exist, so “NoSQL” does not mean “no ACID transactions.” Regional replication modes add further choices. See [DynamoDB read consistency](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadConsistency.html).

## Analytics: Redshift and S3

Redshift supports warehouse workloads with large scans, joins, and aggregation. S3 stores objects and commonly holds lake data. A query service such as Athena or a processing engine such as Spark supplies computation over that data; S3 itself does not execute relational queries.

Separate checkout transactions from large historical reports when their workloads compete. Define loading, freshness, and reconciliation rules for analytical copies.

## Caching and specialized models

ElastiCache is often used to accelerate reads or hold cache state. Define eviction, expiration, invalidation, and recovery behavior. MemoryDB targets durable in-memory database use; the correct choice depends on the application's persistence and failure requirements, not simply the presence of a Redis-compatible API.

DocumentDB is not the MongoDB server. Keyspaces is not an arbitrary Cassandra installation. Test compatibility, query behavior, limits, and migration procedures. Neptune is relevant when the key operation is relationship traversal rather than conventional table access.

## Service lifecycle changes

**QLDB is historical material, not a current deployment choice.** AWS ended its support on July 31, 2025. Older exam material associates it with an immutable, cryptographically verifiable ledger; new designs need another supported architecture and explicit audit-history guarantees. See the [AWS QLDB end-of-support notice](https://docs.aws.amazon.com/qldb/latest/developerguide/getting-started-step-7.html).

**Timestream for LiveAnalytics closed to new customers on June 20, 2025.** Distinguish it from Timestream for InfluxDB and verify customer eligibility rather than recommending “Timestream” generically. See the [LiveAnalytics availability change](https://docs.aws.amazon.com/timestream/latest/developerguide/AmazonTimestreamForLiveAnalytics-availability-change.html).

## A practical selection sequence

1. Decide whether the main workload is transactional, analytical, search, caching, or object storage.
2. List the reads and writes, their data sizes, and their latency requirements.
3. Define uniqueness, transaction, consistency, recovery, and regional requirements.
4. Check API compatibility, supported regions, limits, and customer eligibility.
5. Benchmark representative data and evaluate the full cost, including storage, I/O, transfer, backups, and operations.

For an exam question, identify the explicit requirement and deployment type. “Warehouse” points toward Redshift; “MongoDB compatible” suggests testing DocumentDB. Neither clue establishes that a service meets every unstated requirement.

## Related notes

- [Choosing a database](07_choosing_database.md)
- [Google Cloud database services](08_gcp_services.md)
- [Synchronous and asynchronous replication](../09_database_replication/04_synchronous_vs_asynchronous_replication.md)
