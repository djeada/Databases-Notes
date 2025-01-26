## Sharding

Sharding is a method of horizontally partitioning data in a database, so that each shard contains a unique subset of the data. This approach allows a database to scale by distributing data across multiple servers or clusters, effectively handling large datasets and high traffic loads.

After reading the material, you should be able to answer the following questions:

1. What is sharding and how does it enhance database scalability?
2. What are the different sharding strategies and what are their respective advantages and disadvantages?
3. What factors should be considered when selecting a sharding key?
4. What are the common challenges associated with implementing sharding and what best practices can mitigate them?
5. How are cross-shard queries managed and what implications do they have on system performance and complexity?

### How Sharding Works

Imagine you have a vast library of books that no longer fits on a single bookshelf. To manage this, you distribute the books across multiple bookshelves based on genres or authors. Similarly, sharding splits your database into smaller, more manageable pieces.

At its core, sharding involves breaking up a large database table into smaller chunks called shards. Each shard operates as an independent database, containing its portion of the data.

```
    +----------------------+
    |     User Database    |
    +----------------------+
             /   |    \
            /    |     \
           /     |      \
    +------+  +------+     +------+
    |Shard1|  |Shard2|     |Shard3|
    +------+  +------+     +------+
        |         |             |
+-------+--+  +---+------+  +---+------+
| User IDs |  | User IDs |  | User IDs |
| 1 - 1000 |  |1001-2000 |  |2001-3000 |
+----------+  +----------+  +----------+
```

In this diagram:

- **Shard1** contains User IDs from 1 to 1000.
- **Shard2** contains User IDs from 1001 to 2000.
- **Shard3** contains User IDs from 2001 to 3000.

When a user with ID 1500 logs in, the system knows to query Shard2 directly, reducing the load on the other shards and improving response time.

### Practical Example: Sharding an E-commerce Database

In this expanded example, we’ll deep-dive into how an online store might shard its database to address performance and scalability issues. We will examine the technical and operational facets, including how queries are routed, how data distribution is managed, and how the business justifies sharding from both a performance and cost perspective.

#### Before Sharding: Single Large Table

I. **Growing User Base**  

- The online store has expanded from a few thousand to millions of customers.  
- As a result, the number of daily orders has skyrocketed, and each new purchase inserts a record into the same monolithic “Orders” table.

II. **Performance Bottlenecks**  

- Queries that retrieve order history, compute totals over given time periods, or join with other large tables (like Customers or Products) are increasingly slow—sometimes taking seconds or minutes.
- Maintaining indexes on a table with tens or hundreds of millions of rows becomes costly. Every insert or update operation triggers index updates, increasing locking or concurrency contention.
- CPU, RAM, and I/O usage on the single database server spikes during peak shopping periods (e.g., holidays, flash sales), leading to degraded performance and potential service unavailability.

III. **Operational Risks**  

- With all data on one server, a hardware failure or network issue can render the entire store’s order data inaccessible.  
- Full table backups become unwieldy. Restoring from large backups can take hours, which is unacceptable for a business that relies on 24/7 availability.

**Orders Table (Single Shard):**

| OrderID   | CustomerID | OrderDate    | TotalAmount |
|-----------|------------|--------------|-------------|
| 1         | 101        | 2021-01-10   | $150        |
| 2         | 102        | 2021-01-11   |$200        |
| …         | …          | …            | …           |
| 1,000,000 | 9999       | 2021-12-31   | $75         |

As this table grows past millions or even billions of records, simple queries and maintenance tasks become infeasible on a single node.  

#### After Sharding: Distributed Orders Tables

To alleviate these problems, the company decides to shard the “Orders” table based on **OrderDate**. This approach splits the massive single table into smaller, more manageable chunks—each chunk stored on a different database server or instance.

**Sharding Approach: Range-Based (by Month)**

I. **Logical Partitioning**  

- Each month’s orders go into its own shard (e.g., January, February, etc.).  
- Physically, each shard could be a separate database instance or a separate schema on different servers.

II. **Data Routing**  

- The application’s data access layer inspects the `OrderDate` of an incoming query.  
- Based on the month, it routes the query to the correct shard.  
- For example, a query for orders in January 2021 automatically goes to the “January 2021” shard.

**Shard January (Shard 1):**

