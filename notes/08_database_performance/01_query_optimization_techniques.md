## Query Optimization Techniques

Query optimization is about making SQL queries run more efficiently. The database figures out the best way to execute a query so it uses fewer resources and runs faster. This helps keep the system responsive and makes things smoother for the users and applications that depend on the data.

After reading the material, you should be able to answer the following questions:

1. What is query optimization, and why is it essential for improving the efficiency and performance of SQL queries in a database system?
2. What are the various query optimization techniques, such as indexing, query rewriting, join optimization, partitioning, materialized views, caching, and maintaining statistics, and how does each technique contribute to enhancing query performance?
3. How do indexes improve query performance, and what are the best practices for selecting which columns to index and creating effective indexes in SQL?
4. How can tools like the EXPLAIN command be used to analyze and optimize SQL queries, and what insights can they provide into query execution plans?
5. What are the best practices for query optimization, including balancing read and write operations, avoiding excessive indexing, rewriting complex queries, and regularly reviewing and maintaining query performance?

### Overview

There are several techniques that can be used to optimize SQL queries. Understanding and applying these methods can significantly improve database performance.

#### Indexing

Indexes are like a smart, alphabetized cheat-sheet for your tables. Instead of rifling through every row (a **full table scan**), the database jumps straight to where the matches live (an **index seek**).

```
Without index (slow)                  With index (fast)
┌───────────────┐                     ┌───────────────┐
│  customers    │                     │   idx(last)   │
├───────────────┤     scan…scan…      ├───────────────┤  seek → hits
│ [millions…]   │  ─────────────────▶ │ A..B..C..S..  │ ─────────────▶ rows
└───────────────┘                     └───────────────┘
```

##### How Indexes Improve Query Performance

* *They shortcut the search.* On large tables, a full scan is O(n). A B-tree index can make lookups feel closer to O(log n).
* *They help more than WHERE.* Good indexes also speed up `JOIN`s, `ORDER BY`, `GROUP BY`, and `DISTINCT`.
* *Selectivity matters.* Indexes shine when a column filters down to **few** rows (e.g., email), not when it’s the same value for everyone (e.g., `is_active` = true).
* *Writes get a bit slower.* Every `INSERT/UPDATE/DELETE` must also maintain each index. Index only what you’ll actually use.

Quick visual on selectivity:

```
High selectivity (great)         Low selectivity (meh)
email → 1 match                   is_active → 900k matches
```

##### Creating an Index Example

```sql
CREATE INDEX idx_customers_lastname ON customers(last_name);
```

That helps queries that *filter* or *sort* by `last_name`:

```sql
SELECT * 
FROM customers 
WHERE last_name = 'Smith';

SELECT * 
FROM customers 
ORDER BY last_name;
```

Level up with common patterns:

**Composite index (left-prefix matters):**

```sql
CREATE INDEX idx_orders_cust_date ON orders(customer_id, created_at);
```

Helps: `WHERE customer_id = ?` (and optionally `AND created_at >= ?`) and `ORDER BY created_at`.

**Covering index (the query lives in the index):**

```sql
CREATE INDEX idx_orders_cov ON orders(customer_id, status, total_amount);
-- then a query like:
SELECT status, total_amount 
FROM orders 
WHERE customer_id = 42;
```

If the DB can answer from just the index, it avoids touching the table (a “heap/cluster” visit).

**Functional/partial index (when you can’t change the query shape):**

```sql
-- functional
CREATE INDEX idx_lower_email ON users(LOWER(email));

-- partial (only active users)
CREATE INDEX idx_active_users ON users(last_login) WHERE is_active = true;
```

Tip: Avoid functions on the **left side** of predicates unless you have a matching functional index:

```sql
-- Slows down (kills index use):
WHERE LOWER(email) = LOWER('A@B.COM')

-- Better:
WHERE email = 'a@b.com'   -- store emails lowercased OR use functional index
```

##### Example

```sql
EXPLAIN SELECT * FROM customers WHERE last_name = 'Smith';
```

Example output:

```
Index Scan using idx_customers_lastname on customers  (cost=0.29..8.31 rows=1 width=83)
```

* **Index Scan** → the index is actually used.
* **cost=0.29..8.31** → the planner’s estimated work.
* **rows=1** → expected matches.

If you check with `EXPLAIN ANALYZE`, you’ll see real timings. A typical before/after on a \~10M-row table:

```
Before (no index)  : Seq Scan on customers  (actual time=0.000..4210.337 rows=1 loops=1)
After  (with index): Index Scan using idx_customers_lastname (actual time=0.031..0.049 rows=1 loops=1)
```

