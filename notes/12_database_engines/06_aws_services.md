## AWS Database Services Overview

AWS offers a variety of managed database services for different use cases, designed for high availability, scalability, and performance. These services include SQL and NoSQL databases, as well as in-memory and graph databases.

## Database Service Decision Matrix

| Service Type          | Use Case                                         | AWS Services         |
|-----------------------|--------------------------------------------------|----------------------|
| Relational Databases  | Structured data, ACID transactions               | Amazon RDS, Aurora   |
| NoSQL Databases       | Key-value/document data, flexible schema         | DynamoDB, DocumentDB |
| In-Memory Databases   | Caching, session management, real-time analytics | ElastiCache          |
| Graph Databases       | Highly connected data, complex relationship queries  | Neptune             |
| Time-Series Databases | Time-based data, IoT and operational applications| Timestream           |
| Ledger Databases      | Immutable transaction logs, verifiable data      | QLDB                 |
| Database Migration    | Database migration to AWS                        | AWS DMS              |

## AWS Database Services

### Relational Databases

- **Amazon RDS**
  - Managed relational database service supporting MySQL, PostgreSQL, Oracle, Microsoft SQL Server, and MariaDB
  - Automatic backups, patching, and monitoring
  - Multi-AZ deployment for high availability and read replicas for read scalability

- **Amazon Aurora**
  - Fully managed, MySQL- and PostgreSQL-compatible relational database
  - Up to 5 times faster than standard MySQL and 3 times faster than PostgreSQL
  - Automatic scaling, backup, and fault tolerance

### NoSQL Databases

- **Amazon DynamoDB**
  - Managed NoSQL database service, designed for single-digit millisecond latency
  - Highly scalable and supports key-value and document data models
  - Provides ACID transactions, on-demand capacity, and global tables for multi-region deployments

- **Amazon DocumentDB**
  - Fully managed, MongoDB-compatible document database
  - Highly available with automatic backup and failover
  - Supports MongoDB workloads and APIs

### In-Memory Databases

- **Amazon ElastiCache**
  - Managed in-memory data store and cache service
  - Supports Redis and Memcached engines
  - Improves application performance by reducing latency and increasing throughput

### Graph Databases

- **Amazon Neptune**
  - Fully managed graph database service
  - Supports property graph and RDF data models
  - Optimized for storing and querying highly connected data

### Time-Series Databases

- **Amazon Timestream**
  - Managed time-series database service for IoT and operational applications
  - Fast, scalable, and cost-effective
  - Built-in analytics and visualization tools

### Ledger Databases

- **Amazon QLDB**
  - Fully managed ledger database
  - Provides a transparent, immutable, and cryptographically verifiable transaction log
  - Supports SQL-like query language (PartiQL)

### Database Migration Services

- **AWS Database Migration Service (DMS)**
  - Helps migrate databases to AWS easily and securely
  - Supports homogeneous and heterogeneous migrations (e.g., Oracle to Amazon Aurora, MySQL to MySQL)
  - Minimal downtime during migration
