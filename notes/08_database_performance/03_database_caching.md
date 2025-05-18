## Database Caching

Database caching is a powerful performance optimization technique that involves temporarily storing frequently accessed data in a cache for quick retrieval. By keeping commonly requested information readily available, caching reduces the time it takes to access data and lessens the load on the database server. This can significantly enhance the responsiveness and scalability of applications, leading to a better user experience.

After reading the material, you should be able to answer the following questions:

1. What is database caching, and how does it improve the performance and scalability of applications?
2. What are the different types of caching strategies, such as in-memory caching, client-side caching, and server-side caching, and when is each type most effectively used?
3. How do techniques like query result caching, object caching, database buffer caching, and prepared statement caching enhance database performance? Provide examples for each.
4. What are the primary cache invalidation strategies, including Time-to-Live (TTL), event-based invalidation, and manual invalidation, and how do they help maintain data consistency between the cache and the underlying database?
5. What are the best practices for implementing database caching, such as selecting which data to cache, setting appropriate TTL values, monitoring cache performance, and ensuring the security of cached data?

### Understanding Database Caching

At its core, caching works by storing copies of data in a location that can be accessed more quickly than the original source. In the context of databases, this often means keeping data in memory rather than retrieving it from disk storage each time it is needed. By doing so, applications can serve data faster and handle more concurrent users without overloading the database server.

#### How Caching Improves Performance

To visualize how caching fits into an application architecture, consider the following diagram:

```
#
       +-------------------+
       |    Client App     |
       +---------+---------+
                 |
           Data Request
                 |
                 v
       +---------+---------+
       |        Cache      |
       +---------+---------+
                 |
        Is Data in Cache?
            /        \
          Yes         No
           |           |
    Serve Data      Query Database
     from Cache          |
           |             v
           +-------Update Cache
                         |
                         v
                 Return Data to Client
```

- The client application requests data.
- The cache checks if it contains the requested data.
- If the data is found (cache hit), it is served directly from the cache to the client.
- If the data is not found (cache miss), the application queries the database, updates the cache with the new data, and then serves it to the client.

By serving data from the cache whenever possible, the application reduces the number of direct queries to the database, improving overall performance.

### Types of Caching Strategies

There are several caching strategies that can be employed, each suited to different scenarios and requirements.

#### In-Memory Caching

In-memory caching stores data in the system's RAM, providing the fastest possible data retrieval. Tools like Redis and Memcached are popular choices for implementing in-memory caches. They allow applications to store key-value pairs, lists, hashes, and other data structures in memory for quick access.

#### Client-Side Caching

Client-side caching involves storing data on the client's device, such as in a web browser's cache or local storage. This is particularly useful for static resources like images, stylesheets, and scripts. By caching data on the client side, applications can reduce server load and improve load times. However, this approach has limitations, including limited storage capacity and potential security concerns when storing sensitive data on the client's device.

#### Server-Side Caching

Server-side caching stores data on the server, closer to the application logic and database. This approach is effective for dynamic content and API responses that may be expensive to generate. By caching these responses, the server can quickly serve subsequent requests without recomputing the data. Challenges with server-side caching include the need for additional infrastructure and ensuring cache synchronization in distributed systems.

### Implementing Database Caching Techniques

There are various techniques for implementing caching in database applications, each with its own advantages and use cases.

#### Query Result Caching

Query result caching involves storing the results of frequently executed database queries. When the same query is requested again, the application retrieves the result from the cache instead of executing the query against the database. This reduces CPU and I/O usage on the database server and speeds up application response times.