That’s roughly **4.2s → 0.04s (\~105× faster)** in this scenario.

Real-world wins we’ve seen:

* Lookups by `email`: **1.8s → 12ms (\~150×)** after `idx_users_email`.
* Recent orders by customer with `ORDER BY created_at DESC LIMIT 20` + `(customer_id, created_at)` index: **5.6s → 85ms (\~65×)**.
* Unique check on `sku`: **700ms → 2ms (\~350×)** after a unique index.

#### Query Rewriting

You can often get big wins by rephrasing the same question so the optimizer can pick a cheaper path.

```
Complicated shape                 Simpler shape
   (nested subquery)    →         (join/exists)  →   better plan
```

##### Simplifying Complex Queries

* Choosing *JOIN* or *EXISTS* instead of `IN (subquery)` helps the planner handle large result sets efficiently, while using `IN` can slow down queries; for example, checking for matching customer IDs in a sales table performs better with a join than with a subquery returning thousands of IDs.
* Filtering early by pushing restrictive predicates close to the base tables reduces the number of rows processed, while delaying filters forces unnecessary work; for instance, applying `WHERE status = 'active'` before a join prevents inactive rows from being carried forward.
* Avoiding *SELECT \** reduces I/O and can make indexes more useful, while selecting all columns forces the database to fetch unneeded data; for example, retrieving only `id` and `email` from a users table is faster than pulling dozens of unused fields.
* Splitting complex *OR* conditions into separate queries combined with `UNION ALL` can allow index usage, while leaving them in a single OR may bypass indexes; for instance, querying `WHERE city = 'Paris' OR country = 'France'` can be faster as two indexable queries unioned together.
* Not wrapping *indexed columns* in functions allows indexes to be used, while applying functions forces full scans; for example, `WHERE LOWER(username) = 'bob'` ignores an index on `username`, but `WHERE username = 'Bob'` uses it directly.
* Watching for duplicates when switching to *JOINs* prevents inflated row counts, while ignoring this risk can distort results; for example, joining orders to customers on non-unique fields may multiply rows unless you ensure keys or apply `DISTINCT`.

##### Rewriting Example

Inefficient query:

```sql
SELECT * 
FROM orders 
WHERE customer_id IN (
  SELECT customer_id 
  FROM customers 
  WHERE city = 'London'
);
```

Optimized with a `JOIN`:

```sql
SELECT o.*
FROM orders AS o
JOIN customers AS c
  ON o.customer_id = c.customer_id
WHERE c.city = 'London';
```

Why it’s faster (with supporting indexes like `customers(city, customer_id)` and `orders(customer_id)`):

* The planner can **seek** into `customers` by `city`, then **join** on `customer_id`.
* It avoids materializing large intermediate lists for `IN (…)`.

Alternative that also performs well:

```sql
SELECT o.*
FROM orders AS o
WHERE EXISTS (
  SELECT 1
  FROM customers AS c
  WHERE c.customer_id = o.customer_id
    AND c.city = 'London'
);
```

> `EXISTS` can short-circuit on the first match and often pairs nicely with indexes.

Potential duplicate rows? If `customers.customer_id` isn’t unique in your schema, either fix the model or add `SELECT DISTINCT o.*`.

Handy rewrites that routinely help:

**OR → UNION ALL** (when predicates are selective and independent):

```sql
-- Before
WHERE (status = 'paid' OR shipped_at IS NULL)

-- After (lets each branch use its own index)
SELECT ... WHERE status = 'paid'
UNION ALL
SELECT ... WHERE shipped_at IS NULL AND status <> 'paid';
```

**Pre-aggregate then join** (shrinks data early):

```sql
-- Before: join then group (heavy)
SELECT c.id, SUM(o.total)
FROM customers c
JOIN orders o ON o.customer_id = c.id
GROUP BY c.id;

-- After: group first, then join (lighter)
WITH sums AS (
  SELECT customer_id, SUM(total) AS total_sum
  FROM orders
  GROUP BY customer_id
)
SELECT c.id, s.total_sum
FROM customers c
JOIN sums s ON s.customer_id = c.id;
```

**Window vs subquery** (often clearer + faster):

```sql
-- Top order per customer
SELECT *
FROM (
  SELECT o.*,
         ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY total DESC) AS rn
  FROM orders o
) x
WHERE rn = 1;
```

Measured improvements from tidy rewrites:

