# Relational Databases (RDBMS)

- **Overview:** Based on the relational model, using tables, columns, rows, and keys to store and relate data.
- **Examples:** MySQL, PostgreSQL, Oracle, and SQL Server.
- **Use Cases:** Suitable for structured data, transactions, and applications that require data consistency.
- **Strengths:** ACID properties, strong consistency, and adherence to schema.
- **Weaknesses:** Limited horizontal scaling and difficulties in handling unstructured data.

# NoSQL Databases

## Document-Based

- **Overview:** Store and manage data as documents, usually in formats like JSON or BSON.
- **Examples:** MongoDB, Couchbase.
- **Use Cases:** Content management systems, catalog management, and analytics.
- **Strengths:** Schema flexibility, high performance, and ease of use.
- **Weaknesses:** Limited support for complex transactions and joins.

## Column-Based

- **Overview:** Organize data in columns rather than rows, optimized for reading and writing large data sets.
- **Examples:** Cassandra, HBase.
- **Use Cases:** Time series data, sensor data, and analytics.
- **Strengths:** High write performance, horizontal scalability, and data compression.
- **Weaknesses:** Limited support for joins and complex queries.

## Key-Value

- **Overview:** Store data as key-value pairs, optimized for simple data storage and retrieval.
- **Examples:** Redis, Amazon DynamoDB.
- **Use Cases:** Caching, session management, and configuration management.
- **Strengths:** High performance, scalability, and simplicity.
- **Weaknesses:** Limited support for complex data structures and queries.

## Graph-Based

- **Overview:** Store and manage data as nodes, edges, and properties in a graph structure.
- **Examples:** Neo4j, Amazon Neptune.
- **Use Cases:** Social networks, recommendation engines, and fraud detection.
- **Strengths:** High performance for graph traversal, relationship-based querying, and data modeling.
- **Weaknesses:** Limited support for operations outside of graph traversal and complex aggregations.
