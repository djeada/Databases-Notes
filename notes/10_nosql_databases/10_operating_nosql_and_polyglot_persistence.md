# Operating NoSQL Systems and Polyglot Persistence

NoSQL systems are often introduced through data models, but production success depends just as much on operations. A database choice adds responsibilities for deployment, backups, monitoring, security, capacity, failure recovery, schema evolution, and synchronization with other systems.

A specialized database should solve a measurable workload problem that justifies those costs.

## One application can use several data stores

A realistic architecture might use:

```text
PostgreSQL
  |-- transactional orders/customers
  |
  +--> Redis
  |      sessions/cache/rate limits
  |
  +--> OpenSearch
  |      product search
  |
  +--> graph projection
         recommendations/fraud
```

This is often called **polyglot persistence**: choose different storage technologies for different access patterns.

It can be powerful, but every additional store creates another system whose correctness and lifecycle must be understood.

## Start with the simplest sufficient architecture

Before adding a second database, ask whether the current one can solve the workload with:

- a better index,
- a materialized view,
- built-in JSON/document features,
- full-text search,
- partitioning,
- a cache,
- read replicas.

A specialized NoSQL system should be introduced because measured requirements justify it, not because the data is described as "modern" or "large."

## Define the source of truth

If the same fact appears in several systems, name the authoritative copy.

Example:

```text
PostgreSQL products      -> authoritative catalog
Redis product cache      -> rebuildable
OpenSearch product index -> rebuildable search projection
warehouse product dim    -> analytical history/projection
```

Without this rule, conflict resolution becomes ambiguous.

## Derived stores

A derived store should normally be rebuildable.

Ask:

1. Can we recreate it from authoritative data?
2. How long does a rebuild take?
3. What happens while rebuilding?
4. Is replay idempotent?
5. How do we verify completeness?

If nobody knows how to rebuild the search index or graph projection, it has quietly become a second source of truth.

## Synchronization

Common synchronization methods include:

- application dual writes,
- change-data capture,
- event streams,
- scheduled batch jobs,
- database-native connectors.

Each has failure modes.

## Dual-write problem

Bad sequence:

```text
write PostgreSQL succeeds
write search index fails
```

Now the systems disagree.

Reversing the order merely reverses the failure case.

Use patterns such as:

- transactional outbox,
- CDC,
- replayable event log,
- reconciliation job.

## Eventual projections

Derived systems often lag behind the source:

```text
source commit
    |
    v
CDC/event
    |
    v
projection update
```

Document the expected lag.

Examples:

```text
search: under 30 seconds
recommendations: under 10 minutes
fraud block list: under 2 seconds
```

A vague statement such as "eventually consistent" is not an operational target.

## Reconciliation

Even with a good event pipeline, periodically compare source and projection.

Checks can include:

- row/document counts,
- sampled checksums,
- missing IDs,
- lag watermark,
- last processed offset.

Reconciliation catches silent divergence.

## Backups

Every authoritative NoSQL store needs a tested recovery strategy.

Questions:

- what is the RPO?
- what is the RTO?
- are backups application-consistent?
- are backups encrypted?
- can a backup be restored into a clean environment?
- are schema/index definitions included?

Replication is not a backup.

## Derived-store backup decision

A fully rebuildable cache/search index may not need the same backup policy as the primary database.

Trade-off:

```text
backup derived store
vs
rebuild from source
```

Compare:

- backup cost,
- rebuild duration,
- source retention,
- user impact.

## Capacity dimensions differ by model

Document stores:

- document count/size,
- working-set memory,
- index size,
- update rate.

Key-value stores:

- key count,
- value size,
- memory,
- TTL/eviction rate,
- hot keys.

Wide-column stores:

- partition size,
- write rate,
- tombstones,
- compaction,
- repair.

Graph databases:

- node/relationship count,
- degree distribution,
- traversal depth,
- memory/cache.

Use model-specific capacity metrics.

## Hotspot testing

Average traffic hides skew.

Examples:

- one celebrity account,
- one huge tenant,
- one popular cache key,
- one Cassandra partition,
- one graph supernode.

Benchmark the hottest realistic key/partition/node, not only uniform random data.

## Schema and index lifecycle

Flexible schema still needs change management.

Production rollout may require:

```text
new code reads old + new
       |
       v
backfill / rebuild index
       |
       v
new code writes new shape
       |
       v
remove compatibility
```

Index builds can consume significant CPU, disk, memory, and replication bandwidth.

Treat them as migrations.

## Observability

For every database, monitor at least:

- request/query latency,
- throughput,
- errors/timeouts,
- resource saturation,
- replication/consistency health,
- storage headroom,
- backup success.

Then add model-specific signals.

## Document-store signals

Examples:

- slow queries,
- documents scanned vs returned,
- index hit behavior,
- replication lag,
- chunk/shard imbalance.

## Key-value signals

Examples:

- hit/miss rate,
- evictions,
- memory fragmentation,
- hot keys,
- expired keys,
- command latency.

## Wide-column signals

Examples:

- pending compactions,
- tombstone warnings,
- dropped messages,
- partition size,
- repair status,
- coordinator latency.

## Graph signals

Examples:

- traversal latency,
- page/cache hit behavior,
- high-degree nodes,
- transaction contention,
- query-plan expansion.

## Security

NoSQL does not reduce security requirements.

Apply:

- authentication,
- least privilege,
- TLS,
- private networking,
- secret rotation,
- audit logging,
- backup protection.

Do not expose a development database directly to the public internet merely because the quickstart did so.

## Tenant isolation

Multi-tenant NoSQL systems need deliberate isolation.

Possible approaches:

- tenant field in every record,
- tenant-prefixed keys,
- tenant-specific partitions,
- separate databases/collections,
- separate clusters for strong isolation.

The application must not rely on naming convention alone for authorization.

## Data retention

Retention affects every copy:

```text
primary
replicas
cache
search
analytics
backup
```

A privacy/delete request is incomplete if only one store is updated.

Define how deletions propagate to derived systems.

## Disaster recovery

A DR plan should include dependencies such as:

- identity provider,
- KMS/secrets,
- object-storage backups,
- DNS,
- event offsets,
- schema/index definitions.

Restoring the raw data without the supporting configuration may not restore the service.

## Failure modes to test

Test at least:

- node failure,
- replica lag,
- network delay,
- disk full,
- credential rotation,
- expired certificate,
- projection consumer stopped,
- backup restore,
- duplicate event replay.

The operational model is part of the database model.

## Managed service versus self-managed

Managed services can reduce responsibility for:

- patching,
- node replacement,
- some backup automation,
- infrastructure scaling.

You still own:

- access model,
- data design,
- queries,
- index choices,
- costs,
- recovery objectives,
- application behavior during failover.

## Cost model

Specialized stores add cost beyond server price:

- replicated storage,
- network transfer,
- backups,
- monitoring,
- operational labor,
- developer complexity,
- data synchronization.

A system that saves 5 ms but doubles operational complexity may not be worthwhile.

## Avoid premature polyglot persistence

Bad reasoning:

```text
sessions -> Redis
search -> OpenSearch
graph -> Neo4j
events -> Cassandra
analytics -> ClickHouse
```

simply because each technology is known for that category.

Better reasoning:

1. measure the current bottleneck,
2. define the exact workload,
3. test simpler options,
4. benchmark the candidate,
5. include failure/operations cost,
6. add the store only if the benefit remains compelling.

## Migration into a specialized store

A safe sequence:

```text
create target schema/model
       |
       v
bulk backfill
       |
       v
start CDC/event sync
       |
       v
validate source vs target
       |
       v
shadow reads / compare
       |
       v
move production reads
```

Keep rollback possible until confidence is high.

## Migration away from a specialized store

Exit strategy matters too.

Ask:

- can data be exported?
- are proprietary APIs deeply embedded?
- can authoritative state be reconstructed?
- what downtime is required?

Avoid accidental lock-in where portability is important.

## Ownership

Every data store needs a clear owner responsible for:

- schema/model review,
- access control,
- alerts,
- backup/restore,
- patching/upgrades,
- incident response.

A database with no owner is an operational risk.

## Documentation

Document:

- why the store exists,
- authoritative versus derived status,
- main access patterns,
- consistency assumptions,
- rebuild/restore procedure,
- dashboards/alerts,
- escalation contacts.

This prevents future teams from treating a derived cache as irreplaceable business truth.

## Practical technology map

Use the focused engine notes for concrete implementations:

- [MongoDB](../12_database_engines/04_mongodb.md) — document database,
- [Neo4j](../12_database_engines/05_neo4j.md) — graph database,
- [Redis](../12_database_engines/10_redis.md) — key-value/data-structure store,
- [Cassandra](../12_database_engines/11_cassandra.md) — wide-column database,
- [OpenSearch/Elasticsearch](../12_database_engines/12_elasticsearch_and_opensearch.md) — search projection,
- [ClickHouse](../12_database_engines/13_clickhouse.md) — analytical projection.

## Production checklist

Before introducing another NoSQL database:

1. What exact workload does it solve?
2. Why is the existing database insufficient?
3. Is this source of truth or derived?
4. How is data synchronized?
5. What is the tolerated lag?
6. How is divergence detected?
7. Can the data be rebuilt?
8. What is the backup/restore plan?
9. What are the model-specific capacity limits?
10. How are security and tenant isolation enforced?
11. What happens during node/network failure?
12. Who owns it operationally?
13. What is the total cost?
14. How would we migrate away later?

## Related notes

- [NoSQL introduction](01_nosql_databases_intro.md)
- [Consistency, transactions, and replication](09_consistency_transactions_and_replication.md)
- [Database security](../11_security_best_practices/02_database_security.md)
- [Backup and recovery](../11_security_best_practices/01_backup_and_recovery_strategies.md)
- [Performance monitoring](../11_security_best_practices/05_performance_monitoring_and_tuning.md)
- [Choosing a database](../12_database_engines/07_choosing_database.md)
