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

## Distinguish the kinds of integrity being protected

**Entity integrity** keeps an identifier unambiguous. **Referential integrity** keeps relationships valid. **Domain integrity** limits the allowed values of an attribute. **Business integrity** preserves the application's larger invariants, such as a reservation corresponding to an order.

The mechanisms overlap but do not replace one another. A unique identifier does not validate an amount, and a valid amount does not establish that the transaction was authorized. Constraints define the rules you encoded, not every possible truth about the world.

## Try deletion policies on a small independent model

Continue in the same SQLite connection or use another fresh one with foreign-key enforcement enabled:

```sql
PRAGMA foreign_keys = ON;
CREATE TABLE integrity_departments (
    department_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE integrity_staff (
    staff_id INTEGER PRIMARY KEY,
    department_id INTEGER REFERENCES integrity_departments(department_id)
        ON DELETE SET NULL,
    name TEXT NOT NULL
);
INSERT INTO integrity_departments VALUES (1, 'Support');
INSERT INTO integrity_staff VALUES (10, 1, 'Sam');
DELETE FROM integrity_departments WHERE department_id = 1;
SELECT staff_id, department_id, name FROM integrity_staff;
```

| staff_id | department_id | name |
|---|---|---|
| 10 | NULL | Sam |

`SET NULL` retains the employee but removes the reference. The reference column is nullable so that policy is representable. Declaring it `NOT NULL` would conflict with the intended result when deletion happens.

`CASCADE` instead deletes dependent rows, useful when their lifecycle truly belongs to the parent. Restricting or rejecting deletion keeps the relationship intact until a deliberate alternative is chosen. “No action” and “restrict” can differ in check timing, so use the chosen engine's definition rather than treating every rejection policy as identical.

For historical order data, cascading customer deletion could erase facts needed by accounting or customer service. Decide the retention and anonymization model with its owners instead of selecting cascade because it makes a delete command succeed.

## Deferred constraints check at a different boundary

Sometimes records form relationships before all of the transaction's statements have executed. A deferred foreign key can allow temporary missing references while requiring a valid state by commit. This is a SQLite example:

```sql
CREATE TABLE integrity_parents (parent_id INTEGER PRIMARY KEY);
CREATE TABLE integrity_children (
    child_id INTEGER PRIMARY KEY,
    parent_id INTEGER NOT NULL,
    FOREIGN KEY (parent_id) REFERENCES integrity_parents(parent_id)
        DEFERRABLE INITIALLY DEFERRED
);
BEGIN;
INSERT INTO integrity_children VALUES (1, 99);
INSERT INTO integrity_parents VALUES (99);
COMMIT;
SELECT child_id, parent_id FROM integrity_children;
```

| child_id | parent_id |
|---|---|
| 1 | 99 |

After the first insert, the parent is not yet present. After the second, the reference is valid, so commit succeeds. Removing the parent insert would make commit fail and leave error handling to the application. Deferral changes **when** a rule must hold, not whether it matters. See [SQLite foreign keys](https://www.sqlite.org/foreignkeys.html).

## Model a uniqueness rule spanning two columns

A booking must not reuse the same seat for one screening, while that seat can be used at other screenings:

```sql
CREATE TABLE integrity_bookings (
    booking_id INTEGER PRIMARY KEY,
    screening_id INTEGER NOT NULL,
    seat_number TEXT NOT NULL,
    customer_name TEXT NOT NULL,
    UNIQUE (screening_id, seat_number)
);
INSERT INTO integrity_bookings VALUES (1, 100, 'A1', 'Alice');
INSERT INTO integrity_bookings VALUES (2, 101, 'A1', 'Bob');
SELECT screening_id, seat_number FROM integrity_bookings ORDER BY screening_id;
```

| screening_id | seat_number |
|---|---|
| 100 | A1 |
| 101 | A1 |

The pair is unique, not each field individually. Two concurrent attempts to reserve `(100, A1)` must pass the same database rule, so only one can be accepted under the constraint. A preliminary application check for availability is useful for messaging but cannot replace the unique constraint: another writer can act after the check.

A global rule such as “at most ten active reservations per customer” is more complex. A row-level check normally cannot count other rows safely. Consider a redesigned counter or allocation structure, locking the owning entity, or serializable transactions with retry, according to the engine.

## Type declarations are engine-specific enforcement

PostgreSQL normally rejects a text value for an integer amount unless an appropriate conversion succeeds. Ordinary SQLite tables use type affinity rather than treating every type declaration as strict enforcement. For supported SQLite versions, strict tables are an option:

```sql
CREATE TABLE integrity_strict_amounts (
    amount_id INTEGER PRIMARY KEY,
    amount_cents INTEGER NOT NULL CHECK (amount_cents >= 0)
) STRICT;
INSERT INTO integrity_strict_amounts VALUES (1, 1500);
```

SQLite 3.37 or later is required. Even strict typing does not prove the amount is the correct price or uses the correct currency. Syntax validation, domain checks, and business calculation are different layers. See [SQLite strict tables](https://www.sqlite.org/stricttables.html).

## Import, repair, and monitor without silently weakening the model

For imports, stage records in a separate area, validate them, report rejected rows, and load accepted records through a controlled transaction policy. Decide whether the batch is all-or-nothing or whether partial acceptance is allowed and recorded. Do not disable constraints and assume that turning them on afterward validates everything already loaded.

If data was written while checks were absent, use engine-supported integrity checks and explicit reconciliation queries. SQLite provides `PRAGMA foreign_key_check`; it reports violations rather than repairing them. Record the rule being checked, the affected identifiers, and an owner for remediation.

Constraints use work: foreign-key checks, uniqueness searches, and cascading operations can need indexes and acquire locks. Measure those costs, but first preserve the correctness requirement. An appropriate index on referencing columns can make related checks and deletions much cheaper than repeatedly scanning the child table.

Translate failures into useful application outcomes: duplicate email, missing referenced product, or unavailable seat are different causes. Do not expose raw database internals as the only user feedback. A constraint error inside a transaction also needs a rollback or retry decision; the statement failure alone does not complete the business workflow.

## Check your understanding

1. Why is a required unique email declared with both `NOT NULL` and `UNIQUE`?
2. What stock value does the valid product insert produce?
3. Why does a foreign key not prove that an order contains at least one item?
4. Should deleting a customer automatically delete their financial history? Explain the policy your application needs.

Continue with the [SQL introduction](../03_sql/01_intro_to_sql.md) to practice querying and changing these structures.