| OrderID | CustomerID | OrderDate    | TotalAmount |
|---------|------------|--------------|-------------|
| 1       | 101        | 2021-01-10   |$150        |
| 2       | 102        | 2021-01-11   | $200        |
| …       | …          | …            | …           |

**Shard February (Shard 2):**

| OrderID | CustomerID | OrderDate    | TotalAmount |
|---------|------------|--------------|-------------|
| 5001    | 201        | 2021-02-01   |$250        |
| 5002    | 202        | 2021-02-02   | $300        |
| …       | …          | …            | …           |

Each additional month has its own dedicated shard.

**Advantages**

- **Improved** query performance allows queries for a single month's orders to only touch that month’s shard, drastically reducing the dataset size per query.
- **Indexes** on each shard are smaller and more efficient to maintain.
- **Scalability** and load distribution are enhanced as each shard (month) can be placed on separate hardware, preventing any single server from being overwhelmed by the entire dataset.
- **Growth** can be managed effectively as new months or years are assigned to freshly provisioned servers with minimal disruption.
- **Operational** flexibility includes targeted maintenance, such as moving historical data to cheaper storage, simplified backups, and fault isolation to maintain availability.

**Operational Considerations**

- **Dynamic** range splitting allows systems to on-the-fly split hot ranges into smaller sub-ranges, spreading the load over additional shards.
- **Partitioning** decisions involve mapping each range to a separate physical database instance or a table partition within a larger instance, depending on hardware resources and failover strategies.

**Challenges:**

- Generating a sales report spanning multiple months requires querying each relevant shard. This can involve additional complexity in the application layer or a dedicated query router that merges results.  
- Data analysts must be aware that “Orders” is no longer a single table but a collection of partitions.
- If one particular month (e.g., during a major sale event) has disproportionately more orders than others, the shard for that month might receive heavier read/write traffic.
- If the business continues to grow, each monthly shard will also get larger. Eventually, monthly partitions might need to become weekly or daily partitions to keep shards small and query performance high.

### Selecting a Sharding Key

The **sharding key** is crucial because it decides how data is split. A poor choice can lead to uneven data distribution or inefficient query patterns. An ideal key aligns with the **application’s data access** and **growth patterns**.

#### Factors to Consider

I. **Uniform Data Distribution**  

- Ensuring shards are balanced in terms of storage size and query load prevents a few shards from becoming hotspots.  
- If traffic is naturally skewed (e.g., certain months or certain users are heavily used), more sophisticated strategies like dynamic splitting or directory-based sharding might be required.

II. **Query Patterns**  

- If the majority of queries filter by date (e.g., “get orders from last month”), sharding by `OrderDate` makes sense.  
- If queries mostly filter by `CustomerID`, consider using `CustomerID` as a key instead, so each customer’s orders reside on a single shard.  
- For analytical workloads spanning entire datasets, be prepared to do cross-shard joins or aggregations.

III. **Future Scalability**  

- Consider how fast your data grows. A fixed range strategy (e.g., monthly) might suffice for some time, but if the data grows exponentially, you might need more frequent partitioning (e.g., daily or weekly).  
- Evaluate how easy it is to add new shards or rebalance existing shards as the database grows.

IV. **Operational Complexity**  

- Simpler keys (e.g., hashing a single column) are easier to implement but can complicate certain query types.  
- More flexible approaches (like directory-based sharding) require additional infrastructure (a directory service) and can be more operationally intensive but provide finer control.

#### Example Sharding Keys

I. **UserID**  

- Applicable to systems heavily centered around individual user data (profiles, preferences, history).  
- Typically results in a balanced distribution if user IDs are sequential or assigned randomly.  
- Potential Issue: “Whales” or “power users” might generate more data than average, creating some imbalance.

II. **Geographic Location**  

- Ideal for region-specific data (e.g., content delivery, localized promotions, compliance with data residency laws).  
- Can serve users with minimal latency by localizing data.  
- Potential Issue: Large population centers (e.g., New York, Tokyo) might accumulate significantly more data or traffic than smaller regions.

III. **Date/Time**  

- Best for time-series or chronologically queried data (e.g., logs, metrics, orders).  
- Eases archiving and purging of old data (drop old shards).  
- Potential Issue: Seasonal spikes or large volume in certain time periods can create load imbalances.

### Sharding Strategies

There are several ways to decide how data is distributed across shards. Each method handles data placement, query routing, and shard expansion differently.

