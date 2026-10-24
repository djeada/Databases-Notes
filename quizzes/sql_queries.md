# SQL Queries Quiz

Notes: [Introduction to SQL](../notes/03_sql/01_intro_to_sql.md), [DDL](../notes/03_sql/02_data_definition_language_ddl.md), [DML](../notes/03_sql/03_data_manipulation_language_dml.md), [DCL](../notes/03_sql/04_data_control_language_dcl.md), [Joins, Subqueries, and Views](../notes/03_sql/06_joins_subqueries_and_views.md), [Stored Procedures and Functions](../notes/03_sql/07_stored_procedures_and_functions.md), [Triggers](../notes/03_sql/08_triggers.md), [Hierarchical Data](../notes/03_sql/09_hierarchical_data.md), [Aggregate Functions](../notes/03_sql/10_aggregate_functions.md), [Window Functions](../notes/03_sql/11_window_functions.md)

Predict what each query returns or which statement answers the question, using the bookstore-style examples from the SQL notes.

#### Q. Alice has two orders, Bob has one and Carol has none. What `order_count` does this query report for Carol?

```sql
SELECT c.name, COUNT(*) AS order_count
FROM customers AS c
LEFT JOIN orders AS o ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name;
```

* [ ] 0
* [x] 1
* [ ] `NULL`
* [ ] Carol's row is not returned

> **Explanation:** The left join preserves Carol as one null-extended row, and `COUNT(*)` counts rows. `COUNT(o.order_id)` would ignore the null order ID and report 0.

#### Q. Every customer must stay in a report, but only their `open` orders should be attached. Where does `o.status = 'open'` belong in a `customers LEFT JOIN orders` query?

* [x] In the join's `ON` condition
* [ ] In the `WHERE` clause
* [ ] In a `HAVING` clause after grouping
* [ ] In the `ORDER BY` clause

> **Explanation:** In `ON` it limits which orders match while unmatched customers are still kept. In `WHERE` it filters the joined result, removing customers whose order columns are null, so the left join behaves like an inner join.

#### Q. The `blocked` table contains the values `2` and `NULL`. Customers have IDs 1, 2 and 3. What does this query return?

```sql
SELECT customer_id
FROM customers
WHERE customer_id NOT IN (SELECT customer_id FROM blocked);
```

* [ ] IDs 1 and 3
* [ ] IDs 1, 2 and 3
* [x] No rows
* [ ] Only ID 2

> **Explanation:** For IDs 1 and 3, comparing with the null yields unknown, so `NOT IN` never becomes true. A correlated `NOT EXISTS` expresses "no matching blocked row" and returns IDs 1 and 3.

#### Q. Which query lists customers who have never placed an order without being affected by null values in `orders.customer_id`?

* [ ] `SELECT name FROM customers WHERE customer_id NOT IN (SELECT customer_id FROM orders);`
* [x] `SELECT name FROM customers c WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id);`
* [ ] `SELECT name FROM customers c JOIN orders o ON o.customer_id <> c.customer_id;`
* [ ] `SELECT name FROM customers c LEFT JOIN orders o ON o.customer_id = c.customer_id WHERE o.status IS NOT NULL;`

> **Explanation:** `NOT EXISTS` asks whether any matching order row exists, so a null in another order cannot make the test unknown. The `<>` join pairs every customer with other customers' orders instead.

#### Q. Which query finds departments with at least two employees earning more than 60000?

* [x] `SELECT dept_id FROM employees WHERE salary > 60000 GROUP BY dept_id HAVING COUNT(*) >= 2;`
* [ ] `SELECT dept_id FROM employees WHERE COUNT(*) >= 2 AND salary > 60000 GROUP BY dept_id;`
* [ ] `SELECT dept_id FROM employees GROUP BY dept_id HAVING salary > 60000;`
* [ ] `SELECT dept_id FROM employees GROUP BY dept_id WHERE COUNT(*) >= 2;`

> **Explanation:** `WHERE` filters individual rows before grouping, and `HAVING` tests the resulting group count. Aggregates are not allowed in `WHERE`, and a bare non-grouped column in `HAVING` is invalid or meaningless.

#### Q. No employee row matches the filter. What does this query return?

```sql
SELECT COUNT(*) AS n, SUM(salary) AS total
FROM employees
WHERE employee_id < 0;
```

* [ ] No rows at all
* [x] One row: `n = 0`, `total = NULL`
* [ ] One row: `n = 0`, `total = 0`
* [ ] One row: `n = NULL`, `total = NULL`

> **Explanation:** An aggregate without `GROUP BY` always returns one row. Counts of empty input are zero, while `SUM` and `AVG` return null; with a `GROUP BY` key there would be no groups and no rows.

