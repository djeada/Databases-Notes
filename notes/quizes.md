<details>
<summary>How is data stored in memory or on a disk?</summary><br>
Data is stored in memory as binary information in the form of bits (0s and 1s). In memory, data is stored in structures like arrays, linked lists, and trees. On a disk, data is stored in files and folders with a specific file system format such as NTFS, FAT32, or ext4. Data storage involves addressing, organizing, and managing the data for efficient access and retrieval.
</details>

<details>
<summary>Why can there be only one primary key in a table?</summary><br>
There can be only one primary key in a table because its purpose is to uniquely identify each record in the table. A primary key consists of one or more columns, and its values must be unique and not null. Having more than one primary key would be redundant and could lead to data inconsistency.
</details>

<details>
<summary>How does rolling back a transaction work?</summary><br>
Rolling back a transaction means undoing all the changes made during the transaction and returning the database to its previous state before the transaction began. This is typically done in case of errors, data inconsistencies, or when the transaction fails to meet certain conditions. Rolling back helps maintain the consistency and integrity of the data in the database.
</details>

<details>
<summary>How are indices formatted in a database?</summary><br>
Indices in a database are formatted as data structures, such as B-trees or hash indexes, that store a mapping between the values of a specific column or columns and the corresponding rows in the table. Indices are designed to improve the performance of data retrieval operations by allowing the database system to find and access the desired data more quickly.
</details>

<details>
<summary>How are prepared statements and meta commands stored and processed?</summary><br>
Prepared statements are precompiled SQL queries with placeholders for parameter values. They are stored as separate objects in the database and are processed by the database engine when executed. Prepared statements help improve performance and security by reducing the overhead of parsing and compiling the SQL query multiple times and by preventing SQL injection attacks. Meta commands, on the other hand, are commands used to manage the database system itself, such as creating or modifying tables and indexes. They are usually processed by the database management system rather than the database engine.
</details>

<details>
<summary>What is a view in SQL?</summary><br>
A view in SQL is a virtual table that represents the result of a stored query on one or more tables. Views are not physically stored in the database but are generated on-the-fly when accessed. They provide a way to simplify complex queries, restrict access to sensitive data, or present data in a specific format without modifying the underlying tables.
</details>


<details>
<summary>What are database constraints, and why do they matter?</summary>
Database constraints are rules that enforce data consistency and integrity, ensuring that the database remains accurate and reliable.
</details>

<details>
<summary>Is a table in a database dynamic or static?</summary><br>
A table in a database is dynamic because its contents can change over time as new data is inserted, updated, or deleted. Tables are designed to store and manage data in a structured format and can be modified to adapt to changing requirements or data.
</details>

<details>
<summary>What is the difference between a primary key and a foreign key?</summary><br>
A primary key is a unique identifier for each row in a table, ensuring that no two rows have the same primary key value. A foreign key, on the other hand, is a column or set of columns in one table that refers to the primary key of another table. Foreign keys help establish relationships between tables and maintain referential integrity in a relational database.
</details>

<details>
<summary> What are the main differences between primary and foreign keys in a database?</summary>
A primary key uniquely identifies a row in a table, while a foreign key establishes a relationship between tables by referencing the primary key of another table.
</details>

<details>
<summary>What is a database schema, and why is it important?</summary><br>
A database schema is the structure and organization of a database, including tables, columns, relationships, and constraints. It is important because it provides a blueprint for the organization of the data, ensuring that data is stored efficiently, consistently, and securely. A well-designed schema also facilitates data retrieval and manipulation by providing a clear and logical structure for the database.
</details>

<details>
<summary>Can you explain the differences between Inner Join and Left Join in SQL?</summary>
Inner Join returns only the rows that have matching values in both tables, while Left Join returns all rows from the left table and the matched rows from the right table, filling in NULL values for non-matching rows.
</details>

<details>
<summary>What distinguishes WHERE and HAVING in SQL?</summary>
WHERE is used to filter rows before the grouping and aggregation occurs, while HAVING is used to filter the results of aggregated data after the GROUP BY clause.
</details>

<details>
<summary>When should you use a subquery in SQL, and can you provide an example?</summary>
Subqueries are used when a query depends on the results of another query, often to filter or manipulate data based on intermediate results. Example: SELECT * FROM employees WHERE salary > (SELECT AVG(salary) FROM employees);
</details>

<details>
<summary> How can you improve the performance of a slow SQL query?</summary>
You can improve performance by using proper indexing, optimizing joins, using LIMIT and OFFSET clauses, avoiding unnecessary columns in SELECT, and breaking down complex queries into simpler parts.
</details>

<details>
<summary>What is a relational database model, and why is it called "relational"?</summary>
A relational database model organizes data into tables (relations) with rows and columns, and it is called "relational" because it emphasizes the relationships between tables through keys and joins.
</details>