```
#
                                 ┌──────────────────┐
                                 │  Client Request  │
                                 └────────┬─────────┘
                                          │
                                          ▼
                                  ┌────────────────┐
                                  │ Check Redis    │
                                  │  (cache_key)   │
                                  └───┬───────────┘
                HIT? Yes ───────────│─────────┐ No
                                  │         ▼
          ┌───────────┐         ┌───────┐  ┌────────────────────┐
          │ Return    │◀────────│Redis  │  │ Query Database     │
          │ Cached    │         │Hit!   │  │ (SELECT * FROM ...)│
          └───────────┘         └───────┘  └─────────┬──────────┘
                                                     │
                                                     ▼
                                              ┌────────────┐
                                              │ Store in   │
                                              │ Redis      │
                                              │ (ex=3600s) │
                                              └────┬───────┘
                                                   │
                                                   ▼
                                             ┌───────────┐
                                             │ Return    │
                                             │ DB Result │
                                             └───────────┘
```

**Example in Python using Flask and Redis:**

```python
from flask import Flask, jsonify
import redis
import sqlite3
import json

app = Flask(__name__)
cache = redis.Redis(host='localhost', port=6379, db=0)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    return conn

@app.route('/products')
def get_products():
    cache_key = 'product_list'
    cached_data = cache.get(cache_key)

    if cached_data:
        products = json.loads(cached_data)
        source = 'cache'
    else:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM products')
        products = cursor.fetchall()
        conn.close()
        cache.set(cache_key, json.dumps(products), ex=3600)  # Cache data for 1 hour
        source = 'database'

    return jsonify({'source': source, 'products': products})
```

- The application attempts to retrieve the list of products from the cache using a unique cache key.
- If the data is not in the cache (cache miss), it queries the database, stores the result in the cache, and then serves the data.
- If the data is in the cache (cache hit), it serves the data directly from the cache, reducing database load.

#### Object Caching

Object caching involves storing entire objects or data structures in the cache rather than just raw query results. This is especially useful in object-oriented applications where the same data object is used frequently.

```
#
      ┌────────────────────┐
      │ getUserById(123)   │
      └───────┬────────────┘
              │
              ▼
       ┌───────────────┐
       │ userCache.get │
       │ (key = 123)   │
       └───────┬───────┘
 HIT? Yes ─────┤      No ──────────────────────┐
              │                                │
              ▼                                ▼
       ┌─────────────┐                   ┌──────────────────┐
       │ Return      │                   │ Fetch from       │
       │ Cached User │                   │ Database         │
       └─────────────┘                   └────────┬─────────┘
                                                 │
                                                 ▼
                                         ┌──────────────────────┐
                                         │ userCache.put(123,   │
                                         │   <User Object>)     │
                                         └────────┬─────────────┘
                                                  │
                                                  ▼
                                           ┌─────────────┐
                                           │ Return User │
                                           └─────────────┘
```

**Example in Java using Ehcache:**

```java
import net.sf.ehcache.Cache;
import net.sf.ehcache.CacheManager;
import net.sf.ehcache.Element;

public class UserService {
    private CacheManager cacheManager;
    private Cache userCache;

    public UserService() {
        cacheManager = CacheManager.getInstance();
        userCache = cacheManager.getCache("userCache");
    }

    public User getUserById(int userId) {
        Element element = userCache.get(userId);

        if (element != null) {
            return (User) element.getObjectValue();
        } else {
            User user = database.getUserById(userId);
            userCache.put(new Element(userId, user));
            return user;
        }
    }
}
```

- The `getUserById` method first checks if the user object is in the cache.
- If the user is not cached, it retrieves the user from the database, caches the object, and then returns it.
- This reduces the need to query the database for the same user multiple times.

#### Database Buffer Caching

Databases themselves often implement caching mechanisms to improve performance. Adjusting database configurations can enhance this caching.

```
┌──────────────────────┐
│ PostgreSQL Server    │
└──────────┬───────────┘
           │ shared_buffers
           │  = 256MB
           │
           ▼
┌────────────────────────────┐
│ In‐Memory Buffer Cache     │
│ ┌────────────────────────┐ │
│ │ Data Pages             │ │
│ └────────────────────────┘ │
└──────────┬─────────────────┘
           │
           ▼
┌────────────────────────────┐
│ Disk I/O Reduced           │
│ Faster Query Responses     │
└────────────────────────────┘
```