#### Q. The `salary` column holds 100, 200 and `NULL`. What does `AVG(salary)` return?

* [ ] 100
* [x] 150
* [ ] 300
* [ ] `NULL`

> **Explanation:** Aggregates skip nulls, so the average is taken over the two known values. `AVG(COALESCE(salary, 0))` would treat the unknown salary as a real zero and return 100.

#### Q. Joining employees to their projects duplicated salaries for people on several projects. Why is `SUM(DISTINCT salary)` not a correct fix?

* [ ] `DISTINCT` cannot be combined with `SUM`
* [x] Two different employees with equal salaries are counted once
* [ ] It still adds each duplicated salary several more times
* [ ] It returns null when any salary repeats

> **Explanation:** `DISTINCT` deduplicates numeric values, not facts. Deduplication must use the identity of what is counted; aggregate employees separately before joining the one-to-many relationship.

#### Q. What `RANK()` and `DENSE_RANK()` values does the row with amount 200 receive?

```sql
WITH t(id, amount) AS (VALUES (1, 100), (2, 100), (3, 200))
SELECT id,
       RANK() OVER (ORDER BY amount) AS r,
       DENSE_RANK() OVER (ORDER BY amount) AS d
FROM t;
```

* [ ] `r = 2`, `d = 2`
* [x] `r = 3`, `d = 2`
* [ ] `r = 3`, `d = 3`
* [ ] `r = 2`, `d = 3`

> **Explanation:** Both 100-valued rows tie at rank 1. `RANK()` leaves a gap after ties, so the next rank is 3, while `DENSE_RANK()` continues with 2.

#### Q. What running total does the first row (`id = 1`) show?

```sql
WITH t(id, amount) AS (VALUES (1, 100), (2, 100), (3, 200))
SELECT id, SUM(amount) OVER (ORDER BY amount) AS running
FROM t
ORDER BY id;
```

* [ ] 100
* [x] 200
* [ ] 400
* [ ] `NULL`

> **Explanation:** The default frame with `ORDER BY` is `RANGE ... CURRENT ROW`, which includes the whole peer group of tied values. Use `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` with a unique order to advance one row at a time.

#### Q. `LAST_VALUE(amount) OVER (ORDER BY id)` returns each row's own amount instead of the partition's final amount. What fixes it?

* [ ] Add `PARTITION BY id` and keep `ORDER BY id`
* [x] Add `ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`
* [ ] Replace it with `LAG(amount) OVER (ORDER BY id)`
* [ ] Sort both the window and outer query with `ORDER BY id DESC`

> **Explanation:** The default ordered frame ends at the current row's peers, so the "last" value in that frame is the current one. Extending the frame to `UNBOUNDED FOLLOWING` lets it see the end of the partition.

#### Q. You need the top two sales per product. Why is `WHERE ROW_NUMBER() OVER (PARTITION BY product_id ORDER BY amount DESC) <= 2` the wrong approach?

* [ ] `ROW_NUMBER()` cannot be used with `PARTITION BY`
* [x] Window functions run after `WHERE`, so they cannot appear there
* [ ] It keeps ties that `RANK()` would drop
* [ ] `PARTITION BY` columns must also be listed in a `GROUP BY` clause

> **Explanation:** Window functions run on rows that already passed `WHERE` and grouping, so they cannot be referenced there. Compute the row number in a CTE or subquery and filter it in the outer query.

#### Q. What does `LAG(quantity) OVER (PARTITION BY product_id ORDER BY sale_date)` return for each product's earliest sale?

* [ ] The same row's quantity
* [ ] 0
* [x] `NULL`
* [ ] The previous product's last quantity

> **Explanation:** `LAG` looks one row back inside the partition; the first row has no predecessor, so the default result is null. Partitions never borrow rows from another product.

#### Q. A report needs each sale's quantity alongside its product's total quantity, keeping one output row per sale. Which expression fits?

* [ ] `SUM(quantity)` with `GROUP BY product_id`
* [x] `SUM(quantity) OVER (PARTITION BY product_id)`
* [ ] `SUM(DISTINCT quantity)` with `GROUP BY sale_id`
* [ ] `COUNT(quantity) OVER (ORDER BY product_id)`

> **Explanation:** An aggregate used as a window function computes across related rows without collapsing them. `GROUP BY product_id` would return one row per product and lose the individual sales.

#### Q. A recursive CTE walks a category tree downward starting from Computing and returns Computing at depth 0. How do you return only its descendants?

* [ ] Remove the anchor query from the CTE
* [ ] Change `UNION ALL` to `UNION` in the CTE
* [x] Filter the final query with `WHERE depth > 0`
* [ ] Start the anchor row at depth 1 instead of 0

