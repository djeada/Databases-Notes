# Data Integrity: Put the Rules in the Database

**Data integrity** means the stored data satisfies the rules the system relies on. A **constraint** is a rule declared in a table's definition so the database can check it whenever relevant data changes.

For the bookstore, an order should reference a real customer, a quantity should be positive, and a customer email should not duplicate another required email. The application can explain these rules to users, while database constraints protect them across different writers.

## Translate plain-language rules into declarations

| Requirement | Database declaration | What it checks |
| --- | --- | --- |
| Each customer has an identifier. | `PRIMARY KEY` | The identifier is unique and required, with engine-specific legacy exceptions. |
| Every customer supplies an email. | `NOT NULL` | The value is not the SQL missing-value marker. |
| Required emails cannot repeat. | `UNIQUE` with `NOT NULL` | Another row cannot store the same email under the chosen comparison rules. |
| An order points to a customer. | `FOREIGN KEY` | Referencing values match an eligible referenced key. |
| Quantity is positive. | `CHECK (quantity > 0)` with `NOT NULL` | The supplied number is greater than zero. |

A **primary key** identifies the row. A **foreign key** validates a reference. Neither declaration automatically verifies that a customer name is correctly spelled or an email belongs to that person.

## Run a small example

Use a fresh SQLite database for these statements. Prices are stored as integer cents, so `1500` means 15.00 in the chosen currency.

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    price_cents INTEGER NOT NULL CHECK (price_cents >= 0),
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0)
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id)
);

INSERT INTO customers VALUES (1, 'Alice', 'alice@example.com');
INSERT INTO products (product_id, title, price_cents)
VALUES (10, 'Database Basics', 1500);
INSERT INTO orders VALUES (101, 1);
```

The product insert omits `stock`, so its **default** supplies zero. A default is a value used when an input is omitted; it is not validation of arbitrary supplied input.

## Try invalid writes separately

Run each attempt on its own. Each should fail under the constraints above:

```sql
-- A duplicate required email.
INSERT INTO customers VALUES (2, 'Bob', 'alice@example.com');
```

```sql
-- A negative price.
INSERT INTO products VALUES (20, 'SQL Practice', -100, 5);
```

```sql
-- Customer 99 does not exist.
INSERT INTO orders VALUES (102, 99);
```

The failure message identifies the violated rule. A rejected statement is different from a completed application workflow: transaction error handling depends on the engine, so explicitly decide whether to retry or roll back the surrounding work.

## Missing is not the same as empty

`NULL` is SQL's marker for a missing or unknown value. An empty string, zero, and `NULL` are different values in many engines. A `NOT NULL` text column can still contain an empty string unless another rule prevents it.

A `CHECK` rejects an expression that evaluates to false. If the expression is unknown because of `NULL`, it generally passes. That is why required positive quantities need both `NOT NULL` and `CHECK (quantity > 0)`.

Also consider the chosen type's behavior. SQLite's ordinary type declarations are permissive; stricter type validation needs an appropriate strict-table or application validation design. Constraints do not turn every SQLite type declaration into PostgreSQL-style type enforcement.

## Decide what deletion means

If Alice has orders, what should happen when someone deletes her customer row? Possible policies include rejecting the deletion, deleting dependent orders, or retaining orders with an appropriate anonymization workflow.

An `ON DELETE` action expresses a reference policy where supported. `CASCADE` means related rows are deleted automatically; it should be selected because those rows are meant to disappear, not simply to silence a foreign-key error.

## Know which rules need more than one row

“Stock must not be negative” is a row rule. “Every completed order must have at least one item” involves several records and a workflow. “Do not sell the last copy twice” involves concurrent transactions.

Use constraints where they express the rule, and transaction/concurrency logic for the remaining requirements. A pre-insert application check can race: two clients may both pass it before either inserts. A database uniqueness rule closes that particular gap.

## Check your understanding

1. Why is a required unique email declared with both `NOT NULL` and `UNIQUE`?
2. What stock value does the valid product insert produce?
3. Why does a foreign key not prove that an order contains at least one item?
4. Should deleting a customer automatically delete their financial history? Explain the policy your application needs.

Continue with the [SQL introduction](../03_sql/01_intro_to_sql.md) to practice querying and changing these structures.
