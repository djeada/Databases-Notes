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

## Make a later constraint failure undo an earlier successful write

An invalid operation provides a stronger demonstration than rolling back a successful update by choice. This Python exercise creates its own in-memory database, so it does not depend on the bookstore:

```python
import sqlite3

connection = sqlite3.connect(':memory:')
connection.execute('PRAGMA foreign_keys = ON')
connection.executescript("""
CREATE TABLE atomic_stock (
    product_id INTEGER PRIMARY KEY,
    stock INTEGER NOT NULL CHECK (stock >= 0)
);
CREATE TABLE atomic_orders (
    order_id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES atomic_stock(product_id)
);
INSERT INTO atomic_stock VALUES (10, 5);
INSERT INTO atomic_orders VALUES (101, 10);
""")

try:
    with connection:
        connection.execute(
            'UPDATE atomic_stock SET stock = stock - 1 WHERE product_id = ?',
            (10,),
        )
        connection.execute(
            'INSERT INTO atomic_orders VALUES (?, ?)',
            (101, 10),  # Duplicate order ID: the insert fails.
        )
except sqlite3.IntegrityError:
    print('checkout rejected')

print(connection.execute('SELECT stock FROM atomic_stock').fetchone()[0])
print(connection.execute('SELECT COUNT(*) FROM atomic_orders').fetchone()[0])
connection.close()
```

The output is `checkout rejected`, then `5`, then `1`. The stock update reached 4 inside the transaction, but the duplicate insert raised an exception that escaped the context manager. The context therefore rolled back the whole pending operation. Catching the exception **inside** the context and continuing normally could cause the earlier update to commit under this connection mode.

The example uses Python's default SQLite transaction handling. It proves that the application has a rollback path for this failure. It does not test a power loss or prove every deployment setting is durable.

## Atomic writes can still need explicit business validation

If an update matches zero rows, the database usually treats the statement as successful execution. An absent product is not a syntax error. Likewise, transferring to a missing account can credit zero rows. The application must check affected-row counts or returned rows and raise a business failure that triggers rollback.

The [transaction control note](../03_sql/05_transaction_control_language_tcl.md) includes a complete transfer helper that checks both the debit and the credit. It also rejects nonpositive amounts and transfers to the same account. Atomicity supplies a unit of acceptance for that helper; those validations determine what the unit means.

A sequence or identity counter is another important boundary. PostgreSQL sequence increments are not rolled back with a failed transaction, and SQL Server identity values can also have gaps. Atomicity of the business rows does not imply that every internal counter returns to its previous value. Do not use missing order IDs as evidence that rows disappeared or that a transaction partially committed.

## Put notification intent inside an outbox

The outbox pattern stores the intent to notify alongside the accepted business record. These tables are independent of the bookstore:

```sql
CREATE TABLE atomic_checkouts (
    checkout_id INTEGER PRIMARY KEY,
    request_key TEXT NOT NULL UNIQUE,
    customer_name TEXT NOT NULL
);
CREATE TABLE atomic_outbox (
    message_id INTEGER PRIMARY KEY,
    checkout_id INTEGER NOT NULL REFERENCES atomic_checkouts(checkout_id),
    message_type TEXT NOT NULL,
    sent_at TEXT,
    UNIQUE (checkout_id, message_type)
);

BEGIN;
INSERT INTO atomic_checkouts VALUES (1, 'checkout-request-abc', 'Bob');
INSERT INTO atomic_outbox (message_id, checkout_id, message_type)
VALUES (1, 1, 'order_confirmation');
COMMIT;

SELECT c.request_key, o.message_type
FROM atomic_outbox AS o
JOIN atomic_checkouts AS c ON c.checkout_id = o.checkout_id
WHERE o.sent_at IS NULL
ORDER BY o.message_id;
```

The pending message is `checkout-request-abc, order_confirmation`. A failure before commit must roll back both records. A worker sees the committed pending record later, sends the notification, and then marks progress. A crash after sending but before marking progress can cause another send, so delivery needs duplicate tolerance or a stable message ID accepted by the recipient.

The unique request key helps recognize a retried checkout. It does not automatically return the first request's outcome: application code must look up the existing record and verify that a repeated key represents the same operation. The unique message pair prevents recording the same confirmation intent twice for one checkout.

For multiple workers, use the engine's appropriate claim or locking mechanism so they do not all process the same pending row at once. This SQLite example shows transactional recording, not a complete concurrent delivery queue.

## Two-phase commit coordinates multiple participants

A local transaction cannot ordinarily make two unrelated databases commit together. **Two-phase commit (2PC)** adds a coordinator and a durable decision:

1. Ask each participant to prepare. It records enough state to commit later and retains the necessary resources.
2. If all participants prepare, record and distribute the commit decision. Otherwise resolve the participants with an abort decision.

A participant that has prepared cannot simply guess the decision when the coordinator disappears. In-doubt prepared transactions can hold locks until recovery resolves them. This is a major operational cost, not merely two extra SQL statements.

PostgreSQL exposes a participant mechanism through prepared transactions. This optional example requires a disposable PostgreSQL instance configured with `max_prepared_transactions` greater than zero; it is commonly disabled by default. It demonstrates one participant, **not a complete distributed coordinator**:

```sql
-- PostgreSQL; prepared transactions must be enabled for this exercise
CREATE TABLE atomic_pg_events (event_id INTEGER PRIMARY KEY, description TEXT NOT NULL);
BEGIN;
INSERT INTO atomic_pg_events VALUES (1, 'prepared example');
PREPARE TRANSACTION 'notes_atomicity_demo';

SELECT gid FROM pg_prepared_xacts WHERE gid = 'notes_atomicity_demo';
COMMIT PREPARED 'notes_atomicity_demo';
SELECT event_id, description FROM atomic_pg_events;
```

Preparation ends the current transaction but leaves its outcome unresolved. The prepared-transaction view shows the identifier; `COMMIT PREPARED`, issued outside a transaction block by an authorized role, makes event 1 visible. `ROLLBACK PREPARED` is the alternative abort decision. Always resolve the exercise's prepared transaction; abandoning it can retain locks.

Two-phase **commit** coordinates a distributed acceptance decision. Two-phase **locking** is a concurrency-control protocol. Their similar names do not make them the same mechanism. When 2PC is unsuitable, a saga uses separately committed steps and compensating actions. Compensation is a new business action, such as issuing a refund; it is not a database rollback that erases every external effect.

References: [PostgreSQL prepared transactions](https://www.postgresql.org/docs/current/sql-prepare-transaction.html) and [PostgreSQL sequence behavior](https://www.postgresql.org/docs/current/functions-sequence.html).

## Check your understanding

1. What values do the two stock queries return, and why?
2. How can committing after a failed insert create an incomplete checkout?
3. Why can zero affected rows require rollback even when no exception was raised?
4. What does an outbox record put inside the transaction, and what work remains outside it?

Next: [Consistency](03_consistency.md) asks whether the complete operation leaves valid data.
