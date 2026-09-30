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

## Check your understanding

1. Why does Alice appear twice in the inner join?
2. Where should the open-status condition go if Carol must remain in the report?
3. Why is `COUNT(o.order_id)` different from `COUNT(*)` after the left join?
4. Why might `EXISTS` be clearer than a join when you only want customers with an order?
5. Does creating `order_totals` store an independent snapshot of the totals?

Continue with [stored procedures and functions](07_stored_procedures_and_functions.md) for reusable database logic. [Aggregate functions](10_aggregate_functions.md) and [window functions](11_window_functions.md) develop reporting calculations.