#### Range-Based Sharding

- Divide data into contiguous ranges of values based on the sharding key.
- Each range is assigned to a specific shard.

**Example Setup (By UserID):**

- **Shard 1:** User IDs 1 – 1,000,000  
- **Shard 2:** User IDs 1,000,001 – 2,000,000  
- **Shard 3:** User IDs 2,000,001 – 3,000,000  

**Advantages**

- If you need to query User IDs 1,500,000 to 1,600,000, you can directly go to **Shard 2**.
- It offers **simplicity**, making it easy to conceptualize, set up, and maintain if data distribution is somewhat uniform.

**Disadvantages**

- If the majority of users have high IDs, such as newly registered users, the last shard might receive all the **write** traffic.
- Splitting or merging shards to rebalance data can be **operationally** intensive, requiring data to be migrated to a new range or merged with another shard.

**Operational Considerations**

- Implementing **dynamic** range splitting allows systems to on-the-fly split hot ranges into smaller sub-ranges, spreading the load over additional shards.
- Deciding between **physical** and logical partitions involves mapping each range to a separate physical database instance or a table partition within a larger instance, depending on hardware resources and failover strategies.

#### Hash-Based Sharding

Compute a hash of the sharding key and use the hash value (mod the number of shards) to assign the data to a shard.

```
shard_index = hash(UserID) % shard_count
```

**Advantages**

- Hashing typically ensures a **balanced** distribution of data and traffic, preventing any single shard from becoming a hotspot unless there is extreme skew in the key distribution.
- It allows for **predictable** lookups for single keys, enabling you to determine exactly which shard to query by computing the hash.

**Disadvantages**

- Hashing does not support **natural** range queries, so operations like “get all orders from IDs 1,000 to 2,000” must either check all shards or rely on an external index.
- Adding or removing shards is **difficult** because changing the shard count alters the modulo operation, often requiring data to be rehashed and moved across shards unless consistent hashing is implemented.

**Operational Considerations**

- Implementing **consistent** hashing can reduce data movement during cluster expansions or contractions, but it adds complexity to the hashing mechanism.
- Managing **cross-shard** joins for large analytical queries may require a coordinator or aggregator layer that fetches data from all shards and merges the results.

#### Directory-Based Sharding

- Maintain a **central directory** or metadata service that maps specific keys or key ranges to particular shards.  
- When the application receives a query, it checks the directory to see which shard(s) to query.

**Example Directory Mapping (By Ranges):**

| Key Range            | Shard   |
|----------------------|---------|
| User IDs 1–500,000   | Shard A |
| User IDs 500,001–1,000,000 | Shard B |
| User IDs 1,000,001–2,000,000 | Shard C |

**Advantages**

- The system can change assignments on the fly, making it **flexible** and dynamic without the need to recalculate hashes.
- It offers **fine-grained** control, allowing you to handle exceptional cases by assigning specific ranges to different shards.

**Disadvantages**

- Incorporating the directory or mapping service introduces **complexity**, as it must remain highly available and consistent.
- The directory can become a **potential** bottleneck if not properly replicated or cached, acting as a single point of failure or limiting performance.

**Operational Considerations**

- Implementing **caching** for directory data helps avoid network round-trips for every query but requires a strategy for cache invalidation when mappings change.
- Utilizing **autonomous** range splits allows advanced systems to detect shard hotspots automatically and split them, updating the directory as necessary.

### Handling Cross-Shard Queries

Cross-shard queries arise when data needed for a query is **distributed** across multiple shards rather than contained in a single shard. In a sharded environment, each shard holds a subset of the total dataset. Consequently, operations that must combine or aggregate data from multiple shards introduce additional complexity.

#### Concrete Example

**Scenario:**

I. You have a `users` collection sharded by `user_id`.  

II. User IDs are **hashed** to evenly distribute user documents across Shard A, Shard B, and Shard C.  

**Cross-Shard Query Use Case:**

- A request comes in to list all users who signed up within the past 24 hours.
- Since sign-up timestamps are **not** the shard key (which is `user_id`), those timestamp-based records could be scattered across all shards.
- The application or query engine must reach out to **every** shard, filter by the sign-up time, then merge the results into a single response.

#### Key Considerations for Cross-Shard Queries

I. **Parallel Query Execution**  

