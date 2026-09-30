# Database Review Quiz

Try answering each question before opening its answer. SQL exercises identify their dialect; syntax and guarantees vary between engines.

<details>
<summary>What is the purpose of a VIEW in a relational database?</summary>

A VIEW in a relational database is a virtual table based on the result set of a SELECT query. Views serve several purposes:
- **Simplify Complex Queries:** Views can encapsulate complex queries, making it easier for users to retrieve data without needing to understand the underlying query logic.
- **Customized Data Representation:** Views can present data in a specific format or structure that is more useful for certain applications or user needs.
- **Data Security:** Views can restrict access to specific columns or rows, ensuring that users see only the data they are authorized to view.
- **Data Abstraction:** Views provide a level of abstraction, hiding the complexity and details of the underlying database schema.

</details>

<details>
<summary>What is the difference between a database and a schema?</summary>

A schema can mean the logical design of tables and constraints or an engine-specific namespace. PostgreSQL and SQL Server allow multiple schemas inside a database. MySQL generally treats `SCHEMA` as a synonym for `DATABASE`; SQLite uses schema names for attached databases.

</details>

<details>
<summary>What is a stored procedure?</summary>

A stored procedure is a named routine executed by the database. It can accept parameters and contain SQL and procedural logic. Compilation and plan caching depend on the engine; a procedure is not automatically faster than equivalent parameterized SQL.

</details>

<details>
<summary>What is the purpose of the NULL value in SQL?</summary>

In SQL, the NULL value represents the absence of a value or an unknown value in a column. It is distinct from zero, an empty string, or any other default value. Handling NULLs requires special considerations in SQL queries because standard comparison operators (e.g., =, <, >) do not work with NULL values. Instead, SQL provides specific functions and keywords such as IS NULL and IS NOT NULL to manage NULLs effectively. NULL values are used to represent missing or undefined data.

</details>

<details>
<summary>What is the difference between a view and a materialized view?</summary>

- **View:** A view is a virtual table in SQL that is based on the result set of a SELECT query. It does not store the data physically; rather, it dynamically fetches data from the underlying tables whenever it is accessed. Views are useful for simplifying complex queries, providing security by restricting access to specific data, and presenting data in a specific format.
- **Materialized View:** A materialized view, on the other hand, is a physical copy of the result set of a query that is stored in the database. It can be refreshed periodically or on-demand to ensure data consistency. Materialized views improve query performance by providing precomputed results, at the cost of potentially having outdated data between refreshes.

</details>

<details>
<summary>What is the difference between the CHAR and VARCHAR data types?</summary>

- **CHAR:** The CHAR data type is used to store fixed-length character strings. When data is stored in a CHAR column, it always uses the defined length, padding with spaces if necessary. This makes CHAR efficient for storing data of a consistent length but can waste space when storing shorter strings.
- **VARCHAR:** The VARCHAR data type is used to store variable-length character strings. It only uses as much storage space as needed for the actual content plus a small overhead for storing the length of the string. VARCHAR is more flexible and space-efficient for data of varying lengths.

</details>

<details>
<summary>What is the difference between a unique constraint and a unique index?</summary>

- **Unique Constraint:** A unique constraint ensures that all values in one or more columns are unique across the table, preventing duplicate entries. It is primarily a logical constraint used for data integrity and is enforced by the database system.
- **Unique Index:** A unique index physically implements the unique constraint by creating an index that enforces uniqueness. Besides ensuring unique values, it also improves query performance by allowing faster searches and lookups on the indexed columns.

</details>

<details>
<summary>What is the difference between the UNION and JOIN operators?</summary>

- **UNION:** The UNION operator combines the result sets of two or more SELECT statements vertically, appending rows from each SELECT to the result set. It removes duplicate rows by default unless UNION ALL is used. UNION is useful for combining results from multiple queries with the same structure.
- **JOIN:** The JOIN operator combines columns from two or more tables horizontally based on a related column between them. Different types of joins (INNER JOIN, LEFT JOIN, RIGHT JOIN, etc.) determine how rows are matched and included in the result set. JOINS are used to retrieve related data from multiple tables in a single query.

