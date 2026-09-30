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

## Practice before moving on

1. List the titles of products with zero stock. Expected title: History of Computing.
2. List Alice's orders newest first, breaking date ties by order ID.
3. Change the total query to count the lines in each order. Expected counts: 2, 1, and 1.
4. Explain why Carol is missing from the inner-join result.

Continue with [DDL](02_data_definition_language_ddl.md) to understand the setup definitions, then [DML](03_data_manipulation_language_dml.md) to change rows. The [joins chapter](06_joins_subqueries_and_views.md) develops the matching behavior.
