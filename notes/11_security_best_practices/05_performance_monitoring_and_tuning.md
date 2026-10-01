# Performance Monitoring and Tuning

Performance tuning should start with a measured problem:

- checkout latency increased,
- connection pools are waiting,
- a report saturates I/O,
- replicas fall behind,
- lock waits increased after a deployment.

The useful loop is:

```text
observe
  │
  ▼
form hypothesis
  │
  ▼
measure specific cause
  │
  ▼
make one justified change
  │
  ▼
repeat same workload
  │
  ▼
compare
```

Do not tune settings because they are popular on a blog. A change is useful only when it improves the target workload without unacceptable cost elsewhere.

## Start from user-visible behavior

The database exists to serve application work.

Measure:

- latency,
- throughput,
- error rate,
- freshness,
- timeout rate.

Database CPU at 80% is not automatically a problem if latency and headroom remain acceptable.

Conversely, CPU at 20% does not prove health if requests are blocked on locks or storage.

## Percentiles

Averages hide slow users.

Suppose request latency is:

```text
p50 = 20 ms
p95 = 80 ms
p99 = 2.5 s
```

The median looks healthy, but 1% of requests are extremely slow.

Track at least:

- p50 for typical behavior,
- p95/p99 for tail behavior.

Use the percentile that matches the service objective.

## Service-level objectives

An SLO can make tuning concrete.

Example:

```text
99% of checkout database operations
complete within 100 ms
over a 30-day window
```

Now the team can ask:

- which queries violate the target?
- which time windows are worst?
- is the problem capacity or contention?
- did the last change improve the SLO?

## Core database signals

| Signal | What it helps explain |
| --- | --- |
| query latency | slow statements and tail behavior |
| queries/transactions per second | workload volume |
| errors/rollbacks | failed work |
| active connections | concurrency |
| connection-pool wait | queueing before SQL runs |
| CPU | compute pressure |
| memory | cache and sort/hash pressure |
| disk latency/IOPS | storage bottlenecks |
| temp-file usage | spills or large sorts/hashes |
| lock waits | contention |
| deadlocks | incompatible lock ordering |
| long transactions | retained locks/old snapshots |
| replication lag | read freshness/failover readiness |
| table/index growth | capacity and maintenance needs |
| checkpoint/WAL activity | write/recovery pressure |

No single metric diagnoses a database.

## Saturation

A resource can be healthy at high utilization if there is still headroom and latency remains stable.

Watch for **saturation**:

```text
demand
   │
   ▼
resource reaches capacity
   │
   ▼
queue grows
   │
   ▼
latency rises sharply
```

Examples:

- CPU run queue,
- storage queue depth,
- connection pool waiters,
- lock waiters.

## Baseline

Before tuning, capture normal behavior.

Record:

- traffic volume,
- latency percentiles,
- CPU/memory,
- connection count,
- slowest/frequent queries,
- disk usage,
- replication lag.

Without a baseline, it is difficult to know whether today's value is unusual.

## Annotate changes

Performance graphs should show:

- deployments,
- migrations,
- index creation,
- configuration changes,
- batch jobs,
- maintenance.

Example:

```text
latency
  ^
  |        /^^^^
  |_______/     ____
          |
      deployment
```

The annotation can turn a vague incident into a clear correlation.

## Runnable PostgreSQL health check

The repository includes:

[`scripts/security/postgres_health_check.sql`](../../scripts/security/postgres_health_check.sql)

Start the local PostgreSQL environment:

```bash
cd scripts
bash setup/start_postgres.sh
cd ..
```

Run the health queries:

```bash
docker exec -i postgres-local   psql -U demo -d test   < scripts/security/postgres_health_check.sql
```

The script reads:

- current identity,
- sessions by state,
- long transactions,
- lock waits,
- database counters,
- largest tables,
- index size and scan counts.

It is read-only.

## Current activity

PostgreSQL exposes live sessions through `pg_stat_activity`.

Example:

```sql
SELECT
    pid,
    usename,
    application_name,
    state,
    now() - query_start AS query_age,
    wait_event_type,
    wait_event
FROM pg_stat_activity
WHERE datname = current_database()
ORDER BY query_start;
```

This helps answer:

- what is running now?
- what is waiting?
- which sessions have been active a long time?

## Long transactions

Long transactions can cause more than slow requests.

They may:

- hold locks,
- retain old MVCC row versions,
- delay cleanup,
- consume pool connections.

Query:

```sql
SELECT
    pid,
    usename,
    state,
    now() - xact_start AS transaction_age
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
ORDER BY xact_start;
```

A long transaction may be legitimate, but it should be understood.

## Idle in transaction

Especially suspicious:

```text
state = idle in transaction
```

The application started a transaction and then stopped issuing SQL.

This can happen when code:

- forgets to commit/rollback,
- waits for user input,
- performs an external API call inside a transaction.

Keep transaction scopes short.

## Lock waits

A slow query may be fast SQL waiting behind another transaction.

Conceptually:

```text
Transaction A holds row lock
          │
          ▼
Transaction B waits
          │
          ▼
latency grows
```

