# Introduction to SQL

SQL, or **Structured Query Language**, lets you describe the data you want or the change you want to make. For example, “show Alice's orders” becomes a `SELECT` query; “record a new customer” becomes an `INSERT` statement.

The DBMS chooses how to carry out the request. You specify the result, not a loop that reads each disk location yourself. This is why SQL is called a **declarative language**.

## Set up one database for the examples

This note and the next SQL notes use a bookstore. Run the following setup in a **fresh SQLite database**. For each note, start from this setup unless the note explicitly continues an earlier exercise. Use a SQLite shell, a playground configured for SQLite, or Python's `sqlite3` module. Keep the same database connection when working through a transaction example.

The table names are lowercase and use underscores. Prices use integer cents: `1500` represents 15.00 in one currency. Dates use text in `YYYY-MM-DD` format for this SQLite exercise.

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
    stock INTEGER NOT NULL CHECK (stock >= 0)
);

CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    order_date TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'open'
        CHECK (status IN ('open', 'completed', 'cancelled'))
);

CREATE TABLE order_items (
    order_id INTEGER NOT NULL REFERENCES orders(order_id),
    line_number INTEGER NOT NULL,
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price_cents INTEGER NOT NULL CHECK (unit_price_cents >= 0),
    PRIMARY KEY (order_id, line_number)
);

INSERT INTO customers VALUES
    (1, 'Alice', 'alice@example.com'),
    (2, 'Bob', 'bob@example.com'),
    (3, 'Carol', 'carol@example.com');

INSERT INTO products VALUES
    (10, 'Database Basics', 1500, 5),
    (20, 'SQL Practice', 2500, 8),
    (30, 'History of Computing', 1800, 0);

INSERT INTO orders VALUES
    (101, 1, '2025-01-10', 'completed'),
    (102, 1, '2025-01-12', 'open'),
    (103, 2, '2025-01-12', 'completed');

INSERT INTO order_items VALUES
    (101, 1, 10, 2, 1500),
    (101, 2, 20, 1, 2500),
    (102, 1, 10, 1, 1500),
    (103, 1, 20, 2, 2500);
