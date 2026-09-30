# Introduction to Databases

A bookstore needs to remember its customers, books, orders, and remaining stock. At first, a spreadsheet or a CSV file might be enough. Once a website, a checkout desk, and an import job all change the same information, storing it becomes only part of the problem. The system also needs to answer questions, reject invalid changes, coordinate simultaneous work, and recover after failure.

A **database** is an organized collection of data. A **database management system (DBMS)** is the software that stores and manages that collection. SQLite, PostgreSQL, MySQL, and MongoDB are DBMSs. When someone says “we use PostgreSQL as our database,” they are naming the software as well as implying the data it manages.

This note starts with a small relational database: one that represents facts in tables and connects them through keys. You will create it, insert records, query related tables, update and delete data, and try a rollback. Later notes compare other database models and explain the machinery behind these operations.

## 1. Why a file is not always enough

Suppose the bookstore keeps this CSV:

```csv
order_id,customer_name,customer_email,order_date
101,Alice,alice@example.com,2025-01-10
102,Alice,alice@example.com,2025-01-12
103,Bob,bob@example.com,2025-01-12
```

It is readable and easy to export. It is also repeating Alice's email. Correcting that address means finding every relevant row. If one row is missed, the file contains conflicting answers to “what is Alice's email?”

Now imagine two programs each load the entire file. One adds an order while the other corrects an email. If both save their own complete version, the later save can overwrite the other's work. A file format does not provide a transaction or a concurrency protocol by itself.

A DBMS supplies mechanisms for these problems:

| Need | What the DBMS provides | Bookstore example |
|---|---|---|
| Preserve facts beyond one process | Persistent storage | Orders remain after the website restarts |
| Find selected records | Queries and access structures | Find Alice's orders without loading the file into application code |
| Reject invalid data | Constraints | Prevent two customers from sharing a required unique email |
| Connect facts | Keys and joins in a relational model | Attach each order to its customer |
| Group related changes | Transactions | Accept an order and its stock reservation together |
| Coordinate competing clients | Concurrency control | Handle two buyers requesting the final copy |
| Recover from failures | Journals or logs, plus backup tools | Recover after a crash or restore an earlier copy |
| Limit access | Engine or platform access controls | Let a reporting account read orders without editing them |

These capabilities have boundaries. A database cannot decide that a supplied postal address is true, and a backup must still be taken and tested. A spreadsheet or append-only file remains useful for small manual tasks, exports, or simple logs. The reason to use a DBMS is the set of operations and guarantees the application needs.

### A technology that uses this approach

