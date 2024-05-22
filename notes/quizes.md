<details>
  <summary>What is the purpose of a VIEW in a relational database?</summary><br>
  A VIEW in a relational database is a virtual table based on the result set of a SELECT query. Views serve several purposes:
  <ul>
    <li><strong>Simplify Complex Queries:</strong> Views can encapsulate complex queries, making it easier for users to retrieve data without needing to understand the underlying query logic.</li>
    <li><strong>Customized Data Representation:</strong> Views can present data in a specific format or structure that is more useful for certain applications or user needs.</li>
    <li><strong>Data Security:</strong> Views can restrict access to specific columns or rows, ensuring that users see only the data they are authorized to view.</li>
    <li><strong>Data Abstraction:</strong> Views provide a level of abstraction, hiding the complexity and details of the underlying database schema.</li>
  </ul>
</details>

<details>
  <summary>What is the difference between a database and a schema?</summary><br>
  <ul>
    <li><strong>Database:</strong> A database is a comprehensive container that includes a collection of related data and objects, such as tables, views, indexes, and procedures. It serves as the main organizational structure for storing and managing data.</li>
    <li><strong>Schema:</strong> A schema is a subset within a database that groups database objects and defines their ownership. It provides a logical grouping of objects and helps in managing and organizing the database structure, often used to enforce security and access control.</li>
  </ul>
</details>


<details>
  <summary>What is a stored procedure?</summary><br>
  A stored procedure is a precompiled set of SQL statements that are stored in the database. Stored procedures can be executed repeatedly, improving performance by reducing the need for repeated parsing and compilation of SQL statements. They also promote code reuse and consistency, as they can encapsulate complex logic and operations that can be reused across multiple applications or user requests.
</details>

<details>
  <summary>What is the purpose of the NULL value in SQL?</summary><br>
  In SQL, the NULL value represents the absence of a value or an unknown value in a column. It is distinct from zero, an empty string, or any other default value. Handling NULLs requires special considerations in SQL queries because standard comparison operators (e.g., =, <, >) do not work with NULL values. Instead, SQL provides specific functions and keywords such as IS NULL and IS NOT NULL to manage NULLs effectively. NULL values are used to represent missing or undefined data.
</details>

<details>
  <summary>What is the difference between a view and a materialized view?</summary><br>
  <ul>
    <li><strong>View:</strong> A view is a virtual table in SQL that is based on the result set of a SELECT query. It does not store the data physically; rather, it dynamically fetches data from the underlying tables whenever it is accessed. Views are useful for simplifying complex queries, providing security by restricting access to specific data, and presenting data in a specific format.</li>
    <li><strong>Materialized View:</strong> A materialized view, on the other hand, is a physical copy of the result set of a query that is stored in the database. It can be refreshed periodically or on-demand to ensure data consistency. Materialized views improve query performance by providing precomputed results, at the cost of potentially having outdated data between refreshes.</li>
  </ul>
</details>

<details>
  <summary>What is the difference between the CHAR and VARCHAR data types?</summary><br>
  <ul>
    <li><strong>CHAR:</strong> The CHAR data type is used to store fixed-length character strings. When data is stored in a CHAR column, it always uses the defined length, padding with spaces if necessary. This makes CHAR efficient for storing data of a consistent length but can waste space when storing shorter strings.</li>
    <li><strong>VARCHAR:</strong> The VARCHAR data type is used to store variable-length character strings. It only uses as much storage space as needed for the actual content plus a small overhead for storing the length of the string. VARCHAR is more flexible and space-efficient for data of varying lengths.</li>
  </ul>
</details>


<details>
  <summary>What is the difference between a unique constraint and a unique index?</summary><br>
  <ul>
    <li><strong>Unique Constraint:</strong> A unique constraint ensures that all values in one or more columns are unique across the table, preventing duplicate entries. It is primarily a logical constraint used for data integrity and is enforced by the database system.</li>
    <li><strong>Unique Index:</strong> A unique index physically implements the unique constraint by creating an index that enforces uniqueness. Besides ensuring unique values, it also improves query performance by allowing faster searches and lookups on the indexed columns.</li>
  </ul>