```

`customers` and `products` describe people and books. `orders` describes purchases, and `order_items` describes their individual lines. Stock is the current illustrative inventory; the setup does not replay historical sales to calculate it.

A **statement** is one SQL command. The semicolon ends a statement. `--` introduces a comment continuing to the end of the line. Keywords such as `SELECT` are capitalized here to make the structure easier to see; capitalization is not generally required for those keywords.

## Distinguish a database, a table, and a schema

The bookstore database contains several tables. A table defines a kind of record, such as a customer or an order line. Its rows are the current records, while its columns describe the attributes. A **schema** can mean the overall definition of those objects; in PostgreSQL and SQL Server it also names a namespace grouping objects inside a database, as in `public.orders` or `dbo.Orders`.

SQLite's `main` names the primary attached database, not an identical PostgreSQL-style schema system. Knowing the engine helps interpret a qualified object name. A tutorial's table named `orders` and a production table named `sales.orders` may share a concept without sharing a namespace or permissions.

A **primary key** identifies one row. A **foreign key** validates a reference to another eligible key. In the setup, `orders.customer_id` references `customers.customer_id`; `order_items` uses `(order_id, line_number)` together to identify a line. Line number 1 can appear in several different orders, so line number alone is not its key.

A **result set** is the output of a query, not automatically a stored table. It can have calculated columns, duplicate-looking rows, or nulls introduced by joins. A **view** saves a query definition so callers can reuse it. The joins note develops those differences with examples.

## Read a query one clause at a time

```sql
SELECT title, price_cents
FROM products
WHERE stock > 0
ORDER BY price_cents, product_id;
```

| title | price_cents |
| --- | --- |
| Database Basics | 1500 |
| SQL Practice | 2500 |

`FROM` identifies the input table. `WHERE` keeps rows with stock greater than zero. `SELECT` chooses the values to return. `ORDER BY` sorts the output, breaking equal-price ties by product ID.

SQL writes `SELECT` first, but thinking “input, filter, output, order” often makes the query easier to understand. This is a logical explanation, not a promise about the engine's physical execution order.

## Filter with conditions

```sql
SELECT product_id, title
FROM products
WHERE price_cents < 2000 AND stock > 0
ORDER BY product_id;
```

Only Database Basics matches both conditions. History of Computing costs less than 2000 cents but has no stock.

Use `AND` when both conditions must hold, `OR` when either suffices, and parentheses when the grouping could be unclear. Use `=` for equality and `<>` for inequality. Strings use single quotes, as in `status = 'open'`.

## Give an output column a name

An **alias** is a name used within a query or its result:

```sql
SELECT title, price_cents / 100.0 AS price
FROM products
WHERE product_id = 10;
```

The result contains `Database Basics` and `15.0`. `AS price` names the calculated column; it does not rename the stored `price_cents` column. `100.0` requests non-integer arithmetic here. Formatting a currency for display is a separate application concern.

## Join related rows

```sql
SELECT c.name, o.order_id, o.status
FROM customers AS c
JOIN orders AS o ON o.customer_id = c.customer_id
ORDER BY o.order_id;
```

| name | order_id | status |
| --- | --- | --- |
| Alice | 101 | completed |
| Alice | 102 | open |
| Bob | 103 | completed |

`c` and `o` are table aliases. The join produces one result per matching customer-order pair. Alice appears twice because she has two orders. Carol does not appear because this query asks for matching orders and she has none.

Joins do not copy the joined values permanently into another table. They assemble a result for this query.

## Calculate one result per group

An **aggregate function** combines several input values. `SUM` adds them; `COUNT` counts rows or non-null values.

```sql
SELECT order_id, SUM(quantity * unit_price_cents) AS total_cents
FROM order_items
GROUP BY order_id
ORDER BY order_id;
```

| order_id | total_cents |
| --- | --- |
| 101 | 5500 |
| 102 | 1500 |
| 103 | 5000 |

`GROUP BY` makes one group of lines per order. `SUM` calculates each group's total. Without grouping, summing these line amounts would give one total for the whole input.

## Understand missing values

`NULL` represents a missing or unknown value. It is not zero or an empty string. Use `IS NULL` and `IS NOT NULL` to test it; `value = NULL` does not behave like an ordinary equality check.

The required columns in this setup reject nulls. Later, a left join can still produce nulls in its result when one side has no matching row. That does not insert nulls into the base table.

## Understand the command families

| Family | Purpose | Examples |
| --- | --- | --- |
| DDL: data definition | Define or change the structure. | `CREATE`, `ALTER`, `DROP` |
| DML: data manipulation | Read or change rows. | `SELECT`, `INSERT`, `UPDATE`, `DELETE` |
| TCL: transaction control | Commit or undo grouped work. | `BEGIN`, `COMMIT`, `ROLLBACK` |
| DCL: data control | Grant or revoke privileges in engines that support them. | `GRANT`, `REVOKE` |

Some classifications place `SELECT` in a separate query-language group. Understanding what a statement does matters more than remembering one taxonomy.

## Read conditions as questions about each row

The bookstore asks three different questions: which books fall in a price band, which selected books are available, and which titles contain a word. Each has a direct SQL expression:

```sql
SELECT product_id, title
FROM products
WHERE price_cents BETWEEN 1500 AND 1800
ORDER BY product_id;

SELECT product_id, title
FROM products
WHERE product_id IN (10, 30) AND stock > 0
ORDER BY product_id;