SQLite runs as a library inside an application and manages a local database, rather than requiring a separate database server. That makes it useful for a desktop catalog or offline application. Its main database can live in a file, with additional journal files used according to the configuration. [SQLite's usage guide](https://www.sqlite.org/whentouse.html) explains the intended workloads.

Android's Room library builds on SQLite for local structured storage. An app can keep records locally and show them while offline; Room supplies an application-facing layer for entities and queries. This is a concrete example of database storage being useful even without a remote service. See [Android's Room overview](https://developer.android.com/training/data-storage/room).

## 2. Read the structure before writing commands

Separate customer details from order details:

| customer_id | name | email |
|---|---|---|
| 1 | Alice | alice@example.com |
| 2 | Bob | bob@example.com |

A **table** groups records of the same shape. A **row**, or record, describes one customer. A **column**, or field, names one attribute, such as `email`. `alice@example.com` is one value in that column.

The **schema** defines the structure: column names, data types, and rules. The current rows are the data stored under that definition. Changing Alice's email changes data; adding a phone column changes the schema.

`customer_id` is the **primary key**: the chosen identifier for a row. Alice and another customer can have the same name, and a name can change. A stable identifier avoids using display text as identity.

Orders contain a reference to that identifier:

| order_id | customer_id | order_date |
|---|---|---|
| 101 | 1 | 2025-01-10 |
| 102 | 1 | 2025-01-12 |
| 103 | 2 | 2025-01-12 |

Orders 101 and 102 belong to Alice because they contain `customer_id = 1`. This is a **one-to-many relationship**: one customer can have many orders, and each order belongs to one customer in this design.

```text
customers                           orders
customer_id = 1  <----------------  order_id = 101, customer_id = 1
                 <----------------  order_id = 102, customer_id = 1
customer_id = 2  <----------------  order_id = 103, customer_id = 2
```

A **foreign key** declares that the reference must match an existing eligible key. It can reject an order for a nonexistent customer. It does not automatically retrieve the customer's name; that is the query's job.

## 3. Create the database and its first tables

The following SQL uses **SQLite**. Use a fresh database for this note, separate from the fuller bookstore setup in the later SQL chapter. Run the blocks in reading order, except the explicitly marked invalid-write examples.

If you have the SQLite command-line program, open a database with:

```bash
sqlite3 introduction.db
```

With Python 3.12 or later, its standard-library shell is another option:

```bash
python3 -m sqlite3 introduction.db
```

Both open or create a database file named `introduction.db`. They are alternative ways to run the same SQL, not two steps to perform in sequence. You can also use a SQLite playground. SQL statements end with a semicolon; single quotes delimit text values.

Create the tables before inserting rows:

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    order_date TEXT NOT NULL
);
```

`CREATE TABLE` defines an object in the schema. Read each declaration as a statement about valid records:

- `INTEGER` stores an integer identifier. In SQLite, this particular `INTEGER PRIMARY KEY` declaration also identifies the table's rowid.
- `TEXT` stores strings, such as names and email addresses.
- `NOT NULL` requires a value to be present. It does not reject an empty string by itself.
- `UNIQUE` prevents two customer rows from having equal email values under the column's comparison rules.
- `REFERENCES customers(customer_id)` creates the foreign-key relationship.

`PRAGMA foreign_keys = ON` enables foreign-key checks for this SQLite connection. A new connection must enable them too. Dates are ISO-formatted text here, such as `2025-01-10`; the declaration alone does not verify that every string is a real date. PostgreSQL would normally use a `DATE` column for this fact.

## 4. Insert records: create the data

```sql
INSERT INTO customers (customer_id, name, email) VALUES
    (1, 'Alice', 'alice@example.com'),
    (2, 'Bob', 'bob@example.com');

INSERT INTO orders (order_id, customer_id, order_date) VALUES
    (101, 1, '2025-01-10'),
    (102, 1, '2025-01-12'),
    (103, 2, '2025-01-12');
```

`INSERT INTO` names the table and destination columns. Each tuple after `VALUES` supplies one row in that column order. Listing columns explicitly makes the intended mapping easier to read and less dependent on the table's declaration order.

Insert customers first because the orders reference them. An order can have a distinct `order_id` while still repeating `customer_id`: several orders belonging to one customer is expected, not a duplicate-key error.

## 5. Select records: ask a precise question

First inspect the customers:

```sql
SELECT customer_id, name, email
FROM customers
ORDER BY customer_id;
```

| customer_id | name | email |
|---|---|---|
| 1 | Alice | alice@example.com |
| 2 | Bob | bob@example.com |

Now ask for Alice's order history:

```sql
SELECT order_id, order_date
FROM orders
WHERE customer_id = 1
ORDER BY order_id;
```

| order_id | order_date |
|---|---|
| 101 | 2025-01-10 |
| 102 | 2025-01-12 |

Read the clauses as instructions about the result: use `orders` as the input, keep rows meeting the `WHERE` condition, return two named columns, and sort the result by order identifier. SQL describes the desired result; the DBMS chooses how to find it.

`SELECT *` requests all columns and is convenient when exploring a table. Named columns are clearer in application queries. Without `ORDER BY`, a result has no guaranteed display order even when repeated runs happen to look the same.

## 6. Join related tables

The account page needs a customer name beside each order. Retrieve it with a join:

```sql
SELECT c.name, o.order_id, o.order_date
FROM customers AS c
JOIN orders AS o ON o.customer_id = c.customer_id
ORDER BY o.order_id;
```

| name | order_id | order_date |
|---|---|---|
| Alice | 101 | 2025-01-10 |
| Alice | 102 | 2025-01-12 |
| Bob | 103 | 2025-01-12 |

`AS c` and `AS o` introduce **aliases**, short names used within the query. The `ON` condition pairs an order with the customer whose identifier matches. Alice appears twice because she has two matching orders. The join creates a result; it does not copy her name into the stored orders.

This example is an inner join: it returns matching pairs. A customer with no orders would not appear. A later lesson introduces a left join when customers without orders must remain visible.

### Relationships beyond this first example

One-to-one means each record corresponds to at most one record on the other side: a customer might have one separate preference record. Enforcing that relationship requires more than calling it one-to-one; the reference needs an appropriate uniqueness rule.

Many-to-many means records on both sides can have several matches: one order contains several books, and one book appears in several orders. A relational design normally introduces an `order_items` table to represent these pairings and their quantity and purchase price. The [data-models note](04_data_models.md) creates and queries all three relationship types.

## 7. Update a fact without rewriting its references

Alice corrects her email address:

```sql
UPDATE customers
SET email = 'alice.smith@example.com'
WHERE customer_id = 1;

