## Choosing a Database on Google Cloud

Choosing the right Google Cloud database can significantly influence your project’s reliability, performance, cost, scalability, and operational complexity. In GCP exams, database questions usually describe a workload and expect you to match it to the service with the best fit.

A practical way to start is to ask:

* Is this application traffic or analytics traffic?
* Is the data relational, document-like, key-value, time-series, or file-based?
* Do you need SQL?
* Do you need transactions?
* Do you need global scale?
* Do you need low-latency reads and writes?
* Do you need realtime mobile/web synchronization?
* Do you need to analyze huge datasets?
* Do you need a cache rather than a primary database?

A useful rule of thumb:

**Choose the GCP database based on workload first. Choose the product name second.**

The most important exam distinction is:

```text
OLTP = application database
OLAP = analytics database
```

**OLTP** means user-facing applications doing small reads, writes, updates, and transactions.

**OLAP** means analytics, dashboards, reports, aggregations, and large scans over big datasets.

### GCP Database Options

#### Cloud SQL

Cloud SQL is Google Cloud’s managed relational database service for **MySQL, PostgreSQL, and SQL Server**.

It is the safest default choice when the question describes a normal relational application.

**Best for:** traditional applications, structured data, SQL queries, transactions, existing MySQL/PostgreSQL/SQL Server workloads, lift-and-shift migrations.

| Best for                                                                           | GCP service   | Key traits                                                                          |
| ---------------------------------------------------------------------------------- | ------------- | ----------------------------------------------------------------------------------- |
| Standard relational apps, orders, users, inventory, CMS, ERP, small-to-medium SaaS | **Cloud SQL** | Managed MySQL/PostgreSQL/SQL Server, SQL, joins, transactions, backups, replication |

Example:

```text
+----+----------+----------+
| id | customer | balance  |
+----+----------+----------+
|  1 | Omar     | 1250.00  |
|  2 | Layla    |   93.70  |
+----+----------+----------+
```

Use **Cloud SQL** when the question says:

* managed MySQL
* managed PostgreSQL
* managed SQL Server
* relational database
* SQL transactions
* lift and shift
* existing app migration
* standard web application

Avoid Cloud SQL when the question requires:

* global horizontal scale,
* very high write throughput,
* petabyte-scale analytics,
* low-latency NoSQL at massive scale.

Exam rule:

**Normal relational database on GCP = Cloud SQL.**

#### AlloyDB

AlloyDB is Google Cloud’s high-performance, PostgreSQL-compatible database.

It is usually chosen when the question specifically emphasizes **PostgreSQL compatibility plus higher performance, availability, or enterprise-grade features**.

**Best for:** demanding PostgreSQL workloads, enterprise apps, high-performance transactional systems, PostgreSQL modernization.

| Best for                                         | GCP service | Key traits                                                                    |
| ------------------------------------------------ | ----------- | ----------------------------------------------------------------------------- |
| High-performance PostgreSQL-compatible workloads | **AlloyDB** | PostgreSQL-compatible, managed, high performance, strong availability options |

Use **AlloyDB** when the question says:

* PostgreSQL-compatible
* improve PostgreSQL performance
* modernize PostgreSQL
* enterprise PostgreSQL workload
* high-performance relational database

Avoid AlloyDB when the question requires:

* MySQL or SQL Server compatibility,
* global strongly consistent relational scale,
* analytics over petabytes.

Exam rule:

**PostgreSQL-compatible but more powerful/enterprise-focused = AlloyDB.**

#### Cloud Spanner

Cloud Spanner is Google Cloud’s globally scalable relational database with strong consistency.

It is the answer when the question combines:

```text
relational database + global scale + strong consistency
```

**Best for:** global financial systems, globally distributed SaaS, high-scale relational apps, mission-critical systems needing strong consistency across regions.

| Best for                                                    | GCP service       | Key traits                                                                       |
| ----------------------------------------------------------- | ----------------- | -------------------------------------------------------------------------------- |
| Global relational applications requiring strong consistency | **Cloud Spanner** | SQL, relational model, horizontal scale, strong consistency, global distribution |

