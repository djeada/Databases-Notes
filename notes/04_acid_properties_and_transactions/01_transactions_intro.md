# Transactions: Make One Business Operation One Unit of Work

A bookstore checkout changes several facts: stock decreases, an order is created, and the purchased items are recorded. Those changes belong together. An order without its items is incomplete; a stock reduction without an order loses inventory.

A **transaction** groups database operations so they can be committed together or rolled back together. **Commit** accepts the changes. **Rollback** discards the transaction's changes. These operations apply to the database work in that transaction; they do not undo an email or an external payment.

## Follow one checkout

Use the fresh bookstore database from [Introduction to SQL](../03_sql/01_intro_to_sql.md). Product 10 starts with five copies in stock. This example records one copy for Bob, customer 2.

```sql
BEGIN;

UPDATE products
SET stock = stock - 1
WHERE product_id = 10 AND stock >= 1;

INSERT INTO orders (order_id, customer_id, order_date)
VALUES (104, 2, '2025-01-13');

INSERT INTO order_items
    (order_id, line_number, product_id, quantity, unit_price_cents)
VALUES (104, 1, 10, 1, 1500);

COMMIT;
```

On the starting data, the update changes one row, stock becomes four, and order 104 has one item. The application must check that the update changed exactly one row **before continuing**. Zero changed rows means the product is missing or unavailable; it is not a SQL error. In that case, roll back instead of creating the order. The [transaction control note](../03_sql/05_transaction_control_language_tcl.md) implements this check in Python.

If an insert fails, the application must also roll back the whole checkout. Engines differ in whether an error cancels a statement or leaves the transaction unusable. Do not assume that catching an exception makes earlier changes disappear.

## Four questions behind ACID

**ACID** names four properties used to reason about transactions. Each addresses a different problem.

| Property | Question | Checkout example |
|---|---|---|
| Atomicity | Can part of the operation be committed alone? | Stock and the order must be accepted together |
| Consistency | Does the resulting data obey the required rules? | Stock stays nonnegative and each order references a real customer |
| Isolation | What happens when operations overlap? | Two buyers must not both claim the final copy |
| Durability | What survives after commit is acknowledged? | The accepted order survives a crash under the configured durability guarantees |

A transaction is not automatically correct just because it commits. It can atomically run the wrong calculation, and the database cannot infer a business rule that you never encoded.

## Why isolation needs its own chapter

Suppose one copy remains. Alice and Bob both read `stock = 1`, then both create an order based on that old value. Grouping each checkout into a transaction does not, by itself, prove this workflow is safe.

The conditional update above makes the stock check part of the write. Depending on the engine and isolation level, competing transactions may wait, observe that no stock remains, or fail and require a retry. More complicated rules can need locks or serializable isolation.

**Concurrent** means operations overlap in time. An **isolation level** specifies which interactions concurrent transactions may observe. Serializable isolation promises an outcome equivalent to some serial order of successful transactions; weaker levels offer fewer guarantees. See [Isolation](04_isolation.md) for concrete read anomalies.

## Keep the transaction boundary deliberate

A **connection** is an application's session with the database. Start, perform, and finish the transaction on the same connection. Many drivers provide a transaction context manager that commits on success and rolls back on failure; check its actual behavior.

In **autocommit** mode, each statement normally has its own transaction. That is useful for a single independent change, but it does not group a three-statement checkout. Keep transactions short: waiting for a user or a network payment while holding database resources can delay other work.

A lost connection during commit creates a different problem: the server may have committed even though the client never received confirmation. A retry needs a stable operation identifier or another way to recognize an already accepted checkout. Retrying blindly can duplicate work.

## Check your understanding

1. Why does the stock update belong in the same transaction as the order insert?
2. Why must the application inspect the number of changed rows?
3. Which ACID property addresses two buyers competing for the final copy?
4. Can rolling back the database cancel an email that has already been sent?
5. Why can a missing commit response require more care than an ordinary rejected statement?

Continue with [Atomicity](02_atomicity.md), then [Consistency](03_consistency.md), [Isolation](04_isolation.md), and [Durability](05_durability.md).
