# Composite Indexes and Column Order

A composite index contains more than one key column.

Example:

~~~sql
CREATE INDEX idx_orders_customer_status_date
ON orders(customer_id, status, order_date DESC);
~~~

Column order is part of the data structure. The useful question is not merely which columns appear in WHERE, but which ordered access path the query needs.

## Lexicographic ordering

A B-tree on:

~~~text
(customer_id, status, order_date)
~~~

is ordered conceptually like words in a dictionary:

~~~text
customer first
then status within customer
then date within customer + status
~~~

Example sequence:

~~~text
(41, closed, 2026-09-01)
(41, open,   2026-08-10)
(41, open,   2026-09-15)
(42, closed, 2026-09-01)
(42, open,   2026-08-20)
(42, open,   2026-10-01)
~~~

That ordering determines which predicates can narrow the scan efficiently.

## Leading prefix

Query:

~~~sql
WHERE customer_id = 42
~~~

can use the index because all rows for customer 42 are adjacent.

Query:

~~~sql
WHERE customer_id = 42
  AND status = 'open'
~~~

uses a longer leading prefix.

## Missing the leading column

Query:

~~~sql
WHERE status = 'open'
~~~

does not constrain customer_id.

Open rows are spread across every customer group.

Modern engines can sometimes use skip-scan, bitmap combinations, or the index for special reasons, but a conventional composite B-tree is not primarily ordered by status.

Do not assume every suffix predicate receives a direct seek.

## Equality then range

Query:

~~~sql
WHERE customer_id = 42
  AND order_date >= '2026-10-01'
ORDER BY order_date;
~~~

Candidate:

~~~sql
CREATE INDEX idx_orders_customer_date
ON orders(customer_id, order_date);
~~~

The engine can seek to customer 42 and then walk that customer's date range.

## Equality, equality, range

Query:

~~~sql
WHERE tenant_id = ?
  AND status = ?
  AND created_at >= ?
ORDER BY created_at;
~~~

A natural candidate is:

~~~text
(tenant_id, status, created_at)
~~~

The equality columns establish a prefix; created_at defines the range.

This is a useful heuristic, not a universal formula.

## "Most selective first" is incomplete

A common rule says to put the most selective column first.

That ignores:

- required sort order,
- tenant/locality boundaries,
- range predicates,
- join access,
- other important queries.

A tenant_id column can correctly lead an index even if it is less selective than another predicate because every query must remain inside one tenant.

## ORDER BY after equality

Index:

~~~sql
CREATE INDEX idx_orders_customer_date
ON orders(customer_id, order_date DESC);
~~~

Query:

~~~sql
WHERE customer_id = 42
ORDER BY order_date DESC
LIMIT 20;
~~~

Since customer_id is fixed, the remaining order already matches order_date DESC.

This can eliminate a large sort.

## Mixed sort directions

Some engines support mixed index ordering.

PostgreSQL example:

~~~sql
CREATE INDEX idx_leaderboard
ON leaderboard(category ASC, score DESC);
~~~

Useful query:

~~~sql
WHERE category = 'database'
ORDER BY score DESC;
~~~

Check engine-specific capabilities and the actual plan.

## Range can end efficient prefix narrowing

Index:

~~~text
(customer_id, order_date, status)
~~~

Query:

~~~sql
WHERE customer_id = 42
  AND order_date >= '2026-01-01'
  AND status = 'open'
~~~

Once order_date becomes a range, status generally cannot narrow one contiguous B-tree region the same way another equality column could.

The engine can still filter status from candidate entries, but may inspect more rows.

A different candidate:

~~~text
(customer_id, status, order_date)
~~~

may fit the workload better.

## One index cannot optimize every query

Suppose two important queries are:

~~~sql
WHERE customer_id = ?
ORDER BY order_date DESC
~~~

and:

~~~sql
WHERE status = 'open'
ORDER BY order_date DESC
~~~

Natural candidates differ:

~~~text
(customer_id, order_date)
(status, order_date)
~~~

Every additional index costs write/storage work.

Prioritize the important workload.

## Composite versus separate indexes

