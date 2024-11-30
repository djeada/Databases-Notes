## Sharding

Sharding is a method of horizontally partitioning data in a database, so that each shard contains a unique subset of the data. This approach allows a database to scale by distributing data across multiple servers or clusters, effectively handling large datasets and high traffic loads.

Imagine you have a vast library of books that no longer fits on a single bookshelf. To manage this, you distribute the books across multiple bookshelves based on genres or authors. Similarly, sharding splits your database into smaller, more manageable pieces.

### How Sharding Works

At its core, sharding involves breaking up a large database table into smaller chunks called shards. Each shard operates as an independent database, containing its portion of the data.

**Diagram of Sharding:**

```
                    +----------------------+
                    |     User Database    |
                    +----------------------+
                             /   |   \
                            /    |    \
                           /     |     \
                    +------+  +------+  +------+
                    |Shard1|  |Shard2|  |Shard3|
                    +------+  +------+  +------+
                       |         |         |
               +-------+--+  +---+---+  +---+---+
               | User IDs |  | User IDs |  | User IDs |
               | 1 - 1000 |  |1001-2000|  |2001-3000|
               +----------+  +---------+  +---------+
```

In this diagram:

- **Shard1** contains User IDs from 1 to 1000.
- **Shard2** contains User IDs from 1001 to 2000.
- **Shard3** contains User IDs from 2001 to 3000.

When a user with ID 1500 logs in, the system knows to query Shard2 directly, reducing the load on the other shards and improving response time.

### Practical Example: Sharding an E-commerce Database

Let's consider an online store that has a rapidly growing customer base. The "Orders" table has become enormous, leading to slow queries and performance issues.

#### Before Sharding: Single Large Table

**Orders Table:**

| OrderID | CustomerID | OrderDate  | TotalAmount |
|---------|------------|------------|-------------|
| 1       | 101        | 2021-01-10 | $150        |
| 2       | 102        | 2021-01-11 | $200        |
| ...     | ...        | ...        | ...         |
| 1,000,000 | 9999     | 2021-12-31 | $75         |

Handling queries on this table is slow due to its size.

#### After Sharding: Distributed Orders Tables

The database is sharded based on the "OrderDate" using range-based sharding.

**Shard January:**

| OrderID | CustomerID | OrderDate  | TotalAmount |
|---------|------------|------------|-------------|
| 1       | 101        | 2021-01-10 | $150        |
| 2       | 102        | 2021-01-11 | $200        |
| ...     | ...        | ...        | ...         |

**Shard February:**

| OrderID | CustomerID | OrderDate  | TotalAmount |
|---------|------------|------------|-------------|
| 5001    | 201        | 2021-02-01 | $250        |
| 5002    | 202        | 2021-02-02 | $300        |
| ...     | ...        | ...        | ...         |

**Shard March to December:**

Similarly, other shards contain orders for their respective months.

By sharding the "Orders" table by month, queries for orders in a specific month only access the relevant shard, significantly improving performance.

### Selecting a Sharding Key

The **sharding key** determines how data is distributed across shards and affects system performance and scalability.  

**Factors to Consider:**

- A key that ensures **uniform data distribution** helps avoid overloading specific shards and maintains balance.  
- Keys aligned with **query patterns** localize data access, reducing the need for cross-shard queries.  
- Supporting **scalability** is essential, ensuring the system can accommodate the addition of new shards without significant restructuring.  

**Example Sharding Keys:**

- Using **UserID** works well for user-centric applications where data is often accessed by individual users.  
- **Geographic location** is suitable for systems handling data based on regions, like content delivery or local services.  
- **Date/Time** is an effective choice for applications managing time-series data, such as logs or transactional records.

### Sharding Strategies

Different strategies can be used to determine how data is partitioned across shards.

#### Range-Based Sharding

Data is divided based on ranges of the sharding key.

**Example:**

- **Shard1:** User IDs 1 - 1,000,000
- **Shard2:** User IDs 1,000,001 - 2,000,000
- **Shard3:** User IDs 2,000,001 - 3,000,000

**Advantages:**

- Simple to implement.
- Efficient for range queries.

**Disadvantages:**

- Potential for uneven data distribution.
- Hotspots if one range is accessed more frequently.

#### Hash-Based Sharding

A hash function is applied to the sharding key to determine the shard.

**Hash Function Example:**

```
Shard Number = Hash(UserID) % Total Shards
```

- For UserID 12345: `Hash(12345) % 3 = 0` → Shard0
- For UserID 67890: `Hash(67890) % 3 = 1` → Shard1

**Advantages:**

- Even data distribution.
- Avoids hotspots.

**Disadvantages:**

- Not suitable for range queries.
- Adding shards requires rehashing data.

