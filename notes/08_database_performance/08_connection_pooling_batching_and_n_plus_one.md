# Connection Pooling, Batching, Round Trips, and N+1 Queries

Database performance is not only query execution time.

A request can be slow because it spends time:

~~~text
waiting for connection
opening connection
network round trip
executing SQL
transferring rows
deserializing rows
application work
~~~

Optimizing only the SQL plan can miss most of the latency.

## Connection setup has cost

Opening a connection may involve TCP setup, TLS, authentication, session initialization, and server resources.

Creating a new connection for every small query wastes work.

## Connection pool

A pool reuses a bounded set of open connections.

~~~text
requests
   |
   v
connection pool
   |
   +--> connection 1
   +--> connection 2
   +--> connection 3
   |
   +--> wait queue when all busy
~~~

The pool both saves setup cost and limits concurrency.

## Pool is also a queue

If all connections are busy, a request can spend time waiting before SQL starts.

Measure:

- pool acquisition time,
- active connections,
- idle connections,
- waiters,
- pool timeout count.

A database query can appear fast in server metrics while application latency is high because of pool wait.

## Bigger pool is not always faster

A larger pool can increase:

- database memory use,
- concurrent locks,
- CPU context switching,
- I/O contention,
- tail latency.

Size the pool from measured database capacity and application demand, not from the maximum number of web requests.

## Multiple application instances

Ten application instances with pool size 50 can create:

~~~text
10 × 50 = 500 potential connections
~~~

Fleet-wide concurrency matters.

## Pool timeout and backpressure

Do not let requests wait forever.

A bounded acquisition timeout creates backpressure and can protect the database during overload.

~~~text
pool exhausted
    |
wait briefly
    |
timeout or degrade
~~~

## Transaction cleanup

Return a connection to the pool only after:

- commit or rollback,
- cursor cleanup,
- transaction cleanup,
- required session-state reset.

A leaked open transaction can hold locks and surprise the next user of the connection.

## Session state

Database sessions may retain:

- temporary tables,
- role changes,
- isolation level,
- prepared statements,
- session variables.

Pool mode must match the application.

## External poolers

Tools such as PgBouncer can reduce backend connection count.

Pooling mode matters. Transaction-level pooling may not preserve every session-level feature.

## Round trips

Suppose an application inserts 10,000 rows one at a time:

~~~text
10,000 rows
× one request each
= 10,000 round trips
~~~

Even fast statements become slow.

Batching reduces protocol and server overhead.

## Multi-row insert

Instead of one statement per row:

~~~sql
INSERT INTO events(...) VALUES (...);
INSERT INTO events(...) VALUES (...);
INSERT INTO events(...) VALUES (...);
~~~

use a multi-row insert where appropriate:

~~~sql
INSERT INTO events(...)
VALUES
  (...),
  (...),
  (...);
~~~

For serious ingestion, prefer the database's bulk-load API.

## Runnable PostgreSQL demo

The repository adds:

scripts/performance/postgres_pool_and_batch_demo.py

Run:

~~~bash
cd scripts
bash setup/start_postgres.sh
cd ..
python scripts/performance/postgres_pool_and_batch_demo.py
~~~

The script measures on the local development database:

- repeated single-row execute calls,
- batched multi-row inserts,
- repeated pooled connection checkout.

The numbers are machine-specific. The value is seeing the difference in work shape.

## Batch size trade-off

A batch that is too large can:

- consume memory,
- create long transactions,
- hold locks longer,
- generate large WAL bursts,
- exceed protocol/statement limits.

Use bounded batches and measure.

## Commit frequency

Committing every row can force repeated durability work.

One enormous transaction can hold resources for too long.

Balance:

- atomicity requirement,
- durability overhead,
- failure recovery,
- lock duration,
- WAL/redo volume.

## Bulk load

For PostgreSQL, COPY is designed for high-throughput loading.

Other engines expose:

- bulk loader,
- array/batch protocol,
- import command.

Use the native bulk path when loading large volumes.