> **Explanation:** The anchor supplies the starting row, and the recursive step builds on it, so removing it returns nothing. Filtering the final result keeps the traversal intact while excluding the starting node.

#### Q. A `categories` table has `parent_id REFERENCES categories(category_id)` and `CHECK (parent_id <> category_id)`. Which invalid structure can still be stored?

* [ ] A category whose parent ID does not exist
* [ ] A category that is its own parent
* [x] Two categories that are each other's parent
* [ ] A root category with a null parent

> **Explanation:** The foreign key rejects missing parents and the check rejects a self-loop, but a longer cycle such as A to B to A satisfies both. Traversals should track visited IDs instead of trusting a depth limit.

#### Q. Why can moving a branch be expensive when a tree is stored as materialized paths such as `/1/2/5/`?

* [ ] Every node's parent ID must be recomputed
* [x] Every descendant's stored path string must be rewritten
* [ ] The whole table must be renumbered with new intervals
* [ ] A recursive query must run after each insert

> **Explanation:** A materialized path stores the traversal result in each row, so moving a subtree changes the prefix of every descendant. Adjacency lists update one parent reference; nested sets renumber intervals.

#### Q. In this SQLite/PostgreSQL upsert, what does `excluded.price_cents` refer to?

```sql
INSERT INTO catalog (sku, title, price_cents)
VALUES ('BK-10', 'Database Basics, revised', 1600)
ON CONFLICT (sku) DO UPDATE
SET price_cents = excluded.price_cents;
```

* [ ] The price currently stored in the conflicting row
* [x] The price proposed by the insert that conflicted
* [ ] The price of a previously deleted row
* [ ] The column's declared default value

> **Explanation:** `excluded` is the pseudo-row holding the values the insert tried to add. The conflict target must match a primary key or unique constraint.

#### Q. Why is SQLite's `INSERT OR REPLACE` not interchangeable with `ON CONFLICT ... DO UPDATE`?

* [ ] It only works on tables without a primary key
* [x] It can delete the conflicting row and insert a new one
* [ ] It silently ignores the new values whenever a conflict occurs
* [ ] It requires an explicit transaction to run

> **Explanation:** Replacing means deleting and reinserting, which can fire delete triggers, affect references and change generated identifiers. An upsert's `DO UPDATE` modifies the existing row in place.

#### Q. An update intended for product 10 is run as `UPDATE products SET price_cents = 2000;`. What happens?

* [ ] The statement fails without a `WHERE` clause
* [ ] Only the first product row is updated
* [x] Every product row gets the new price
* [ ] Only rows with a null price change

> **Explanation:** Without `WHERE`, `UPDATE` targets every row in the table. Run risky changes inside a transaction and check the affected-row count before committing.

#### Q. The `phone` column holds `NULL`, `''` and `'12345'` in three rows. Which rows does `WHERE phone <> '12345'` return?

* [ ] The `NULL` row and the `''` row
* [x] Only the `''` row
* [ ] Only the `NULL` row
* [ ] All three rows

> **Explanation:** Comparing null with any value is unknown, not true, so the null row is filtered out. To include missing phones, write `phone IS NULL OR phone <> '12345'` explicitly.

#### Q. `UPDATE products SET stock = stock - 1 WHERE product_id = 10 AND stock > 0 RETURNING stock;` returns no rows. What can the application conclude?

* [ ] The product does not exist in the table
* [ ] The product exists but is out of stock
* [x] No row qualified; the reason needs another check
* [ ] The update succeeded but `RETURNING` printed nothing

> **Explanation:** An empty `RETURNING` result means the statement changed nothing. It cannot tell a missing product from one with zero stock; query again if the user needs that distinction.

#### Q. What is the key difference between `DELETE FROM products;` and `DROP TABLE products;`?

* [ ] `DELETE` also removes the table's indexes
* [x] `DELETE` keeps the table; `DROP` removes it
* [ ] `DROP` keeps the rows but removes constraints
* [ ] They are synonyms that differ only in speed

> **Explanation:** `DELETE` removes rows and leaves an empty table with its columns, constraints and grants. `DROP TABLE` removes the object, so later queries against it fail.

#### Q. Why is adding a `NOT NULL` column to a table that already has rows harder than defining it on a new, empty table?

* [ ] `NOT NULL` columns cannot be added with `ALTER TABLE`
* [x] Existing rows need a default or a backfill
* [ ] The table's primary key must be dropped first
* [ ] Existing rows are deleted to satisfy the constraint

> **Explanation:** Each existing row would otherwise violate the rule immediately. Choosing a default or backfill is a business decision and usually part of a planned migration.

