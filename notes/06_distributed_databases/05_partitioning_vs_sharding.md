## Partitioning 

- **Definition**: A technique to divide a large database table into smaller, more manageable parts known as partitions.
- **Purpose**: 
    1. Enhance query performance by accessing only relevant partitions.
    2. Streamline data management tasks such as backup and archiving.
- **Types of Partitioning**: 
    1. Range partitioning
    2. List partitioning
    3. Hash partitioning
    4. Key partitioning
    5. Composite partitioning

## Sharding 

- **Definition**: A technique to split large datasets into smaller, more manageable pieces called shards, distributed across multiple nodes or clusters.
- **Purpose**: 
    1. Boost performance and scalability of large datasets in distributed systems.
    2. Spread data across multiple nodes or clusters.
    3. Decrease query latency by parallelizing operations across shards.
- **Sharding Strategies**: 
    1. Range-based sharding
    2. Hash-based sharding
    3. List-based sharding

## Differences Between Partitioning and Sharding

- **Scope**: Partitioning typically happens within a single database or a single node, whereas sharding spreads data across multiple nodes or clusters in a distributed system.
- **Granularity**: Partitioning focuses on dividing a single table, while sharding splits an entire dataset (which may include multiple tables).
- **Data Management**: Partitioning streamlines data management tasks within a single database, while sharding tackles challenges in distributed systems such as scalability and fault isolation.

## Use Cases

- **Partitioning**: 
    1. Time-based data (e.g., sales data partitioned by date)
    2. Categorical data (e.g., partition by country or department)

- **Sharding**: 
    1. Distributed databases (e.g., MongoDB, Apache Cassandra)
    2. Distributed caching systems (e.g., Memcached, Redis)
    3. Large-scale, high-traffic applications with horizontal scaling requirements

## Best Practices

- Choose partitioning or sharding based on system requirements, data characteristics, and query patterns.
- Combine partitioning and sharding to optimize performance and manageability in large-scale distributed systems.
- Monitor and adjust partitioning or sharding schemes as the system evolves to maintain performance.
