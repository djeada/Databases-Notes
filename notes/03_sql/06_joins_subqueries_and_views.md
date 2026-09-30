# Joins, Subqueries, and Views

The bookstore's tables separate customers, orders, products, and order lines. A query puts the relevant facts together without permanently copying them. This note explains three tools: a **join** combines matching rows, a **subquery** uses another query inside a statement, and a **view** names a reusable query.

Use a fresh copy of the SQLite [introductory setup](01_intro_to_sql.md). In particular, Alice has two orders, Bob has one, and Carol has none. If you committed extra orders during the transaction exercises, reset the sample before comparing these results.

## An inner join returns matching pairs

```sql
SELECT c.name, o.order_id
FROM customers AS c
INNER JOIN orders AS o ON o.customer_id = c.customer_id
ORDER BY o.order_id;
```

| name | order_id |
| --- | --- |
| Alice | 101 |
| Alice | 102 |
| Bob | 103 |

Start with Alice's customer row. The `ON` condition finds two orders with her customer ID, so the result contains two pairs. Bob matches once; Carol does not match.

`INNER JOIN` can be written as `JOIN`. `c` and `o` are aliases, short query names for the tables. `c.name` means the name column from the customer side.

## A left join keeps the unmatched left rows

Suppose the report needs every customer, including those who have not bought anything:

```sql
SELECT c.name, o.order_id
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.customer_id
ORDER BY c.customer_id, o.order_id;
```

| name | order_id |
| --- | --- |
| Alice | 101 |
| Alice | 102 |
| Bob | 103 |
| Carol | NULL |

Carol's row is retained. Since there is no order to supply right-side values, those values are `NULL` in the query result. The join did not create an empty order in the database.

“Left” refers to the table written before the join. Reversing the table positions changes which unmatched rows are preserved.

## Put a filter where its meaning belongs

To keep every customer but attach only open orders, include that condition in the matching rule:

```sql
SELECT c.name, o.order_id
FROM customers AS c
LEFT JOIN orders AS o
    ON o.customer_id = c.customer_id AND o.status = 'open'
ORDER BY c.customer_id;
```

The result is Alice with order 102, Bob with null, and Carol with null.

If instead you write `WHERE o.status = 'open'`, the filter applies to the joined result. Bob and Carol have null on the order side, so they do not pass that condition and disappear. This is a frequent cause of a left join behaving like an inner join.

## A join can multiply rows

Joining order 101 to its items returns two rows because the order has two lines. Joining each line to its product supplies the title:

```sql
SELECT i.line_number, p.title, i.quantity, i.unit_price_cents
FROM order_items AS i
JOIN products AS p ON p.product_id = i.product_id
WHERE i.order_id = 101
ORDER BY i.line_number;
```

| line_number | title | quantity | unit_price_cents |
| --- | --- | --- | --- |
| 1 | Database Basics | 2 | 1500 |
| 2 | SQL Practice | 1 | 2500 |

That multiplication is correct here. But summing an order-level value after joining it to multiple lines can count that value several times. Decide what one input row represents before aggregating.

## Aggregate a left join carefully

Count orders for every customer:

```sql
SELECT c.customer_id, c.name, COUNT(o.order_id) AS order_count
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
ORDER BY c.customer_id;
```

The counts are Alice = 2, Bob = 1, Carol = 0. `COUNT(o.order_id)` ignores the null order ID in Carol's unmatched result row. `COUNT(*)` would count that preserved row and report one for Carol.

Use `WHERE` to filter input rows and `HAVING` to filter aggregate groups. For example, `HAVING COUNT(o.order_id) >= 2` keeps only Alice after the groups have been calculated.

## Use a scalar subquery for one calculated value

A **scalar** result is one value. This query compares each product with the average current price:

```sql
SELECT title, price_cents
FROM products
WHERE price_cents > (SELECT AVG(price_cents) FROM products)
ORDER BY product_id;
```

The inner query calculates approximately 1933.33 cents. Only SQL Practice, at 2500 cents, is above it. `AVG` combines the input prices into one result, which the outer condition uses.

The optimizer decides how to execute the statement. A nested query is not a guarantee that the engine physically runs it once in exactly the way the syntax is written.

## Use EXISTS when you need to know whether a match exists

```sql
SELECT c.customer_id, c.name
FROM customers AS c
WHERE EXISTS (
    SELECT 1
    FROM orders AS o
    WHERE o.customer_id = c.customer_id
)
ORDER BY c.customer_id;
```

The result contains Alice and Bob once each. `EXISTS` asks whether the inner query has any matching row; it does not return every matching order.

This is a **correlated subquery** because it refers to the outer row through `c.customer_id`. For finding customers with no orders, use the same query with `NOT EXISTS`; the result is Carol.