</details>

<details>
<summary>What is the difference between a primary key and a candidate key?</summary>

A candidate key is a minimal set of attributes that uniquely identifies a row. The primary key is the candidate key selected as the main identifier. Other candidate keys are alternate keys. Adding unnecessary attributes to a candidate key makes it a superkey rather than another candidate key.

</details>

<details>
<summary>What is the purpose of the ROW_NUMBER() function?</summary>

The ROW_NUMBER() function in SQL assigns a unique sequential integer to each row within a result set. This function is often used for pagination, ranking, and assigning unique identifiers to rows. It helps in generating row numbers dynamically based on the order specified in the OVER clause, allowing for flexible and efficient row manipulation and analysis.

</details>

<details>
<summary>What is an ALIAS command?</summary>

An alias is a temporary query name, not a separate SQL command. For example, `SELECT u.name AS display_name FROM users AS u;` gives the table and output column aliases. Whether `AS` is optional or supported for table aliases depends on the dialect.

</details>

<details>
<summary>How is data stored in memory or on a disk?</summary>

Data storage varies depending on whether it is stored in memory (RAM) or on a disk (persistent storage):
- **In Memory:** Data is stored as binary information in the form of bits (0s and 1s). Memory storage uses structures like arrays, linked lists, and trees to organize data for quick access and manipulation. Memory is volatile, meaning data is lost when the power is turned off.
- **On Disk:** Data is stored persistently in files and folders within a specific file system format, such as NTFS, FAT32, or ext4. Disk storage uses sectors and tracks to organize data physically on the storage medium. Data management on disk involves addressing, organizing, and maintaining data to ensure efficient access and retrieval.

</details>

<details>
<summary>Are all columns keys?</summary>

No, not all columns in a database table are keys. A key is a column or a set of columns used to uniquely identify rows within a table. There are different types of keys, such as primary keys, foreign keys, and unique keys. While key columns are used for identification and establishing relationships between tables, many other columns contain non-unique data and serve other purposes, such as storing descriptive information.

</details>

<details>
<summary>Are all keys indexes?</summary>

No. Keys express logical rules; indexes are access structures. Engines commonly create indexes for primary and unique keys, but an index on the referencing side of a foreign key is engine-dependent. Non-unique indexes do not define candidate keys.

</details>

<details>
<summary>Why can there be only one primary key in a table?</summary>

SQL designates one candidate key as the primary key. Other candidate keys can remain as alternate keys enforced with required unique columns. The primary key can contain multiple columns; the one-primary-key convention does not imply that a row has only one possible identifier.

</details>

<details>
<summary>How does rolling back a transaction work?</summary>

Rollback undoes that transaction’s transactional changes, not concurrent commits by other transactions. Some effects, such as PostgreSQL sequence increments or external API calls, are not undone. DDL rollback behavior also depends on the engine.

</details>

<details>
<summary>How are indices formatted in a database?</summary>

Indices in a database are formatted as data structures that provide efficient access paths to rows in a table. Common formats include:
- **B-tree Indexes:** These are balanced tree structures that maintain sorted order of data, allowing quick searches, insertions, deletions, and sequential access.
- **Hash Indexes:** These use a hash function to map key values to specific locations, providing fast access for equality comparisons.
- **Bitmap Indexes:** These use bitmaps to represent the presence of values and are efficient for columns with a low number of distinct values.


  Indices are crucial for improving the performance of data retrieval operations by reducing the amount of data the database engine needs to scan.

</details>

<details>
<summary>How are prepared statements and meta commands stored and processed?</summary>

Prepared statements separate SQL structure from bound values; preparation and plan reuse depend on the driver and engine. Client meta-commands such as psql’s `\d` are interpreted by the client, which may issue SQL internally. They are not SQL schema-definition commands.

