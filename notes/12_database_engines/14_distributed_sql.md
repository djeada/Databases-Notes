# Distributed SQL Databases

Distributed SQL databases keep a relational SQL model while distributing data and replication across multiple nodes.

The goal is to combine:

- SQL schemas and transactions,
- horizontal scale,
- automatic replication,
- high availability,
- multi-region deployment.

Examples commonly discussed in this category include:

- CockroachDB,
- Google Spanner,
- YugabyteDB,
- TiDB.

These systems make different trade-offs and have different SQL compatibility. "Distributed SQL" is a category, not a guarantee that every PostgreSQL/MySQL feature works unchanged.

This note uses CockroachDB for the runnable example because it can be started locally as one process while exposing the same SQL concepts used in a distributed cluster.

Official references:

- [CockroachDB developer basics](https://www.cockroachlabs.com/docs/stable/developer-basics.html)
- [CockroachDB local cluster](https://www.cockroachlabs.com/docs/stable/start-a-local-cluster.html)
- [CockroachDB architecture](https://www.cockroachlabs.com/docs/stable/architecture/overview.html)

## Why distributed SQL exists

A traditional single-primary relational deployment might look like:

```text
application
    │
    ▼
 primary DB
    │
    ├── replica
    └── replica
```

Read replicas can scale some reads, but writes still converge on one primary.

Manual sharding can scale writes:

```text
customers A-H -> shard 1
customers I-P -> shard 2
customers Q-Z -> shard 3
```

but the application now handles:

- routing,
- rebalancing,
- cross-shard queries,
- cross-shard transactions,
- shard hotspots.

Distributed SQL moves much of that complexity into the database.

## High-level architecture

A distributed SQL database often looks conceptually like:

```text
                  SQL clients
                      │
         ┌────────────┼────────────┐
         ▼            ▼            ▼
       node A       node B       node C
         │            │            │
         └──── distributed KV ─────┘
                   ranges
                + replicas
```

Any node can accept SQL connections.

The SQL layer translates table/index operations into distributed key-value reads and writes.

## Ranges

CockroachDB splits key space into ranges.

Conceptually:

```text
sorted key space

[A ........ F] [G ........ M] [N ........ Z]
   range 1        range 2        range 3
```

Ranges split as they grow.

Different ranges can live on different nodes.

This allows data and write load to spread across the cluster.

## Replication

Each range has multiple replicas.

Example:

```text
range 42

node A -> replica
node B -> replica
node C -> replica
```

A consensus protocol coordinates committed writes.

If one node fails, a quorum can still make progress when enough replicas remain.

Replication is automatic database behavior rather than application-managed copies.

## Raft consensus

CockroachDB uses Raft for range replication.

Simplified:

```text
write request
     │
     ▼
range leader/leaseholder
     │
     ├──► replica B
     └──► replica C
           │
     quorum acknowledgement
           │
           ▼
        commit
```

Consensus adds network coordination.

That is the core distributed trade-off:

> Strongly consistent replicated writes cannot be faster than the network coordination they require.

Region placement matters.

## Local setup

The repository includes:

[`scripts/cockroach/docker-compose.yml`](../../scripts/cockroach/docker-compose.yml)

Start:

```bash
cd scripts/cockroach
docker compose up -d
docker compose ps
```

Open SQL shell:

```bash
docker exec -it cockroach-notes   cockroach sql   --insecure   --host=localhost:26257
```

The local demo uses:

```text
--single-node
--insecure
```

Those are learning settings, not a production architecture.

Stop:

```bash
docker compose down
```

## Runnable SQL demo

The repository includes:

[`scripts/cockroach/demo.sql`](../../scripts/cockroach/demo.sql)

Run:

```bash
docker exec -i cockroach-notes   cockroach sql   --insecure   --host=localhost:26257   < demo.sql
```

The script:

1. creates an accounts table,
2. inserts sample balances,
3. transfers value inside a transaction,
4. queries the result.

The SQL intentionally looks familiar because distributed SQL aims to preserve the relational programming model.

## Transactions

CockroachDB provides ACID transactions.

Example:

```sql
BEGIN;

UPDATE accounts
SET balance = balance - 100
WHERE id = 1;

UPDATE accounts
SET balance = balance + 100
WHERE id = 2;

COMMIT;
```

From the application perspective, the transaction is relational.

Internally, the affected keys may live in several ranges and require distributed coordination.

## Serializable isolation

CockroachDB uses serializable isolation by default.

This prevents many concurrency anomalies but can require transaction retries when concurrent transactions conflict.

Conceptually:

```text
T1 reads X
T2 reads X

T1 writes X and commits

T2 tries to commit based on stale assumptions
        │
        ▼
serialization conflict
        │
        ▼
retry T2
```

Applications must be prepared for retriable transaction errors.

This is not a bug; it is part of maintaining serializable behavior under concurrency.

## Transaction retry loop

A generic application pattern:

```text
for limited attempts:
    BEGIN
    read current state
    perform writes
    COMMIT

    if serialization retry:
        backoff
        retry whole transaction
    else:
        return
```

Retry the **whole transaction**, not only the last SQL statement, because earlier reads may no longer be valid.

Many official drivers/framework integrations provide helpers for this.

## Primary keys matter

Distributed databases route and organize data from keys.

A monotonically increasing key can concentrate new writes:

```text
1
2
3
4
5
...
latest keys all target nearby key range
```

A more distributed key can spread writes.

But random keys can hurt locality for range scans.

The key design must balance:

- write distribution,
- locality,
- query patterns,
- index size.

Do not choose UUID/randomness mechanically without understanding the workload.

## Secondary indexes

A distributed secondary index is another distributed data structure.

For:

```sql
CREATE INDEX idx_orders_customer
ON orders(customer_id);
```

the database maintains index keys in addition to table keys.

Each write can therefore involve:

```text
table range
+
one or more index ranges
```

Indexes improve reads but add distributed write work.

The same index trade-off exists as in a single-node database, amplified by networking and replication.

## Hotspots

A hotspot occurs when too much traffic targets one range/node.

Examples:

- one global counter,
- monotonically increasing write key,
- one tenant dominating traffic,
- one frequently updated row.

```text
all clients
   │
   ▼
same key/range
   │
   ▼
one coordination bottleneck
```

Distribution cannot fix a workload whose business semantics require one serialized location.

Sometimes the data model must change.

## Multi-region data

Distributed SQL becomes especially interesting when data must survive regional failures or be placed near users.

Example:

```text
Europe region        US region         Asia region
  nodes                nodes              nodes
                        |                  /
     ________ replicated SQL data _______/
```

But geography creates latency.

A synchronous write that requires a quorum across distant regions can take tens or hundreds of milliseconds depending on topology.

Data placement should follow:

- user geography,
- consistency needs,
- disaster-recovery goals,
- write locality,
- legal/data-residency requirements.

## Locality

Some distributed SQL products let tables or rows express regional locality.

The goal is to answer:

- where should replicas live?
- where should the lease/leader be?
- which rows should stay near which users?

A global table does not mean every query has equal latency from everywhere.

## Cross-region transaction cost

Suppose:

```text
row A -> Europe-local
row B -> US-local
```

A transaction updating both can require cross-region coordination.

```text
Europe
   │
   ├──── network round trip ───► US
   │
   ◄─────────────────────────────
   ▼
commit
```

Keep transactional boundaries geographically coherent when possible.

## Distributed joins

The SQL layer can execute joins even if data lives across ranges.

But distributed joins can move substantial data over the network.

```text
shard/range A ──┐
                ├── network exchange -> join
shard/range B ──┘
```

Schema and index design still matter.

"Database handles distribution" does not mean network costs disappear.

## Constraints

Distributed SQL systems generally aim to preserve relational concepts such as:

- primary keys,
- unique constraints,
- foreign keys,
- transactions.

Exact feature coverage differs by product/version.

Check compatibility before migrating applications that depend on:

- extensions,
- stored procedures,
- triggers,
- exotic data types,
- engine-specific locking,
- specialized index types.

## PostgreSQL compatibility

Some distributed SQL systems speak the PostgreSQL wire protocol or support PostgreSQL-like syntax.

This helps clients connect.

It does **not** imply binary or behavioral equivalence with PostgreSQL.

Always check:

- SQL syntax,
- system catalogs,
- extensions,
- isolation behavior,
- DDL,
- driver behavior,
- ORM support.

## CockroachDB versus PostgreSQL

PostgreSQL is usually simpler when:

- one region is enough,
- vertical scaling/replicas meet load,
- write scale fits a primary,
- PostgreSQL extensions/features matter,
- low operational complexity is important.

CockroachDB-style distributed SQL becomes attractive when:

- horizontal write scale is required,
- multi-region resilience is required,
- automatic sharding/rebalancing is valuable,
- strong relational transactions must span distributed data.

Do not adopt distributed SQL to solve a problem that one PostgreSQL cluster already handles comfortably.

## Distributed SQL versus Cassandra

Both distribute data, but the programming model differs.

Cassandra:

- query-first denormalized tables,
- no distributed joins,
- tunable consistency,
- optimized around partition-key operations.

Distributed SQL:

- relational schemas,
- joins,
- constraints,
- distributed ACID transactions,
- stronger coordination.

```text
Need highly predictable partition-key access at massive scale?
    -> Cassandra may fit.

Need relational transactions while scaling/distributing?
    -> distributed SQL may fit.
```

## Distributed SQL versus manual sharding

Manual sharding:

```text
application
   │
   ├── route tenant A -> PostgreSQL shard 1
   ├── route tenant B -> PostgreSQL shard 2
   └── route tenant C -> PostgreSQL shard 3
```

Advantages:
- uses familiar engines,
- explicit control,
- can be cost-effective for simple tenancy.

Costs:
- routing logic,
- rebalancing,
- cross-shard operations,
- schema deployment across shards,
- operational tooling.

Distributed SQL moves much of this inside the database, but adds consensus/distributed-system overhead.

## Backup and restore

Replication protects availability.

Backups protect recoverability.

Both are required.

A globally replicated accidental delete is still an accidental delete everywhere.

Test:

- backup creation,
- restore,
- point-in-time recovery,
- cluster loss scenarios.

## Schema changes

Distributed DDL may require work across many ranges/nodes.

Large schema changes should be planned for:

- background backfills,
- additional index storage,
- temporary write amplification,
- rollout compatibility.

Use expand-and-contract application deployment patterns just as with other production databases.

## Monitoring

Important signals include:

- SQL latency,
- transaction retries,
- contention,
- range distribution,
- unavailable/under-replicated ranges,
- node CPU/memory/disk,
- network latency,
- replication health,
- hot ranges,
- connection count,
- backup status.

Distributed systems need topology-aware monitoring.

## Failure scenarios

Test:

```text
one process dies
one node dies
one zone dies
network becomes slow
network partitions
disk fills
region disappears
```

The architecture is valuable only if actual failure behavior matches the application's expectations.

## Cost model

Distributed SQL often stores several replicas and performs coordination for writes.

Costs include:

- multiple compute nodes,
- replicated storage,
- cross-zone/region network,
- backup storage,
- operational or managed-service cost.

A single-node relational database is often far cheaper.

Use distributed SQL when its resilience/scale features solve a real requirement.

## Common mistakes

### Choosing it only because "we may scale someday"

Distributed coordination has immediate complexity and cost.

### Assuming PostgreSQL compatibility means PostgreSQL identity

Feature differences matter.

### Ignoring transaction retries

Serializable conflicts are part of the application model.

### Cross-region transactions everywhere

Network latency becomes application latency.

### Hot sequential keys

Automatic sharding cannot eliminate all key-design problems.

### Replication without backups

Availability is not recoverability.

## Decision checklist

Before choosing distributed SQL:

1. Why is one primary relational database insufficient?
2. Is the problem write scale, geography, resilience, or all three?
3. Which SQL/extension features are mandatory?
4. What is acceptable transaction latency?
5. Which transactions cross regions?
6. Can the application retry transactions?
7. How should primary keys distribute traffic?
8. What locality/data-residency rules exist?
9. What is the replication cost?
10. What simpler architecture was benchmarked first?

## Related notes

- [PostgreSQL](03_postgresql.md)
- [Cassandra](11_cassandra.md)
- [Choosing a database](07_choosing_database.md)
- [Distributed databases](../06_distributed_databases/)
- [Concurrency control](../07_concurrency_control/)