</details>

<details>
  <summary>What is the difference between the UNION and JOIN operators?</summary><br>
  <ul>
    <li><strong>UNION:</strong> The UNION operator combines the result sets of two or more SELECT statements vertically, appending rows from each SELECT to the result set. It removes duplicate rows by default unless UNION ALL is used. UNION is useful for combining results from multiple queries with the same structure.</li>
    <li><strong>JOIN:</strong> The JOIN operator combines columns from two or more tables horizontally based on a related column between them. Different types of joins (INNER JOIN, LEFT JOIN, RIGHT JOIN, etc.) determine how rows are matched and included in the result set. JOINS are used to retrieve related data from multiple tables in a single query.</li>
  </ul>
</details>

<details>
  <summary>What is the difference between a primary key and a candidate key?</summary><br>
  <ul>
    <li><strong>Primary Key:</strong> A primary key is a unique identifier for each row in a table. It is a chosen candidate key that ensures each row is uniquely identifiable. A table can have only one primary key, and it enforces uniqueness and not-null constraints on the key columns.</li>
    <li><strong>Candidate Key:</strong> A candidate key is any column or combination of columns that can uniquely identify rows in a table. There can be multiple candidate keys in a table, but only one can be chosen as the primary key. All candidate keys are potential primary keys, and they ensure the uniqueness of rows.</li>
  </ul>
</details>

<details>
  <summary>What is the purpose of the ROW_NUMBER() function?</summary><br>
  The ROW_NUMBER() function in SQL assigns a unique sequential integer to each row within a result set. This function is often used for pagination, ranking, and assigning unique identifiers to rows. It helps in generating row numbers dynamically based on the order specified in the OVER clause, allowing for flexible and efficient row manipulation and analysis.
</details>

<details>
  <summary>What is an ALIAS command?</summary><br>
  The ALIAS command in SQL allows you to assign a temporary name to a table or column within a query. This alias can simplify query syntax and improve readability. Aliases are defined using the AS keyword, though the AS keyword is optional in many SQL implementations. For example:
  <ul>
    <li>Column Alias: <code>SELECT column_name AS alias_name FROM table_name;</code></li>
    <li>Table Alias: <code>SELECT t.column_name FROM table_name AS t;</code></li>
  </ul>
  Aliases are especially useful in complex queries involving multiple tables and subqueries.
</details>

<details>
  <summary>How is data stored in memory or on a disk?</summary><br>
  Data storage varies depending on whether it is stored in memory (RAM) or on a disk (persistent storage):
  <ul>
    <li><strong>In Memory:</strong> Data is stored as binary information in the form of bits (0s and 1s). Memory storage uses structures like arrays, linked lists, and trees to organize data for quick access and manipulation. Memory is volatile, meaning data is lost when the power is turned off.</li>
    <li><strong>On Disk:</strong> Data is stored persistently in files and folders within a specific file system format, such as NTFS, FAT32, or ext4. Disk storage uses sectors and tracks to organize data physically on the storage medium. Data management on disk involves addressing, organizing, and maintaining data to ensure efficient access and retrieval.</li>
  </ul>
</details>

<details>
  <summary>Are all columns keys?</summary><br>
  No, not all columns in a database table are keys. A key is a column or a set of columns used to uniquely identify rows within a table. There are different types of keys, such as primary keys, foreign keys, and unique keys. While key columns are used for identification and establishing relationships between tables, many other columns contain non-unique data and serve other purposes, such as storing descriptive information.
</details>

<details>
  <summary>Are all keys indexes?</summary><br>
  Not necessarily. While keys are often indexed to improve the speed of data retrieval operations, not all keys are required to be indexes. Indexes are additional data structures that provide quick access to rows based on the indexed columns. However, some keys, especially those not frequently used in search operations, may not be indexed to save on storage space and maintenance overhead. Indexing decisions depend on the specific database design and performance requirements.
