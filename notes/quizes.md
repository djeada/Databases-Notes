# Database Review Quiz

Try answering each question before opening its answer. SQL exercises identify their dialect; syntax and guarantees vary between engines.

## Database Fundamentals

<details>
<summary>What is a database?</summary>

A database is an organized collection of data stored electronically so it can be queried, updated and managed efficiently. A database management system (DBMS) is the software that stores the data, enforces rules such as constraints, coordinates concurrent users through transactions, and recovers the data after failures. Databases range from a single SQLite file embedded in an application to distributed systems spread across many servers.

</details>

<details>
<summary>What is SQL?</summary>

SQL (Structured Query Language) is the standard declarative language for relational databases. You describe the result you want, and the optimizer decides how to obtain it. SQL covers querying data, changing rows, defining and altering structures, controlling access and grouping work into transactions. Every engine implements its own dialect, so syntax and behavior can differ between PostgreSQL, MySQL, SQL Server and SQLite.

</details>

<details>
<summary>What is the difference between a database and a schema?</summary>

A schema can mean the logical design of tables and constraints or an engine-specific namespace. PostgreSQL and SQL Server allow multiple schemas inside a database. MySQL generally treats `SCHEMA` as a synonym for `DATABASE`; SQLite uses schema names for attached databases.

</details>

<details>
<summary>What is a database schema, and why is it important?</summary>

A database schema is the structured blueprint of a database: its tables, columns, data types, relationships, indexes and constraints. It defines how data is organized and which rules every writer must obey. A well-designed schema keeps data consistent and unambiguous, makes queries straightforward to write, and lets the database reject invalid data instead of relying on every application to check it.

</details>

<details>
<summary>Is a table in a database dynamic or static?</summary>

A table is dynamic: its contents change over time through inserts, updates and deletes. Its structure can also change through DDL such as `ALTER TABLE`, although structural changes on production data are usually planned as migrations because existing rows and running applications must keep working.

</details>

<details>
<summary>What are some common types of database management systems (DBMS), and how do they differ?</summary>

- **Relational** (PostgreSQL, MySQL, SQL Server): tables, SQL, constraints and transactions; strong at combining independently stored facts.
- **Document** (MongoDB, Couchbase): flexible nested records; good when a bounded aggregate is read and written together.
- **Key-value** (Redis): direct access by key; fast but limited querying.
- **Wide-column** (Cassandra): tables designed around partition keys for known queries at large scale.
- **Graph** (Neo4j): nodes and relationships for traversal-heavy queries.

Memory-first systems such as Redis keep data in RAM for speed; Redis can persist to disk, while caches like Memcached do not persist at all. Guarantees depend on the product and configuration, not just the category.

</details>

## Relational Model and Design

<details>
<summary>What is a relational database model, and why is it called "relational"?</summary>

The relational model organizes data into relations, which SQL presents as tables of rows and columns. Each table typically represents one entity type, and each row is one fact about an instance. The name comes from the mathematical term **relation** (a set of tuples), not from the relationships between tables. Relationships are represented by keys: a foreign key stores the identifier of a related row, and joins combine related rows at query time.

</details>

<details>
<summary>In databases, what are the meanings of the terms "entities" and "attributes"?</summary>

An entity is an object or concept the database tracks, such as a customer or an order; an entity type is the kind of thing, and an entity instance is one occurrence, such as the customer Alice. Attributes are the properties of an entity, such as a customer's name and email, and usually become columns.

</details>

<details>
<summary>Differentiate between base and derived relations in a relational database.</summary>

- **Base relations:** the actual stored tables defined by the schema.
- **Derived relations:** results computed from base relations by operations such as selection, projection, join and union. Ordinary views are named derived relations: they store a query definition, not the data itself.

</details>

<details>
<summary>Explain the two main principles of the relational database model and how they differ.</summary>

Two goals are often emphasized:

- **Data integrity:** the data must obey declared rules, such as keys, foreign keys and checks, so it stays valid and unambiguous.
- **Data independence:** applications work with logical relations, so the physical storage (files, indexes, layout) can change without changing queries.

Integrity is about what values are allowed; independence is about separating the logical model from storage choices. They are design goals rather than a complete definition: the model itself represents data as relations and manipulates them with relational operations.

</details>

<details>
<summary>List some relational operations that can be performed on tables in a relational database.</summary>