SELECT customer_id, name, email
FROM customers
WHERE customer_id = 1;
```

| customer_id | name | email |
|---|---|---|
| 1 | Alice | alice.smith@example.com |

`SET` describes the change. `WHERE` limits which rows receive it. Her orders still refer to customer 1, so the relationship remains intact. Storing the email only on the customer avoids editing it in every order.

Without a `WHERE` condition, this update would target all customer rows. With a condition matching no rows, it would change nothing; that is not necessarily a SQL error. Applications should inspect affected-row counts when they depend on a particular record being updated.

## 8. Delete an independent record

Add a temporary customer, inspect it, then remove it:

```sql
INSERT INTO customers (customer_id, name, email)
VALUES (3, 'Carol', 'carol@example.com');

SELECT customer_id, name FROM customers WHERE customer_id = 3;

DELETE FROM customers WHERE customer_id = 3;

SELECT COUNT(*) AS remaining_rows
FROM customers
WHERE customer_id = 3;
```

The first query returns `(3, Carol)`; the final count is `0`. `DELETE` removes rows while retaining the table definition. `DROP TABLE` removes the table object itself.

Carol has no orders in this exercise. Deleting Alice is a different operation because existing orders refer to her. With the declared foreign key and no cascading deletion policy, that deletion is rejected. Deciding how to remove or anonymize customers with order history is a business-design question.

The four everyday data operations are often abbreviated **CRUD**: create records with `INSERT`, read with `SELECT`, update with `UPDATE`, and delete with `DELETE`. Creating a table is schema definition, distinct from CRUD's creation of a record.

## 9. Let the database reject broken rules

Run these two deliberately invalid statements separately. They are not part of a script expected to complete successfully:

```sql
-- Expected UNIQUE failure: Alice already owns this required email.
INSERT INTO customers (customer_id, name, email)
VALUES (4, 'Dana', 'alice.smith@example.com');
```

```sql
-- Expected FOREIGN KEY failure: customer 99 does not exist.
INSERT INTO orders (order_id, customer_id, order_date)
VALUES (104, 99, '2025-01-13');
```

The first fails because of the email rule, and the second because of the customer reference. Neither invalid row is accepted. Constraints protect data even when an import script or another application bypasses a web form's validation.

These declarations do not verify email ownership, consent, or whether an order was placed by the person operating the browser. Validation, authentication, and authorization remain separate responsibilities.

## 10. Try a transaction without keeping its changes

A **transaction** groups database changes into a unit that can be accepted with `COMMIT` or discarded with `ROLLBACK`. Try changing Alice's name temporarily:

```sql
BEGIN;
UPDATE customers SET name = 'Temporary name' WHERE customer_id = 1;
SELECT name FROM customers WHERE customer_id = 1;
ROLLBACK;
SELECT name FROM customers WHERE customer_id = 1;
```

The first query returns `Temporary name`; the second returns `Alice`. The transaction can read its own uncommitted change, and rollback removes that change. Her earlier email correction remains because this rollback does not undo previously committed work.

For checkout, the same grouping can cover stock reduction, order creation, and purchased-item insertion. The application must check failures and choose a correct concurrency strategy. A transaction does not automatically reserve stock that was merely read, and rolling it back cannot unsend an email or reverse an external payment. Those details are developed in the [ACID chapter](../04_acid_properties_and_transactions/01_transactions_intro.md).

## 11. Add an access structure for a recurring query

Order-history requests filter by customer identifier. An **index** gives the DBMS an additional route to those matching orders:

```sql
CREATE INDEX idx_orders_customer ON orders(customer_id);

