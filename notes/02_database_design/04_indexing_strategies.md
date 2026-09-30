# Indexing Strategies: Design for a Specific Query

An **index** is an additional structure that helps the database find selected rows. It is comparable to a book's index: look up a topic, find its location, and then read the relevant pages. The database still has to retrieve and return the answer.

Assume you know tables and basic `SELECT` queries. The [SQL introduction](../03_sql/01_intro_to_sql.md) provides that starting point.

## Begin with the question the application asks

A customer opens an order-history page. The query looks for that customer's recent orders:

```sql
SELECT order_id, order_date
FROM orders
WHERE customer_id = 1
ORDER BY order_date, order_id;
```

Without a suitable index, the engine may examine the orders table to find matching rows. With millions of orders and only a few belonging to this customer, avoiding that work can matter. With three rows, a scan may be simpler and faster.

The **optimizer** is the part of the DBMS that chooses an execution strategy. Declaring an index makes another strategy possible; it does not force the engine to use it.

## Start with one useful index

For customer lookup:

```sql
CREATE INDEX idx_orders_customer ON orders (customer_id);
```

The index organizes entries by customer ID and lets the engine locate that customer's orders. It may still need to sort the matching rows by date.

For customer lookup with the requested order, consider:

```sql
CREATE INDEX idx_orders_customer_date
ON orders (customer_id, order_date, order_id);
```

This is a **composite index**: one index containing several columns, ordered by customer first, date within that customer, and order ID within that date. Choose this alternative when it fits the workload; do not keep both examples automatically.

## Column order changes the access path

Imagine an address book sorted first by country and then by surname. It is easy to find Smiths within one country, but all Smiths across countries are scattered.

Similarly, `(customer_id, order_date)` and `(order_date, customer_id)` are different indexes. The first fits one customer's date range; the second may fit all orders in a date range. Engine-specific optimizations can help with other patterns, but the order is still a design decision.

## Match the amount of data requested

A query returning one email match may benefit greatly from an index. A query returning almost every customer may benefit little: it still needs to retrieve almost every row.

**Selectivity** describes how much a condition narrows the data. Look at how many rows the actual predicate matches rather than assuming a column is useful because it has an index. A boolean status may still be valuable in a partial index for a rare status.

## Other index choices, after the basics

| Choice | What it does | Question to ask |
| --- | --- | --- |
| Unique index or constraint | Prevents duplicate key values. | Is uniqueness a business rule or only a search need? |
| Covering index | Contains the values needed by a particular query. | Does avoiding extra table access justify the larger index? |
| Partial or filtered index | Indexes a subset of rows when supported. | Can the engine establish that the query needs only that subset? |
| Expression index | Indexes a calculation such as a lowercased email. | Does the query use the corresponding expression? |

These are engine-dependent options. The basic point is to match the access path to the repeated query, not to accumulate every available index type.

## Every extra index has a write cost

When an order is inserted, the database may need to insert its index entries too. Updating an indexed customer or date can require index maintenance. More indexes use more storage and memory and can increase write work.

A primary or unique constraint may already have a supporting index. Check the existing definitions before adding another identical one. A foreign-key declaration does not universally create an index on the referencing columns.

## Verify with a plan and a representative workload

An **execution plan** shows how a query will or did access data. Use the chosen engine's plan tools to check rows examined, sorting, estimates, and elapsed time. Some analysis commands execute the query, so understand the tool before applying it to a write.

Compare the read improvement with insertion and update costs. Test customers with a few orders and customers with many; one convenient test value can hide a different workload.

## Read a B-tree lookup as a sequence of choices

SQLite and PostgreSQL support ordered B-tree-family indexes. A simplified index on customer and date keeps keys ordered by customer first, then date. The engine follows upper-level entries toward a relevant leaf range rather than examining every table row.

```text
(customer_id, order_date)
(1, 2025-01-10)
(1, 2025-01-12)
(2, 2025-01-12)
```

The prefix `customer_id = 1` selects one ordered region. A date range narrows it further. With only a date filter, the relevant entries can be scattered across customers, so the same index may be less useful. Engines sometimes support other routes such as skip scans; “leftmost prefix” is a useful design starting point, not a claim that every non-prefix query must ignore the index.

A **leaf** is the tree level containing indexed entries. Depending on the engine, an entry identifies another table location or carries clustered row data. Matching entries may still require additional reads to obtain requested columns.

## Implement a covering and a partial index

Use the fresh [SQLite bookstore](../03_sql/01_intro_to_sql.md). This index contains the filter and the columns returned by an order-history query:

```sql
CREATE INDEX idx_design_customer_history
ON orders(customer_id, order_date, order_id);
EXPLAIN QUERY PLAN
SELECT order_id, order_date
FROM orders
WHERE customer_id = 1
ORDER BY order_date, order_id;
```

SQLite can report a covering-index search because it can obtain the required values from the index. PostgreSQL's index-only scans have additional visibility requirements; containing the columns alone does not guarantee zero heap visits. The source of the result remains the table's logical data, not a new authoritative customer history.

If the application primarily needs open orders, a partial index can omit completed and cancelled orders:

```sql
CREATE INDEX idx_design_open_orders
ON orders(customer_id, order_date)
WHERE status = 'open';

SELECT order_id, order_date
FROM orders
WHERE customer_id = 1 AND status = 'open'
ORDER BY order_date, order_id;
```

