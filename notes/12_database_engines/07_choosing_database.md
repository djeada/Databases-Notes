## Choosing Database

Choosing the right database can significantly influence your project's success. It requires careful evaluation of factors such as the data model, performance requirements, scalability, availability, and cost. Understanding your specific use case and its limitations helps ensure that your choice supports both immediate needs and future growth.

### Data Models

Each model handles specific workloads and data shapes, so understanding their strengths helps you make informed architectural decisions.

*Choose the model that matches the **shape of your data** and the **way it will be queried**—the engine comes later.*

#### Relational (Row-Store SQL)

Relational databases structure data into tables with fixed schemas, enforcing strong consistency and rich relational integrity through ACID transactions.

Structured rows, strong consistency, rich joins.

| Best for                                       | Typical engines               | Key traits                                  |
| ---------------------------------------------- | ----------------------------- | ------------------------------------------- |
| Financial ledgers, inventory, order processing | PostgreSQL, MySQL, SQL Server | ACID, referential integrity, mature tooling |

```
+----+----------+----------+
| id | customer | balance  |
+----+----------+----------+
|  1 | Omar     |  1 250.00|
|  2 | Layla    |    93.70 |
+----+----------+----------+
```

#### Document & Key-Value (NoSQL)

Document and key-value stores offer flexible schema designs, storing JSON-like documents or simple key-value pairs for scalable and agile development.

Flexible JSON blobs or simple keys, line-out scalability.

| Best for                                 | Typical engines              | Key traits                                                          |
| ---------------------------------------- | ---------------------------- | ------------------------------------------------------------------- |
| Content feeds, user profiles, catalogues | MongoDB, DynamoDB, Couchbase | Schema-optional, sharding built-in, eventual or tunable consistency |

```json
{
  "user": "Omar",
  "posts": [
    {"id": 1, "text": "Hello"},
    {"id": 2, "text": "World"}
  ]
}
```

#### Time-Series

Time-series databases are optimized for storing and querying time-stamped or sequential data, enabling efficient analysis of trends and temporal patterns.

Append-only metrics indexed by timestamp.

| Best for                                    | Typical engines                          | Key traits                                 |
| ------------------------------------------- | ---------------------------------------- | ------------------------------------------ |
| IoT telemetry, server metrics, market ticks | TimescaleDB, InfluxDB, Amazon Timestream | High ingest rate, roll-ups, window queries |

```
  value
20 ┤                              *
18 ┤                         *
16 ┤                    *
14 ┤               *
12 ┤          *
10 ┤     *
 8 ┤ *
 0 ┼────────────────────────── time
```

#### Graph

Graph databases represent data as nodes and edges, enabling fast traversals and complex relationship queries for connected data scenarios.

Nodes and edges with millisecond traversals.

| Best for                                    | Typical engines                 | Key traits                                           |
| ------------------------------------------- | ------------------------------- | ---------------------------------------------------- |
| Social graphs, fraud rings, recommendations | Neo4j, Amazon Neptune, ArangoDB | Index-free adjacency, path finding, pattern matching |

```
(Omar)───knows───(Layla)
  │ ▲              │
  │ └──knows────┐  │
  ▼             ▼  ▼
(Zayn)       (Noura)
```

#### In-Memory / Cache

In-memory and caching systems load data directly into RAM, delivering sub-millisecond access times for high-performance and transient workloads.

Entire dataset—or the hot subset—in RAM.

| Best for                                                  | Typical engines  | Key traits                                        |
| --------------------------------------------------------- | ---------------- | ------------------------------------------------- |
| Session state, leaderboard counters, low-latency look-ups | Redis, Memcached | µs read/write, TTL eviction, optional persistence |

```
Client → [Redis] → (TTL 60 s) → Primary DB
```

### Scalability

Scalability involves deciding between horizontal scaling (adding nodes) or vertical scaling (enhancing existing nodes). Managed services often offer auto-scaling to adjust capacity dynamically based on demand, supporting seamless growth without manual intervention.

#### Scale-Up (Vertical)