</details>

<details>
  <summary>Why can there be only one primary key in a table?</summary><br>
  There can be only one primary key in a table because its primary purpose is to uniquely identify each record in the table. The primary key enforces uniqueness and non-null constraints on the designated columns, ensuring that no two rows have the same primary key value. Allowing more than one primary key would create ambiguity and redundancy, undermining the integrity and consistency of the database. However, a table can have multiple candidate keys, but only one can be chosen as the primary key.
</details>

<details>
  <summary>How does rolling back a transaction work?</summary><br>
  Rolling back a transaction involves undoing all changes made during the transaction and returning the database to its state before the transaction began. This process is typically initiated in response to errors, data inconsistencies, or when certain conditions are not met within the transaction. By rolling back, the database maintains data integrity and consistency, ensuring that only valid data is committed. Rollbacks are essential for error handling and maintaining the ACID (Atomicity, Consistency, Isolation, Durability) properties of transactions.
</details>

<details>
  <summary>How are indices formatted in a database?</summary><br>
  Indices in a database are formatted as data structures that provide efficient access paths to rows in a table. Common formats include:
  <ul>
    <li><strong>B-tree Indexes:</strong> These are balanced tree structures that maintain sorted order of data, allowing quick searches, insertions, deletions, and sequential access.</li>
    <li><strong>Hash Indexes:</strong> These use a hash function to map key values to specific locations, providing fast access for equality comparisons.</li>
    <li><strong>Bitmap Indexes:</strong> These use bitmaps to represent the presence of values and are efficient for columns with a low number of distinct values.</li>
  </ul>
  Indices are crucial for improving the performance of data retrieval operations by reducing the amount of data the database engine needs to scan.
</details>

<details>
  <summary>How are prepared statements and meta commands stored and processed?</summary><br>
  <ul>
    <li><strong>Prepared Statements:</strong> These are precompiled SQL queries with placeholders for parameters. When a prepared statement is created, the SQL engine parses, compiles, and optimizes the query, storing the execution plan. When executed, only the parameter values are sent, reducing parsing and compiling overhead. This approach improves performance and security by preventing SQL injection attacks.</li>
    <li><strong>Meta Commands:</strong> Meta commands are used to manage and configure the database system, such as creating or altering tables, indexes, and users. These commands are processed by the database management system (DBMS) and typically involve changes to the database schema or administrative tasks rather than data manipulation.</li>
  </ul>
</details>

<details>
  <summary>What is a view in SQL?</summary><br>
  A view in SQL is a virtual table that represents the result of a predefined query on one or more tables. Views do not store data physically; instead, they dynamically generate data when accessed. Views simplify complex queries, enhance security by restricting access to specific data, and present data in a customized format. They are useful for abstracting the underlying table structures and providing a consistent interface for users and applications.
</details>

<details>
  <summary>What are database constraints, and why do they matter?</summary><br>
  Database constraints are rules applied to columns or tables to enforce data integrity and consistency. Common types of constraints include:
  <ul>
    <li><strong>Primary Key Constraint:</strong> Ensures each row in a table is uniquely identifiable.</li>
    <li><strong>Foreign Key Constraint:</strong> Maintains referential integrity by ensuring a column's values match values in another table's primary key.</li>
    <li><strong>Unique Constraint:</strong> Ensures all values in a column or set of columns are unique.</li>
    <li><strong>Check Constraint:</strong> Enforces a condition that each row must satisfy.</li>
    <li><strong>Not Null Constraint:</strong> Ensures a column cannot have NULL values.</li>
  </ul>
  Constraints are crucial for maintaining the accuracy, reliability, and integrity of data within a database.
</details>

<details>
  <summary>Is a table in a database dynamic or static?</summary><br>
  A table in a database is dynamic because its contents can change over time through various operations such as insertions, updates, and deletions. Tables are designed to store and manage data in a structured format and are continuously modified to reflect new information, evolving requirements, and data maintenance activities. The schema or structure of the table can also change, adding to its dynamic nature.