- **Selection (σ):** keep the rows that satisfy a condition; in SQL, the `WHERE` clause.
- **Projection (π):** keep only some columns; in SQL, the `SELECT` list.
- **Join:** combine rows from two tables based on related columns.
- **Union:** rows from either input, without duplicates.
- **Intersection:** rows present in both inputs (`INTERSECT`).
- **Difference:** rows in the first input but not the second (`EXCEPT`, or `MINUS` in Oracle).
- **Rename:** give a relation or attribute a new name; in SQL, aliases.

Grouping and aggregate functions such as `COUNT`, `SUM` and `AVG` are common extensions of the basic relational algebra.

</details>

<details>
<summary>What is normalization in the context of database design, and why is it important?</summary>

Normalization organizes tables so each fact is stored once, with the entity it describes. It works by identifying functional dependencies and splitting tables losslessly, following forms such as 1NF, 2NF, 3NF and BCNF.

- **Removes update anomalies:** renaming a customer changes one row instead of every order that repeated the name.
- **Protects integrity:** keys and foreign keys can enforce the rules directly.
- **Simplifies maintenance:** each fact has one authoritative place.

Normalization is not automatically faster: reports may need more joins. Some systems later denormalize selected data, with an explicit plan for keeping copies in sync.

</details>

## Keys and Constraints

<details>
<summary>What is the difference between a primary key and a candidate key?</summary>

A candidate key is a minimal set of attributes that uniquely identifies a row. The primary key is the candidate key selected as the main identifier. Other candidate keys are alternate keys. Adding unnecessary attributes to a candidate key makes it a superkey rather than another candidate key.

</details>

<details>
<summary>What is the difference between a primary key and a foreign key?</summary>

- **Primary key:** a column or set of columns that uniquely identifies each row in its table. It must be unique and cannot contain NULL.
- **Foreign key:** a column or set of columns that references a primary key or unique key in a table (possibly the same table). The database rejects values with no matching referenced row, which maintains referential integrity. A nullable foreign key can be NULL to mean "no related row".

</details>

<details>
<summary>Why can there be only one primary key in a table?</summary>

SQL designates one candidate key as the primary key. Other candidate keys can remain as alternate keys, enforced with `UNIQUE` and `NOT NULL` constraints. The primary key can contain multiple columns; the one-primary-key convention does not imply that a row has only one possible identifier.

</details>

<details>
<summary>Are all columns keys?</summary>

No. A key is a column or set of columns used to uniquely identify rows (primary, alternate/unique keys) or to reference another table (foreign keys). Most columns store descriptive, often non-unique facts such as a name, price or status, and are not part of any key.

</details>

<details>
<summary>Are all keys indexes?</summary>

No. Keys express logical rules; indexes are access structures. Engines commonly create indexes for primary and unique keys, but an index on the referencing side of a foreign key is engine-dependent. Non-unique indexes do not define candidate keys.

</details>

<details>
<summary>What is the difference between a unique constraint and a unique index?</summary>

- **Unique constraint:** a logical rule that no two rows share the same values in the listed columns. It is part of the schema's meaning and can be referenced by foreign keys.
- **Unique index:** a physical access structure that also rejects duplicates. Most engines enforce a unique constraint by creating a unique index, which also speeds up lookups on those columns.

Some engines allow unique indexes with extra features, such as partial or expression-based uniqueness, that cannot be declared as a plain constraint.

</details>

<details>
<summary>What are database constraints, and why do they matter?</summary>

Constraints are rules the database enforces on every write, whichever application or tool performs it:

- **Primary key:** each row is uniquely identifiable.
- **Foreign key:** a referencing value must match an existing row's primary or unique key.
- **Unique:** values in a column or column set are not repeated.
- **Check:** each row must satisfy a condition, such as `price_cents >= 0`.
- **Not null:** a column must always have a value.

Because the database rejects invalid data at the source, constraints close gaps that application checks leave open, such as two concurrent clients both passing a pre-insert check.

</details>

<details>
<summary>Why are domain constraints important in a database?</summary>

Domain constraints define the permissible values for an attribute through its data type, `NOT NULL`, and `CHECK` conditions on ranges or formats. For example, a date of birth must be a valid date and not in the future. They keep invalid values out regardless of which application writes the data. How strictly types are enforced is engine-specific: ordinary SQLite tables use type affinity unless declared `STRICT`.

</details>

<details>
<summary>What is the purpose of ON DELETE CASCADE?</summary>