<details>
<summary>Why are domain constraints important in a database?</summary>
Domain constraints define the valid values for an attribute, ensuring data consistency and integrity within the database.
</details>

<details>
<summary>Differentiate between base and derived relations in a relational database.</summary>
Base relations are tables that store actual data, while derived relations are tables formed from other relations using operations like SELECT, JOIN, or UNION.
</details>

<details>
<summary>Explain the two main principles of the relational database model and how they differ.</summary>
The two main principles are data integrity (ensuring data is accurate and consistent) and data independence (allowing the physical storage of data to change without affecting the logical structure).
</details>

<details>
<summary>Why are stored procedures considered executable code in a database?</summary>
Stored procedures are precompiled SQL statements that can be executed multiple times with different parameters, improving performance and reusability of complex logic.
</details>

<details>
<summary>What is the role of an index in a relational database model?</summary>
An index speeds up data retrieval by providing a more efficient way to look up rows in a table based on specific column values.
</details>

<details>
<summary>List some relational operations that can be performed on tables in a relational database.</summary>
Some relational operations include SELECT, JOIN, UNION, INTERSECT, DIFFERENCE, PROJECT, and AGGREGATE functions like COUNT, SUM, AVG, MIN, and MAX.
</details>

<details>
<summary>What is the purpose of a VIEW in a relational database?</summary>
A VIEW is a virtual table based on the result of a SELECT query, which allows you to simplify complex queries, provide a customized view of data, and enhance data security by restricting access to specific columns or rows.
</details>

<details>
<summary>What is normalization in the context of database design, and why is it important?</summary>
Normalization is the process of organizing a database to minimize data redundancy and improve data integrity by dividing tables into smaller, more focused tables and establishing relationships between them.
</details>

<details>
<summary>What are the advantages of using stored procedures in a database?</summary>
Stored procedures can reduce network traffic and latency, improve application performance, allow for code reuse, encapsulate logic, and provide better data security.
</details>

<details>
<summary>Can you explain the concept of ACID properties in database systems?</summary>
ACID properties (Atomicity, Consistency, Isolation, and Durability) are a set of principles that ensure reliable database transactions, maintaining the integrity and consistency of the data.
</details>

<details>
<summary>What is a transaction in a database, and why is it important?</summary>
A transaction is a sequence of one or more operations (e.g., insert, update, delete) that are executed as a single unit of work. Transactions ensure data consistency and integrity by adhering to the ACID properties.
</details>

<details>
<summary>What is a trigger in a relational database?</summary>
A trigger is an automatic action that occurs in response to a specific event, such as insert, update, or delete, on a particular table. Triggers help maintain referential integrity and are managed by the DBMS. They can be nested, allowing one trigger to initiate other triggers.
</details>

<details>
<summary>What is NOLOCK and how does it affect concurrency?</summary>
NOLOCK is used to enhance concurrency on a busy system by allowing SELECT statements to read data without acquiring locks. This can lead to dirty reads when data is being updated simultaneously, but it reduces blocking and allows for greater access to the data.
</details>

<details>
<summary>How does the STUFF function differ from the REPLACE function in SQL?</summary>
The STUFF function overwrites specified characters of a string, while the REPLACE function replaces all occurrences of a specified character with a new character. STUFF allows for more targeted character modifications, whereas REPLACE applies to all instances of the specified character.
</details>

<details>
<summary>What are self joins and cross joins in SQL?</summary>
A self join is used to join a table to itself, often using aliases to avoid confusion. It is useful for hierarchical data structures like reporting relationships. A cross join returns the Cartesian product of two tables, combining every row from one table with every row from the other.
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
<summary>What are cursors in SQL and when are they useful?</summary>
Cursors are memory work areas used to perform row-by-row operations when set-based operations are not possible. There are two types of cursors: implicit cursors, managed automatically by SQL Server, and explicit cursors, declared and managed by the programmer for row-by-row operations on result sets with more than one row.
</details>

<details>
<summary>What are the similarities and differences between TRUNCATE and DELETE commands in SQL?</summary>
Both TRUNCATE and DELETE remove data from a table without affecting the table structure. TRUNCATE is a DDL command and faster than DELETE, as it doesn't store data in rollback space, but it can't execute triggers or use a WHERE clause. DELETE is a DML command that can execute triggers and use a WHERE clause but is slower because it stores data in rollback space.
</details>

<details>
<summary>What are COMMIT and ROLLBACK commands in SQL?</summary>
COMMIT is used to permanently save changes made by a transaction, while ROLLBACK is used to undo changes made by a transaction. COMMIT makes the transaction irreversible, and ROLLBACK allows for data recovery if needed.
</details>

