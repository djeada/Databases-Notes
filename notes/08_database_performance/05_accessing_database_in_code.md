# Accessing Databases in Code

Application code sits between users and the database. A request can be slow even when the SQL engine executes its statements quickly.

A useful lifecycle is:

~~~text
request
  |
acquire connection
  |
begin transaction if needed
  |
execute parameterized SQL
  |
fetch only required data
  |
commit or rollback
  |
return connection to pool
~~~

This note focuses on correct and efficient driver use. For deeper discussion of pools, batching, and N+1 queries, see [Connection Pooling, Batching, Round Trips, and N+1](08_connection_pooling_batching_and_n_plus_one.md).

## Drivers and abstractions

A database driver speaks the database protocol. ORMs and query builders sit above it.

Typical APIs include:

| Language | Database | Driver/API |
| --- | --- | --- |
| Python | PostgreSQL | psycopg / psycopg2 |
| Python | MySQL | mysql-connector-python |
| Python | SQLite | sqlite3 |
| Java | relational databases | JDBC |
| JavaScript | PostgreSQL | pg |
| .NET | SQL Server | ADO.NET / SqlClient |

Understanding the driver lifecycle helps diagnose problems hidden by higher-level frameworks.

## Local PostgreSQL setup

The repository includes:

~~~bash
cd scripts
bash setup/start_postgres.sh
~~~

Local connection:

~~~text
postgresql://demo:secret@127.0.0.1:5432/test
~~~

The credential is intentionally simple for local learning only.

## Basic Python connection

~~~python
import psycopg2

connection = psycopg2.connect(
    "postgresql://demo:secret@127.0.0.1:5432/test"
)

try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT current_database(), current_user")
        print(cursor.fetchone())
finally:
    connection.close()
~~~

Production connection data should normally come from configuration or a secret manager.

## Parameterize values

Unsafe:

~~~python
query = (
    "SELECT order_id FROM orders "
    f"WHERE customer_id = {customer_id}"
)
cursor.execute(query)
~~~

Safe:

~~~python
cursor.execute(
    "SELECT order_id FROM orders WHERE customer_id = %s",
    (customer_id,),
)
~~~

Parameterization separates SQL structure from values and prevents value-position SQL injection.

## Dynamic identifiers

Placeholders generally represent values, not table names or column names.

Use an allowlist:

~~~python
allowed_sort = {
    "date": "order_date",
    "total": "total_cents",
}

sort_column = allowed_sort[user_choice]

cursor.execute(
    f"""
    SELECT order_id, order_date, total_cents
    FROM orders
    ORDER BY {sort_column} DESC
    LIMIT %s
    """,
    (page_size,),
)
~~~

Only trusted application constants become SQL structure.

## Transaction boundaries

A transaction should cover the smallest complete business operation.

Example transfer:

