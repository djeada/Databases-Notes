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
                      HIT? ───────────│─────────┐ No
                                 Yes  │         ▼
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
    HIT? ──────┤──────No ──────────────────────┐
          Yes  │                               │
               ▼                               ▼
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

* When *caching* is used to store data after it is first fetched, applications reduce repeated database queries, while omitting it results in slower response times; for example, a news site can quickly serve popular articles without repeatedly hitting the database.
* By serving requests directly from cached entries until their expiration, users experience consistently fast reads, whereas skipping this practice causes each request to trigger a database query; for instance, an e-commerce site can display product details instantly during peak hours.
* After the *time-to-live (TTL)* expires, the next request triggers a cache miss that forces a reload from the database, ensuring updated data is available, while not using this method risks showing outdated information indefinitely; a practical example is refreshing stock prices after a set interval.

```
Time ─────────────────────────────────────────────────────────────────────────►

t0                         t1                         t2                        t3
│                          │                          │                         │
Client ► Cache [HIT]    Client ► Cache [HIT]       Client ► Cache [MISS]     Client ► Cache [HIT]
           │                         │                          │                         │
           │<────────────── TTL valid window ──────────────────>│                         │
                                                (expires here)  │                         │
                                                             fetch ► DB
                                                             update cache
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

* In many systems, a short *TTL* acts as a safeguard to ensure stale data is eventually cleared, while omitting it can leave the cache relying solely on external signals that may fail; for example, product prices may still refresh within minutes even if an update notification is missed.
* When *event-based* purging is added for critical objects, updates are reflected almost immediately, whereas skipping this leads to reliance on scheduled expirations alone; a typical use case is invalidating a user’s session cache as soon as they log out.
* Combining both approaches creates a blended strategy that balances freshness with resilience, while using only one risks either unnecessary reloads or delayed updates; an example is a content platform that uses events to purge updated articles but also applies a brief fallback TTL.

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

* In an *e-commerce* platform, product listings are often treated as immutable and can be cached with a TTL close to the catalog update frequency, while omitting this practice causes unnecessary database load; for example, setting a 30–60 minute TTL lets popular items stay responsive without risking stale availability data.
* For *SaaS CRUD* applications, user and organization objects change infrequently, so long TTL values are acceptable, whereas avoiding them forces constant database queries; in this case, ensuring invalidation correctness matters more than maximizing cache hit rates, such as when an admin updates organization details only a few times a day.
* In a *social feed* with high read amplification, separating feed metadata from item bodies improves efficiency, while skipping this separation makes each read heavier and slower; for instance, a service may cache only the list of post IDs and then fetch or fan-out item content on demand.

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

* Applying short-lived *TTLs* to volatile entities ensures that fast-changing data like prices or session states remain fresh, while omitting them risks users seeing outdated values; for example, a 30-second TTL on product prices prevents showing yesterday’s discount during checkout.
* Using *write-through* or *write-behind* caching patterns keeps cache and database consistent during updates, whereas skipping this practice can lead to stale cache entries that contradict the source of truth; an example is updating a shopping cart total in Redis as part of the same database transaction.
* Implementing *event-driven invalidation* allows immediate removal or refresh of keys after updates, while not doing so leaves caches dependent on TTL expiration alone; for instance, a `product.updated` event can trigger Redis consumers to drop outdated product details right away.
* Enabling *background refresh* for popular keys pre-fetches data just before expiration, avoiding user-visible cache misses, while ignoring this approach can cause noticeable latency spikes; a common case is refreshing trending feed items a few seconds before their TTL lapses.

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

* Running *warm-up scripts* at deploy time preloads hot keys into the cache, avoiding a cold-start surge of database queries, while omitting this step can cause spikes in latency just after rollout; for example, loading a JSON list of top product IDs ensures they are immediately available in Redis.
* Using *probabilistic early refresh* lets the first thread refresh data while others continue serving the cached value, whereas not applying it can cause many threads to block simultaneously at expiration; a case in point is “lazy expiring,” where only one user request triggers a refresh of a popular item.
* Applying *request coalescing* ensures that only the first cache miss triggers a database fetch, with others waiting for the refreshed result, while leaving it out risks a thundering herd effect; for example, a single-flight lock on a trending news article prevents hundreds of concurrent queries.
* Adding *read replicas* or specialized CQRS read stores helps distribute load during inevitable cache misses, while relying on a single primary database can create bottlenecks; an example is serving cache misses for analytics queries from read replicas instead of the main transactional store.

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

* Leveraging *frameworks* that provide declarative caching APIs simplifies integration and reduces custom code, while bypassing them forces developers to manage low-level cache interactions; for example, using Spring’s `@Cacheable` annotation makes adding caching to a service method both easier and more consistent.
* Centralizing *TTLs*, eviction rules, and key naming conventions in a single module keeps cache behavior predictable, whereas scattering these settings across services leads to inconsistent policies; for instance, a shared configuration file ensures all services apply the same naming pattern for user sessions.
* Emitting *hit*, *miss*, *eviction*, and *latency* metrics gives teams visibility into cache effectiveness, while ignoring these signals makes it difficult to detect regressions; for example, a dashboard that shows cache hit rates beside database query counts helps diagnose performance issues quickly.
* Periodically disabling the cache in staging validates that the application remains functional without it, while skipping this step risks hidden dependencies that surface only in production; an example is ensuring a SaaS dashboard still renders correctly—just more slowly—when cache bypass is enforced.

> **Tip**: Treat the cache as *a copy* of the source of truth, never the truth itself. Design every code path to *degrade gracefully* when the cache is empty or unreachable.

### Real-World Use Cases

Database caching is used extensively in various applications to improve performance and scalability.

* High-traffic websites such as news platforms or online stores improve scalability and response time through *caching*, while omitting it results in database overload and slower page delivery; for example, a breaking news article can be served instantly to millions without repeated database queries.
* Distributed *CDNs* store static assets like images, scripts, or stylesheets on edge servers near users, which lowers latency, while skipping them forces every request to travel to the origin server; for instance, an e-commerce site loads product images faster when they come from a nearby CDN node.
* Storing *session data* in a cache accelerates authentication and personalization, while leaving this data only in the database increases login times and reduces responsiveness; for example, a social media platform can quickly recall user preferences from cached session keys.