`SELECT 1` supplies an arbitrary value because existence, rather than the selected contents, is what matters. An optimizer can transform the query, so correlation does not prove a fixed number of physical executions.

## Other joins, once matching is clear

A **right join** preserves unmatched rows from the right side. It can usually be expressed as a left join with table positions exchanged. A **full outer join** preserves unmatched rows from both sides. Support depends on engine and version.

A **cross join** produces every pair: three customers crossed with three products produces nine result rows. It is useful when every combination is intended, and a warning sign when a matching condition was accidentally omitted.

A **self-join** uses the same table more than once with different aliases. For example, comparing products with other products is still a join between two sets of rows, even though both sets come from one table.

## Name a reusable query with a view

Create an ordinary view for totals:

```sql
CREATE VIEW order_totals AS
SELECT order_id, SUM(quantity * unit_price_cents) AS total_cents
FROM order_items
GROUP BY order_id;
```

Query it like a table:

```sql
SELECT order_id, total_cents
FROM order_totals
WHERE total_cents > 5000
ORDER BY order_id;
```

Only order 101 appears, with 5500 cents. The view stores the query definition, not a separately refreshed copy of the totals. Changing a base row affects what a later query sees under its transaction's visibility rules.

A **materialized view** stores results too and needs an engine-specific maintenance strategy. Whether an ordinary view can be updated also depends on its definition and the engine; an aggregate view should not be treated as a universally writable table.

## See both unmatched sides with a full join

A reconciliation report often asks which identifiers occur in either of two sources. These independent tables keep the example small:

```sql
CREATE TABLE join_expected (item_id INTEGER PRIMARY KEY, label TEXT NOT NULL);
CREATE TABLE join_received (item_id INTEGER PRIMARY KEY, label TEXT NOT NULL);
INSERT INTO join_expected VALUES (1, 'first'), (2, 'second');
INSERT INTO join_received VALUES (2, 'second'), (3, 'third');

SELECT e.item_id AS expected_id, r.item_id AS received_id
FROM join_expected AS e
FULL OUTER JOIN join_received AS r ON r.item_id = e.item_id
ORDER BY COALESCE(e.item_id, r.item_id);
```

The pairs are `(1, NULL)`, `(2, 2)`, and `(NULL, 3)`. Item 1 is missing from the received source, item 2 matches, and item 3 was not expected. A full join preserves unmatched rows from both sides. SQLite supports right and full joins starting with 3.39.0; use a newer shell for this exercise. PostgreSQL also supports them, while MySQL does not provide this full-join syntax.

A right join preserves the table written on the right:

```sql
SELECT e.item_id AS expected_id, r.item_id AS received_id
FROM join_expected AS e
RIGHT JOIN join_received AS r ON r.item_id = e.item_id
ORDER BY r.item_id;
```

It returns `(2, 2)` and `(NULL, 3)`. Rewriting it as `join_received LEFT JOIN join_expected` preserves the same source and is often easier to read. Prefer an explicit `ON` condition to a natural join: a future column with a shared name can silently change what `NATURAL JOIN` matches.

## Cross joins generate combinations; self joins compare rows

A cross join has no matching condition. It is useful when the question really is “every customer with every product,” such as generating a recommendation candidate set:

```sql
SELECT c.name, p.title
FROM customers AS c
CROSS JOIN products AS p
ORDER BY c.customer_id, p.product_id;
```

Three customers times three products gives nine rows, including Carol with all three books. Filtering recommendations requires further rules; this query alone recommends nothing intelligently. On large tables, the product of their row counts can become very large.

A self join uses the same table twice under different aliases. To compare each cheaper book with each more expensive book:

```sql
SELECT cheaper.product_id AS cheaper_id,
       dearer.product_id AS dearer_id
FROM products AS cheaper
JOIN products AS dearer ON cheaper.price_cents < dearer.price_cents
ORDER BY cheaper.product_id, dearer.product_id;
```

The pairs are `(10, 20)`, `(10, 30)`, and `(30, 20)`. These aliases represent different candidate rows of the same base table. The strict inequality excludes equal-price pairs and a product compared with itself. An employee-to-manager relationship is another self-join use: join one employee's `manager_id` to another employee's ID.

## A correlated subquery refers to the current outer row

This report calculates an order count for each customer:

```sql
SELECT c.name,
       (SELECT COUNT(*)
        FROM orders AS o
        WHERE o.customer_id = c.customer_id) AS order_count
FROM customers AS c
ORDER BY c.customer_id;
```

The results are Alice 2, Bob 1, and Carol 0. The inner query refers to `c.customer_id`, so it is **correlated** with the outer query. That describes its meaning, not a guarantee that the engine executes it as a literal application-style loop. The optimizer may choose an efficient equivalent plan.

