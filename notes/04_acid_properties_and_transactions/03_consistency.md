# Consistency: Preserve the Rules That Make Data Valid

In ACID, **consistency** means that correct transactions take the database from a valid state to another valid state. A valid state satisfies the system's required rules. The database enforces declared constraints; the application must correctly implement rules that are not fully expressed by those constraints.

This use of “consistency” concerns valid data. [Eventual consistency](../06_distributed_databases/07_eventual_consistency.md) concerns when separate copies agree. The same word describes different questions.

## Name the rules before choosing a mechanism

For the bookstore, “the data should be correct” is too vague. These rules are specific enough to test:

| Rule | Possible enforcement |
|---|---|
| Every customer has a distinct email | `UNIQUE` and `NOT NULL` |
| Each order references an existing customer | `FOREIGN KEY` and `NOT NULL` |
| Stock cannot be negative | `CHECK (stock >= 0)` and `NOT NULL` |
| A purchased quantity is positive | `CHECK (quantity > 0)` and `NOT NULL` |
| A successful checkout records both its stock change and its items | Correct transaction logic |

A **constraint** is a rule declared in the schema that the database checks when data changes. An **invariant** is any condition that must remain true as the system operates. An invariant may be implemented by a constraint, transaction logic, or both.

## Test a declared rule

Use the fresh [bookstore setup](../03_sql/01_intro_to_sql.md). Product 10 starts with stock 5 and has a nonnegative-stock constraint.

```sql
UPDATE products SET stock = -1 WHERE product_id = 10;
```

This statement is deliberately invalid. SQLite rejects it with a check-constraint failure; it does not store stock -1. Run it on its own, rather than including it in a script expected to complete successfully.

```sql
SELECT stock FROM products WHERE product_id = 10;
```

The value is still 5. The constraint protects this rule even if an application sends a bad update.

`CHECK (stock >= 0)` alone does not reject `NULL` in SQL: a check generally rejects a false result, while an unknown result is allowed. `NOT NULL` supplies the separate requirement that a value be present. Likewise, foreign-key enforcement must actually be enabled; the SQLite setup uses `PRAGMA foreign_keys = ON` for each connection.

## A valid row can still belong to an invalid workflow

Consider decreasing stock by one and committing without creating an order. Every remaining row may satisfy its keys and checks. Nevertheless, the checkout's business rule has been violated.

The engine cannot infer that every stock reduction must correspond to a sale: stock might also decrease because a damaged book was removed. The application needs a clearly defined operation, the right transaction boundary, and suitable concurrency control.

**Atomicity** makes changes an all-or-nothing unit. **Consistency** asks whether that unit performs a valid change. A transaction can atomically deduct the wrong quantity.

## A check followed by a write can race

Suppose one copy remains. Two transactions each read stock 1 and independently decide that a sale is allowed. Their decisions were based on data that can change before they write.

For a simple stock reservation, combine the condition and modification:

```sql
UPDATE products
SET stock = stock - 1
WHERE product_id = 10 AND stock >= 1;
```

Continue only if one row changed. Handle any concurrency failure according to the engine and retry policy. Keep the order inserts in the same transaction. This avoids relying on an earlier, separate availability check.

More complex invariants can span multiple rows. For example, limiting a customer's total unpaid orders cannot generally be enforced by an ordinary row-level `CHECK`. The design may require a different schema, explicit locking, or serializable isolation with retries. See [Isolation](04_isolation.md) and the [double booking problem](../07_concurrency_control/04_double_booking_problem.md).

## Translate a seat rule into a unique key

For a cinema, “a seat cannot be booked twice” means within the same screening, not across all screenings. Use a composite uniqueness rule in an independent SQLite table:

```sql
CREATE TABLE consistency_bookings (
    booking_id INTEGER PRIMARY KEY,
    screening_id INTEGER NOT NULL,
    seat_code TEXT NOT NULL,
    customer_name TEXT NOT NULL,
    UNIQUE (screening_id, seat_code)
);
INSERT INTO consistency_bookings VALUES
    (1, 100, 'A1', 'Alice'),
    (2, 101, 'A1', 'Bob');
SELECT screening_id, seat_code FROM consistency_bookings ORDER BY screening_id;
```

Both rows are valid: A1 can be sold once for screening 100 and once for screening 101. A second A1 booking for screening 100 would fail, even if two applications attempted it concurrently. The key encodes the scope of the invariant. A uniqueness rule on `seat_code` alone would prohibit legitimate sales at later screenings.

An application can check availability to give useful feedback, but the uniqueness constraint remains the authority at write time. Another transaction can book the seat between a display query and the attempted insert. Handle the conflict as “seat unavailable,” and roll back any associated database changes such as a reservation charge record.