</details>

<details>
  <summary>What is SQL?</summary><br>
  SQL, which stands for Structured Query Language, is a specialized programming language designed for managing and manipulating relational databases. It allows users to perform various operations such as querying data, updating records, creating and modifying database structures, and controlling access to the data. SQL is essential for interacting with databases and is widely used in data management and analysis.
</details>

<details>
  <summary>What is a database?</summary><br>
  A database is a systematic collection of data that is stored electronically and can be accessed, managed, and updated efficiently. Databases enable the storage, organization, and retrieval of large amounts of information. They can vary in complexity from simple text files to sophisticated systems that handle vast quantities of data and support complex queries and transactions. Databases are fundamental in various applications, including business, research, and technology.
</details>


<details>
  <summary>What is the difference between a primary key and a foreign key?</summary><br>
  <ul>
    <li><strong>Primary Key:</strong> A primary key is a column or set of columns in a table that uniquely identifies each row. It enforces uniqueness and ensures that no two rows have the same primary key value. Primary keys cannot contain NULL values.</li>
    <li><strong>Foreign Key:</strong> A foreign key is a column or set of columns in one table that references the primary key of another table. It establishes a relationship between the tables, ensuring referential integrity by enforcing that values in the foreign key column must match values in the referenced primary key column.</li>
  </ul>
</details>

<details>
  <summary>What are the main differences between primary and foreign keys in a database?</summary><br>
  The main differences between primary and foreign keys are:
  <ul>
    <li><strong>Primary Key:</strong> Uniquely identifies a row within its own table, enforcing uniqueness and not allowing NULL values.</li>
    <li><strong>Foreign Key:</strong> Establishes a link between two tables by referencing the primary key in another table, ensuring referential integrity but allowing duplicate and NULL values unless otherwise constrained.</li>
  </ul>
  Primary keys ensure each record is uniquely identifiable within its table, while foreign keys create relationships between tables.
</details>

<details>
  <summary>What is a database schema, and why is it important?</summary><br>
  A database schema is the structured blueprint of a database, encompassing its tables, columns, relationships, indexes, and constraints. It defines how data is organized and the relationships between different parts of the data. A well-designed schema is crucial because it ensures data is stored efficiently, consistently, and securely. It also facilitates data retrieval and manipulation by providing a clear, logical structure, helping to enforce data integrity and improve query performance.
</details>

<details>
  <summary>Can you explain the differences between Inner Join and Left Join in SQL?</summary><br>
  <ul>
    <li><strong>Inner Join:</strong> This type of join returns only the rows that have matching values in both tables. If there is no match, the row is excluded from the result set. Inner joins are used when you need to find records that have corresponding entries in both tables.
    </li>
    <li><strong>Left Join:</strong> Also known as a Left Outer Join, this join returns all rows from the left table and the matched rows from the right table. If there are no matches in the right table, NULL values are returned for columns from the right table. Left joins are useful when you need to include all records from the left table regardless of whether they have matching rows in the right table.</li>
  </ul>
</details>

<details>
  <summary>What distinguishes WHERE and HAVING in SQL?</summary><br>
  The <strong>WHERE</strong> and <strong>HAVING</strong> clauses are both used to filter records in SQL, but they are applied at different stages of query processing:
  <ul>
    <li><strong>WHERE:</strong> This clause is used to filter rows before any grouping or aggregation takes place. It applies to individual rows and is used to set conditions on the columns of the table.</li>
    <li><strong>HAVING:</strong> This clause is used to filter groups after the grouping and aggregation have been performed. It applies to the aggregated data and is typically used in conjunction with the GROUP BY clause.</li>
  </ul>
</details>

