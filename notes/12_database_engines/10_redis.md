# Redis

Redis is an in-memory data store built around specialized data structures such as strings, hashes, lists, sets, sorted sets, streams, JSON, geospatial indexes, probabilistic structures, and newer vector-oriented capabilities.

It is commonly used as:

- a cache,
- a session store,
- a rate limiter,
- a low-latency key-value store,
- a leaderboard,
- a queue or stream component,
- short-lived coordination state.

Redis can persist data, replicate it, and run in clustered deployments, but many applications deliberately use it as a **derived** or **rebuildable** layer in front of a durable database.

Official documentation:

- [Redis data types](https://redis.io/docs/latest/develop/data-types/)
- [Redis persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)

## Mental model

A common production pattern is:

```text
                    ┌───────────────┐
request ───────────►│ Redis cache   │
                    └──────┬────────┘
                           │ miss
                           ▼
                    ┌───────────────┐
                    │ primary DB    │
                    └──────┬────────┘
                           │
                           └──► populate cache
```

The primary database remains the source of truth.

Redis removes repeated work from the hot path.

## Local setup

The repository includes:

[`scripts/redis/docker-compose.yml`](../../scripts/redis/docker-compose.yml)

Start Redis:

```bash
cd scripts/redis
docker compose up -d
docker compose ps
```

Open the CLI:

```bash
docker exec -it redis-notes redis-cli
```

Check connectivity:

```text
PING
```

Expected:

```text
PONG
```

Run the repository command demo:

```bash
cat demo.redis | docker exec -i redis-notes redis-cli
```

The file exercises strings, hashes, counters, sorted sets, and streams.

Stop it:

```bash
docker compose down
```

Use `docker compose down -v` only when you also want to delete the demo data volume.

## Strings

Strings are the simplest Redis value.

```text
SET user:42:name "Alice"
GET user:42:name
```

Counters are atomic:

```text
SET page:home:views 0
INCR page:home:views
INCR page:home:views
GET page:home:views
```

Expected:

```text
"2"
```

Counters are useful for:

- request counts,
- sequence-like values,
- simple quotas,
- metrics that do not need relational joins.

## Expiration

Keys can expire automatically.

```text
SET session:abc123 "user=42" EX 3600
TTL session:abc123
```

This is one reason Redis is popular for sessions and caches.

Expiration is not a substitute for application correctness. If a key must exist permanently, relying only on TTL-based Redis state is usually the wrong design.

## Hashes

A Redis hash stores named fields:

```text
HSET user:42 name "Alice" plan "pro" country "DE"
HGET user:42 name
HGETALL user:42
```

Conceptually:

```text
user:42
├── name    -> Alice
├── plan    -> pro
└── country -> DE
```

Hashes are useful for compact object-like state when access is mostly by known key.

They do not provide relational joins or foreign-key constraints.

## Sets

Sets contain unique unordered members.

```text
SADD article:7:tags redis database caching
SMEMBERS article:7:tags
SISMEMBER article:7:tags redis
```

Set operations can model intersections:

```text
SINTER users:premium users:active
```

Useful for:

- membership,
- tags,
- unique collections,
- intersections/unions.

## Sorted sets

A sorted set associates each member with a score.

```text
ZADD leaderboard 1200 alice
ZADD leaderboard 1500 bob
ZADD leaderboard 1325 carol

ZREVRANGE leaderboard 0 2 WITHSCORES
```

Typical use cases:

- leaderboards,
- priority ordering,
- time-based queues,
- ranked results.

```text
score
1500  bob
1325  carol
1200  alice
```

## Lists

Lists are ordered sequences.

```text
LPUSH jobs email:1001
LPUSH jobs email:1002
RPOP jobs
```

Lists can support simple queues, but production task systems often need stronger delivery tracking, retries, visibility, and observability.

Redis Streams are often better when an append-only event log and consumer groups are needed.

## Streams

Redis Streams provide log-like entries with IDs.

```text
XADD orders * order_id 1001 amount 49.90
XADD orders * order_id 1002 amount 19.95

XRANGE orders - +
```

Conceptually:

```text
orders stream
│
├── 1727...-0 -> order_id=1001 amount=49.90
└── 1727...-0 -> order_id=1002 amount=19.95
```

Streams can support consumer groups.

Kafka and Redis Streams overlap in some use cases, but they have different operational models, ecosystem depth, retention patterns, and scaling designs.

Choose based on required throughput, replay, consumer topology, persistence, and operational context.

## Atomic operations

A major Redis strength is that individual commands are atomic.

For example:

```text
INCR rate:user:42
```

does not require a read-modify-write cycle in application code.

This matters under concurrency.

Bad application pattern:

```text
GET counter -> 10
application computes 11
SET counter 11
```

Two clients can overwrite each other.

Use atomic commands whenever the operation can be expressed directly.

## Transactions

Redis provides `MULTI` / `EXEC`:

```text
MULTI
INCR account:42:logins
SET account:42:last_login "2026-09-30T20:00:00Z"
EXEC
```

Commands are queued and executed as a transaction block.

Redis transactions are not the same as a relational database transaction with arbitrary rollback semantics.

If business correctness spans complex relational rules, a relational database transaction is usually a better source of truth.

## Optimistic checks with WATCH

`WATCH` can detect whether a key changed before `EXEC`.

Conceptually:

```text
WATCH inventory:42
GET inventory:42
      │
      ▼
application decides update
      │
      ▼
MULTI
SET inventory:42 ...
EXEC
```

If another client modifies the watched key first, the transaction aborts.

This is optimistic concurrency.

## Caching patterns

### Cache-aside

Application controls the cache.

```text
GET cache key
    │
    ├── hit -> return
    │
    └── miss
          │
          ▼
       query DB
          │
          ▼
       SET cache
```

Advantages:
- simple,
- only requested data is cached.

Risks:
- stale data,
- cache stampedes,
- invalidation complexity.

### Write-through

Writes update cache through a layer that also updates durable storage.

This can simplify read freshness but adds coupling.

### Write-behind

Cache accepts writes and durable storage is updated later.

This can improve write latency but increases durability and failure complexity.

Use only when lost/delayed writes are acceptable and recovery is well understood.

## Cache invalidation

Suppose:

```text
DB user name = Alice
Redis cache  = Alice
```

The database changes to Alicia.

The cache is now stale.

Common strategies:

- delete cache entry after DB update,
- short TTL,
- event-driven invalidation,
- versioned keys,
- refresh-ahead.

No strategy is universally best.

## Cache stampede

If one popular key expires:

```text
1000 requests
      │
      ▼
same cache miss
      │
      ▼
1000 DB queries
```

Mitigations include:

- jittered TTLs,
- request coalescing,
- distributed locks,
- stale-while-revalidate patterns,
- prewarming.

## Rate limiting

A basic fixed-window limiter:

```text
INCR rate:api:42:2026093020
EXPIRE rate:api:42:2026093020 3600
```

If the counter exceeds the quota, reject further requests.

More accurate algorithms may use sorted sets or Lua scripts for sliding windows/token buckets.

The important property is that the update must be atomic.

## Lua / server-side functions

Redis can execute server-side logic atomically.

Historically this is commonly demonstrated with Lua.

Use server-side logic when several commands must behave as one atomic operation, but keep scripts short and predictable because long-running server work blocks other operations on the same execution path.

## Persistence

Redis supports multiple persistence strategies.

### RDB snapshots

Periodic point-in-time snapshots.

```text
memory
  │
  └──► dump.rdb
```

Advantages:
- compact,
- convenient for snapshots/backups.

Trade-off:
- writes since the latest snapshot may be lost after a failure.

### AOF

Append-only file records write operations.

```text
SET ...
INCR ...
HSET ...
      │
      ▼
 append-only log
```

AOF can reduce the recovery-point gap but costs additional I/O and storage.

### No persistence

A valid choice for disposable caches that can be rebuilt.

The correct choice depends on whether Redis is a cache or a primary data store.

## Replication

A basic topology:

```text
          writes
client ───────────► primary
                    │
              replication
             ┌──────┴──────┐
             ▼             ▼
          replica A     replica B
```

Replication improves availability and read-scaling options.

It does not replace backups.

## Redis Cluster

Redis Cluster shards keys across hash slots.

```text
key
 │
 ▼
hash slot
 │
 ├──► shard A
 ├──► shard B
 └──► shard C
```

Multi-key operations can become constrained when keys belong to different slots.

Hash tags can force related keys into one slot:

```text
cart:{user42}:items
cart:{user42}:totals
```

The text inside braces determines the shared slot.

Design keys intentionally before scaling.

## Sentinel

Redis Sentinel is used with non-clustered Redis deployments for monitoring and failover coordination.

It can:

- detect primary failure,
- promote a replica,
- provide discovery information to clients.

Cluster mode and Sentinel solve related but different deployment problems.

## Eviction

When Redis reaches a configured memory limit, an eviction policy decides what happens.

Possible strategies include:

- reject writes,
- evict selected keys,
- use recency/frequency-oriented eviction,
- evict TTL keys.

A cache should have an explicit memory and eviction policy.

Running an in-memory system without memory planning is an operational failure waiting to happen.

## Data modeling

Good Redis design starts from access patterns.

Example session key:

```text
session:<token>
```

Example per-user rate key:

```text
rate:<user_id>:<window>
```

Example leaderboard:

```text
leaderboard:<season>
```

Avoid treating Redis as a relational database encoded into arbitrary key strings.

## Hot keys

One key receiving enormous traffic can overload the node responsible for it.

Examples:

- one global counter,
- one celebrity profile,
- one huge sorted set,
- one lock for the entire system.

Mitigations depend on semantics:

- shard counters,
- replicate/read-cache,
- split data structures,
- local caching,
- redesign coordination.

## Big keys

A key containing millions of members or a huge value can cause:

- long command latency,
- large network responses,
- expensive deletion,
- replication pressure.

Monitor key size, not only key count.

## Redis versus Memcached

Memcached is simpler and focused on volatile key/value caching.

Redis provides richer structures, persistence options, replication, streams, scripting, and broader use cases.

Choose Memcached when simple distributed caching is enough.

Choose Redis when richer server-side operations materially simplify the system.

## Redis versus a relational database

Use Redis when:

- access is key-oriented,
- very low latency matters,
- data structures fit Redis operations,
- cache/session/rate-limit semantics dominate.

Use PostgreSQL/MySQL/SQL Server when:

- joins matter,
- relational constraints matter,
- durable transactional state is central,
- ad-hoc querying is important.

Often the right architecture is both:

```text
PostgreSQL = source of truth
Redis      = low-latency derived state
```

## Managed options

Common managed Redis-compatible services include:

- Redis Cloud,
- Azure Managed Redis,
- Amazon ElastiCache,
- Google Cloud Memorystore.

Compatibility, persistence, clustering, modules, and command support differ by service.

Test required commands and failure behavior before migrating.

## Production checklist

Before using Redis in production:

1. Is this authoritative data or rebuildable derived data?
2. What is the memory limit?
3. What eviction policy applies?
4. Is persistence required?
5. What is the acceptable data-loss window?
6. Is replication configured?
7. Is clustering necessary?
8. How are hot and large keys detected?
9. Are application timeouts configured?
10. What happens when Redis is completely unavailable?

## Common mistakes

### Using Redis as an invisible dependency

Applications should have explicit behavior for cache failure.

### No TTL policy

Caches grow forever.

### Storing huge blobs

Large values increase memory, replication, and network costs.

### Assuming persistence equals backup

Operational mistakes can affect persistent Redis data too.

### One global lock

This serializes the system and creates a hot key.

### Using KEYS in production

A full keyspace scan can be disruptive. Prefer cursor-based `SCAN` for administrative iteration.

## Related notes

- [Choosing a database](07_choosing_database.md)
- [Cassandra](11_cassandra.md)
- [OpenSearch and Elasticsearch](12_elasticsearch_and_opensearch.md)
- [Database caching](../08_database_performance/03_database_caching.md)
- [Distributed databases](../06_distributed_databases/)