**Configuring buffer cache in PostgreSQL:**

In the `postgresql.conf` file:

```
# Adjust shared_buffers to increase memory allocated for caching data pages
shared_buffers = 256MB
```

By increasing the `shared_buffers` setting, PostgreSQL allocates more memory for caching data, which can reduce disk I/O operations and improve query performance.

#### Prepared Statement Caching

Caching prepared statements can reduce the overhead of parsing and planning SQL queries, especially for queries that are executed frequently with different parameters.

```
┌───────────────────────────┐
│ PREPARE get_users_by_age  │
│   (INT) AS                │
│ SELECT * FROM users       │
│ WHERE age > $1;           │
└────────────┬──────────────┘
             │
             │   Subsequent EXECUTE calls:
             ▼
┌───────────────────┐      ┌───────────────────┐
│ EXECUTE           │      │ EXECUTE           │
│ get_users_by_age  │      │ get_users_by_age  │
│ (30)              │      │ (40)              │
└──────────┬────────┘      └───────────┬───────┘
           │                           │
           ▼                           ▼
 ┌─────────────────┐         ┌─────────────────┐
 │ Planner & Exec  │         │ Planner & Exec  │
 │ (no re‐parse!)  │         │ (no re‐parse!)  │
 └─────────────────┘         └─────────────────┘
```

**Example in PostgreSQL:**

```sql
-- Prepare a statement with a parameter placeholder
PREPARE get_users_by_age(INT) AS
SELECT * FROM users WHERE age > $1;

-- Execute the prepared statement with a specific parameter
EXECUTE get_users_by_age(30);
```

By preparing the statement once, subsequent executions with different parameters can be performed without re-parsing, which improves performance.

### Cache Invalidation Strategies

Keeping your cache coherent with the source of truth (the database) is one of the hardest problems in computer science. Below are three classic strategies, each with an ASCII diagram that shows **who** triggers the change and **when** the cached value is refreshed.

#### Time-to-Live (TTL)

1. **Write** – when data is first fetched from the DB, it is inserted into the cache with a fixed expiration time.
2. **Serve-from-cache** – until that timer “pops,” every read is a fast cache hit.
3. **Expire & Refresh** – after the TTL elapses, the next read is a miss, so the application reloads the data from the DB and starts a fresh timer.

```
Time ─────────────────────────────────────────────────────────►

 Client  ─►  Cache (HIT)   Cache (HIT)   Cache ✖ (MISS)   Cache (HIT)
                 │             │               │               │
                 │   TTL ticking down…         │               │
                 └───────────────<  TTL  >─────┘               │
                                         fetch ► DB ──► update │
```

**Pros**

* Simple “set-and-forget”; no need to listen for update events.
* Works even if the application has no write access to the cache layer (e.g., CDN).

**Cons**

* Freshness is probabilistic: the *worst-case* staleness equals the TTL value.
* Choosing the right TTL is tricky—too long gives stale data, too short kills performance.

**Redis snippet**

```python
cache.set('user_123', user_data, ex=3600)  # expires in 1 h
```

#### Event-Based Invalidation

Every mutating operation (INSERT/UPDATE/DELETE) triggers a cache purge for the affected keys:

```
#
            ┌─────────────────────────────┐
            │     UPDATE/INSERT/DELETE    │
            └──────────────┬──────────────┘
                           │ 1.  write to DB
                           ▼
┌───────────┐   2. delete(key)    ┌───────────┐
│   Cache   │◄────────────────────│  App/API  │
└───────────┘                     └───────────┘
       ▲                              │
       │ 3. next read = MISS          │
       └───────────────◄──────────────┘
                           fetch fresh row ► DB
```

**Pros**

* Near-real-time consistency—staleness is only the network/processing delay after a write.
* No guesswork about TTL values.