</details>

<details>
<summary>What are database constraints, and why do they matter?</summary>

Database constraints are rules applied to columns or tables to enforce data integrity and consistency. Common types of constraints include:
- **Primary Key Constraint:** Ensures each row in a table is uniquely identifiable.
- **Foreign Key Constraint:** Maintains referential integrity by ensuring a column's values match values in another table's primary key.
- **Unique Constraint:** Ensures all values in a column or set of columns are unique.
- **Check Constraint:** Enforces a condition that each row must satisfy.
- **Not Null Constraint:** Ensures a column cannot have NULL values.


  Constraints are crucial for maintaining the accuracy, reliability, and integrity of data within a database.

</details>

<details>
<summary>Is a table in a database dynamic or static?</summary>

A table in a database is dynamic because its contents can change over time through various operations such as insertions, updates, and deletions. Tables are designed to store and manage data in a structured format and are continuously modified to reflect new information, evolving requirements, and data maintenance activities. The schema or structure of the table can also change, adding to its dynamic nature.

</details>

<details>
<summary>What is SQL?</summary>

SQL, which stands for Structured Query Language, is a specialized programming language designed for managing and manipulating relational databases. It allows users to perform various operations such as querying data, updating records, creating and modifying database structures, and controlling access to the data. SQL is essential for interacting with databases and is widely used in data management and analysis.

</details>

<details>
<summary>What is a database?</summary>

A database is a systematic collection of data that is stored electronically and can be accessed, managed, and updated efficiently. Databases enable the storage, organization, and retrieval of large amounts of information. They can vary in complexity from simple text files to sophisticated systems that handle vast quantities of data and support complex queries and transactions. Databases are fundamental in various applications, including business, research, and technology.

</details>

<details>
<summary>What is the difference between a primary key and a foreign key?</summary>

- **Primary Key:** A primary key is a column or set of columns in a table that uniquely identifies each row. It enforces uniqueness and ensures that no two rows have the same primary key value. Primary keys cannot contain NULL values.
- **Foreign Key:** A foreign key is a column or set of columns in one table that references the primary key of another table. It establishes a relationship between the tables, ensuring referential integrity by enforcing that values in the foreign key column must match values in the referenced primary key column.

</details>

<details>
<summary>What is a database schema, and why is it important?</summary>

A database schema is the structured blueprint of a database, encompassing its tables, columns, relationships, indexes, and constraints. It defines how data is organized and the relationships between different parts of the data. A well-designed schema is crucial because it ensures data is stored efficiently, consistently, and securely. It also facilitates data retrieval and manipulation by providing a clear, logical structure, helping to enforce data integrity and improve query performance.

</details>

<details>
<summary>Can you explain the differences between Inner Join and Left Join in SQL?</summary>

- **Inner Join:** This type of join returns only the rows that have matching values in both tables. If there is no match, the row is excluded from the result set. Inner joins are used when you need to find records that have corresponding entries in both tables.
- **Left Join:** Also known as a Left Outer Join, this join returns all rows from the left table and the matched rows from the right table. If there are no matches in the right table, NULL values are returned for columns from the right table. Left joins are useful when you need to include all records from the left table regardless of whether they have matching rows in the right table.

</details>

<details>
<summary>What distinguishes WHERE and HAVING in SQL?</summary>

The **WHERE** and **HAVING** clauses are both used to filter records in SQL, but they are applied at different stages of query processing:
- **WHERE:** This clause is used to filter rows before any grouping or aggregation takes place. It applies to individual rows and is used to set conditions on the columns of the table.
- **HAVING:** This clause is used to filter groups after the grouping and aggregation have been performed. It applies to the aggregated data and is typically used in conjunction with the GROUP BY clause.

</details>

<details>
<summary>When should you use a subquery in SQL, and can you provide an example?</summary>