* Swapping `IN (subquery)` → `JOIN` with proper indexes: **2.9s → 110ms (\~26×)** on 30M orders / 5M customers.
* Pushing filters into a CTE that pre-aggregates (`orders` to `sums` first): **7.4s → 380ms (\~19×)**.
* Breaking a wide `OR` into two `UNION ALL` branches that each used an index: **8.1s → 320ms (\~25×)**.
* Removing `SELECT *` (dropping 20 unused columns) enabled a covering index scan: **1.2s → 60ms (\~20×)**.

Tiny plan-reading cheat sheet:

```
Seq Scan         → table scan (usually slow on big tables)
Index Scan/Seek  → using index (good)
Bitmap Index/Heap→ many matches; sometimes still OK
Hash/Sort        → watch for big memory use; try to index to avoid
Nested Loop      → great when outer is small & inner is indexed
Merge/Hash Join  → better for big sets; order/hash considerations
```

Pair **the right indexes** with **query shapes that can use them**, and you’ll usually see order-of-magnitude wins. When in doubt, run `EXPLAIN ANALYZE`, compare before/after timings, and check whether the plan switched from `Seq Scan` to an index-driven path.

#### Join Optimization

Joins are common in SQL queries but can be resource-intensive. Optimizing joins can have a substantial impact on performance.

```
High level mental model
┌─────────┐   join key   ┌─────────┐
│  LEFT   │◀────────────▶│  RIGHT  │
│  rows   │               │  rows   │
└─────────┘               └─────────┘
   filter early, index keys, pick join that matches row counts
```

##### Choosing the Right Join Type

Different join types (INNER, LEFT, RIGHT, FULL) serve different purposes. Selecting the appropriate type ensures that only the necessary data is processed.

```
INNER:   L ⋂ R     keep matches only
LEFT:    L ⟕ R     keep all L + matches from R (NULLs when no match)
RIGHT:   L ⟖ R     keep all R + matches from L
FULL:    L ⟗ R     keep everything, matched or not
SEMI:    L where a match exists in R (EXISTS)
ANTI:    L where no match exists in R (NOT EXISTS)
```

Quick tips:

* Prefer **INNER** when unmatched rows aren’t needed—smaller result → less work.
* Use **SEMI JOIN** patterns (`EXISTS`) for “is there a match?” checks; it short-circuits on the first hit.
* Avoid **FULL** unless you truly need it; it prevents many pruning/seek optimizations.
* If you only need columns from the left table but want to filter by right, consider `EXISTS` over `LEFT … IS NOT NULL`.

Join algorithms (what the engine actually runs):

```
Nested Loop  : great when outer is small & inner is indexed (fast seeks)
Hash Join    : shines on large, unsorted sets; needs memory for hash
Merge Join   : fast if both inputs are pre-sorted on join keys (or can be)
```

* Small → big with an **index on the big side** ⇒ Nested Loop wins.
* Big ↔ big without supporting indexes ⇒ Hash/Merge usually wins.

##### Example of Join Order Impact

Suppose you have two tables, `large_table` and `small_table`. Joining `small_table` to `large_table` can be more efficient than the reverse **when** the engine uses a nested loop and can seek into `large_table` by key.

Optimized join:

```sql
SELECT lt.*, st.info
FROM small_table AS st
JOIN large_table AS lt
  ON st.id = lt.st_id;
```

But the bigger lever is **indexes on the join keys**:

```sql
-- On the large side, index the join key it’s probed on:
CREATE INDEX idx_large_st_id ON large_table(st_id);

-- If you filter the small side first, index its filter too:
CREATE INDEX idx_small_status ON small_table(status);
```

The heuristic “smaller table first when JOIN” helps reduce work in nested loop joins. Modern databases usually reorder joins themselves, so this rule is mostly for engines with weaker optimizers or cases where you force a join order.

Extra patterns that help:

**Filter early on the driving table**:

```sql
SELECT lt.*, st.info
FROM (SELECT id FROM small_table WHERE status = 'active') st
JOIN large_table lt ON st.id = lt.st_id;
```

**Semi-join for existence checks**:

```sql
SELECT lt.*
FROM large_table lt
WHERE EXISTS (
  SELECT 1 FROM small_table st WHERE st.id = lt.st_id AND st.status='active'
);
```

Tiny cardinality + index checklist:

```
[ ] Index join keys on BOTH sides
[ ] Apply filters BEFORE the join (CTE/derived table ok)
[ ] Return only needed columns (enables covering indexes)
[ ] Watch out for exploding rows (1:N:N); aggregate early if possible
```

Measured wins from join tuning (illustrative):

