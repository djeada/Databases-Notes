# Database Management Systems: Follow a Request Through the Engine

A database is the stored data and its definitions. A **database management system (DBMS)** is the software that accepts requests, checks rules, chooses execution strategies, coordinates concurrent work, and manages storage and recovery. A database driver, command-line client, and cloud hosting service surround the DBMS but do not replace these engine responsibilities.

The [first note](01_databases_intro.md) showed the SQL an application sends. The [database-types note](02_types_of_databases.md) compared models. Here we follow those requests through SQLite and PostgreSQL, then connect the responsibilities to other DBMS families.

## Connect the application to the right process

### SQLite: the engine runs inside the application

With SQLite, application code calls a library that manages the local database. Python includes a SQLite interface:

```python
import sqlite3

conn = sqlite3.connect(":memory:")
try:
    conn.execute("CREATE TABLE products (product_id INTEGER PRIMARY KEY, title TEXT)")
    conn.execute("INSERT INTO products VALUES (?, ?)", (10, "Database Basics"))
    conn.commit()
    print(conn.execute("SELECT title FROM products WHERE product_id = ?", (10,)).fetchone())
finally:
    conn.close()
```

The output is `('Database Basics',)`. `:memory:` creates a temporary database private to this ordinary connection; its records disappear when it closes. Using a file path instead allows data to outlive the connection under the engine's persistence guarantees.

```text
Python process
  application code -> sqlite3 interface -> SQLite engine -> memory or local files
```

There is no separate server to log into. Access to a file-backed database is governed largely by filesystem access and the application's design. SQLite does not offer PostgreSQL-style database roles and `GRANT` statements. Its [serverless architecture](https://www.sqlite.org/serverless.html) explains the library model; “serverless” here is distinct from a cloud provider's serverless hosting product.

### PostgreSQL: a client sends requests to a server

PostgreSQL runs a server process that manages database files and accepts client connections. A terminal program such as `psql` is a client. A web application's driver is also a client.

```text
Application process                         Database server
  driver -> connection over network/socket -> PostgreSQL -> database files
```

If PostgreSQL is already running and your account may create databases, these shell commands create and open a practice database:

```bash
createdb chapter1_dbms
psql -d chapter1_dbms
```

The commands use configured connection defaults; they do not install or start a server. `createdb` is a client utility, while `CREATE DATABASE` is the corresponding SQL operation. In the `psql` session, run:

```sql
CREATE TABLE server_products (
    product_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    price_cents INTEGER NOT NULL CHECK (price_cents >= 0)
);

INSERT INTO server_products VALUES (10, 'Database Basics', 1500);

SELECT product_id, title, price_cents FROM server_products;
```

| product_id | title | price_cents |
|---|---|---|
| 10 | Database Basics | 1500 |