`ON DELETE CASCADE` is a referential action on a foreign key, not a separate constraint. When a parent row is deleted, the database automatically deletes the child rows that reference it, so no orphaned rows remain. Choose it only when the children's lifecycle truly belongs to the parent, such as order lines belonging to an order. For data like historical orders, alternatives such as `RESTRICT` (reject the delete) or `SET NULL` may be safer.

</details>

## SQL Basics

<details>
<summary>What are DDL, DML, and DCL in SQL?</summary>

- **DDL (Data Definition Language):** defines and changes structures, such as `CREATE TABLE`, `ALTER TABLE` and `DROP TABLE`.
- **DML (Data Manipulation Language):** reads and changes rows, such as `SELECT`, `INSERT`, `UPDATE` and `DELETE`. `SELECT` is sometimes separated out as DQL.
- **DCL (Data Control Language):** manages permissions, such as `GRANT` and `REVOKE`.

Transaction control statements such as `COMMIT`, `ROLLBACK` and `SAVEPOINT` are often grouped as TCL.

</details>

<details>
<summary>What is the purpose of the NULL value in SQL?</summary>

NULL marks a missing or unknown value. It is distinct from zero, an empty string or any default. Comparing NULL with `=`, `<>` or `<` yields unknown rather than true, so `WHERE phone = NULL` matches nothing; use `IS NULL` and `IS NOT NULL` instead. Aggregates such as `SUM` and `AVG` ignore NULLs, and `COALESCE` substitutes a fallback value when one is appropriate.

</details>

<details>
<summary>What is an alias in SQL?</summary>

An alias is a temporary query name, not a separate SQL command. For example, `SELECT u.name AS display_name FROM users AS u;` gives the table and output column aliases. Whether `AS` is optional or supported for table aliases depends on the dialect.

</details>

<details>
<summary>What is the difference between the CHAR and VARCHAR data types?</summary>

- **CHAR(n):** a fixed-length string. Shorter values are padded with spaces to `n` characters.
- **VARCHAR(n):** a variable-length string that stores only the actual characters plus a small length overhead, up to `n`.

CHAR suits values that always have the same length, such as fixed codes. Storage and performance details are engine-specific: in PostgreSQL, for example, `char(n)` has no performance advantage over `varchar(n)` or `text`.

</details>

<details>
<summary>What is the purpose of the CASE expression?</summary>

`CASE` adds conditional logic inside a query and returns a value, much like if/else in a programming language. It can label rows (`CASE WHEN EXTRACT(HOUR FROM created_at) >= 12 THEN 'PM' ELSE 'AM' END`), map codes to names, or count conditions with `SUM(CASE WHEN ... THEN 1 ELSE 0 END)`. Because it is an expression, it can appear in `SELECT`, `WHERE`, `ORDER BY` and inside aggregates.

</details>

<details>
<summary>How does the STUFF function differ from the REPLACE function in SQL Server?</summary>

- **STUFF:** deletes a given number of characters at a given position and inserts another string there. `STUFF('abcdef', 2, 3, '123')` returns `'a123ef'`.
- **REPLACE:** replaces every occurrence of a substring. `REPLACE('abcdefabc', 'abc', '123')` returns `'123def123'`.

STUFF is position-based and T-SQL-specific; REPLACE is pattern-based and exists in most dialects.

</details>

<details>
<summary>What are the similarities and differences between TRUNCATE and DELETE commands in SQL?</summary>

Both remove rows and keep the table definition. `DELETE` can filter rows with `WHERE`; `TRUNCATE` removes the whole table's data using an engine-specific bulk operation. Logging, identity resets, triggers, and rollback differ. PostgreSQL and SQL Server can roll back a transactional `TRUNCATE`; MySQL `TRUNCATE` implicitly commits. PostgreSQL also supports `TRUNCATE` triggers.

</details>

<details>
<summary>How are prepared statements and meta commands stored and processed?</summary>

Prepared statements separate SQL structure from bound values; preparation and plan reuse depend on the driver and engine. Client meta-commands such as psql’s `\d` are interpreted by the client, which may issue SQL internally. They are not SQL schema-definition commands.

</details>

## Joins and Set Operations

<details>
<summary>What is a join in SQL, and what are the different types?</summary>

A join combines rows from two or more tables based on a related condition.

- **INNER JOIN:** only pairs of rows that match.
- **LEFT JOIN:** all rows from the left table, with NULLs where the right side has no match.
- **RIGHT JOIN:** all rows from the right table, with NULLs where the left side has no match.
- **FULL OUTER JOIN:** all rows from both tables, matched where possible and NULL-extended otherwise.
- **CROSS JOIN:** every combination of rows (the Cartesian product).