Vertical scaling, or scaling up, increases the capacity of a single node by adding more CPU, RAM, or IOPS, simplifying operations at the expense of hitting hardware limits.

| Best for                    | How it scales                       | Trade-offs                                                  |
| --------------------------- | ----------------------------------- | ----------------------------------------------------------- |
| Early MVPs, small OLTP apps | Add CPU / RAM / IOPS to **one** box | Simpler ops, but hard ceiling and cost curve is exponential |

```
+------------+
| 4 vCPU, 8G |
+------------+
      │   upgrade
      ▼
+------------+
| 32 vCPU,   |
| 256 G RAM  |
+------------+
```

#### Read Replication

Read replication distributes query load by creating copies of the primary database, improving read throughput while maintaining a single write master.

| Best for                         | How it scales                           | Trade-offs                                     |
| -------------------------------- | --------------------------------------- | ---------------------------------------------- |
| Read-heavy workloads, dashboards | Fans out read traffic to **N** replicas | Write master can still bottleneck; replica lag |

```
Clients
  │
  ├─► Replica 1  (SELECT)
  ├─► Replica 2  (SELECT)
  └─► Primary    (RW)
```

#### Sharding / Partitioning

Sharding splits data across multiple nodes based on key ranges or hash functions, enabling vast datasets to be partitioned for parallel processing.

| Best for                          | How it scales                                | Trade-offs                            |
| --------------------------------- | -------------------------------------------- | ------------------------------------- |
| Large OLTP sets, multitenant SaaS | Split data by key range or hash across nodes | Cross-shard joins/txns become complex |

```
Shard Key = user_id % 3
┌────────────┬────────────┬────────────┐
│  Shard 0   │  Shard 1   │  Shard 2   │
│ users 0,3… │ users 1,4… │ users 2,5… │
└────────────┴────────────┴────────────┘
```

#### Geo-Distributed / Active-Active

Geo-distributed active-active configurations place writable nodes across regions to reduce latency and enhance resilience, requiring careful consensus and CAP trade-offs.

| Best for                      | How it scales                                               | Trade-offs                                      |
| ----------------------------- | ----------------------------------------------------------- | ----------------------------------------------- |
| Low-latency global apps, BCDR | Writes land in nearest region; consensus syncs across sites | Network partitions → CAP decisions; higher cost |

```
╭── us-east ──╮        ╭── eu-west ─╮
│  RW node    │◀──────▶│  RW node   │
╰─────────────╯        ╰────────────╯
```

#### Serverless / Elastic Autoscaling

Serverless and elastic autoscaling platforms automatically adjust compute resources in response to traffic spikes, offering rapid scaling at the cost of cold start delays.

| Best for                     | How it scales                       | Trade-offs                             |
| ---------------------------- | ----------------------------------- | -------------------------------------- |
| Spiky, unpredictable traffic | Capacity grows & shrinks in seconds | Cold starts, price premium per request |

```
Load
  │
  ├──── low ──► 1 container
  └──── burst ► 50 containers
```

#### Dedicated Cache Layer

Adding a dedicated caching layer offloads frequent reads to in-memory stores, accelerating data access but introducing extra hops and eviction complexities.

| Best for                              | How it scales                                       | Trade-offs                            |
| ------------------------------------- | --------------------------------------------------- | ------------------------------------- |
| Hot-read amplification, session state | Offload reads to in-memory tier; add nodes linearly | Extra hop, eviction strategy required |

```
Client → Redis Cluster → Primary DB
          (1 ms)          (10 ms)
```

### Availability and Reliability

Maintaining uptime and reliability requires features like Multi-AZ deployments, read replicas, and robust backup and recovery options. Managed services with built-in failover capabilities can ensure your database remains accessible during hardware failures or other disruptions.

> Resiliency is architecture, not luck—choose a pattern that meets your SLA and your budget.*

#### Single-Node + Local Backup

Local backups provide a basic level of protection by dumping data to the same infrastructure, suitable for non-critical environments with relaxed recovery objectives.

