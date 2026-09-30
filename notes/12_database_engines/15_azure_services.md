# Choosing a Database on Microsoft Azure

Azure provides several managed relational, NoSQL, cache, and distributed data services. The correct service depends on the data model, access pattern, transaction requirements, compatibility needs, recovery objectives, and team expertise.

A cloud provider can operate infrastructure for you, but it cannot choose a good schema or query pattern.

Official references:

- [Azure data-store selection guide](https://learn.microsoft.com/en-us/azure/architecture/guide/technology-choices/data-stores-getting-started)
- [Azure SQL Database overview](https://learn.microsoft.com/en-us/azure/azure-sql/database/sql-database-paas-overview)
- [Azure Database for PostgreSQL](https://learn.microsoft.com/en-us/azure/postgresql/)
- [Azure Database for MySQL](https://learn.microsoft.com/en-us/azure/mysql/)
- [Azure Managed Redis](https://learn.microsoft.com/en-us/azure/redis/)

## Workload map

| Need | Candidate | What to investigate |
| --- | --- | --- |
| Managed SQL Server-compatible relational database | Azure SQL Database | compatibility, service tier, compute model, HA, networking |
| Lift-and-shift SQL Server with broader instance compatibility | Azure SQL Managed Instance | feature compatibility, VNet integration, migration path |
| Managed PostgreSQL | Azure Database for PostgreSQL Flexible Server | extensions, version, HA topology, storage, networking |
| Managed MySQL | Azure Database for MySQL Flexible Server | version, HA, storage, read scaling |
| Globally distributed NoSQL/document/key-value workloads | Azure Cosmos DB | API, partition key, consistency level, request-unit/capacity model |
| Redis-compatible in-memory data | Azure Managed Redis | tier, persistence, clustering, region availability |
| Managed Cassandra estate | Azure Managed Instance for Apache Cassandra | compatibility, topology, migration, operations |
| SQL Server with full VM-level control | SQL Server on Azure Virtual Machines | OS/database patch ownership, HA, backup design |
| Search | Azure AI Search | indexing, ranking, vector/text search, ingestion model |

Treat this table as a starting point, not an automatic decision.

## Azure SQL Database

Azure SQL Database is a fully managed database-as-a-service based on the SQL Server engine.

Microsoft manages much of the platform work:

- patching,
- backups,
- built-in availability,
- infrastructure maintenance,
- monitoring integrations.

The application team still owns:

- schema design,
- indexes,
- query tuning,
- transaction correctness,
- cost/capacity choices,
- data-retention policy.

### Architecture

```text
application
    │
    ▼
Azure SQL logical server endpoint
    │
    ▼
Azure SQL Database
    │
    ├── managed backups
    ├── managed HA
    └── monitoring
```

This is not the same as managing a normal SQL Server VM.

## SQL Database versus Managed Instance

A simplified comparison:

```text
cloud-native app
    │
    └──► Azure SQL Database

existing SQL Server app
with more instance-level dependencies
    │
    └──► SQL Managed Instance may fit better
```

Managed Instance is commonly considered for migrations that rely on more SQL Server instance-level behavior.

Do not assume perfect compatibility. Inventory:

- SQL Agent jobs,
- linked servers,
- CLR,
- server-level configuration,
- cross-database behavior,
- authentication,
- special extensions/features.

## Azure Database for PostgreSQL

Azure Database for PostgreSQL Flexible Server runs PostgreSQL as a managed service.

Typical fit:

- normal application OLTP,
- PostGIS applications,
- web backends,
- services wanting PostgreSQL without operating the VM/database stack.

### CLI example

With Azure CLI installed and authenticated:

```bash
az login
```

Create a resource group:

```bash
az group create   --name db-notes-rg   --location eastus
```

Create a development PostgreSQL server:

```bash
az postgres flexible-server create   --resource-group db-notes-rg   --name <globally-unique-server-name>   --location eastus   --admin-user dbadmin   --admin-password '<strong-password>'   --tier Burstable   --public-access <your-ip-address>
```

The exact SKU, PostgreSQL version, storage, HA, and network settings should be chosen deliberately.

For production, private networking and Microsoft Entra authentication may be preferable to broad public access.

## PostgreSQL high availability

A managed PostgreSQL deployment can use zone-redundant high availability where available.

Conceptually:

```text
availability zone 1         availability zone 2
┌──────────────────┐        ┌──────────────────┐
│ primary          │───────►│ standby          │
└──────────────────┘        └──────────────────┘
         │
         ▼
     application
```

HA improves service availability.

Backups/PITR are still needed for recoverability.

## Azure Database for MySQL

Azure Database for MySQL Flexible Server is the managed MySQL option.

Typical fit:

- MySQL-backed web applications,
- WordPress and common MySQL ecosystems,
- applications wanting managed backups/HA.

Before migration, validate:

- exact MySQL version,
- authentication plugins,
- storage engine behavior,
- extensions/plugins,
- replication assumptions,
- SQL modes.

"Managed MySQL" does not mean every self-hosted configuration transfers unchanged.

## Azure Cosmos DB

Azure Cosmos DB is a distributed NoSQL database service.

It is commonly considered when applications need:

- global distribution,
- low-latency document/key access,
- automatic partitioning,
- multiple consistency choices,
- high availability across regions.

A simplified model:

```text
application
   │
   ▼
Cosmos DB container
   │
   ▼
partition key
   │
   ├── logical partition A
   ├── logical partition B
   └── logical partition C
```

Partition-key choice is one of the most important decisions.

## Cosmos DB partition key

Suppose orders are stored with:

```text
partition key = customer_id
```

Queries for one customer are naturally scoped.

```text
customer 42 -> partition
             ├── order A
             ├── order B
             └── order C
```

A bad key can cause:

- hot partitions,
- skewed storage,
- expensive cross-partition queries,
- scalability limits.

Choose the key from expected traffic and query patterns, not just entity identity.

## Cosmos DB consistency

Distributed reads/writes involve consistency trade-offs.

Azure Cosmos DB provides configurable consistency models.

The application should explicitly decide:

- must every read see the latest committed write?
- can replicas lag?
- is session-level consistency enough?
- what latency/availability trade-off is acceptable?

Do not choose eventual or strong consistency by slogan.

Test the actual user-facing behavior.

## Request/capacity model

Cosmos DB capacity and cost are tied to operations and data characteristics.

Expensive patterns can include:

- cross-partition scans,
- poorly indexed large documents,
- high write volume,
- hot partition keys.

Model expected operations before production.

A database that scales automatically can also scale the bill automatically.

## Azure Managed Redis

Azure Managed Redis is Azure's current managed Redis offering for low-latency in-memory workloads.

Common uses:

- caching,
- sessions,
- rate limiting,
- leaderboards,
- transient state.

Architecture:

```text
application
    │
    ├──► Azure Managed Redis
    │         │
    │      cache hit
    │
    └──► durable database on miss
```

Do not make Redis the only copy of critical transactional data unless the persistence/durability model is deliberately designed for that role.

Azure Cache for Redis has a retirement path; new designs should check Microsoft's current migration guidance and Azure Managed Redis availability rather than assuming the older service is the long-term target.

## Azure Managed Instance for Apache Cassandra

Organizations with Cassandra workloads can evaluate Azure Managed Instance for Apache Cassandra.

The relevant questions are:

- driver/CQL compatibility,
- Cassandra version,
- topology,
- data migration,
- repair/backup responsibilities,
- network latency,
- operational boundary between Azure and the customer.

Managed Cassandra does not change the underlying need for query-first data modeling and good partition keys.

## Azure AI Search

Azure AI Search is not a relational database.

It is a search/indexing service for:

- text search,
- document retrieval,
- faceting,
- semantic/vector-oriented search workflows.

A common architecture:

```text
primary database / blob storage
            │
            ▼
      indexing pipeline
            │
            ▼
      Azure AI Search
            │
            ▼
         search API
```

The source database remains authoritative.

## SQL Server on Azure VMs

If an application needs full SQL Server and OS-level control, a VM can be appropriate.

You control more:

- SQL Server configuration,
- operating system,
- installed agents/software,
- storage layout,
- maintenance windows.

You also own more:

- patching,
- HA topology,
- VM management,
- monitoring,
- backup integration.

Use a VM when that control is required, not simply because it looks familiar.

## Managed database versus VM

```text
more managed                         more control
<---------------------------------------------------->
Azure SQL DB   Managed Instance   SQL Server VM
```

As control increases, operational responsibility usually increases.

## Networking

Production databases should normally use deliberate network boundaries.

Options include:

- private endpoints,
- VNet integration,
- firewall rules,
- restricted public endpoints.

A development quickstart using public access should not become a production architecture by accident.

## Identity

Azure integrates database services with Microsoft Entra ID.

Benefits can include:

- centralized identity,
- managed identities,
- reduced static-password use,
- auditable role assignment.

Where supported, prefer workload identity/managed identity over storing administrator passwords in application configuration.

## Secrets

Do not put database credentials in:

- source code,
- Docker images,
- public CI variables,
- repository files.

Use:

- Azure Key Vault,
- managed identity,
- protected deployment secrets.

Rotate credentials and test rotation.

## Encryption

Azure managed services generally provide encryption capabilities at rest and in transit, but application requirements may include:

- customer-managed keys,
- key rotation,
- field-level encryption,
- compliance boundaries.

Understand which layer owns the encryption key and where decryption occurs.

## Backups

A managed service usually automates backup creation.

You still need to define:

- retention,
- point-in-time recovery window,
- geo-redundancy if required,
- restore testing,
- RPO,
- RTO.

```text
backup exists
    !=
restore has been tested
```

## High availability versus disaster recovery

HA protects against local component failures.

DR protects against larger failures.

```text
HA:
zone / node failure
      │
      ▼
local failover

DR:
region or account-level event
      │
      ▼
separate recovery strategy
```

Do not treat one as the other.

## Cost dimensions

Managed database cost can include:

- compute,
- storage,
- backup storage,
- provisioned throughput,
- I/O,
- replicas,
- cross-region replication,
- network egress,
- reserved capacity.

A technically correct architecture can still be economically wrong.

Benchmark and estimate bills before scaling.

## Choosing by workload

### Conventional transactional application

Start with:

- Azure SQL Database,
- Azure Database for PostgreSQL,
- Azure Database for MySQL.

Choose based on application compatibility and team expertise.

### Existing SQL Server enterprise application

Evaluate:

- Azure SQL Managed Instance,
- SQL Server on Azure VM.

### Global NoSQL application

Evaluate:

- Cosmos DB.

### Cache/session/rate limit

Evaluate:

- Azure Managed Redis.

### Search

Evaluate:

- Azure AI Search.

### Existing Cassandra estate

Evaluate:

- Azure Managed Instance for Apache Cassandra.

## Example application stack

A realistic Azure application might use:

```text
ASP.NET API
    │
    ├──► Azure SQL Database
    │       transactional truth
    │
    ├──► Azure Managed Redis
    │       cache/session
    │
    ├──► Azure AI Search
    │       product search
    │
    └──► Blob Storage
            files
```

Using several data stores is justified only when each solves a clear workload.

## Multi-region design

Before enabling multi-region features, answer:

1. Where are users?
2. Where are writes performed?
3. What consistency is required?
4. What happens during failover?
5. Can two regions write simultaneously?
6. How is conflict resolution handled?
7. What is cross-region network cost?
8. What is the tested recovery procedure?

A global checkbox does not replace distributed-system design.

## Migration strategy

For an existing database:

```text
inventory dependencies
        │
        ▼
choose target service
        │
        ▼
compatibility testing
        │
        ▼
schema + data migration
        │
        ▼
replication / sync
        │
        ▼
cutover rehearsal
        │
        ▼
production cutover
```

Do not discover unsupported extensions or authentication assumptions during cutover.

## Observability

Monitor both application and database:

- query latency,
- connection count,
- CPU,
- storage,
- IOPS,
- lock waits,
- deadlocks,
- replication lag,
- cache hit ratio,
- request-unit/capacity consumption,
- backup success,
- failover events.

Use Azure Monitor integration plus engine-native query diagnostics.

## Common mistakes

### Choosing a service from one keyword

"Global" does not automatically mean Cosmos DB.

"SQL Server" does not automatically mean Managed Instance.

### Leaving public access wide open

Development defaults should be tightened before production.

### Ignoring compatibility

Managed PostgreSQL/MySQL/SQL Server services have platform-specific limits.

### Treating managed as maintenance-free

Schema, queries, incidents, and capacity still belong to the team.

### No restore tests

Automated backups are only useful if recovery works.

### Adding specialized databases too early

One relational database can support many applications for a long time.

## Practical selection sequence

1. Classify the workload: OLTP, distributed NoSQL, cache, search, analytics.
2. Identify mandatory engine/API compatibility.
3. List transaction and consistency requirements.
4. Estimate data size, growth, I/O, and latency.
5. Decide region/zone topology.
6. Design private networking and identity.
7. Define RPO/RTO.
8. Benchmark a representative workload.
9. Estimate total monthly cost.
10. Test backup and failover before production.

## Related notes

- [SQL Server](09_sql_server.md)
- [PostgreSQL](03_postgresql.md)
- [MySQL](02_mysql.md)
- [Redis](10_redis.md)
- [Cassandra](11_cassandra.md)
- [AWS database services](06_aws_services.md)
- [Google Cloud database services](08_gcp_services.md)
- [Choosing a database](07_choosing_database.md)