~~~python
with connection:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE accounts
            SET balance = balance - %s
            WHERE account_id = %s
              AND balance >= %s
            """,
            (amount, from_id, amount),
        )

        if cursor.rowcount != 1:
            raise ValueError("insufficient funds")

        cursor.execute(
            """
            UPDATE accounts
            SET balance = balance + %s
            WHERE account_id = %s
            """,
            (amount, to_id),
        )
~~~

The transaction commits on success and rolls back on exception with the psycopg2 connection context manager.

## Keep transactions short

Avoid holding a transaction open while doing unrelated work such as:

- calling an external API,
- waiting for a user,
- sending email,
- rendering a large response.

An open transaction can hold locks, snapshots, and a pool connection.

## Autocommit

Autocommit is useful for truly independent statements.

It is not appropriate when several statements must succeed or fail as one unit.

Know the driver default instead of relying on it accidentally.

## Connection pooling

Opening a connection has setup cost.

Pools reuse a bounded number of sessions.

Runnable demo:

~~~bash
python scripts/performance/postgres_pool_and_batch_demo.py
~~~

The demo compares local connection reuse and batched inserts.

## Fleet-wide pool size

If 20 application processes each allow 30 database connections, the fleet can create 600 sessions.

Pool sizing is a database-capacity decision, not only an application setting.

## Fetch only what is needed

If one row is expected:

~~~python
cursor.execute(
    """
    SELECT order_id, status
    FROM orders
    WHERE order_id = %s
    """,
    (order_id,),
)

row = cursor.fetchone()
~~~

Do not fetch an entire result set just to use the first row.

## Avoid unbounded fetchall

Dangerous shape:

~~~python
cursor.execute("SELECT * FROM huge_events")
rows = cursor.fetchall()
~~~

The client may allocate memory for the entire result.

Use:

- pagination,
- fetchmany,
- streaming/server-side cursor,
- bulk-export APIs.

## Project required columns

Prefer:

~~~sql
SELECT order_id, order_date, status
FROM orders
~~~

over SELECT * when large unused columns exist.

This reduces storage work, network transfer, and object allocation.

## Round trips and N+1

Application loops can create hundreds of queries:

~~~text
load customers
for each customer:
    load orders
~~~

The repository includes:

~~~bash
python scripts/orm/n_plus_one_demo.py
~~~

Set-based retrieval or explicit eager/select-in loading usually reduces round trips.

## Batch writes

With psycopg2:

~~~python
from psycopg2.extras import execute_values

execute_values(
    cursor,
    """
    INSERT INTO events(event_id, payload)
    VALUES %s
    """,
    rows,
    page_size=500,
)
~~~

For very large PostgreSQL loads, use COPY rather than millions of individual INSERT requests.

## Prepared statements

Prepared statements can reduce repeated parsing/planning work depending on engine and driver.

They do not repair:

- a poor index,
- a huge result set,
- N+1,
- lock contention.

## Timeouts

Set limits for:

- pool acquisition,
- statement execution,
- socket/network operations,
- outer HTTP/job deadline.

Timeouts should be coordinated so there is time for cancellation and cleanup.

PostgreSQL session example:

~~~sql
SET statement_timeout = '2s';
~~~

Choose deadlines from the product requirement, not from a copied default.

## Cancellation

If the caller abandons a request, cancel expensive database work when the driver/framework supports it.

Otherwise the server can continue work nobody will use.

## Error categories

Treat failures differently.

Examples:

- constraint/validation error,
- serialization/deadlock conflict,
- connection loss,
- timeout,
- permission error.

Do not retry every database exception.

## Retry transient conflicts

A safe pattern is:

~~~text
run whole transaction
   |
retryable conflict?
   |-- no --> fail
   |
   yes
   |
backoff + jitter
   |
retry from beginning
~~~

Earlier reads may be invalid after a concurrency conflict, so retry the whole logical transaction.

## Timeout ambiguity

A client can time out after the server committed but before the response arrived.

Therefore:

~~~text
timeout != definitely rolled back
~~~

Use idempotency keys or stable business identifiers for externally retried create operations when needed.

## Connection loss

After a connection-level error, do not assume the session can safely continue.

Discard or reset the connection according to driver/pool behavior.

## Application identity

PostgreSQL clients can set application_name.

Example:

~~~text
application_name=checkout-api
~~~

This makes sessions easier to attribute in pg_stat_activity.

## Observe active sessions

~~~sql
SELECT
    pid,
    usename,
    application_name,
    state,
    wait_event_type,
    wait_event
FROM pg_stat_activity;
~~~

This can distinguish application pool/session problems from query execution problems.

## Serialization cost

Database execution may be fast while application time is spent on:

- ORM object creation,
- JSON encoding,
- network response generation.

Measure the full request path.

## Async database clients

Async I/O lets application workers do other work while waiting.

It does not make the database execute SQL faster.

Bound concurrency so an async service does not overwhelm the database.

## Read replicas

Routing reads to replicas can reduce primary load.

But replicas can lag.

Mark operations that require:

- read-your-write,
- primary/leader read,
- stale-tolerant replica read.

Replica routing is a consistency decision as well as a performance decision.

## Logging

Useful fields include:

- query fingerprint/name,
- duration,
- row count,
- request ID,
- application name.

Avoid logging:

- passwords,
- full connection strings,
- sensitive parameter values,
- huge query results.

## ORMs

ORMs can hide query count and transaction lifetime.

Enable SQL/query metrics during development and diagnose generated SQL like hand-written SQL.

See chapter 14 for ORM-specific examples.

## Runtime versus migration credentials

The public application should generally not use the high-privilege role used for schema migrations.

This reduces accidental DDL and security blast radius.

## Efficient access checklist

1. Are values parameterized?
2. Are transactions short?
3. Are connections pooled?
4. Is fleet-wide pool size bounded?
5. Is query count per request visible?
6. Are writes batched where useful?
7. Are bulk APIs used for large ingestion?
8. Are only needed rows and columns fetched?
9. Are large results streamed or paginated?
10. Are timeouts and cancellation configured?
11. Are retries limited to retryable failures?
12. Are retried writes idempotent?
13. Are replica consistency requirements explicit?
14. Are logs free of credentials and sensitive values?

## Review questions

1. Why can a request be slow when server-side SQL execution is fast?
2. Why should transaction scope follow a business invariant rather than an entire HTTP request automatically?
3. What performance problem does batching solve?
4. Why does asynchronous I/O not increase database capacity by itself?
5. Why can a timeout be ambiguous for a write?
6. Why can fetchall be dangerous for large results?
7. How can pool metrics distinguish application queueing from slow SQL?

## Related notes

- [Connection pooling, batching, and N+1](08_connection_pooling_batching_and_n_plus_one.md)
- [Pagination and large result sets](09_pagination_and_large_result_sets.md)
- [SQL injection](../11_security_best_practices/06_sql_injection.md)
- [ORM introduction](../14_orm/01_introduction_to_orm.md)
- [ORM query performance](../14_orm/04_relationship_loading_and_query_performance.md)
