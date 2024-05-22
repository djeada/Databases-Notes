## Partitioning 

Partitioning is a technique used to divide a large database table into smaller, more manageable parts known as partitions. Each partition is stored within the same database, but they can be accessed and managed independently.

Before Partitioning:

```
+-------------------------------------------+
Some Table
Row 1: Data A1, B1, C1
Row 2: Data A2, B2, C2
Row 3: Data A3, B3, C3
Row 4: Data A4, B4, C4
Row 5: Data A5, B5, C5
+-------------------------------------------+
```

After Partitioning:

```
+-------------------------+-------------------------+-------------------------+
Partition 1               | Partition 2             | Partition 3             
------------------------- | ------------------------|-------------------------
Row 1: Data A1, A2, A3    | Row 1: Data B1, B2, B3  | Row 1: Data C1, C2, C3  
Row 2: Data A4, A5        | Row 2: Data B4, B5      | Row 2: Data C4, C5      
+-------------------------+-------------------------+-------------------------+
```

After partitioning, the table is divided into separate partitions within the same database. This allows for improved performance and easier management.

Purpose: 

1. Enhance query performance by accessing only relevant partitions.
2. Streamline data management tasks such as backup and archiving.

Types of Partitioning:

1. Range partitioning
2. List partitioning
3. Hash partitioning
4. Key partitioning
5. Composite partitioning

## Sharding 

A technique to split large datasets into smaller, more manageable pieces called shards, distributed across multiple nodes or clusters.

Before Sharding:

```
+------------------------------------------------+
| Single Database Instance                       |
|                                                |
| - Data A1, A2, A3                              |
| - Data B1, B2, B3                              |
| - Data C1, C2, C3                              |
|                                                |
+------------------------------------------------+
```

Initially, all data is stored in a single database instance.

After Sharding:

```
+-------------------+-------------------+-------------------+
| Shard 1           | Shard 2           | Shard 3           |
|                   |                   |                   |
| - Data A1, A2, A3 | - Data B1, B2, B3 | - Data C1, C2, C3 |
|                   |                   |                   |
| (Database 1)      | (Database 2)      | (Database 3)      |
+-------------------+-------------------+-------------------+
```

After sharding, the data is distributed across multiple database instances, each known as a shard. Each shard holds a portion of the data.

Purpose:

1. Boost performance and scalability of large datasets in distributed systems.
2. Spread data across multiple nodes or clusters.
3. Decrease query latency by parallelizing operations across shards.

Sharding Strategies: 

1. Range-based sharding
2. Hash-based sharding
3. List-based sharding

## Differences Between Partitioning and Sharding

| Feature                  | Partitioning                                                                 | Sharding                                                                 |
|--------------------------|------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| **Definition**           | Dividing a large table into smaller parts within a single database.          | Splitting a database to distribute the load across multiple servers.     |
| **Purpose**              | To manage and optimize database performance and simplify management.         | To distribute datasets and load, improving performance and scalability.   |
| **Data Distribution**    | Data is split across partitions within a single database system.             | Data is spread across multiple database systems.                         |
| **Query Performance**    | Can improve performance for large tables by isolating parts of the table.    | Significantly improves performance by distributing queries across servers.|
| **Scalability**          | Improves management and performance but is limited to vertical scaling.      | Highly scalable, allows for horizontal scaling across many servers.      |
| **Complexity**           | Relatively simpler to implement than sharding.                               | More complex due to data distribution and management across servers.     |
| **Use Cases**            | Large tables where data can be logically segmented within the same database. | Very large datasets and high-traffic applications requiring distributed databases. |
| **Transaction Management** | Easier, as transactions are typically within the same database system.       | More complex due to transactions possibly spanning multiple databases.    |
| **Redundancy and Fault Tolerance** | Limited, as data is often in a single system.                        | Higher, as data is distributed and can be replicated across servers.      |

## Best Practices

- Choose partitioning or sharding based on system requirements, data characteristics, and query patterns.
- Combine partitioning and sharding to optimize performance and manageability in large-scale distributed systems.
- Monitor and adjust partitioning or sharding schemes as the system evolves to maintain performance.