SELECT product_id, title
FROM products
WHERE title LIKE '%Computing%'
ORDER BY product_id;
```

The first query returns products 10 and 30. `BETWEEN` includes both endpoints; product 10 is not excluded for costing exactly 1500 cents. The second returns only product 10: membership in a list and availability must both hold. The third returns product 30. In a `LIKE` pattern, `%` matches any sequence of characters and `_` matches one character. Case matching and escaping depend on the database and collation, so do not assume that a search behaves identically on every engine.

A search box should pass its value as a parameter, not paste it into the statement. In Python's SQLite interface:

```python
search = '%Computing%'
rows = connection.execute(
    'SELECT product_id, title FROM products WHERE title LIKE ? ORDER BY product_id',
    (search,),
).fetchall()
```

Here `connection` is the connection containing the setup. The parameter is a value, not SQL syntax. A value containing a quote remains data. Parameters do not substitute table names or an entire `ORDER BY` expression; choose allowed identifiers in application code when those must vary.

## Order before choosing the first few rows

```sql
SELECT product_id, title, price_cents
FROM products
ORDER BY price_cents DESC, product_id
LIMIT 2;
```

This returns SQL Practice at 2500 cents, followed by History of Computing at 1800 cents. `LIMIT` restricts the result count. It does not mean “the newest” or “the highest” without an appropriate ordering. The ID breaks ties so that a page boundary is predictable.

SQLite and PostgreSQL support this `LIMIT` spelling. SQL Server commonly uses `TOP` or `OFFSET ... FETCH`; an example copied between engines may need syntax changes. Offset pagination can also shift when other users insert rows. For a changing order history, a cursor based on the last `(order_date, order_id)` can provide a more stable continuation.

## Distinguish filtering rows from filtering groups

Suppose the report should include only completed orders worth at least 5000 cents:

```sql
SELECT o.order_id,
       SUM(i.quantity * i.unit_price_cents) AS total_cents
FROM orders AS o
JOIN order_items AS i ON i.order_id = o.order_id
WHERE o.status = 'completed'
GROUP BY o.order_id
HAVING SUM(i.quantity * i.unit_price_cents) >= 5000
ORDER BY o.order_id;
```

The result is order 101 with 5500 cents and order 103 with 5000 cents. `WHERE` removes order 102 before totals are calculated. `HAVING` then tests each completed order's total. Putting a total calculation directly in `WHERE` would confuse a condition on one input row with a condition on a group.

Select the grouping key and aggregate values deliberately. SQLite permits some non-grouped columns in aggregate queries, but that can produce an arbitrary representative value and is rejected by other engines. Do not rely on that permissive behavior to choose which customer's name belongs to a total.

## Build a report in two understandable steps

A **common table expression (CTE)** names a query result within one statement. It is useful when an intermediate result has a clear meaning:

```sql
WITH customer_spending AS (
    SELECT o.customer_id,
           SUM(i.quantity * i.unit_price_cents) AS spent_cents
    FROM orders AS o
    JOIN order_items AS i ON i.order_id = o.order_id
    GROUP BY o.customer_id
)
SELECT c.name, COALESCE(s.spent_cents, 0) AS spent_cents
FROM customers AS c
LEFT JOIN customer_spending AS s ON s.customer_id = c.customer_id
ORDER BY c.customer_id;
```

Alice has 7000 cents, Bob 5000, and Carol 0. This example includes all statuses; an accounting report would first decide whether open or cancelled orders belong in its definition of spending. The CTE totals each customer's lines. The outer query includes every customer and converts a missing total to zero for display. `COALESCE` returns the first non-null argument.

A CTE is not automatically a stored table or a performance improvement. The optimizer's handling varies. Its immediate value here is that “calculate customer totals” and “display all customers” are visible as separate steps.

A **subquery** can also provide one value for a condition:

```sql
SELECT product_id, title
FROM products
WHERE price_cents > (SELECT AVG(price_cents) FROM products)
ORDER BY product_id;
```

The average is about 1933.33 cents, so only SQL Practice qualifies. The inner query returns one scalar value. Later notes explain subqueries that refer to the current outer row and queries that test whether any matching row exists.

## Make changes without losing the practice data

Reading with `SELECT` does not reserve a book. A change must use a writing statement. This exercise inserts a customer, updates their name, and removes the row inside one transaction:

```sql
BEGIN;
INSERT INTO customers (customer_id, name, email)
VALUES (4, 'Dana', 'dana@example.com');
UPDATE customers SET name = 'Dana Lee' WHERE customer_id = 4;
SELECT customer_id, name FROM customers WHERE customer_id = 4;
DELETE FROM customers WHERE customer_id = 4;
ROLLBACK;
```

The intermediate result is `4, Dana Lee`. The final rollback restores the state from before `BEGIN`. The example is a rehearsal, not a recommended way to create then immediately delete a real customer. In an actual operation, use `COMMIT` only after the required work succeeds.

The predicate is crucial: `UPDATE customers SET name = 'Dana Lee'` would target every customer. Inspect the corresponding `SELECT` when learning, and have application code check how many rows a write affected when it expects exactly one.

## Practice structure changes on a separate object

The main setup is DDL followed by DML. Try both families on a small scratch table:

```sql
CREATE TABLE intro_import_batches (
    batch_id INTEGER PRIMARY KEY,
    source_name TEXT NOT NULL
);
ALTER TABLE intro_import_batches ADD COLUMN imported_rows INTEGER NOT NULL DEFAULT 0;
INSERT INTO intro_import_batches (batch_id, source_name)
VALUES (1, 'supplier catalog');
SELECT batch_id, source_name, imported_rows FROM intro_import_batches;
DROP TABLE intro_import_batches;
```

The query returns `1, supplier catalog, 0`. `CREATE` defines the empty table, `ALTER` adds a column, and `INSERT` supplies a record under that definition. `DROP` removes the scratch object afterward. Use this disposable table for practice; changing a populated application's structure requires the migration procedure in the next note.

A text declaration does not by itself validate a date, and a number does not carry a currency unit automatically. Integer cents are suitable for this single-currency exercise, but currency conversions, fractional unit prices, and taxes require an explicit precision and rounding policy. PostgreSQL's `NUMERIC` and other engines' exact decimal types can serve different requirements from approximate floating point.

## Preview a window without replacing the detailed lesson

The order lines can retain their individual rows while showing the order's total beside each line:

```sql
SELECT order_id, line_number,
       quantity * unit_price_cents AS line_total_cents,
       SUM(quantity * unit_price_cents) OVER (PARTITION BY order_id) AS order_total_cents
