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

## Check your understanding

1. Why does `AFTER` not mean “after commit”?
2. What do `OLD` and `NEW` refer to during a price update?
3. Why does assigning the same price twice produce only one history row?
4. Does this table preserve a price change that was rolled back?
5. When would a default or constraint be clearer than a trigger?

Next: [hierarchical data](09_hierarchical_data.md) extends the table model to trees.
