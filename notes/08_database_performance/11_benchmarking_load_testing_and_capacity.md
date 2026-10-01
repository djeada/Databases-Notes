# Benchmarking, Load Testing, and Capacity Planning

A performance claim without a workload definition is incomplete.

"Query X takes 5 ms" is useful only when you know:

- data size,
- parameter values,
- cache state,
- concurrency,
- hardware,
- database version/configuration.

Benchmarking should model the production question you are trying to answer.

## Microbenchmark versus workload test

Microbenchmark:

~~~text
one query
one parameter
one connection
~~~

Useful for isolating a query change.

Load/workload test:

~~~text
many query types
realistic read/write ratio
many concurrent clients
~~~

Useful for system capacity and interactions.

Use both for different questions.

## Define the hypothesis

Good benchmark question:

> Does the composite index reduce p95 latency for the open-orders endpoint under 100 concurrent requests without increasing write latency beyond the allowed target?

Bad benchmark question:

> Is the new index faster?

The first defines success and trade-offs.

## Representative data volume

Indexes and plans change as tables grow.

Test near realistic scale.

A 1,000-row table cannot demonstrate behavior of a billion-row table.

If full scale is impossible, preserve:

- cardinality,
- skew,
- row width,
- index selectivity.

## Data skew

Synthetic uniform IDs can hide production hotspots.

Include:

- largest tenant,
- popular product,
- common status,
- rare status,
- burst traffic.

## Workload mix

Example:

~~~text
60 percent product reads
20 percent order reads
10 percent order writes
5 percent search
5 percent background jobs
~~~

A change that improves one query may hurt the total system through cache or write amplification.

## Concurrency

Latency under one connection can look excellent.

Increase concurrent clients gradually.

Typical curve:

~~~text
load increases
    |
throughput rises
    |
saturation point
    |
latency rises sharply
throughput flattens
~~~

The knee of the curve is important capacity information.

## Coordinated omission

A load generator can under-report latency if it waits for a slow request before scheduling the next one.

Real traffic may continue arriving while the service is slow.

Use load tools/methods that preserve intended arrival rate when latency distributions matter.

## Percentiles

Track:

- p50,
- p95,
- p99,
- max carefully,
- error/timeout rate.

Average latency hides tail behavior.

## Throughput

Measure:

~~~text
requests/sec
transactions/sec
rows/sec
MB/sec
~~~

Choose the unit that matches the workload.

## Error rate

A system is not "fast" if it returns errors under load.

Include:

- timeout rate,
- deadlocks,
- failed transactions,
- connection failures.

## Resource metrics

During load testing, observe:

- CPU,
- memory,
- I/O latency/IOPS,
- disk throughput,
- connections,
- pool wait,
- lock waits,
- temp files,
- WAL/redo,
- replication lag.

This explains the saturation point.

## Warm-up

JIT compilation, caches, connection pools, and buffer caches may change during the first minutes.

Separate:

- warm-up period,
- measured steady state.

For cold-start questions, test cold state intentionally.

## Cold-cache benchmark

A cold-cache test is valid only when the product question is cold-start behavior.

Do not clear caches just because it seems more "fair."

Most production systems operate warm most of the time.

## Repeated trials

One run can be noise.

Run several trials and report distribution or confidence, not only the best number.

## Change one variable

If you simultaneously change:

- database version,
- index,
- instance size,
- pool size,

you cannot attribute the result.

Control variables where possible.

## Correctness first

Verify the optimized query returns the same:

- rows,
- ordering,
- totals,
- null semantics.

A faster wrong query is not an optimization.

## Write cost

If you add an index, benchmark writes too.

Measure:

- insert latency,
- update latency,
- storage growth,
- WAL/redo,
- checkpoint pressure.

Read optimization shifts work elsewhere.

## Benchmark environment

Document:

- CPU/RAM,
- storage type,
- database version,
- settings,
- dataset size,
- client location,
- network.

Without context, benchmark numbers are not reproducible.

## Production shadow testing

Where safe, production-like traffic can be replayed against a staging/shadow environment.

