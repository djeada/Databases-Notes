# Denormalization: Add Redundancy with a Maintenance Plan

[Normalization](02_normalization.md) separates facts so each has a clear home. **Denormalization** deliberately stores an additional copy or precomputed result to make a particular read cheaper. It creates a new responsibility: keep that copy correct, or explicitly allow it to lag.

Start with a concrete slow read, not with the assumption that joins are always expensive.

## Example: show an order's total

In the bookstore, an order's amount can be calculated from its lines:

```text
order 101:
  line 1: 2 × 15.00 = 30.00
  line 2: 1 × 25.00 = 25.00
  total:              55.00
```

A query can calculate this using `SUM(quantity * purchase_price)`. If every order-history page repeatedly calculates totals for many orders, storing an `order_total` may be useful.

The line items remain the **source of truth**: the facts from which the total is derived. The stored total is an additional representation of those facts.

## Follow the update, not only the fast read

Suppose staff change line 1's quantity from two to three. The correct total becomes 70.00.

If the application changes the line but leaves `order_total = 55.00`, the fast read is now wrong. If two applications maintain the total differently, the same order can produce different answers depending on the query.

The performance benefit therefore has to include both sides:

| Operation | Calculate from lines | Store a total |
| --- | --- | --- |
| Read the total | Read and aggregate relevant lines. | Read the saved total. |
| Change a line | Change the line. | Change the line and maintain the total. |
| Diagnose disagreement | One representation to inspect. | Compare the total with its source lines. |

## Implement a stored total and its maintenance path

Use the fresh [SQLite bookstore setup](../03_sql/01_intro_to_sql.md). This example adds a derived field to orders while leaving line items authoritative:

```sql
ALTER TABLE orders ADD COLUMN cached_total_cents INTEGER;
UPDATE orders
SET cached_total_cents = (
    SELECT COALESCE(SUM(i.quantity * i.unit_price_cents), 0)
    FROM order_items AS i
    WHERE i.order_id = orders.order_id
);
SELECT order_id, cached_total_cents FROM orders ORDER BY order_id;
```

| order_id | cached_total_cents |
|---|---|
| 101 | 5500 |
| 102 | 1500 |
| 103 | 5000 |

A correlated subquery calculates each order's total; `COALESCE` chooses zero for an order without lines. The nullable field lets the initial migration represent “not computed yet.” After backfilling and checking it, an engine-appropriate migration can enforce a stronger required-value rule if needed.

### Follow a complete write rather than updating only the display field

```sql
BEGIN;
UPDATE order_items SET quantity = 3 WHERE order_id = 101 AND line_number = 1;
UPDATE orders
SET cached_total_cents = (
    SELECT COALESCE(SUM(quantity * unit_price_cents), 0)
    FROM order_items WHERE order_id = 101
)
WHERE order_id = 101;
SELECT cached_total_cents FROM orders WHERE order_id = 101;
ROLLBACK;
```

The query sees `7000` inside the transaction. Rollback returns both the quantity and the cached total to their earlier values. Atomic grouping prevents committing just one change, but all writers still need a concurrency-safe maintenance policy. The example relies on one SQLite writer at a time; do not infer that this recomputation is safe under every multi-writer engine and isolation level.

For a server database, concurrent edits can require locking the owning order, applying safe deltas, or serializable transactions with retries. A trigger can centralize maintenance but must handle inserts, updates, deletes, moves between orders, and multi-row operations. A trigger that updates only for inserts would leave deletions wrong.

### Detect drift and rebuild

```sql
SELECT o.order_id, o.cached_total_cents,
       COALESCE(SUM(i.quantity * i.unit_price_cents), 0) AS actual_total_cents
FROM orders AS o
LEFT JOIN order_items AS i ON i.order_id = o.order_id
GROUP BY o.order_id, o.cached_total_cents
HAVING o.cached_total_cents IS NULL
    OR o.cached_total_cents <> COALESCE(SUM(i.quantity * i.unit_price_cents), 0)
ORDER BY o.order_id;
```

The correctly initialized sample returns no rows. Run the original backfill expression to rebuild totals from the source. Reconciliation is part of the design: “the application normally updates it” is not enough when bugs, old clients, or imports can bypass that path.

## Choose how the copy is maintained

**In the same transaction:** the line change and total update commit together. All writers must follow the maintenance rule, or database-side logic must enforce it. Concurrent changes still need safe coordination.

**By background refresh:** a worker periodically recomputes totals or summaries. Readers can see an older result. Record refresh progress and decide how much staleness is acceptable.

**Through a materialized view:** the database stores a query result using its supported refresh model. This reduces custom code but has engine-specific costs and restrictions.