- The query is dispatched to all shards simultaneously, each shard performs filtering locally, and partial results are returned.  
- A coordinator node or application layer merges these partial results, potentially sorting or further aggregating to produce the final dataset.

II. **Data Duplication or Global Indices**  

- Some architectures maintain a **global secondary index** or a specialized summary table that holds aggregated data (e.g., sign-up timestamps), reducing the need to scan every shard.  
- This technique can accelerate cross-shard queries but introduces additional **consistency** burdens—updates to the global index must stay in sync with the underlying shard data.

III. **Increased Overhead**  

- Dispatching queries to multiple shards and merging results can be time-consuming, especially as the number of shards grows.  
- Network latency and coordination overhead can degrade performance if not carefully optimized or cached.

IV. **Consistency and Freshness**  

- If data is replicated or cached across shards, ensuring that each shard returns **consistent** information is more complex than in a single-database scenario.  
- Systems may adopt **eventual consistency** models for global views or rely on distributed transaction protocols to guarantee consistency at the cost of performance.

### Practical Implementation with MongoDB

MongoDB provides **native** support for sharding, which automates many tasks such as data distribution, balancing, and routing. However, understanding how it works behind the scenes helps you design and operate a sharded cluster effectively.

#### Will This Work Out of the Box?

I. **Automated Routing**  

- MongoDB’s query router (mongos) automatically determines which shard(s) hold the relevant data.  
- If the query’s filter uses the shard key (e.g., `user_id`), MongoDB routes the request to the appropriate shard only.  
- If the query does **not** filter on the shard key, MongoDB sends a “scatter-gather” operation to **all** shards, and then merges the results.

II. **Balancer**  

- Behind the scenes, MongoDB’s balancer monitors each shard’s storage load and will **migrate** chunks of data between shards to even things out.  
- This process is typically transparent to the application, though it can introduce slight performance overhead during migrations.

III. **Local Copies vs. Managed Shards**  

- You can set up multiple local copies of MongoDB on your own servers (each acting as a shard and a replica set for high availability) or use a cloud-managed MongoDB service (like Atlas).  
- In both cases, MongoDB handles the distribution of data and queries, but the operational details (upgrades, monitoring, failover) may be simpler with a managed service.

#### Example Commands

I. **Enable Sharding on Database**  

```javascript
sh.enableSharding("myDatabase")
```

Tells MongoDB that you intend to distribute collections in `myDatabase` across multiple shards.

II. **Choose a Shard Key**  

- Carefully select a field that will distribute data evenly and align with common query patterns.  
- Example: `user_id` hashed for uniform distribution.

III. **Shard the Collection**  

```javascript
sh.shardCollection("myDatabase.users", { "user_id": "hashed" })
```

 Instructs MongoDB to distribute the `users` collection using a hash of the `user_id` field.

#### Query Routing Examples

**Single Shard Query**  

```javascript
db.users.find({ "user_id": 12345 })
```

Because the shard key is specified (`user_id`), MongoDB routes this query **directly** to the single shard holding documents with `user_id` 12345.

**Broadcast Query**  

```javascript
db.users.find({ "age": {$gte: 18 } })
```  

Since `age` is not the shard key, MongoDB must **broadcast** this query to all shards, collect partial results, and merge them before returning the final result.

### Real-World Use Case: Twitter's Timeline Storage

Twitter processes **millions** of tweets per day and needs to store and retrieve them efficiently. Sharding is a important part of making sure low-latency access and high availability.

#### Challenges

I. **Massive Data Ingestion**  

- During peak events (e.g., breaking news, sports), Twitter sees huge spikes in tweet volume.  
- The underlying data storage layer must handle high write throughput without degrading performance.

II. **Rapid Retrieval**  

- Users expect to see their timeline updates in near real-time.  
- Systemic delays or failures in retrieving tweets would negatively impact the user experience.

#### Sharding Strategy

I. **User-Based Sharding**  

- Tweets are distributed across shards based on `UserID`.  
- All tweets from a specific user reside on the same shard, making it easy to fetch a user’s entire tweet history quickly.

II. **Even Load Distribution**  

- Because Twitter’s user base is massive and users are fairly well-distributed, using `UserID` helps balance storage across shards.  
- However, “power users” (accounts with extremely high tweet volume) can still create hotspots, so Twitter may have additional strategies to handle these cases.