Support varies: MySQL has no `FULL OUTER JOIN`, and SQLite added right and full joins in 3.39.0.

</details>

<details>
<summary>Can you explain the differences between Inner Join and Left Join in SQL?</summary>

- **Inner join:** returns only rows that have matching values in both tables. Unmatched rows are excluded.
- **Left join:** returns every row from the left table plus matching rows from the right table. Where no match exists, the right table's columns are NULL.

A filter on the right table placed in `WHERE` removes those NULL-extended rows and turns a left join back into an inner join; put it in the `ON` clause to keep unmatched left rows.

</details>

<details>
<summary>What is the difference between a cross join and an inner join?</summary>

- **Cross join:** the Cartesian product of two tables, every row paired with every row, with no condition. Three customers and three products give nine rows.
- **Inner join:** only the pairs that satisfy a join condition, usually on key columns.

Cross joins are useful when every combination is intended; an accidental one, from a missing join condition, can produce a huge result.

</details>

<details>
<summary>What are self joins and cross joins in SQL?</summary>

A self join is used to join a table to itself, often using aliases to avoid confusion. It is useful for hierarchical data structures like reporting relationships. A cross join returns the Cartesian product of two tables, combining every row from one table with every row from the other.

</details>

<details>
<summary>What is a self-join?</summary>

A self-join joins a table with itself, using different aliases for each copy. It compares rows within the same table, for example matching each employee's `manager_id` to another employee's `id` to list employees with their managers:

```sql
SELECT e.name AS employee, m.name AS manager
FROM employees AS e
LEFT JOIN employees AS m ON m.id = e.manager_id;
```

</details>

<details>
<summary>What is the difference between the UNION and JOIN operators?</summary>

- **UNION:** combines the results of two queries vertically, appending rows. Both queries must return the same number of compatible columns. It removes duplicate rows unless `UNION ALL` is used.
- **JOIN:** combines tables horizontally, placing columns from related rows side by side based on a condition.

</details>

<details>
<summary>What is the difference between UNION and UNION ALL?</summary>

Both combine the result sets of two or more `SELECT` statements with compatible columns.

- **UNION:** removes duplicate rows, which usually requires a sort or hash step.
- **UNION ALL:** keeps every row, including duplicates, and is cheaper.

Use `UNION ALL` when duplicates are impossible or wanted.

</details>

<details>
<summary>How do UNION, MINUS, UNION ALL, and INTERSECT differ in SQL?</summary>

INTERSECT returns distinct rows common to both SELECT queries. MINUS returns distinct rows from the first query not found in the second query; MINUS is Oracle's name, while the SQL standard, PostgreSQL, SQL Server and SQLite use EXCEPT. UNION returns all distinct rows from either query. UNION ALL returns all rows from both queries, including duplicates.

</details>

## Subqueries

<details>
<summary>When should you use a subquery in SQL, and can you provide an example?</summary>

Use a subquery when one query needs the result of another, such as comparing rows with a calculated value or testing whether related rows exist. For example, to find employees earning more than the average salary:

```sql
SELECT *
FROM employees
WHERE salary > (SELECT AVG(salary) FROM employees);
```

The inner query returns one value, the average, and the outer query keeps employees above it.

</details>

<details>
<summary>What is the difference between correlated and nested subqueries in SQL?</summary>

A subquery is nested inside another query. A correlated subquery additionally references an outer query’s columns. It is logically evaluated in the outer-row context, but the optimizer can decorrelate it; do not infer a fixed number of physical executions from the syntax.

</details>

<details>
<summary>What is the difference between the IN and EXISTS operators?</summary>

`IN` compares a value with a set; `EXISTS` tests whether a subquery returns any row. Optimizers can produce similar plans for equivalent forms, so neither is universally faster. `NOT IN` can evaluate to unknown if the subquery contains a null; correlated `NOT EXISTS` is often clearer for anti-joins.

</details>

<details>
<summary>What is the difference between the EXISTS and NOT EXISTS operators?</summary>

Both test whether a subquery returns rows; neither returns the matching rows themselves.

- **EXISTS:** true when the subquery returns at least one row, for example customers who have an order.
- **NOT EXISTS:** true when the subquery returns no rows, for example customers with no orders.

They are usually correlated with the outer row. The engine can stop at the first matching row, but whether that is faster than a join or `IN` depends on the optimizer and plan.

</details>