The rows are managed by the server; exiting `psql` does not remove them. The client does not need direct access to the server's data files. A remote hostname and database account can be supplied through connection options when required. PostgreSQL's [architecture tutorial](https://www.postgresql.org/docs/current/tutorial-arch.html) describes this separation.

### Managed hosting adds another layer

A managed PostgreSQL service still runs a database engine and accepts database connections. The provider can operate infrastructure, patching, or automated backups, while the application team still controls its schema, workload, data-access logic, and many configuration decisions. “Managed” is a division of operational responsibilities, not a different logical data model.

## Follow parsing, planning, and execution

Use the fresh two-table SQLite setup from sections 3 and 4 of the [introduction](01_databases_intro.md). This is a separate SQLite exercise from the PostgreSQL session above:

```sql
SELECT order_id, order_date
FROM orders
WHERE customer_id = 1
ORDER BY order_id;
```

The intended result is orders 101 and 102. The engine typically performs these stages:

| Stage | Question being resolved | Example |
|---|---|---|
| Parse | Is the statement syntactically meaningful? | Interpret `SELECT`, `FROM`, and the filter |
| Resolve and validate | What objects and values does it refer to? | Find `orders`, check column names, and apply permission rules where supported |
| Optimize and plan | Which available strategy is appropriate? | Compare a table scan with an indexed search |
| Execute | Which visible rows meet the conditions? | Retrieve Alice's orders and sort the result |
| Return | How should values reach the client? | Send two identifiers and dates |

**Declarative SQL** states what result is needed. The **optimizer** chooses how to produce it. The **executor** performs those chosen operations. Different engines organize these components differently, but the distinction explains why the same SQL can execute with different access paths.

### Inspect an actual access path

```sql
EXPLAIN QUERY PLAN
SELECT order_id, order_date
FROM orders
WHERE customer_id = 1
ORDER BY order_id;

CREATE INDEX idx_dbms_orders_customer ON orders(customer_id);

EXPLAIN QUERY PLAN
SELECT order_id, order_date
FROM orders
WHERE customer_id = 1
ORDER BY order_id;
```

On this simple setup, the earlier plan can report `SCAN orders`, while the later plan can report `SEARCH orders USING INDEX idx_dbms_orders_customer (customer_id=?)`. These are illustrative plan details, not guaranteed wording across versions. A **scan** examines input broadly; an indexed **search** targets entries through an access structure. SQLite documents the distinction in [EXPLAIN QUERY PLAN](https://www.sqlite.org/eqp.html).

The index does not change which orders satisfy the query. It changes an available way to find them. With three rows, either approach is inexpensive; with many orders and a selective customer filter, fewer page visits can matter.

### Estimates and measurements are different

PostgreSQL uses `EXPLAIN` for an estimated plan. On the independent `server_products` table above:

```sql
EXPLAIN
SELECT title FROM server_products WHERE product_id = 10;

EXPLAIN (ANALYZE, BUFFERS)
SELECT title FROM server_products WHERE product_id = 10;
```

The second form actually executes the query and reports runtime details. The primary-key index may be useful, but a tiny table can still get a sequential scan. Estimated costs are planner units, not a direct time measurement. See PostgreSQL's [EXPLAIN documentation](https://www.postgresql.org/docs/current/sql-explain.html).

For a slow request, identify whether the time comes from execution, a lock wait, acquiring a connection, or transferring a huge result. These need different remedies. Creating an index cannot fix a request that mostly waits for an application connection pool.

## Keep metadata and data distinct

The engine maintains a **catalog**: information about tables, columns, constraints, indexes, and other objects. It consults that metadata when interpreting SQL.

SQLite exposes schema definitions through `sqlite_schema`:

```sql
SELECT name, type
FROM sqlite_schema
WHERE name IN ('customers', 'orders', 'idx_dbms_orders_customer')
ORDER BY name;
```

| name | type |
|---|---|
| customers | table |
| idx_dbms_orders_customer | index |
| orders | table |

This query asks about database objects, not customer records. PostgreSQL has its own system catalogs and exposes portable object information through `information_schema`. Catalog layouts are engine-specific even when the application tables look similar.

## Enforce rules for every writer

A web form might reject a duplicate email before submitting it. An import script could bypass that form entirely. A database `UNIQUE` constraint applies at the write boundary, protecting the table regardless of which client issued the insert.

Other constraints enforce required values, valid references, and row-level conditions. For SQLite, foreign-key checking must be enabled on each relevant connection. For PostgreSQL, roles and privileges additionally determine who may perform the operation.

A schema rule is not the same thing as a complete business operation. A price of 1 cent can satisfy a nonnegative-price check while still being an incorrect price. A stock decrement without its related order may satisfy every row-level check while violating checkout behavior.

## Coordinate transactions and competing clients

A transaction groups related work, but the application must choose the boundary and respond to failures. For example, creating an order, recording its lines, and reserving stock should normally be one database operation from the business perspective.

**Concurrency control** governs overlapping transactions. A **lock** coordinates conflicting access. **Multi-version concurrency control (MVCC)** lets readers use appropriate row versions while other work changes data. **Isolation levels** determine which interactions the engine permits.

PostgreSQL uses MVCC: an ordinary reader can see an appropriate committed version without reading another transaction's unfinished changes. Competing writers still need coordination, and stronger guarantees can require waiting or retrying. SQLite also supports transactions and concurrent access, but normally serializes writes to a database. These are different implementations, not a difference between “real database” and “just a file.”

For the final copy of a book, an application can condition the decrement on stock being available and check that one row changed. It must then create the order in the same transaction. The [transaction-control note](../03_sql/05_transaction_control_language_tcl.md) provides a complete implementation; [isolation](../04_acid_properties_and_transactions/04_isolation.md) explains the concurrency cases.

## Manage memory, pages, and persistent storage

A **page** is a storage chunk containing row or index information. A **buffer pool** or **page cache** keeps useful pages in memory. A query can find a needed page already cached or cause a read from a lower storage layer.

This is why a repeated query can run faster without any SQL change: the pages it needs may already be available. The operating system can add another cache layer. A page-cache hit is different from an application cache that returns an earlier query result without executing SQL at all.

Updates can modify memory-resident pages before those changes reach their final data-file locations. Engines use recovery mechanisms to make the persistence sequence safe. PostgreSQL uses a **write-ahead log (WAL)**: required log information is persisted before corresponding changed data pages. SQLite has rollback-journal and WAL modes with their own details. The [storage chapter](../05_storage_and_indexing/01_how_tables_and_indexes_are_stored_on_disk.md) develops these mechanisms.

## Recover from a crash and from a bad change

Crash recovery reconstructs the appropriate accepted state after an interrupted process or machine failure. It uses the engine's recovery information and configured durability behavior. A transaction log is not the same thing as application diagnostic output.

A committed accidental deletion presents a different problem: crash recovery does not infer that the deletion was unwanted. A backup or a suitable earlier recovery point supplies a historical state to restore.

### Take and inspect a SQLite backup

If the introductory exercise created `introduction.db`, this standalone Python program uses SQLite's backup API:

```python
import sqlite3

source = sqlite3.connect("introduction.db")
backup = sqlite3.connect("introduction_backup.db")
try:
    source.backup(backup)
    copied = backup.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    print(copied)
finally:
    backup.close()
    source.close()
```

After the introductory exercises, the count is `2`. This checks that a copied table can be read; a serious restore test must check more than one count. The backup API handles copying through the engine instead of assuming that a live database is safely copied by grabbing one arbitrary file. See Python's [SQLite backup interface](https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.backup).

### Export and restore a PostgreSQL practice database

For the separate PostgreSQL exercise, these are shell commands using your configured database credentials:

```bash
pg_dump -Fc -f chapter1_dbms.dump chapter1_dbms
createdb chapter1_dbms_restored
pg_restore -d chapter1_dbms_restored chapter1_dbms.dump
psql -d chapter1_dbms_restored -c 'SELECT COUNT(*) FROM server_products;'
```

The final count should be `1`. `-Fc` creates a custom-format archive, and `pg_restore` loads it into the fresh target database. `pg_dump` exports one database; global objects such as roles need separate treatment. This is a small restore exercise, not a complete production recovery plan. PostgreSQL's [pg_dump documentation](https://www.postgresql.org/docs/current/app-pgdump.html) describes the formats and scope.

## Apply permissions at the right layer

In PostgreSQL, a role can represent a login or a set of privileges. Run this example in the `chapter1_dbms` database as an account allowed to create roles and grant access:

```sql
CREATE ROLE chapter1_report_reader;
GRANT USAGE ON SCHEMA public TO chapter1_report_reader;
GRANT SELECT ON TABLE public.server_products TO chapter1_report_reader;
```

This grants a read capability; it does not create a new password-authenticated login or automatically assign an existing user to the role. A login needs suitable database-connect permissions, authentication configuration, and role membership. `USAGE` on the schema allows object access through that namespace; `SELECT` permits reading the table.

Table-read permission also does not mean an application user may see every customer's orders. When many people share one application's database account, the application must enforce the user's allowed scope, or use an appropriate row-level policy. The [DCL note](../03_sql/04_data_control_language_dcl.md) completes the role example.

For SQLite, protecting the database file and controlling which application operations are exposed is central. For a cloud-hosted engine, provider identity and network controls add layers while database privileges still matter.

## Compare the full range of DBMS families

A DBMS's data model is separate from whether it runs embedded, on a server, or as a managed service.

| Family | Named technology | What its mechanism emphasizes | Example to evaluate |
|---|---|---|---|
| Relational | PostgreSQL, MySQL, SQLite, SQL Server, Oracle Database | Tables, keys, constraints, and relational queries | Orders linked to customers and products |
| Document | MongoDB, CouchDB | Records with nested fields and document operations | A product's varying descriptive attributes |
| Key-value | Redis | Direct access to values or structures through keys | Expiring sessions and carts |
| Wide-column | Cassandra, HBase | Keyed groups and access-pattern-oriented design | Customer events within a time bucket |
| Graph | Neo4j | Nodes and relationship traversal | Recommendations along customer connections |
| Hierarchical | IBM IMS | Segments organized under parent segments | Existing applications navigating a defined hierarchy |
| Network | IDMS | Record navigation through owner/member sets | Existing systems with multiple predefined relationship paths |
| Object-oriented | ObjectDB | Persistence through an object model and object-oriented APIs | A Java application persisting domain objects |

The [next note](04_data_models.md) shows the hierarchical, network, and object structures, develops entity-relationship modeling, and distinguishes an object database from an ORM using relational storage.

## Distributed SQL and the “NewSQL” label

**NewSQL** is an informal label associated with systems that combine relational SQL and transactions with distributed storage and execution. **Distributed SQL** is often a more concrete description. CockroachDB and Google Spanner are examples to investigate; they are not identical architectures or SQL dialects.

CockroachDB divides data into ranges and uses replication coordination to maintain them across nodes. A SQL transaction can touch data beyond one range, so the engine must coordinate the operation across the relevant participants. Its [developer guide](https://www.cockroachlabs.com/docs/stable/developer-basics.html) also explains that some serialization conflicts must be retried by the client.

Google Spanner uses TrueTime, an API exposing time with uncertainty, as part of its transaction-ordering design. Its external-consistency guarantee respects real-time order between transactions. That is a specific mechanism and promise, rather than a generic assertion that all distributed databases are strongly consistent. See Spanner's [TrueTime explanation](https://docs.cloud.google.com/spanner/docs/true-time-external-consistency?hl=en).

### A transaction still looks like database work

In a fresh CockroachDB practice database, this standalone SQL transfers 20.00 of store credit between two known records. It is a single-session teaching example, not a full payment or gift-credit service:

```sql
CREATE TABLE distributed_store_credit (
    customer_id INT PRIMARY KEY,
    balance_cents INT NOT NULL CHECK (balance_cents >= 0)
);
INSERT INTO distributed_store_credit VALUES (1, 10000), (2, 5000);

BEGIN;
UPDATE distributed_store_credit
SET balance_cents = balance_cents - 2000 WHERE customer_id = 1;
UPDATE distributed_store_credit
SET balance_cents = balance_cents + 2000 WHERE customer_id = 2;
COMMIT;

SELECT customer_id, balance_cents
FROM distributed_store_credit
ORDER BY customer_id;
```

| customer_id | balance_cents |
|---|---|
| 1 | 8000 |
| 2 | 7000 |

The combined credit stays 15000. If the records reside on different ranges, preserving one transaction requires distributed coordination. A local practice instance may place everything together, so these rows demonstrate the operation's meaning, not proof of a cross-node execution.

Real code must check both records, validate authorization and available credit, handle errors, and roll back on failure. A missing destination can produce a zero-row update rather than an exception. Serialization retries must repeat the intended transaction without duplicating external effects.

### Compare dimensions instead of assigning guarantees to categories

| Question | Relational examples | NoSQL examples | Distributed SQL examples |
|---|---|---|---|
| What does the model expose? | PostgreSQL tables, relationships, and SQL | MongoDB documents, Redis keys, Cassandra partitions, Neo4j graphs | SQL tables and relationships with distributed implementation |
| What makes a write correct? | Constraints, transaction logic, and isolation choices | Product-specific validation, atomic scope, and coordination | Constraints and transaction logic plus cross-node coordination |
| Where can work run? | Embedded or server; replicas and other distribution options exist | Single-node or distributed depending on the product | Distributed storage/execution is a central design concern |
| What performance should be expected? | Measure the query and concurrency pattern | Measure the actual API and access pattern | Include network coordination, data locality, and retry behavior |
| What must be operated? | Connections, storage, recovery, permissions, migrations | The chosen product's corresponding mechanisms | Those mechanisms plus a suitable node and locality configuration |

There is no universal row saying “SQL scales vertically” and “NoSQL has eventual consistency.” Scaling, transaction scope, replica freshness, and deployment are separate properties. Likewise, an informal NewSQL label does not prove low cost or simple operations.

## Evaluate a DBMS beyond a feature list

Return to the bookstore's actual workload. One offline terminal and a shared website face different deployment and concurrency questions. A catalog page and a revenue report read different portions of the data.

Assess a candidate using a complete representative operation: the schema, query, concurrent write, error path, permissions, and restore process. Check what the team must operate, which drivers and tools fit its environment, and where the guarantees stop.

Attach each selection criterion to an observable requirement:

| Criterion | Concrete question or check |
|---|---|
| Data structure and query complexity | Can the schema express orders, lines, and their relationships, and can the required reports query them? |
| Scalability | Which bottleneck is growing: storage, write contention, CPU, or reads? What does adding resources actually distribute? |
| Performance | What are the latency distribution and throughput under representative parameters and concurrent load? |
| Consistency and reliability | What is atomic, what can a read observe, and how does retry behave after an ambiguous commit? |
| Availability and fault tolerance | What happens when the writer or one region is unavailable, and which copy is safe to promote? |
| Security | How are connections authenticated, permissions limited, sensitive data protected, and relevant actions audited? |
| Cost and licensing | Include service or license charges, storage, data movement, backup retention, and operator time |
| Community and support | Are usable drivers, migration tools, documentation, and support available for the team's environment? |
| Operational complexity | Can the team deploy, monitor, patch, back up, restore, and recover this system within its requirements? |

A product's advertised “scalability” is not a substitute for a concrete capacity and failure model.

## Practice and check your understanding

1. In the SQLite Python example, what disappears when the connection closes, and how would a file-backed database differ?
2. Which process owns PostgreSQL's data files when a remote client executes a query?
3. What work do parsing, planning, and execution each do?
4. Why can adding an index leave a query's result unchanged but alter its plan?
5. Explain the difference between catalog metadata, cached pages, and an application result cache.
6. Why does recovery from a crash not undo an accepted accidental deletion?
7. What does the reporting-role example grant, and what setup does it not perform?
8. How do object-oriented, hierarchical, and network DBMSs differ from relational storage?

Continue with [data models](04_data_models.md) to turn a business rule into a concrete structure and executable schema.