Subqueries, or nested queries, are used when you need to use the results of one query within another query. They are particularly useful for filtering or manipulating data based on intermediate results.


  Example: To find employees with salaries above the average salary, you can use a subquery as follows:
  <pre>`SELECT * FROM employees WHERE salary > (SELECT AVG(salary) FROM employees);`</pre>
  In this example, the subquery calculates the average salary, and the outer query selects employees whose salaries are greater than this average.

</details>

<details>
<summary>How can you improve the performance of a slow SQL query?</summary>

Several techniques can be used to improve the performance of a slow SQL query:
- **Proper Indexing:** Create indexes on columns that are frequently used in WHERE clauses, joins, and order by clauses to speed up data retrieval.
- **Optimize Joins:** Ensure that joins are based on indexed columns and consider using appropriate join types for the task.
- **Use LIMIT and OFFSET Clauses:** Limit the number of rows returned by a query to reduce the amount of data processed.
- **Avoid Unnecessary Columns:** Select only the columns you need rather than using SELECT * to reduce the amount of data processed and transferred.
- **Simplify Complex Queries:** Break down complex queries into simpler parts and use temporary tables or subqueries to manage intermediate results.

</details>

<details>
<summary>What is a relational database model, and why is it called "relational"?</summary>

A relational database model organizes data into tables (also called relations) composed of rows and columns. Each table represents a specific entity type, and rows within a table correspond to individual records of that entity. It is called "relational" because it emphasizes the relationships between tables through the use of keys (primary and foreign keys) and joins. These relationships allow for complex queries and data manipulation across multiple tables, maintaining data integrity and consistency.

</details>

<details>
<summary>Why are domain constraints important in a database?</summary>

Domain constraints define the permissible values for a given attribute, ensuring that data entered into the database is valid and consistent. They enforce rules such as data types, ranges, and formats. For example, a domain constraint on a date of birth field might ensure that the value is a valid date and not in the future. These constraints help maintain data integrity by preventing invalid data from being entered and ensuring that the data adheres to the specified rules and business logic.

</details>

<details>
<summary>Differentiate between base and derived relations in a relational database.</summary>

- **Base Relations:** Also known as base tables, these are the actual tables in a database that store the data. They are the primary structures for data storage and are defined by the database schema.
- **Derived Relations:** These are virtual tables created by querying one or more base relations. Derived relations are formed using operations like SELECT, JOIN, and UNION. Views are a common example of derived relations, as they do not store data physically but represent the results of a query applied to base tables.

</details>

<details>
<summary>Explain the two main principles of the relational database model and how they differ.</summary>

Data integrity and data independence are useful design goals rather than an exhaustive definition of the relational model. Integrity concerns valid data. Physical data independence separates logical relations from storage choices. The relational model represents data as relations and queries it through relational operations.

</details>

<details>
<summary>Why are stored procedures considered executable code in a database?</summary>

A stored procedure is a named routine executed by the database. It can accept parameters and contain SQL and procedural logic. Compilation and plan caching depend on the engine; a procedure is not automatically faster than equivalent parameterized SQL.

</details>

<details>
<summary>List some relational operations that can be performed on tables in a relational database.</summary>

Relational operations are fundamental for querying and manipulating data in a relational database. Some key relational operations include:
- **SELECT:** Retrieves specific rows from one or more tables based on a specified condition.
- **JOIN:** Combines rows from two or more tables based on a related column between them.
- **UNION:** Combines the result sets of two or more SELECT statements into a single result set, removing duplicates.
- **INTERSECT:** Returns the common rows from two SELECT statements.
- **DIFFERENCE (EXCEPT):** Returns rows from the first SELECT statement that are not present in the second SELECT statement.
- **PROJECT:** Selects specific columns from a table, effectively reducing the number of columns in the result set.
- **AGGREGATE Functions:** Performs calculations on a set of values to return a single value, including functions like COUNT, SUM, AVG, MIN, and MAX.

</details>

<details>
<summary>What is the difference between a clustered and a non-clustered index?</summary>