## Aggregation and Window Functions

<details>
<summary>What is the purpose of the GROUP BY clause?</summary>

`GROUP BY` puts rows with the same values in the listed columns into groups, so aggregate functions such as `COUNT`, `SUM`, `AVG`, `MIN` and `MAX` return one result per group. For example, `SELECT department_id, COUNT(*) FROM employees GROUP BY department_id;` counts employees in each department. Every selected column must either be grouped or aggregated (some engines relax this).

</details>

<details>
<summary>What distinguishes WHERE and HAVING in SQL?</summary>

The **WHERE** and **HAVING** clauses are both used to filter records in SQL, but they are applied at different stages of query processing:

- **WHERE:** This clause is used to filter rows before any grouping or aggregation takes place. It applies to individual rows and is used to set conditions on the columns of the table.
- **HAVING:** This clause is used to filter groups after the grouping and aggregation have been performed. It applies to the aggregated data and is typically used in conjunction with the GROUP BY clause.

</details>

<details>
<summary>What is the purpose of the ROW_NUMBER() function?</summary>

`ROW_NUMBER()` is a window function that assigns sequential integers 1, 2, 3... to rows within each partition, in the order given by its `OVER (... ORDER BY ...)` clause. Common uses are picking the latest row per group and deduplication. Tied rows still get different numbers, so add a unique tie-breaker column to the ordering if the result must be deterministic.

</details>

<details>
<summary>What is the RANK function in SQL?</summary>

`RANK()` is a window function that numbers rows within a partition according to the `ORDER BY` in its `OVER` clause. Tied rows receive the same rank, and the next rank skips ahead by the number of ties: values 100, 100, 200 get ranks 1, 1, 3. `DENSE_RANK()` gives 1, 1, 2 instead, and `ROW_NUMBER()` gives 1, 2, 3.

</details>

## Views, Procedures and Triggers

<details>
<summary>What is the purpose of a VIEW in a relational database?</summary>

A VIEW in a relational database is a virtual table based on the result set of a SELECT query. Views serve several purposes:

- **Simplify Complex Queries:** Views can encapsulate complex queries, making it easier for users to retrieve data without needing to understand the underlying query logic.
- **Customized Data Representation:** Views can present data in a specific format or structure that is more useful for certain applications or user needs.
- **Data Security:** Views can restrict access to specific columns or rows, ensuring that users see only the data they are authorized to view.
- **Data Abstraction:** Views provide a level of abstraction, hiding the complexity and details of the underlying database schema.

</details>

<details>
<summary>What is the difference between a view and a materialized view?</summary>

- **View:** stores only the query definition. Each read runs the query against the current base tables, so results are always current.
- **Materialized view:** stores the query's result physically. Reads are fast because the work is precomputed, but the data is only as fresh as the last refresh, which happens on demand, on a schedule or through engine-specific incremental maintenance.

</details>

<details>
<summary>What is a stored procedure?</summary>

A stored procedure is a named routine executed by the database. It can accept parameters and contain SQL and procedural logic. Compilation and plan caching depend on the engine; a procedure is not automatically faster than equivalent parameterized SQL.

</details>

<details>
<summary>Why are stored procedures considered executable code in a database?</summary>

A stored procedure is a program stored in the database and run by the database server. Besides SQL statements, it can use variables, conditions, loops and error handling written in a procedural language such as PL/pgSQL or T-SQL. It is invoked as a statement, for example `CALL cancel_order(101);` in PostgreSQL or `EXEC` in SQL Server, rather than being a passive data structure like a table or view.

</details>

<details>
<summary>What are the advantages of using stored procedures in a database?</summary>

Stored procedures offer several advantages in a database environment:

- **Plan reuse:** Some engines cache routine execution plans; parameterized queries can also reuse plans, and performance still needs measurement.
- **Reduced Network Traffic:** Executing stored procedures reduces the amount of data transmitted between the database server and client by encapsulating multiple operations in a single call.
- **Code Reuse:** Encapsulating complex logic in stored procedures promotes code reuse and simplifies maintenance.
- **Enhanced Security:** Stored procedures can restrict direct access to data and enforce security measures by controlling user access to specific procedures.
- **Consistency:** Centralizing business logic in stored procedures ensures that consistent operations are performed across different applications.

</details>

<details>
<summary>What is a trigger in a relational database?</summary>

