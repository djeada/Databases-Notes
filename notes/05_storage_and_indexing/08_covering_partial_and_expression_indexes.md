# Covering, Partial, and Expression Indexes

A basic index answers:

> How can the engine locate matching rows?

More specialized index designs answer:

- Can the query be satisfied from the index without fetching table columns?
- Can the index omit rows that are rarely useful?
- Can it index a function or derived value?

These patterns can make hot access paths much smaller or cheaper.

## Covering indexes

Suppose the query is:

~~~sql
SELECT order_date, total_cents
FROM orders
WHERE customer_id = 42
ORDER BY order_date DESC
LIMIT 20;
~~~

Search/order key:

~~~text
customer_id, order_date
~~~

Returned payload:

~~~text
total_cents
~~~

A covering index stores all values required by the query.

## PostgreSQL INCLUDE

~~~sql
CREATE INDEX idx_orders_customer_date
ON orders(customer_id, order_date DESC)
INCLUDE (total_cents);
~~~

customer_id and order_date are key columns.

total_cents is stored as non-key payload.

Payload columns do not affect:

- search ordering,
- uniqueness semantics.

## Unique index with INCLUDE

~~~sql
CREATE UNIQUE INDEX ux_users_email
ON users(email)
INCLUDE (display_name);
~~~

Uniqueness applies to email only.

display_name is payload.

## Index-only scans

Conceptually:

~~~text
normal index scan:
index -> table/heap -> result

index-only scan:
index -------------> result
~~~

A covering index can make an index-only scan possible.

But all values being present in the index does not guarantee zero table visits in every engine.

## PostgreSQL visibility requirement

PostgreSQL indexes do not contain full tuple visibility state.

The visibility map helps determine whether heap access can be skipped.

Therefore:

~~~text
covering index
does not guarantee
no heap visits
~~~

A frequently updated table may get less benefit than a mostly stable one.

## Covering-index trade-off

Payload columns make index leaves wider.

Costs:

- more pages,
- more cache pressure,
- more write work,
- larger storage footprint,
- possible index tuple-size limits.

Do not INCLUDE every SELECT column mechanically.

## SQLite covering index

SQLite can report a covering-index plan when every requested value is available in the index.

Example:

~~~sql
CREATE INDEX idx_orders_customer_date_total
ON orders(customer_id, order_date DESC, total_cents);
~~~

SQLite does not use PostgreSQL's INCLUDE syntax here; total_cents is another index key column.

## Partial indexes

A partial index stores only rows satisfying a predicate.

~~~sql
CREATE INDEX idx_open_orders_customer_date
ON orders(customer_id, order_date DESC)
WHERE status = 'open';
~~~

Only open orders occupy this index.

## Why partial indexes help

Suppose:

~~~text
95% closed historical orders
5% open orders
~~~

and the application frequently reads open orders.

Full index:

~~~text
index all orders
~~~

Partial index:

~~~text
index only open orders
~~~

Potential benefits:

- smaller tree,
- less cache usage,
- fewer index updates for unrelated rows.

## Query must match the predicate

A partial index on:

~~~sql
WHERE status = 'open'
~~~

can support:

~~~sql
WHERE customer_id = 42
  AND status = 'open'
~~~

It cannot safely answer a query for every status because closed rows are absent.

The optimizer must prove the query condition implies the index predicate.

## Parameterized queries and partial indexes

Planner behavior can be subtle with parameterized predicates.

A generic condition such as:

~~~text
status = ?
~~~

may not always allow the planner to prove that the predicate means:

~~~text
status = 'open'
~~~

at plan time.

Behavior depends on engine and planning mode.

Inspect the real plan.

## Soft-delete pattern

Table:

~~~text
users
├── id
├── email
└── deleted_at
~~~

Most queries need only live users.

Candidate:

~~~sql
CREATE INDEX idx_users_live_email
ON users(email)
WHERE deleted_at IS NULL;
~~~

Deleted rows are not carried in the active lookup index.

## Partial unique index

A useful correctness pattern:

~~~sql
CREATE UNIQUE INDEX ux_active_email
ON users(email)
WHERE deleted_at IS NULL;
~~~

This can enforce:

~~~text
email unique among active rows
~~~

while keeping historical deleted rows.

Use it only if that matches the business rule.

## Expression indexes

An expression index stores the result of a function/expression.

~~~sql
CREATE INDEX idx_users_lower_email
ON users(lower(email));
~~~