EXPLAIN QUERY PLAN
SELECT order_id, order_date
FROM orders
WHERE customer_id = 1;
```

`EXPLAIN QUERY PLAN` describes SQLite's chosen access path. It can show a search using `idx_orders_customer` rather than a scan through all orders. It does not return the order history itself. Exact plan text varies, and a three-row table cannot demonstrate a production performance gain.

SQLite uses B-tree structures for its indexes: ordered keys guide lookup toward matching entries. Maintaining those entries costs space and additional work when relevant rows change. That tradeoff is why an index should answer a real access pattern instead of being added to every column. The [DBMS note](03_database_management_systems_dbms_.md) follows planning and execution in more detail.

## 12. Put the database behind an application

A website usually has this request path:

```text
Browser -> Web application -> Database query -> DBMS
Browser <- Rendered page  <- Returned rows  <- DBMS
```

The application checks who is allowed to see an order, sends a query, and renders the returned rows. A database driver is the library that lets application code send those requests.

For a complete Python example, save the SQL blocks from sections 3 and 4 as `intro.sql`, then run this program once with a fresh `introduction.db` file:

```python
import sqlite3
from pathlib import Path

conn = sqlite3.connect("introduction.db")
try:
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(Path("intro.sql").read_text())
    rows = conn.execute(
        "SELECT order_id, order_date FROM orders "
        "WHERE customer_id = ? ORDER BY order_id",
        (1,),
    ).fetchall()
    print(rows)
finally:
    conn.close()
```

The result is `[(101, '2025-01-10'), (102, '2025-01-12')]`. This is an alternative way to run the initial setup, not a program to run on top of an already populated file. SQLite's connection opens a local file, so no database server is required.

The `?` placeholder is a **bound parameter**. The driver supplies the customer identifier separately from SQL structure. Application code should bind untrusted values instead of building query text by concatenating them. The [SQL injection note](../11_security_best_practices/06_sql_injection.md) explains why.

## 13. Where other technologies fit

The same bookstore can have several kinds of data, but that does not mean it needs several database products immediately.

| Technology | Concrete role to investigate | Why the mechanism fits |
|---|---|---|
| SQLite | Local offline catalog | Embedded queries and transactions work without a separate server |
| PostgreSQL or MySQL | Shared customers, stock, and orders | Client-server access, relational constraints, and transactions support operational workflows |
| MongoDB | Catalog records with varying nested specifications | A document groups each product's attributes |
| Redis | Expiring login sessions or reusable catalog responses | Direct key lookup and expiration fit these temporary records |
| Neo4j | Traversing customer follows and book recommendations | Graph patterns express paths through relationships |

These are possible designs, not claims about a particular company's deployment. The next note creates and queries examples of the models so the tradeoffs are visible in code.

## Practice and check your understanding

1. Query Bob's orders. Expected: order 103 only.
2. Change Alice's display name inside a transaction and roll it back. Which name should the next query show?
3. Insert a customer with a new identifier and an existing email. Which rule rejects it?
4. Explain why a foreign key and a join are both useful but do different work.
5. Why does the email correction avoid changing the two orders that belong to Alice?
6. Which command changes a row, which removes a row, and which removes a table?
7. Why is a cache of “one copy remaining” insufficient to authorize a purchase?

Continue with [database types](02_types_of_databases.md) for concrete SQL, MongoDB, Redis, Cassandra, and Neo4j examples. The [glossary](05_glossary.md) is a reference for unfamiliar terms.
