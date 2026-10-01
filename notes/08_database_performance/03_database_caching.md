# Caching: Reuse Work Without Losing Track of Freshness

A **cache** keeps a reusable copy of data or a computed result. Reading the copy can avoid repeating a more expensive operation. The difficulty is knowing whether that copy is still appropriate for the request.

Read [query optimization](01_query_optimization_techniques.md) first. A cache can reduce repeated work, but cache misses still need an efficient path to the source data.

## Separate two different layers

| Layer | What it keeps | Who manages correctness |
|---|---|---|
| Database page cache | Storage pages used while executing queries | The database engine coordinates page versions and transactions |
| Application result cache | Values or objects returned by earlier reads | The application must define keys, freshness, and invalidation |

A page being in memory does not mean the database skips SQL execution. An application result cache can skip a query entirely, but its contents can be older than the current database state. See [database pages](../05_storage_and_indexing/04_database_pages.md) for the first layer; this note focuses on the second.

## Follow a cache-aside read

Suppose many visitors read the same book description. The database is the **source of truth**: the accepted authoritative record. The application can keep a cached copy under `product:10:description`.

```text
look up the cache key
if an unexpired entry exists:
    return its value                  # cache hit
otherwise:
    read the value from the database  # cache miss
    put a copy in the cache
    return the value
```

This pattern is called **cache-aside** because the application explicitly uses the cache beside its database access. A missing cache entry is an ordinary condition, not proof that the product does not exist.

A **time to live (TTL)** is how long an entry is allowed to remain before it expires. A 60-second TTL limits that entry's lifetime, but the value's age can also depend on which database copy was read and when the read began.

## Watch a stale value appear

At 10:00, a visitor loads a product description and the application caches it. At 10:01, staff edit the description in the database. At 10:02, another visitor reads the old cached description.

That might be acceptable for editorial text. The same reasoning is dangerous for a checkout's stock decision: cached “one copy left” does not authorize selling a copy. The final stock reservation must use the authoritative transactional operation.

Define an **acceptable staleness** requirement for each use. A catalog page, a payment record, and a user's permission state can require very different policies.

## Invalidation has races

**Invalidation** removes or marks a cached entry so it will be reloaded. A common write path updates the database, commits, then deletes the cache entry. This is useful, but it is not automatically race-free:

```text
Reader starts loading the old database value.
Writer commits the new value and invalidates the cache.
Reader finishes and puts its old value into the cache.
```

The cache is stale again even though the writer invalidated it. A failed invalidation after commit creates another stale-entry path.

Possible designs include versioned values, ordered change events, short TTLs, or an application-specific coordination protocol. Each needs a clear handling of delayed messages, retries, and competing writes. “Invalidate on update” is a starting policy, not a proof of consistency.

## Compare write strategies

| Strategy | Basic behavior | Question to resolve |
|---|---|---|
| Cache-aside | Application reads cache, falls back to database, and populates | How are stale entries expired or invalidated? |
| Read-through | Cache layer obtains a missing value from its configured source | What freshness and failure behavior does that layer provide? |
| Write-through | A write path updates the backing store and cache | What happens if only one update succeeds? |
| Write-behind | Cache accepts a write and persists it later | Can acknowledged changes be lost, reordered, or duplicated? |

Two separate systems do not become one atomic transaction because a strategy has a convenient name. Write-behind is especially different from caching read-only copies: it can put accepted but unpersisted data at risk.

## Design the key before storing the result

A cache key must include everything that changes the result. A customer-specific order list cannot use a global `open_orders` key. Tenant, customer, permission context, filter, locale, page, and representation version can matter.

Do not treat a cached object as proof that its requester is authorized to see it. Reusing one tenant's result for another is a correctness and security failure, even if it improves the hit rate.

**Negative caching** stores a “not found” result briefly. It can reduce repeated missing-key lookups, but can also hide an object created after the negative entry was stored.

## Handle expiry and failure under load

If a popular key expires, many callers can miss simultaneously and all query the database. This is a **cache stampede**. Coalescing concurrent loads for a key, adding jitter to expiration times, or serving an allowed stale value during refresh can reduce the burst.

Cache memory is finite. **Eviction** removes entries to make room, possibly before their TTL ends. An LRU policy favors recently used entries; an LFU policy favors frequently used entries. Actual cache implementations vary.

Plan for a cache outage or a cold start. Falling back to the database is useful only if the database can survive that extra load. Timeouts, bounded concurrency, and application-specific degraded responses may be needed. A shared cache also adds a network request; for a cheap query, that overhead can outweigh the saved work.

## Measure the whole request

Track hits and misses, latency, eviction, load amplification, and stale-value incidents. A **hit rate** is the proportion of lookups served by the cache. A high hit rate is not enough if the cached values are wrong or the expensive misses dominate user experience.

Start with one frequently reused, expensive read whose staleness policy is clear. Compare total request performance and database load before expanding the cache.

## Check your understanding

1. Why does a database page cache not remove the need to execute SQL?
2. Which bookstore data can tolerate staleness, and which requires an authoritative checkout decision?
3. How can a reader repopulate an old value after a writer invalidates it?
4. What inputs must a customer-specific cache key include?
5. Why can a cache outage overload a previously healthy database?

Next: [materialized views](04_materialized_views.md) provide another way to reuse calculated results with explicit maintenance rules.


## Related notes

- [Materialized views](04_materialized_views.md)
- [Connection pooling, batching, and N+1](08_connection_pooling_batching_and_n_plus_one.md)
- [Key-value modeling and Redis cache patterns](../10_nosql_databases/06_key_value_modeling.md)
- [Redis engine note](../12_database_engines/10_redis.md)
