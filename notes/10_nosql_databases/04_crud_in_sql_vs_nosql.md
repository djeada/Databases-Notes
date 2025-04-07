## CRUD in SQL vs NoSQL

Comparing common CRUD operations in SQL (relational databases) and MongoDB (a NoSQL document store) provides valuable insights into the differences between relational and non-relational databases. Understanding these differences is crucial for developers and database administrators when designing and implementing data storage solutions tailored to specific application requirements.

After reading the material, you should be able to answer the following questions:

- What does CRUD stand for, and why are these operations fundamental in database management?
- How are data structures organized differently in SQL (relational databases) compared to MongoDB (a NoSQL document store)?
- What are the SQL and MongoDB syntax and methods for performing Create, Read, Update, and Delete operations?
- What are the differences between performing CRUD operations in SQL and MongoDB, particularly regarding schema flexibility and data relationships?
- When should you choose a SQL database over MongoDB, and vice versa, based on application requirements and data integrity needs?

### Overview

- **CRUD** stands for Create, Read, Update, and Delete, which are the four basic operations for data manipulation. These operations form the foundation of interacting with databases, enabling users to manage and manipulate data effectively.
- In **SQL** (Structured Query Language) databases, data is organized in tables with fixed schemas. This means that each table has a predefined structure, and all records within the table adhere to this structure. This rigidity ensures data integrity and consistency, making SQL databases ideal for applications requiring complex transactions and reliable data consistency.
- **MongoDB**, on the other hand, is a NoSQL (Not Only SQL) document store that stores data in flexible, JSON-like documents. This flexibility allows for varying structures within the same collection, enabling developers to iterate quickly and handle unstructured or semi-structured data more efficiently. MongoDB is well-suited for applications that require scalability and rapid development cycles.

### CRUD Operations Comparison

Understanding how CRUD operations are implemented in both SQL and MongoDB highlights the practical differences in data manipulation between relational and non-relational databases. Below is an in-depth comparison of each CRUD operation.

#### Create

**SQL: Inserting New Records**

In SQL databases, adding new records to a table is performed using the `INSERT INTO` statement. This operation requires specifying the table name, the columns where data will be inserted, and the corresponding values. The fixed schema ensures that the data conforms to the table's structure, maintaining consistency across all records.

**SQL Syntax:**

```sql
INSERT INTO table_name (column1, column2, ...) VALUES (value1, value2, ...);
```

**SQL Example:**

```sql
INSERT INTO users (first_name, last_name, age) VALUES ('John', 'Doe', 25);
```

This statement adds a new user with the first name "John," last name "Doe," and age 25 to the `users` table.

**MongoDB: Inserting Documents**

In MongoDB, new data is added to a collection using the `insertOne` or `insertMany` methods. Unlike SQL tables, MongoDB collections do not enforce a fixed schema, allowing each document to have a different structure. This flexibility is advantageous for applications that require dynamic data models.

**MongoDB Syntax:**

```javascript
db.collection.insertOne(document);
```

**MongoDB Example:**

```javascript
db.users.insertOne({ first_name: 'John', last_name: 'Doe', age: 25 });
```

This command inserts a new document into the `users` collection with the specified fields and values.

- **Schema flexibility** differs between the two; SQL enforces predefined schemas, ensuring strict structure and data consistency, while MongoDB supports dynamic schemas, allowing documents in the same collection to have different structures.  
- **Bulk inserts** are supported by both systems, with SQL using constructs like `INSERT INTO ... VALUES (...), (...);` and MongoDB utilizing `insertMany`. MongoDB’s approach is often simpler when inserting a large number of documents, especially if their structures vary.

#### Read

**SQL: Retrieving Data with SELECT**

The `SELECT` statement in SQL is used to retrieve data from one or more tables. It allows for precise querying through the use of conditions, joins, and projections, enabling users to extract exactly the data they need.

**SQL Syntax:**

```sql
SELECT column1, column2, ... FROM table_name WHERE condition;
```

**SQL Example:**

```sql
SELECT first_name, last_name, age FROM users WHERE age = 25;
```

This query retrieves the `first_name`, `last_name`, and `age` of all users in the `users` table who are 25 years old.

**MongoDB: Querying Documents with find**

In MongoDB, the `find` method is used to retrieve documents from a collection that match a specified query. The method also supports projections, allowing users to specify which fields to include or exclude in the returned documents.

**MongoDB Syntax:**

```javascript
db.collection.find(query, projection);
```