This table does not validate whether A1 exists in the screening's auditorium. That requires a seat model and appropriate references. Constraints enforce the rules you declare; they do not fill in missing business definitions.

## Detect a stale edit with a version column

A catalog editor can read version 1, make changes in a browser, and submit them after another editor has already saved version 2. A version condition detects that obsolete decision:

```sql
CREATE TABLE consistency_catalog (
    product_id INTEGER PRIMARY KEY,
    price_cents INTEGER NOT NULL CHECK (price_cents >= 0),
    version INTEGER NOT NULL CHECK (version > 0)
);
INSERT INTO consistency_catalog VALUES (10, 1500, 1);

UPDATE consistency_catalog
SET price_cents = 1600, version = version + 1
WHERE product_id = 10 AND version = 1;

UPDATE consistency_catalog
SET price_cents = 1700, version = version + 1
WHERE product_id = 10 AND version = 1;

SELECT product_id, price_cents, version FROM consistency_catalog;
```

The first update changes one row; the second changes zero. The final row is `(10, 1600, 2)`. Both proposed prices satisfy the nonnegative-price check. The version condition enforces a different rule: do not overwrite a change made since the editor's read.

The application must inspect the affected-row count and report the conflict or reload data. A zero-row outcome should not be described as a saved edit. This is **optimistic concurrency control** at the application level; the database still coordinates the actual write. Every editing path must follow the version protocol, or an administrative update can bypass it.

## A cross-row invariant needs a cross-row design

A warehouse ledger can express “current stock equals the sum of movements.” Use an independent movement table where receipts are positive and dispatches negative:

```sql
CREATE TABLE consistency_movements (
    movement_id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,
    quantity_delta INTEGER NOT NULL CHECK (quantity_delta <> 0),
    reason TEXT NOT NULL
);
INSERT INTO consistency_movements VALUES
    (1, 10, 5, 'opening stock'),
    (2, 10, -1, 'sale'),
    (3, 10, 2, 'delivery');

SELECT product_id, SUM(quantity_delta) AS calculated_stock
FROM consistency_movements
GROUP BY product_id
ORDER BY product_id;
```

The derived stock is 6. This ledger preserves reasons and provides a way to reconstruct quantity. It does not yet prevent a dispatch that drives the total negative: an ordinary check on one movement cannot sum the other rows safely under concurrent writers.

One approach retains a current-stock row and conditionally decrements it in the same transaction that inserts a dispatch movement. Receipts increment the current-stock row and insert their movement together. A reconciliation query compares the cache with the ledger sum. This adds a redundancy invariant, so every writing path must maintain both representations. Another design derives stock entirely from movements but needs a concurrency strategy for admitting new dispatches.

Do not assume a trigger that reads a sum is automatically safe against another simultaneous trigger. The locking or isolation strategy must protect the same logical product across competing dispatches.

## Distinguish transaction-end validity from intermediate work

A workflow may temporarily create a reference before its target is inserted. With a deferrable foreign key, the database can check that relationship at commit rather than immediately. The [integrity note](../02_database_design/05_data_integrity.md) shows a complete SQLite example. Deferral changes the checking time; it does not mean the final state may contain missing parents.

Likewise, a transfer temporarily reduces one account before increasing the other. Other sessions should not observe an accepted half-transfer, and the application must not commit before both results are validated. A sum-of-balances invariant also needs a defined scope: fees, external deposits, and withdrawals can legitimately change that sum if they are part of the model.

## Validate data coming from less trusted paths

A user interface may reject invalid input, yet bulk imports, background jobs, and maintenance scripts can bypass that interface. Database constraints give those paths shared enforcement. Stage a large import, validate duplicates and references, then promote accepted data transactionally. Disabling constraints for speed is not equivalent to proving that the imported state is valid.

Consistency checks should also distinguish a true violation from incomplete information. A null delivery date might mean “not shipped yet,” while a negative item quantity may be impossible in an order table. Using a refund or movement table for returns can be clearer than overloading an order quantity with two unrelated meanings.

A consistent state is defined by the model and its invariants. If the model forgets a required relationship, perfectly executed transactions can preserve an inadequate definition. Requirements analysis, schema design, transaction logic, and concurrent tests therefore work together.

## Check your understanding

1. Why are `CHECK` and `NOT NULL` separate requirements?
2. Can a database satisfy every declared constraint while a checkout is still wrong?
3. What changes when the stock test becomes part of the update?
4. How does ACID consistency differ from replicas eventually agreeing?

Next: [Isolation](04_isolation.md) explains what concurrent transactions can observe.
