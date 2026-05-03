## Choosing a Database on AWS

Choosing the right AWS database can significantly influence your project’s reliability, performance, cost, scalability, and operational complexity. In AWS exam questions, database scenarios usually describe a workload and expect you to match it to the best purpose-built AWS service.

A practical way to start is to ask:

* Is this application traffic or analytics traffic?
* Is the data relational, document-like, key-value, graph-like, time-series, or file-based?
* Do you need SQL?
* Do you need transactions?
* Do you need global scale?
* Do you need low-latency reads and writes?
* Do you need a cache rather than a primary database?
* Do you need to analyze huge datasets?
* Do you need compatibility with MySQL, PostgreSQL, Oracle, SQL Server, MongoDB, Cassandra, or Redis?

A useful rule of thumb:

**Choose the AWS database based on workload first. Choose the product name second.**

The most important exam distinction is:

```text
OLTP = application database
OLAP = analytics database
```

**OLTP** means user-facing applications doing small reads, writes, updates, and transactions.

**OLAP** means analytics, dashboards, reports, aggregations, and large scans over big datasets.

AWS officially groups its database options by workload, including relational databases like Amazon RDS and Aurora, key-value databases like DynamoDB, in-memory databases like ElastiCache and MemoryDB, graph databases like Neptune, time-series databases like Timestream, and data warehouse services like Redshift. ([AWS Documentation][1])

### AWS Database Options

#### Amazon RDS

Amazon RDS is AWS’s managed relational database service.

It supports common relational engines such as **PostgreSQL, MySQL, MariaDB, Oracle, SQL Server, and Db2**. ([AWS Documentation][2])

It is the safest default choice when the question describes a normal relational application.

**Best for:** traditional applications, structured data, SQL queries, transactions, existing database migrations, ERP, CRM, e-commerce, and line-of-business systems.

| Best for                                                          | AWS service    | Key traits                                                                              |
| ----------------------------------------------------------------- | -------------- | --------------------------------------------------------------------------------------- |
| Standard relational apps, orders, users, inventory, ERP, CRM, CMS | **Amazon RDS** | Managed relational database, SQL, joins, transactions, backups, read replicas, Multi-AZ |

Example:

```text
+----+----------+----------+
| id | customer | balance  |
+----+----------+----------+
|  1 | Omar     | 1250.00  |
|  2 | Layla    |   93.70  |
+----+----------+----------+
```

Use **Amazon RDS** when the question says:

* managed MySQL
* managed PostgreSQL
* managed MariaDB
* managed Oracle
* managed SQL Server
* managed Db2
* relational database
* SQL transactions
* joins
* existing database migration
* traditional enterprise application
* Multi-AZ high availability
* read replicas

Avoid RDS when the question requires:

* massive serverless key-value scale,
* single-digit millisecond NoSQL performance at huge scale,
* petabyte-scale analytics,
* graph traversal,
* time-series optimization,
* in-memory caching.

Exam rule:

**Normal relational database on AWS = Amazon RDS.**

#### Amazon Aurora

Amazon Aurora is AWS’s cloud-optimized relational database compatible with **MySQL and PostgreSQL**.

It is usually chosen when the question asks for a relational database like MySQL/PostgreSQL but emphasizes **higher performance, high availability, cloud-native scaling, or global database features**. AWS describes Aurora as offering high performance and availability at global scale with MySQL and PostgreSQL compatibility. ([AWS Documentation][1])

**Best for:** high-performance relational applications, cloud-native MySQL/PostgreSQL workloads, SaaS platforms, e-commerce, financial applications, and systems needing better availability than standard self-managed relational databases.

| Best for                                               | AWS service       | Key traits                                                                                       |
| ------------------------------------------------------ | ----------------- | ------------------------------------------------------------------------------------------------ |
| High-performance MySQL/PostgreSQL-compatible workloads | **Amazon Aurora** | MySQL/PostgreSQL compatibility, managed, high availability, read scaling, Aurora Global Database |