A rowstore clustered index stores table rows in its leaf pages, logically ordered by its key. A nonclustered index is a separate structure with row locators or included data. Neither guarantees final query order or contiguous disk placement. Terminology and implementation differ by engine.

</details>

<details>
<summary>What is normalization in the context of database design, and why is it important?</summary>

Normalization is the process of organizing a database to minimize data redundancy and ensure data integrity. This is achieved by dividing large tables into smaller, more focused tables and establishing relationships between them. The importance of normalization includes:
- **Data Redundancy Reduction:** Eliminates duplicate data, saving storage space and reducing the risk of data inconsistencies.
- **Data Integrity:** Ensures that data dependencies are logical and consistent, maintaining accuracy and reliability.
- **Improved Query Performance:** Smaller, well-structured tables can enhance query performance and make the database easier to maintain.
- **Ease of Maintenance:** Normalized databases are simpler to update and extend, reducing the complexity of database modifications.

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
<summary>Can you explain the concept of ACID properties in database systems?</summary>

ACID properties are a set of principles that ensure reliable database transactions, maintaining the integrity and consistency of the data. The ACID properties are:
- **Atomicity:** Ensures that a transaction is treated as a single unit of work. Either all operations within the transaction are completed successfully, or none are. This prevents partial updates to the database.
- **Consistency:** Ensures that a transaction brings the database from one valid state to another, maintaining the integrity of the database according to predefined rules and constraints.
- **Isolation:** Ensures that transactions are executed independently, preventing concurrent transactions from interfering with each other. This is achieved by managing locks and ensuring that intermediate transaction states are not visible to other transactions.
- **Durability:** Ensures that once a transaction is committed, its changes are permanent and will survive system failures. This is typically achieved through mechanisms like transaction logs and backups.

</details>

<details>
<summary>What is a transaction in a database, and why is it important?</summary>

A transaction is a sequence of one or more database operations (such as inserts, updates, and deletes) that are executed as a single unit of work. Transactions are important because they ensure data consistency and integrity by adhering to the ACID properties. This means that:
- All operations within a transaction are completed successfully, or none are, ensuring atomicity.
- The database remains in a consistent state before and after the transaction.
- Transactions are isolated from one another, preventing concurrent transactions from causing inconsistencies.
- Once committed, the changes made by a transaction are durable and survive system failures.

</details>

<details>
<summary>What is a trigger in a relational database?</summary>

A trigger is a set of SQL statements that automatically executes in response to certain events on a specified table or view, such as inserts, updates, or deletes. Triggers are used to enforce business rules, maintain data integrity, and automate system tasks. They can be defined to execute before or after the triggering event, and can also be nested, meaning one trigger can initiate another. Triggers are managed by the database management system (DBMS) and help maintain consistent and reliable data.

</details>

<details>
<summary>What is NOLOCK and how does it affect concurrency?</summary>

In SQL Server, `WITH (NOLOCK)` requests Read Uncommitted behavior for data reads. It can return dirty, missing, or duplicated data. It neither releases another transaction’s locks nor avoids every lock: schema stability locking still applies. Consider row-versioned isolation when correct nonblocking reads are needed.

</details>

<details>
<summary>How does the STUFF function differ from the REPLACE function in SQL?</summary>

The STUFF and REPLACE functions in SQL are used to manipulate strings, but they operate differently:
- **STUFF:** The STUFF function inserts a string into another string, replacing a specified number of characters. It is used to overwrite part of a string with another string starting at a specified position. For example, `STUFF('abcdef', 2, 3, '123')` results in 'a123ef'.
- **REPLACE:** The REPLACE function replaces all occurrences of a specified substring within a string with another substring. It applies to all instances of the target substring. For example, `REPLACE('abcdefabc', 'abc', '123')` results in '123def123'.


  STUFF is used for more targeted character modifications, while REPLACE applies globally to all specified instances in the string.

</details>

