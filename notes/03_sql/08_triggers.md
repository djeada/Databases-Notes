# Triggers: Run Database Logic When Data Changes

A **trigger** is database logic invoked automatically by a specified event. Unlike a procedure, which a caller explicitly invokes, a trigger can run because an application inserts, updates, or deletes rows.

This note uses **SQLite** and the fresh [bookstore setup](01_intro_to_sql.md). We will record changes to product prices, then see what happens when the surrounding transaction rolls back.

## Begin with a reason for the extra behavior

Suppose staff can update prices through two different applications. Both should record the old and new price. If each application must remember an extra insert, one might forget. A database trigger can apply that behavior to updates from either application.

First create a table to hold the history:

```sql
CREATE TABLE product_price_changes (
    change_id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL,
    old_price_cents INTEGER NOT NULL,
    new_price_cents INTEGER NOT NULL,
    changed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

This example keeps the product identifier as historical information without a foreign key that would force a policy for later product deletion. It records price changes, not the identity of the human who caused them. Those are deliberate limits of this small example.

## Define an update trigger

```sql
CREATE TRIGGER record_product_price_change
AFTER UPDATE OF price_cents ON products
FOR EACH ROW
WHEN OLD.price_cents <> NEW.price_cents
BEGIN
    INSERT INTO product_price_changes
        (product_id, old_price_cents, new_price_cents)
    VALUES (NEW.product_id, OLD.price_cents, NEW.price_cents);
END;
```

Read the definition from top to bottom:

- `AFTER` specifies timing relative to the row update. It does not mean after transaction commit.
- `UPDATE OF price_cents` selects updates that mention this column.
- `FOR EACH ROW` makes the body run separately for each qualifying row.
- `OLD` contains the row's previous values; `NEW` contains its new values.
- `WHEN` excludes assignments that leave the price unchanged.
- `BEGIN ... END` groups the trigger's statements; it does not start an independent transaction.

Both prices are non-null in the bookstore schema, so `<>` is sufficient here. If nullable fields were allowed, the comparison would need a deliberate null policy. SQLite documents its trigger behavior and restrictions in [CREATE TRIGGER](https://www.sqlite.org/lang_createtrigger.html).

## Observe the extra write

```sql
UPDATE products SET price_cents = 1600 WHERE product_id = 10;

SELECT product_id, old_price_cents, new_price_cents
FROM product_price_changes
ORDER BY change_id;
```

| product_id | old_price_cents | new_price_cents |
|---|---|---|
| 10 | 1500 | 1600 |

The application issued an update to `products`; the trigger also inserted a history row. Repeating the same assignment does not create another history entry:

```sql
UPDATE products SET price_cents = 1600 WHERE product_id = 10;
SELECT COUNT(*) AS change_count FROM product_price_changes;
```

The count stays 1 because the `WHEN` condition is false.

## Trigger changes participate in rollback

Continue from the previous exercise, where the current price is 1600:

```sql
BEGIN;
UPDATE products SET price_cents = 1700 WHERE product_id = 10;
SELECT COUNT(*) AS change_count FROM product_price_changes;
ROLLBACK;
SELECT COUNT(*) AS change_count FROM product_price_changes;
SELECT price_cents FROM products WHERE product_id = 10;
```

The first count is 2 inside the transaction. After rollback, the count is 1 and the price is 1600. The trigger's inserted row rolls back with the price update.

Consequently, this history table records accepted changes, not every attempted change or rejected statement. A security audit of unsuccessful attempts needs a different logging design.

## Timing and scope vary by engine

| Choice | Meaning |
|---|---|
| `BEFORE` | Run before the affected row or statement is applied, where supported |
| `AFTER` | Run after the relevant change, generally still within its transaction |
| `INSTEAD OF` | Replace the requested operation, commonly for a view |
| Row trigger | Run for each affected row |
| Statement trigger | Run for the statement as a whole, where supported |

SQLite provides row triggers; other engines have different combinations and syntax. Do not paste a MySQL `SET NEW.column = ...` body into SQLite, or assume PostgreSQL trigger-function syntax works in every engine.

## Prefer the simplest rule mechanism

Use `NOT NULL`, `UNIQUE`, `CHECK`, or a foreign key when they express the rule directly. Use a column default for a straightforward initial timestamp. A trigger is useful when a data change genuinely requires additional database work.

The tradeoff is less visible behavior. An update may write several tables, acquire additional locks, or activate further triggers. Review multi-row updates, rollback behavior, and interactions with other triggers. Keep trigger code short and document the behavior beside the schema.

## Validate a transition when the old row matters

A row check can require an allowed status, but it cannot ordinarily express “a completed order must not return to open” using both the old and new versions. A SQLite trigger can reject that specific transition:

```sql
CREATE TRIGGER prevent_completed_order_reopening
BEFORE UPDATE OF status ON orders
FOR EACH ROW
WHEN OLD.status = 'completed' AND NEW.status = 'open'
BEGIN
    SELECT RAISE(ABORT, 'completed orders cannot be reopened');
END;
```

Run this **deliberately failing** statement separately:

```sql
-- Expected trigger error; not part of a successful script
UPDATE orders SET status = 'open' WHERE order_id = 101;
```

Order 101 remains completed. `RAISE(ABORT, ...)` aborts the statement; it does not mean that every earlier statement in an already open transaction has been rolled back. Application error handling still owns that larger boundary.

This rule prohibits one transition. It does not fully specify a state machine, and it does not validate refunds. If cancelled orders may never reopen either, declare that additional rule. Prefer a check for rules about one new row alone, and a trigger only when the old row or related work is essential.

## Supply writes through a SQLite view explicitly

SQLite views do not automatically accept writes. An `INSTEAD OF` trigger can give a view a narrow update interface:

```sql
CREATE VIEW trigger_product_prices AS
SELECT product_id, title, price_cents FROM products;

