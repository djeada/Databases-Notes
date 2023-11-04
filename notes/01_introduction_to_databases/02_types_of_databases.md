# Overview of Database Types

Various types of databases cater to different needs and applications.

## Relational Databases (RDBMS)

### Description
Relational databases, or Relational Database Management Systems (RDBMS), store data in structured tables with rows and columns. Unique keys identify each row, and a predefined schema dictates the data's structure and types.

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