Example:

```text
Users in US ─┐
             ├──► Cloud Spanner global database
Users in EU ─┤
             │
Users in APAC┘
```

Use **Cloud Spanner** when the question says:

* globally distributed relational database
* strong consistency
* horizontal scaling
* high availability
* global transactions
* multi-region relational database
* mission-critical application
* relational database at massive scale

Avoid Spanner when:

* a simple regional relational database is enough,
* the workload is analytics,
* the workload is simple key-value or document access,
* cost and simplicity matter more than global scale.

Exam rule:

**Relational + global scale + strong consistency = Spanner.**

#### Firestore

Firestore is a serverless NoSQL document database. It is commonly used for web and mobile apps.

It stores data as documents and collections rather than relational tables.

**Best for:** mobile apps, web apps, realtime sync, offline support, user profiles, app state, flexible JSON-like documents.

| Best for                                    | GCP service   | Key traits                                                                             |
| ------------------------------------------- | ------------- | -------------------------------------------------------------------------------------- |
| Mobile/web apps with flexible document data | **Firestore** | Serverless, NoSQL document database, realtime updates, offline sync, automatic scaling |

Example:

```json
{
  "user": "Omar",
  "city": "Berlin",
  "cart": [
    { "product": "Book", "quantity": 1 },
    { "product": "Mouse", "quantity": 2 }
  ]
}
```

Use **Firestore** when the question says:

* mobile application
* web application
* realtime updates
* offline synchronization
* serverless NoSQL
* document database
* JSON-like data
* flexible schema

Avoid Firestore when:

* complex joins are required,
* heavy relational transactions are required,
* petabyte-scale analytics are required,
* extremely high time-series write throughput is required.

Exam rule:

**Mobile/web app + realtime/offline document database = Firestore.**

#### Bigtable

Bigtable is Google Cloud’s massively scalable NoSQL wide-column database.

It is designed for very high throughput and low-latency access at huge scale.

**Best for:** time-series data, IoT telemetry, clickstream data, monitoring data, financial tick data, personalization, ad tech, high-volume event data.

| Best for                                                  | GCP service  | Key traits                                                                     |
| --------------------------------------------------------- | ------------ | ------------------------------------------------------------------------------ |
| Huge NoSQL workloads with low latency and high throughput | **Bigtable** | Wide-column/key-value style, massive scale, low latency, high write throughput |

Example:

```text
Row key: device_123#2026-05-03T10:00:00

temperature: 22.4
humidity: 41
battery: 87
```

Use **Bigtable** when the question says:

* IoT
* telemetry
* time-series
* clickstream
* low-latency reads/writes
* high write throughput
* billions of rows
* petabytes
* HBase-compatible
* sparse data
* wide-column database

Avoid Bigtable when:

* you need joins,
* you need complex SQL,
* you need ad hoc analytics,
* you need relational constraints,
* you need multi-row relational transactions.

Exam rule:

**Massive low-latency NoSQL/time-series/event data = Bigtable.**

#### BigQuery

BigQuery is Google Cloud’s serverless data warehouse for analytics.

It is not a normal application database. It is for analyzing large datasets using SQL.

**Best for:** analytics, dashboards, reporting, business intelligence, data warehouse, machine learning over large datasets, ad hoc SQL queries, petabyte-scale scans.

| Best for                                   | GCP service  | Key traits                                                                |
| ------------------------------------------ | ------------ | ------------------------------------------------------------------------- |
| Analytics and reporting over huge datasets | **BigQuery** | Serverless data warehouse, SQL analytics, large scans, BI, ML integration |

Example:

```sql
SELECT
  country,
  COUNT(*) AS purchases,
  SUM(amount) AS revenue
FROM sales
GROUP BY country;
```

Use **BigQuery** when the question says:

* analytics
* data warehouse
* BI
* dashboard
* reporting
* aggregate queries
* petabyte scale
* ad hoc SQL
* analyze logs
* historical analysis
* Looker/Data Studio reporting

Avoid BigQuery when:

* the application needs millisecond transactional updates,
* users are constantly updating individual rows,
* you need OLTP behavior,
* you need a primary backend database for an app.

Exam rule:

**Analytics + SQL + huge data = BigQuery.**

#### Memorystore

Memorystore is Google Cloud’s managed in-memory cache service for Redis and Memcached.

It is usually not the primary database. It is a performance layer.

**Best for:** caching, sessions, leaderboards, rate limiting, queues, counters, temporary data, hot reads.

| Best for                                      | GCP service     | Key traits                                             |
| --------------------------------------------- | --------------- | ------------------------------------------------------ |
| In-memory caching and very low-latency access | **Memorystore** | Managed Redis/Memcached, low latency, TTL, cache layer |

Example:

```text
Client → Memorystore cache → Primary database
             │
             └── TTL: 60 seconds
```

Use **Memorystore** when the question says:

* cache
* Redis
* Memcached
* session store
* leaderboard
* rate limiting
* temporary data
* reduce database load
* low-latency repeated reads

Avoid Memorystore when:

* you need durable primary storage,
* you need long-term analytics,
* you need relational transactions.

Exam rule:

**Cache / Redis / Memcached = Memorystore.**

#### Cloud Storage

Cloud Storage is not a database, but it appears in database-style exam questions.

It is object storage for files, blobs, backups, images, videos, logs, and static assets.

**Best for:** unstructured data, images, videos, backups, exports, data lake storage, raw log files, static website files.

| Best for                                                 | GCP service       | Key traits                                               |
| -------------------------------------------------------- | ----------------- | -------------------------------------------------------- |
| Files, images, videos, backups, blobs, data lake objects | **Cloud Storage** | Object storage, durable, scalable, cheap for large files |

Example:

```text
/user-uploads/profile-picture.png
/backups/db-backup-2026-05-03.sql
/logs/app/server-log.json
```

Use **Cloud Storage** when the question says:

* store files
* store images
* store videos
* store backups
* store large objects
* raw logs
* data lake
* static assets

Avoid Cloud Storage when:

* you need SQL queries as the primary access pattern,
* you need transactions,
* you need low-latency row updates.

Exam rule:

**Files/blobs/backups/images/videos = Cloud Storage.**

### Decision-Making Rules for GCP Exams

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
    Cloud SQL / AlloyDB / Spanner /          BigQuery
    Firestore / Bigtable
```

Use this rule:

| Workload                       | Pick                                                |
| ------------------------------ | --------------------------------------------------- |
| Application reads/writes       | Cloud SQL, AlloyDB, Spanner, Firestore, or Bigtable |
| Analytics, reports, dashboards | BigQuery                                            |

Exam rule:

**If users are using the app, think OLTP. If analysts are querying data, think BigQuery.**

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
     ┌────────┼─────────┐                         ▼
     ▼        ▼         ▼                    BigQuery
 Cloud SQL  AlloyDB  Spanner
```

Recommended choices:

| Need                                               | GCP service   |
| -------------------------------------------------- | ------------- |
| Standard relational application                    | **Cloud SQL** |
| Managed MySQL                                      | **Cloud SQL** |
| Managed PostgreSQL                                 | **Cloud SQL** |
| Managed SQL Server                                 | **Cloud SQL** |
| High-performance PostgreSQL-compatible database    | **AlloyDB**   |
| Global relational database with strong consistency | **Spanner**   |
| Analytics and large SQL scans                      | **BigQuery**  |

Rule of thumb:

**Start with Cloud SQL for normal relational apps. Use Spanner only when the question clearly needs global scale or horizontal relational scaling. Use BigQuery for analytics.**

#### Semi-Structured and NoSQL Decision Tree

