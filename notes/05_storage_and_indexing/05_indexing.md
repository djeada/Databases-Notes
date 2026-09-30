# Database Indexing

An index is an additional access path to data. It can reduce the rows and pages examined by a query, but it also consumes storage and must be maintained when indexed data changes. Start with the queries you need to support, then verify the resulting plans.

## How a B-tree lookup works

A B-tree-family index stores ordered keys in a balanced structure. Internal pages direct a search toward leaf pages; leaf entries identify rows or contain the rows themselves, depending on the engine.

```text
Root page --> Internal page --> Leaf entries --> Rows, if needed
```

An equality lookup can navigate to the matching keys. A range lookup finds its starting point and then scans the relevant entries. Retrieving many rows still costs work: logarithmic navigation does not make the whole result free.

Without `ORDER BY`, SQL does not guarantee output order even when the plan uses an ordered index.

## Index types and access methods

| Type | Useful operations | Important limits |
| --- | --- | --- |
| B-tree family | Equality, ranges, ordered traversal | Matching many rows can make a scan cheaper. |
| Hash | Equality | Does not support ordered range traversal; availability depends on the engine. |
| Bitmap | Combining categorical predicates in analytical workloads | Persistent bitmap indexes can create write contention; support is engine-specific. |
| Inverted / full-text | Search terms, documents, and some containment queries | Tokenization and supported operators determine matching behavior. |
| Spatial | Geometric predicates | Often requires an exact predicate check after candidate lookup. |
| BRIN (PostgreSQL) | Pruning block ranges when values correlate with storage order | Lossy summaries; generally less useful when values are scattered. |
| Columnstore | Scans, compression, analytical aggregation | Different trade-offs from a rowstore lookup index. |

PostgreSQL bitmap scans combine index results at execution time; they are not the same as Oracle persistent bitmap indexes. PostgreSQL GIN, GiST, and SP-GiST support different operator classes, rather than being interchangeable general-purpose indexes.

## Clustered storage and secondary indexes

A rowstore clustered index stores table rows in its leaf pages, logically organized by the index key. It does not guarantee that pages occupy consecutive disk sectors.

- **InnoDB:** the primary key normally supplies the clustered key. Secondary entries carry that key to locate the row.
- **SQL Server:** a table can have one clustered rowstore index or be a heap. A primary-key constraint can use a clustered or nonclustered index.
- **PostgreSQL:** ordinary tables are heaps with separate indexes. `CLUSTER` rewrites a table in an index's order once; later writes do not automatically preserve that order.

Both clustered and secondary B-tree indexes can support range searches. A secondary lookup needs extra table access only when the query cannot be answered from the index and the engine's visibility rules require it.

## Designing a composite index

Assume PostgreSQL and this access pattern:

```sql
SELECT order_id, order_date, total
FROM orders
WHERE customer_id = 42
  AND order_date >= DATE '2025-01-01'
  AND order_date < DATE '2026-01-01'
ORDER BY order_date;
```

A useful candidate is:

```sql
CREATE INDEX idx_orders_customer_date
ON orders (customer_id, order_date);
```

The equality predicate selects one customer; within that customer, the date keys support a range and ordering. An index on `(order_date, customer_id)` is a different access path and may be less effective for this query. Leading-column rules are useful guidance, but engines can have skip-scan and other optimizations: inspect the actual plan.

### Covering a query

In PostgreSQL, payload columns can be included:

```sql
CREATE INDEX idx_orders_customer_date_cover
ON orders (customer_id, order_date) INCLUDE (order_id, total);
```

Choose this **instead of** the previous index unless both have a demonstrated purpose. Coverage is a property of a particular query, not an index label that applies to all queries. PostgreSQL index-only scans also depend on visibility information; including every selected column does not guarantee zero heap fetches.

### Indexing a subset

For queries that repeatedly select open orders:

```sql
CREATE INDEX idx_orders_open_customer
ON orders (customer_id)
WHERE status = 'open';
```

PostgreSQL calls this a partial index; SQL Server has filtered indexes. The optimizer must be able to establish that a query's predicate satisfies the index condition. Parameterized predicates can affect that proof.

### Indexing an expression

```sql
CREATE INDEX idx_users_lower_email ON users (lower(email));
SELECT user_id FROM users WHERE lower(email) = 'alice@example.com';
```

An expression index can support a matching expression. Requirements such as function immutability and collation semantics depend on the engine.

## Keys, uniqueness, and foreign keys

A `UNIQUE` constraint states a data rule; a unique index is an enforcement and access mechanism. Nullable uniqueness rules differ between engines. A primary key is not synonymous with a clustered index.

A foreign-key constraint does not universally create an index on its referencing columns. Such an index may be valuable for joins and parent-row updates or deletions. Check the engine and workload rather than assuming it exists.

## Verify the benefit

For PostgreSQL:

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT order_id, order_date, total
FROM orders
WHERE customer_id = 42;
```

`ANALYZE` executes the statement. Look at actual rows, estimates, buffers, and total time. A sequential scan is not inherently a problem: on a small table, or when much of a table qualifies, it can be the best plan.

Refresh planner statistics when needed. Compare representative parameter values and consider the write cost before retaining an index.

## Monitoring and maintenance

PostgreSQL usage and size:

```sql
SELECT relname AS table_name,
       indexrelname AS index_name,
       idx_scan,
       pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;
```

Size and a zero scan count do not prove bloat or redundancy. Statistics have an observation period and can reset; an index may enforce a constraint or support infrequent critical work. Measure unused space with suitable engine-specific diagnostics.

Maintenance syntax is not portable:

```sql
-- PostgreSQL: requires a supported version and cannot run in a transaction block.
REINDEX INDEX CONCURRENTLY idx_orders_customer_date;
```

```sql
-- SQL Server
ALTER INDEX idx_orders_customer_date ON dbo.orders REBUILD;
-- A different, incremental maintenance operation:
ALTER INDEX idx_orders_customer_date ON dbo.orders REORGANIZE;
```

Measure whether maintenance improves the workload. Rebuilds consume I/O, CPU, log space, and temporary capacity; online options have engine and edition restrictions. A fixed fragmentation percentage alone is insufficient justification.

## Related notes

- [Storage on disk](01_how_tables_and_indexes_are_stored_on_disk.md)
- [Primary keys and secondary indexes](03_primary_key_vs_secondary_key.md)
- [Index access methods](../08_database_performance/02_indexing_strategies.md)
- [SQL Server indexing walkthrough](../../projectes/indexes_in_microsoft_sql_server.md)
- [PostgreSQL indexes](https://www.postgresql.org/docs/current/indexes.html)