**Cons**

* You must **own every write path**; a forgotten code path means stale data.
* Extra complexity: publish/subscribe channels or message queues are common to broadcast events reliably.

```python
def update_user(user_id, new_data):
    database.update_user(user_id, new_data)    # 1️⃣
    cache.delete(f'user_{user_id}')            # 2️⃣
```

#### Manual Invalidation

A human (or a one-off script) explicitly removes or refreshes cache entries when they know data changed unexpectedly—e.g., after a hotfix directly in the DB.

```
Administrator / Script
        │  invalidate(key)
        ▼
┌────────────┐
│   Cache    │─────────► subsequent read = MISS → DB
└────────────┘
```

**Pros**

* Absolute control—great for emergency fixes, migrations, or ad-hoc cleanup.
* Zero code overhead if you already have a cache CLI.

**Cons**

* Easy to forget: relies on tribal knowledge and discipline.
* Does not scale for high-write or multi-service architectures.

### Choosing a Strategy

| Scenario                            | Recommended Approach                |
| ----------------------------------- | ----------------------------------- |
| Read-heavy, infrequent writes       | **TTL** with a moderate timeout     |
| Latency-sensitive & write-intensive | **Event-based** (often + short TTL) |
| One-off data repair or migration    | **Manual**                          |

> **Hybrid in practice** – Many production systems blend these techniques:
> *short TTL* as a safety net **+** *event-based* purging for critical objects. This “belt-and-suspenders” model keeps data fresh while guarding against missed events.

### Best Practices

Below is a “hands-on” playbook that teams actually use when they roll out a cache in front of a relational or NoSQL store. Feel free to cherry-pick the bits that fit your stack—everything is numbered so you can treat it like a checklist.

#### Pinpoint the “hot” data (don’t guess)

| Signal                 | How to Capture It (examples)                                                                                                                                                                                                                                                                                                | What You Learn                                                     |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------ |
| **Query frequency**    | *PostgreSQL:*<br/>`sql<br/>SELECT query, calls, total_exec_time/1000 AS seconds<br/>FROM pg_stat_statements<br/>ORDER BY calls DESC LIMIT 25;<br/>` <br>*MySQL 8+* `sql<br/>SELECT DIGEST_TEXT, COUNT_STAR AS calls<br/>FROM performance_schema.events_statements_summary_by_digest<br/>ORDER BY calls DESC LIMIT 25;<br/>` | Which exact SQL statements hammer the DB.                          |
| **Row/block reads**    | Cloud watch, Azure Monitor, or `pg_stat_io`, `INNODB_METRICS`                                                                                                                                                                                                                                                               | Whether repeated reads are on the same few tables or indexes.      |
| **Application traces** | App-side APM (OpenTelemetry/SkyWalking/New Relic/DataDog). Filter spans by **percentage of total wall-clock time** rather than pure count.                                                                                                                                                                                  | Pinpoints functions / endpoints dominating user latency.           |
| **Object popularity**  | Log or stream every **cache miss** for a day into BigQuery/Redshift, run a `GROUP BY key_id ORDER BY cnt DESC`.                                                                                                                                                                                                             | Even after you add a cache, this tells you if the pattern changed. |

> **Rule of thumb:** If a query or endpoint accounts for **>3 % of total DB CPU time** or **>100 QPS**, it’s a cache candidate.

#### Segregate “reads” into buckets before you cache

| Bucket                                    | Example pattern                     | Caching tactic                                                                                                    |
| ----------------------------------------- | ----------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **Immutable** for hours/days              | Product catalog, static config JSON | Set TTL equal to typical update interval. No invalidation headaches.                                              |
| **Frequently read, occasionally updated** | User profile, shopping-cart totals  | *Write-through* cache + key version (`user:123:v5`). Bump version on update to guarantee freshness.               |
| **Write-heavy**                           | Orders, ledger balances             | Usually **don’t** cache. If you must, use *read-through with short (≤5 s) TTL* and *striped locks* on cache miss. |
| **Fan-out read** (feeds, timelines)       | Top-N posts, leaderboard            | Cache the **list** separately from the **objects**. Invalidate the list on write; objects use a longer TTL.       |

