# Performance Monitoring and Tuning

Tuning starts with a measured problem: a slow checkout query, rising lock waits, or a report exhausting memory. Collect a baseline, identify the expensive operation, make one justified change, and compare the same workload again.

## Measure user-visible behavior and resource use

| Metric | What it helps explain |
| --- | --- |
| Query latency, including p50/p95/p99 | Typical response times and slow outliers. |
| Throughput and error rate | Whether the service meets demand successfully. |
| CPU, memory, I/O latency, IOPS, bytes per second | Resource pressure and saturation. |
| Active connections and pool wait time | Whether requests are queuing before execution. |
| Lock waits, deadlocks, long transactions | Contention and work held open too long. |
| Data, index, and log size | Capacity use and growth. |
| Replica replay lag | Freshness and failover readiness. |

Read/write throughput in bytes per second is different from operations per second. Many small random I/Os can have low bandwidth but high latency. A high cache hit rate alone does not establish that a query is efficient.

## Build useful dashboards

A database exporter can expose metrics to Prometheus; Grafana can visualize the collected time series. Organize a dashboard around request latency and errors, resource saturation, and database waits. Annotate deployments and maintenance so changes in the workload have context.

Counters need rates over a time interval; gauges represent current values. Avoid averaging away tail latency or mixing nodes with different roles. Alert on sustained symptoms and capacity headroom rather than every brief spike.

## Find expensive queries

Use the engine's query statistics and slow-query facilities. PostgreSQL's `pg_stat_statements` requires configuration; MySQL provides Performance Schema and the slow query log. SQL Server Query Store and Extended Events provide workload and event information.

For MySQL, these administrative settings enable slow logging and set the global threshold for new sessions:

```sql
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;
```

Existing sessions retain their session threshold; set `SESSION long_query_time` when testing there. Query logs may contain sensitive values, so apply the same access controls and retention policy as other operational data.

## Inspect an execution plan

For PostgreSQL:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id, total
FROM orders
WHERE customer_id = 123;
```

This runs the query. Compare estimated and actual rows, repeated loop counts, buffer use, spills, and total execution time. Large estimate errors may indicate outdated statistics or correlated data. A scan can be appropriate when much of a table is needed.

## Correct the access pattern

Prefer a half-open range when selecting a year from a timestamp column:

```sql
SELECT order_id, order_date, total
FROM orders
WHERE order_date >= '2023-01-01'
  AND order_date < '2024-01-01';
```

Unlike `BETWEEN '2023-01-01' AND '2023-12-31'`, this includes the whole final day. Avoiding a function on the indexed column can also make an ordinary date index usable. Define the reporting timezone when boundaries represent local dates.

Choose indexes against real predicates, joins, and ordering. Check write overhead before retaining them. Use partitioning for appropriate pruning and lifecycle management; partitioning does not necessarily distribute data across servers. Sharding does.

## Track index storage separately

PostgreSQL example:

```sql
SELECT relname AS table_name, indexrelname AS index_name,
       idx_scan,
       pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
ORDER BY pg_relation_size(indexrelid) DESC;
```

A large index is not necessarily bloated, and zero scans do not prove that it is unnecessary. It may enforce a constraint, support rare work, or have recently reset statistics. Review an adequate observation period before removal.

## Change configuration with a capacity model

Memory settings can apply per operation or connection. For example, PostgreSQL `work_mem` can be consumed by multiple operations in many simultaneous sessions. A generous value multiplied across the workload can exhaust memory.

Keep a record of the baseline, change, and rollback procedure. Repeat the benchmark with representative data sizes and parameter values, and check latency, throughput, correctness, and resource use together.

## Related notes

- [Query optimization](../08_database_performance/01_query_optimization_techniques.md)
- [Indexing](../05_storage_and_indexing/05_indexing.md)
- [PostgreSQL monitoring](https://www.postgresql.org/docs/current/monitoring.html)
