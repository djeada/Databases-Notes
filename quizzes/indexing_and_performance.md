# Indexing and Query Performance Quiz

Notes: [Storage on Disk](../notes/05_storage_and_indexing/01_how_tables_and_indexes_are_stored_on_disk.md), [Row vs Column Storage](../notes/05_storage_and_indexing/02_row_based_vs_column_based_databases.md), [Indexing Overview](../notes/05_storage_and_indexing/05_indexing.md), [B-Tree Internals](../notes/05_storage_and_indexing/06_btree_internals_and_page_splits.md), [Composite Indexes](../notes/05_storage_and_indexing/07_composite_indexes_and_column_order.md), [Covering, Partial and Expression Indexes](../notes/05_storage_and_indexing/08_covering_partial_and_expression_indexes.md), [Clustered Indexes and Heaps](../notes/05_storage_and_indexing/09_clustered_indexes_heap_tables_and_row_locality.md), [Specialized Index Structures](../notes/05_storage_and_indexing/10_specialized_index_structures.md), [Index Maintenance](../notes/05_storage_and_indexing/11_index_maintenance_bloat_and_online_operations.md), [Query Optimization](../notes/08_database_performance/01_query_optimization_techniques.md), [Caching](../notes/08_database_performance/03_database_caching.md), [Materialized Views](../notes/08_database_performance/04_materialized_views.md), [Execution Plans](../notes/08_database_performance/07_execution_plans_statistics_and_cardinality.md), [Connection Pooling and N+1](../notes/08_database_performance/08_connection_pooling_batching_and_n_plus_one.md), [Pagination](../notes/08_database_performance/09_pagination_and_large_result_sets.md), [Partitioning for Performance](../notes/08_database_performance/10_partitioning_sharding_and_data_locality.md), [Write Performance and Vacuum](../notes/08_database_performance/12_write_performance_vacuum_and_bloat.md)

Choose indexes, read plans and reason about read and write costs. Syntax is PostgreSQL unless a question names another engine.

#### Q. A B-tree index exists on `orders(customer_id, status, order_date)`. Which filter can it serve least directly with a normal index seek?

* [ ] `WHERE customer_id = 42`
* [ ] `WHERE customer_id = 42 AND status = 'open'`
* [x] `WHERE status = 'open'`
* [ ] `WHERE customer_id = 42 AND status = 'open' AND order_date >= '2026-10-01'`

> **Explanation:** A composite B-tree is ordered by its leading column first. Without a `customer_id` condition, open rows are spread across every customer group, so there is no single prefix to seek to.

#### Q. Which index best supports this query?

```sql
SELECT order_id, order_date
FROM orders
WHERE customer_id = 42 AND order_date >= '2026-10-01'
ORDER BY order_date;
```

* [x] `(customer_id, order_date)`
* [ ] `(order_date, customer_id)`
* [ ] `(order_date)` alone
* [ ] `(order_id, customer_id)`

> **Explanation:** Equality on the leading column puts all of customer 42's entries together, and the second column then gives the range and the sort order. Leading with the date would interleave every customer in the range.

#### Q. A query filters `tenant_id = ?`, `status = ?` and `created_at >= ?`, and orders by `created_at`. Which column order is the natural starting candidate?

* [ ] `(created_at, tenant_id, status)`
* [x] `(tenant_id, status, created_at)`
* [ ] `(status, created_at, tenant_id)`
* [ ] `(created_at, status, tenant_id)`

> **Explanation:** Equality columns form the prefix, and the range column comes last so the engine can walk it in order. This is a heuristic to verify with plans, not a universal formula.

#### Q. What does `INCLUDE (total_cents)` change in this PostgreSQL index?

```sql
CREATE INDEX idx_orders_customer_date
ON orders(customer_id, order_date DESC)
INCLUDE (total_cents);
```

* [ ] `total_cents` becomes a third sort key
* [x] `total_cents` is stored as payload for covering reads
* [ ] The index now enforces uniqueness on `total_cents`
* [ ] Rows with a null `total_cents` are excluded

> **Explanation:** Included columns are non-key payload, so they affect neither search order nor uniqueness. They let a query that also returns `total_cents` be answered from the index.

#### Q. A PostgreSQL index covers every column a query needs, yet the plan still shows heap fetches. Why?

* [ ] Covering indexes are ignored when sorting
* [x] Pages not marked all-visible need heap checks
* [ ] PostgreSQL always reads the heap for every row
* [ ] The index was built without `CONCURRENTLY`

> **Explanation:** PostgreSQL indexes do not store full row-visibility state. The visibility map lets an index-only scan skip the heap only for all-visible pages, so frequently updated tables benefit less.