<details>
  <summary>When should you use a subquery in SQL, and can you provide an example?</summary><br>
  Subqueries, or nested queries, are used when you need to use the results of one query within another query. They are particularly useful for filtering or manipulating data based on intermediate results. 
  <br><br>
  Example: To find employees with salaries above the average salary, you can use a subquery as follows:
  <pre><code>SELECT * FROM employees WHERE salary > (SELECT AVG(salary) FROM employees);</code></pre>
  In this example, the subquery calculates the average salary, and the outer query selects employees whose salaries are greater than this average.
</details>

<details>
  <summary>How can you improve the performance of a slow SQL query?</summary><br>
  Several techniques can be used to improve the performance of a slow SQL query:
  <ul>
    <li><strong>Proper Indexing:</strong> Create indexes on columns that are frequently used in WHERE clauses, joins, and order by clauses to speed up data retrieval.</li>
    <li><strong>Optimize Joins:</strong> Ensure that joins are based on indexed columns and consider using appropriate join types for the task.</li>
    <li><strong>Use LIMIT and OFFSET Clauses:</strong> Limit the number of rows returned by a query to reduce the amount of data processed.</li>
    <li><strong>Avoid Unnecessary Columns:</strong> Select only the columns you need rather than using SELECT * to reduce the amount of data processed and transferred.</li>
    <li><strong>Simplify Complex Queries:</strong> Break down complex queries into simpler parts and use temporary tables or subqueries to manage intermediate results.</li>
  </ul>
</details>

<details>
  <summary>What is a relational database model, and why is it called "relational"?</summary><br>
  A relational database model organizes data into tables (also called relations) composed of rows and columns. Each table represents a specific entity type, and rows within a table correspond to individual records of that entity. It is called "relational" because it emphasizes the relationships between tables through the use of keys (primary and foreign keys) and joins. These relationships allow for complex queries and data manipulation across multiple tables, maintaining data integrity and consistency.
</details>

<details>
  <summary>Why are domain constraints important in a database?</summary><br>
  Domain constraints define the permissible values for a given attribute, ensuring that data entered into the database is valid and consistent. They enforce rules such as data types, ranges, and formats. For example, a domain constraint on a date of birth field might ensure that the value is a valid date and not in the future. These constraints help maintain data integrity by preventing invalid data from being entered and ensuring that the data adheres to the specified rules and business logic.
</details>

<details>
  <summary>Differentiate between base and derived relations in a relational database.</summary><br>
  <ul>
    <li><strong>Base Relations:</strong> Also known as base tables, these are the actual tables in a database that store the data. They are the primary structures for data storage and are defined by the database schema.</li>
    <li><strong>Derived Relations:</strong> These are virtual tables created by querying one or more base relations. Derived relations are formed using operations like SELECT, JOIN, and UNION. Views are a common example of derived relations, as they do not store data physically but represent the results of a query applied to base tables.</li>
  </ul>
</details>

<details>
  <summary>Explain the two main principles of the relational database model and how they differ.</summary><br>
  The two main principles of the relational database model are:
  <ul>
    <li><strong>Data Integrity:</strong> Ensures that data is accurate, consistent, and reliable. It is maintained through constraints, keys, and rules that enforce valid data entry and relationships between tables. Data integrity prevents errors and inconsistencies within the database.</li>
    <li><strong>Data Independence:</strong> Allows changes to the physical storage of data without affecting the logical structure of the database. It separates the way data is stored from how it is accessed, enabling the database to evolve and scale without disrupting applications and users. Data independence is achieved through abstraction layers and the use of schemas.</li>
  </ul>
  While data integrity focuses on the correctness and reliability of the data, data independence emphasizes the flexibility and adaptability of the database structure.
</details>

<details>
  <summary>Why are stored procedures considered executable code in a database?</summary><br>
  Stored procedures are precompiled collections of SQL statements and optional control-of-flow statements stored under a name and processed as a unit. They can be executed repeatedly with different parameters. Stored procedures are considered executable code because they encapsulate complex logic, can perform various operations (such as data manipulation, control flow, and error handling), and are executed directly by the database engine. They improve performance by reducing the need for repeated parsing and compilation and enhance code reusability and maintainability.
