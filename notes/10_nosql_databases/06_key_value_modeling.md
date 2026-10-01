# Key-Value Modeling: Keys, TTLs, Caching, and Atomic Operations

A key-value store exposes a simple idea:

```text
key -> value
```

The simplicity is powerful because the database can optimize direct lookup very
well. The trade-off is that application design must make the important access
paths obvious in the key.

A key-value model is a good fit when the application usually knows the key
before it asks for the value.

## Start from the operation

Examples:

```text
session token -> session state
user ID       -> profile cache
rate key      -> request counter
cart ID       -> shopping cart
job ID        -> job state
```

These are naturally key-oriented.

Less natural:

```text
"find every session whose user lives in Berlin"
```

That is not a direct key lookup.

A secondary index or another database may be needed.

## Key design is data modeling

A key is not merely a string.

It encodes:

- namespace,
- identity,
- sometimes tenant,
- sometimes time bucket,
- sometimes version.

Example:

```text
session:8ac17...
```

Example:

```text
user:42:cart
```

Example:

```text
rate:user:42:2026-10-01T15
```

A good key is:

- deterministic,
- unambiguous,
- reasonably compact,
- stable across application versions.

## Namespaces

Prefix related key families:

```text
session:<token>
cart:<user_id>
profile:<user_id>
rate:<user_id>:<window>
```

This improves:

- debugging,
- metrics,
- bulk maintenance,
- ownership clarity.

Avoid using a prefix as a substitute for a proper authorization boundary.

## Avoid ambiguous concatenation

Bad:

```text
tenant + user
12 + 34 -> 1234
1 + 234 -> 1234
```

Use separators or structured encoding:

```text
tenant:12:user:34
tenant:1:user:234
```

## Tenant-aware keys

For multi-tenant systems:

```text
tenant:acme:session:...
tenant:beta:session:...
```

This makes tenant identity explicit.

It does not replace permission checks.

## Value shape

A value can be:

- string,
- serialized JSON,
- binary object,
- specialized data structure.

The value format has a schema even if the database treats it as opaque bytes.

Example JSON value:

```json
{
  "user_id": 42,
  "currency": "EUR",
  "items": [
    {"sku": "DB-101", "qty": 1}
  ]
}
```

The application still needs versioning and validation.

## Redis as a concrete example

Redis provides richer server-side data structures:

- strings,
- hashes,
- sets,
- sorted sets,
- lists,
- streams.

The engine chapter contains a complete Redis note:

[Redis](../12_database_engines/10_redis.md)

This chapter focuses on modeling choices.

## String

Good for:

- opaque cached JSON,
- counters,
- tokens,
- simple values.

Example:

```text
SET feature:checkout:v2 enabled
```

Counter:

```text
INCR article:42:views
```

## Hash

A hash stores fields under one key.

```text
HSET user:42
  name "Alice"
  plan "pro"
  country "DE"
```

This can update one field without replacing the entire serialized value.

## Set

A set represents unique membership.

```text
SADD team:7:members 42 51 87
```

Useful for:

- membership,
- deduplication,
- tags.

## Sorted set

Members have scores.

```text
ZADD leaderboard 1200 alice
ZADD leaderboard 1500 bob
```

Useful for:

- rankings,
- priority queues,
- time-ordered scheduling.

## TTL

Time-to-live is one of the most important key-value features.

Example:

```text
SET session:abc <value> EX 3600
```

A session expires after one hour.

TTLs are natural for:

- sessions,
- verification codes,
- short-lived caches,
- rate-limit windows.

## TTL is part of business semantics

Ask:

- what happens after expiration?
- can the value be rebuilt?
- does expiration create user-visible behavior?
- can several related keys expire at different times?

If the only copy of a critical payment state expires automatically, the data
model is probably wrong.

## Cache-aside

A common caching pattern:

```text
application
    │
    ▼
cache lookup
    │
    ├── hit -> return
    │
    └── miss
          │
          ▼
       primary DB
          │
          ▼
       populate cache
```

The primary database remains authoritative.

## Cache key composition

Suppose API response depends on:

- customer ID,
- language,
- currency.

Bad key:

```text
customer:42
```

It ignores response dimensions.

Better:

```text
customer:42:lang:de:currency:EUR
```

Cache keys must include every input that changes the result.

## Cache invalidation

Suppose:

```text
DB price = 49.90
cache    = 49.90
```

Database changes to 59.90.

The cache is stale.

Strategies include:

### Delete on write

```text
update DB
  │
  ▼
delete cache key
```

Next read reloads.

### Short TTL

Staleness is bounded by expiration.

### Event-driven invalidation

```text
DB change
  │
  ▼
event
  │
  ▼
cache invalidator
```

### Versioned key

```text
product:42:v7
```

Change version to move callers to a new key.

No invalidation strategy is universally correct.

## Cache consistency window

Document the tolerated staleness.

Example:

```text
product description -> 5 minutes acceptable
inventory available  -> 5 minutes unacceptable
```

Different fields may need different cache policies.

## Cache stampede

If one popular key expires:

```text
10,000 requests
      │
      ▼
all see miss
      │
      ▼
10,000 DB queries
```

Mitigations:

- request coalescing,
- jittered TTL,
- stale-while-revalidate,
- prewarming,
- lock/single-flight pattern.

## TTL jitter

Instead of every key expiring at exactly 3600 seconds:

```text
3600 ± random jitter
```

This spreads refresh work.

## Negative caching

An application can cache "not found" briefly.

Example:

```text
user:999 -> missing
TTL 30 sec
```

Useful when bots repeatedly request nonexistent IDs.

Use short TTLs so newly created data does not remain hidden too long.

## Hot keys

A hot key receives disproportionate traffic.

Example:

```text
global:counter
```

all requests hit one location.

Distributed storage cannot automatically parallelize an operation that truly
serializes through one key.

Possible designs:

- sharded counters,
- local caches,
- replicated reads,
- split state by tenant/time.

The semantics decide what is safe.

## Large values

Bad:

```text
one key -> 100 MB object
```

Costs:

- network latency,
- memory,
- replication,
- copy/deserialization,
- eviction impact.

Prefer bounded values.

## Large collections

A set/sorted set with millions of members can become an operational hotspot.

Consider partitioning:

```text
leaderboard:2026:region:eu
leaderboard:2026:region:us
```

if product semantics allow.

## Atomic commands

Key-value systems often provide atomic server-side operations.

Example:

```text
INCR inventory:reserved
```

is safer than:

```text
GET
application +1
SET
```

because two clients can race in the read-modify-write sequence.

## Compare-and-set

Some systems support conditional writes:

```text
update value only if version == 7
```

This is optimistic concurrency.

Use it for:

- locks,
- lease renewal,
- versioned state.

## Distributed locks

A lock key can coordinate work:

```text
lock:job:123
```

but distributed locks are easy to misuse.

A robust design needs:

- unique ownership token,
- expiration/lease,
- safe release,
- fencing/versioning for protected resources,
- behavior under network pauses.

Do not assume "SET if absent with TTL" solves every coordination problem.

## Idempotency key

A useful key-value pattern:

```text
idempotency:<request_id> -> result/status
```

On retry:

1. client sends same request ID,
2. server finds existing result,
3. server avoids duplicate side effect.

Good for:

- payment requests,
- order submission,
- external webhook processing.

The key must be scoped to the right operation/customer.

## Rate limiting

Fixed window:

```text
rate:user:42:2026-10-01T15 -> count
```

Increment atomically.

Expire after the window.

Trade-off: traffic can burst around boundary.

Other algorithms:

- sliding window,
- token bucket,
- leaky bucket.

Choose from fairness and cost requirements.

## Session storage

Key:

```text
session:<random-token>
```

Value:

```json
{
  "user_id": 42,
  "roles": ["customer"],
  "created_at": "...",
  "csrf_state": "..."
}
```

Security considerations:

- token must be unpredictable,
- TTL should match session policy,
- sensitive values should be minimized,
- logout should invalidate/revoke state.

## Write-through cache

Application writes through the cache layer to durable storage.

Pros:

- cache stays populated,
- consistent write path.

Cons:

- cache becomes part of critical writes,
- failure handling becomes more complex.

## Write-behind

Cache accepts writes, durable database updates later.

This can reduce apparent latency.

It increases risk:

- data loss before flush,
- ordering problems,
- recovery complexity.

Use only when business semantics tolerate it.

## Cache versus source of truth

Ask explicitly:

```text
If every cache key disappears now,
can the system reconstruct correct state?
```

If yes, it is likely a cache/derived store.