The result is order 102 on January 12. The partial index saves entries by indexing a subset, but the planner must establish that the query fits that predicate. A query parameter that could mean any status may not provide the same proof. See [SQLite partial indexes](https://www.sqlite.org/partialindex.html).

## Use a hash index for equality, not range ordering

PostgreSQL offers hash indexes in addition to its default B-tree. This standalone PostgreSQL example demonstrates the syntax:

```sql
-- PostgreSQL
CREATE TABLE index_login_accounts (
    account_id INTEGER PRIMARY KEY,
    email TEXT NOT NULL
);
INSERT INTO index_login_accounts VALUES (1, 'alice@example.com');
CREATE INDEX idx_login_email_hash ON index_login_accounts USING hash(email);
SELECT account_id FROM index_login_accounts WHERE email = 'alice@example.com';
```

The result is account 1. A hash maps the search value to a bucket and can support equality. It does not provide the same ordered traversal for prefix ranges or sorting as a B-tree. PostgreSQL hash indexes also do not replace a unique constraint for enforcing distinct emails. The [PostgreSQL index-types guide](https://www.postgresql.org/docs/current/indexes-types.html) describes supported operations.

For a login table requiring unique email, the B-tree-backed uniqueness rule may already supply the needed lookup. Adding a hash copy without a demonstrated benefit would add maintenance rather than solve a missing access path.

## Bitmap indexes and bitmap scans are different mechanisms

A bitmap represents a set of matching row positions as bits. Combining bitmaps can efficiently identify rows satisfying several conditions. Oracle Database provides stored bitmap indexes that can suit read-heavy reporting with suitable low-cardinality dimensions. Frequent updates and concurrent transactional changes can make that design inappropriate.

PostgreSQL can construct a bitmap during execution from ordinary index results. A **bitmap heap scan** is a query-plan operation, not evidence that an Oracle-style persistent bitmap index was created. Read the engine's actual mechanism before choosing an index from a generic list.

## Full-text search indexes language tokens

`LIKE '%database%'` and searching natural-language text are different operations. A full-text index stores searchable tokens and can support token matching, ranking, or language-specific processing according to the engine.

SQLite's FTS5 extension provides an executable example when the installed build includes it:

```sql
CREATE VIRTUAL TABLE design_book_search USING fts5(title, description);
INSERT INTO design_book_search VALUES
    ('Database Basics', 'An introduction to relational database design'),
    ('SQL Practice', 'Exercises about queries joins and transactions');

SELECT title
FROM design_book_search
WHERE design_book_search MATCH 'transactions';
```

The result is `SQL Practice`. This creates a virtual full-text table, not a normal B-tree over the original products table. Keeping it synchronized with the catalog requires an explicit maintenance design; FTS5 also supports external-content arrangements with their own rules. See [SQLite FTS5](https://www.sqlite.org/fts5.html).

PostgreSQL uses text-search values and commonly a GIN index for this role. A plain text B-tree does not become a language-search index just because it is placed on a description column.

## Spatial indexes narrow candidate regions

For pickup locations, a spatial access structure can discard regions that cannot match a geometric request. SQLite's R-tree extension indexes bounding boxes. This separate example uses an illustrative planar coordinate system, not latitude/longitude distances:

```sql
CREATE VIRTUAL TABLE design_pickup_regions USING rtree(
    region_id, min_x, max_x, min_y, max_y
);
INSERT INTO design_pickup_regions VALUES
    (1, 0, 10, 0, 10),
    (2, 20, 30, 20, 30);

SELECT region_id
FROM design_pickup_regions
WHERE min_x <= 5 AND max_x >= 5
  AND min_y <= 5 AND max_y >= 5
ORDER BY region_id;
```

Region 1 contains the point `(5, 5)`. Bounding-box matching is not the same as proving an exact relationship for an arbitrary polygon. GIS engines can use the index to find candidates, then perform an exact test. Coordinate systems and units matter for distance queries. See [SQLite R-tree](https://www.sqlite.org/rtree.html).

## Measure and maintain the access paths

Capture plans, elapsed-time distributions, row counts, and I/O under representative data and concurrent load. Separate a cold-cache run from a warm one. A high count of repeated customer IDs does not automatically make indexing useless: an individual customer might still account for only a small fraction of orders.

An index can help reads while slowing writes to the indexed columns. Large text keys consume more storage than compact identifiers. Additional indexes can also increase backup size, cache pressure, and migration time. Compare the full workload rather than only the fastest demonstrated read.

Review overlapping indexes by actual use. An index on `(customer_id, order_date)` may cover some purposes of an index on customer alone, but different widths, uniqueness, predicates, and engine access paths can justify keeping both. Do not delete one based on column-prefix similarity alone.

Statistics maintenance helps planning; rebuild or reorganization is a separate operation. SQL Server, PostgreSQL, and SQLite expose different maintenance tools, costs, and locking behavior. Routine rebuilding of every index is not a universal requirement. Investigate measured bloat, fragmentation, or plan problems, then choose the engine-supported remedy.

## Check your understanding

1. Why might a scan be reasonable for the three-row introductory example?
2. How is an index on `(customer_id, order_date)` different from the reverse order?
3. Why would an index help one email lookup more than a query returning every customer?
4. What work does an extra index add to an order insert?

[Database Indexing](../05_storage_and_indexing/05_indexing.md) explains the storage structures and engine-specific maintenance. Continue with [data integrity](05_data_integrity.md) to separate finding data quickly from enforcing its rules.
