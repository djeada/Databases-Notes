## Partitioning vs. Sharding

When a database begins to sag under the weight of its own success, engineers reach for two closely-related remedies: *partitioning* and *sharding*. Both techniques carve a huge dataset into smaller slices, yet they do so at very different depths of the stack. By the time you finish these notes you should feel comfortable answering why, when, and how each approach shines, along with the trade-offs hiding beneath the surface.

After reading the material, you should be able to answer the following questions:

1. In plain language, how does partition pruning differ from query routing in a sharded setup?
2. When would list partitioning outperform hash partitioning, and why?
3. What failure scenarios does sharding mitigate that partitioning alone cannot?
4. How does the two-phase commit protocol address multi-shard transaction consistency?
5. Imagine a write-heavy workload with seasonal spikes; sketch a hybrid design combining both techniques to tame those spikes.

### Partitioning

Before diving into syntax or strategies, picture a single table stretching far beyond your screen. By splitting that table into *partitions* the database can prune irrelevant chunks during a query and treat maintenance tasks like backups or index rebuilds piece-by-piece rather than all-at-once. Think of it as shelving volumes in a giant library rather than piling every book on one table.

```
┌─────────────────────────────┐
│        big_sales            │
│ ─────────────────────────── │
│  2023-01-…  ▸ Partition p23 │
│  2024-01-…  ▸ Partition p24 │
│  2025-01-…  ▸ Partition p25 │
└─────────────────────────────┘
```

#### How the Database Decides Where a Row Lands

Although every engine offers its own bells and whistles, five patterns dominate:

* Range partitioning slices by continuous spans such as dates or ID intervals, ideal when queries naturally filter by that range.
* List partitioning corrals discrete categories—for example, country codes or product tiers—into their own sections.
* Hash partitioning sends each row through a hash function, scattering hot spots and keeping partitions roughly the same size.
* Key partitioning piggybacks on the primary key, guaranteeing uniqueness is preserved inside each fragment.
* Composite partitioning layers one technique atop another (range → hash is common) for workloads with multiple access patterns.

Mathematically you can model a simple range splitter with

$$
partition_{id} =
\left\lfloor
  \frac{row_{value}-\min}{\Delta}
\right\rfloor$$

where $\Delta$ is the chosen interval width.

#### Hands-On: PostgreSQL Range Partitioning

Let's take a look at some examples:

**Create the parent (partitioned) table**

```sql
CREATE TABLE orders (
  id         bigint,
  order_date date,
  amount     numeric
) PARTITION BY RANGE (order_date);
```

**psql output:**

```
CREATE TABLE
```

* By specifying `PARTITION BY RANGE (order_date)`, you tell PostgreSQL that `orders` won’t store rows itself but will route them to child tables based on the `order_date` value.
* The parent table holds no data; it acts like an index on date ranges. Any insert into `orders` is automatically redirected to whichever child partition matches.
* Useful when your data has a natural order (e.g., time series), so you can group rows into contiguous non‐overlapping spans—improving manageability and performance.

**Define a specific partition for the year 2025**

```sql
CREATE TABLE orders_2025
  PARTITION OF orders
  FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
```

**psql output:**

```
CREATE TABLE
```

* `orders_2025` is now a real table that will physically contain all rows whose `order_date` ≥ 2025-01-01 and < 2026-01-01.
* The `FROM` value is inclusive, the `TO` value is exclusive. This ensures partitions don’t overlap and every date is covered exactly once (assuming you add adjacent ranges).
* From here on, any insertion like

```sql
INSERT INTO orders (id, order_date, amount)
VALUES (123, '2025-05-05', 49.95);
```

will go straight into `orders_2025` without touching other partitions.

**Verify partition pruning with an `EXPLAIN`**

```sql
EXPLAIN SELECT * FROM orders WHERE order_date = '2025-05-05';
```

**psql output:**

```
->  Seq Scan on orders_2025  (cost=0.00..35.50 rows=5 width=...)
```

* **Planner insight:** Instead of scanning every partition in turn, PostgreSQL’s planner “prunes” away all that don’t match the `WHERE` clause at plan time.
* **Only one scan:** You see only `orders_2025` in the plan, proving that lookups on `orders` automatically get optimized to target just the relevant partition.
* **Performance gain:** Partition pruning can drastically reduce I/O and CPU work, especially when you have many partitions (e.g., one per month or year).

#### Decoding Common Options

| Keyword / Option           | Meaning                                              | Typical Use-Case                                             |
| -------------------------- | ---------------------------------------------------- | ------------------------------------------------------------ |
| `PARTITION BY RANGE (...)` | Chooses range strategy and the key column(s)         | Time-series or numeric intervals                             |
| `FOR VALUES FROM () TO ()` | Declares the lower-inclusive, upper-exclusive bounds | Adjacent partitions must not overlap                         |
| `DEFAULT PARTITION`        | Catch-all for rows that fit no explicit slice        | Shields you from insert errors when ranges lag behind growth |

#### Why Teams Embrace Partitioning

Query latency drops because only relevant partitions are scanned. Maintenance windows shrink: vacuuming a quiet 2022 table can happen while 2025 receives writes. Resource allocation becomes flexible; you might place cold partitions on slower disks. Even fault isolation improves—a corrupt partition rarely topples the rest of the schema.

