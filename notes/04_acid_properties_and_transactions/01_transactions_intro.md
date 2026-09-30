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

## Inspect the accepted operation, not just the last statement

Continue immediately after the checkout above. Verify both its stock change and its recorded line:

```sql
SELECT product_id, stock FROM products WHERE product_id = 10;
SELECT o.order_id, o.customer_id, o.status,
       i.product_id, i.quantity, i.unit_price_cents
FROM orders AS o
JOIN order_items AS i ON i.order_id = o.order_id
WHERE o.order_id = 104;
```

The stock result is `(10, 4)`. The order result is `(104, 2, open, 10, 1, 1500)`. Its `open` status comes from the default, not from a hidden transaction property. The purchase price is recorded on the line so a later catalog price change does not rewrite what Bob agreed to pay.

This is still a deliberately small checkout. It does not charge a card, calculate tax, reserve a named copy, or record a complete stock ledger. A transaction's boundary should correspond to the operation actually implemented, and its success response should describe only that operation's guarantees.

## Contrast one transaction with separate autocommitted changes

Use a separate table to observe state without affecting the checkout:

```sql
CREATE TABLE tx_demo_steps (
    step_id INTEGER PRIMARY KEY,
    description TEXT NOT NULL
);

INSERT INTO tx_demo_steps VALUES (1, 'first independently accepted step');
BEGIN;
INSERT INTO tx_demo_steps VALUES (2, 'second step, still pending');
SELECT step_id FROM tx_demo_steps ORDER BY step_id;
ROLLBACK;
SELECT step_id FROM tx_demo_steps ORDER BY step_id;
```

In a SQLite shell with no enclosing transaction, the initial insert commits as its own statement. Inside the explicit transaction, the first query sees steps 1 and 2. After rollback, only step 1 remains. Rollback undoes the pending transaction; it cannot undo an earlier independent commit merely because the commands were part of the same script.

A driver might implicitly begin a transaction for that first insert. Before reproducing the shell behavior through Python, commit the setup and initial insert, or configure explicit transaction handling. A script is a sequence of commands, while a transaction is a database boundary. They are not synonyms.

## Follow the transaction's states

A useful conceptual lifecycle is:

```text
No active transaction
        |
      BEGIN
        |
  Active: read, validate, write
        |                  |
    all work succeeds     failure or cancellation
        |                  |
      COMMIT             ROLLBACK
        |                  |
  accepted changes       discarded changes
```

During the active phase, the connection can read its own writes. Other connections' visibility depends on isolation. A failed statement may leave the transaction active in SQLite or leave it in an aborted state in PostgreSQL. In either case, the client must determine whether to recover to a savepoint or roll back the whole business operation.

The diagram omits the uncertain client outcome when a connection disappears during commit. The server may have accepted the transaction before the connection failed. Durable operation IDs allow the client to query that accepted state instead of treating silence as proof of failure.

## Read-only work can also need a transaction

Suppose a financial report reads order totals and then reads payment totals. If those two statements use different snapshots, a concurrent payment can appear in one part of the report and not the other. A read-only transaction can make the intended snapshot policy explicit.

This independent **PostgreSQL** exercise creates a tiny ledger:

```sql
-- PostgreSQL
CREATE TABLE tx_report_ledger (
    entry_id INTEGER PRIMARY KEY,
    amount_cents BIGINT NOT NULL
);
INSERT INTO tx_report_ledger VALUES (1, 5500), (2, 5000);

BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY;
SELECT COUNT(*) AS entry_count FROM tx_report_ledger;
SELECT SUM(amount_cents) AS total_cents FROM tx_report_ledger;
COMMIT;
```

The initial results are 2 and 10500. PostgreSQL Repeatable Read uses one snapshot established by the first relevant statement, so both reads use the same committed view even if another session inserts a row between them. Read Committed would ordinarily take a new snapshot for the second statement. A stable snapshot does not automatically validate every cross-row business invariant; the isolation note explains write skew.

Long-running reports also have costs. Their snapshots can keep older row versions needed for visibility, and they can contend with maintenance or schema changes. Choose a clear consistency requirement rather than leaving a transaction open while a user reads the report on screen.

## Separate business operations from database statements

One transfer may require several statements, while one bulk update may affect thousands of rows. Transaction size is therefore not measured solely by statement count. Estimate the rows touched, locks held, log volume, and expected duration.

For a batch import, committing each valid record separately allows partial progress but creates a partial result on failure. One large transaction supplies all-or-nothing acceptance but can use substantial resources. Batches provide another contract: each batch is atomic, and the import tracks which batches were accepted. Explain that contract to users and give retries a way to avoid duplicating accepted records.

PostgreSQL and InnoDB support transactional table updates. Some MySQL storage engines do not supply the same rollback guarantee, and DDL can implicitly commit. SQLite's file-based deployment supplies real transactions but coordinates writes differently from a server with row-level locking. “This program uses SQL” is not enough to establish its transaction semantics.

Continue through each ACID property by asking what could go wrong in this exact checkout: a partial write, an invalid state, an overlapping buyer, or a crash after acknowledgment.

## Check your understanding

1. Why does the stock update belong in the same transaction as the order insert?
2. Why must the application inspect the number of changed rows?
3. Which ACID property addresses two buyers competing for the final copy?
4. Can rolling back the database cancel an email that has already been sent?
5. Why can a missing commit response require more care than an ordinary rejected statement?

Continue with [Atomicity](02_atomicity.md), then [Consistency](03_consistency.md), [Isolation](04_isolation.md), and [Durability](05_durability.md).
