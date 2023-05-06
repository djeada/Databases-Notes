## Distributed database systems
Distributed database systems store and manage data across multiple nodes, often in geographically diverse locations, to provide high availability, fault tolerance, and scalability. This note focuses on the concept of distributed database systems and notable implementations, such as Google Spanner, Amazon DynamoDB, and Apache Cassandra.

## Characteristics

### Data Distribution
Data is distributed across multiple nodes, often in different locations or data centers, to ensure availability and fault tolerance.

### Scalability
Distributed database systems are designed to scale horizontally, allowing for the addition of new nodes to handle increased load and data storage requirements.

### Consistency Models
Distributed databases typically use various consistency models, such as eventual consistency or strong consistency, to balance the trade-offs between data consistency, availability, and performance.

### Replication and Partitioning
Data replication and partitioning strategies are employed to distribute and manage data across multiple nodes, ensuring fault tolerance and load balancing.

## Notable Implementations

### Google Spanner

1. Google Spanner is a globally distributed, strongly consistent database service that combines the benefits of relational databases with the scalability and availability of NoSQL systems.
2. It uses the TrueTime API, a globally synchronized clock, to ensure external consistency and provide strong consistency guarantees across distributed nodes.
3. Spanner is well-suited for large-scale applications requiring strong consistency and high availability, such as financial systems or inventory management applications.

### Amazon DynamoDB

1. Amazon DynamoDB is a managed NoSQL database service that provides fast and predictable performance with seamless scalability.
2. It supports both key-value and document data models and offers eventual consistency or strong consistency options for read operations.
3. DynamoDB is designed for applications with high write and read throughput requirements, such as gaming, IoT, and ad tech.

### Apache Cassandra

1. Apache Cassandra is an open-source, highly scalable, and distributed NoSQL database that provides high availability and fault tolerance.
2. It uses a partitioned row store with tunable consistency and supports a wide range of consistency levels, from eventual consistency to linearizability.
3. Cassandra is ideal for applications that require high write throughput and the ability to scale across multiple data centers, such as time-series data storage, messaging systems, or recommendation engines.