| Best for                    | How it protects                  | Trade-offs                                         |
| --------------------------- | -------------------------------- | -------------------------------------------------- |
| Dev, POCs, throw-away demos | Nightly dump to same data center | RTO hours, RPO ≤ 24 h; hardware failure = downtime |

```
App ──► DB │──► local backup.gz
           │
      same rack
```

#### Synchronous Failover (Same Zone)

Synchronous failover replicates data in real time within the same availability zone, providing fast recovery but remaining vulnerable to zone-level outages.

| Best for                             | How it protects                                  | Trade-offs                                    |
| ------------------------------------ | ------------------------------------------------ | --------------------------------------------- |
| Small prod apps, cost-sensitive OLTP | Sync replica in same AZ; auto-promote on failure | AZ outage brings both down; write latency ↑ • |

```
Primary  ──► Sync Replica
   │ 1-RTT write ack  ▲
   └──── health check─┘
```

#### Cross-Zone Async Replication

Cross-zone asynchronous replication ships updates to a standby in another zone, balancing recovery speed with geographic fault tolerance at the cost of potential data lag.

| Best for                       | How it protects                          | Trade-offs                                                         |
| ------------------------------ | ---------------------------------------- | ------------------------------------------------------------------ |
| Standard web & mobile backends | Replica in different AZ; failover script | RPO seconds-minutes (async); split-brain risk if promote too early |

```
AZ-A (RW)  ───async──►  AZ-B (Stand-by)
```

#### Multi-Region Active-Passive (Warm Stand-by)

Warm stand-by setups continuously ship logs to a remote region, enabling fast DNS-based failover while controlling costs compared to fully active designs.

| Best for                       | How it protects                                        | Trade-offs                                                      |
| ------------------------------ | ------------------------------------------------------ | --------------------------------------------------------------- |
| Compliance-driven, 99.95 % SLA | Continuous log shipping to remote region; DNS cut-over | RTO 1-15 min; extra 50–100 % cost; app tier must also fail over |

```
us-east-1  ──logs──►  eu-west-1
 RW                Warm Stand-by
```

#### Multi-Region Active-Active (Consensus / Global Txn)

Global active-active architectures accept writes in all regions, coordinating via consensus protocols to maintain consistency across geographies at scale.

| Best for                             | How it protects                                      | Trade-offs                                                                 |
| ------------------------------------ | ---------------------------------------------------- | -------------------------------------------------------------------------- |
| 24×7 global products, <100 ms writes | All regions accept writes; paxos/raft ensures quorum | Higher write latency (N/2+1), complex conflict resolution, premium pricing |

```
╭─us-east──╮  ↔ Paxos ↔  ╭─eu-west──╮
│  RW node │             │  RW node │
╰──────────╯             ╰──────────╯
          ↕
        ap-southeast
```

#### Periodic Immutable Backups + Point-in-Time Restore

Immutable backups combined with WAL-based point-in-time restore protect against data corruption and human error by ensuring snapshots cannot be altered.

| Best for                   | How it protects                         | Trade-offs                          |
| -------------------------- | --------------------------------------- | ----------------------------------- |
| Ransomware, operator error | Snapshots to object store; PITR via WAL | No live HA; downtime during restore |

```
DB WAL ► S3 Glacier (immutability)
```

#### Chaos & Observability Layer

Integrating chaos testing and observability into your stack validates resilience by proactively injecting failures and monitoring key signals against SLOs.

| Best for              | How it protects                                                 | Trade-offs                            |
| --------------------- | --------------------------------------------------------------- | ------------------------------------- |
| Enforced SLOs, audits | Fault-injection + golden signals (latency, error %, saturation) | Requires culture & tooling investment |

```
[Chaos Monkey] → inject fault
      │
      ▼
Alerts (SLO burn) ─► PagerDuty
```

### Decision-Making Trees

**Quick-start:** decide which branch to follow *before* you think about engines or vendors.
Answer the questions in this one diagram—then jump straight to the matching decision tree.