Check wait events, blockers, and transaction age before rewriting the query.

## Deadlocks

A deadlock:

```text
T1 holds A, waits for B
T2 holds B, waits for A
```

The database detects the cycle and aborts one transaction.

Fixes may include:

- acquire locks in consistent order,
- shorten transactions,
- reduce rows touched,
- retry aborted transactions.

Do not "fix" deadlocks only by increasing timeouts.

## Connection pressure

Applications often fail at the pool before the database maxes CPU.

```text
requests
   │
   ▼
connection pool
   │
   ├── available -> query runs
   └── empty     -> request waits
```

Measure:

- pool size,
- checked-out connections,
- wait time,
- timeout count.

A larger pool is not always better.

Too many active connections can increase:

- memory use,
- context switching,
- contention.

## Find expensive queries

Two dimensions matter:

1. **slow per execution**,
2. **expensive in aggregate**.

Example:

```text
query A: 3 seconds × 1/day
query B: 20 ms × 10 million/day
```

Query B may consume more total resources.

## pg_stat_statements

PostgreSQL's `pg_stat_statements` extension aggregates normalized query statistics.

Useful fields include:

- calls,
- total execution time,
- mean execution time,
- rows.

A typical investigation can order by cumulative execution time.

Do not enable extensions in production casually; follow deployment/change-control procedures.

## Slow query logs

Database slow-query logging is another source.

For PostgreSQL, `log_min_duration_statement` can log statements exceeding a threshold.

Choose the threshold carefully:

- too high misses important work,
- too low floods logs.

Prefer parameter-aware/protected logging that does not expose secrets.

## Query plan

Once a problematic query is known, inspect its execution plan.

PostgreSQL:

```sql
EXPLAIN
SELECT ...
```

For actual runtime:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT ...
```

`ANALYZE` executes the query.

Use caution with:

- UPDATE,
- DELETE,
- expensive production queries.

Run destructive statements inside a safe test environment or transaction that you deliberately roll back.

## What to read in EXPLAIN

Look for:

- actual rows versus estimated rows,
- sequential scans,
- repeated nested loops,
- sorts,
- hash tables,
- disk spills,
- buffer reads/hits,
- filters removing many rows.

A plan node is not "bad" by name.

A sequential scan can be correct for a small table or query reading most rows.

## Estimation errors

The optimizer relies on statistics.

If it expects:

```text
10 rows
```

but receives:

```text
10,000,000 rows
```

it may choose a poor join strategy.

Update/analyze statistics and inspect data distribution before forcing plans.

## Cardinality skew

Uniform averages hide skew.

Example:

```text
tenant A = 80% of rows
other tenants = 20%
```

A parameterized query can behave very differently for tenant A than tenant Z.

Benchmark representative parameter values.

## Indexes

Choose indexes from real access patterns.

Example query:

```sql
SELECT
    order_id,
    created_at,
    total
FROM orders
WHERE customer_id = $1
ORDER BY created_at DESC
LIMIT 20;
```

A candidate index:

```sql
CREATE INDEX idx_orders_customer_created
ON orders(customer_id, created_at DESC);
```

Validate with the execution plan.

## Index trade-offs

Every index costs:

- disk,
- memory/cache,
- insert/update/delete work,
- vacuum/maintenance.

More indexes can improve reads while slowing writes.

Remove an index only after understanding:

- constraint use,
- rare but critical queries,
- statistic reset history.

## Sargability

A predicate that lets the engine use an index search is often called sargable.

Less index-friendly:

```sql
WHERE DATE(created_at) = DATE '2026-10-01'
```

Often better:

```sql
WHERE created_at >= TIMESTAMP '2026-10-01 00:00:00'
  AND created_at <  TIMESTAMP '2026-10-02 00:00:00'