A transaction is a group of work that commits together or rolls back. A refresh is the operation that updates a derived copy. They solve different parts of the problem.

## Distinguish redundancy from historical facts

A purchase price belongs to an order line even if the product has a current price elsewhere. Those values describe different times and are not duplicate copies of one fact.

Similarly, an invoice may need the billing address as issued, not the customer's current address. Define which question a field answers before replacing it with a reference or labeling it denormalization.

## Measure before introducing another representation

First inspect the query, its indexes, and the number of rows actually read. A suitable index or smaller result may remove the bottleneck without duplicating data.

If denormalization is still justified, document:

- Which read it accelerates.
- Which data is authoritative.
- Which writes must update the copy.
- Whether readers may see stale values.
- How to rebuild and reconcile the copy after an error.

An **index** adds an access path to existing data; a stored total adds another representation of a calculation. A **cache** is another copy with its own expiry or invalidation rules. Do not treat these mechanisms as identical.

## Compare four concrete techniques

| Technique | Read saved | Additional write responsibility |
|---|---|---|
| Redundant column | Avoid fetching a related value | Keep the copy aligned with its authoritative owner |
| Precomputed aggregate | Avoid repeated sums or counts | Apply every relevant source change or refresh |
| Separate read table | Present a flattened report in one lookup | Rebuild and synchronize the entire projection |
| Embedded document | Load a bounded aggregate as one record | Decide which shared facts are duplicated and how they change |

A **projection** is a representation prepared for a particular read. A customer-order dashboard might use a row containing the order identifier, current customer display name, and total. It is useful only if readers know whether it means current state, an as-issued snapshot, or a delayed report.

## PostgreSQL materialized views provide a managed stored result

This independent PostgreSQL example requires a database where you can create objects. It keeps the setup small so it does not depend on SQLite's dialect:

```sql
-- PostgreSQL
CREATE TABLE denorm_sales (
    sale_id INTEGER PRIMARY KEY,
    sold_on DATE NOT NULL,
    amount_cents BIGINT NOT NULL
);
INSERT INTO denorm_sales VALUES (1, DATE '2025-01-10', 3000),
                               (2, DATE '2025-01-10', 2500);
CREATE MATERIALIZED VIEW denorm_daily_sales AS
SELECT sold_on, SUM(amount_cents) AS revenue_cents
FROM denorm_sales GROUP BY sold_on;

SELECT sold_on, revenue_cents FROM denorm_daily_sales ORDER BY sold_on;
```

The initial result is January 10 with revenue `5500`. Adding a sale does not automatically update this ordinary PostgreSQL materialized view:

```sql
-- PostgreSQL
INSERT INTO denorm_sales VALUES (3, DATE '2025-01-10', 1500);
REFRESH MATERIALIZED VIEW denorm_daily_sales;
SELECT sold_on, revenue_cents FROM denorm_daily_sales ORDER BY sold_on;
```

After refresh it shows `7000`. A concurrent refresh has extra requirements, including a suitable unique index; it is not the default behavior merely because the view exists. See [PostgreSQL materialized views](https://www.postgresql.org/docs/current/rules-materializedviews.html).

This can fit a report that accepts refresh delay. It is a poor substitute for a checkout decision that must use current stock. An ordinary view stores a query definition; a materialized view stores its result according to its refresh model.

## Document and query-oriented stores make the same tradeoff visible

MongoDB can embed a bounded set of order lines inside the order document, making one-order reads convenient. Cassandra often maintains different tables for different keyed queries. These are concrete reasons a model can use deliberate redundancy, not reasons to copy every field indiscriminately.

A background projection needs a version or progress marker, retry handling, and a policy for duplicate or out-of-order changes. If a consumer applies an increment twice, its total drifts even when every event was valid. Rebuilding from authoritative data and comparing results gives an escape path when the incremental copy becomes suspect.

## Decide whether the measured benefit justifies the cost

Compare response-time distribution, source rows read, update cost, storage growth, and reconciliation complexity. Test typical and unusually large orders. Check whether the latest display must include a just-committed write. A faster stale total is not an equivalent result if the application promised a current amount.

Document the source, refresh or update mechanism, permitted delay, ownership, and rebuild procedure beside the schema. Retire a projection when the workload no longer needs it instead of carrying its write cost indefinitely.

## Check your understanding

1. What should happen to order 101's total if a line is changed?
2. Why is “update it in the application” incomplete when several programs write the data?
3. When would a daily sales summary allow delayed refresh, while a checkout amount would not?
4. Why is purchase price different from a duplicated current price?

Continue with [indexing strategies](04_indexing_strategies.md) for a way to improve access without adding business facts. [Materialized views](../08_database_performance/04_materialized_views.md) develops the stored-summary approach.