If no, you are using it as primary storage and need a durability/recovery
design.

## Persistence

Some key-value stores can persist memory state.

Persistence options may include:

- snapshots,
- append-only log,
- replicas.

Persistence changes recovery properties but not automatically business
correctness.

See the Redis engine note for concrete details.

## Eviction

A cache with bounded memory must choose what happens under pressure.

Potential outcomes:

- evict old/less-used keys,
- evict only expiring keys,
- reject writes.

The application should know what policy applies.

## Key cardinality

Track:

- total keys,
- keys per namespace,
- memory per namespace,
- TTL distribution.

A memory leak can appear as:

```text
session:* key count grows forever
```

because expiration was forgotten.

## Scan versus lookup

Direct lookup:

```text
GET session:abc
```

matches the model.

Scanning every key to find matching values does not.

If the application frequently scans:

```text
all keys where country = DE
```

add a maintained index/set or use a database designed for that query.

## Secondary lookup structures

You can maintain extra sets:

```text
users_by_country:DE -> {42, 87, 101}
```

But now writes must update:

- user value,
- country index.

This is application-managed denormalization.

Define transaction/atomicity behavior.

## Sharding

Distributed key-value systems hash or range-partition keys.

Key design affects:

- load distribution,
- multi-key operations,
- locality.

Redis Cluster, for example, uses hash slots.

Related keys can be forced into one slot with hash tags where appropriate.

See the Redis engine note for the concrete behavior.

## Multi-key operations

A simple key-value model becomes harder when one operation touches many keys.

Example:

```text
cart:<id>
inventory:<sku>
coupon:<code>
customer:<id>
```

Ask whether the database supports:

- atomic multi-key transactions,
- same-shard requirement,
- optimistic checks.

Do not assume single-key atomicity extends globally.

## Serialization format

Opaque values need a format:

- JSON,
- MessagePack,
- Protobuf,
- custom binary.

Consider:

- backward compatibility,
- forward compatibility,
- size,
- debugging,
- language interoperability.

## Schema versioning

Serialized value:

```json
{
  "version": 2,
  "user_id": 42,
  "items": []
}
```

The application can migrate older values when read.

A cache can often simply invalidate old-version keys instead.

## Versioned namespace

Another pattern:

```text
profile:v3:user:42
```

Deploy new code to use `v3`.

Old keys expire naturally.

This is simple for derived caches.

## Metrics

Monitor:

- hit ratio,
- miss ratio,
- evictions,
- memory,
- key count,
- command latency,
- hot keys,
- expired keys,
- replication lag,
- rejected connections.

A high hit ratio does not prove value if misses are extremely expensive.

## Runnable Redis demo

The engine chapter already includes:

[`scripts/redis/demo.redis`](../../scripts/redis/demo.redis)

This NoSQL chapter adds a key-design exercise:

[`scripts/redis/nosql_key_design.redis`](../../scripts/redis/nosql_key_design.redis)

It demonstrates:

- namespace conventions,
- TTL,
- atomic counters,
- sorted-set ranking,
- idempotency keys.

## Common mistakes

### Key does not include all result dimensions

Wrong cached response returned.

### No TTL on disposable data

Memory grows forever.

### One global hot key

Throughput serializes.

### GET-modify-SET for counters

Lost updates occur.

### Treating cache as durable truth accidentally

Eviction becomes data loss.

### Scanning keyspace for normal queries

Access model is wrong.

### Distributed lock without lease/fencing design

Stale owner can corrupt protected resource.

## Modeling checklist

1. What exact key does each request know?
2. Is value size bounded?
3. Is this cache or authoritative state?
4. What TTL should apply?
5. How is stale data invalidated?
6. Can a key become hot?
7. Are updates expressible atomically?
8. Do operations span multiple keys?
9. What happens after eviction?
10. How are retries/idempotency handled?
11. What serialization/versioning is needed?
12. Which metrics prove the store is healthy?

## Related notes

- [NoSQL introduction](01_nosql_databases_intro.md)
- [Document modeling](05_document_modeling.md)
- [Wide-column modeling](07_wide_column_modeling.md)
- [Consistency, transactions, and replication](09_consistency_transactions_and_replication.md)
- [Redis engine note](../12_database_engines/10_redis.md)
- [Database caching](../08_database_performance/03_database_caching.md)
