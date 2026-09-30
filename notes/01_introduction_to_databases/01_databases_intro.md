# Introduction to Databases

Imagine a small bookstore taking orders through a website. It needs to remember who bought something, what they bought, and how much stock remains. Keeping that information only in the running application would lose it when the process stops. Writing files can preserve it, but the application would have to handle searching, simultaneous changes, and recovery itself.

A **database** is an organized collection of data. A **database management system**, or **DBMS**, is the software that reads and changes it. SQLite and PostgreSQL are examples of DBMSs. We will begin with a relational database, which represents data as tables.

## Read a table before writing SQL

Here are two customers:

| customer_id | name | email |
| --- | --- | --- |
| 1 | Alice | alice@example.com |
| 2 | Bob | bob@example.com |

A **row** describes one customer. A **column** describes one kind of information, such as a name. The value `Alice` is the name in the first row.

The table's definition is part of its **schema**: its column names, types, and rules. The schema says what a customer record can contain; the rows are the data currently stored under that definition.

`customer_id` identifies a customer even if two customers have the same name. We will make it the **primary key**, a required identifier that cannot repeat. Names are useful for display, but poor identifiers because they can change or be shared.

## Keep different facts in different tables

A customer can place more than one order. Put orders in their own table:

| order_id | customer_id | order_date |
| --- | --- | --- |
| 101 | 1 | 2025-01-10 |
| 102 | 1 | 2025-01-12 |
| 103 | 2 | 2025-01-12 |

Orders 101 and 102 belong to Alice because both contain `customer_id = 1`. We store her name once in `customers` rather than copying it into every order.

This is a **one-to-many relationship**: one customer can have many orders, while each order belongs to one customer in this design. A **foreign key** is a database rule that requires each order's customer ID to match an existing customer. It prevents an order from pointing to a customer who is missing.

```text
customers.customer_id <---- orders.customer_id
one customer                  many orders
```

An order can contain several products. We will add that relationship later using an order-items table; the two tables above are enough for this first example.

## Run a complete first example

Use SQLite for this exercise. Run the statements below in order in a fresh database, using a SQLite shell or playground. `PRAGMA foreign_keys = ON` enables foreign-key checks for the current SQLite connection.

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

INSERT INTO customers VALUES
    (1, 'Alice', 'alice@example.com'),
    (2, 'Bob', 'bob@example.com');

INSERT INTO orders VALUES
    (101, 1, '2025-01-10'),
    (102, 1, '2025-01-12'),
    (103, 2, '2025-01-12');
```

`CREATE TABLE` defines the structure. `INSERT` adds rows. `NOT NULL` requires a value, and `UNIQUE` rejects duplicate email values. Together, these declarations give the DBMS rules to check when data changes.

Dates here are text in `YYYY-MM-DD` form to keep the SQLite example simple. A text column alone does not validate that every supplied string is a real date.

## Ask a question with a query

A **query** is a request for data. This one asks for Alice's orders:

```sql
SELECT order_id, order_date
FROM orders
WHERE customer_id = 1
ORDER BY order_id;
```

Read it as: select these two columns, from the orders table, keeping only Alice's rows, and sort them by order ID.

| order_id | order_date |
| --- | --- |
| 101 | 2025-01-10 |
| 102 | 2025-01-12 |

The query produces a result; it does not change the stored rows.

## Combine related data

To show names instead of customer IDs, use a **join**. A join pairs rows according to a condition:

```sql
SELECT customers.name, orders.order_id, orders.order_date
FROM customers
JOIN orders ON customers.customer_id = orders.customer_id
ORDER BY orders.order_id;
```

| name | order_id | order_date |
| --- | --- | --- |
| Alice | 101 | 2025-01-10 |
| Alice | 102 | 2025-01-12 |
| Bob | 103 | 2025-01-12 |

The `ON` condition says which customer goes with each order. A foreign key checks whether references are valid; a join uses those values to assemble a result. They serve different purposes.

## What the DBMS does for the application

As the store grows, two customers may try to buy the last copy of a book at once. The application also needs an order and its stock change to succeed together. A DBMS supplies transaction and concurrency mechanisms for these problems; the application must still use them correctly.

A **transaction** groups related database work so it can be committed together or rolled back. An **index** is an additional structure that helps find selected rows without searching the whole table. You do not need either mechanism to understand this first query, but they explain why database software does more than save a file.

Backups, permissions, and recovery settings also need to be configured. Using a database does not automatically make incorrect application decisions correct.

## Check your understanding

1. Which part of the customer example is the schema, and which part is the data?
2. Why is `customer_id` a better identifier than `name`?
3. Which customer placed order 102, and how can you tell?
4. What does the foreign key prevent? What does the join do?
5. Try selecting Bob's orders. What should the result contain?

Continue with [database types](02_types_of_databases.md) to see other ways of organizing data. The [SQL introduction](../03_sql/01_intro_to_sql.md) develops the commands used here.