```
#
                       ┌────────────────────────────────────────┐
                       │   What does your application store?    │
                       └────────────────────────────────────────┘
                                       │
                ┌──────────────────────┼─────────────────────────┐
                ▼                       ▼                        ▼
   Rows / columns fit a rigid   JSON, XML, key-value with    Raw binaries, logs,
        schema that rarely        evolving fields and       audio-video, images,
          changes? (Yes)          partial structure? (Yes)      sensor dumps?
                │                       │                         │
                ▼                       ▼                         ▼
        ┌──────────────┐        ┌──────────────────┐       ┌─────────────────┐
        │  STRUCTURED  │        │ SEMI-STRUCTURED  │       │  UNSTRUCTURED   │
        └──────────────┘        └──────────────────┘       └─────────────────┘
                │                       │                         │
     → Go to the **Structured**   → Go to the **Semi-**     → Go to the **Un-**
          decision tree                decision tree              decision tree
```

*Rule of thumb*: if even **10 %** of your data can’t live in a fixed table, treat the set as semi-structured; if you mostly store files or streams, treat it as unstructured.

####  Structured Data

```
#
                       ┌───────────────┐
                       │ Structured    │
                       └───────────────┘
                               │
             ┌─────────────────┼─────────────────┐
             ▼                                   ▼
         OLTP / ACID                    Analytics / OLAP
   (high-QPS, row lookups)           (large scans, aggregates)
             │                                   │
 ┌───────────┴───────────┐             ┌─────────┴─────────┐
 ▼                       ▼             ▼                   ▼
< 1 TB single node   > 1 TB or global   Column-store    Serverless
 MySQL, Postgres     NewSQL (TiDB,      (Snowflake,     column-store
 + read replicas     CockroachDB,       Redshift,       (BigQuery,
 or partitions       Spanner)           ClickHouse)     Athena)
```

*Rule of thumb*: start simple (row-store) until analytics queries dominate or data tops \~1 TB.

#### Unstructured Data

```
#
                       ┌─────────────────────────────┐
                       │       Unstructured          │
                       └─────────────────────────────┘
                                      │
                ┌─────────────────────┼─────────────────────┐
                ▼                     ▼                     ▼
        POSIX‐like FS?         Huge blobs?          µs-latency blocks?
            │ Yes                  │ Yes                      │ Yes
            ▼                      ▼                          ▼
   Distributed File FS      Object Store (S3, GCS)      Block Store (EBS)
            │ No                   │ No                       │ No
            └─▶ Need global CDN? ─▶ CDN ─▶ otherwise FS / OS
```

*Translation*: choose by **access semantics** (files vs. objects vs. blocks) and **latency vs. size** constraints.

#### Semi-Structured Data

```
                      ┌────────────────────────┐
                      │   Semi-Structured      │
                      └────────────────────────┘
                                   │
          ┌────────────────────────┼─────────────────────────┐
          ▼                        ▼                         ▼
      Document-style?        Simple KV / cache?        Graph relations?
          │ Yes                    │ Yes                     │ Yes
          ▼                        ▼                         ▼
   Document DB (Mongo,       In-Memory KV (Redis)       Graph DB (Neo4j,
   Couchbase) 10 GB-10 TB     µs latency, TTL keys       Neptune)
          │ No                     │ No                      │ No
          └─────────────┬──────────┴───────────┬────────────┘
                        ▼                      ▼
               Wide/sparse cols?        Full-text search?
                    │ Yes                     │ Yes
                    ▼                        ▼
         Wide-Column (Cassandra)     Search DB (Elastic,
             Time-series OK           OpenSearch)
                    │ No
                    ▼
           Time-ordered writes?
                    │ Yes
                    ▼
        Time-Series DB (InfluxDB,
             TimescaleDB)
```

*Shortcut*: pick by **dominant access pattern**—JSON blobs, key-value, graph traversals, etc.

#### How to Use These Trees

1. **Locate your data shape** (structured, semi-, unstructured).
2. **Walk the branch** that matches latency, size, and query style.
3. **Prototype quickly**—run real workloads for a day.
4. **Re-check every 6-12 months** as traffic and cloud services evolve.

Stick to the diagram path and you’ll land on a database that fits today without painting yourself into a corner tomorrow.
