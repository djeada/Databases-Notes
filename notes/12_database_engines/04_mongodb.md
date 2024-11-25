## MongoDB
- MongoDB: a popular, open-source, NoSQL database management system
- Document-oriented, using BSON (Binary JSON) format for data storage
- Designed for scalability, high availability, and high performance
- Suitable for a wide range of applications, from small projects to large-scale enterprise systems

## Features

###  Schemaless
No fixed schema; documents can have different fields and structures

###  Horizontal Scalability
Supports sharding for distributing data across multiple servers

### High Availability
Supports replica sets for automatic failover and redundancy

### Indexing
Allows indexing on any field, including embedded documents and arrays

###  Aggregation Framework
Provides powerful data processing and analytics capabilities

### Text Search
Built-in support for full-text search and indexing

### GridFS
Supports storage and retrieval of large files using a distributed file system

## MongoDB Commands
A. Creating a Database
```
use database_name;
```
B. Creating Collections
```
db.createCollection("collection_name");
```
C. Inserting Data
```
db.collection_name.insert({
field1: value1,
field2: value2,
...
});
```
D. Querying Data
```
db.collection_name.find({
field: value
});
```
E. Updating Data
```
db.collection_name.update(
{ field: value }, // query
{ $set: { field: new_value } } // update
);
```
F. Deleting Data
```
db.collection_name.remove({ field: value });
```
G. Dropping Collections
```
db.collection_name.drop();
```

## Administration and Management

### MongoDB Compass
A graphical administration tool for MongoDB

### Command-Line Client
A text-based interface for executing commands and managing databases (e.g., mongo shell)

###  Performance Tuning
MongoDB provides various configuration options for optimizing performance

###  Backup and Recovery
Supports logical and physical backups using tools like mongodump and MongoDB Cloud Manager

### Monitoring
Built-in statistics and monitoring tools for diagnosing performance issues

## Use Cases
- Common choice for web applications due to its flexibility and high performance
- Suitable for real-time analytics and data processing workloads
- Ideal for applications with large amounts of unstructured data or varying data schemas
- Well-suited for content management and media storage due to its document-oriented nature

## Engine

MongoDB primarily uses the **WiredTiger** storage engine as the default, but it has other engines tailored for specific use cases.

#### 1. **WiredTiger (Default Storage Engine)**
   - **Key Features:**
     - **Document-Level Concurrency:** Supports concurrent read and write operations at the document level.
     - **Compression:** Uses compression for data storage to reduce disk space usage.
     - **Indexing:** Supports various types of indexes for efficient data retrieval.
     - **Write-Ahead Logging (WAL):** Ensures data durability by logging changes before applying them.
   - **Best For:** General-purpose applications requiring high performance, concurrency, and efficient storage.

#### 2. **MMAPv1 (Deprecated)**
   - **Key Features:**
     - Uses memory-mapped files for data storage.
     - Limited to collection-level locking, which can hinder performance under heavy write loads.
   - **Best For:** Early MongoDB systems (deprecated in modern versions).

#### 3. **In-Memory Storage Engine**
   - **Key Features:**
     - Stores all data in memory for ultra-fast read/write operations.
     - Data is not persisted to disk (volatile storage).
   - **Best For:** Use cases like caching or analytics where speed is critical and data durability is not required.

#### 4. **Ephemeral For Test (Ephemeral Engine)**
   - **Key Features:**
     - Temporary, in-memory storage designed for testing and development purposes.
     - Data is lost when the server restarts.
   - **Best For:** Development and testing environments.

#### 5. **Third-Party Storage Engines**
   - MongoDB's pluggable storage engine architecture allows the integration of custom or third-party engines (e.g., RocksDB).

---

### **Key Features of MongoDB’s Storage Model**

#### 1. **Document-Oriented Storage**
   - MongoDB stores data in BSON (Binary JSON) format, which supports complex and nested data structures.
   - Flexible schemas allow for easy evolution of the data model.

#### 2. **Collections**
   - Collections group related documents, similar to tables in relational databases.
   - Collections do not enforce a fixed schema, making MongoDB highly adaptable.

#### 3. **Indexes**
   - MongoDB supports several types of indexes to optimize query performance:
     - Single-field indexes (default).
     - Compound indexes (multiple fields).
     - Text indexes (for full-text search).
     - Geospatial indexes (for location-based queries).
     - TTL indexes (for automatically expiring documents).
   - Indexes can be created and modified dynamically.

#### 4. **Sharding**
   - MongoDB supports horizontal scaling through sharding, where data is distributed across multiple servers.
   - A shard key determines how documents are distributed.

#### 5. **Replication**
   - MongoDB ensures high availability using replication:
     - **Replica Sets:** A group of MongoDB servers maintaining the same data, providing redundancy and failover.

#### 6. **Aggregation Framework**
   - MongoDB provides a powerful pipeline-based framework for data aggregation and transformation.

---

### **Advanced Storage Features in MongoDB**

#### 1. **Change Streams**
   - Real-time data change notifications for applications.

#### 2. **GridFS**
   - A mechanism for storing and retrieving large files (e.g., images, videos) that exceed BSON’s size limit (16MB).

#### 3. **Data Durability**
   - By default, MongoDB uses journaling to ensure durability and recoverability of data.

#### 4. **Transactions**
   - MongoDB supports ACID transactions for multi-document operations, introduced in version 4.0.


### **Comparison to Relational Databases**
- **Schema Flexibility:** MongoDB's flexible schema contrasts with the fixed schemas of relational databases like MySQL or PostgreSQL.
- **Scaling:** MongoDB excels in horizontal scaling with sharding, while relational databases typically scale vertically.
- **Transactions:** While MongoDB now supports multi-document ACID transactions, relational databases like PostgreSQL have more mature and robust transaction handling.
- **Complex Queries:** MongoDB’s aggregation framework is highly powerful but can be less intuitive than SQL for certain types of queries.