#### Decide TTLs with data—not folklore

I. **Pull update intervals**: For each key type, compute the 95ᵗʰ percentile of “time between writes.”

*Example Postgres:*

```sql
WITH history AS (
SELECT user_id, lag(updated_at) OVER (PARTITION BY user_id ORDER BY updated_at) AS prev
FROM user_profile_changes
)
SELECT percentile_cont(0.95) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (updated_at-prev)))
FROM history WHERE prev IS NOT NULL;
```

II. **Pick TTL ≈ 50 – 80 % of that 95ᵗʰ percentile**. 

This maximizes hit rate while guaranteeing ≤5 % stale probability.

III. **Review TTLs monthly**—product changes often shorten or lengthen update cycles.

> **Advanced:** Add *stale-while-revalidate* (serve stale for ≤X s while a background task refreshes). Redis 7’s `CLIENT TRACKING` with `BCAST` or a CDN’s `stale-while-revalidate` header make this easy.

#### Wire it up (language-agnostic pseudocode)

```python
cache = Redis(..., client_tracking=True)   # enables auto-invalidation messages
db    = PostgreSQL(...)

def get_user(user_id):
    version = db.fetch_value(
        "SELECT cache_version FROM user WHERE id = %s", [user_id]
    )
    key = f"user:{user_id}:v{version}"
    
    if (data := cache.get(key)) is not None:
        metrics.hit.inc()
        return deserialise(data)
    
    # Miss: lock per-key to avoid stampede
    with cache.lock(f"lock:{key}", timeout=3):
        if (data := cache.get(key)) is not None:  # double-check
            return deserialise(data)

        row = db.fetch_row("SELECT ... FROM user WHERE id = %s", [user_id])
        cache.setex(key, ttl_user, serialise(row))
        metrics.miss.inc()
        return row
```

*Why the version column?* An update transaction simply increments `cache_version`, guaranteeing the next read builds a new key and the old value expires naturally.

#### Monitor like a SRE, not like a developer

| Metric                                       | Target                              | Alert when…                                                                       |
| -------------------------------------------- | ----------------------------------- | --------------------------------------------------------------------------------- |
| **Cache hit ratio** `(hits / (hits+misses))` | > 0.8 for read-through              | Drops 10 % in 5 min ⇒ cold keys.                                                  |
| **p99 latency** (cache & DB)                 | Cache p99 ≤ 3 ms; DB p99 ≤ read SLA | Cache ≥ 20 ms ⇒ network, serialization, or swap.                                  |
| **Evictions per minute**                     | 0 on provisioned RAM                | > 1 % of set rate ⇒ resize or add LRU tiers.                                      |
| **Hot key balance**                          | No single key > 5 % of gets         | If violated, consider sharding that key or using *local in-process* cache for it. |

Grafana dashboards that plot **hit ratio vs. TTL** and **evictions vs. memory used** are the fastest way to validate sizing.

#### Scale & harden

* Redis Cluster or Memcached’s client-side consistent hashing. Keep *slot* count ≥ 160 × nodes to smooth key re-distribution.
* For read-only or “mostly read” keys, add an in-process LRU (Guava, Caffeine, `functools.lru_cache`) sized for 5 – 10 % memory of the app pod.
* TLS everywhere (`requirepass`, `auth`, or ACLs).
* Key namespaces (`app1:*`) to stop accidental collisions.
* Encrypt sensitive blobs → envelope encryption (`AES-GCM`) before putting them in cache.

#### Why it differs by app