</details>

<details>
  <summary>List some relational operations that can be performed on tables in a relational database.</summary><br>
  Relational operations are fundamental for querying and manipulating data in a relational database. Some key relational operations include:
  <ul>
    <li><strong>SELECT:</strong> Retrieves specific rows from one or more tables based on a specified condition.</li>
    <li><strong>JOIN:</strong> Combines rows from two or more tables based on a related column between them.</li>
    <li><strong>UNION:</strong> Combines the result sets of two or more SELECT statements into a single result set, removing duplicates.</li>
    <li><strong>INTERSECT:</strong> Returns the common rows from two SELECT statements.</li>
    <li><strong>DIFFERENCE (EXCEPT):</strong> Returns rows from the first SELECT statement that are not present in the second SELECT statement.</li>
    <li><strong>PROJECT:</strong> Selects specific columns from a table, effectively reducing the number of columns in the result set.</li>
    <li><strong>AGGREGATE Functions:</strong> Performs calculations on a set of values to return a single value, including functions like COUNT, SUM, AVG, MIN, and MAX.</li>
  </ul>
</details>

<details>
  <summary>What is the difference between a clustered and a non-clustered index?</summary><br>
  <ul>
    <li><strong>Clustered Index:</strong> A clustered index sorts and stores the data rows in the table based on the index key. There can be only one clustered index per table, as the data rows themselves can be sorted in only one order. It significantly affects the physical storage of the data on disk.</li>
    <li><strong>Non-Clustered Index:</strong> A non-clustered index creates a separate structure that contains the index key values and pointers to the physical data rows. This index does not alter the physical order of the data within the table. A table can have multiple non-clustered indexes, providing various paths to access the data efficiently.</li>
  </ul>
</details>

<details>
  <summary>What is normalization in the context of database design, and why is it important?</summary><br>
  Normalization is the process of organizing a database to minimize data redundancy and ensure data integrity. This is achieved by dividing large tables into smaller, more focused tables and establishing relationships between them. The importance of normalization includes:
  <ul>
    <li><strong>Data Redundancy Reduction:</strong> Eliminates duplicate data, saving storage space and reducing the risk of data inconsistencies.</li>
    <li><strong>Data Integrity:</strong> Ensures that data dependencies are logical and consistent, maintaining accuracy and reliability.</li>
    <li><strong>Improved Query Performance:</strong> Smaller, well-structured tables can enhance query performance and make the database easier to maintain.</li>
    <li><strong>Ease of Maintenance:</strong> Normalized databases are simpler to update and extend, reducing the complexity of database modifications.</li>
  </ul>
</details>

<details>
  <summary>What are the advantages of using stored procedures in a database?</summary><br>
  Stored procedures offer several advantages in a database environment:
  <ul>
    <li><strong>Performance Improvement:</strong> Stored procedures are precompiled, reducing the overhead of parsing and compiling SQL statements for each execution.</li>
    <li><strong>Reduced Network Traffic:</strong> Executing stored procedures reduces the amount of data transmitted between the database server and client by encapsulating multiple operations in a single call.</li>
    <li><strong>Code Reuse:</strong> Encapsulating complex logic in stored procedures promotes code reuse and simplifies maintenance.</li>
    <li><strong>Enhanced Security:</strong> Stored procedures can restrict direct access to data and enforce security measures by controlling user access to specific procedures.</li>
    <li><strong>Consistency:</strong> Centralizing business logic in stored procedures ensures that consistent operations are performed across different applications.</li>
  </ul>
</details>