**MongoDB Example:**

```javascript
db.users.find({ age: 25 }, { first_name: 1, last_name: 1, age: 1, _id: 0 });
```

This command retrieves all documents from the `users` collection where the `age` is 25, including only the `first_name`, `last_name`, and `age` fields while excluding the `_id` field.

- In **SQL**, joins are used to combine data from multiple tables, an important feature for handling normalized data structures. Conversely, MongoDB promotes embedding related data within documents, which eliminates the need for joins and can improve read performance in specific scenarios.  
- MongoDB’s **aggregation framework** enables advanced data processing and transformation within the database, offering functionality comparable to SQL's `GROUP BY` and `HAVING` clauses for summarizing and filtering data.

#### Update

**SQL: Modifying Existing Records with UPDATE**

The `UPDATE` statement in SQL is used to modify existing records in a table. It requires specifying the table to update, the columns to change, and the new values, along with conditions to target specific records.

**SQL Syntax:**

```sql
UPDATE table_name SET column1 = value1, column2 = value2, ... WHERE condition;
```
  
**SQL Example:**
  
```sql
UPDATE users SET age = 26 WHERE first_name = 'John' AND last_name = 'Doe';
```

This statement updates the `age` of the user named "John Doe" to 26 in the `users` table.

**MongoDB: Updating Documents with updateOne/updateMany**

In MongoDB, the `updateOne` and `updateMany` methods are used to modify existing documents within a collection. These methods allow for atomic updates and support a variety of update operators to manipulate document fields.

**MongoDB Syntax:**

```javascript
db.collection.updateOne(filter, update);
db.collection.updateMany(filter, update);
```

**MongoDB Example:**

```javascript
db.users.updateOne(
  { first_name: 'John', last_name: 'Doe' },
  { $set: { age: 26 } }
);
```

This command updates the `age` field to 26 for the first document in the `users` collection where `first_name` is "John" and `last_name` is "Doe."

- **Atomicity** is supported in both SQL and MongoDB, ensuring that single operations either fully succeed or fail. MongoDB provides more granular control over atomic updates at the field level within a document, which can simplify certain use cases.  
- A variety of **update operators** in MongoDB, such as `$set` for updating specific fields, `$unset` for removing fields, `$inc` for incrementing numeric values, and `$push` for adding elements to arrays, enable efficient and expressive data modifications. Achieving similar functionality in SQL often requires more verbose queries or additional logic.

#### Delete

**SQL: Removing Records with DELETE**

The `DELETE FROM` statement in SQL is used to remove records from a table based on specified conditions. It's a straightforward operation but must be used with caution to avoid unintended data loss.

**SQL Syntax:**

```sql
DELETE FROM table_name WHERE condition;
```
  
**SQL Example:**

```sql
DELETE FROM users WHERE first_name = 'John' AND last_name = 'Doe';
```

This statement deletes all records from the `users` table where the `first_name` is "John" and the `last_name` is "Doe."

**MongoDB: Deleting Documents with deleteOne/deleteMany**

MongoDB provides the `deleteOne` and `deleteMany` methods to remove documents from a collection. These methods allow for precise targeting of documents to delete based on filter criteria.

**MongoDB Syntax:**

```javascript
db.collection.deleteOne(filter);
db.collection.deleteMany(filter);
```

**MongoDB Example:**

```javascript
db.users.deleteOne({ first_name: 'John', last_name: 'Doe' });
```
 
This command deletes the first document in the `users` collection that matches the criteria where `first_name` is "John" and `last_name` is "Doe."

- In **SQL**, cascade deletes are handled via foreign key constraints, automatically deleting related records in other tables when a parent record is removed. MongoDB lacks built-in cascade delete functionality, requiring developers to implement such behavior manually or via application logic.  
- **Soft deletes** are easier to implement in MongoDB because its flexible schema allows adding a `deleted` flag or similar field without altering existing structure. In SQL, soft deletes require additional columns and explicit handling in queries to filter out logically deleted records.

### CRUD Operations Table

The table below provides a concise comparison of CRUD operations between SQL and MongoDB, highlighting their syntax and examples to facilitate quick reference and understanding.