A trigger is database code that runs automatically when a specified event, such as an insert, update or delete, happens on a table (or, with `INSTEAD OF`, on a view). It can run before or after the change, per row or per statement depending on the engine. `AFTER` means after the row change, not after commit: trigger writes are part of the same transaction and roll back with it. Prefer constraints or defaults when they express the rule directly, because triggers add less visible behavior.

</details>

<details>
<summary>What are cursors in SQL and when are they useful?</summary>

A cursor exposes a query result for incremental fetching or row-by-row processing. It is useful when a procedure must handle each row individually or when a client streams a large result in batches instead of loading it all at once. Set-based SQL statements are usually simpler and faster than looping over rows. Cursor kinds, options and lifecycles differ between engines.

</details>

<details>
<summary>What is the difference between a temporary table and a table variable?</summary>

In SQL Server, temporary tables and table variables both can use tempdb; a table variable is not inherently memory-only. They differ in scope, statistics, and optimization behavior. Performance depends on row counts, queries, and version; benchmark rather than assuming table variables are faster.

</details>

## Transactions and Concurrency

<details>
<summary>What is a transaction in a database, and why is it important?</summary>

A transaction is a group of one or more operations, such as inserts, updates and deletes, treated as a single unit of work. A checkout that reserves stock and creates an order should either do both or neither. Transactions provide the ACID properties:

- All operations commit together or none do (atomicity).
- Declared rules hold before and after the transaction (consistency).
- Concurrent transactions are protected from each other's intermediate work to the degree set by the isolation level (isolation).
- Committed changes survive crashes (durability).

</details>

<details>
<summary>Can you explain the concept of ACID properties in database systems?</summary>

- **Atomicity:** a transaction's changes are all applied or none are, so a failure cannot leave a partial update.
- **Consistency:** a committed transaction moves the database from one valid state to another, respecting constraints and other declared rules.
- **Isolation:** concurrent transactions do not see each other's uncommitted work, and the isolation level determines which other anomalies are prevented. Engines implement it with locks, MVCC snapshots or both.
- **Durability:** once a commit is acknowledged, the change survives crashes, typically because the commit is recorded in a write-ahead log flushed to durable storage.

</details>

<details>
<summary>What are COMMIT and ROLLBACK commands in SQL?</summary>

`COMMIT` ends a transaction and makes its changes permanent and visible to other transactions. `ROLLBACK` ends a transaction and discards all of its uncommitted changes, returning the data to its state before the transaction began. Neither can undo the other: a committed change can only be reversed by a new transaction, and a rollback cannot recover data that was already committed and later lost.

</details>

<details>
<summary>How does rolling back a transaction work?</summary>

Rollback undoes that transaction’s transactional changes, not concurrent commits by other transactions. Some effects, such as PostgreSQL sequence increments or external API calls, are not undone. DDL rollback behavior also depends on the engine.

</details>

<details>
<summary>What is a database transaction log, and why is it important?</summary>

A transaction log (write-ahead log, redo log) records changes before the corresponding data pages are written to disk. A commit is durable once its log records are safely persisted, so after a crash the engine replays committed work and undoes incomplete work. The log also supports point-in-time recovery when archived with backups, and replication, which ships log records to replicas.

</details>

<details>
<summary>What is NOLOCK and how does it affect concurrency?</summary>

In SQL Server, `WITH (NOLOCK)` requests Read Uncommitted behavior for data reads. It can return dirty, missing, or duplicated data. It neither releases another transaction’s locks nor avoids every lock: schema stability locking still applies. Consider row-versioned isolation when correct nonblocking reads are needed.

</details>

<details>
<summary>What is a deadlock in a database, and how can it be resolved?</summary>

A deadlock is a cycle of waits: T1 holds a lock T2 needs while T2 holds a lock T1 needs, so neither can proceed. Databases such as PostgreSQL, MySQL and SQL Server detect the cycle and abort one transaction as the victim, which the application should retry as a whole transaction. To prevent deadlocks, acquire locks in a consistent order (for example, by account ID) and keep transactions short. Lock timeouts only limit waiting; they do not fix the design.

</details>

## Indexing and Performance

<details>
<summary>How is data stored in memory or on a disk?</summary>

Databases store tables and indexes in files divided into fixed-size **pages** (for example, 8 KB in PostgreSQL), each holding several rows or index entries. To read a row, the engine loads its page into a memory cache called the buffer pool. A cache hit avoids storage I/O; a miss reads the page from disk. Memory is fast but volatile, so changes are first recorded in a durable log and changed pages are written back to disk later.

</details>

<details>
<summary>How are indices formatted in a database?</summary>