#### Handling Cross-Shard Operations

I. **Aggregation Services**  

- A specialized aggregation service compiles tweets from various shards to build a user’s **home timeline** (tweets from users they follow).  
- This aggregator queries the relevant shards in parallel and merges results, adding filtering or ranking logic as needed.

II. **Caching Layers**  

- Caches like Redis store recently generated or frequently accessed timelines.  
- This caching mechanism reduces read pressure on the underlying shard infrastructure and speeds up user-facing queries.

### Best Practices for Sharding

Carrying out a sharded architecture effectively requires **strategic planning** and **ongoing maintenance** to make sure that performance, consistency, and operational costs are well-managed.

I. Understand Your Data and Access Patterns

- Analyzing **common** queries helps identify which fields your application frequently filters or sorts on.
- Determining **natural** partitions involves assessing if your data naturally segments by time, region, user, or other criteria.
- Recognizing **data** skew allows you to anticipate potential hotspots, such as specific months, users, or regions.

II. Plan for Scalability

- Selecting a **flexible** shard key ensures that your data can expand gracefully as it changes over time.
- Utilizing **automated** scaling tools enables your database solution to support shard addition and rebalancing with minimal manual intervention, reducing human error and downtime.

III. Monitor and Optimize

- Tracking **key** metrics like query latency, throughput, shard disk usage, CPU/RAM utilization, and network traffic provides insights into system performance.
- Performing **rebalancing** shards periodically ensures that data distribution remains even, which may involve splitting or merging shards or adjusting chunk sizes.
- Refining **shard** keys may be necessary if usage patterns shift drastically, potentially requiring partial re-sharding.

IV. Handle Failures Gracefully

- Implementing **redundancy** through replication within shards ensures high availability in case a primary node fails.
- Establishing **failover** mechanisms allows automatic switching to replicas or backups, preventing downtime from hardware or network issues.
- Developing a **disaster** recovery strategy for restoring backups in a sharded environment is essential, and regularly testing these procedures ensures their effectiveness.

### Challenges of Sharding

While sharding improves scalability and performance for high-volume applications, it also introduces **new complexities** that must be carefully managed.

I. Increased System Complexity

- Managing **application logic** becomes more intricate as the system must handle routing queries to the appropriate shards.
- Ensuring **scalability** requires careful planning to distribute data evenly across shards.
- Implementing **failure detection** mechanisms is necessary to identify and respond to shard outages promptly.
- Coordinating **schema changes** across multiple shards demands meticulous synchronization to maintain consistency.
- Designing **load balancing** strategies is essential to prevent any single shard from becoming a bottleneck.

II. Data Consistency

- Maintaining **referential integrity** across shards complicates the enforcement of relationships between different data sets.
- Achieving **synchronization** of data updates requires efficient protocols to minimize inconsistencies.
- Implementing **conflict resolution** strategies is necessary when concurrent updates occur on different shards.
- Monitoring **data replication** ensures that all shards have the most recent and accurate information.
- Establishing **version control** for data helps track changes and maintain consistency across the system.

III. Operational Overhead

- Coordinating **deployment processes** across multiple shards increases the complexity of releasing updates.
- Managing **resource allocation** requires monitoring each shard's performance to optimize usage.
- Ensuring **security measures** are uniformly applied across all shards protects the system from vulnerabilities.
- Automating **maintenance tasks** helps reduce the manual effort required to keep each shard operational.
- Tracking **system metrics** from various shards provides comprehensive insights into overall system health.

IV. Performance Challenges

- Optimizing **query performance** across shards demands efficient indexing and caching strategies.
- Minimizing **latency** involves strategically placing shards to reduce data retrieval times.
- Balancing **read and write operations** ensures that neither overwhelms any single shard.
- Implementing **parallel processing** can enhance performance but requires careful coordination.
- Monitoring **throughput rates** helps identify and address performance bottlenecks promptly.

V. Cost Implications

- Scaling **infrastructure** to accommodate multiple shards can lead to increased operational costs.
- Investing in **automation tools** may be necessary to manage the complexity of a sharded system efficiently.
- Allocating **budget for monitoring** ensures that all shards are consistently tracked for performance and issues.
- Balancing **resource utilization** helps manage costs by optimizing the use of existing infrastructure.
- Planning for **future expansion** involves budgeting for additional shards as data grows.