```

The second form exposes a range on the indexed column.

Timezone semantics must match the business requirement.

## SELECT only what is needed

Avoid:

```sql
SELECT *
```

for hot paths when only a few columns are needed.

Benefits:

- less network transfer,
- less memory,
- possible covering/index-only paths,
- clearer API contract.

## Batch operations

Bad:

```text
10,000 network round trips
one INSERT each
```

Better:

- multi-row insert,
- bulk load,
- batch execution.

Reduce round trips before micro-tuning server settings.

## N+1 queries

Application code can generate many tiny queries.

```text
1 query for users
+
1 query per user's orders
```

For 1,000 users:

```text
1,001 queries
```

Use:

- joins,
- select-in/eager loading,
- explicit projections.

See the ORM query-performance note in chapter 14.

## Temporary files

Large sorts/hash operations may spill to disk.

A rise in temp bytes can indicate:

- insufficient per-operation memory,
- unexpectedly large result sets,
- poor plans.

Do not simply raise memory globally.

Per-operation memory multiplied by concurrent operations can exhaust the host.

## Memory model

If:

```text
work_mem = 64 MB
```

that is not necessarily one 64 MB allocation per connection.

One query may have several sort/hash nodes, and many sessions can execute concurrently.

Capacity model:

```text
per-operation memory
× operations per query
× concurrent queries
```

must fit host memory with headroom.

## Cache hit ratio

A high cache hit ratio is not proof of efficiency.

A query can repeatedly scan millions of cached pages and still waste CPU.

Use cache metrics together with:

- rows read,
- plan shape,
- latency,
- total workload.

## Storage latency

Database performance is sensitive to:

- fsync latency,
- random read latency,
- write throughput,
- queue depth.

Measure the storage layer rather than assuming "SSD" is enough.

Cloud disks often have independent:

- capacity,
- IOPS,
- throughput,
- burst limits.

## WAL / transaction log

High write load generates WAL/redo.

Monitor:

- WAL generation rate,
- checkpoint behavior,
- archive backlog,
- replica replay lag,
- disk capacity.

A sudden WAL spike may come from:

- bulk update,
- index build,
- migration,
- high insert volume.

## Checkpoints

Checkpoints bound crash recovery work but can create I/O pressure.

Too frequent:

```text
more checkpoint I/O
```

Too infrequent:

```text
more recovery/log requirements
```

Tune only with measured checkpoint/WAL behavior and engine documentation.

## Autovacuum and dead tuples

PostgreSQL MVCC leaves obsolete row versions until cleanup.

Monitor:

- `n_dead_tup`,
- autovacuum activity,
- table growth,
- long transactions.

Turning off autovacuum to reduce load usually creates larger problems.

## Bloat

A large table/index is not automatically bloated.

Bloat investigation should compare:

- live rows,
- dead rows,
- expected size,
- workload churn,
- free space.

Avoid routine rebuilds without evidence.

## Replication lag

Lag can be measured by:

- bytes/log position,
- wall-clock replay delay,
- queue depth.

Different measures answer different questions.

A replica "5 MB behind" may be seconds or minutes depending on write rate.

## Read replicas

Moving reads to replicas can reduce primary load, but introduces:

- staleness,
- replication capacity,
- failover complexity.

Do not send read-after-write requests to a lagging replica unless the product tolerates it.

## Dashboards

Organize dashboards by questions:

### User experience

- request/query latency,
- throughput,
- errors.

### Resource saturation

- CPU,
- memory,
- storage,
- connections.

### Database contention

- locks,
- long transactions,
- deadlocks.

### Data safety

- replication lag,
- backup success,
- disk headroom.

A dashboard full of 100 unprioritized charts is hard to use during an incident.

## Alert design

Alert on actionable conditions.

Bad:

```text
CPU > 70% for 1 minute
```

Better depends on the service:

```text
p99 latency over SLO for 10 minutes
AND connection-pool wait increasing
```

Use symptom alerts plus supporting diagnostic metrics.

## Capacity headroom

Performance and capacity planning overlap.

Track growth:

```text
disk used
connections
WAL volume
table size
query rate
```

Forecast when limits will be reached.

Do not wait until the disk is 99% full.

## Benchmarking

A benchmark should resemble production:

- data size,
- skew,
- concurrency,
- query mix,
- indexes,
- hardware,
- network,
- transaction boundaries.

A single query on an empty laptop database does not predict production.

## Load testing

Increase load gradually.

Observe:

```text
throughput increases
latency stable
        │
        ▼
saturation point
        │
        ▼
latency rises / throughput flattens
```

The knee of the curve reveals practical capacity.

## One change at a time

If you simultaneously:

- add index,
- change memory,
- change query,
- increase pool size,

you may not know which change mattered.

Keep a tuning log:

```text
problem
baseline
hypothesis
change
result
rollback
```

## Regression testing

Important query plans can change after:

- engine upgrades,
- statistics changes,
- schema changes,
- data growth.

Performance tests should be part of major upgrades and migrations.

## Security and observability

Monitoring data can be sensitive.

Avoid exposing:

- raw SQL with secrets,
- connection strings,
- personally identifiable values,
- credentials.

Restrict access to performance dashboards and query logs.

## Common mistakes

### Tuning without a baseline

No way to prove improvement.

### Increasing every memory setting

Concurrency can exhaust RAM.

### Adding indexes for every predicate

Writes and storage degrade.

### Ignoring pool wait

Application queues before SQL runs.

### Looking only at averages

Tail latency remains hidden.

### Treating CPU as the only bottleneck

Locks/storage/network may dominate.

### Running EXPLAIN ANALYZE on destructive SQL in production

It executes the statement.

## Tuning workflow

1. Define the user-visible symptom.
2. Confirm it with latency/error metrics.
3. Identify the database operation.
4. Check waits and contention.
5. Inspect query frequency and cumulative cost.
6. Read the execution plan.
7. Check indexes/statistics/data skew.
8. Check resource saturation.
9. Make the smallest justified change.
10. Repeat the same measurement.
11. Monitor for regressions.

## Related notes

- [Capacity planning](03_capacity_planning.md)
- [Database hardening](11_database_hardening_and_patch_management.md)
- [Query optimization](../08_database_performance/01_query_optimization_techniques.md)
- [Indexing](../05_storage_and_indexing/05_indexing.md)
- [ORM query performance](../14_orm/04_relationship_loading_and_query_performance.md)