Compare:

~~~text
index A: customer_id
index B: status
~~~

with:

~~~text
index C: (customer_id, status)
~~~

Some engines can combine separate indexes.

A composite index often gives a more direct ordered path and can support ORDER BY.

Separate indexes can better support independent queries.

Use the actual query mix and execution plans.

## Bitmap combination

PostgreSQL can combine multiple indexes through bitmap operations for some queries.

That can help a predicate such as:

~~~sql
WHERE customer_id = ?
  AND status = ?
~~~

Trade-offs:

- extra combination work,
- ordering may be lost,
- a sort can still be needed,
- a dedicated composite index may be cheaper for a hot query.

## Key columns versus payload columns

Suppose the query filters/orders by:

~~~text
customer_id
order_date
~~~

and returns:

~~~text
total_cents
status
~~~

Do not automatically add every returned field as a search key.

In PostgreSQL, INCLUDE can store payload columns without making them part of the navigation key.

See the next note.

## Unique composite index

~~~sql
CREATE UNIQUE INDEX ux_tenant_email
ON users(tenant_id, email);
~~~

This means:

~~~text
email is unique within each tenant
~~~

not globally.

The whole tuple defines uniqueness, while column order still affects access patterns.

## Tenant-first indexes

For multi-tenant schemas:

~~~text
tenant_id
entity_id
created_at
~~~

tenant-first ordering can improve:

- scoped access,
- locality,
- per-tenant ranges,
- safer query patterns.

This can matter more than global selectivity.

## Search plus sort

Query:

~~~sql
SELECT id, title
FROM posts
WHERE author_id = ?
  AND published = true
ORDER BY published_at DESC
LIMIT 50;
~~~

Candidate:

~~~text
(author_id, published, published_at DESC)
~~~

Reasoning:

1. author equality,
2. published equality,
3. desired order.

A partial index may remove published from the key entirely:

~~~sql
CREATE INDEX idx_published_posts_author_date
ON posts(author_id, published_at DESC)
WHERE published = true;
~~~

## Join keys

Join:

~~~sql
ON order_items.order_id = orders.order_id
~~~

An index beginning with order_items.order_id can make repeated join lookups cheaper.

Trailing columns can support additional filter/order requirements.

## Low-cardinality leading column

Index:

~~~text
(is_deleted, customer_id)
~~~

may be inefficient if is_deleted=false for almost all rows.

A partial index can be smaller:

~~~sql
CREATE INDEX idx_live_customers
ON customers(customer_id)
WHERE deleted_at IS NULL;
~~~

## Parameter skew

One composite index can work very differently for:

- a tiny tenant,
- the largest tenant,
- a common status,
- a rare status.

Test representative and worst-case parameters.

## Runnable demonstration

This chapter adds:

~~~text
scripts/indexing/sqlite_composite_index_demo.py
~~~

Run:

~~~bash
python scripts/indexing/sqlite_composite_index_demo.py
~~~

The demo shows plans for:

- customer + status + date,
- customer-only,
- status-only,

against one composite index.

The purpose is to make stored column order visible in the query plans.

## Design workflow

1. Write the exact WHERE predicates.
2. Mark equality predicates.
3. Mark range predicates.
4. Write required ORDER BY.
5. Identify join keys.
6. Identify tenant/locality boundaries.
7. Decide whether a partial predicate can shrink the index.
8. Separate search keys from returned payload.
9. Compare with existing indexes.
10. Validate on representative data.
11. Measure write/storage cost.

## Common mistakes

- Putting every WHERE column into one index without considering order.
- Treating "most selective first" as a universal law.
- Assuming a suffix-only predicate gets an efficient direct seek.
- Ignoring ORDER BY when choosing index order.
- Creating a new composite index for every query variant.

## Related notes

- [Database indexing](05_indexing.md)
- [B-tree internals](06_btree_internals_and_page_splits.md)
- [Covering, partial, and expression indexes](08_covering_partial_and_expression_indexes.md)
- [Execution plans and cardinality](../08_database_performance/07_execution_plans_statistics_and_cardinality.md)