### Sharding

While partitioning rearranges furniture within one house, sharding is more like buying extra houses in new neighborhoods. Each *shard* is a full database instance containing a subset of the rows, and together they form a loose federation under the application layer.

```
                ┌───────────────┐
     Client  ►  │ Router / API  │
                └────┬───┬──────┘
                     │   │
        ┌────────────┘   └────────────┐
   ┌─────────────┐               ┌─────────────┐
   │  Shard A    │               │  Shard B    │   …
   │ users 1-N/2 │               │ users N/2+1 │
   └─────────────┘               └─────────────┘
```

#### Motivations That Push Teams Toward Shards

A single server inevitably runs out of CPU, memory, or I/O bandwidth. By sprinkling data across multiple machines the system gains horizontal scalability. Query throughput rises because shards answer requests in parallel. Resilience improves as well; if shard B disappears during a nightly redeploy shard A soldiers on, keeping part of the application available.

#### Popular Strategies for Splitting the Data

* Range-based sharding collects logically adjacent rows (for example, user IDs 1–1 000 000) on the same host, which simplifies range queries at the cost of potential hot shards.
* Hash-based sharding feeds the sharding key through a hash and assigns modulo-based buckets, making load nicely uniform but scattering neighbor records.
* Directory-based sharding stores a mapping table (often called a *lookup service*) telling the router exactly where each key lives, favoring flexibility over pure mathematical routing.

#### Hands-On: MongoDB Hash Sharding

Below you’ll see each shell command, the trimmed MongoDB response, and an expanded explanation—still in a single‐level list for clarity.

**Enable sharding on the target database**

```js
sh.enableSharding("ecommerce");
```

**Shell output:**

```json
{ "ok" : 1 }
```

* This tells the cluster’s config servers that the `ecommerce` database is now eligible to have its collections distributed across shards.
* Existing collections remain untouched until you shard them explicitly.
* You must enable sharding on a database before you can shard any of its collections.

**Shard a specific collection using a hashed key**

```js
sh.shardCollection("ecommerce.orders", { "user_id" : "hashed" });
```

**Shell output:**

```json
{ "collectionsharded" : "ecommerce.orders", "ok" : 1 }
```

* By choosing `{ user_id: "hashed" }`, you tell MongoDB to compute a hash of each document’s `user_id` field and use that to assign it to a chunk.
* The system splits the key’s hash space into multiple chunks (default 2 per shard initially) to start distributing data.
* As data grows, the balancer process will migrate chunks among shards to even out storage and load.

* **Inspect how data is distributed across shards**

```js
db.orders.getShardDistribution();
```

**Shell output:**

```
Shard shard0000: 45% data
Shard shard0001: 55% data
```

* This utility reports the approximate percentage of documents or data size on each shard for the `orders` collection.
* A near‐even split (45% vs 55%) confirms the hash function is effectively spreading user records across shards.
* Use this periodically to catch hotspots; if one shard drifts too far in usage, you can trigger a manual rebalance or adjust chunk settings.

#### Unpacking Key Flags

| Flag / Parameter                 | What It Controls                                              | Insight                              |
| -------------------------------- | ------------------------------------------------------------- | ------------------------------------ |
| `"hashed"` in `shardCollection`  | Routing is based on the hash of the key rather than raw value | Avoids regional hot spots            |
| `--chunkSize` in `mongos` config | Maximum chunk (sub-shard) size in MB                          | Smaller chunks migrate more smoothly |
| `balancerStopped`                | Boolean to pause automatic rebalancing                        | Handy during peak traffic windows    |

### Side-by-Side Comparison

| Dimension              | Partitioning                                       | Sharding                                                  |
| ---------------------- | -------------------------------------------------- | --------------------------------------------------------- |
| Where data lives       | One database engine, multiple internal segments    | Many engines, each a self-contained database              |
| Primary goal           | Speed up queries and maintenance                   | Add capacity beyond a single server                       |
| Transaction scope      | Usually local and ACID-compliant across partitions | Cross-shard transactions require 2PC or application logic |
| Operational complexity | Moderate—DDL and monitoring remain centralized     | Higher—orchestration, failover, and backups multiply      |
| Growth path            | Vertical (bigger box) until vertical limits hit    | Horizontal from day one                                   |

### Blending the Two

Large platforms often partition *inside* every shard, marrying the easy pruning of partitions with the elastic headroom of shards. For example, an e-commerce company might hash-shard by user ID and range-partition each shard’s `orders` table by month, yielding fast user look-ups *and* swift archival of old months.

### Practical Guidance

* Start with partitioning if the bottleneck is query latency over a single giant table or if maintenance tasks have become unwieldy.
* Plan for sharding once you foresee the primary server exhausting resources even after aggressive tuning.
* Prototype tooling and disaster-recovery workflows early; complexity compounds quickly once dozens of shards are in play.
* Keep the sharding key stable—re-sharding live traffic is far more painful than migrating partitions.
* Monitor chunk or partition skew by calculating the coefficient of variation ${\sigma}/{\mu}$; when that value drifts upward, rebalance before hotspots burn users.
