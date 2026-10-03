# Query Optimization: Find and Reduce Unnecessary Work

A query can return the correct result and still do far more work than necessary. **Optimization** means reducing that work while preserving the result the application needs. Start with one measured problem, not a checklist of indexes to add everywhere.

Before this note, practice [joins](../03_sql/06_joins_subqueries_and_views.md) and understand [indexes](../05_storage_and_indexing/05_indexing.md). We will use the bookstore's order lookup to connect SQL, access paths, and measurements.

## State the request and measure the problem

Suppose the account page needs a customer's open orders, newest first. Record the SQL, parameter values, typical result size, and observed response times. Also ask whether time is spent executing SQL, waiting for a connection, waiting for a lock, transferring results, or rendering the page.

**Latency** is time to complete an operation. **Throughput** is completed operations per unit time. A database can have good average latency but poor slow-tail latency, so distributions matter more than one favorable timing.

Use representative data. A three-row tutorial table teaches syntax; it cannot demonstrate production speed or the effects of skewed customer activity.

## Read a plan for the actual query

Use the fresh [SQLite bookstore setup](../03_sql/01_intro_to_sql.md):

```sql
EXPLAIN QUERY PLAN
SELECT order_id, order_date
FROM orders
WHERE customer_id = 1 AND status = 'open'
ORDER BY order_date DESC, order_id DESC;
```

An **execution plan** describes how the engine intends to obtain the result. Look for a scan or indexed search and whether sorting needs a temporary structure. The exact plan text varies with engine version, statistics, and available indexes; it is not another table of business results.

In PostgreSQL, `EXPLAIN` shows estimates; `EXPLAIN (ANALYZE, BUFFERS)` actually runs the statement and adds execution and buffer information. Applying an execution-measuring form to a write can perform the write, so use an appropriate test environment and transaction strategy.

**Estimated rows** are the optimizer's prediction. **Actual rows** are what execution produced. A large mismatch is a clue that the optimizer chose based on inaccurate information. Costs in a plan are usually engine-specific estimates, not milliseconds.

## Match an index to the access pattern

```sql
CREATE INDEX idx_orders_customer_status_date
ON orders(customer_id, status, order_date DESC, order_id DESC);
```

The query fixes the first two columns to one customer's open orders, then requests the remaining columns in the index's order. This gives the engine a potentially useful route to matching rows without a separate sort.

Run the plan query again. The optimizer may still choose another route, especially for a tiny table. An index is an available option, not an instruction that the engine must use it.

Do not add every column “just in case.” Each index uses space and increases relevant write work. [Performance indexing strategies](02_indexing_strategies.md) covers composite, partial, and covering indexes in more detail.

## Keep predicates usable by the available index

A **predicate** is a condition such as `order_date >= ...`. An index on a date column is often more useful when the query compares that column directly than when it first applies an unrelated function to every value.

For the tutorial's consistently formatted ISO date text, find January orders with a half-open range:

```sql
SELECT order_id, order_date
FROM orders
WHERE order_date >= '2025-01-01'
  AND order_date < '2025-02-01'
ORDER BY order_date, order_id;
```

A **half-open range** includes the lower boundary and excludes the upper boundary. With real timestamp columns, this approach also avoids guessing the last fraction of a second in the month. Choose boundaries in the intended timezone.

An expression index can sometimes support a computed predicate. Implicit type conversions, collation differences, and a leading-wildcard search can also change whether an index is useful. Inspect the plan rather than assuming every function or conversion has the same effect in every engine.

## Check whether joins multiply rows unnecessarily

If the page only needs customers who have an order, joining customers to every order and then removing duplicates can create avoidable intermediate rows. `EXISTS` expresses the intended question:

```sql
SELECT c.customer_id, c.name
FROM customers AS c
WHERE EXISTS (
    SELECT 1 FROM orders AS o
    WHERE o.customer_id = c.customer_id
)
ORDER BY c.customer_id;
```

This returns Alice and Bob once each. It expresses existence; it does not promise a faster plan in every engine. The optimizer may implement equivalent SQL forms similarly.

For real joins, verify the join keys and expected relationship: one-to-many naturally expands rows, while a missing join condition can create every pairing. A join's output size affects later sorts and aggregates.

## Reduce output only when the requirement allows it

Select the needed columns instead of an unnecessarily wide result. Paginate long lists rather than transferring every row for one screen. Use a deterministic ordering with a unique tie-breaker.

**Offset pagination** skips a number of earlier rows; deep offsets can become expensive and concurrent changes can shift positions. **Keyset pagination** continues from the last seen ordering key. For the order-date/identifier ordering, the next page can ask for records earlier than the last `(order_date, order_id)` pair. Its exact predicate and index must match the ordering and null policy.

Avoid an **N+1 query** pattern: loading a list with one query, then issuing one more query per item. A deliberate join, batch lookup, or ORM eager-loading strategy can reduce round trips. It can also overfetch, so compare total work and result size.

## Diagnose statistics and resource limits

The optimizer uses **statistics** about table size and value distribution. Stale statistics or highly uneven data can lead to poor estimates. Use the engine's supported statistics-maintenance commands and inspect whether the estimate actually improves.

Sorting or joining a large intermediate result can exceed its memory allowance and **spill** temporary data to disk. Large scans can compete for I/O; locks can turn a quick query into a long wait. Those problems need different remedies. Raising memory globally can overload a server when many operations run concurrently.

A **partitioned table** separates data into subsets. **Partition pruning** lets a suitable predicate exclude irrelevant partitions. It helps only when the request and partition scheme align; partitioning is not a universal replacement for indexing.

## Compare before and after fairly

Keep the data, parameters, and load comparable. Measure more than one run and distinguish cold-cache from warm-cache behavior. Include write costs if you added an index, and verify the same rows, ordering, null behavior, and totals.

For production changes, compare against the actual workload and watch for regressions. A hint that forces a plan can become inappropriate when data changes; hints should follow a diagnosis rather than substitute for one.

If an expensive calculation must be reused, consider a [materialized view](04_materialized_views.md) or [cache](03_database_caching.md). Both introduce freshness and maintenance requirements. Distributed execution also adds data-transfer costs: moving rows across nodes can dominate the local SQL work.

## Check your understanding

1. How does a connection-pool wait differ from a slow query execution?
2. Why do the index columns follow this query's filters and ordering?
3. Why can the tiny tutorial table still use a scan after the index is added?
4. What does a large estimated-versus-actual row mismatch suggest?
5. Which correctness checks belong beside a before-and-after timing?

Continue with [indexing strategies](02_indexing_strategies.md), then [caching](03_database_caching.md). For ongoing diagnosis, see [performance monitoring](../11_security_best_practices/05_performance_monitoring_and_tuning.md).