Use **Aurora** when the question says:

* MySQL-compatible
* PostgreSQL-compatible
* high-performance relational database
* cloud-native relational database
* highly available relational database
* global database with MySQL/PostgreSQL compatibility
* faster than standard MySQL/PostgreSQL
* enterprise relational workload

Avoid Aurora when:

* you need Oracle, SQL Server, MariaDB, or Db2 specifically,
* you need pure key-value NoSQL,
* you need graph queries,
* you need data warehouse analytics,
* you need only the simplest cheapest relational option.

Exam rule:

**MySQL/PostgreSQL-compatible + high performance/high availability = Aurora.**

#### Amazon DynamoDB

Amazon DynamoDB is AWS’s fully managed serverless NoSQL key-value and document database.

It is designed for high-scale applications needing very low latency and massive throughput.

**Best for:** serverless applications, key-value access, shopping carts, user profiles, gaming, IoT metadata, mobile apps, high-scale web apps, event-driven systems, and workloads with predictable access patterns.

| Best for                                   | AWS service         | Key traits                                                                                               |
| ------------------------------------------ | ------------------- | -------------------------------------------------------------------------------------------------------- |
| Massive scale key-value/document workloads | **Amazon DynamoDB** | Serverless NoSQL, key-value/document, single-digit millisecond latency, automatic scaling, global tables |

Example:

```json
{
  "PK": "USER#123",
  "SK": "PROFILE",
  "name": "Omar",
  "city": "Berlin",
  "plan": "Pro"
}
```

Use **DynamoDB** when the question says:

* serverless NoSQL
* key-value database
* document database
* single-digit millisecond latency
* massive scale
* high throughput
* automatic scaling
* unpredictable traffic
* global tables
* shopping cart
* gaming leaderboard
* user profile
* IoT application metadata

Avoid DynamoDB when:

* you need many joins,
* you need complex ad hoc SQL,
* access patterns are unknown,
* you need relational constraints,
* you need data warehouse analytics.

Exam rule:

**Serverless NoSQL + key-value/document + massive scale = DynamoDB.**

#### Amazon Redshift

Amazon Redshift is AWS’s managed data warehouse for analytics.

It is not a normal application database. It is for analyzing large datasets using SQL. AWS describes Redshift as an OLAP system, unlike RDS databases, which are OLTP systems. ([Trailhead][3])

**Best for:** data warehousing, BI, dashboards, reporting, large SQL analytics, historical analysis, and analytical queries over large datasets.

| Best for                                    | AWS service         | Key traits                                                                 |
| ------------------------------------------- | ------------------- | -------------------------------------------------------------------------- |
| Analytics and reporting over large datasets | **Amazon Redshift** | Data warehouse, OLAP, SQL analytics, columnar storage, MPP, BI integration |

Example:

```sql
SELECT
  country,
  COUNT(*) AS purchases,
  SUM(amount) AS revenue
FROM sales
GROUP BY country;
```

Use **Redshift** when the question says:

* data warehouse
* analytics
* BI
* dashboard
* reporting
* aggregate queries
* OLAP
* columnar storage
* large SQL scans
* historical analysis
* analyze data from S3
* petabyte-scale warehouse

Avoid Redshift when:

* you need a user-facing transactional app database,
* you need many small row updates,
* you need single-record millisecond reads/writes,
* you need a cache.

Exam rule:

**Analytics + data warehouse + SQL = Redshift.**

#### Amazon ElastiCache

Amazon ElastiCache is AWS’s managed in-memory caching service for **Redis/Valkey and Memcached**.

It is usually not the primary database. It is a performance layer in front of another database.

**Best for:** caching, sessions, leaderboards, rate limiting, hot reads, temporary data, and reducing load on a primary database.