<details>
  <summary>Can you explain the concept of ACID properties in database systems?</summary><br>
  ACID properties are a set of principles that ensure reliable database transactions, maintaining the integrity and consistency of the data. The ACID properties are:
  <ul>
    <li><strong>Atomicity:</strong> Ensures that a transaction is treated as a single unit of work. Either all operations within the transaction are completed successfully, or none are. This prevents partial updates to the database.</li>
    <li><strong>Consistency:</strong> Ensures that a transaction brings the database from one valid state to another, maintaining the integrity of the database according to predefined rules and constraints.</li>
    <li><strong>Isolation:</strong> Ensures that transactions are executed independently, preventing concurrent transactions from interfering with each other. This is achieved by managing locks and ensuring that intermediate transaction states are not visible to other transactions.</li>
    <li><strong>Durability:</strong> Ensures that once a transaction is committed, its changes are permanent and will survive system failures. This is typically achieved through mechanisms like transaction logs and backups.</li>
  </ul>
</details>

<details>
  <summary>What is a transaction in a database, and why is it important?</summary><br>
  A transaction is a sequence of one or more database operations (such as inserts, updates, and deletes) that are executed as a single unit of work. Transactions are important because they ensure data consistency and integrity by adhering to the ACID properties. This means that:
  <ul>
    <li>All operations within a transaction are completed successfully, or none are, ensuring atomicity.</li>
    <li>The database remains in a consistent state before and after the transaction.</li>
    <li>Transactions are isolated from one another, preventing concurrent transactions from causing inconsistencies.</li>
    <li>Once committed, the changes made by a transaction are durable and survive system failures.</li>
  </ul>
</details>

<details>
  <summary>What is a trigger in a relational database?</summary><br>
  A trigger is a set of SQL statements that automatically executes in response to certain events on a specified table or view, such as inserts, updates, or deletes. Triggers are used to enforce business rules, maintain data integrity, and automate system tasks. They can be defined to execute before or after the triggering event, and can also be nested, meaning one trigger can initiate another. Triggers are managed by the database management system (DBMS) and help maintain consistent and reliable data.
</details>

<details>
  <summary>What is NOLOCK and how does it affect concurrency?</summary><br>
  NOLOCK is a query hint in SQL that allows a SELECT statement to read data without acquiring shared locks. This can improve concurrency on a busy system by allowing multiple read operations to occur simultaneously without blocking writes. However, using NOLOCK can lead to dirty reads, where a query reads uncommitted data that might be rolled back. While NOLOCK reduces blocking and improves access to data, it should be used with caution due to the risk of reading inconsistent or incorrect data.
</details>

<details>
  <summary>How does the STUFF function differ from the REPLACE function in SQL?</summary><br>
  The STUFF and REPLACE functions in SQL are used to manipulate strings, but they operate differently:
  <ul>
    <li><strong>STUFF:</strong> The STUFF function inserts a string into another string, replacing a specified number of characters. It is used to overwrite part of a string with another string starting at a specified position. For example, <code>STUFF('abcdef', 2, 3, '123')</code> results in 'a123ef'.</li>
    <li><strong>REPLACE:</strong> The REPLACE function replaces all occurrences of a specified substring within a string with another substring. It applies to all instances of the target substring. For example, <code>REPLACE('abcdefabc', 'abc', '123')</code> results in '123def123'.</li>
  </ul>
  STUFF is used for more targeted character modifications, while REPLACE applies globally to all specified instances in the string.
</details>

<details>
<summary>What are self joins and cross joins in SQL?</summary>
A self join is used to join a table to itself, often using aliases to avoid confusion. It is useful for hierarchical data structures like reporting relationships. A cross join returns the Cartesian product of two tables, combining every row from one table with every row from the other.
</details>

