## SQLite
- SQLite: a self-contained, serverless, zero-configuration, transactional SQL database engine
- Lightweight and easy to use, suitable for small to medium-sized applications
- Ideal for embedded systems, mobile applications, and local data storage

## Features

### Serverless and Self-Contained
- No separate server process or setup required
- Database stored in a single file on disk

### Transactional
Supports ACID transactions, ensuring data consistency

### Cross-Platform
Compatible with various operating systems, including Windows, macOS, Linux, and Android

### Small Footprint
Low memory and storage requirements, making it suitable for embedded systems and mobile applications

### Extensive Language Support
APIs available for several programming languages, including C, C++, Java, Python, and more

### Public Domain
Free and open-source, with no licensing restrictions

## Limitations

### Not Suitable for Large Applications
Limited scalability compared to more robust database engines like MySQL or PostgreSQL

### Limited Concurrency
Write transactions lock the entire database, which may cause contention in multi-user applications

### Lack of User Management and Access Control
No built-in support for user authentication or role-based access control

### Subset of SQL Features
Some SQL features, such as RIGHT JOINs and complete ALTER TABLE support, are not available in SQLite

## Use Cases

### Embedded Systems
Ideal for applications that require a lightweight, self-contained database engine

### Mobile Applications
Popular choice for Android and iOS app development due to its low footprint and ease of use

### Desktop Applications
Suitable for local data storage in desktop applications where a full-fledged database server is not required

### Prototyping and Testing
Provides a simple and convenient way to prototype and test applications before deploying to a production database server

## SQLite Commands
### Creating a Database
SQLite databases are created by opening a file with the appropriate API or command-line tool

### Creating Tables

```
CREATE TABLE table_name (
 column_name1 datatype PRIMARY KEY,
 column_name2 datatype NOT NULL,
 ...
);
```

### Inserting Data

```
INSERT INTO table_name (column1, column2, ...)
VALUES (value1, value2, ...);
```

### Querying Data

```
SELECT column1, column2, ...
FROM table_name
WHERE condition;
```

### Updating Data

```
UPDATE table_name
SET column1 = value1, column2 = value2, ...
WHERE condition;
```

### Deleting Data

```
DELETE FROM table_name
WHERE condition;
```

### Dropping Tables

```
DROP TABLE table_name;
```

## ENGINE:

SQLite is a lightweight, serverless, self-contained database engine. Unlike  for example MySQL, which offers a variety of storage engines tailored to different use cases, SQLite has a single storage engine that is designed to handle most typical use cases efficiently. However, SQLite provides flexibility in how data is stored and managed. Below are some aspects of SQLite's storage system:

---

### **Key Features of SQLite's Storage Engine**

1. **Single Storage Engine:**
   - SQLite uses a B-Tree-based storage engine for its tables and indexes. This design is optimized for speed and efficiency in handling most database operations.
   - The database is stored as a single file, making it portable and easy to integrate with applications.

---

2. **Journaling Modes:**
   - SQLite provides multiple journaling modes to handle transactions and data consistency:
     - **DELETE:** Default mode where the journal file is deleted after the transaction is committed.
     - **WAL (Write-Ahead Logging):** Offers better performance for concurrent read/write operations by keeping a separate log file.
     - **TRUNCATE:** Truncates the journal file instead of deleting it.
     - **PERSIST:** Keeps the journal file but marks it as empty after a transaction.
     - **MEMORY:** Keeps the journal in memory for faster performance but sacrifices persistence.

---

3. **In-Memory Mode:**
   - SQLite supports creating a database entirely in memory (`:memory:`), which is extremely fast but volatile (data is lost when the connection is closed).

---

4. **File Storage Options:**
   - SQLite supports different modes for how data is synced to disk:
     - **FULL:** Ensures maximum durability by syncing data to disk after every write.
     - **NORMAL:** Balances durability and performance.
     - **OFF:** Improves performance by not syncing data immediately to disk (not recommended for critical data).

---

5. **Temporary Databases:**
   - SQLite allows creating temporary databases that exist only during the session. These are often used for intermediate or scratch data.

---

6. **Virtual Table Mechanism:**
   - SQLite supports virtual tables, which allow the use of custom storage backends. Examples include:
     - **FTS (Full-Text Search):** A module for performing full-text searches.
     - **R-Tree:** Optimized for spatial data and geometric indexing.
     - **JSON1:** Provides JSON storage and query capabilities.

---

7. **Atomic Commit and Rollback:**
   - SQLite ensures ACID compliance (Atomicity, Consistency, Isolation, Durability) for transactions using its internal mechanisms like journaling or WAL.

