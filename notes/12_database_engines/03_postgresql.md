# PostgreSQL

PostgreSQL is an open-source object-relational database maintained by the PostgreSQL Global Development Group. It supports relational queries, extensible types, and transactions for a wide range of applications.

## Features

### ACID Compliance

Supports ACID transactions, ensuring data consistency and reliability

### Extensibility

- Allows custom functions, operators, data types, and index methods
- Supports stored procedures, triggers, and views

### Concurrency Control

Uses MVCC so ordinary reads can observe committed versions while writers work. Writes, explicit locking reads, and schema operations still use locks.

### Robust Security

Offers strong encryption, authentication, and authorization mechanisms

### Cross-Platform

Compatible with various operating systems, including Windows, macOS, Linux, and Unix

### Full-Text Search

Built-in support for text search and advanced indexing

### Spatial Data Support

Support for geographic objects and spatial queries through PostGIS extension

### High Availability and Replication

Supports various replication methods, including streaming replication and logical replication

## PostgreSQL Commands

### Creating a Database

```
CREATE DATABASE database_name;
```

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

## Administration and Management

### pgAdmin

A popular, open-source graphical administration tool for PostgreSQL

### Command-Line Client

A text-based interface for executing SQL queries and managing databases (e.g., psql)

### Performance Tuning

PostgreSQL provides various configuration options for optimizing performance

### Backup and Recovery

Supports logical and physical backups using tools like pg_dump and pg_basebackup

### Monitoring

Built-in statistics collector for monitoring and diagnosing performance issues

## Use Cases

- Common choice for web applications due to its flexibility and extensibility
- Widely used in GIS applications due to PostGIS support
- Suitable for data warehousing and analytical processing workloads
- Ideal for large-scale enterprise applications requiring a robust and feature-rich RDBMS

## Storage architecture

Ordinary PostgreSQL tables use heap storage and MVCC. The system also supports extensible table and index access methods; these are different from MySQL’s storage-engine model.

### **Key Features of PostgreSQL’s Storage System**

#### **Unified Storage Engine**

   - Heap storage is the normal built-in table access method. Concurrency, recovery, and extensible access methods work together; performance depends on the workload and design.

---

#### **Table Storage Models**

   - PostgreSQL organizes data in tables using a row-based storage model.
   - **Heap Storage:**
     - Default storage model for tables.
     - Data is stored in no particular order, and MVCC (Multiversion Concurrency Control) ensures consistency without locking reads.

---

#### **MVCC (Multiversion Concurrency Control)**

   - PostgreSQL uses MVCC to handle transactions and concurrency.
   - Instead of locking rows, it creates multiple versions of rows to ensure consistency.
   - MVCC supports advanced features like:
     - Point-in-time recovery (PITR).
     - Non-blocking reads during write operations.

---

#### **Tablespaces**

   - PostgreSQL supports tablespaces, allowing users to control where data files are stored on disk.
   - Useful for optimizing storage performance and managing large-scale data systems.

---

#### **TOAST (The Oversized-Attribute Storage Technique)**

   - PostgreSQL can handle large data fields like blobs, JSON, or XML efficiently using TOAST.
   - Automatically stores large column data externally and references it in the main table.

---

### **Indexing Options in PostgreSQL**

PostgreSQL supports a variety of indexing methods, allowing customization for different workloads:

1. **B-Tree:**
   - Default index type, ideal for most general-purpose queries.
2. **Hash:**
   - Optimized for equality lookups (e.g., `=` or `IN`).
3. **GIN (Generalized Inverted Index):**
   - Efficient for full-text searches and indexing JSON/array fields.
4. **GiST (Generalized Search Tree):**
   - Useful for spatial data, geometric searches, and full-text indexing.
5. **BRIN (Block Range Index):**
   - Optimized for large, sequentially stored data sets like time-series data.
6. **SP-GiST (Space Partitioned GiST):**
   - Efficient for non-balanced tree structures like quadtrees or k-d trees.
7. **Bloom Filters:**
   - Space-efficient, probabilistic data structures for certain query types.

---

### **Advanced Features in PostgreSQL**

#### **Partitioning**

   - PostgreSQL supports declarative partitioning (range, list, and hash) to optimize large data sets by dividing them into smaller, manageable parts.

#### **Foreign Data Wrappers (FDW)**

   - Allows PostgreSQL to interact with external data sources (e.g., other databases, files) as if they were local tables.

#### **Custom Data Types**

   - PostgreSQL allows users to define their own data types, providing flexibility for domain-specific applications.

#### **JSON and JSONB Support**

   - PostgreSQL has robust support for semi-structured data through JSON and JSONB.
   - JSONB (binary JSON) provides efficient indexing and querying capabilities.

#### **Full-Text Search**

   - Built-in full-text search capabilities enable efficient querying of textual data.

#### **PL/pgSQL and Other Procedural Languages**

   - PostgreSQL supports embedded procedural languages (e.g., PL/pgSQL, PL/Python, PL/Perl), allowing complex application logic to run within the database.

---

### **Storage Customization in PostgreSQL**

- While PostgreSQL doesn’t use multiple storage engines like MySQL, it offers advanced configuration and extension capabilities to tailor the database to specific needs:
  - Extensions like `pg_partman` for partition management.
  - `TimescaleDB` for time-series data.
  - `PostGIS` for geographic and spatial data.

### **Comparison to MySQL**

- **Single Unified Engine vs. Multiple Engines:**
  - PostgreSQL has a unified engine with deep extensibility, while MySQL offers multiple engines (e.g., InnoDB, MyISAM).
- **Concurrency:** PostgreSQL’s MVCC implementation often outperforms MySQL for high-concurrency scenarios.
- **Extensibility:** PostgreSQL supports custom data types, extensions, and advanced indexing, making it more flexible for complex applications.
- **ACID Compliance:** PostgreSQL is fully ACID-compliant by default, whereas MySQL depends on the storage engine (e.g., InnoDB is ACID-compliant, MyISAM is not).