<details>
<summary>What are self joins and cross joins in SQL?</summary>

A self join is used to join a table to itself, often using aliases to avoid confusion. It is useful for hierarchical data structures like reporting relationships. A cross join returns the Cartesian product of two tables, combining every row from one table with every row from the other.

</details>

<details>
<summary>What is the difference between the IN and EXISTS operators?</summary>

`IN` compares a value with a set; `EXISTS` tests whether a subquery returns any row. Optimizers can produce similar plans for equivalent forms, so neither is universally faster. `NOT IN` can evaluate to unknown if the subquery contains a null; correlated `NOT EXISTS` is often clearer for anti-joins.

</details>

<details>
<summary>Given the `users` and `cities` tables, write a query to return the list of cities without any users.</summary>

A query to test your understanding of LEFT JOIN and INNER JOIN. Given the users table with columns id, name, and city_id, and the cities table with columns id and name, write a query to find cities without any users.

```sql
SELECT
  cities.name
FROM
  cities
  LEFT JOIN users ON users.city_id = cities.id
WHERE
  users.id IS NULL
```

</details>

<details>
<summary>What is the RANK function in SQL?</summary>

The RANK function assigns a rank to each row returned by a SELECT statement based on a specified column. Rows with equal values receive the same rank, and the rank is determined by the row's position in the result set, not the row's sequential number.

</details>

<details>
<summary>What is the difference between a cross join and an inner join?</summary>

- **Cross Join:** A cross join produces the Cartesian product of the two tables involved, meaning it returns all possible combinations of rows from the tables. It does not require any condition and is rarely used except for specific cases where all combinations are needed.
- **Inner Join:** An inner join returns only the rows where there is a match between the tables based on a specified condition (usually a key column). It is one of the most commonly used joins, as it filters out unmatched rows, providing meaningful combined results from the related tables.

</details>

<details>
<summary>What is the purpose of the CASE statement?</summary>

The CASE statement in SQL is used to perform conditional logic and return different values based on specified conditions within a query. It works similarly to an if-else construct in programming languages. The CASE statement allows for more readable and flexible queries by enabling conditional output, making it useful for transforming data, handling multiple conditions, and creating calculated columns.

</details>

<details>
<summary>What are cursors in SQL and when are they useful?</summary>

A cursor exposes a query result for incremental fetching or row-by-row processing. Some procedural tasks need this, but set-based SQL often avoids repeated operations. Cursor types and lifecycle are engine-specific; Oracle’s implicit/explicit distinction should not be presented as SQL Server’s universal taxonomy.

</details>

<details>
<summary>What are the similarities and differences between TRUNCATE and DELETE commands in SQL?</summary>

`DELETE` can filter rows with `WHERE`; `TRUNCATE` removes the whole table’s data using an engine-specific bulk operation. Logging, identity resets, triggers, and rollback differ. PostgreSQL and SQL Server can roll back a transactional `TRUNCATE`; MySQL `TRUNCATE` implicitly commits. PostgreSQL also supports `TRUNCATE` triggers.

</details>

<details>
<summary>What are COMMIT and ROLLBACK commands in SQL?</summary>

COMMIT is used to permanently save changes made by a transaction, while ROLLBACK is used to undo changes made by a transaction. COMMIT makes the transaction irreversible, and ROLLBACK allows for data recovery if needed.

</details>

<details>
<summary>What is the difference between UNION and UNION ALL?</summary>

Both UNION and UNION ALL are SQL operations used to combine the result sets of two or more SELECT statements into a single result set. The key difference is how they handle duplicate rows:
- **UNION:** Combines the results of the SELECT statements and removes any duplicate rows, ensuring that each row in the final result set is unique.
- **UNION ALL:** Combines the results of the SELECT statements without removing duplicates, so the final result set may contain duplicate rows.

</details>

<details>
<summary>What is the difference between a temporary table and a table variable?</summary>

