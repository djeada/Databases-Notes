# DDL: Define and Change the Database Structure

**Data Definition Language (DDL)** defines database objects. A table definition says which columns exist, what kinds of values they accept, and which rules apply. It is different from inserting the current rows into that table.

This note assumes you have worked through the [SQL introduction](01_intro_to_sql.md). Examples use SQLite unless another engine is named. The existing bookstore tables remain available.

## Read a table definition

This creates a separate practice table:

```sql
CREATE TABLE suppliers (
    supplier_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE
);
```

Read each line as a declaration. `supplier_id` identifies a supplier. `name` is required text. Email is optional but subject to SQLite's unique-value rules when provided. An empty table now exists; no supplier row has been created yet.

The **data type** describes the intended kind of value, such as integer or text. The **constraint** describes a rule, such as required or unique. Type behavior differs by engine: SQLite ordinary tables are more permissive than PostgreSQL tables.

## Choose types from meaning

| Fact | A possible representation | Reason |
| --- | --- | --- |
| Supplier identifier | Integer | A stable reference to a supplier. |
| Name | Text | Words rather than numeric arithmetic. |
| Quantity | Integer plus a positive check | A count of whole units. |
| Price | Integer cents in this tutorial | Exact arithmetic in the chosen smallest currency unit. |
| Date | ISO-formatted text in this SQLite tutorial | A consistent representation; the text type alone does not validate dates. |

A phone number is usually text: leading zeros and a plus sign matter, and adding two phone numbers is meaningless. Choose types from the operations and rules needed, rather than from the appearance of one sample.

## Give new rows a default

Add a country column with an explicit default for this exercise:

```sql
ALTER TABLE suppliers
ADD COLUMN country_code TEXT NOT NULL DEFAULT 'DE';
```

`ALTER TABLE` changes the definition of an existing table. Omitting country on a later insert uses `DE`; existing rows also need a defined treatment during such changes. In a real migration, do not assign a country merely because a default makes the command convenient.

Add a row and inspect it:

```sql
INSERT INTO suppliers (supplier_id, name, email)
VALUES (1, 'Example Books', 'orders@example.com');

SELECT supplier_id, name, country_code
FROM suppliers;
```

The country is `DE`. Changing a column's default later does not generally rewrite all explicitly stored historical values.

## Connect tables with a foreign key

An order's customer is declared as:

```sql
-- Declaration fragment, shown inside a table definition:
customer_id INTEGER NOT NULL REFERENCES customers(customer_id)
```

`REFERENCES` says which existing identifier must match. It is not a join command. The DBMS checks validity during writes; a query must still request a join to display the customer's name.

SQLite requires foreign-key enforcement to be enabled on each connection. Other engines have their own rules for adding and validating constraints on populated tables.

## Add an access path

```sql
CREATE INDEX idx_orders_customer ON orders (customer_id);
```

An index helps some queries find rows. It does not add a new business record or change what an order means. It also consumes space and adds maintenance work during writes.

Use [indexing strategies](../02_database_design/04_indexing_strategies.md) to decide whether an index supports a measured access pattern.

## Remove data or remove the object?

These operations have different scopes:

| Operation | Meaning |
| --- | --- |
| `DELETE FROM suppliers;` | Remove the supplier rows; retain the table definition. |
| `DROP TABLE suppliers;` | Remove the table object and its data. |
| `TRUNCATE TABLE suppliers;` | Engine-specific whole-table removal; SQLite does not support this statement. |

For this practice table, cleanup is:

```sql
DROP TABLE suppliers;
```

A real application migration should consider readers, writers, dependencies, and recoverability before dropping an object.

## Why production changes need a migration

A **migration** is a controlled change from the current schema to a new one. Adding a required column to a table with existing rows raises a question: where will those existing values come from?

One approach is to add an optional column, fill its values with a **backfill**, update application writers, validate the data, and then require the value using the chosen engine's supported procedure. Large backfills and constraint checks can take time or block work.

The migration must describe the existing data, the new rule, how writers remain compatible during the transition, and how failures are handled. Merely showing a fresh `CREATE TABLE` does not explain changing a live system.

## Transaction behavior differs by engine

SQLite supports transactional schema changes with documented restrictions. PostgreSQL supports rollback for most DDL, while commands such as `CREATE DATABASE` cannot run inside a transaction block. MySQL DDL commonly causes implicit commits.

An **implicit commit** means the engine commits without the application issuing `COMMIT` at that point. Therefore, do not assume a later rollback will undo every schema change and surrounding write in every engine.

## Check your understanding

1. Why is a table empty immediately after `CREATE TABLE`?
2. What does adding a default decide for omitted values, and what business assumption might it hide?
3. How is deleting every row different from dropping the table?
4. Why is adding a required column to existing data harder than defining it on a new empty table?

Continue with [DML](03_data_manipulation_language_dml.md), which works with rows under these definitions.