Query:

~~~sql
SELECT user_id
FROM users
WHERE lower(email) = lower($1);
~~~

The engine can search the indexed expression instead of evaluating lower(email) over every candidate row.

## Good expression-index use cases

Examples:

- normalized text,
- extracted JSON scalar,
- date bucket,
- arithmetic transformation,
- derived lookup key.

The query expression still needs to align with what the optimizer can match to the index.

## Determinism and immutability

Databases usually restrict indexed expressions to functions whose result is stable for the same stored row.

PostgreSQL requires index expressions to use immutable functions.

The index must be able to trust:

~~~text
same row values -> same index key
~~~

until the row changes.

## Generated-column alternative

Instead of indexing:

~~~text
lower(email)
~~~

you can sometimes define a generated/stored column:

~~~text
normalized_email
~~~

and index that field.

Advantages:

- visible schema meaning,
- reuse by queries and tools.

Trade-offs depend on engine and storage behavior.

## JSON indexing

Suppose a JSON document contains:

~~~text
country
tags
nested attributes
~~~

Different operations can require different index structures.

Examples:

- B-tree/expression index for one extracted scalar,
- GIN/inverted index for containment/membership.

There is no single "JSON index" that optimizes every JSON query.

## Combining partial and covering

PostgreSQL example:

~~~sql
CREATE INDEX idx_open_orders
ON orders(customer_id, order_date DESC)
INCLUDE (total_cents)
WHERE status = 'open';
~~~

This combines:

- smaller indexed subset,
- customer/date navigation,
- payload for possible index-only access.

Powerful, but specialized.

## Combining expression and partial

~~~sql
CREATE INDEX idx_active_users_lower_email
ON users(lower(email))
WHERE deleted_at IS NULL;
~~~

The index represents:

~~~text
normalized email of active users
~~~

It can also be UNIQUE if that is the desired constraint.

## Too-specialized indexes

A narrowly optimized index may be used by only one rare query.

Costs remain:

- storage,
- inserts,
- updates,
- vacuum/maintenance,
- backups.

Track usage over a meaningful observation period.

## Covering index versus composite key

Suppose a query filters on x and returns y.

Two PostgreSQL designs:

~~~sql
CREATE INDEX idx_xy
ON t(x, y);
~~~

versus:

~~~sql
CREATE INDEX idx_x_include_y
ON t(x) INCLUDE (y);
~~~

Both contain y.

But in the second design:

- y is not a navigation key,
- uniqueness can still apply only to x,
- upper tree levels can stay smaller.

Use INCLUDE when y is payload rather than a search key.

## Runnable SQLite demonstration

This chapter adds:

~~~text
scripts/indexing/sqlite_covering_index_demo.py
~~~

Run:

~~~bash
python scripts/indexing/sqlite_covering_index_demo.py
~~~

It compares:

- a filter/order index that still needs the table payload,
- a covering index that contains the selected payload.

The script prints EXPLAIN QUERY PLAN output.

## Runnable PostgreSQL demonstration

This chapter also adds:

~~~text
scripts/indexing/postgres_partial_expression_indexes.sql
~~~

Run:

~~~bash
docker exec -i postgres-local \
  psql -U demo -d test \
  < scripts/indexing/postgres_partial_expression_indexes.sql
~~~

The exercise creates:

- a partial index for open orders,
- an expression index on lower(email),
- EXPLAIN examples for matching predicates.

## Design checklist

### Covering

- Is the query hot enough to justify duplicate payload?
- Are included columns narrow?
- Is index-only access realistic for the table's update pattern?

### Partial

- Is the indexed subset substantially smaller?
- Do important queries explicitly imply the predicate?
- Will rows move in and out of the predicate frequently?

### Expression

- Does the application query the expression repeatedly?
- Is the expression valid/deterministic for indexing?
- Would a generated/normalized schema field be clearer?

## Common mistakes

- Including every returned column in an index.
- Creating a partial index whose predicate queries do not express.
- Building an expression index but querying a different expression.
- Assuming a covering index permanently eliminates table access.
- Combining every specialization into one huge index without measuring cost.

## Related notes

- [Composite indexes and column order](07_composite_indexes_and_column_order.md)
- [Database indexing](05_indexing.md)
- [Specialized index structures](10_specialized_index_structures.md)
- [Execution plans](../08_database_performance/07_execution_plans_statistics_and_cardinality.md)
