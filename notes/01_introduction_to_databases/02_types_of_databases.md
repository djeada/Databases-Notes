# Overview of Database Types

Various types of databases cater to different needs and applications.

## Relational Databases (RDBMS)

### Description
Relational databases, or Relational Database Management Systems (RDBMS), store data in structured tables with rows and columns. Unique keys identify each row, and a predefined schema dictates the data's structure and types.

```
+----------------+      +------------------+
|   Customers    |      |    Orders        |
+----------------+      +------------------+
| ID   | Name    |      | OrderID | CustID |
|------+-------- |      |--------+---------|
| 1    | Alice   |      | 123    | 1       |
| 2    | Bob     |      | 124    | 2       |
| 3    | Charlie |      | 125    | 1       |
+----------------+      +------------------+
        |                        |
        |-------Foreign Key------|
```

### Representative Systems
- MySQL
- PostgreSQL
- Oracle Database
- Microsoft SQL Server

### Use Cases
- Transaction processing systems
- Enterprise applications
- Systems prioritizing data consistency and integrity

### Strengths
- ACID compliance ensures data reliability.
- Strong support for structured data and complex queries.
- Schema adherence enforces data consistency.

### Weaknesses
- Limited horizontal scalability.
- Rigidity can hinder handling unstructured data.
- Performance may degrade with large databases.

## NoSQL Document-Based Databases

### Description
Document-based databases manage data as documents, typically in formats like JSON or BSON.

```
+-----------------------------------------+
|        Document-Based DB                |
+-----------------------------------------+
| Document 1                              |
| {                                       |
|   "id": "001",                          |
|   "type": "customer",                   |
|   "name": "Alice",                      |
|   "orders": [                           |
|     {"order_id": "1001", "total": 300}, |
|     {"order_id": "1002", "total": 450}  |
|   ]                                     |
| }                                       |
+-----------------------------------------+
| Document 2                              |
| {                                       |
|   "id": "002",                          |
|   "type": "customer",                   |
|   "name": "Bob",                        |
|   "orders": [                           |
|     {"order_id": "1003", "total": 200}  |
|   ]                                     |
| }                                       |
+-----------------------------------------+
```

### Representative Systems
- MongoDB
- Couchbase

### Use Cases
- Content and catalog management
- Real-time analytics
- High-speed logging and caching

### Strengths
- Schema-less design offers flexibility.
- High performance and easy scalability.
- Suitable for hierarchical data storage.

### Weaknesses
- Limited support for complex, multi-operation transactions.
- Inefficient for complex queries and joins.

## NoSQL Column-Based Databases

### Description
Column-based databases, or wide-column stores, organize data by columns instead of rows, optimizing for scaling and handling large datasets.

```
+---------------------------------------+
|       Column-Based Database           |
+---------------------------------------+
| Column Family: Customers              |
|---------------------------------------|
| ID | Name     | Age | Email           |
|----|----------|-----|-----------------|
| 1  | Alice    | 30  | alice@email.com |
| 2  | Bob      |     | bob@email.com   |
| 3  | Charlie  | 40  |                 |
+---------------------------------------+
| Column Family: Orders                 |
|---------------------------------------|
| OrderID | CustID | Amount | Status    |
|---------|--------|--------|-----------|
| 1001    | 1      | 300    | Shipped   |
| 1002    | 2      | 450    | Delivered |
| 1003    | 1      |        | Pending   |
+---------------------------------------+
```

### Representative Systems
- Apache Cassandra
- Google Cloud Bigtable
- Apache HBase

### Use Cases
- Time series data
- Big Data processing
- Large-scale real-time data processing

### Strengths
- High performance for large data reads and writes.
- Efficient columnar data storage and retrieval.
- Scalable and fault-tolerant.

### Weaknesses
- Not suitable for complex multi-table queries.
- Learning curve for SQL users.

## NoSQL Key-Value Databases

### Description
Key-value databases are simple NoSQL databases storing data as key-value pairs.

```
+-----------------------------------------------+
|      Key-Value Database                       |
+-----------------------------------------------+
| Key        | Value                            |
|------------|----------------------------------|
| user:1001  | { "name": "Alice",               |
|            |   "age": 30,                     |
|            |   "email": "alice@example.com"}  |
| user:1002  | { "name": "Bob",                 |
|            |   "age": 25,                     |
|            |   "email": "bob@example.com"}    |
| settings:1 | { "theme": "dark",               |
|            |   "language": "en"}              |
+-----------------------------------------------+
```

### Representative Systems
- Redis
- Amazon DynamoDB

### Use Cases
- Caching
- Session management
- User preference storage

### Strengths
- Efficient data storage and retrieval.
- High performance and scalability.
- Suitable for high traffic and large datasets.

### Weaknesses
- Limited support for complex queries.
- Lack of structure can complicate data management.

## NoSQL Graph-Based Databases

### Description
Graph databases manage data as nodes (entities) and edges (relationships).

```
+--------------------------------------------------+
|                Graph-Based DB                    |
+--------------------------------------------------+
| Nodes                                            |
|--------------------------------------------------|
| (User1:User {name: "Alice", age: 30})            |
| (User2:User {name: "Bob", age: 25})              |
| (Product1:Product {name: "Laptop", price: 1200}) |
| (Product2:Product {name: "Phone", price: 800})   |
+--------------------------------------------------+
| Relationships                                    |
|--------------------------------------------------|
| (User1)-[:PURCHASED]->(Product1)                 |
| (User1)-[:FRIEND_OF]->(User2)                    |
| (User2)-[:PURCHASED]->(Product2)                 |
+--------------------------------------------------+
```

### Representative Systems
- Neo4j
- Amazon Neptune

### Use Cases
- Social networks
- Recommendation engines
- Fraud detection

### Strengths
- Efficient handling of relationship-centric data.
- Powerful graph traversal queries.
- Intuitive data modeling for certain use cases.

### Weaknesses
- Requires a shift from traditional SQL mindset.
- Limited support for non-graph related operations.
- May be less efficient for handling non-graph related operations.