An index is a separate data structure that maps key values to row locations. Common formats include:

- **B-tree:** a balanced tree that keeps keys sorted; the default in most engines, supporting equality, ranges and ordering.
- **Hash:** maps keys to buckets; suits equality lookups only.
- **Bitmap:** bitmaps marking which rows have each value; suits low-cardinality columns in read-heavy analytics.
- **Inverted (GIN, full-text):** maps terms or array elements to the rows containing them.

Indexes reduce the pages a query reads but add storage and work to every write.

</details>

<details>
<summary>What is the difference between a clustered and a non-clustered index?</summary>

A rowstore clustered index stores table rows in its leaf pages, logically ordered by its key. A nonclustered index is a separate structure with row locators or included data. Neither guarantees final query order or contiguous disk placement. Terminology and implementation differ by engine.

</details>

<details>
<summary>How can you improve the performance of a slow SQL query?</summary>

Start by measuring: run `EXPLAIN` (or `EXPLAIN ANALYZE`) and compare estimated with actual rows. Then:

- **Index the access pattern:** match indexes to the filters, joins and ordering the query uses.
- **Keep predicates sargable:** compare raw columns, for example a date range instead of `DATE(created_at) = ...`.
- **Avoid row multiplication:** aggregate before joining one-to-many tables.
- **Fetch less:** select only needed columns and paginate with keyset pagination rather than deep `OFFSET`.
- **Refresh statistics:** stale statistics after bulk changes cause poor plans.

Compare before and after on representative data.

</details>

<details>
<summary>How can index tuning be used to improve query performance in SQL?</summary>

Match indexes to measured filters, joins, and ordering. Inspect actual plans and representative parameter values, then compare latency, I/O, storage, and write overhead. Engine-specific advisors can suggest candidates, but their suggestions need workload validation.

</details>

<details>
<summary>What are some reasons for poor query performance in SQL?</summary>

Common causes include inefficient access paths, inaccurate row estimates, excessive result sizes, spills, blocking, and repeated application round trips. Inspect plans and wait information before changing the schema. Normalization, scalar functions, and temporary tables are not inherently the cause of slow queries.

</details>

## Distributed Databases

<details>
<summary>What is a distributed database, and what are its advantages and challenges?</summary>

A distributed database stores data across multiple servers or locations, often by sharding (splitting data) and replication (copying it).

- **Advantages:** more storage and throughput than one machine, fault tolerance through replicas, and lower latency when data is placed near its users.
- **Challenges:** keeping replicas consistent, handling network latency and partitions (the CAP trade-off), routing queries that span shards, and coordinating distributed transactions, for example with two-phase commit.

</details>

## SQL Practice Exercises

<details>
<summary>Given the `users` and `cities` tables, write a query to return the list of cities without any users.</summary>

A query to test your understanding of LEFT JOIN and INNER JOIN. Given the users table with columns id, name, and city_id, and the cities table with columns id and name, write a query to find cities without any users.

`cities` input:

| id | name |
| ---: | --- |
| 1 | Berlin |
| 2 | Rome |
| 3 | Paris |

`users` input:

| id | name | city_id |
| ---: | --- | ---: |
| 10 | Ana | 1 |
| 11 | Ben | 1 |
| 12 | Chiara | 2 |

```sql
SELECT
  cities.name
FROM
  cities
  LEFT JOIN users ON users.city_id = cities.id
WHERE
  users.id IS NULL
```

| name |
| --- |
| Paris |

</details>

<details>
<summary>Given the user transactions table, write a query to get the first purchase for each user.</summary>

Consider a transactions table with columns user_id, created_at, and product. Write a query to obtain the first purchase (i.e., the purchase with the minimum created_at value) for each user.

`transactions` input:

| user_id | created_at | product |
| ---: | --- | --- |
| 1 | 2025-01-02 10:00 | Book |
| 1 | 2025-01-05 09:00 | Mug |
| 2 | 2025-01-03 12:00 | Pen |
| 2 | 2025-01-04 08:00 | Bag |

```sql
SELECT
  t.user_id, t.created_at, t.product
FROM
  transactions AS t
  INNER JOIN (
    SELECT user_id, MIN(created_at) AS min_created_at
    FROM transactions
    GROUP BY user_id
  ) AS t1 ON (t.user_id = t1.user_id AND t.created_at = t1.min_created_at)
ORDER BY t.user_id
```