<details>
  <summary>What is the difference between the IN and EXISTS operators?</summary><br>
  <ul>
    <li><strong>IN:</strong> The IN operator is used to check if a value exists within a specified set of values or the result of a subquery. It is typically used with a list of static values or a subquery that returns a single column. IN is straightforward but can be less efficient for large data sets.</li>
    <li><strong>EXISTS:</strong> The EXISTS operator checks for the existence of rows returned by a subquery. It returns TRUE if the subquery returns one or more rows, and FALSE otherwise. EXISTS is often more efficient than IN for large data sets or complex subqueries because it stops processing as soon as a match is found.</li>
  </ul>
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
  <summary>What is the difference between a cross join and an inner join?</summary><br>
  <ul>
    <li><strong>Cross Join:</strong> A cross join produces the Cartesian product of the two tables involved, meaning it returns all possible combinations of rows from the tables. It does not require any condition and is rarely used except for specific cases where all combinations are needed.</li>
    <li><strong>Inner Join:</strong> An inner join returns only the rows where there is a match between the tables based on a specified condition (usually a key column). It is one of the most commonly used joins, as it filters out unmatched rows, providing meaningful combined results from the related tables.</li>
  </ul>
</details>

<details>
  <summary>What is the purpose of the CASE statement?</summary><br>
  The CASE statement in SQL is used to perform conditional logic and return different values based on specified conditions within a query. It works similarly to an if-else construct in programming languages. The CASE statement allows for more readable and flexible queries by enabling conditional output, making it useful for transforming data, handling multiple conditions, and creating calculated columns.
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
  <summary>What is the difference between UNION and UNION ALL?</summary><br>
  Both UNION and UNION ALL are SQL operations used to combine the result sets of two or more SELECT statements into a single result set. The key difference is how they handle duplicate rows:
  <ul>
    <li><strong>UNION:</strong> Combines the results of the SELECT statements and removes any duplicate rows, ensuring that each row in the final result set is unique.</li>
    <li><strong>UNION ALL:</strong> Combines the results of the SELECT statements without removing duplicates, so the final result set may contain duplicate rows.</li>
  </ul>
</details>

<details>
  <summary>What is the difference between a temporary table and a table variable?</summary><br>
  <ul>
    <li><strong>Temporary Table:</strong> A temporary table is a database table that exists temporarily and is available only for the duration of a session or transaction. It is stored in the tempdb database and can be explicitly dropped or automatically dropped when the session ends.</li>
    <li><strong>Table Variable:</strong> A table variable is a variable that holds a table-like structure in memory and has a limited scope within a batch, stored procedure, or function. It is faster for small datasets and is automatically deallocated when its scope ends.</li>
  </ul>
</details>

<details>
  <summary>What is the purpose of the GROUP BY clause?</summary><br>
  The GROUP BY clause in SQL is used to arrange identical data into groups based on one or more columns. It is commonly used with aggregate functions such as SUM, AVG, COUNT, MIN, and MAX to perform operations on each group of data. This clause helps in summarizing and analyzing data by dividing it into manageable groups, facilitating easier reporting and data analysis.
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
  <summary>What is the difference between the EXISTS and NOT EXISTS operators?</summary><br>
  The EXISTS and NOT EXISTS operators in SQL are used to test for the existence of rows returned by a subquery:
  <ul>
    <li><strong>EXISTS:</strong> The EXISTS operator returns TRUE if the subquery returns one or more rows. It is often used in correlated subqueries to check for the presence of related data.</li>
    <li><strong>NOT EXISTS:</strong> The NOT EXISTS operator returns TRUE if the subquery returns no rows. It is useful for ensuring that certain data does not exist in a related table.</li>
  </ul>
  Both operators are used to improve query performance by allowing early termination of the subquery evaluation when a match is found (or not found).
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

<details>
  <summary>What is the purpose of the CASCADE DELETE constraint?</summary><br>
  The CASCADE DELETE constraint in SQL ensures that when a row in a parent table is deleted, all related rows in the child tables are automatically deleted as well. This constraint maintains referential integrity by ensuring that no orphaned rows exist in the child tables. CASCADE DELETE is useful for managing dependent data and simplifying the deletion of related records.
</details>

<details>
  <summary>What is a self-join?</summary><br>
  A self-join is a join operation where a table is joined with itself. This type of join is useful when you need to compare rows within the same table or query hierarchical data. For example, a self-join can be used to find relationships between rows in a table, such as employees and their managers within the same employee table. The self-join is achieved by using table aliases to distinguish between the different instances of the table.
</details>