* **E-commerce**: product listings (immutable) vs. cart totals (write-through). TTL for product ≈ catalog update frequency (often 30 min – 1 h).
* **SaaS CRUD** apps: user & org objects updated sporadically—TTL can be hours. Focus more on *invalidation correctness* than raw hit rate.
* **Social feed**: massive read amplification. Split feed metadata (list of IDs) and item bodies, use fan-out on write or “pull with cache”.

Each app’s *write cadence* and *staleness tolerance* ultimately dictate TTL and invalidation strategy—use the measurement steps above to quantify both before you start tweaking configs.

### Potential Challenges and Solutions

While caching can slash response times from ~50 ms to sub‑5 ms and offload 80‑90 % of read traffic, it introduces its own pitfalls.

#### Stale Data (Cache‑DB Drift)

```
Time --->

 [DB   ] v2  ──────────────┐
 [Cache] v1 ──┐            │  (TTL 30 s)
              └─>  *Stale* │
 update()                 invalidate()
```

*Scenario*: A product’s price changes from €29.99 to €24.99 at **13:05:12** but users keep seeing the old price for up to 30 s because that’s the TTL.

**Mitigations**

* **Short‑lived TTLs** on volatile entities (e.g. prices 30 s, user sessions 15 min, catalog 1 h).
* **Write‑through / write‑behind** patterns so the cache is updated in the same transaction that touches the DB.
* **Event‑driven invalidation**: emit a `product.updated` event from the write service; consumers delete or refresh the key in Redis immediately.
* **Background refresh** ("refresh‑ahead") so popular keys are re‑fetched a few seconds *before* they expire.

#### Cache Miss Penalties (Thundering Herd)

```
┌───────────────┐
│  Cache (hit)  │  1 ms
└───────────────┘
     △
     │ miss
     ▼
┌──────────────────┐
│  Primary DB      │  ~40 ms
└──────────────────┘
```

*Scenario*: After a deploy, the cache is cold. 5 k rps hits the DB, which briefly spikes to 90 % CPU causing p99 latency to jump from 60 ms ⇒ 1 s.

**Mitigations**

* **Warm‑up scripts** at deploy time (`redis-cli MSET $(cat hot_keys.json)`).
* **Probabilistic early refresh** (e.g. \["lazy expiring"] where the first thread refreshes while others keep serving the old value).
* **Request coalescing** / *single‑flight*: the first miss locks the key; other requests wait for the result instead of hammering the DB.
* **Read replicas** or CQRS read stores to share the load when misses inevitably happen.

#### Increased Complexity (Operational Overhead)

```
┌────────┐   ┌────────┐   ┌────────────┐   ┌────────┐
│Client  │──▶│ Service│──▶│   Cache    │──▶│Database│
└────────┘   └────────┘   └────────────┘   └────────┘
                   ▲
             eviction policy,
           replication, metrics
```

*Pain Points*: extra moving parts (Redis cluster + Sentinel), failure modes (cache down ≠ DB down), and cognitive load for new devs who must understand eviction policies.

**Mitigations**

* **Leverage frameworks** (`Spring @Cacheable`, `NestJS cache‑manager`, Django’s `cache` API) so most logic is declarative.
* Keep TTLs, eviction policies, and key naming conventions in a single module.
* Emit *hit*, *miss*, *eviction*, *latency* metrics; dashboard them next to DB metrics.
* Periodically turn off the cache in staging to prove the app still works (albeit slower).

> **Tip**: Treat the cache as *a copy* of the source of truth, never the truth itself. Design every code path to *degrade gracefully* when the cache is empty or unreachable.

### Real-World Use Cases

Database caching is used extensively in various applications to improve performance and scalability.

#### High-Traffic Web Applications

Websites that experience high traffic volumes, such as news sites or e-commerce platforms, benefit from caching by reducing database load and serving content more quickly.

#### Content Delivery Networks (CDNs)

CDNs cache static content at servers distributed around the globe, reducing latency by serving content from a location closer to the user.

#### Session Management

Applications often use caching to store session data, improving the speed of user authentication and personalization features.