#### Q. Which query can use the partial index `ON orders(customer_id, order_date DESC) WHERE status = 'open'`?

* [ ] `WHERE customer_id = 42`
* [x] `WHERE customer_id = 42 AND status = 'open'`
* [ ] `WHERE customer_id = 42 AND status = 'closed'`
* [ ] `WHERE status IN ('open', 'closed')`

> **Explanation:** The index contains only open orders, so the planner must prove the query's condition implies `status = 'open'`. A query for all or closed orders needs rows the index omits.

#### Q. `created_at` has a B-tree index. Which predicate selects October 1, 2026 in a form that can use a normal range scan?

* [ ] `WHERE DATE(created_at) = DATE '2026-10-01'`
* [x] `WHERE created_at >= '2026-10-01' AND created_at < '2026-10-02'`
* [ ] `WHERE CAST(created_at AS TEXT) LIKE '2026-10-01%'`
* [ ] `WHERE EXTRACT(DAY FROM created_at) = 1 AND EXTRACT(MONTH FROM created_at) = 10`

> **Explanation:** Wrapping the indexed column in a function hides its ordering unless a matching expression index exists. A half-open range on the raw column stays sargable.

#### Q. Logins look up users with `WHERE lower(email) = lower($1)`. Which index matches that predicate?

* [ ] `CREATE INDEX ON users (email);`
* [x] `CREATE INDEX ON users (lower(email));`
* [ ] `CREATE INDEX ON users USING hash (email);`
* [ ] `CREATE INDEX ON users (email) WHERE email IS NOT NULL;`

> **Explanation:** An expression index stores the computed value, so the planner can match an identical expression in the query. A plain index on `email` orders the raw values, not their lowercase forms.

#### Q. Which predicate is a PostgreSQL hash index unable to accelerate?

* [ ] `session_token = $1`
* [x] `created_at BETWEEN $1 AND $2`
* [ ] `api_key = 'abc-123-xyz-456'`
* [ ] `email = 'a@example.com'`

> **Explanation:** Hashing maps keys to buckets and does not preserve order, so it suits equality only. A B-tree handles both equality and ranges and is usually the more versatile choice.

#### Q. A huge append-only events table is written in time order, and queries scan narrow time windows. Which PostgreSQL index type can be much smaller than a B-tree here?

* [ ] GIN
* [ ] Hash
* [x] BRIN
* [ ] GiST

> **Explanation:** BRIN summarizes ranges of table pages, which works well when the value correlates with physical row order. GIN suits containment and full-text search; hash suits equality.

#### Q. Which PostgreSQL index type fits `WHERE tags @> ARRAY['postgres']` on an array column?

* [ ] BRIN
* [x] GIN
* [ ] Hash
* [ ] A B-tree on `tags`

> **Explanation:** GIN is an inverted index that maps elements to the rows containing them, which fits array and document containment. Ordering-based B-trees cannot answer "contains this element" directly.

#### Q. Why does a B-tree on `body` not help `WHERE body LIKE '%database%'`?

* [ ] B-trees cannot store text columns
* [x] A leading wildcard gives no prefix to seek to
* [ ] `LIKE` is always executed as a full sort
* [ ] The pattern is case-insensitive by default

> **Explanation:** B-tree ordering helps only when the beginning of the value is known. Use full-text search, a trigram index such as `pg_trgm`, or a search engine for substring and word queries.

#### Q. In MySQL InnoDB, why does a wide primary key such as a long string make secondary indexes larger?

* [ ] InnoDB copies the whole row into each secondary index
* [x] Each secondary index entry stores the primary-key value
* [ ] Secondary indexes must include every key column twice
* [ ] Wide keys disable index compression

> **Explanation:** InnoDB clusters rows by primary key, and secondary entries locate rows by carrying that key value rather than a heap address. PostgreSQL secondary indexes instead point to heap tuples.

#### Q. You run PostgreSQL `CLUSTER orders USING idx_orders_date;`. What happens to rows inserted afterwards?

* [ ] They are always placed in index order
* [x] They are not kept in that order automatically
* [ ] They are rejected until `CLUSTER` runs again
* [ ] They are routed to a separate clustered table

> **Explanation:** PostgreSQL's `CLUSTER` is a one-time physical reorder of a heap table. In SQL Server and InnoDB, "clustered" instead means a persistent storage organization that is maintained.

#### Q. 98% of rows have `status = 'active'`. The plan for `WHERE status = 'active'` uses a sequential scan. What is the most likely reading?

* [ ] The index is corrupt and needs `REINDEX`
* [x] Scanning beats random lookups for most rows
* [ ] The optimizer ignores indexes on text columns
* [ ] Statistics must be stale since a scan was chosen