This returns all purchases tied for the earliest timestamp. To choose exactly one, use `ROW_NUMBER()` ordered by `created_at` and a unique transaction ID.

| user_id | created_at | product |
| ---: | --- | --- |
| 1 | 2025-01-02 10:00 | Book |
| 2 | 2025-01-03 12:00 | Pen |

</details>

<details>
<summary>Given the user transactions table, write a query to get the total purchases made in the morning (AM) versus afternoon/evening (PM) by day.</summary>

PostgreSQL example. Interpret `created_at` in the intended reporting timezone before grouping.

Using the transactions table with columns user_id, created_at, and product, write a query to compare total purchases made in the morning (AM) versus afternoon/evening (PM) by day.

`transactions` input (timestamps shown in the reporting timezone):

| user_id | created_at | product |
| ---: | --- | --- |
| 1 | 2025-02-01 09:30 | Book |
| 2 | 2025-02-01 13:10 | Mug |
| 3 | 2025-02-01 17:15 | Pen |
| 1 | 2025-02-02 08:45 | Bag |
| 2 | 2025-02-02 15:00 | Lamp |

```sql
SELECT
  DATE_TRUNC('day', created_at) AS date,
  CASE
    WHEN EXTRACT(HOUR FROM created_at) >= 12 THEN 'PM'
    ELSE 'AM'
  END AS time_of_day,
  COUNT(*)
FROM
  transactions
GROUP BY date, time_of_day
ORDER BY date, time_of_day
```

| date | time_of_day | count |
| --- | --- | ---: |
| 2025-02-01 00:00:00 | AM | 1 |
| 2025-02-01 00:00:00 | PM | 2 |
| 2025-02-02 00:00:00 | AM | 1 |
| 2025-02-02 00:00:00 | PM | 1 |

</details>

<details>
<summary>Write an SQL query that makes recommendations using the pages that your friends liked, without recommending pages you already like.</summary>

Assume you have two tables: usersAndFriends with columns user_id and friend, and usersLikedPages with columns user_id and page_id. Write a query that recommends pages liked by your friends, excluding pages you already like.

`usersAndFriends` input:

| user_id | friend |
| ---: | ---: |
| 1 | 2 |
| 1 | 3 |

`usersLikedPages` input:

| user_id | page_id |
| ---: | ---: |
| 1 | 10 |
| 2 | 10 |
| 2 | 20 |
| 3 | 30 |

```sql
SELECT DISTINCT
  uf.user_id, ulp.page_id
FROM
  usersAndFriends uf
  JOIN usersLikedPages ulp ON uf.friend = ulp.user_id
WHERE
  NOT EXISTS (
    SELECT 1
    FROM usersLikedPages
    WHERE user_id = uf.user_id AND page_id = ulp.page_id
  )
```

| user_id | page_id |
| ---: | ---: |
| 1 | 20 |
| 1 | 30 |

</details>

<details>
<summary>Write a query for the month-over-month percentage change in monthly active users.</summary>

PostgreSQL example. Counts users active at least once in each observed month, not the average daily active users. For a calendar with missing months, join to a complete month series before applying `LAG`.

Assume you have a logins table with columns user_id and date. Write a query to calculate the percentage change in monthly active users month over month.

`logins` input:

| user_id | date |
| ---: | --- |
| 1 | 2025-09-03 |
| 2 | 2025-09-20 |
| 1 | 2025-10-05 |
| 2 | 2025-10-12 |
| 3 | 2025-10-22 |
| 1 | 2025-11-08 |

```sql
WITH monthly_active_users AS (
  SELECT
    DATE_TRUNC('month', date) AS month,
    COUNT(DISTINCT user_id) AS active_users
  FROM
    logins
  GROUP BY month
),
monthly_change AS (
  SELECT
    month,
    active_users,
    LAG(active_users) OVER (ORDER BY month) AS prev_month_active_users
  FROM
    monthly_active_users
)
SELECT
  month,
  active_users,
  prev_month_active_users,
  ROUND(
    ((active_users - prev_month_active_users) * 100.0)
      / NULLIF(prev_month_active_users, 0),
    2
  ) AS percentage_change
FROM
  monthly_change
ORDER BY month;
```

| month | active_users | prev_month_active_users | percentage_change |
| --- | ---: | ---: | ---: |
| 2025-09-01 00:00:00 | 2 | NULL | NULL |
| 2025-10-01 00:00:00 | 3 | 2 | 50.00 |
| 2025-11-01 00:00:00 | 1 | 3 | -66.67 |

</details>