| Best for                                      | AWS service            | Key traits                                                          |
| --------------------------------------------- | ---------------------- | ------------------------------------------------------------------- |
| In-memory caching and very low-latency access | **Amazon ElastiCache** | Redis/Valkey or Memcached-compatible, low latency, TTL, cache layer |

Example:

```text
Client → ElastiCache → Primary database
            │
            └── TTL: 60 seconds
```

Use **ElastiCache** when the question says:

* cache
* Redis
* Valkey
* Memcached
* session store
* leaderboard
* rate limiting
* temporary data
* reduce database load
* low-latency repeated reads

Avoid ElastiCache when:

* you need durable primary storage,
* you need relational transactions,
* you need analytics,
* you need long-term data retention.

Exam rule:

**Cache / Redis / Memcached = ElastiCache.**

#### Amazon MemoryDB

Amazon MemoryDB is a Redis-compatible, durable, in-memory database service.

This is different from ElastiCache. ElastiCache is usually a cache. MemoryDB can be used as a primary database for workloads that need Redis-compatible APIs with durability.

**Best for:** durable Redis-compatible applications, ultra-low-latency primary database use cases, event processing, gaming, financial workloads, and microservices needing in-memory speed with persistence.

| Best for                                  | AWS service         | Key traits                                                                    |
| ----------------------------------------- | ------------------- | ----------------------------------------------------------------------------- |
| Durable Redis-compatible primary database | **Amazon MemoryDB** | Redis-compatible, in-memory speed, durable storage, primary database use case |

Use **MemoryDB** when the question says:

* Redis-compatible primary database
* durable in-memory database
* ultra-low latency with durability
* not just a cache

Avoid MemoryDB when:

* the question only says cache,
* you only need temporary session caching,
* you need relational SQL,
* you need analytics.

Exam rule:

**Redis-compatible durable primary database = MemoryDB.**

**Cache = ElastiCache. Durable Redis primary DB = MemoryDB.**

#### Amazon DocumentDB

Amazon DocumentDB is AWS’s managed document database with MongoDB compatibility.

It is used when the question describes MongoDB-style JSON document workloads.

**Best for:** JSON documents, content management, catalogs, user profiles, MongoDB-compatible applications, semi-structured data.

| Best for                              | AWS service           | Key traits                                                        |
| ------------------------------------- | --------------------- | ----------------------------------------------------------------- |
| MongoDB-compatible document workloads | **Amazon DocumentDB** | Document database, JSON-like data, MongoDB compatibility, managed |

Example:

```json
{
  "product_id": "P100",
  "name": "Laptop",
  "attributes": {
    "ram": "16GB",
    "storage": "512GB"
  }
}
```

Use **DocumentDB** when the question says:

* MongoDB-compatible
* document database
* JSON documents
* flexible schema
* content catalog
* semi-structured records
* migrate MongoDB workload

Avoid DocumentDB when:

* you need simple key-value scale,
* you need graph traversal,
* you need time-series optimization,
* you need SQL data warehouse analytics.

Exam rule:

**MongoDB-compatible document database = DocumentDB.**

#### Amazon Neptune

Amazon Neptune is AWS’s managed graph database.

It is chosen when relationships between entities are the main thing being queried.

**Best for:** social networks, fraud detection, recommendations, knowledge graphs, identity graphs, network dependencies, relationship traversal.

| Best for                           | AWS service        | Key traits                                                                                 |
| ---------------------------------- | ------------------ | ------------------------------------------------------------------------------------------ |
| Highly connected relationship data | **Amazon Neptune** | Graph database, nodes and edges, relationship traversal, Gremlin/SPARQL/openCypher support |

Example:

```text
(Omar)──knows──(Layla)
  │              │
bought         works_at
  │              │
  ▼              ▼
(Product)     (Company)
```

Use **Neptune** when the question says:

* graph database
* nodes and edges
* relationship traversal
* social graph
* fraud rings
* recommendations
* knowledge graph
* identity graph
* dependency graph

Avoid Neptune when:

* you only need simple relational joins,
* you need key-value lookups,
* you need data warehouse analytics,
* relationships are not the main query pattern.

Exam rule:

**Graph relationships / nodes and edges = Neptune.**

#### Amazon Timestream

Amazon Timestream is AWS’s time-series database.

It is optimized for data points indexed by time.

**Best for:** IoT telemetry, DevOps metrics, application monitoring, sensor readings, industrial data, time-window queries.

| Best for                                  | AWS service           | Key traits                                                                       |
| ----------------------------------------- | --------------------- | -------------------------------------------------------------------------------- |
| Time-series data and time-window analysis | **Amazon Timestream** | Time-series database, timestamp indexing, retention, rollups, time-based queries |

Example:

```text
device_id: sensor-123
time: 2026-05-03T10:00:00Z
temperature: 22.4
humidity: 41
```

Use **Timestream** when the question says:

* time-series database
* IoT telemetry
* sensor readings
* metrics
* monitoring
* time-window queries
* average over last hour
* retention policies
* rollups/downsampling

Avoid Timestream when:

* you need general-purpose relational transactions,
* you need document storage,
* you need graph traversal,
* you need data warehouse analytics over many unrelated datasets.

Exam rule:

**Time-series metrics / IoT sensor data = Timestream.**

#### Amazon Keyspaces

Amazon Keyspaces is AWS’s managed Apache Cassandra-compatible database service.

It is chosen when the question specifically mentions Cassandra compatibility or Cassandra workloads.

**Best for:** Cassandra-compatible applications, wide-column workloads, high-scale distributed NoSQL systems.

| Best for                                   | AWS service          | Key traits                                                               |
| ------------------------------------------ | -------------------- | ------------------------------------------------------------------------ |
| Cassandra-compatible wide-column workloads | **Amazon Keyspaces** | Managed Cassandra-compatible database, wide-column model, scalable NoSQL |

Use **Keyspaces** when the question says:

* Cassandra-compatible
* Apache Cassandra migration
* CQL
* wide-column NoSQL
* existing Cassandra workload

Avoid Keyspaces when:

* you need MongoDB compatibility,
* you need Redis,
* you need relational SQL,
* you need graph queries.

Exam rule:

**Cassandra-compatible = Amazon Keyspaces.**

#### Amazon QLDB

Amazon QLDB is AWS’s ledger database.

It is designed for immutable, cryptographically verifiable transaction history.

**Best for:** systems needing an immutable audit trail, financial ledgers, supply chain history, insurance claims, registration systems.

| Best for                    | AWS service     | Key traits                                                     |
| --------------------------- | --------------- | -------------------------------------------------------------- |
| Immutable verifiable ledger | **Amazon QLDB** | Append-only journal, cryptographic verification, audit history |

Use **QLDB** when the question says:

* immutable ledger
* cryptographically verifiable history
* complete audit trail
* append-only transaction log
* verify every change
* centralized trusted ledger

Avoid QLDB when:

* you need decentralized blockchain,
* you need normal relational database queries,
* you need analytics warehouse,
* you only need ordinary audit columns.

Exam rule:

**Immutable verifiable ledger = QLDB.**

#### Amazon S3

Amazon S3 is not a database, but it appears often in database-style exam questions.

It is object storage for files, blobs, backups, logs, data lakes, images, videos, and static assets.

**Best for:** unstructured data, images, videos, backups, exports, raw logs, data lake storage, static files.

| Best for                                                     | AWS service   | Key traits                                               |
| ------------------------------------------------------------ | ------------- | -------------------------------------------------------- |
| Files, images, videos, backups, blobs, raw data lake objects | **Amazon S3** | Object storage, highly durable, scalable, cost-effective |

Example:

```text
s3://company-data-lake/raw/events/2026/05/03/events.json
s3://app-uploads/images/profile-picture.png
s3://database-backups/prod-backup.sql
```

Use **S3** when the question says:

* store files
* images
* videos
* backups
* logs
* static assets
* object storage
* data lake
* raw events
* archive data

Avoid S3 when:

* you need transactions,
* you need low-latency row updates,
* you need SQL as the primary application access pattern,
* you need a relational database.

Exam rule:

**Files / blobs / backups / data lake = S3.**

### Decision-Making Rules for AWS Exams

#### First Question: OLTP or OLAP?

```text
                       ┌────────────────────────────┐
                       │ What is the workload type? │
                       └────────────────────────────┘
                                      │
                 ┌────────────────────┴────────────────────┐
                 ▼                                         ▼
        Application database                         Analytics
        OLTP                                        OLAP
                 │                                         │
                 ▼                                         ▼
 RDS / Aurora / DynamoDB / DocumentDB /       Redshift
 Neptune / Timestream / Keyspaces
```

Use this rule:

| Workload                        | Pick                                                              |
| ------------------------------- | ----------------------------------------------------------------- |
| Application reads/writes        | RDS, Aurora, DynamoDB, DocumentDB, Neptune, Timestream, Keyspaces |
| Analytics, reports, dashboards  | Redshift                                                          |
| Files and raw data lake objects | S3                                                                |
| Cache                           | ElastiCache                                                       |

Exam rule:

**If users are using the app, think OLTP. If analysts are querying data, think Redshift.**

#### Structured Data Decision Tree

```text
                       ┌─────────────────┐
                       │ Structured Data │
                       └─────────────────┘
                                │
              ┌─────────────────┴─────────────────┐
              ▼                                   ▼
        OLTP / Transactions                 Analytics / OLAP
              │                                   │
       ┌──────┴──────┐                            ▼
       ▼             ▼                       Redshift
      RDS          Aurora
```

Recommended choices:

| Need                                                  | AWS service                         |
| ----------------------------------------------------- | ----------------------------------- |
| Standard relational application                       | **Amazon RDS**                      |
| Managed MySQL                                         | **Amazon RDS or Aurora MySQL**      |
| Managed PostgreSQL                                    | **Amazon RDS or Aurora PostgreSQL** |
| Managed Oracle                                        | **Amazon RDS**                      |
| Managed SQL Server                                    | **Amazon RDS**                      |
| Managed MariaDB                                       | **Amazon RDS**                      |
| Managed Db2                                           | **Amazon RDS**                      |
| High-performance MySQL/PostgreSQL-compatible database | **Amazon Aurora**                   |
| Analytics and large SQL scans                         | **Amazon Redshift**                 |

Rule of thumb:

**Start with RDS for normal relational apps. Use Aurora when the question emphasizes high performance, high availability, or cloud-native MySQL/PostgreSQL. Use Redshift for analytics.**

#### Semi-Structured and NoSQL Decision Tree

```text
                      ┌──────────────────────┐
                      │ Semi-Structured Data │
                      └──────────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        ▼                         ▼                         ▼
 Key-value / document?      MongoDB-compatible?          Cache?
 Massive serverless?              │                      Redis?
        │                         │                         │
        ▼                         ▼                         ▼
    DynamoDB                 DocumentDB               ElastiCache
```

Recommended choices:

| Need                                      | AWS service     |
| ----------------------------------------- | --------------- |
| Serverless NoSQL key-value/document       | **DynamoDB**    |
| Massive scale with low latency            | **DynamoDB**    |
| MongoDB-compatible document database      | **DocumentDB**  |
| Redis/Memcached cache                     | **ElastiCache** |
| Durable Redis-compatible primary database | **MemoryDB**    |
| Cassandra-compatible wide-column database | **Keyspaces**   |

Rule of thumb:

**DynamoDB is for AWS-native serverless NoSQL. DocumentDB is for MongoDB compatibility. ElastiCache is for cache. MemoryDB is for durable Redis-compatible primary storage.**

#### Specialized Data Decision Tree