A scalar subquery must obey the engine's rules for returning one value. Do not select an arbitrary matching order ID and assume it chooses the newest. Use a complete ordering with a limit, or a proper aggregate, according to the question. If many per-customer summaries are needed, grouping orders once and joining those summaries can also make the query clearer.

## Avoid null surprises in an anti-match

Suppose an external blocklist has a missing identifier:

```sql
CREATE TABLE join_blocked_customers (customer_id INTEGER);
INSERT INTO join_blocked_customers VALUES (2), (NULL);

SELECT customer_id
FROM customers
WHERE customer_id NOT IN (SELECT customer_id FROM join_blocked_customers)
ORDER BY customer_id;
```

The result is empty. For IDs 1 and 3, the comparisons include an unknown comparison with null, so `NOT IN` does not become true. This is not the intended “all customers except Bob.” Express the match being excluded instead:

```sql
SELECT c.customer_id
FROM customers AS c
WHERE NOT EXISTS (
    SELECT 1
    FROM join_blocked_customers AS b
    WHERE b.customer_id = c.customer_id
)
ORDER BY c.customer_id;
```

This returns 1 and 3. `NOT EXISTS` asks whether a matching row exists; the unrelated null row does not match a known customer ID. If the schema prohibits null IDs, `NOT IN` can also be valid. Understanding the input's nullability is part of choosing the expression.

## Group before joining another one-to-many relationship

A customer can have many orders and many support tickets. Joining both detail tables directly can pair every order with every ticket, inflating counts. Here is a separate ticket table:

```sql
CREATE TABLE join_support_tickets (
    ticket_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id)
);
INSERT INTO join_support_tickets VALUES (1, 1), (2, 1), (3, 2);

WITH order_counts AS (
    SELECT customer_id, COUNT(*) AS order_count
    FROM orders GROUP BY customer_id
), ticket_counts AS (
    SELECT customer_id, COUNT(*) AS ticket_count
    FROM join_support_tickets GROUP BY customer_id
)
SELECT c.name,
       COALESCE(o.order_count, 0) AS order_count,
       COALESCE(t.ticket_count, 0) AS ticket_count
FROM customers AS c
LEFT JOIN order_counts AS o ON o.customer_id = c.customer_id
LEFT JOIN ticket_counts AS t ON t.customer_id = c.customer_id
ORDER BY c.customer_id;
```

Alice has 2 orders and 2 tickets, Bob 1 and 1, Carol 0 and 0. Each CTE has at most one row per customer, so the final joins preserve that report's grain. Adding `DISTINCT` to a multiplied result is not a general repair: it can discard genuinely separate rows or leave a duplicated monetary sum.

## A view has a definition, dependencies, and a write policy

The existing order-total view is a saved calculation, not stored totals. When order lines change, a later query through the view reflects the underlying rows visible to that query. A materialized view is different: its stored results need the engine's refresh or maintenance mechanism.

SQLite views are read-only unless `INSTEAD OF` triggers supply write behavior. PostgreSQL can automatically update certain simple views. An independent PostgreSQL example illustrates keeping changes inside the view's condition:

```sql
-- PostgreSQL
CREATE TABLE join_pg_stock (
    product_id INTEGER PRIMARY KEY,
    stock INTEGER NOT NULL CHECK (stock >= 0)
);
INSERT INTO join_pg_stock VALUES (10, 5), (30, 0);
CREATE VIEW join_pg_available AS
SELECT product_id, stock FROM join_pg_stock WHERE stock > 0
WITH LOCAL CHECK OPTION;
UPDATE join_pg_available SET stock = 4 WHERE product_id = 10;
SELECT product_id, stock FROM join_pg_stock ORDER BY product_id;
```

The base table contains `(10, 4)` and `(30, 0)`. Through this view, setting product 10 to zero would violate its check option and fail; the row would no longer satisfy `stock > 0`. The base table's own check still permits zero. A view can present a restricted interface, but table privileges must also be designed if users should be unable to bypass that interface.

References: [SQLite SELECT and join support](https://www.sqlite.org/lang_select.html), [SQLite 3.39.0](https://www.sqlite.org/releaselog/3_39_0.html), and [PostgreSQL CREATE VIEW](https://www.postgresql.org/docs/current/sql-createview.html).

## Check your understanding

1. Why does Alice appear twice in the inner join?
2. Where should the open-status condition go if Carol must remain in the report?
3. Why is `COUNT(o.order_id)` different from `COUNT(*)` after the left join?
4. Why might `EXISTS` be clearer than a join when you only want customers with an order?
5. Does creating `order_totals` store an independent snapshot of the totals?

Continue with [stored procedures and functions](07_stored_procedures_and_functions.md) for reusable database logic. [Aggregate functions](10_aggregate_functions.md) and [window functions](11_window_functions.md) develop reporting calculations.
