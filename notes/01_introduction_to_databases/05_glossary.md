# Database Glossary

Use this page as a reference when a term interrupts your reading. You do not need to memorize it before starting SQL. The groups follow the learning path: data, queries, transactions, storage, distributed systems, and analytics.

## Data and structure

| Term | Plain-language meaning and example |
|---|---|
| Database | An organized collection of data, such as the bookstore's customers and orders |
| DBMS | Database management system: software that stores, queries, and manages the database; SQLite is one example |
| Relational database / RDBMS | A database based on relations, represented as tables; an RDBMS is the software managing it |
| Table | A named collection of rows with defined columns, such as `customers` |
| Row / record | One entry, such as Alice's customer record |
| Column / field | One named attribute, such as `email`; SQL client columns also describe query results |
| Data type | A description of permitted values and operations, such as an integer or date; enforcement differs by engine |
| Schema | The database's structural definitions; in some engines, also a named namespace containing objects |
| Primary key | The chosen identifier for each row, such as `customer_id`; it may contain multiple columns |
| Foreign key | A constraint requiring a reference to match an eligible key in another or the same table, except for permitted nulls |
| Composite key | A key made from multiple columns, such as `(order_id, line_number)` |
| Constraint | A declared rule the database checks, such as requiring a distinct email |
| `UNIQUE` | Rejects duplicate key values; the treatment of null values depends on the engine and options |
| `NOT NULL` | Requires a value to be present; an empty string is still a value |
| `CHECK` | Rejects rows when its expression is false; an unknown result caused by nulls generally passes |
| `NULL` | A marker for a missing or unknown value, distinct from zero and an empty string |
| Cardinality | In modeling, how many entities can be related, such as one customer to many orders; in query planning, an estimated or actual row count |
| Normalization | Organizing tables around their dependencies to avoid repeated facts and update anomalies |
| Denormalization | Deliberately storing derived or repeated information, often to reduce measured read costs; copies need maintenance |

For examples, see [data models](04_data_models.md), [normalization](../02_database_design/02_normalization.md), and [data integrity](../02_database_design/05_data_integrity.md).

## SQL and queries

| Term | Plain-language meaning and example |
|---|---|
| SQL | Structured Query Language: a language for querying and managing relational data |
| Dialect | An engine's particular SQL syntax and behavior; SQLite and PostgreSQL differ |
| Query | A request for information; “SQL statement” also includes commands that change data or structure |
| `SELECT` | Produces a result from expressions, tables, or other query inputs |
| `INSERT` / `UPDATE` / `DELETE` | Add rows, change rows, or remove rows |
| `WHERE` | Keeps rows for which its condition is true |
| `ORDER BY` | Specifies result ordering; without it, do not depend on row order |
| `JOIN` | Combines rows from inputs according to a condition or, for a cross join, every pairing |
| Alias | A name used in a query, such as `c` for `customers` |
| Subquery | A query inside another statement, such as a query calculating an average for a filter |
| Aggregate | A calculation over multiple rows, such as `SUM(quantity)` |
| `GROUP BY` | Forms groups of rows so aggregates can be calculated for each group |
| Window function | Calculates across related rows while retaining individual result rows, such as a running total |
| View | A named query that can be used like a table; an ordinary view does not store a separate result snapshot |
| Materialized view | A stored query result maintained or refreshed according to the engine and configuration |
| Stored procedure | A named routine invoked to perform database work; available syntax and capabilities vary |
| Function | A routine that computes a result; SQL functions vary in supported inputs, results, and effects |
| Trigger | Database logic invoked by specified events, such as inserting a row |
| Bound parameter | A value passed separately from SQL text through a driver's placeholder mechanism |
| SQL injection | Untrusted input changes SQL structure because it was assembled into executable query text |
| DDL / DML / DCL / TCL | Common labels for defining objects, working with rows, controlling access, and controlling transactions |

Start with the runnable [SQL introduction](../03_sql/01_intro_to_sql.md). For injection prevention, see [SQL injection](../11_security_best_practices/06_sql_injection.md).

## Transactions and concurrency

| Term | Plain-language meaning and example |
|---|---|
| Transaction | Database operations grouped into a unit that can commit or roll back |
| Commit / rollback | Accept a transaction's changes / discard its changes |
| Savepoint | A marker allowing rollback of part of a transaction without committing the rest |
| Autocommit | A connection mode that normally gives each statement its own transaction; driver behavior matters |
| ACID | Atomicity, consistency, isolation, and durability: four distinct transaction guarantees |
| Atomicity | Transactional changes are committed together or rolled back together |
| Consistency, in ACID | Correct transactions preserve the application's required data rules |
| Isolation | Guarantees about how overlapping transactions interact and what they can observe |
| Durability | Acknowledged commits survive failures within the configured storage and recovery guarantees |
| Concurrency | Operations overlap in time |
| Lock | Coordination that prevents conflicting operations on a resource |
| Deadlock | Transactions wait on resources held by one another in a cycle; the engine usually aborts one to make progress |
| MVCC | Multi-version concurrency control: readers can use appropriate versions of data while other transactions change it |
| Snapshot | A view of data at a defined point or visibility boundary; its lifetime depends on the engine and isolation level |
| Serializable | Successful transactions have an outcome equivalent to some serial execution order; failures can require retries |
| Invariant | A condition that must remain true, such as stock never becoming negative |

