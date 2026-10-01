# B-Tree Index Internals and Page Splits

B-tree-family indexes are the default general-purpose index in many relational databases because they support ordered search efficiently.

They are useful for equality lookups, range predicates, ordered traversal, and top-N access paths. The important idea is not merely "lookup is logarithmic." A real B-tree is a set of storage pages that must stay balanced while rows are inserted, updated, and deleted.

## Tree shape

A simplified B-tree:

~~~text
                    root
              /       |       \
             /        |        \
        internal   internal   internal
          /  \       /  \       /  \
       leaf leaf  leaf leaf   leaf leaf
~~~

Internal pages guide navigation. Leaf pages contain index entries in key order.

## Why trees stay shallow

If one internal page can point to hundreds of child pages, even a very large index can have only a few levels.

Fan-out depends on:

- page size,
- key width,
- tuple/pointer overhead,
- engine implementation.

Narrow keys generally fit more entries per page.

## Leaf entries and row locators

For an index on customer_id:

~~~sql
CREATE INDEX idx_orders_customer
ON orders(customer_id);
~~~

leaf entries conceptually look like:

~~~text
customer_id -> row locator
~~~

The locator differs by engine.

- PostgreSQL secondary indexes point to heap tuples.
- InnoDB secondary indexes include the clustered primary-key value.
- SQLite rowid-table secondary indexes use rowid to identify the row.

That physical difference affects index size and lookup cost.

## Equality lookup

Query:

~~~sql
SELECT *
FROM orders
WHERE customer_id = 42;
~~~

Navigation:

~~~text
root
  |
internal page
  |
leaf containing 42
  |
matching entries
  |
table rows if required
~~~

Finding the first matching leaf can be cheap while returning many matching rows is still expensive.

## Range scan

Query:

~~~sql
WHERE order_date >= '2026-10-01'
  AND order_date <  '2026-11-01'
~~~

The B-tree can seek to the first October entry and then walk leaf entries in order until November begins.

~~~text
seek
 |
 v
Oct 1 -> Oct 2 -> ... -> Oct 31
                         |
                         stop
~~~

## ORDER BY and LIMIT

Candidate index:

~~~sql
CREATE INDEX idx_orders_customer_date
ON orders(customer_id, order_date DESC);
~~~

Query:

~~~sql
SELECT order_id, order_date
FROM orders
WHERE customer_id = 42
ORDER BY order_date DESC
LIMIT 20;
~~~

The engine may seek to customer 42 and return the first 20 entries without sorting a much larger result.

Always verify with the execution plan.

## Inserting into a leaf

If a page has free space:

~~~text
[10, 20, 30, free, free]
~~~

inserting 25 can produce:

~~~text
[10, 20, 25, 30, free]
~~~

No structural change is needed.

## Page split

If a leaf is full:

~~~text
[10, 20, 30, 40, 50]
~~~

and 35 must be inserted, the engine may split the page:

~~~text
before:
[10, 20, 30, 40, 50]

after:
[10, 20, 30]  [35, 40, 50]
       \        /
       parent updated
~~~

A split can require:

- another page,
- entry redistribution,
- parent updates,
- recovery/log writes.

Splits are normal B-tree maintenance.

## Root split

If the root fills, the tree can gain another level:

~~~text
old root
   |
split
   |
new root
 /     \
old A  old B
~~~

This keeps the tree balanced.

## Sequential keys

An increasing identity or timestamp often inserts near the right edge.

Possible advantages:

- predictable locality,
- fewer random insertion targets.

Possible costs:

- a hot rightmost page under high concurrency,
- a hot range in some distributed range-sharded systems.

The architecture matters.

## Random keys

Random keys spread insert targets across more leaf pages.

Possible effects:

- more cache churn,
- more random page access,
- different split behavior.

But random distribution can be useful in some distributed systems.

There is no universal "sequential good, random bad" rule.

## Fill factor

Some engines can intentionally leave free space in pages.

~~~text
packed:
[10 20 30 40 50]

with headroom:
[10 20 30 40 __]
~~~

The extra space can reduce immediate splits for update/insert-heavy workloads.

Trade-off:

- larger index,
- more pages to cache/read.

Tune only from measured behavior.

## Key width matters

Compare a narrow integer key with a long text or wide composite key.

Wider entries mean fewer entries per page.

That can increase:

- index size,
- tree height,
- cache pressure,
- write amplification.

This matters especially in engines where secondary indexes also carry the clustered primary key.

## Duplicate keys

A non-unique index can contain many entries for the same value.

Example:

~~~text
status = 'active'
~~~

for nearly every row.

Finding the first entry is cheap. Reading almost the whole table is not.

Low selectivity can make a table scan cheaper.

## Engine-specific compression/deduplication

Database engines can reduce repeated index-key storage with techniques such as prefix compression or deduplication.

The conceptual B-tree model is useful, but physical entries are not necessarily naive full copies of every key.

## Deletes and updates

Deletes may leave reusable space without immediately shrinking the index file.

If an indexed key changes:

~~~text
old key -> remove/invalidate old entry
new key -> insert new entry
~~~

Updating indexed columns therefore has write cost.

## B-tree is not a binary search tree

A binary tree has two children per node.

A database B-tree page can have many children.

~~~text
binary tree:
2 children

B-tree:
many child pointers per storage page
~~~

High fan-out reduces the number of page accesses.

## B+ tree terminology

Many database implementations are technically B+ tree variants:

- internal pages primarily guide navigation,
- leaf pages carry row references/data,
- leaves support ordered traversal.

Documentation often uses B-tree as the family name.

## Buffer-cache interaction

Upper levels are small and frequently accessed, so they are often cached.

A real lookup can therefore spend most of its I/O on leaf and table pages rather than repeatedly reading the root.

## Clustered versus secondary B-tree

Clustered/index-organized:

~~~text
B-tree leaf
   |
   +--> row data
~~~

Heap plus secondary index:

~~~text
B-tree leaf
   |
   +--> row locator
          |
          v
       table/heap page
~~~

The second layout can require an additional page lookup.

## A split is not automatically "fragmentation"

Page splitting preserves order and balance.

Frequent splits may increase write work or reduce page density, but observing splits alone is not a reason to rebuild an index.

Measure:

- workload latency,
- page density/bloat,
- index size,
- write rate,
- engine diagnostics.

## Runnable exercise

This chapter adds:

~~~text
scripts/indexing/sqlite_btree_growth_demo.py
~~~

Run:

~~~bash
python scripts/indexing/sqlite_btree_growth_demo.py
~~~

It compares indexes built from narrow integer keys and wider text keys, then reports local database page counts and sizes.

The exercise demonstrates storage consequences of entry width; it is not a universal benchmark.

## Design checklist

1. Which equality/range/order operations must the index support?
2. How wide is the key?
3. How many duplicates exist?
4. Is the table write-heavy?
5. Are inserts mostly monotonic or random?
6. Does the engine copy the primary key into secondary indexes?
7. Are covering payloads making leaf entries too wide?
8. Are page/cache effects measured?

## Common mistakes

- Assuming logarithmic lookup means the complete query is always cheap.
- Treating random keys as universally bad.
- Treating sequential keys as universally best.
- Treating a page split as index corruption.
- Rebuilding indexes merely because splits occur.

## Related notes

- [Database pages](04_database_pages.md)
- [Database indexing](05_indexing.md)
- [Composite indexes and column order](07_composite_indexes_and_column_order.md)
- [Clustered indexes and heap tables](09_clustered_indexes_heap_tables_and_row_locality.md)
- [Index maintenance and bloat](11_index_maintenance_bloat_and_online_operations.md)
