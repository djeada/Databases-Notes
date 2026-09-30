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

## Transform values in a result before deciding to store them

A scalar function works on a value in each row. It does not combine an entire group like `SUM` does:

```sql
SELECT customer_id,
       UPPER(name) AS mailing_label,
       LOWER(email) AS email_label
FROM customers
ORDER BY customer_id;

SELECT product_id,
       CASE WHEN stock = 0 THEN 'unavailable' ELSE 'available' END AS availability
FROM products
ORDER BY product_id;
```

The first query displays ALICE, BOB, and CAROL. The second labels product 30 unavailable and the others available. The stored names and stock values are unchanged. `CASE` chooses one result according to a condition; it is useful for report labels without introducing redundant stored columns.

SQLite's built-in case conversions are not a complete solution for every language's Unicode rules. Normalizing email addresses also requires an application policy rather than an assumption that all text can safely be lowercased.

`TRIM` removes surrounding characters, `CAST` asks for a conversion, and `COALESCE` provides a fallback for null. Converting malformed input to a number is not validation: SQLite can turn some invalid numeric text into zero. Validate the source and choose suitable column rules before writing data.

## Insert a result set, not just literal rows

A report snapshot can collect several rows with one command:

```sql
CREATE TABLE dml_stock_snapshot (
    product_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    stock INTEGER NOT NULL,
    captured_on TEXT NOT NULL
);
INSERT INTO dml_stock_snapshot (product_id, title, stock, captured_on)
SELECT product_id, title, stock, '2025-01-13'
FROM products
WHERE stock > 0;

SELECT product_id, stock FROM dml_stock_snapshot ORDER BY product_id;
```

The result contains product 10 with 5 units and product 20 with 8. `INSERT ... SELECT` inserts the rows returned by its source query; it does not create a continuing link to the source. A later inventory update will not rewrite this snapshot. That is correct only if the table means “stock captured at this time.” For repeated snapshots, include the capture identifier in the key rather than overwriting history accidentally.

Specify the destination columns. Relying on every column's current physical order makes an import fragile when the table definition changes. The number and meanings of the selected expressions must match those destination columns.

## Handle an existing key deliberately

SQLite supports an upsert: insert a row, or update it when a specified unique key conflicts. This is useful for synchronizing a supplier's current catalog:

```sql
CREATE TABLE dml_supplier_catalog (
    supplier_sku TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    price_cents INTEGER NOT NULL CHECK (price_cents >= 0)
);
INSERT INTO dml_supplier_catalog VALUES ('BK-10', 'Database Basics', 1500);

INSERT INTO dml_supplier_catalog (supplier_sku, title, price_cents)
VALUES ('BK-10', 'Database Basics, revised', 1600)
ON CONFLICT (supplier_sku) DO UPDATE
SET title = excluded.title,
    price_cents = excluded.price_cents;

SELECT supplier_sku, title, price_cents FROM dml_supplier_catalog;
```

There is one row: BK-10, Database Basics, revised, 1600. `excluded` refers to the proposed insert's values. The conflict target must correspond to a primary key or uniqueness rule. This update policy accepts the incoming source as current; a real integration may also need a version or timestamp to prevent an older message replacing newer data.

SQLite's `INSERT OR REPLACE` is not interchangeable with an update. It can delete a conflicting row and insert a replacement, affecting references, triggers, and generated identifiers. PostgreSQL also has `ON CONFLICT`, while MySQL has different upsert syntax. Check the engine's exact behavior before porting synchronization code.

## Get values from the write itself

SQLite 3.35.0 and later support `RETURNING`:

```sql
BEGIN;
UPDATE products
SET stock = stock - 1
WHERE product_id = 10 AND stock > 0
RETURNING product_id, stock;
ROLLBACK;
```

The update returns `10, 4`, then the rollback restores 5 units. Returning the affected row avoids a separate query just to discover the direct change. No returned row means this statement found no qualifying product. It does not tell you whether the product was missing or out of stock; decide whether the application needs to distinguish those cases.

`RETURNING` reports rows changed directly by this statement. It is not a general report of all changes made by triggers. PostgreSQL supports a similar clause; SQL Server uses `OUTPUT` for related purposes.

## Understand how null changes a condition

Use a separate optional-contact table:

```sql
CREATE TABLE dml_optional_contacts (
    contact_id INTEGER PRIMARY KEY,
    phone TEXT
);
INSERT INTO dml_optional_contacts VALUES (1, NULL), (2, ''), (3, '12345');

SELECT contact_id FROM dml_optional_contacts WHERE phone IS NULL;
SELECT contact_id FROM dml_optional_contacts WHERE phone = '';
SELECT contact_id FROM dml_optional_contacts WHERE phone <> '12345';
```

The first returns 1, the second 2, and the third only 2. A null phone does not satisfy `phone <> '12345'`; that comparison is unknown. If the business question includes missing phones, write `phone IS NULL OR phone <> '12345'` explicitly. Replacing nulls with empty strings silently erases the distinction between “unknown” and “known to be empty.”

The same issue affects `NOT IN` when its list or subquery contains a null. An anti-match with `NOT EXISTS` is often clearer, as demonstrated in the joins note.

## Bind values and check the write's outcome

This Python helper assumes an existing SQLite connection containing the bookstore. Call it when that connection has no unrelated transaction in progress:

```python
def change_price(connection, product_id, price_cents):
    if not isinstance(price_cents, int) or price_cents < 0:
        raise ValueError('price must be nonnegative integer cents')
    with connection:
        cursor = connection.execute(
            'UPDATE products SET price_cents = ? WHERE product_id = ?',
            (price_cents, product_id),
        )
        if cursor.rowcount != 1:
            raise ValueError('product does not exist')
```

With Python's default SQLite transaction handling, the context commits a successful write and rolls it back when the exception escapes. It does not close the connection. Custom autocommit settings change that behavior; use the connection configuration described in the transaction note.

The application validates the intended unit and reports a missing product. The database check remains useful because imports, other services, and administrative tools can write through different paths. Neither layer substitutes for the other. An expected uniqueness conflict, an unavailable connection, and invalid input also deserve different handling; catching every error and claiming success loses that information.

References: [SQLite UPSERT](https://www.sqlite.org/lang_upsert.html) and [SQLite RETURNING](https://www.sqlite.org/lang_returning.html).

## Check your understanding

1. What does the sample contain after each rolled-back exercise?
2. Why does changing a current product price leave past purchase prices alone?
3. What happens if an update intended for product 10 has no `WHERE` clause?
4. Why must a sale attempt check the affected-row count?

Continue with [permissions](04_data_control_language_dcl.md) to decide who may perform these operations, and [transactions](05_transaction_control_language_tcl.md) to group related changes.