See [transactions](../04_acid_properties_and_transactions/01_transactions_intro.md) before [concurrency control](../07_concurrency_control/01_shared_vs_exclusive_locks.md).

## Storage and performance

| Term | Plain-language meaning and example |
|---|---|
| Index | An extra access structure that can reduce lookup work; maintaining it also costs space and writes |
| Query plan | The engine's chosen operations for executing a query, such as a scan followed by a sort |
| Scan | Read rows or entries and test them, rather than locating only specific matches |
| Selectivity | How much of the input a condition matches; a filter matching few rows is often called highly selective |
| Page | A chunk used to organize database storage and memory management |
| Buffer pool / page cache | Memory holding database pages so they can be reused without another engine storage read |
| Cache | A reusable copy of data or results; different cache layers have different freshness rules |
| WAL | Write-ahead log: recovery information persisted before corresponding data-page changes |
| Checkpoint | An engine-specific recovery progress boundary, often coordinated with flushing data |
| Row-oriented storage | Keeps a record's fields together, commonly suited to short record operations |
| Column-oriented storage | Keeps values of the same column together, commonly suited to broad analytical scans |
| In-memory database | Keeps its main working data in memory; persistence and recovery are separate design choices |
| Vertical scaling | Increase the resources of a machine, such as memory or CPU |
| Horizontal scaling | Add machines; useful work must still be distributed among them |

See [row and column storage](../05_storage_and_indexing/02_row_based_vs_column_based_databases.md), [pages](../05_storage_and_indexing/04_database_pages.md), and [indexing](../05_storage_and_indexing/05_indexing.md).

## Distribution and database models

| Term | Plain-language meaning and example |
|---|---|
| Node | A machine or participating process in a distributed system |
| Partitioning | Divide a dataset into subsets, such as orders grouped by month |
| Sharding | Distribute horizontal subsets across nodes and route operations to the owning shard |
| Shard key | The value used to choose a shard, such as a customer identifier |
| Replication | Maintain copies of data by transferring changes between nodes |
| Primary / replica | A node accepting writes / a node maintaining a copy, in a common single-writer design |
| Replication lag | A replica has not yet received or applied the latest changes |
| Failover | Transfer a failed node's serving or writing role to another node |
| Network partition | A communication break that prevents some nodes from reaching others |
| CAP | During a network partition, a distributed read/write service cannot guarantee both linearizability and a successful response to every request at a non-failing node |
| Linearizability | Operations appear to take effect at a single point between invocation and completion, respecting real-time order |
| Eventual consistency | If updates stop and communication recovers, replicas are expected to converge |
| BASE | An informal description of some systems favoring availability and eventual convergence; it is not a precise universal alternative to ACID |
| NoSQL | An umbrella label for models such as document, key-value, wide-column, and graph; guarantees depend on the product |
| Document database | Stores records as documents with fields and potentially nested values |
| Key-value store | Retrieves a value primarily by its associated key |
| Wide-column database | Organizes data around partition and clustering keys for defined access patterns; distinct from columnar analytical storage |
| Graph database | Represents entities and connections for relationship traversal |

See [database types](02_types_of_databases.md) and [distributed databases](../06_distributed_databases/01_distributed_database_systems.md).

## Analytics, operations, and tools

| Term | Plain-language meaning and example |
|---|---|
| OLTP | Online transaction processing: many short operational reads and writes |
| OLAP | Online analytical processing: reports and calculations over many records |
| Data warehouse | An analytical store combining data for reporting, often with historical records |
| ETL / ELT | Extract-transform-load / extract-load-transform: different placements of transformation in a data pipeline |
| Big data | Data whose scale, rate, or complexity motivates specialized storage or processing; no universal size threshold |
| Hadoop / HDFS | A distributed data-processing ecosystem / its distributed filesystem |
| MapReduce | A computation model that maps input records and combines grouped intermediate results |
| Spark | A distributed processing engine with SQL and other interfaces |
| ORM | Object-relational mapper: translates between application objects and relational database operations |
| Backup | A preserved copy intended for later restoration, rather than only ongoing replication |
| RPO / RTO | Recovery point objective: acceptable data-loss window / recovery time objective: acceptable time to restore service |
| Migration | A controlled change to schema or data between application versions or systems |

Product names are introduced in the [engine chapters](../../README.md#12-database-engines), where their capabilities have context. Start [data warehousing](../13_big_data/01_data_warehousing.md) after practicing aggregates and joins.