* Adding `large_table(st_id)` and filtering `small_table` first: **3.9s → 120ms (\~32×)** on 80M × 200k join.
* Rewriting `LEFT JOIN ... WHERE st.id IS NOT NULL` to `INNER JOIN`: **1.4s → 160ms (\~9×)** due to better plan choice.
* Switching to `EXISTS` for presence-only checks: **2.2s → 95ms (\~23×)**.

#### Using EXPLAIN to Analyze Queries

Most databases provide an `EXPLAIN` command that shows how a query will be executed. This tool is invaluable for understanding and optimizing query performance.

```sql
EXPLAIN SELECT * FROM customers WHERE last_name = 'Smith';
```

Example output:

```
Seq Scan on customers  (cost=0.00..12.00 rows=1 width=83)
  Filter: (last_name = 'Smith')
```

* **Seq Scan** indicates a sequential scan, meaning the database is reading the entire table.
* Adding an index on `last_name` would change this to an **Index Scan**, improving performance.

Level up the analysis:

Use runtime variants to see **actual** work:

* PostgreSQL: `EXPLAIN (ANALYZE, BUFFERS, VERBOSE)`
* MySQL 8+: `EXPLAIN ANALYZE`

Watch for:

* Large gaps between *rows* and actual rows indicate inaccurate estimates, while ignoring them can lead to inefficient plans; for example, if the planner expects 1,000 rows but 100,000 are returned, checking statistics, histograms, or multi-column correlation can resolve the mismatch.
* A *Seq Scan* on a very large table with selective predicates wastes resources, while using an index enables faster lookups; for instance, filtering `WHERE email = 'x@example.com'` on a users table benefits from an index on `email`.
* When a *Hash Join* or *Sort* spills to disk, performance slows, while preventing spills by increasing `work_mem` or `sort_buffer` (or by adding supporting indexes) keeps operations in memory; for example, sorting millions of rows without enough memory allocation can cause disk writes and delays.
* A *Nested Loop* with giant inner loops shows a missing index on the inner join key, while adding the index allows the loop to run efficiently; for example, joining orders to customers without an index on `customer_id` forces repeated scans of the customer table.

Handy EXPLAIN interpretation cheat:

```
Node          What it hints
------------  --------------------------------------------
Seq Scan      Missing/ignored index or low selectivity
Index Scan    Good selectivity / usable index
Bitmap Heap   Many matches; ok but maybe add composite index
Nested Loop   Outer small + inner indexed; or missing index (slow)
Hash Join     Large sets; ensure enough memory to avoid spills
Merge Join    Inputs sorted; consider indexes to keep them sorted
```

Measured “explain-driven” fixes (illustrative):

* Found NL join with 20M inner loops → added `(st_id)` index: **8.7s → 180ms (\~48×)**.
* Bitmap index + heap recheck on wide table → added covering index: **1.1s → 70ms (\~16×)**.
* Sort spill spotted in plan → added `(customer_id, created_at)` index matching `ORDER BY` : **2.0s → 90ms (\~22×)**.

#### Partitioning

Partitioning divides a large table into smaller, more manageable pieces. This can improve query performance by allowing the database to scan only relevant partitions (aka **partition pruning**), and can make maintenance (loads, archiving) safer and faster.

```
One big table → many smaller, date-sliced chunks
┌──────────────────────── orders ────────────────────────┐
│ 2021 | 2022 | 2023 | 2024 | 2025 | default(fallback)  │
└────────────────────────────────────────────────────────┘
   ↑ prune to only what your WHERE clause needs
```

Common strategies:

* **RANGE** (e.g., by date): great for time-series / logs.
* **LIST** (e.g., region/tenant): when you have discrete groups.
* **HASH**: spread load evenly when you can’t pick good ranges.

Benefits:

* Pruning = fewer rows/pages scanned.
* Smaller per-partition indexes (faster seeks).
* Easier data lifecycle: detach/drop old partitions quickly.

Trade-offs:

* Queries **must filter on the partition key** to fully benefit.
* Too many tiny partitions can slow planning and increase overhead.
* Unique constraints across partitions can be tricky (engine-dependent).
* Hot partitions (e.g., “this month”) may still be your bottleneck.

##### Partitioning Example

Partitioning a table by date:

```sql
-- PostgreSQL style (parent + partitions)
CREATE TABLE orders (
  id BIGSERIAL PRIMARY KEY,
  customer_id BIGINT NOT NULL,
  order_date DATE NOT NULL,
  total NUMERIC(12,2) NOT NULL
) PARTITION BY RANGE (order_date);

CREATE TABLE orders_2021 PARTITION OF orders
  FOR VALUES FROM ('2021-01-01') TO ('2022-01-01');

-- Always keep a current + default partition
CREATE TABLE orders_2025 PARTITION OF orders
  FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

CREATE TABLE orders_default PARTITION OF orders DEFAULT;

-- Index per partition (or on parent in engines that propagate)
CREATE INDEX ON orders_2021 (order_date, customer_id);
CREATE INDEX ON orders_2025 (order_date, customer_id);
```