> **Explanation:** A predicate that matches most rows is not selective. Visiting nearly every row through an index adds random I/O, so a scan is often the correct plan.

#### Q. `EXPLAIN ANALYZE` shows an estimate of 10 rows but an actual count of 2,000,000 after a large backfill. What should you check first?

* [ ] Whether the connection pool is large enough
* [x] Whether statistics are stale (run `ANALYZE`)
* [ ] Whether the query selects every column
* [ ] Whether `fsync` is enabled on the server

> **Explanation:** Row estimates come from statistics, and a bulk change can leave them describing the old table. Bad estimates drive poor join orders and access paths.

#### Q. The optimizer badly underestimates `WHERE country = 'DE' AND currency = 'EUR'`. What is the likely cause?

* [ ] The two columns lack a combined index
* [x] It treats correlated predicates as independent
* [ ] Text comparisons are always estimated at one row
* [ ] The query is missing a `LIMIT` clause

> **Explanation:** Multiplying separate selectivities underestimates strongly related columns. Some engines, including PostgreSQL, support extended multicolumn statistics for such cases.

#### Q. When is a nested loop join a good plan?

* [ ] When both inputs are huge and unsorted
* [x] When the outer input is small and the inner lookup is indexed
* [ ] When the join condition is a range on unindexed columns
* [ ] When memory is too small for any sort

> **Explanation:** A nested loop does one inner lookup per outer row, which is cheap for few outer rows with an indexed inner side. It degrades badly when the outer input is unexpectedly large.

#### Q. Which join algorithm builds an in-memory table from one input and probes it with the other, and is common for equality joins?

* [ ] Nested loop join
* [ ] Merge join
* [x] Hash join
* [ ] Cross join

> **Explanation:** A hash join hashes one side and looks up each row of the other side. Memory pressure can make it spill to disk; a merge join instead relies on sorted inputs.

#### Q. An API serves `ORDER BY created_at DESC, id DESC LIMIT 20 OFFSET 20000`. Why do deep pages get slower?

* [ ] `OFFSET` disables all indexes
* [x] The engine still reads and discards the skipped rows
* [ ] Each page reopens a new connection
* [ ] `LIMIT` forces a full table sort on every single call

> **Explanation:** Offset pagination must walk past every earlier row. Keyset pagination resumes from the last row's `(created_at, id)` and, with a matching index, avoids that prefix.

#### Q. Which condition fetches the next keyset page after the row `(created_at = $2, id = $3)` for `ORDER BY created_at DESC, id DESC`?

* [ ] `WHERE created_at < $2 AND id < $3`
* [x] `WHERE created_at < $2 OR (created_at = $2 AND id < $3)`
* [ ] `WHERE created_at <= $2 AND id <> $3`
* [ ] `WHERE created_at <= $2 AND (id <= $3 OR id IS NULL)`

> **Explanation:** The cursor must follow the full ordering: older timestamps, or the same timestamp with a smaller ID. Separate `AND` conditions skip, repeat or re-include rows; in PostgreSQL `(created_at, id) < ($2, $3)` is equivalent.

#### Q. A page loads 100 customers, then runs one orders query per customer in a loop. How many queries does the request issue?

* [ ] 2
* [ ] 100
* [x] 101
* [ ] 200

> **Explanation:** This is the N+1 pattern: one list query plus one per row. Each statement may be fast, but round trips add up; fix it with a join, one `IN` query or eager loading.

#### Q. Ten application instances each use a connection pool of 50. What should you check before raising the pool size to "speed things up"?

* [ ] That each pool uses a different database user
* [x] That the database can serve 500 connections
* [ ] That every query uses a prepared statement
* [ ] That autocommit is disabled in every instance

> **Explanation:** Fleet-wide connections multiply: $10 \times 50 = 500$. Larger pools can add memory use, lock contention and tail latency, so size them from measured database capacity.

#### Q. With cache-aside, a writer commits a new price and deletes the cache key. How can the cache still end up stale?

* [ ] Deleting a key always fails under heavy load
* [x] A slow reader can re-cache the old value
* [ ] Cache-aside never reads from the database
* [ ] The cache refuses keys deleted within the TTL

> **Explanation:** A reader may load the old database value, the writer then commits and invalidates, and the reader finally stores its old value. Versioned values, ordered events or short TTLs reduce this race.

#### Q. What is the main risk of a write-behind cache compared with caching read-only copies?

* [ ] Reads always bypass the cache and hit the database
* [x] Acknowledged writes may be lost before persisting
* [ ] It cannot store values that have a TTL
* [ ] It requires one materialized view per cached key

> **Explanation:** Write-behind accepts a write and persists it later, so a crash can lose, reorder or duplicate acknowledged changes. Two systems do not become one atomic transaction because of a strategy name.