#### Directory-Based Sharding

A lookup service maintains a mapping of keys to shards.

**Example Directory:**

| UserID Range | Shard  |
|--------------|--------|
| 1 - 500,000  | ShardA |
| 500,001 - 1,000,000 | ShardB |
| ...          | ...    |

**Advantages:**

- Flexible and dynamic.
- Can handle uneven data distribution.

**Disadvantages:**

- Directory can become a bottleneck.
- Added complexity.

### Handling Cross-Shard Queries

- Queries across multiple shards can become **complex** due to the distribution of data.  
- In scenarios like identifying all users signed up in the past 24 hours, data is **spread** across multiple shards, requiring additional mechanisms for aggregation.  
- Using **parallel queries**, systems execute the query on all shards simultaneously and merge the results to produce the final output.  
- Data **duplication** can be implemented by maintaining a global summary table or index containing key information from all shards.  
- Cross-shard querying introduces **overhead**, as the system must coordinate and aggregate data from multiple sources.  
- Ensuring data **consistency** is a challenge, especially if the system relies on duplicated or aggregated information across shards.  

### Practical Implementation with MongoDB

MongoDB is a popular NoSQL database that supports sharding natively.

**Setting Up Sharding:**

I. **Enable Sharding on the Database:**

```javascript
sh.enableSharding("myDatabase")
```

II. **Choose a Shard Key:**

For example, using "user_id".

III. **Shard the Collection:**

```javascript
sh.shardCollection("myDatabase.users", { "user_id": "hashed" })
```

**Data Distribution:**

- MongoDB automatically distributes data based on the hashed "user_id".
- Balancer ensures shards are evenly loaded.

**Single Shard Query:**

```javascript
db.users.find({ "user_id": 12345 })
```

The query is routed to the shard containing `user_id` 12345.

**Broadcast Query:**

```javascript
db.users.find({ "age": { $gte: 18 } })
```

The query is sent to all shards since "age" is not the shard key.

### Real-World Use Case: Twitter's Timeline Storage

Twitter employs sharding to efficiently manage its vast volume of tweet data.

**Challenges:**

- Handling the ingestion of millions of tweets daily requires a scalable and robust data storage solution.
- Ensuring rapid retrieval of tweets for user timelines is essential for a seamless user experience.

**Sharding Strategy:**

Tweets are distributed across shards based on the UserID, ensuring that all tweets from a particular user reside in the same shard. 

**Benefits:**

- This approach leads to an even distribution of data across shards, preventing any single shard from becoming a bottleneck.
- It facilitates efficient retrieval of a user's tweets, as all relevant data is located within the same shard.

**Handling Cross-Shard Operations:**

- Aggregation services compile data from multiple shards to construct comprehensive user timelines.
- Caching mechanisms, such as Redis clusters, are utilized to store home timelines, enhancing performance and reducing latency. 

### Best Practices for Sharding

Implementing sharding effectively involves careful planning.

#### Understand Your Data and Access Patterns

Analyze how data is accessed to choose an appropriate shard key.

**Questions to Ask:**

- What are the most common queries?
- Does the data have natural partitions?
- Are certain data ranges accessed more frequently?

#### Plan for Scalability

Design the sharding strategy to accommodate future growth.

- Using a **flexible shard key** enables the system to accommodate new shards without requiring extensive data redistribution.  
- Leveraging **automated scaling** tools simplifies the process of adding shards, minimizing manual intervention and downtime.  

#### Monitor and Optimize

Regularly monitor shard performance and adjust as needed.

**Metrics to Track:**

- Query latency
- Shard sizes
- Resource utilization

**Optimization Actions:**

- Rebalancing shards
- Adjusting shard keys

#### Handle Failures Gracefully

Implement robust mechanisms to deal with shard failures.

- Implementing **redundancy** by replicating data within shards helps prevent data loss and ensures availability during failures.  
- Employing **failover strategies** allows the system to automatically reroute traffic to backup replicas or alternate shards if a primary shard fails.  

### Challenges of Sharding

While sharding offers significant benefits, it also introduces complexity.

#### Increased System Complexity

- **Application logic** becomes more complex as applications must be designed to understand and interact with the sharding architecture.  
- **Testing** scenarios grow in complexity to ensure functionality and reliability across all shards under various conditions.  

#### Data Consistency

- **Distributed transactions** pose challenges in ensuring ACID properties across multiple shards, requiring additional coordination mechanisms.  
- **Consistency models** may need to be adjusted, often relaxing strict consistency to improve performance and scalability.  

#### Operational Overhead

- **Maintenance** requirements increase due to the need to manage a larger number of servers and their configurations.  
- **Backups** must be performed separately for each shard, adding to the time and effort required for data protection.  
