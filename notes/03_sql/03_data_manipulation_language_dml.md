# DML: Read, Add, Change, and Remove Rows

**Data Manipulation Language (DML)** works with table data. `SELECT` reads rows, `INSERT` adds them, `UPDATE` changes them, and `DELETE` removes them. The table's structure remains in place unless a separate schema-changing command alters it.

Use the SQLite bookstore setup from the [SQL introduction](01_intro_to_sql.md). The write examples below are independent exercises wrapped in a transaction and rolled back, so they do not leave the sample database changed. A transaction is a group of database work; [TCL](05_transaction_control_language_tcl.md) explains it in detail.

## Read only the data you need

```sql
SELECT product_id, title, stock
FROM products
WHERE stock = 0
ORDER BY product_id;
```

The result is product 30, History of Computing, with stock zero. `WHERE` chooses rows, while the `SELECT` list chooses columns.

`SELECT *` requests all columns. That can be convenient while exploring, but listing needed columns makes application expectations clearer and avoids transferring unused data.

## Add a row with INSERT

```sql
BEGIN;

INSERT INTO customers (customer_id, name, email)
VALUES (4, 'Dana', 'dana@example.com');

SELECT customer_id, name FROM customers WHERE customer_id = 4;

ROLLBACK;
```

The select sees Dana because a transaction sees its own writes. The rollback removes that uncommitted insert. After the exercise, only the original three customers remain.

The column list and value list correspond by position: 4 goes into `customer_id`, Dana into `name`, and the email into `email`. Explicit column lists make that correspondence visible and reduce dependence on a table's column order.

Inserting an existing customer ID or duplicate required email violates a declared rule and is rejected. A successful insert creates a row; it does not automatically send a welcome email or validate email ownership.

## Change a targeted row with UPDATE

```sql
BEGIN;

UPDATE products
SET price_cents = 1600
WHERE product_id = 10;

SELECT product_id, price_cents FROM products WHERE product_id = 10;

ROLLBACK;
```

Product 10 temporarily has a current price of 1600 cents. The rollback restores 1500. Existing order-item purchase prices do not change: they describe the amount charged at purchase time, not the product's current offer.

`SET` specifies the new value. `WHERE` specifies which rows receive it. Omitting `WHERE` applies the update to every row. That is valid for an intentional bulk change, but disastrous for an operation intended to affect one product.

## Use current values for a relative change

```sql
BEGIN;

UPDATE products
SET stock = stock + 2
WHERE product_id = 10;

SELECT stock FROM products WHERE product_id = 10;

ROLLBACK;
```

Stock temporarily becomes seven. The database calculates the new value from the row's current value. This is preferable to unnecessarily reading five into application code and later writing a stale calculated value.

For a limited-stock purchase, the condition matters too:

```sql
UPDATE products
SET stock = stock - 1
WHERE product_id = 30 AND stock > 0;
```

Product 30 has zero stock, so this affects **zero rows**. It is not a SQL error. The application must inspect the affected-row count and avoid recording a sale when the decrement did not happen.

## Remove a row with DELETE

Try deletion on a newly inserted practice customer:

```sql
BEGIN;

INSERT INTO customers (customer_id, name, email)
VALUES (4, 'Dana', 'dana@example.com');

DELETE FROM customers WHERE customer_id = 4;
SELECT customer_id FROM customers WHERE customer_id = 4;

ROLLBACK;
```

The select returns no rows. The customer table still exists. Deleting a customer with referenced orders is different: the foreign-key policy decides whether the deletion is rejected or another declared action happens.

## Distinguish the common outcomes

| Outcome | Meaning | Application response |
| --- | --- | --- |
| One target row changed | The statement found and modified the intended record, subject to engine count semantics. | Continue after validating the workflow. |
| Zero rows affected | No qualifying row was changed. | Decide whether this means missing data, no stock, or a conflict. |
| Constraint error | The proposed change violates a declared rule. | Explain the problem and handle the surrounding transaction. |
| Connection lost during commit | The client may not know whether work committed. | Resolve the outcome using a stable request ID or another safe protocol. |

Success at the SQL statement level is not always success at the business-operation level. A zero-row update is the simplest example of that distinction.

## Check your understanding

1. What does the sample contain after each rolled-back exercise?
2. Why does changing a current product price leave past purchase prices alone?
3. What happens if an update intended for product 10 has no `WHERE` clause?
4. Why must a sale attempt check the affected-row count?

Continue with [permissions](04_data_control_language_dcl.md) to decide who may perform these operations, and [transactions](05_transaction_control_language_tcl.md) to group related changes.