#### Q. Three customers are combined with three products using `CROSS JOIN`. How many rows are returned?

* [ ] 3
* [ ] 6
* [x] 9
* [ ] 0, because there is no join condition

> **Explanation:** A cross join returns every pair: 3 × 3 = 9. That is useful when all combinations are intended and a warning sign when a matching condition was accidentally omitted.

#### Q. Products cost 1500, 2500 and 1800. How many rows does this self-join return?

```sql
SELECT a.product_id, b.product_id
FROM products AS a
JOIN products AS b ON a.price_cents < b.price_cents;
```

* [ ] 2
* [x] 3
* [ ] 6
* [ ] 9

> **Explanation:** The strict inequality produces one row per cheaper/dearer pair: 1500<1800, 1500<2500 and 1800<2500. It excludes equal-price pairs and a product compared with itself.

#### Q. Why do the notes prefer an explicit `ON` condition over `NATURAL JOIN`?

* [ ] `NATURAL JOIN` always performs a cross join
* [x] A new shared column name silently changes the match
* [ ] `NATURAL JOIN` ignores the tables' primary keys
* [ ] `NATURAL JOIN` is only valid in SQLite databases

> **Explanation:** `NATURAL JOIN` matches on every column with the same name. Adding, say, a `status` column to both tables would quietly add a matching condition and change results.

#### Q. What does `CREATE VIEW order_totals AS SELECT order_id, SUM(...) ... GROUP BY order_id;` store?

* [x] The query definition, evaluated when the view is read
* [ ] A snapshot of the totals at creation time
* [ ] A copy of the totals refreshed every hour
* [ ] An index on `order_id` that speeds up the totals query

> **Explanation:** An ordinary view names a query; later reads see current base data. A materialized view is the variant that stores results and needs a refresh strategy.

#### Q. A SQLite `AFTER UPDATE` trigger inserts a price-history row, and then the transaction that changed the price rolls back. What remains?

* [ ] The history row, because the trigger ran after the update
* [x] Neither the price change nor the history row
* [ ] The price change, but no history row
* [ ] Both, because triggers commit on their own

> **Explanation:** `AFTER` means after the row change, not after commit. Trigger writes run inside the same transaction and are rolled back with it.

#### Q. In a row-level `UPDATE` trigger on `products`, what do `OLD.price_cents` and `NEW.price_cents` refer to?

* [ ] The previous trigger's value and the current trigger's value
* [x] The row's price before and after the update
* [ ] The committed price and the uncommitted price in other sessions
* [ ] The column's default and its check constraint limit

> **Explanation:** `OLD` holds the row as it was before the statement changed it and `NEW` holds the proposed row. Comparing them lets a trigger record only real changes or validate a transition.

#### Q. Stock must never be negative. Which mechanism do the notes recommend first?

* [ ] A `BEFORE UPDATE` trigger that raises an error
* [x] A `CHECK (stock >= 0)` constraint
* [ ] A stored procedure that all clients must call
* [ ] An application check before each update

> **Explanation:** A declarative constraint directly expresses a single-row rule and applies to every writer. Triggers add less visible behavior and are better reserved for work a constraint cannot express.

#### Q. In PostgreSQL, a role has `SELECT` on `public.orders` but still cannot query it. Which missing grant is the most likely cause?

* [ ] `INSERT` on `public.orders`
* [x] `USAGE` on schema `public`
* [ ] `REFERENCES` on `public.orders`
* [ ] `TRIGGER` on `public.orders`

> **Explanation:** Reading a table needs connect rights on the database, `USAGE` on its schema and `SELECT` on the table. Each privilege has a separate purpose.

#### Q. In PostgreSQL, you run `REVOKE SELECT ON public.orders FROM report_reader;` but a user in that role can still read the table. Why might that be?

* [ ] `REVOKE` only applies after the server restarts
* [x] The user gets access through another role, ownership or `PUBLIC`
* [ ] `REVOKE` affects future tables only
* [ ] Revoked privileges stay active until the next `VACUUM` finishes

> **Explanation:** Revoking removes one grant from one role; it is not an absolute ban. Audit every privilege source, including other role memberships, ownership and grants to `PUBLIC`.

#### Q. In PostgreSQL, how is a function invoked compared with a procedure?

* [ ] Both are invoked only with `CALL`
* [x] A function is used inside `SELECT`; a procedure is run with `CALL`
* [ ] A function runs with `EXEC`; a procedure is used inside `SELECT`
* [ ] Both are invoked only inside triggers

> **Explanation:** Functions return a value or set and can appear in queries. Procedures are invoked as statements with `CALL` and, under specific conditions, may control transactions.
