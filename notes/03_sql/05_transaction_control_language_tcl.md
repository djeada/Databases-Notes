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

## Follow a transfer all the way through failure

Two updates can form one business operation. Use a separate pair of accounts:

```sql
CREATE TABLE tcl_accounts (
    account_id INTEGER PRIMARY KEY,
    balance_cents INTEGER NOT NULL CHECK (balance_cents >= 0)
);
INSERT INTO tcl_accounts VALUES (1, 10000), (2, 2000);

BEGIN;
UPDATE tcl_accounts SET balance_cents = balance_cents - 3000
WHERE account_id = 1 AND balance_cents >= 3000;
UPDATE tcl_accounts SET balance_cents = balance_cents + 3000
WHERE account_id = 2;
SELECT account_id, balance_cents FROM tcl_accounts ORDER BY account_id;
ROLLBACK;
```

Inside the transaction the balances are 7000 and 5000; after rollback they are 10000 and 2000. A successful transfer would commit instead. However, the SQL alone has a gap: an update can affect zero rows without raising an error. If the destination were missing, blindly committing would debit money without crediting an account.

The application must verify both outcomes. This helper uses Python's default SQLite transaction mode and assumes the account setup has been committed before the call:

```python
def transfer(connection, source_id, destination_id, amount_cents):
    if source_id == destination_id:
        raise ValueError('choose different accounts')
    if not isinstance(amount_cents, int) or amount_cents <= 0:
        raise ValueError('amount must be positive integer cents')
    with connection:
        debit = connection.execute(
            'UPDATE tcl_accounts SET balance_cents = balance_cents - ? '
            'WHERE account_id = ? AND balance_cents >= ?',
            (amount_cents, source_id, amount_cents),
        )
        if debit.rowcount != 1:
            raise ValueError('source missing or insufficient funds')
        credit = connection.execute(
            'UPDATE tcl_accounts SET balance_cents = balance_cents + ? '
            'WHERE account_id = ?',
            (amount_cents, destination_id),
        )
        if credit.rowcount != 1:
            raise ValueError('destination missing')
```

Calling `transfer(connection, 1, 2, 3000)` commits the two changes. Calling it with destination 999 raises an error and rolls the debit back. The amount and account checks express the operation's rules; the transaction supplies all-or-nothing persistence for the successful statements. Atomicity does not itself decide that the destination is valid.

For multiple concurrent SQL Server or PostgreSQL transfers, conflicting account updates may wait or deadlock. A consistent account-lock ordering can reduce deadlocks, and the application must handle retriable transaction failures. SQLite serializes writers rather than providing the same row-lock model.

## Know whether the connection starts a transaction for you

In a shell, the examples use explicit `BEGIN`, `COMMIT`, and `ROLLBACK`. Drivers also manage transaction state. Python's `sqlite3` default legacy handling implicitly begins a transaction for writing statements; the connection context manager commits or rolls back an existing transaction when it exits. It does not begin a transaction merely because `with connection:` was entered.

Python 3.12 introduced the `autocommit` configuration, while retaining legacy behavior by default. If the connection is in SQLite autocommit mode, the context manager does not group separately committed statements into a transfer. Configure the mode deliberately, or use explicit transaction statements with a compatible driver configuration. Do not copy a helper that assumes one mode into a connection using another.

An application should own the full transaction boundary. Returning a pooled connection with a transaction left open can leave locks, old snapshots, or unrelated changes for the next borrower. On an exception, roll back before reusing or returning it. On normal completion, commit only the work the current operation owns.

## A savepoint is a recovery boundary inside a transaction

A savepoint does not create an independently committed transaction. This SQLite example keeps one accepted adjustment and abandons an optional second adjustment:

```sql
BEGIN;
UPDATE tcl_accounts SET balance_cents = balance_cents + 100 WHERE account_id = 1;
SAVEPOINT optional_adjustment;
UPDATE tcl_accounts SET balance_cents = balance_cents + 500 WHERE account_id = 2;
ROLLBACK TO optional_adjustment;
RELEASE optional_adjustment;
SELECT account_id, balance_cents FROM tcl_accounts ORDER BY account_id;
ROLLBACK;
```

On the original account setup, the intermediate result is 10100 and 2000. Rolling back to the savepoint preserves the first adjustment and undoes the second. Releasing the savepoint removes that inner boundary; the final outer rollback still undoes the first adjustment. If you ran the successful Python transfer first, begin this exercise with a fresh account setup to obtain these values.

In PostgreSQL, an error normally leaves the transaction unable to execute ordinary statements until rollback, or rollback to an appropriate earlier savepoint. In SQLite, many constraint errors undo just the failed statement and leave the transaction active. The application should not infer one engine's error handling from another's behavior.

## Keep slow external work outside the database transaction

A transaction that waits for a customer to click a button or for an email server to respond can hold locks for seconds or minutes. Collect input and perform work that does not require protected database state before beginning. Inside the transaction, read the necessary state, validate it using an appropriate concurrency strategy, write, and commit promptly.

An email is not undone by `ROLLBACK`. If an order and a notification request must persist together, insert the order and an outbox row in one transaction. A separate worker sends the message after commit and records its progress. That worker still needs duplicate-handling because it might send successfully and fail before marking the row sent.

## Retry the operation, with a way to recognize it

A deadlock or serialization failure may require rerunning the complete transaction against fresh state. Repeating only the last statement can reuse decisions made from an obsolete read. Use bounded retries for errors the driver identifies as retriable; do not retry a bad email address or an insufficient balance as though it were temporary.

A broken connection during commit is different: the server might have committed even though the client did not receive the reply. Use a unique operation identifier for a checkout or payment instruction, and look up its outcome after reconnecting. Blindly submitting the same operation under a new identifier can create a duplicate. Transaction control and idempotency address related but distinct failures.

References: [Python SQLite transaction control](https://docs.python.org/3/library/sqlite3.html#transaction-control) and [PostgreSQL savepoints](https://www.postgresql.org/docs/current/sql-savepoint.html).

## Check your understanding

1. Which changes belong in the same checkout transaction?
2. Why does a zero-row decrement need an application check?
3. What happens to stock if an order insert fails in `buy_one`?
4. Can a savepoint preserve a change after the outer transaction rolls back?

Continue with [joins and views](06_joins_subqueries_and_views.md) for richer reads. The [ACID introduction](../04_acid_properties_and_transactions/01_transactions_intro.md) explains the broader transaction guarantees.