| Operation | SQL Syntax | SQL Example | MongoDB Syntax | MongoDB Example |
|-----------|------------|-------------|----------------|------------------|
| **Create** | `INSERT INTO table_name (columns) VALUES (values);` | `INSERT INTO users (first_name, last_name, age) VALUES ('John', 'Doe', 25);` | `db.collection.insertOne(document);` | `db.users.insertOne({ first_name: 'John', last_name: 'Doe', age: 25 });` |
| **Read** | `SELECT columns FROM table_name WHERE condition;` | `SELECT first_name, last_name, age FROM users WHERE age = 25;` | `db.collection.find(query, projection);` | `db.users.find({ age: 25 }, { first_name: 1, last_name: 1, age: 1, _id: 0 });` |
| **Update** | `UPDATE table_name SET column = value WHERE condition;` | `UPDATE users SET age = 26 WHERE first_name = 'John' AND last_name = 'Doe';` | `db.collection.updateOne(filter, update);` | `db.users.updateOne({ first_name: 'John', last_name: 'Doe' }, { $set: { age: 26 } });` |
| **Delete** | `DELETE FROM table_name WHERE condition;` | `DELETE FROM users WHERE first_name = 'John' AND last_name = 'Doe';` | `db.collection.deleteOne(filter);` | `db.users.deleteOne({ first_name: 'John', last_name: 'Doe' });` |

- In **MongoDB projections**, the second parameter of the `find` method, called `projection`, determines which fields are included or excluded in the query results. Setting a field to `1` includes it, while `0` excludes it. By default, the `_id` field is always included unless explicitly excluded.  
- Both **SQL and MongoDB** support advanced operations beyond basic queries, such as conditional updates, transactional workflows, and bulk operations. SQL is inherently transactional, while MongoDB introduced multi-document transactions starting with version 4.0 to handle complex data consistency needs.

### Best Practices

When working with SQL and MongoDB, adhering to best practices ensures optimal performance, scalability, and maintainability of your database systems. Here are some recommended strategies:

I. In *data modeling*, SQL databases use normalization to eliminate redundancy—breaking data into related tables—thus preserving data integrity. In contrast, MongoDB often embeds related documents, which reduces the overhead of joins and boosts performance for read-heavy applications, like real-time dashboards. 

- If we don’t apply proper modeling and normalization in SQL, we risk data anomalies (inconsistencies during updates) and duplication that can complicate maintenance. 
- If we do carefully plan our modeling, we gain cleaner, more consistent datasets that are easier to maintain and query. 
- In MongoDB, if we fail to embed or reference data properly, we can face excessive queries or complex application logic to manage relationships. Using its embedding features effectively speeds up reads and simplifies certain write operations.

II. Effective schema design revolves around *query patterns*. For SQL databases, this involves minimizing costly joins by strategic table design. MongoDB schemas should limit the necessity for multiple queries by thoughtfully embedding or referencing data based on frequent access patterns.

- If we don’t design with query patterns in mind, applications can suffer slow response times due to numerous or complex joins and lookups.
- If we do tailor schemas to match how our application actually queries data, we avoid bottlenecks and create a more efficient, user-friendly experience.

III. Applications demanding strict *relational integrity* and complicated transaction management typically favor SQL databases due to their strong adherence to ACID principles. Financial systems and e-commerce platforms often benefit from this level of consistency and reliability.

- If we ignore ACID properties in systems that need guaranteed transactions (for example, banking apps), we risk data corruption or erroneous account balances.
- If we do use ACID-centric SQL databases for critical operations, we ensure each transaction remains valid and consistent, greatly reducing the likelihood of data errors.

IV. Projects that emphasize flexibility and horizontal *scalability*, such as content management systems or IoT platforms, usually prefer MongoDB. Its schema-less architecture and smooth data distribution across multiple servers allow effortless scalability as data grows.

- If we skip a scalable approach in rapidly growing environments, we can hit performance limits and downtime due to single-server overload.
- If we do leverage MongoDB’s flexible structure and horizontal scaling, we accommodate data spikes more gracefully and react faster to evolving business needs.

V. Creating *indexes* on frequently queried fields improves performance in both SQL and MongoDB. Developers should regularly analyze query logs and execution patterns to identify optimal fields for indexing, making sure of efficient query responses.

- If we fail to create indexes where needed, queries become increasingly slow, leading to poor user experiences and timeouts in worst cases.
- If we properly index the right fields, we accelerate lookups dramatically, reducing CPU and memory load and improving overall responsiveness.

VI. Tools like SQL’s EXPLAIN plans and MongoDB’s *explain()* method empower developers to scrutinize and fine-tune queries. They provide insight into execution paths, pinpointing inefficient operations and guiding necessary optimizations.