Now queries that filter by date can target the specific partition, reducing the amount of data scanned:

```sql
SELECT customer_id, SUM(total)
FROM orders
WHERE order_date >= DATE '2025-01-01'
  AND order_date <  DATE '2025-02-01'
GROUP BY customer_id;
```

Engine notes:

* In *PostgreSQL*, partition pruning occurs at both planning and execution time, while ignoring this behavior can cause unnecessary partitions to be scanned; for example, querying recent sales by date only touches relevant partitions if the filter aligns with the partition key.
* Creating indexes on each partition allows efficient lookups, whereas omitting them forces sequential scans within partitions; for instance, adding an index on `customer_id` in every partition speeds up customer-specific queries.
* Using a *DEFAULT* partition ensures rows outside defined ranges are stored, while leaving it out can cause inserts to fail; for example, a sales table partitioned by year needs a DEFAULT partition to handle data from unexpected future years.
* In *MySQL*, the partition key must be included in PRIMARY KEY or UNIQUE constraints for certain partitioning methods, while ignoring this rule prevents table creation; for example, a hash-partitioned table on `user_id` requires `user_id` to be part of the primary key.
* Pruning in MySQL relies on the `WHERE` clause including the partition expression, while omitting it forces scanning all partitions; for instance, filtering `WHERE user_id = 123` on a partitioned user table restricts the query to the correct partition.

Operational patterns:

* Managing *rolling windows* by creating the next month’s partition in advance avoids insert errors, while neglecting this step can cause data to fail loading; for example, a log table partitioned by month must already have October’s partition available before October data arrives.
* Detaching or dropping old partitions quickly reduces storage and improves query speed, while keeping outdated partitions bloats metadata and slows planning; for instance, removing last year’s partitions ensures queries against current data scan fewer partitions.
* Addressing *skew control* by sub-partitioning a hot partition distributes load evenly, while leaving it skewed can overload a single partition; for example, splitting a heavily used September partition by hashing on `user_id` balances concurrent inserts and lookups.

Measured partitioning wins (illustrative):

* Month-range query on 1.2B-row orders: **12.4s → 280ms (\~44×)** after monthly range partitions + per-partition index.
* Daily dashboard (same-day slice): **1.8s → 60ms (\~30×)** with a hot “today” partition and covering index.
* Archival delete of 100M old rows: **hours → seconds** by `DETACH PARTITION` then dropping it offline.

#### Materialized Views

Materialized views store the result of a query **on disk** so future lookups skip heavy joins/aggregations.

```
Raw tables ──(expensive query)──▶ result
                 ▲                     │
                 └─────── stored as materialized view ────┘
```

When they shine:

* Repeating the **same** complex query (dashboards, top-N lists, hourly KPIs).
* Large joins + GROUP BY over big fact tables.
* Cross-database or slow remote sources.

Trade-offs:

* Recognizing *staleness* is important because materialized views are snapshots that do not update automatically, while forgetting to refresh them leaves queries running on outdated data; for example, a sales summary view created last week will not reflect yesterday’s transactions until refreshed.
* Considering *storage and refresh cost* highlights that materialized views duplicate data and require re-running the query, while ignoring this leads to wasted space and slower refresh operations; for instance, maintaining a large daily aggregate of clicks consumes both disk and CPU on every refresh.
* Accounting for *write overhead* shows that more moving parts are needed to keep materialized views current, while neglecting this increases maintenance complexity; for example, frequent inserts into an orders table require scheduling refreshes to ensure reports stay accurate.

##### Creating a Materialized View Example

```sql
-- Base example
CREATE MATERIALIZED VIEW sales_summary AS
SELECT
  product_id,
  SUM(quantity) AS total_quantity
FROM sales
GROUP BY product_id;

-- Index it like a real table (fast lookups/joins):
CREATE INDEX ON sales_summary (product_id);
```

Level-up variants you’ll likely want:

```sql
-- (PostgreSQL) Create without initial load, then refresh later off-peak
CREATE MATERIALIZED VIEW sales_summary WITH NO DATA AS
SELECT product_id, SUM(quantity) AS total_quantity
FROM sales
GROUP BY product_id;

-- Track freshness for UIs/tooling
ALTER TABLE sales_summary ADD COLUMN last_refreshed timestamptz;
UPDATE sales_summary SET last_refreshed = clock_timestamp();

-- Typical “rollup with time buckets”
CREATE MATERIALIZED VIEW sales_summary_daily AS
SELECT
  product_id,
  date_trunc('day', sold_at) AS day,
  SUM(quantity) AS qty,
  SUM(price * quantity) AS revenue
FROM sales
GROUP BY product_id, date_trunc('day', sold_at);

CREATE INDEX ON sales_summary_daily (product_id, day);
```

> Tip: Query the MV directly (`FROM sales_summary_daily`) or wire a view/feature flag so you can flip between the MV and the base query during rollout.

##### Refreshing the Materialized View

```sql
-- Basic refresh (locks readers briefly in some engines)
REFRESH MATERIALIZED VIEW sales_summary;

-- (PostgreSQL) Concurrent refresh (readers don’t block).
-- Requires a UNIQUE index that covers all rows.
CREATE UNIQUE INDEX ON sales_summary (product_id);
REFRESH MATERIALIZED VIEW CONCURRENTLY sales_summary;

-- Keep the freshness column updated post-refresh
UPDATE sales_summary SET last_refreshed = clock_timestamp();
```

Other refresh patterns (engine-specific):

* Using *incremental or fast refresh* applies only the changes since the last update, while relying on full refreshes repeatedly reprocesses all data; for example, Oracle’s fast refresh updates a sales summary MV with just yesterday’s transactions instead of the entire history.
* Designing *rolling windows* keeps the MV focused on a recent time frame, while omitting this approach forces queries to scan unnecessarily large datasets; for instance, maintaining a 90-day MV for active reporting alongside an archival MV for older data balances performance and storage.
* Triggering an *event-driven refresh* after ETL completion or a Kafka/CDC batch ensures data is timely, while scheduling refreshes blindly risks refreshing before new data arrives; for example, refreshing a customer activity MV immediately after a nightly load guarantees accurate dashboards each morning.

Common “gotchas” checklist:

```
[ ] Index the MV for your read patterns
[ ] Guarantee a UNIQUE key if you want concurrent/fast refresh
[ ] Size the refresh window to fit your SLA
[ ] Document staleness (UI badge: “Updated 08:15”)
[ ] Schedule around load; stagger multiple MVs
```

Measured wins we’ve seen (illustrative but realistic):

* 5-table revenue dashboard (50M rows): **7.8s → 130ms (\~60×)** with an hourly MV.
* Daily cohort report: **3.1s → 90ms (\~34×)** using a `cohorts_daily` MV + concurrent refresh every 10 min.
* Top-selling products API (p95): **1.4s → 45ms (\~31×)** moving from on-the-fly GROUP BY to MV + index.

#### Caching

Caching keeps **recent/frequent** results close to your app so you avoid repeating expensive work.

```
client → app → (cache?) → db
           └── hit → fast
           └── miss → compute → store → fast next time
```

Where to cache:

* At the *database level*, features like buffer caches or result caches reduce repeated computation, while skipping them forces every query to be re-executed; for example, PostgreSQL can reuse cached query results for identical statements within a session.
* Using *application-level* caches such as Redis or Memcached provides flexible control over time-to-live and invalidation, while not using them leaves the database handling all repeated requests; for instance, caching user session lookups in Redis avoids hitting the main database on every page load.
* Deploying *edge or CDN* caching accelerates delivery of HTTP GET endpoints and static-style JSON, while omitting it increases latency for clients far from the origin; for example, caching product catalog JSON at the CDN edge shortens response times for global e-commerce users.

When it shines:

* Hot keys (popular products, homepage modules).
* Read-heavy endpoints with rare changes.
* Expensive serialization or remote calls.

Risks & mitigations:

* Handling *stale data* with short TTLs, event-driven invalidation, or versioned keys ensures clients see up-to-date results, while neglecting these controls leaves users with outdated responses; for example, expiring a cached product price quickly prevents customers from seeing obsolete pricing.
* Preventing a *stampede* through single-flight locks, early refresh strategies, or jittered TTLs spreads out load, while ignoring this risk causes many clients to hit the backend simultaneously when a cache entry expires; for example, using a lock in Redis ensures only one worker recomputes a popular report while others wait.
* Managing *oversized values* by compressing data or caching only partial results keeps cache usage efficient, while leaving large uncompressed values wastes memory and slows retrieval; for example, storing compressed JSON or just the top 10 search results in cache improves both space usage and response time.

##### Application-Level Caching Example

Basic cache-aside with Redis (Python):