#### Q. What does PostgreSQL require before `REFRESH MATERIALIZED VIEW CONCURRENTLY` can run?

* [ ] The view must have been created `WITH NO DATA`
* [x] A suitable unique index on the materialized view
* [ ] An exclusive lock on every base table
* [ ] A trigger on each source table

> **Explanation:** The concurrent refresh compares old and new results by a unique key so readers can keep querying during the refresh. A plain refresh blocks readers of the view instead.

#### Q. In PostgreSQL, what does an `UPDATE` to a row generally do physically?

* [ ] Overwrites the existing row in place on its page
* [x] Writes a new row version and leaves the old one dead
* [ ] Deletes the row and renumbers the whole table
* [ ] Writes the change only to the WAL, not the table

> **Explanation:** Under MVCC, an update creates a new tuple version. Old versions remain until no transaction needs them, and vacuum then makes their space reusable.

#### Q. A PostgreSQL table had millions of rows deleted and then vacuumed, but its file is about the same size. What does this usually mean?

* [ ] Vacuum failed and must be rerun with `FULL`
* [x] The freed space is reusable inside the table
* [ ] The deleted rows are still visible to queries
* [ ] Autovacuum was disabled for that table

> **Explanation:** Normal vacuum marks dead-tuple space as reusable without returning it to the operating system. Future writes reuse it; shrinking the file needs more disruptive rewrite operations.

#### Q. Dead tuples keep growing even though autovacuum runs regularly. Which application behaviour is a common cause?

* [ ] Using prepared statements for every query
* [x] Sessions left idle in an open transaction
* [ ] Selecting only the columns each page needs
* [ ] Paginating results with keyset cursors

> **Explanation:** A long-running or idle transaction holds an old snapshot, so vacuum cannot remove row versions it might still need. Fix transaction boundaries rather than only tuning vacuum harder.

#### Q. Events are range-partitioned by month and kept for 12 months. What is usually the cheapest way to remove the oldest month?

* [ ] `DELETE FROM events WHERE event_time < ...`
* [x] Detach and drop that month's partition
* [ ] Run `VACUUM FULL` on the parent table
* [ ] `UPDATE` old rows to set `deleted_at`

> **Explanation:** Dropping a partition removes a whole object, avoiding row-by-row deletes, dead tuples and index maintenance. Retention is a major reason to partition by time.

#### Q. A table is partitioned by `event_time`. Which query lets the planner prune unrelated partitions?

* [ ] `WHERE user_id = 42`
* [x] `WHERE event_time >= '2026-10-01' AND event_time < '2026-11-01'`
* [ ] `WHERE event_type = 'login'`
* [ ] `ORDER BY event_time DESC LIMIT 10` with no `WHERE` clause

> **Explanation:** Pruning requires a predicate on the partition key. Filters on other columns must examine every partition, which is why the partition key must match the access patterns.

#### Q. A table has eight indexes. What happens to the cost of each `INSERT`?

* [ ] It stays the same; indexes only affect reads
* [x] It rises, because every index must also be updated
* [ ] It falls, because inserts find free pages faster
* [ ] It rises only for indexes that are unique

> **Explanation:** Each index is another stored structure to maintain on inserts, deletes and updates of indexed columns. Every extra index must earn its write, storage and maintenance cost.

#### Q. Why might you use `CREATE INDEX CONCURRENTLY` on a busy PostgreSQL table?

* [ ] It builds the index faster than a normal build
* [x] It avoids blocking writes during the build
* [ ] It can run inside an explicit transaction block
* [ ] It guarantees that the build cannot fail

> **Explanation:** A concurrent build does more total work and takes longer, but it does not hold locks that block normal writes. It cannot run inside a transaction block and may leave an invalid index on failure.

#### Q. `pg_stat_user_indexes` shows zero scans for an index. Why should you not drop it immediately?

* [ ] Zero scans means every query already uses it
* [x] It may back a unique constraint or rare jobs
* [ ] Dropping an index also drops its table
* [ ] Scan counts include only sequential scans

> **Explanation:** Statistics can reset, and an index may back a uniqueness rule, foreign-key checks or a monthly report. Understand the observation period and purpose first.

#### Q. A report sums `amount` across hundreds of millions of sales. Which storage layout tends to suit it?

* [ ] Row storage, keeping each sale together
* [x] Column storage, reading mainly `amount`
* [ ] A wide-column store keyed by sale ID
* [ ] A key-value store with one sale per key

> **Explanation:** Columnar engines store each field's values together, so an aggregate reads mostly the needed column. Wide-column databases like Cassandra are a different design organized around partition keys.