## N+1 query problem

Suppose a page loads 100 customers:

~~~sql
SELECT * FROM customers LIMIT 100;
~~~

Then application code loops:

~~~text
for each customer:
    SELECT * FROM orders WHERE customer_id = ?
~~~

Total:

~~~text
1 + 100 = 101 queries
~~~

Each SQL statement can be individually fast while the request is slow due to repeated round trips.

## Fix N+1 with set-based retrieval

Possible fixes:

- join,
- one second query with IN (...),
- ORM select-in/eager loading,
- aggregate query,
- precomputed summary.

The best choice depends on result size and duplication.

## One giant join can also be bad

Joining:

~~~text
customer
× orders
× order_items
~~~

can multiply rows dramatically.

Sometimes two set-based queries are better:

1. fetch customers,
2. fetch all orders for those IDs.

This is why select-in loading is useful in many ORMs.

## Existing ORM demonstration

The repository already includes:

scripts/orm/n_plus_one_demo.py

It counts SQL statements for lazy loading versus select-in loading.

## Large IN lists

Replacing N+1 with one enormous IN list can create another problem.

For very large ID sets, consider:

- chunks,
- temporary table,
- array/table-valued parameter,
- staging table.

## Fetch size and streaming

Large results can be fetched in chunks.

~~~text
server result
   |
   +--> 1,000 rows
   +--> 1,000 rows
   +--> ...
~~~

This reduces client memory.

It does not reduce total server work.

Server-side cursors can be useful for exports and ETL, but they hold a connection/session for longer.

## SELECT only needed columns

Avoid SELECT * on hot paths.

Benefits:

- fewer bytes transferred,
- less deserialization,
- smaller client memory,
- more opportunities for covering indexes.

## Serialization cost

The database can finish quickly while the application spends time converting rows into ORM objects or JSON.

Profile the entire request, not only database execution.

## Async clients

Asynchronous I/O can improve application concurrency while waiting on the database.

It does not make SQL itself faster.

If the database is saturated, unbounded async concurrency makes overload worse.

## Prepared statements

Prepared statements can reduce repeated parse/plan overhead and support parameter binding.

They do not fix:

- missing indexes,
- huge result sets,
- N+1,
- lock contention.

## Timeouts

Set coherent deadlines for:

- pool acquisition,
- statement execution,
- HTTP/request deadline.

The outer request should normally leave time for cancellation and cleanup.

## Cancellation

If the caller no longer needs a result, cancel expensive database work when the driver/framework supports it.

Otherwise the server may continue work for an abandoned request.

## Retries

Retries can amplify overload.

~~~text
database overloaded
     |
requests time out
     |
all clients retry
     |
more load
~~~

Retry only transient failures, use backoff/jitter, and keep writes idempotent.

## Query count per request

Track:

~~~text
SQL statements per HTTP request
~~~

This catches N+1 and accidental repeated lookups quickly.

Pair it with total database time and pool wait.

## Common mistakes

- Opening one connection per query.
- Oversizing pools across a fleet.
- Hiding N+1 behind ORM convenience.
- One row per commit for bulk ingestion.
- One gigantic transaction for every import.
- Treating async as permission for unlimited concurrency.
- Retrying every timeout immediately.

## Performance workflow

1. Measure total request latency.
2. Separate pool wait from SQL time.
3. Count statements per request.
4. Identify repeated queries.
5. Batch set-oriented operations.
6. Bound pool concurrency.
7. Use bulk APIs for ingestion.
8. Stream truly large results.
9. Set timeouts and cancellation.
10. Load test realistic concurrency.

## Related notes

- [Accessing databases in code](05_accessing_database_in_code.md)
- [Query optimization](01_query_optimization_techniques.md)
- [Pagination and large result sets](09_pagination_and_large_result_sets.md)
- [ORM relationship loading](../14_orm/04_relationship_loading_and_query_performance.md)
- [Performance monitoring](../11_security_best_practices/05_performance_monitoring_and_tuning.md)