- If we ignore these tools, we may remain blind to hidden performance issues and keep repeating inefficient query patterns.
- If we use them regularly, we can spot and fix slow queries quickly, ensuring our database remains optimized even as data grows and usage patterns evolve.

VII. While designing schemas, SQL databases use *normalization* techniques to enforce data consistency across multiple tables. MongoDB, conversely, uses denormalization strategies—such as embedding frequently accessed data—to accelerate read operations.

- If we apply normalization poorly in SQL, we risk complex joins or contradictory data across tables. 
- If we excessively denormalize in MongoDB without planning, we can end up storing too much duplicate data, causing inflated document sizes and more overhead on updates.
- Balancing normalization and denormalization for the use case leads to data structures that are both consistent and optimized for the most common operations.

VIII. Managing *relationships* in SQL databases involves clearly defined foreign keys and structured joins. MongoDB provides flexibility in managing relationships by either embedding documents for rapid access or using references, depending on how the application queries data.

- If we mismanage relationships in SQL, foreign key constraints can break or lead to orphaned records and data inconsistencies. 
- If we embed everything in MongoDB thoughtlessly, documents can become unwieldy, and updates more complicated. 
- If we choose the right relationship model, we ensure correct data linkage with minimal overhead and simpler development.

IX. Strong *authentication* mechanisms and comprehensive role-based access control are important in securing data, whether in SQL or MongoDB. Carrying out precise permissions prevents unauthorized access and maintains data confidentiality.

- If we neglect user access controls, we leave the door open for data theft, unauthorized modifications, or accidental exposure of sensitive information.
- If we establish solid authentication methods and granular permissions, we safeguard data integrity and uphold the trust of users and stakeholders.

X. Protecting sensitive data demands consistent *data encryption*, both when stored (at rest) and while moving across networks (in transit). This practice safeguards information against interception and breaches.

- If we don’t encrypt data, any unauthorized party gaining access to storage or intercepting traffic can read sensitive information, leading to severe security risks.
- If we encrypt thoroughly, both at rest and in transit, we greatly reduce the danger of data leaks and meet compliance requirements (like GDPR, HIPAA, etc.).

XI. Setting up schedules for *regular backups* minimizes the risk of data loss. Routine backups make sure of quick restoration capability following accidental deletions, corruption, or hardware failures.

- If we forego backups, a single incident (like a system crash) can cause irreversible data loss, damaging operations and reputation.
- If we maintain consistent backups, we can restore data swiftly, preserving business continuity and recovering from disasters with minimal downtime.

XII. Regularly testing *disaster recovery plans* enables organizations to respond effectively to unforeseen database outages, maintaining operational continuity and minimizing downtime.

- If we never test our recovery procedures, we might discover gaps or errors at the worst possible time—during a real crisis.
- If we do conduct frequent drills and tests, we confirm our ability to recover quickly and effectively, reinforcing overall business resilience.

XIII. Continuous *performance monitoring* allows for early detection of bottlenecks or resource contention within databases. Proactive monitoring tools alert administrators to issues before they escalate, making sure of smooth operations.

- If we ignore ongoing monitoring, performance issues can accumulate, ultimately slowing or even crashing the system when under stress.
- If we monitor metrics closely, we can spot trends and correct them preemptively, ensuring consistently responsive systems.

XIV. Conducting routine *maintenance* tasks—such as rebuilding fragmented indexes, archiving outdated data, and applying security patches or upgrades—maintains database performance, stability, and security over time.

- If we disregard maintenance, databases can degrade with accumulated overhead, slower queries, and heightened security vulnerabilities.
- If we schedule regular maintenance windows, we keep systems running efficiently, mitigate risks, and preserve long-term stability.

XV. MongoDB’s built-in *sharding* capability distributes data efficiently across multiple servers, optimizing query performance and managing high transaction volumes, ideal for large-scale applications.

- If we don’t implement sharding when data volume explodes, MongoDB instances can become overloaded, leading to slow queries and potential downtime.
- If we leverage sharding strategically, we scale seamlessly while preserving high throughput and fast response times for growing workloads.

XVI. SQL databases frequently carry out *partitioning* strategies to handle vast datasets effectively. Partitioning large tables, such as logs or transaction records, improves query speed by restricting operations to relevant data subsets.

- If we don’t partition extremely large tables, queries might scan millions of unnecessary rows, bogging down performance.
- If we employ partitioning correctly, we localize data lookups to targeted segments, speeding up queries and reducing strain on the database.
