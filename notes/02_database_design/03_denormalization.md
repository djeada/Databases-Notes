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

## Check your understanding

1. What should happen to order 101's total if a line is changed?
2. Why is “update it in the application” incomplete when several programs write the data?
3. When would a daily sales summary allow delayed refresh, while a checkout amount would not?
4. Why is purchase price different from a duplicated current price?

Continue with [indexing strategies](04_indexing_strategies.md) for a way to improve access without adding business facts. [Materialized views](../08_database_performance/04_materialized_views.md) develops the stored-summary approach.
