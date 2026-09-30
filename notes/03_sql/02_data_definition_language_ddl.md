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

## Inspect the schema before changing it

SQLite stores the definitions of tables, indexes, views, and triggers in `sqlite_schema`. Use it to check what exists rather than guessing from an application model:

```sql
SELECT name, type
FROM sqlite_schema
WHERE name IN ('orders', 'order_items', 'idx_orders_customer')
ORDER BY type, name;

PRAGMA table_info(order_items);
PRAGMA foreign_key_list(order_items);
PRAGMA index_list(order_items);
```

The first result contains the customer index and the two tables. The pragmas show column declarations, references to orders and products, and indexes on order lines. `table_info` includes the column's type, nullability, default, and position in a primary key. These are definitions, not a list of the rows currently stored.

PostgreSQL and MySQL expose much of this metadata through `information_schema`; SQL Server also has `sys` catalog views. Their schemas are not identical, so use the catalog intended for the engine you are inspecting.

## Rehearse a small migration from old data to new data

Use a separate table so this exercise does not change the bookstore:

```sql
CREATE TABLE ddl_contacts (
    contact_id INTEGER PRIMARY KEY,
    full_name TEXT NOT NULL
);
INSERT INTO ddl_contacts VALUES (1, 'Alice Smith'), (2, 'Bob Jones');

BEGIN;
ALTER TABLE ddl_contacts ADD COLUMN display_name TEXT;
UPDATE ddl_contacts SET display_name = full_name;
SELECT contact_id, display_name FROM ddl_contacts ORDER BY contact_id;
COMMIT;
```

The result is Alice Smith and Bob Jones under the new column. The migration has three responsibilities: introduce a place to store the new value, supply values for existing rows, and decide when the application starts reading or writing that place. A backfill alone does not keep future writes synchronized. If old application versions still write only `full_name`, the migration plan must handle those writers too.

For a rename rather than a new fact, modern SQLite supports:

```sql
ALTER TABLE ddl_contacts RENAME COLUMN full_name TO legal_name;
ALTER TABLE ddl_contacts RENAME TO ddl_customer_contacts;
SELECT contact_id, legal_name, display_name
FROM ddl_customer_contacts
ORDER BY contact_id;
```

Both names still contain the original values. Renaming preserves the fact; it changes how code refers to it. Update application queries and examine views, triggers, reports, and migration tooling that depend on the old name.

SQLite added `RENAME COLUMN` in 3.25.0 and `DROP COLUMN` in 3.35.0. Dropping a column can fail when constraints or dependent objects still require it. Check the deployed version and dependencies before selecting a migration command. Older or more complex SQLite changes may require the documented create-copy-drop-rename procedure, preserving indexes, triggers, and foreign keys explicitly.

## Rebuild a table to strengthen a rule

The new contact names are all populated. SQLite 3.53.0 added `ALTER TABLE ... ALTER COLUMN ... SET NOT NULL`. For older supported SQLite versions, or a more extensive definition change, create the intended definition and copy validated data into it. The following exercise uses that broadly compatible rebuild procedure. This practice table has no incoming foreign keys or dependent views:

```sql
BEGIN;
CREATE TABLE ddl_contacts_required (
    contact_id INTEGER PRIMARY KEY,
    legal_name TEXT NOT NULL,
    display_name TEXT NOT NULL
);
INSERT INTO ddl_contacts_required (contact_id, legal_name, display_name)
SELECT contact_id, legal_name, display_name
FROM ddl_customer_contacts;
DROP TABLE ddl_customer_contacts;
ALTER TABLE ddl_contacts_required RENAME TO ddl_customer_contacts;
COMMIT;

SELECT contact_id, display_name
FROM ddl_customer_contacts
ORDER BY contact_id;
```

The two contacts survive. If the copy encounters a null display name, the `NOT NULL` constraint rejects it; the client should roll back the transaction. In a real schema, this shortened example is insufficient when other tables reference the rebuilt table. Use SQLite's full documented procedure and run `PRAGMA foreign_key_check` afterward.

In PostgreSQL, changing nullability can instead use `ALTER TABLE ... ALTER COLUMN ... SET NOT NULL`. The shorter command still needs a valid population and may need locking or a validation strategy on a large table. Syntax convenience does not remove the migration's data obligations.

## Create a view and remove only its access path

A **view** stores a query definition. An **index** stores an access structure. Neither is a new customer or order:

```sql
CREATE VIEW ddl_available_products AS
SELECT product_id, title, price_cents
FROM products
WHERE stock > 0;

SELECT title FROM ddl_available_products ORDER BY product_id;

CREATE INDEX ddl_products_by_price ON products (price_cents);
DROP INDEX ddl_products_by_price;
DROP VIEW ddl_available_products;
```

The view returns Database Basics and SQL Practice. Dropping the index leaves every product intact. Dropping the view removes the saved query, also leaving the products intact. Dependency rules differ: an engine may refuse to drop a referenced object or offer a cascading drop. Read the dependency list before accepting a cascade.

## Treat defaults, checks, and unique constraints as separate rules

A default supplies a value when a column is omitted. It does not prohibit other values. A check tests values in a row. A unique constraint compares values across rows. These mechanisms solve different problems:

```sql
CREATE TABLE ddl_delivery_methods (
    method_id INTEGER PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    fee_cents INTEGER NOT NULL DEFAULT 0 CHECK (fee_cents >= 0)
);
INSERT INTO ddl_delivery_methods (method_id, code)
VALUES (1, 'pickup');
SELECT code, fee_cents FROM ddl_delivery_methods;
```

The result is `pickup, 0`. A negative explicit fee would fail the check; repeating `pickup` would fail uniqueness. Without `NOT NULL`, a check such as `fee_cents >= 0` would not by itself reject a null, because SQL checks accept an unknown result. A definition should express both presence and validity when the requirement needs both.

Use stable keys for relationships. A display name can change or be shared; a primary key must still identify one row. An autogenerated key alone does not enforce a separate business rule such as “one delivery method per code,” which is why this table has both a primary key and a unique code.

## Plan changes around readers and writers

A migration that rewrites a large table or builds an index can consume disk, generate transaction logs, and hold locks. PostgreSQL's `CREATE INDEX CONCURRENTLY` reduces some blocking but has its own restrictions and failure cleanup; it cannot run inside a transaction block. MySQL's supported online DDL operations depend on the operation and engine. Do not translate “online” into “no effect on live traffic.”

For a required field, a common sequence is: add a compatible optional field, deploy writers, backfill old rows in controlled batches, verify completeness, then enforce the requirement. Keep the invariant explicit at each step. If restoring the previous application would no longer understand the new schema, an application rollback and a database rollback are different recovery plans.

References: [SQLite ALTER TABLE](https://www.sqlite.org/lang_altertable.html), [SQLite schema table](https://www.sqlite.org/schematab.html), and [PostgreSQL CREATE INDEX](https://www.postgresql.org/docs/current/sql-createindex.html).

## Check your understanding

1. Why is a table empty immediately after `CREATE TABLE`?
2. What does adding a default decide for omitted values, and what business assumption might it hide?
3. How is deleting every row different from dropping the table?
4. Why is adding a required column to existing data harder than defining it on a new empty table?

Continue with [DML](03_data_manipulation_language_dml.md), which works with rows under these definitions.