Benefits:

- realistic parameter distribution,
- real query mix.

Risks:

- sensitive data,
- accidental writes,
- external side effects.

Sanitize and isolate carefully.

## Query replay

Capture normalized query patterns and parameter distributions, then replay against a copy.

Useful for:

- upgrades,
- index changes,
- configuration changes.

Do not replay destructive production writes into a shared environment.

## Load generators

Common categories:

- HTTP load generators,
- database-specific tools,
- custom application workload drivers.

Examples include pgbench for PostgreSQL and sysbench for some database workloads.

The tool matters less than modeling the right request pattern.

## pgbench concept

pgbench can test PostgreSQL transaction throughput.

Use custom scripts when the default transaction does not resemble your application.

A benchmark that does not match the workload answers the wrong question precisely.

## Think time

Users do not always issue requests back-to-back.

For interactive workloads, model pauses/arrival rates realistically.

For batch ingestion, maximum sustained throughput may be the correct goal.

## Burst testing

Production traffic can spike.

Test:

~~~text
steady baseline
   |
sudden 5x burst
   |
recovery
~~~

Observe:

- queue growth,
- pool exhaustion,
- recovery time.

## Soak testing

Run a sustained workload for hours.

This catches:

- memory leaks,
- growing connection count,
- bloat,
- cache churn,
- compaction/vacuum effects.

Short benchmarks miss long-term maintenance behavior.

## Failure testing under load

Performance during failover matters.

Test:

- replica failover,
- node restart,
- network delay,
- storage throttling,

while workload continues.

Measure both availability and recovery latency.

## Capacity model

A simple throughput model:

~~~text
peak requests/sec
× database operations/request
= database ops/sec demand
~~~

Then include:

- growth factor,
- burst headroom,
- background jobs,
- failover headroom.

## Headroom

Running permanently at 95 percent of a bottleneck resource leaves little room for spikes or node failure.

Capacity planning should include operational reserve.

## Replication headroom

If a primary fails and one replica becomes primary, the remaining topology must absorb the workload.

Capacity needs to cover degraded mode, not only healthy mode.

## Queueing

Near saturation, small increases in utilization can cause large increases in latency.

This is why "CPU went from 80 to 90 percent" can produce a disproportionate p99 increase.

Measure queue/wait metrics.

## Cost-performance

Compare:

~~~text
requests/sec per euro
latency at fixed monthly cost
cost for target SLO
~~~

A faster architecture may not be cost-effective.

## Regression gate

For critical workloads, CI/performance pipelines can reject significant regressions.

Example gate:

~~~text
p95 must not degrade by > 10 percent
errors must remain < 0.1 percent
~~~

Use stable environments and enough repetitions to avoid noisy false failures.

## Runnable benchmark exercises

This PR adds local scripts that generate synthetic data and measurements:

- scripts/performance/sqlite_query_plan_demo.py
- scripts/performance/sqlite_pagination_demo.py
- scripts/performance/sqlite_index_write_cost_demo.py
- scripts/performance/postgres_pool_and_batch_demo.py

These are teaching tools, not standardized database rankings.

## Benchmark report template

Record:

~~~text
goal:
dataset:
hardware:
database version:
configuration:
workload:
concurrency:
warm-up:
duration:
p50/p95/p99:
throughput:
errors:
CPU/memory/I/O:
change tested:
result:
trade-offs:
~~~

## Common mistakes

- Benchmarking tiny datasets.
- Reporting only average latency.
- Ignoring errors.
- One client only.
- Uniform synthetic data hiding skew.
- Comparing warm versus cold runs.
- Changing multiple variables.
- Ignoring write cost.
- Treating laptop numbers as production capacity.
- Running benchmark tools against production without safeguards.

## Related notes

- [Performance monitoring](../11_security_best_practices/05_performance_monitoring_and_tuning.md)
- [Capacity planning](../11_security_best_practices/03_capacity_planning.md)
- [Query optimization](01_query_optimization_techniques.md)
- [Connection pooling and batching](08_connection_pooling_batching_and_n_plus_one.md)