In SQL Server, temporary tables and table variables both can use tempdb; a table variable is not inherently memory-only. They differ in scope, statistics, and optimization behavior. Performance depends on row counts, queries, and version; benchmark rather than assuming table variables are faster.

</details>

<details>
<summary>What is the purpose of the GROUP BY clause?</summary>

The GROUP BY clause in SQL is used to arrange identical data into groups based on one or more columns. It is commonly used with aggregate functions such as SUM, AVG, COUNT, MIN, and MAX to perform operations on each group of data. This clause helps in summarizing and analyzing data by dividing it into manageable groups, facilitating easier reporting and data analysis.

</details>

<details>
<summary>What is a distributed database, and what are its advantages and challenges?</summary>

A distributed database is a database that is stored across multiple servers or locations, often geographically dispersed. Advantages of distributed databases include improved performance and availability, as well as increased fault tolerance and data redundancy. Challenges include managing data consistency and integrity across multiple nodes, handling network latency and partitioning, and implementing complex distributed algorithms for transaction management, replication, and concurrency control.

</details>

<details>
<summary>Given the user transactions table, write a query to get the first purchase for each user.</summary>

Consider a transactions table with columns user_id, created_at, and product. Write a query to obtain the first purchase (i.e., the purchase with the minimum created_at value) for each user.

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
```

This returns all purchases tied for the earliest timestamp. To choose exactly one, use `ROW_NUMBER()` ordered by `created_at` and a unique transaction ID.

</details>

<details>
<summary>What is a database transaction log, and why is it important?</summary>

A database transaction log is a record of all modifications made to a database, including data changes, schema changes, and other transactions. It is important because it provides a mechanism for recovering data in case of system failures or user errors, allows for point-in-time recovery, and aids in maintaining data consistency and integrity by ensuring that transactions adhere to the ACID properties. Transaction logs can also be used for replication and auditing purposes.

</details>

<details>
<summary>What is the difference between correlated and nested subqueries in SQL?</summary>

A subquery is nested inside another query. A correlated subquery additionally references an outer query’s columns. It is logically evaluated in the outer-row context, but the optimizer can decorrelate it; do not infer a fixed number of physical executions from the syntax.

</details>

<details>
<summary>How do UNION, MINUS, UNION ALL, and INTERSECT differ in SQL?</summary>

INTERSECT returns distinct rows common to both SELECT queries. MINUS returns distinct rows from the first query not found in the second query. UNION returns all distinct rows from either query. UNION ALL returns all rows from both queries, including duplicates.

</details>

<details>
<summary>What is a join in SQL, and what are the different types?</summary>

A join in SQL is used to retrieve data from multiple tables by referencing columns or rows between them. Types of joins include: JOIN (returns rows with matching data in both tables), LEFT JOIN (returns all rows from the left table and matching rows from the right table), RIGHT JOIN (returns all rows from the right table and matching rows from the left table), and FULL JOIN (returns rows with matching data in either table).

</details>

<details>
<summary>What are DDL, DML, and DCL in SQL?</summary>

DDL (Data Definition Language) commands deal with database schemas and data structure, e.g., CREATE TABLE or ALTER TABLE. DML (Data Manipulation Language) commands handle data manipulation, e.g., SELECT, INSERT. DCL (Data Control Language) commands manage rights and permissions on the database, e.g., GRANT, REVOKE.

</details>

<details>
<summary>What are some common types of database management systems (DBMS), and how do they differ?</summary>

Some common types of DBMS include relational (e.g., MySQL, PostgreSQL, SQL Server), NoSQL (e.g., MongoDB, Couchbase, Cassandra), and in-memory (e.g., Redis, Memcached). Relational DBMS use tables and SQL for data storage and manipulation, emphasizing data consistency and relationships. NoSQL DBMS offer more flexible data models and are designed for handling unstructured or semi-structured data, often providing horizontal scaling and high availability. In-memory DBMS store data in memory rather than on disk, offering extremely fast data access and manipulation but typically having limited data persistence capabilities.

</details>

<details>
<summary>What is the difference between the EXISTS and NOT EXISTS operators?</summary>

The EXISTS and NOT EXISTS operators in SQL are used to test for the existence of rows returned by a subquery:
- **EXISTS:** The EXISTS operator returns TRUE if the subquery returns one or more rows. It is often used in correlated subqueries to check for the presence of related data.
- **NOT EXISTS:** The NOT EXISTS operator returns TRUE if the subquery returns no rows. It is useful for ensuring that certain data does not exist in a related table.


  Both operators are used to improve query performance by allowing early termination of the subquery evaluation when a match is found (or not found).

</details>

<details>
<summary>How can index tuning be used to improve query performance in SQL?</summary>

Match indexes to measured filters, joins, and ordering. Inspect actual plans and representative parameter values, then compare latency, I/O, storage, and write overhead. Engine-specific advisors can suggest candidates, but their suggestions need workload validation.

</details>

<details>
<summary>What are some reasons for poor query performance in SQL?</summary>

Common causes include inefficient access paths, inaccurate row estimates, excessive result sizes, spills, blocking, and repeated application round trips. Inspect plans and wait information before changing the schema. Normalization, scalar functions, and temporary tables are not inherently the cause of slow queries.

</details>

<details>
<summary>Given the user transactions table, write a query to get the total purchases made in the morning (AM) versus afternoon/evening (PM) by day.</summary>

PostgreSQL example. Interpret `created_at` in the intended reporting timezone before grouping.

Using the transactions table with columns user_id, created_at, and product, write a query to compare total purchases made in the morning (AM) versus afternoon/evening (PM) by day.

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
```

