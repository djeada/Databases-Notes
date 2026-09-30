# Atomicity: Commit the Whole Operation or None of It

**Atomicity** means that a transaction's changes are committed as one unit. If the transaction is rolled back, none of those changes remain committed. The operations still execute one after another; atomicity does not mean they take place at the same instant.

Read [Transactions](01_transactions_intro.md) first. Its checkout groups a stock reduction, an order, and an order item.

## See rollback undo an earlier change

Use the fresh [bookstore setup](../03_sql/01_intro_to_sql.md). Product 10 begins with stock 5.

```sql
BEGIN;

UPDATE products SET stock = stock - 1 WHERE product_id = 10;
SELECT stock FROM products WHERE product_id = 10;

ROLLBACK;

SELECT stock FROM products WHERE product_id = 10;
```

The first query returns 4 within this transaction. The second returns 5 after rollback. Rolling back removes this transaction's change; it does not restore the entire database to an old snapshot or undo other transactions' committed work.

## An error is not the same as rollback

Imagine the stock update succeeds, but inserting the order fails because its identifier already exists. If the application commits the earlier update anyway, inventory decreases without a new order. Atomicity has not guessed the intended checkout boundary for the application.

Use this control flow:

```text
begin transaction
try:
    reserve stock and check that one row changed
    create the order
    create the order item
    commit
on any failure:
    roll back
    report the failure or retry the complete operation when appropriate
```

Some engines abort a transaction after particular errors. Others reject only the failing statement. A transaction helper can enforce the rollback path, but swallowing an exception inside that helper may cause it to treat the operation as successful.

A condition that is false can also be a business failure without a database error. `UPDATE ... WHERE stock >= 1` can affect zero rows. Your code must turn that result into the rollback decision.

## How recovery supports atomicity

A crash can interrupt a transaction after some writes have reached storage. Databases use recovery information, such as a transaction log, to distinguish committed work from incomplete work. On restart, the engine applies its recovery procedure so unfinished transactions do not become partially committed results.

The exact mechanism depends on the engine. A **log** records recovery information; it is not the same thing as an application debug log. [Crash recovery](../11_security_best_practices/07_crash_recovery_in_databases.md) explains the storage details after the ACID foundations.

## Define what is inside the transaction

A database transaction generally covers the transactional operations on its participating database connection. It does not automatically cover another service, a file write, or a message sent to a broker. Some database operations and storage engines also have different rollback behavior.

For example, sending a confirmation email before commit risks announcing an order that later rolls back. Sending it after commit avoids that particular error, but a crash between commit and sending can leave the email unsent. A common design records a pending notification in the same transaction as the order, then lets a worker deliver it with retry and duplicate handling. This is often called a **transactional outbox**.

A **savepoint** marks a place for partial rollback inside a transaction. It helps recover from an optional step, but releasing it does not commit the surrounding transaction. The [SQL transaction control note](../03_sql/05_transaction_control_language_tcl.md) includes a runnable example.

## Check your understanding

1. What values do the two stock queries return, and why?
2. How can committing after a failed insert create an incomplete checkout?
3. Why can zero affected rows require rollback even when no exception was raised?
4. What does an outbox record put inside the transaction, and what work remains outside it?

Next: [Consistency](03_consistency.md) asks whether the complete operation leaves valid data.