```text
                      ┌──────────────────────┐
                      │ Specialized Workload │
                      └──────────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        ▼                         ▼                         ▼
 Graph relationships?       Time-series?              Immutable ledger?
        │                         │                         │
        ▼                         ▼                         ▼
    Neptune                  Timestream                  QLDB
```

Recommended choices:

| Need                             | AWS service    |
| -------------------------------- | -------------- |
| Graph traversal, nodes and edges | **Neptune**    |
| Time-series metrics and IoT data | **Timestream** |
| Immutable verifiable ledger      | **QLDB**       |

Rule of thumb:

**Graph = Neptune. Time-series = Timestream. Ledger = QLDB.**

#### Unstructured Data Decision Tree

```text
                       ┌─────────────────────┐
                       │  Unstructured Data  │
                       └─────────────────────┘
                                  │
                ┌─────────────────┴─────────────────┐
                ▼                                   ▼
          Files / blobs                       Query analytics?
                │                                   │
                ▼                                   ▼
               S3                         Athena / Redshift Spectrum
```

Recommended choices:

| Need                                       | AWS service           |
| ------------------------------------------ | --------------------- |
| Store images, videos, backups, logs, files | **Amazon S3**         |
| Store raw data lake files                  | **Amazon S3**         |
| Query data directly in S3 with SQL         | **Amazon Athena**     |
| Analyze S3 data with warehouse integration | **Redshift Spectrum** |

Rule of thumb:

**S3 stores raw objects. Redshift analyzes warehouse data. Athena queries files in S3 directly.**

### Hard Bulletproof AWS Rules

#### Rule 1: Analytics warehouse means Redshift

Choose **Redshift** when the question mentions:

* data warehouse
* analytics
* BI
* dashboard
* reporting
* aggregate queries
* OLAP
* columnar storage
* historical analysis
* large SQL scans

```text
Huge data + SQL analytics warehouse = Redshift
```

Example question:

> A company wants to run business intelligence reports over terabytes of sales data.

Answer:

```text
Amazon Redshift
```

#### Rule 2: Normal relational database means RDS

Choose **RDS** when the question mentions:

* MySQL
* PostgreSQL
* MariaDB
* Oracle
* SQL Server
* Db2
* relational database
* standard web application
* existing database migration
* transactions
* joins
* Multi-AZ

```text
Normal SQL app = RDS
```

Example question:

> A company wants to migrate an existing Oracle database to a managed AWS service.

Answer:

```text
Amazon RDS for Oracle
```

#### Rule 3: High-performance MySQL/PostgreSQL means Aurora

Choose **Aurora** when the question mentions:

* MySQL-compatible
* PostgreSQL-compatible
* high-performance relational database
* highly available relational database
* cloud-native relational database
* Aurora Global Database
* read scaling
* faster MySQL/PostgreSQL

```text
MySQL/PostgreSQL + high performance = Aurora
```

Example question:

> A company needs a highly available PostgreSQL-compatible database with better performance than standard PostgreSQL.

Answer:

```text
Amazon Aurora PostgreSQL
```

#### Rule 4: Serverless NoSQL key-value/document means DynamoDB

Choose **DynamoDB** when the question mentions:

* serverless NoSQL
* key-value database
* document database
* single-digit millisecond latency
* high throughput
* automatic scaling
* global tables
* shopping cart
* gaming
* user profile
* mobile backend
* unpredictable traffic

```text
Serverless NoSQL at massive scale = DynamoDB
```

Example question:

> A gaming application needs single-digit millisecond access to player state at massive scale.

Answer:

```text
Amazon DynamoDB
```

#### Rule 5: MongoDB-compatible document database means DocumentDB

Choose **DocumentDB** when the question mentions:

* MongoDB-compatible
* document database
* JSON documents
* flexible schema
* migrate MongoDB
* semi-structured application data

```text
MongoDB-compatible = DocumentDB
```

Example question:

> A company wants to migrate a MongoDB-compatible workload to a managed AWS service.