CREATE TRIGGER update_price_through_view
INSTEAD OF UPDATE OF price_cents ON trigger_product_prices
FOR EACH ROW
BEGIN
    UPDATE products
    SET price_cents = NEW.price_cents
    WHERE product_id = OLD.product_id;
END;

BEGIN;
UPDATE trigger_product_prices SET price_cents = 1800 WHERE product_id = 10;
SELECT product_id, price_cents FROM products WHERE product_id = 10;
SELECT COUNT(*) AS change_count FROM product_price_changes;
ROLLBACK;
```

Continuing the earlier price-history exercise, the intermediate price is 1800 and history count is 2. Updating the base table activates its existing audit trigger as well. The rollback returns the price to 1600 and count to 1. The view trigger chooses the old product ID as the target and only writes price; it is not a general-purpose implementation for every possible update to this view.

These nested effects are why readers of schema code need to know which triggers exist. A single visible update may touch several objects, and an error in the additional work can reject the original statement.

## Modify a new row using PostgreSQL's trigger function

PostgreSQL defines the trigger's behavior in a function returning `trigger`. Unlike SQLite's syntax, a PostgreSQL before-row function can assign fields in `NEW`:

```sql
-- PostgreSQL; independent setup
CREATE TABLE trigger_pg_notes (
    note_id INTEGER PRIMARY KEY,
    body TEXT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE FUNCTION trigger_pg_stamp_note()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at := statement_timestamp();
    RETURN NEW;
END;
$$;

CREATE TRIGGER stamp_note_update
BEFORE UPDATE ON trigger_pg_notes
FOR EACH ROW EXECUTE FUNCTION trigger_pg_stamp_note();

INSERT INTO trigger_pg_notes (note_id, body) VALUES (1, 'first draft');
UPDATE trigger_pg_notes SET body = 'revised draft' WHERE note_id = 1;
SELECT note_id, body, updated_at FROM trigger_pg_notes;
```

The row contains 1, revised draft, and the update statement's timestamp. The exact timestamp depends on execution time. `RETURN NEW` supplies the row version to write. `CURRENT_TIMESTAMP` in PostgreSQL represents the transaction's start time; using `statement_timestamp()` here deliberately records the statement's start instead. Neither timestamp is automatically a precise commit time.

A default handles the initial insert, while a trigger handles later updates. MySQL permits assignments with its own `SET NEW.column = ...` syntax in a before trigger. The same requirement can therefore have different executable forms across engines.

## Handle all affected rows in SQL Server

SQL Server DML triggers operate per statement. Its `inserted` and `deleted` tables can contain multiple rows. A trigger that picks one scalar value from them can miss changes during a bulk update. This independent example records every changed price with a set-based insert:

```sql
-- SQL Server; use SSMS or sqlcmd for GO
CREATE TABLE dbo.TriggerProducts (
    ProductId INT PRIMARY KEY,
    PriceCents INT NOT NULL
);
CREATE TABLE dbo.TriggerPriceHistory (
    ProductId INT NOT NULL,
    OldPriceCents INT NOT NULL,
    NewPriceCents INT NOT NULL
);
INSERT INTO dbo.TriggerProducts VALUES (10, 1500), (20, 2500);
GO
CREATE TRIGGER dbo.RecordTriggerPrices
ON dbo.TriggerProducts
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO dbo.TriggerPriceHistory (ProductId, OldPriceCents, NewPriceCents)
    SELECT i.ProductId, d.PriceCents, i.PriceCents
    FROM inserted AS i
    JOIN deleted AS d ON d.ProductId = i.ProductId
    WHERE i.PriceCents <> d.PriceCents;
END;
GO
UPDATE dbo.TriggerProducts SET PriceCents = PriceCents + 100;
SELECT ProductId, OldPriceCents, NewPriceCents
FROM dbo.TriggerPriceHistory ORDER BY ProductId;
GO
```

The history has `(10, 1500, 1600)` and `(20, 2500, 2600)`. The join assumes product IDs are stable during the update. A mutable primary key requires a different matching policy. The trigger handles the statement's full set without a cursor.

## Manage trigger lifecycle and cost

SQLite changes an existing trigger by dropping and recreating it. PostgreSQL and SQL Server provide different replace or alter mechanisms. For the SQLite practice rule, cleanup is:

```sql
-- SQLite
DROP TRIGGER prevent_completed_order_reopening;
```

This removes the transition check, not the orders. Version that definition with the schema so every environment has the same behavior. Avoid assuming the firing order of several triggers supplies a reliable workflow unless the engine explicitly supports and defines that order.

Triggers add work to the original statement. Audit inserts need space, indexes require maintenance, and cross-table updates acquire more locks. Recursive trigger behavior is also configurable or restricted by the engine. Test a multi-row change, a no-op update, a failure in the trigger body, and outer rollback. Long network calls and irreversible external effects are poor trigger responsibilities; recording an outbox row keeps the database-side intent transactional.

References: [PostgreSQL trigger functions](https://www.postgresql.org/docs/current/plpgsql-trigger.html) and [SQL Server multirow triggers](https://learn.microsoft.com/en-us/sql/relational-databases/triggers/create-dml-triggers-to-handle-multiple-rows-of-data).

## Check your understanding

1. Why does `AFTER` not mean “after commit”?
2. What do `OLD` and `NEW` refer to during a price update?
3. Why does assigning the same price twice produce only one history row?
4. Does this table preserve a price change that was rolled back?
5. When would a default or constraint be clearer than a trigger?

Next: [hierarchical data](09_hierarchical_data.md) extends the table model to trees.