```text
                      ┌──────────────────────┐
                      │ Semi-Structured Data │
                      └──────────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        ▼                         ▼                         ▼
 Document-shaped?           Massive scale?              Cache?
 Mobile/web app?            Low latency?                Redis?
        │                         │                         │
        ▼                         ▼                         ▼
    Firestore                 Bigtable                Memorystore
```

Recommended choices:

| Need                              | GCP service     |
| --------------------------------- | --------------- |
| Mobile/web document database      | **Firestore**   |
| Realtime updates and offline sync | **Firestore**   |
| Flexible JSON-like documents      | **Firestore**   |
| Massive NoSQL writes              | **Bigtable**    |
| IoT/time-series/clickstream       | **Bigtable**    |
| Cache/session/Redis/Memcached     | **Memorystore** |

Rule of thumb:

**Firestore is for app documents. Bigtable is for massive low-latency NoSQL data. Memorystore is for cache.**

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
         Cloud Storage                       BigQuery over data
```

Recommended choices:

| Need                                       | GCP service       |
| ------------------------------------------ | ----------------- |
| Store images, videos, backups, logs, files | **Cloud Storage** |
| Store raw data lake files                  | **Cloud Storage** |
| Analyze large stored datasets              | **BigQuery**      |

Rule of thumb:

**Cloud Storage stores raw objects. BigQuery analyzes data.**

### Hard Bulletproof GCP Rules

### Rule 1: Analytics means BigQuery

Choose **BigQuery** when the question mentions:

* analytics
* data warehouse
* BI
* dashboard
* reporting
* aggregate queries
* ad hoc SQL
* petabytes
* historical analysis
* large scans

```text
Huge data + SQL analytics = BigQuery
```

Example question:

> A company wants to analyze several terabytes of sales data and build dashboards.

Answer:

```text
BigQuery
```

#### Rule 2: Normal relational database means Cloud SQL

Choose **Cloud SQL** when the question mentions:

* MySQL
* PostgreSQL
* SQL Server
* relational database
* standard web application
* existing database migration
* transactions
* joins
* traditional schema

```text
Normal SQL app = Cloud SQL
```

Example question:

> A company wants to migrate an existing MySQL application to a managed Google Cloud database.

Answer:

```text
Cloud SQL
```

#### Rule 3: PostgreSQL-compatible high performance means AlloyDB

Choose **AlloyDB** when the question mentions:

* PostgreSQL-compatible
* enterprise PostgreSQL
* high-performance PostgreSQL
* modernize PostgreSQL workload
* demanding transactional PostgreSQL app

```text
PostgreSQL-compatible + high performance = AlloyDB
```

Example question:

> A company wants to modernize a performance-sensitive PostgreSQL workload using a managed Google Cloud database.

Answer:

```text
AlloyDB
```

#### Rule 4: Global relational consistency means Spanner

Choose **Spanner** when the question mentions:

* global relational database
* strong consistency
* global transactions
* horizontal scaling
* mission-critical
* multi-region relational app
* high availability at global scale

```text
Relational + global + strongly consistent = Spanner
```

Example question:

> A financial application needs a relational database that can scale globally while maintaining strong consistency.

Answer:

```text
Cloud Spanner
```

#### Rule 5: Mobile/web realtime document database means Firestore

Choose **Firestore** when the question mentions:

* mobile app
* web app
* realtime sync
* offline support
* document database
* JSON-like documents
* serverless NoSQL
* flexible schema

```text
Mobile/web + realtime/offline documents = Firestore
```

Example question:

> A mobile app needs a serverless NoSQL database with offline synchronization.

Answer:

```text
Firestore
```

#### Rule 6: Massive time-series or telemetry means Bigtable

Choose **Bigtable** when the question mentions:

* IoT telemetry
* time-series data
* clickstream
* monitoring metrics
* financial tick data
* high write throughput
* low latency
* billions of rows
* petabytes
* HBase

```text
Massive low-latency NoSQL = Bigtable
```

Example question:

> An IoT system needs to ingest millions of sensor readings per second with low-latency access.

Answer:

```text
Bigtable
```

#### Rule 7: Cache means Memorystore

Choose **Memorystore** when the question mentions:

* cache
* Redis
* Memcached
* sessions
* leaderboard
* rate limiting
* temporary data
* reduce database load

```text
Redis / Memcached / cache = Memorystore
```

Example question:

> A web app needs to store session data with very low latency.

Answer:

```text
Memorystore
```

#### Rule 8: Files and blobs mean Cloud Storage

Choose **Cloud Storage** when the question mentions:

* files
* images
* videos
* backups
* raw logs
* object storage
* data lake
* static assets

```text
Files and blobs = Cloud Storage
```

Example question:

> A company needs to store user-uploaded images and videos.

Answer:

```text
Cloud Storage
```

### Common Exam Traps

| Question says                                      | Do not pick          | Pick              |
| -------------------------------------------------- | -------------------- | ----------------- |
| Analyze huge data with SQL                         | Bigtable             | **BigQuery**      |
| Store massive IoT telemetry with low latency       | BigQuery             | **Bigtable**      |
| Standard MySQL/PostgreSQL app                      | Spanner              | **Cloud SQL**     |
| Global relational database with strong consistency | Cloud SQL            | **Spanner**       |
| Mobile app with realtime offline sync              | Bigtable             | **Firestore**     |
| Cache session data                                 | Firestore            | **Memorystore**   |
| Store images and videos                            | Cloud SQL            | **Cloud Storage** |
| PostgreSQL-compatible high-performance managed DB  | Cloud SQL by default | **AlloyDB**       |

### Quick Comparison Table

| Service           | Database model                   | Best for                                         | Avoid when                                          |
| ----------------- | -------------------------------- | ------------------------------------------------ | --------------------------------------------------- |
| **Cloud SQL**     | Relational SQL                   | Standard MySQL/PostgreSQL/SQL Server apps        | Need global scale or massive analytics              |
| **AlloyDB**       | PostgreSQL-compatible relational | High-performance PostgreSQL workloads            | Need MySQL/SQL Server or global Spanner-style scale |
| **Spanner**       | Distributed relational SQL       | Global, strongly consistent relational apps      | Simple regional app is enough                       |
| **Firestore**     | Document NoSQL                   | Mobile/web apps, realtime sync, offline support  | Need joins or complex relational queries            |
| **Bigtable**      | Wide-column NoSQL                | IoT, telemetry, time-series, high throughput     | Need SQL analytics or joins                         |
| **BigQuery**      | Data warehouse                   | Analytics, dashboards, reporting, huge SQL scans | Need OLTP app database                              |
| **Memorystore**   | In-memory cache                  | Redis/Memcached, sessions, cache, rate limits    | Need durable primary storage                        |
| **Cloud Storage** | Object storage                   | Files, images, backups, blobs, data lake         | Need database transactions                          |

### Practical GCP Selection Checklist

Before choosing a GCP database, answer these questions:

Data shape:

* Is the data relational?
* Is it document-like?
* Is it time-series?
* Is it key-value?
* Is it unstructured files or blobs?

Query pattern:

* Do I need joins?
* Do I need transactions?
* Do I need SQL?
* Do I mostly read/write by key?
* Do I need aggregate analytics over huge data?
* Do I need realtime sync?

Scale:

* Is this a normal regional app?
* Is this global?
* Is the data measured in gigabytes, terabytes, or petabytes?
* Are writes extremely high volume?
* Are reads latency-sensitive?

Consistency:

* Do reads need the latest committed write?
* Is strong consistency required globally?
* Is eventual consistency acceptable?

Operations:

* Do I want a managed relational database?
* Do I need serverless?
* Do I need automatic scaling?
* Do I need Redis/Memcached compatibility?

Cost and complexity:

* Is a simple managed database enough?
* Am I adding Spanner or Bigtable only because they sound powerful?
* Would Cloud SQL solve the problem more simply?
* Is the workload truly analytics, meaning BigQuery?