Answer:

```text
Amazon DocumentDB
```

#### Rule 6: Cache means ElastiCache

Choose **ElastiCache** when the question mentions:

* cache
* Redis
* Valkey
* Memcached
* session store
* leaderboard
* rate limiting
* temporary data
* reduce database load

```text
Redis / Memcached cache = ElastiCache
```

Example question:

> A web app needs to cache frequent database query results using Redis.

Answer:

```text
Amazon ElastiCache
```

#### Rule 7: Durable Redis primary database means MemoryDB

Choose **MemoryDB** when the question mentions:

* Redis-compatible primary database
* durable in-memory database
* ultra-low latency with durability
* persistent Redis-compatible workload

```text
Durable Redis-compatible database = MemoryDB
```

Example question:

> A microservice needs Redis-compatible low-latency access but cannot lose data because the database is the source of truth.

Answer:

```text
Amazon MemoryDB
```

#### Rule 8: Graph relationships mean Neptune

Choose **Neptune** when the question mentions:

* graph database
* nodes and edges
* relationship traversal
* social network
* fraud detection
* recommendations
* knowledge graph
* identity graph

```text
Graph = Neptune
```

Example question:

> A fraud detection system needs to identify relationships between accounts, devices, transactions, and identities.

Answer:

```text
Amazon Neptune
```

#### Rule 9: Time-series means Timestream

Choose **Timestream** when the question mentions:

* time-series
* IoT telemetry
* sensor readings
* metrics
* monitoring data
* time-window queries
* retention and rollups

```text
Time-series metrics = Timestream
```

Example question:

> An IoT system needs to store and query sensor readings over time.

Answer:

```text
Amazon Timestream
```

#### Rule 10: Cassandra-compatible means Keyspaces

Choose **Keyspaces** when the question mentions:

* Cassandra-compatible
* Apache Cassandra
* CQL
* wide-column database
* migrate Cassandra

```text
Cassandra-compatible = Keyspaces
```

Example question:

> A company wants to migrate an Apache Cassandra workload to a managed AWS service.

Answer:

```text
Amazon Keyspaces
```

#### Rule 11: Immutable ledger means QLDB

Choose **QLDB** when the question mentions:

* immutable ledger
* verifiable transaction history
* cryptographic verification
* complete audit trail
* append-only journal

```text
Immutable verifiable ledger = QLDB
```

Example question:

> A company needs a centralized ledger with a cryptographically verifiable history of every transaction.

Answer:

```text
Amazon QLDB
```

#### Rule 12: Files and blobs mean S3

Choose **S3** when the question mentions:

* files
* images
* videos
* backups
* raw logs
* static assets
* object storage
* data lake
* archive data

```text
Files and blobs = S3
```

Example question:

> A company needs to store user-uploaded images and videos durably.

Answer:

```text
Amazon S3
```

### Common AWS Exam Traps

| Question says                         | Do not pick             | Pick            |
| ------------------------------------- | ----------------------- | --------------- |
| Analyze huge data with SQL            | DynamoDB                | **Redshift**    |
| Store files, images, backups          | RDS                     | **S3**          |
| Standard MySQL/PostgreSQL app         | DynamoDB                | **RDS**         |
| High-performance MySQL/PostgreSQL     | Standard RDS by default | **Aurora**      |
| Serverless key-value at massive scale | RDS                     | **DynamoDB**    |
| MongoDB-compatible workload           | DynamoDB                | **DocumentDB**  |
| Redis cache                           | DynamoDB                | **ElastiCache** |
| Redis-compatible durable primary DB   | ElastiCache by default  | **MemoryDB**    |
| Graph relationship traversal          | RDS                     | **Neptune**     |
| Time-series sensor data               | Redshift by default     | **Timestream**  |
| Cassandra-compatible workload         | DynamoDB                | **Keyspaces**   |
| Immutable audit ledger                | RDS audit table         | **QLDB**        |

### Quick Comparison Table