FROM order_items
ORDER BY order_id, line_number;
```

Order 101 has two rows, with line totals 3000 and 2500; both carry the order total 5500. Orders 102 and 103 have one row each, with totals 1500 and 5000. `GROUP BY` would instead collapse each order into one row. This difference is the starting point for the window-function note, which later adds ordering, ranking, and frames.

Partitioning a large table and replicating a database are different topics from a window's `PARTITION BY`. Table partitioning divides storage by a chosen rule; replication maintains another copy of data. Neither automatically repairs a query that counts the same fact twice. First learn what the query should return, then investigate its plan and the deployment's scaling needs.

## What changes when you move to another SQL engine?

The basic ideas—tables, joins, predicates, groups, and transactions—carry across SQLite, PostgreSQL, MySQL, and SQL Server. Their details differ:

| Decision | SQLite examples here | A production engine may offer |
| --- | --- | --- |
| Money | Integer cents for one currency. | Exact `DECIMAL`/`NUMERIC` with chosen precision and scale. |
| Dates | ISO-formatted text. | Validated date/time types and time zone operations. |
| Generated IDs | `INTEGER PRIMARY KEY` behavior. | Identity columns or sequences, with engine-specific syntax. |
| Permissions | Access controlled around the database file and application. | Database users, roles, and object privileges. |
| Plans | `EXPLAIN QUERY PLAN`. | Engine-specific `EXPLAIN` or execution-plan tools. |

An index may change how a query finds rows without changing which rows it should return. To inspect SQLite's choice, run:

```sql
EXPLAIN QUERY PLAN
SELECT title FROM products WHERE product_id = 10;
```

The exact plan text varies by version. Look for access through the integer primary key. A plan describes an access strategy; timing, data size, and the workload determine whether that strategy is useful. Three sample products cannot establish that a production query is fast.

The following notes develop this foundation in order: DDL defines the rules, DML changes the facts, DCL controls who may act, and TCL groups changes. Joins and routines then build larger queries, while aggregates and windows answer reporting questions.

## Practice before moving on

1. List the titles of products with zero stock. Expected title: History of Computing.
2. List Alice's orders newest first, breaking date ties by order ID.
3. Change the total query to count the lines in each order. Expected counts: 2, 1, and 1.
4. Explain why Carol is missing from the inner-join result.

Continue with [DDL](02_data_definition_language_ddl.md) to understand the setup definitions, then [DML](03_data_manipulation_language_dml.md) to change rows. The [joins chapter](06_joins_subqueries_and_views.md) develops the matching behavior.
