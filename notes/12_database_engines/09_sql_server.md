# Microsoft SQL Server

Microsoft SQL Server is a relational database engine widely used in enterprise applications, business systems, reporting, and Microsoft-centric environments. It supports transactional workloads, analytical features, mature administration tooling, and deep integration with the .NET and Azure ecosystems.

SQL Server is a conventional client/server database:

```text
applications / BI / admin tools
              │
        TDS network protocol
              │
              ▼
      ┌─────────────────┐
      │ SQL Server      │
      │ query processor │
      │ transaction log │
      │ buffer pool     │
      └────────┬────────┘
               │
        data + log files
```

## When SQL Server is used

Common scenarios include:

- ASP.NET and .NET application backends,
- ERP and line-of-business systems,
- enterprise reporting,
- Microsoft BI stacks,
- applications already using Active Directory / Microsoft Entra integration,
- organizations with existing SQL Server operational expertise.

SQL Server is especially attractive when application, identity, administration, and reporting tooling already live in the Microsoft ecosystem.

## Local Docker setup

Microsoft publishes SQL Server Linux container images. For current SQL Server 2025 documentation, see:

- [SQL Server Linux container quickstart](https://learn.microsoft.com/en-us/sql/linux/install-upgrade/quickstart-install-docker?view=sql-server-ver17)
- [Deploy and connect to SQL Server Linux containers](https://learn.microsoft.com/en-us/sql/linux/sql-server-linux-docker-container-deployment?view=sql-server-ver17)

A local development instance:

```bash
docker run   --name sqlserver-notes   --hostname sqlserver-notes   -e ACCEPT_EULA=Y   -e MSSQL_SA_PASSWORD='StrongPassword_123!'   -p 1433:1433   -d   mcr.microsoft.com/mssql/server:2025-latest
```

Check startup:

```bash
docker logs -f sqlserver-notes
```

The password must satisfy SQL Server's password policy.

For disposable learning environments this is convenient. Production containers need persistent storage, secrets management, backups, monitoring, resource limits, and a supported deployment configuration.

## Connect with sqlcmd

Current SQL Server Linux images use the newer tools path:

```text
/opt/mssql-tools18/bin/sqlcmd
```

Connect inside the container:

```bash
docker exec -it sqlserver-notes   /opt/mssql-tools18/bin/sqlcmd   -S localhost   -U sa   -P 'StrongPassword_123!'   -C
```

The `-C` flag trusts the development certificate. Do not treat certificate bypass as a production configuration.

At the prompt:

```sql
SELECT @@VERSION;
GO
```

## Create a database

```sql
CREATE DATABASE shop;
GO

USE shop;
GO
```

Create a table:

```sql
CREATE TABLE dbo.orders (
    order_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    created_at DATETIME2 NOT NULL
        CONSTRAINT df_orders_created_at DEFAULT SYSUTCDATETIME(),
    total_amount DECIMAL(12,2) NOT NULL
        CONSTRAINT ck_orders_total_amount CHECK (total_amount >= 0)
);
GO
```

Insert data:

```sql
INSERT INTO dbo.orders (customer_id, total_amount)
VALUES
    (101, 49.90),
    (205, 19.95),
    (101, 120.00);
GO
```

Query it:

```sql
SELECT
    customer_id,
    COUNT(*) AS orders,
    SUM(total_amount) AS revenue
FROM dbo.orders
GROUP BY customer_id
ORDER BY revenue DESC;
GO
```

## Existing repository console

This repository already contains a multiline SQL Server console:

[`scripts/sqlserver/sql_docker_console.py`](../../scripts/sqlserver/sql_docker_console.py)

It keeps one `sqlcmd` session alive between submitted scripts, which makes it useful for transaction, temporary-table, and session-state experiments.

From `scripts/`:

```bash
python3 -m pip install prompt-toolkit
python3 sqlserver/sql_docker_console.py
```

See [`scripts/README.md`](../../scripts/README.md) for usage.

## Schemas

SQL Server uses schemas as namespaces inside a database.

```text
database: shop
│
├── dbo.orders
├── dbo.customers
└── reporting.monthly_sales
```

Using explicit schema names is a good habit:

```sql
SELECT *
FROM dbo.orders;
```

Schemas help separate ownership and permissions without requiring a separate database for every logical module.

## Identity columns and sequences

An identity column commonly generates numeric keys:

```sql
order_id BIGINT IDENTITY(1,1)
```

SQL Server also supports sequences:

```sql
CREATE SEQUENCE dbo.order_number_seq
    AS BIGINT
    START WITH 100000
    INCREMENT BY 1;
GO
```

Sequences are useful when several tables or operations need values from one generator.

As with other database-generated identifiers, gaps can occur and should normally be treated as expected.

## Transactions

A normal explicit transaction:

```sql
BEGIN TRANSACTION;

UPDATE dbo.accounts
SET balance = balance - 100
WHERE account_id = 1;

UPDATE dbo.accounts
SET balance = balance + 100
WHERE account_id = 2;

COMMIT;
```

On failure:

```sql
ROLLBACK;
```

Use `TRY...CATCH` for robust stored transaction logic:

```sql
BEGIN TRY
    BEGIN TRANSACTION;

    -- related writes

    COMMIT;
END TRY
BEGIN CATCH
    IF XACT_STATE() <> 0
        ROLLBACK;

    THROW;
END CATCH;
GO
```

## Concurrency and isolation

SQL Server supports locking-based isolation and row-versioning options.

Important concepts include:

- shared and exclusive locks,
- lock escalation,
- deadlock detection,
- READ COMMITTED,
- SNAPSHOT isolation,
- READ COMMITTED SNAPSHOT,
- SERIALIZABLE.

A database configured with `READ_COMMITTED_SNAPSHOT` uses row versions for normal READ COMMITTED reads rather than taking shared locks for the entire read operation.

Check the database setting:

```sql
SELECT
    name,
    is_read_committed_snapshot_on,
    snapshot_isolation_state_desc
FROM sys.databases
WHERE name = DB_NAME();
GO
```

Isolation should be chosen around application correctness, not only throughput.

## Clustered and nonclustered indexes

A **clustered index** defines the main B-tree organization of table rows.

A **nonclustered index** is a separate index structure that points to rows through the clustering key or row locator.

Example:

```sql
CREATE INDEX ix_orders_customer_created
ON dbo.orders(customer_id, created_at DESC)
INCLUDE (total_amount);
GO
```

This index can support queries such as:

```sql
SELECT TOP (20)
    order_id,
    created_at,
    total_amount
FROM dbo.orders
WHERE customer_id = @customer_id
ORDER BY created_at DESC;
```

The `INCLUDE` columns can make the index cover the query without adding them to the search key.

## Execution plans

SQL Server has rich execution-plan tooling.

In SQL Server Management Studio, Azure Data Studio-compatible environments, or other tools, inspect the actual plan for important queries.

From SQL:

```sql
SET STATISTICS IO ON;
SET STATISTICS TIME ON;
GO
```

Then run the query and inspect:

- logical reads,
- CPU time,
- elapsed time,
- scans vs seeks,
- sort/hash spills,
- key lookups,
- cardinality estimates.

Do not assume an "Index Seek" automatically means a query is efficient; row counts and repeated lookups matter.

## Columnstore

SQL Server supports columnstore indexes for analytical workloads.

A simplified use case:

```sql
CREATE CLUSTERED COLUMNSTORE INDEX cci_fact_sales
ON dbo.fact_sales;
GO
```

Columnstore is designed for:

- large scans,
- compression,
- analytical aggregations,
- warehouse-style tables.

Traditional rowstore indexes are often better for high-frequency point lookups and OLTP patterns.

Hybrid systems can use both strategies.

## Temporal tables

System-versioned temporal tables automatically retain previous row versions for time-based queries.

Conceptually:

```text
current table
      │ changes
      ▼
history table
```

This is useful for:

- auditing,
- historical inspection,
- "what did this row look like yesterday?" queries.

It is not a substitute for backups.

## JSON

SQL Server can store JSON in string columns and query it with JSON functions.

Example:

```sql
DECLARE @doc NVARCHAR(MAX) =
N'{"customer":{"id":42},"items":[1,2,3]}';

SELECT JSON_VALUE(@doc, '$.customer.id');
GO
```

Relational columns should still be preferred for strongly structured, indexed business data when that model is natural.

## Stored procedures

SQL Server is commonly used with stored procedures:

```sql
CREATE OR ALTER PROCEDURE dbo.get_customer_orders
    @customer_id BIGINT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        order_id,
        created_at,
        total_amount
    FROM dbo.orders
    WHERE customer_id = @customer_id
    ORDER BY created_at DESC;
END;
GO
```

Execute:

```sql
EXEC dbo.get_customer_orders @customer_id = 101;
GO
```

Stored procedures are useful when:

- logic belongs near the data,
- permissions should be granted through a narrow database API,
- many applications reuse the same operation.

They also create deployment/versioning work, so do not move all application logic into procedures by default.

## High availability

Common SQL Server availability patterns include:

- backups and point-in-time restore,
- failover cluster instances,
- Always On availability groups,
- Azure SQL managed high-availability options.

High availability is not the same as backup.

```text
replica / failover -> protects service availability
backup / restore   -> protects recoverability
```

A destructive query can replicate to every availability replica.

## Security

Important production controls include:

- Microsoft Entra / Active Directory integration where appropriate,
- least-privilege logins and database users,
- TLS,
- Transparent Data Encryption where required,
- secrets management,
- auditing,
- row-level security where appropriate,
- network restrictions.

Avoid running applications as `sa`.

## SQL Server versus PostgreSQL/MySQL

Choose based on requirements rather than reputation.

SQL Server is often a strong fit when:

- the organization is already Microsoft-heavy,
- .NET integration matters,
- SQL Server-specific operational tooling is valuable,
- enterprise reporting and administration workflows already exist.

PostgreSQL or MySQL may be preferred when:

- open-source ecosystem fit is stronger,
- portability and licensing strategy point that way,
- team expertise is already centered there.

Benchmark the actual workload and compare operational cost.

## Managed SQL Server choices

Common managed options include:

- Azure SQL Database,
- Azure SQL Managed Instance,
- Amazon RDS for SQL Server,
- SQL Server on cloud VMs.

A managed service reduces patching and infrastructure work, but database design, query tuning, capacity, recovery objectives, and cost management remain application responsibilities.

## Common mistakes

### Using `NOLOCK` as a universal performance fix

`NOLOCK` changes read semantics. It can allow dirty or inconsistent observations.

Do not trade correctness for latency without understanding the consequences.

### Ignoring parameter sensitivity

A plan that works for one parameter distribution may be poor for another. Investigate query plans rather than blindly adding hints.

### Keeping transactions open across network calls

This holds locks and connections longer.

### Assuming replicas are backups

They normally reproduce application changes, including bad ones.

### Running applications as sysadmin

Use least privilege.

## Related notes

- [PostgreSQL](03_postgresql.md)
- [MySQL](02_mysql.md)
- [Choosing a database](07_choosing_database.md)
- [Azure database services](15_azure_services.md)
- [Transactions and ACID](../04_acid_properties_and_transactions/)
- [Database performance](../08_database_performance/)