<details>
<summary>What is a distributed database, and what are its advantages and challenges?</summary><br>
A distributed database is a database that is stored across multiple servers or locations, often geographically dispersed. Advantages of distributed databases include improved performance and availability, as well as increased fault tolerance and data redundancy. Challenges include managing data consistency and integrity across multiple nodes, handling network latency and partitioning, and implementing complex distributed algorithms for transaction management, replication, and concurrency control.
</details>

<details>
<summary>What is WITH(NOLOCK) in SQL?</summary>
WITH(NOLOCK) is used to unlock data locked by uncommitted transactions, allowing SELECT statements to read the data. It is similar to READ UNCOMMITTED and is used when data is already released by committed transactions.
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
</details>

<details>
<summary>What is a database transaction log, and why is it important?</summary><br>
A database transaction log is a record of all modifications made to a database, including data changes, schema changes, and other transactions. It is important because it provides a mechanism for recovering data in case of system failures or user errors, allows for point-in-time recovery, and aids in maintaining data consistency and integrity by ensuring that transactions adhere to the ACID properties. Transaction logs can also be used for replication and auditing purposes.
</details>

<details>
<summary>What is the difference between correlated and nested subqueries in SQL?</summary>
Correlated subqueries execute once for each row selected by the outer query, with a reference to a value from that row. Nested subqueries execute only once for the entire outer query and don't contain any reference to the outer query row.
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
<summary>What are some common types of database management systems (DBMS), and how do they differ?</summary><br>
Some common types of DBMS include relational (e.g., MySQL, PostgreSQL, SQL Server), NoSQL (e.g., MongoDB, Couchbase, Cassandra), and in-memory (e.g., Redis, Memcached). Relational DBMS use tables and SQL for data storage and manipulation, emphasizing data consistency and relationships. NoSQL DBMS offer more flexible data models and are designed for handling unstructured or semi-structured data, often providing horizontal scaling and high availability. In-memory DBMS store data in memory rather than on disk, offering extremely fast data access and manipulation but typically having limited data persistence capabilities.
</details>

<details>
<summary>How can index tuning be used to improve query performance in SQL?</summary>
Index tuning improves query performance by using the Index Tuning Wizard to analyze and optimize query performance based on workload. It recommends the best usage of indexes, analyzes changes in index usage and query distribution, and suggests database tuning for problematic queries.
</details>

<details>
<summary>What are some reasons for poor query performance in SQL?</summary>
Possible reasons include: lack of indexes, excessive stored procedure recompilations, not using SET NOCOUNT ON in procedures and triggers, poorly written queries, highly normalized database design, overuse of cursors and temporary tables, non-optimal predicate usage, queries with built-in or scalar-valued functions, and queries joining columns using arithmetic or string concatenation operators.
</details>

<details>
<summary>Given the user transactions table, write a query to get the total purchases made in the morning (AM) versus afternoon/evening (PM) by day.</summary>

Using the transactions table with columns user_id, created_at, and product, write a query to compare total purchases made in the morning (AM) versus afternoon/evening (PM) by day.

```sql
SELECT
  DATE_TRUNC('day', created_at) AS date,
  CASE 
    WHEN HOUR(created_at) > 11 THEN 'PM'
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
<summary>What is the difference between clustered and non-clustered indexes in a database?</summary><br>
A clustered index determines the physical order of data storage in a table and can have only one per table. It is more efficient for retrieving data in the order of the clustered index. A non-clustered index creates a separate index structure that stores a reference to the data in the table, allowing multiple non-clustered indexes per table. Non-clustered indexes are useful for retrieving data based on specific columns that are not included in the clustered index.
</details>

<details>
<summary>Write an SQL query that makes recommendations using the pages that your friends liked, without recommending pages you already like.</summary>

Assume you have two tables: usersAndFriends with columns user_id and friend, and usersLikedPages with columns user_id and page_id. Write a query that recommends pages liked by your friends, excluding pages you already like.

```sql
SELECT DISTINCT
  uf.friend, ulp.page_id
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
<summary>What is a deadlock in a database, and how can it be resolved?</summary><br>
A deadlock occurs when two or more transactions are waiting for each other to release a resource, causing a circular dependency that prevents any of the transactions from proceeding. Deadlocks can be resolved by implementing timeouts, setting a lock hierarchy to prevent circular dependencies, using optimistic concurrency control, or using a deadlock detection algorithm to identify and break the deadlock by rolling back one of the transactions.
</details>

<details>
<summary>Write an SQL query that shows percentage change month over month in daily active users.</summary>

Assume you have a logins table with columns user_id and date. Write a query to calculate the percentage change in daily active users month over month.

```sql

WITH daily_active_users AS (
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
    daily_active_users
)
SELECT
  month,
  active_users,
prev_month_active_users,
ROUND(
((active_users - prev_month_active_users) * 100.0) / prev_month_active_users,
2
) AS percentage_change
FROM
monthly_change
ORDER BY month;
```
  
</details>
