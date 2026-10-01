# Pagination, Large Result Sets, and Data Transfer

A query is not finished when the database finds matching rows. The system still has to order them, transfer them, allocate client memory, deserialize them, and render/process them.

Returning less data is often the highest-value optimization.

## LIMIT without stable ordering

This is not stable pagination:

~~~sql
SELECT *
FROM orders
LIMIT 20;
~~~

Without ORDER BY, the database does not promise a durable presentation order.

## Offset pagination

Common API:

~~~sql
SELECT order_id, order_date
FROM orders
WHERE customer_id = $1
ORDER BY order_date DESC, order_id DESC
LIMIT 20 OFFSET 20000;
~~~

Simple and convenient, but the database may still have to walk past many earlier rows.

~~~text
read or skip 20,000
return next 20
~~~

Deep pages can become increasingly expensive.

## Keyset pagination

Remember the last row from the previous page.

Suppose the ordering is:

~~~text
order_date DESC, order_id DESC
~~~

Cursor:

~~~text
last_order_date, last_order_id
~~~

Next page:

~~~sql
SELECT order_id, order_date
FROM orders
WHERE customer_id = $1
  AND (
    order_date < $2
    OR (order_date = $2 AND order_id < $3)
  )
ORDER BY order_date DESC, order_id DESC
LIMIT 20;
~~~

With a suitable index, the engine can continue from a known position rather than skip a large prefix.

## Row-value comparison

PostgreSQL can express the same continuation compactly:

~~~sql
WHERE (order_date, order_id) < ($2, $3)
~~~

paired with the matching descending ORDER BY.

Check null and ordering semantics for the exact engine.

## Stable tie-breaker

Ordering only by a non-unique timestamp can create ambiguous page boundaries.

Prefer:

~~~text
ORDER BY created_at DESC, id DESC
~~~

The cursor must represent the complete ordering.

## Runnable SQLite demo

The repository adds:

scripts/performance/sqlite_pagination_demo.py

Run:

~~~bash
python scripts/performance/sqlite_pagination_demo.py
~~~

The script builds a synthetic indexed event table and compares a deep OFFSET query with keyset continuation.

Timings vary by machine; the query shape and work avoided are the main lesson.

## Cursor encoding

An API can represent a cursor logically as:

~~~json
{
  "created_at": "2026-10-01T12:30:00Z",
  "id": 918273
}
~~~

and encode it into an opaque token.

Clients do not need to understand the database key format.

## Cursor validation

A decoded cursor should contain only expected typed fields.

Do not let cursor contents become arbitrary SQL fragments.

If cursors expose sensitive internal identifiers, use an opaque server-side token or integrity protection.

## Inserts during pagination

With offset pagination:

~~~text
page 1 read
new rows inserted at front
page 2 uses OFFSET 20
~~~

rows can move relative to the offset, causing duplicates or skips.

Keyset pagination is usually more stable because it continues from a last-seen ordering key.

## Deletes during pagination

Deletes also shift offsets.

Keyset continuation is less sensitive because it uses values rather than absolute positions.

Exact behavior still depends on isolation/snapshot semantics.

## Snapshot-consistent exports

An export may require one consistent dataset while rows keep changing.

Possible patterns include:

- a database snapshot/transaction,
- exported snapshot feature,
- materialized staging table,
- warehouse snapshot.

Keeping an online transaction open for hours can hurt cleanup and concurrency. Use an engine-appropriate export design.

## COUNT(*) on every page

A UI may request:

~~~text
Page 1 of 4,891,203
~~~

Exact counts for huge changing filters can be expensive.

Alternatives:

- omit exact count,
- approximate count,
- asynchronous count,
- cached count,
- "more results" indicator.

Do not make an exact count the slowest query merely because a UI widget expects one.

## Count plus page is two workloads

Common pattern:

~~~text
SELECT COUNT(*)
SELECT page rows
~~~

Measure them separately.

The count can cost more than the page query.

## Projection

Avoid SELECT * for list pages.

A product listing may need only:

~~~text
id
title
price
thumbnail_url
~~~

not large descriptions, JSON blobs, or audit fields.

Projection reduces storage work, network bytes, and application allocations.

## Large text and blob columns

If each row includes megabytes of content, transfer cost dominates even when lookup is fast.

For file-like objects, object storage may be a better delivery path than ordinary list queries.

## Fetch size

Drivers can fetch rows incrementally:

~~~text
query result
   |
   +--> fetch 1,000
   +--> fetch 1,000
   +--> ...
~~~

This controls client memory but does not reduce total database work.

## Streaming exports

For large exports:

- stream rows,
- write incrementally,
- use database bulk/export APIs,
- avoid building one huge in-memory list.

Also provide cancellation and resource limits.

## API page-size limits

Protect the database from requests such as:

~~~text
?page_size=10000000
~~~

Use a sensible default and maximum based on payload size and use case.

## Search-after style pagination

Search engines often expose a search-after cursor based on sort values.

This is conceptually keyset pagination over an ordered search index.

The same rules apply:

- stable complete sort,
- deterministic tie-breaker,
- opaque cursor.

## Partition-aware pagination

Global ordering across partitions can require merging many inputs.

If the product can paginate naturally within a scope such as tenant, month, or customer, queries can be cheaper.

Pagination and data partitioning should be designed together.

## Time-window APIs

For event history, time windows can be clearer than page numbers:

~~~text
from=2026-10-01
to=2026-10-02
limit=1000
~~~

Return a continuation cursor for the next chunk.

## Large IN lists

For very large ID lists, consider:

- temporary tables,
- arrays/table-valued parameters,
- staging tables,
- chunking.

Huge SQL text increases parse and protocol cost.

## Sorting large results

ORDER BY over millions of rows may require a large memory sort or disk spill.

If the user needs only 20 rows, design an index that supports filter plus order so the engine can stop early.

## Top-N access

A query such as:

~~~sql
ORDER BY score DESC
LIMIT 20
~~~

can be cheap with a matching index or ordered data structure.

Without one, the engine may inspect and sort a large input.

## Pagination index

Example:

~~~sql
CREATE INDEX idx_orders_customer_date_id
ON orders(customer_id, order_date DESC, order_id DESC);
~~~

This can support:

- customer filter,
- stable ordering,
- keyset cursor.

Always verify with the execution plan.

## ORM pagination

ORM APIs often make offset/limit easy.

Convenience can hide deep-offset cost.

For feeds and very large tables, implement cursor/keyset pagination deliberately.

## Common mistakes

- Deep OFFSET for an infinite feed.
- ORDER BY on a non-unique key only.
- SELECT * on list endpoints.
- Exact COUNT(*) on every page without need.
- Fetch all rows then slice in application code.
- Unlimited page-size parameters.
- Returning large blob fields with every list row.

## Pagination checklist

1. Is the order deterministic?
2. Is there a unique tie-breaker?
3. How deep can users navigate?
4. Would keyset pagination fit?
5. Is exact total count required?
6. Does the index support filter and order?
7. Are only needed columns returned?
8. Is page size bounded?
9. Are large payload fields excluded?
10. What happens when rows change between pages?
11. Does export need snapshot consistency?
12. Can the client resume/cancel safely?

## Related notes

- [Query optimization](01_query_optimization_techniques.md)
- [Indexing strategies](02_indexing_strategies.md)
- [Connection pooling and batching](08_connection_pooling_batching_and_n_plus_one.md)
- [Working with billion-row tables](06_working_with_billion_row_table.md)