| Service           | Database model             | Best for                                                          | Avoid when                                                  |
| ----------------- | -------------------------- | ----------------------------------------------------------------- | ----------------------------------------------------------- |
| **Amazon RDS**    | Relational SQL             | Standard MySQL, PostgreSQL, MariaDB, Oracle, SQL Server, Db2 apps | Need serverless NoSQL, graph, analytics warehouse           |
| **Amazon Aurora** | Relational SQL             | High-performance MySQL/PostgreSQL-compatible workloads            | Need Oracle/SQL Server or simple cheapest relational option |
| **DynamoDB**      | Key-value/document NoSQL   | Serverless NoSQL, massive scale, low latency                      | Need joins, ad hoc SQL, relational constraints              |
| **Redshift**      | Data warehouse             | Analytics, BI, reporting, large SQL scans                         | Need OLTP app database                                      |
| **ElastiCache**   | In-memory cache            | Redis/Valkey/Memcached caching, sessions, hot reads               | Need durable source of truth                                |
| **MemoryDB**      | In-memory durable database | Redis-compatible durable primary DB                               | Need only temporary cache                                   |
| **DocumentDB**    | Document database          | MongoDB-compatible JSON document workloads                        | Need key-value scale or analytics                           |
| **Neptune**       | Graph database             | Social graphs, fraud, recommendations, relationship traversal     | Need normal SQL or key-value lookup                         |
| **Timestream**    | Time-series database       | IoT telemetry, metrics, monitoring, time-window queries           | Need general-purpose app database                           |
| **Keyspaces**     | Wide-column NoSQL          | Cassandra-compatible workloads                                    | Need MongoDB, Redis, or relational SQL                      |
| **QLDB**          | Ledger database            | Immutable verifiable audit history                                | Need decentralized blockchain or normal OLTP                |
| **S3**            | Object storage             | Files, images, videos, backups, data lakes                        | Need transactions or row updates                            |

### Practical AWS Selection Checklist

Before choosing an AWS database, answer these questions:

Data shape:

* Is the data relational?
* Is it document-like?
* Is it key-value?
* Is it graph-like?
* Is it time-series?
* Is it an immutable ledger?
* Is it unstructured files or blobs?

Query pattern:

* Do I need joins?
* Do I need SQL?
* Do I need transactions?
* Do I mostly read/write by key?
* Do I need graph traversal?
* Do I need time-window queries?
* Do I need analytics over huge data?
* Do I need a cache?

Scale:

* Is this a normal app?
* Is this high-performance relational?
* Is this massive serverless NoSQL?
* Is traffic unpredictable?
* Is the workload read-heavy?
* Is the workload globally distributed?

Compatibility:

* Need MySQL/PostgreSQL high performance? **Aurora**
* Need normal MySQL/PostgreSQL/Oracle/SQL Server/MariaDB/Db2? **RDS**
* Need MongoDB compatibility? **DocumentDB**
* Need Cassandra compatibility? **Keyspaces**
* Need Redis/Memcached cache? **ElastiCache**
* Need durable Redis-compatible primary DB? **MemoryDB**

Cost and complexity:

* Is RDS enough?
* Are you choosing DynamoDB only because it sounds scalable?
* Are the access patterns known enough for DynamoDB?
* Is this really analytics, meaning Redshift?
* Is this just file storage, meaning S3?
* Is this just a cache, meaning ElastiCache?

[1]: https://docs.aws.amazon.com/whitepapers/latest/aws-overview/database.html?utm_source=chatgpt.com "AWS Database category iconDatabases - Overview of ..."
[2]: https://docs.aws.amazon.com/databases-on-aws-how-to-choose/?utm_source=chatgpt.com "Choosing an AWS database service"
[3]: https://trailhead.salesforce.com/content/learn/modules/core-aws-services/manage-databases-on-aws?utm_source=chatgpt.com "AWS Database Management Essentials - Trailhead"