</details>

<details>
<summary>In databases, what are the meanings of the terms "entities" and "attributes"?</summary>

Entities are objects or concepts represented in a database, and attributes are the properties or characteristics of those entities.

</details>

<details>
<summary>Write an SQL query that makes recommendations using the pages that your friends liked, without recommending pages you already like.</summary>

Assume you have two tables: usersAndFriends with columns user_id and friend, and usersLikedPages with columns user_id and page_id. Write a query that recommends pages liked by your friends, excluding pages you already like.

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

</details>

<details>
<summary>What is a deadlock in a database, and how can it be resolved?</summary>

A deadlock occurs when two or more transactions are waiting for each other to release a resource, causing a circular dependency that prevents any of the transactions from proceeding. Deadlocks can be resolved by implementing timeouts, setting a lock hierarchy to prevent circular dependencies, using optimistic concurrency control, or using a deadlock detection algorithm to identify and break the deadlock by rolling back one of the transactions.

</details>

<details>
<summary>Write a query for the month-over-month percentage change in monthly active users.</summary>

PostgreSQL example. Counts users active at least once in each observed month, not the average daily active users. For a calendar with missing months, join to a complete month series before applying `LAG`.

Assume you have a logins table with columns user_id and date. Write a query to calculate the percentage change in monthly active users month over month.

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
((active_users - prev_month_active_users) * 100.0) / NULLIF(prev_month_active_users, 0),
2
) AS percentage_change
FROM
monthly_change
ORDER BY month;
```

</details>

<details>
<summary>What is the purpose of the CASCADE DELETE constraint?</summary>

The CASCADE DELETE constraint in SQL ensures that when a row in a parent table is deleted, all related rows in the child tables are automatically deleted as well. This constraint maintains referential integrity by ensuring that no orphaned rows exist in the child tables. CASCADE DELETE is useful for managing dependent data and simplifying the deletion of related records.

</details>

<details>
<summary>What is a self-join?</summary>

A self-join is a join operation where a table is joined with itself. This type of join is useful when you need to compare rows within the same table or query hierarchical data. For example, a self-join can be used to find relationships between rows in a table, such as employees and their managers within the same employee table. The self-join is achieved by using table aliases to distinguish between the different instances of the table.

</details>
