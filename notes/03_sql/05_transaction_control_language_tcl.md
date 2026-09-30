# Transactions: Make Related Changes Succeed Together

A checkout involves more than one write. The bookstore must record an order, record its lines, and reduce stock. If an application stops between those operations, a partially recorded purchase can be misleading.

A **transaction** groups database work. `COMMIT` accepts its transactional changes; `ROLLBACK` undoes them. This all-or-nothing property is called **atomicity**. It protects the group, but the application must still decide which statements belong together and when the workflow has failed.

Use the SQLite bookstore from the [SQL introduction](01_intro_to_sql.md). Keep one connection open for each transaction example.

## Follow a successful purchase

For this single-session exercise, assume product 10 exists with five units in stock and order 104 is unused:

```sql
BEGIN;

UPDATE products
SET stock = stock - 1
WHERE product_id = 10 AND stock > 0;

-- In an application, require exactly one affected row before continuing.
INSERT INTO orders (order_id, customer_id, order_date)
VALUES (104, 2, '2025-01-13');

INSERT INTO order_items
    (order_id, line_number, product_id, quantity, unit_price_cents)
VALUES (104, 1, 10, 1, 1500);

COMMIT;
```

After commit, product 10 has four units, and Bob has a new order containing one book. The order uses the default `open` status.

The affected-row check is essential. If no unit was deducted, blindly inserting an order would violate the purchase workflow even though each insert could be valid SQL. A database transaction does not automatically interpret a zero-row update as a failure.

The example uses a known sample purchase price. A real checkout also needs a policy for selecting and validating the price while concurrent changes occur.

## Follow a rollback

This exercise deliberately does not keep its change:

```sql
BEGIN;
UPDATE products SET stock = stock + 10 WHERE product_id = 20;
SELECT stock FROM products WHERE product_id = 20;
ROLLBACK;
SELECT stock FROM products WHERE product_id = 20;
```

The first select sees 18; the second sees the original eight. A transaction reads its own changes before committing them. Rollback does not undo commits made by unrelated transactions.

## Handle the failure explicitly

An application should start the transaction, perform the steps and required checks, then commit only when all succeed. On a relevant error or invalid result, it should roll back.

This Python function demonstrates the affected-row check with the same SQLite schema. `conn` is an existing connection with the sample tables and foreign-key checks enabled. Call it when no other transaction is open; the connection context commits on normal exit and rolls back if an exception leaves the block.

```python
import sqlite3

def buy_one(conn, order_id, customer_id, product_id, price_cents):
    with conn:
        changed = conn.execute(
            "UPDATE products SET stock = stock - 1 "
            "WHERE product_id = ? AND stock > 0",
            (product_id,),
        ).rowcount
        if changed != 1:
            raise ValueError("Product missing or out of stock")

        conn.execute(
            "INSERT INTO orders (order_id, customer_id, order_date) "
            "VALUES (?, ?, ?)",
            (order_id, customer_id, "2025-01-13"),
        )
        conn.execute(
            "INSERT INTO order_items "
            "(order_id, line_number, product_id, quantity, unit_price_cents) "
            "VALUES (?, 1, ?, 1, ?)",
            (order_id, product_id, price_cents),
        )
```

The `?` markers are **bound parameters**: the driver sends the supplied values separately from SQL structure. They avoid building SQL by inserting arbitrary strings.

If a customer ID is invalid or the order ID already exists, an insert raises an error. The context then rolls back the earlier stock decrement too. The function assumes the caller has already established the permitted purchase price; trusting an arbitrary client-supplied amount would be a different correctness problem.

## Savepoints: undo a part of the work

A **savepoint** marks a position inside a transaction. Rolling back to it undoes work after that position while retaining earlier work:

```sql
BEGIN;
UPDATE products SET stock = stock + 1 WHERE product_id = 10;

SAVEPOINT optional_change;
UPDATE products SET price_cents = 2000 WHERE product_id = 10;
ROLLBACK TO optional_change;
RELEASE optional_change;

-- The stock increment remains; the price change was undone.
-- Roll back the exercise so the sample stays unchanged.
ROLLBACK;
```

A savepoint is not an independently durable commit. If the outer transaction rolls back, its earlier changes are undone too.

## Autocommit and connection state

**Autocommit** means statements are committed without an explicit multi-statement transaction around them, according to the engine and driver's rules. Drivers can also open transactions implicitly.

Know which behavior your connection uses. Starting a transaction on one connection and doing the next write on another does not create one shared transaction. Returning an unfinished transaction to a connection pool can also surprise the next borrower.

## Atomicity does not mean complete isolation

Two buyers can both read “one copy remains.” A transaction does not automatically make every read-and-later-write pattern safe against that race. Use conditional updates, constraints, locking, or suitable isolation to protect the relevant decision.

A transaction also does not undo an email or remote payment already sent. External effects need their own coordination or retry-safe design.

## Check your understanding

1. Which changes belong in the same checkout transaction?
2. Why does a zero-row decrement need an application check?
3. What happens to stock if an order insert fails in `buy_one`?
4. Can a savepoint preserve a change after the outer transaction rolls back?

Continue with [joins and views](06_joins_subqueries_and_views.md) for richer reads. The [ACID introduction](../04_acid_properties_and_transactions/01_transactions_intro.md) explains the broader transaction guarantees.