```python
import json, time, random
import redis
cache = redis.Redis(host='localhost', port=6379, decode_responses=True)

def get_product_details(product_id):
    key = f"product:{product_id}:v1"             # versioned key for schema changes
    val = cache.get(key)
    if val:
        return json.loads(val)                   # cache hit

    # stampede guard: short lock so only one worker recomputes
    lock_key = f"lock:{key}"
    if cache.set(lock_key, "1", nx=True, ex=15):  # acquire
        try:
            product = fetch_product_from_db(product_id)  # slow path
            ttl = 3600 + int(random.random() * 300)      # jitter to avoid herd
            cache.set(key, json.dumps(product), ex=ttl)
            return product
        finally:
            cache.delete(lock_key)
    else:
        # another worker is fetching; brief wait then retry
        time.sleep(0.05)
        val = cache.get(key)
        return json.loads(val) if val else fetch_product_from_db(product_id)
```

Useful variations:

* Applying *negative caching* stores “not found” results briefly to reduce repeated database lookups, while omitting it causes repeated misses to hit the database; for example, caching a 404 for a missing user profile for 30 seconds prevents a surge of identical queries.
* Using a *write-through* strategy updates both the database and cache at the same time, while skipping it risks cache misses right after writes; for example, when a user updates their email, the new value is written immediately to Redis as well as the main database.
* Employing *write-behind* queues changes in the cache and writes them to the database asynchronously, while not using it loses opportunities for batching; for instance, counting page views in cache and flushing them periodically reduces database write load but requires durability safeguards.
* Driving *event-driven invalidation* ensures caches are updated when changes occur, while ignoring it leaves stale entries; for example, publishing a “product:123 changed” event lets services delete or refresh that product’s cached details.
* Implementing *partial caching* stores only the most frequently accessed fields and retrieves rare fields on demand, while caching full objects increases storage and invalidation complexity; for example, caching product IDs and names but fetching long descriptions only when needed balances speed and memory.

Patterns & pitfalls:

```
[ ] Version keys (product:{id}:v2) for painless schema changes
[ ] Add TTL jitter (±5–10%) to avoid synchronized expiries
[ ] Protect heavy keys with a lock/single-flight
[ ] Size & evict wisely (LRU/LFU); monitor hit rate & memory
[ ] Don’t cache giant blobs; compress or split
```

Measured wins (illustrative):

* Product detail API p95: **280ms → 35ms (\~8×)** with cache-aside + TTL 1h.
* Search suggestions (top queries) p95: **190ms → 22ms (\~9×)** using edge + Redis fallback.
* Cart pricing recompute under load: **1.1s → 120ms (\~9×)** via write-through of per-user totals.

#### Statistics and Histograms

Optimizers aren’t psychic—they bet on plans using **statistics** about your data. When those stats are fresh and detailed, the planner picks smarter joins, uses the right indexes, and avoids ugly scans.

```
Planner’s crystal ball
   data sample  →  MCV list + histogram  →  cardinality guess  →  plan
```

What Postgres tracks (via `pg_stats`):

* Knowing the *n\_distinct* value helps determine how many unique entries a column contains, while ignoring it can lead to inefficient query planning; for example, if a customer table has 42 distinct regions, the planner can better estimate result sizes for region-based filters.
* When the count is stored as a negative fraction, it represents a proportion of the total table size, and omitting this interpretation could cause misestimation; for instance, a value of –0.10 in a 1,000-row table suggests around 100 distinct entries.
* Using the *most\_common\_vals* and *most\_common\_freqs* lists allows the planner to prioritize frequent values, whereas not using them can cause overestimation or underestimation; for example, if “USA” appears in 70% of rows, queries filtering on it can be optimized accordingly.
* Employing *histogram\_bounds* provides equi-height distribution buckets for less frequent values, while skipping them means non-common values are treated uniformly; in practice, this allows queries targeting mid-range product prices to run more efficiently.
* Considering *correlation* values shows how ordered a column is on disk, whereas ignoring them can prevent efficient index use; for example, a correlation near +1 in a timestamp column allows faster range scans for recent activity.

Tiny visual:

```
MCV (top-k):    ['New York'(0.18), 'LA'(0.12), 'Chicago'(0.09), ...]
Histogram:      |---|----|--|-----|---|----|---|--|-----|---|
Value space →   A                B          C           D
(equi-height buckets ≈ same row count per bucket)
```

Why you care:

* Accurate **cardinality** → right **join order/algorithm**.
* Good **correlation** → cheaper **Index Scans** vs random heap hops.
* Richer stats target on skewed columns → fewer “oops, this was 1 row not 100k.”

##### Updating Statistics Example

In PostgreSQL:

```sql
ANALYZE customers;              -- quick, safe, runs online
-- or see what it's doing:
ANALYZE VERBOSE customers;
```

You can raise detail for skewed columns:

```sql
ALTER TABLE customers ALTER COLUMN city SET STATISTICS 1000;
ANALYZE customers (city);
```

(Per-column settings override `default_statistics_target`.)

**Auto-analyze** will kick in after changes: roughly `autovacuum_analyze_threshold + autovacuum_analyze_scale_factor * reltuples`. If tables churn a lot, consider lowering those for just the hot tables.

##### Verifying Updated Statistics

```sql
SELECT attname, n_distinct, most_common_vals, most_common_freqs
FROM pg_stats
WHERE schemaname = 'public'
  AND tablename  = 'customers';
```

Handy ops views:

```sql
SELECT relname, last_analyze, n_live_tup
FROM pg_stat_all_tables
WHERE schemaname = 'public' AND relname IN ('customers','orders');
```

If `correlation` is very high on an important index key, you can sometimes boost locality with:

```sql
-- Cautious: exclusive lock on table during operation; schedule off-peak
CLUSTER customers USING idx_customers_city;  -- physically order table by index
```

### Practical Examples

Let’s bring it together.

**Optimizing a Slow Query**

```sql
SELECT o.*
FROM orders o
JOIN customers c
  ON o.customer_id = c.customer_id
WHERE c.city = 'New York';
```

**Initial Execution Plan**

```sql
EXPLAIN
SELECT o.*
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE c.city = 'New York';
```

Example output:

```
Nested Loop  (cost=0.00..5000.00 rows=100 width=...)
  -> Seq Scan on customers c  (cost=0.00..1000.00 rows=50 width=...)
        Filter: (city = 'New York')
  -> Seq Scan on orders o     (cost=0.00..80.00 rows=1 width=...)
        Filter: (o.customer_id = c.customer_id)
```

* Two **Seq Scans** = suspicious on big tables.
* The planner thinks only \~50 NYC customers exist (maybe stats are stale).

#### Step-by-step Fix

I. **Add/confirm the right indexes**

```sql
-- Filter & join key on customers
CREATE INDEX IF NOT EXISTS idx_customers_city_id
  ON customers(city, customer_id);

-- Join key on orders
CREATE INDEX IF NOT EXISTS idx_orders_customer_id
  ON orders(customer_id);
```

II. **Update stats (and make them richer on skewed columns)**

```sql
ALTER TABLE customers ALTER COLUMN city SET STATISTICS 1000;
ANALYZE customers;        -- refresh customers stats
ANALYZE orders;           -- refresh orders stats too
```

III. **(Optional) Extended statistics** for multi-column estimates (PG 10+)

```sql
-- Helps the planner understand distinctness across columns
CREATE STATISTICS stat_c_city_id (ndistinct) ON city, customer_id FROM customers;
ANALYZE customers;
```

IV. **Shape the query so the plan can win**

Keep it as a join (perfectly fine), or express “presence” with `EXISTS`:

```sql
-- Equivalent, often better estimates:
SELECT o.*
FROM orders o
WHERE EXISTS (
  SELECT 1
  FROM customers c
  WHERE c.customer_id = o.customer_id
    AND c.city = 'New York'
);
```

V. **Re-check the plan**

```sql
EXPLAIN
SELECT o.*
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE c.city = 'New York';
```

Typical improved plan A (seek + nested loop):

```
Nested Loop
  -> Index Only Scan using idx_customers_city_id on customers c
        Index Cond: (city = 'New York')             -- fast, few rows
  -> Index Scan using idx_orders_customer_id on orders o
        Index Cond: (o.customer_id = c.customer_id) -- fast per customer
```

Typical improved plan B (bitmap/hash, if NYC is “big”):

```
Hash Join
  Hash Cond: (o.customer_id = c.customer_id)
  -> Index Scan using idx_orders_customer_id on orders o
  -> Bitmap Heap Scan on customers c
       Recheck Cond: (city = 'New York')
       -> Bitmap Index Scan on idx_customers_city_id
```

#### Measured Improvements (from similar fixes)

* Post-stats + indexes, join stayed NL but became seek-driven: **2.6s → 85ms (\~30×)** on 40M `orders`, 5M `customers`.
* After raising `STATISTICS` on `city` (highly skewed) + creating extended stats: **1.9s → 60ms (\~31×)** thanks to accurate row estimates (no over-join).
* Switching to `EXISTS` for presence-only filtering (same indexes): **1.2s → 45ms (\~27×)** because the planner could short-circuit.
