# Stored Procedures and Functions: Name Reusable Database Work

A view names a query. A **stored routine** names database code that can accept inputs and perform work. Two common kinds are procedures and functions. Their syntax, return values, transaction rules, and privileges depend on the engine.

Read [joins, subqueries, and views](06_joins_subqueries_and_views.md) first. This note uses **PostgreSQL**, because SQLite does not provide SQL `CREATE PROCEDURE` or `CREATE FUNCTION` commands. SQLite applications can register functions through their programming-language API, which is a different mechanism.

## Start with the work you want to reuse

The bookstore often needs an order's total: multiply each line's quantity by its purchase price, then add the amounts. A plain query is already sufficient. A function can give that calculation a reusable name and accept the order identifier as an argument.

For this standalone PostgreSQL exercise, create a small practice table in a database where you may create objects:

```sql
CREATE TABLE routine_order_items (
    order_id INTEGER NOT NULL,
    line_number INTEGER NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price_cents INTEGER NOT NULL CHECK (unit_price_cents >= 0),
    PRIMARY KEY (order_id, line_number)
);

INSERT INTO routine_order_items VALUES
    (101, 1, 2, 1500),
    (101, 2, 1, 2500),
    (102, 1, 1, 1500);
```

These rows reproduce the first two orders from the SQLite tutorial without requiring you to translate its whole setup.

## Define and call a function

```sql
CREATE FUNCTION bookstore_order_total(p_order_id INTEGER)
RETURNS BIGINT
LANGUAGE SQL
AS $$
    SELECT COALESCE(SUM(quantity * unit_price_cents::BIGINT), 0)
    FROM routine_order_items
    WHERE order_id = p_order_id;
$$;

SELECT bookstore_order_total(101) AS total_cents;
```

The expected result is `5500`.

Read the definition in order:

- `p_order_id` is the input parameter. The prefix distinguishes it from the table's `order_id` column.
- `RETURNS BIGINT` declares the result type.
- `LANGUAGE SQL` says the body is SQL code.
- `$$ ... $$` quotes the function body without escaping its internal quotes.
- `::BIGINT` converts the price before multiplication, avoiding the smaller integer type's multiplication range.
- `COALESCE(..., 0)` chooses zero when `SUM` has no input values.

This function also returns zero for an identifier with no items. That policy does **not** distinguish a missing order from an existing empty order. A production design must choose the intended behavior, perhaps checking an orders table or returning null.

PostgreSQL functions can return scalars or sets and can do more than arithmetic. Their allowed effects and declarations matter; do not assume every function is pure or evaluated just once. See the official [function documentation](https://www.postgresql.org/docs/current/sql-createfunction.html).

## Define and call a procedure

A procedure is invoked to perform an operation rather than used as an expression in a `SELECT`. This example creates another independent practice table:

```sql
CREATE TABLE routine_orders (
    order_id INTEGER PRIMARY KEY,
    status TEXT NOT NULL CHECK (status IN ('open', 'completed', 'cancelled'))
);

INSERT INTO routine_orders VALUES (101, 'completed'), (102, 'open');

CREATE PROCEDURE cancel_open_order(p_order_id INTEGER)
LANGUAGE SQL
AS $$
    UPDATE routine_orders
    SET status = 'cancelled'
    WHERE order_id = p_order_id AND status = 'open';
$$;

CALL cancel_open_order(102);
SELECT order_id, status FROM routine_orders ORDER BY order_id;
```

| order_id | status |
|---|---|
| 101 | completed |
| 102 | cancelled |

Calling it again changes nothing. The procedure also silently does nothing for a missing order or a completed order. That is this example's behavior, not proof that the requested cancellation succeeded. A richer routine can expose an outcome or raise an error.

This routine changes status only. It is not a complete cancellation workflow: it does not handle refunds or restock items. Keep the operation's name and contract specific enough for callers to understand what it guarantees.

## A routine is not a transaction boundary by itself

Calling a routine happens within database transaction rules. These examples do not contain an internal `COMMIT`; callers can group their calls with other statements using a transaction.

Procedural languages add variables, branches, loops, and error handling. PostgreSQL's **PL/pgSQL** is one such language. Its `BEGIN ... END` groups code; it is distinct from the SQL `BEGIN` that starts a transaction. PostgreSQL permits transaction control inside procedures only under specified calling conditions. See the official [procedure documentation](https://www.postgresql.org/docs/current/sql-createprocedure.html).

## Decide whether the database is the right home

A routine can centralize behavior used by several applications and reduce network round trips. It also introduces database code to version, deploy, debug, and test. An ordinary parameterized query or view may already be enough.

Do not assume a routine is faster because it is “precompiled.” Planning and plan reuse depend on the engine, language, and query. A routine still needs suitable indexes and efficient SQL.

Privileges also require an explicit design. PostgreSQL normally runs a routine with the caller's privileges (`SECURITY INVOKER`). `SECURITY DEFINER` uses the owner's privileges and needs careful control of object resolution and access. Merely moving a query into a routine does not automatically bypass table permissions or prevent injection in dynamically assembled SQL.

## Check your understanding

1. Why is the total function used in `SELECT`, while the cancellation procedure is invoked with `CALL`?
2. What does the total function return when no items match, and what ambiguity does that create?
3. Why does the cancellation procedure not guarantee a complete business cancellation?
4. Why does storing code in the database not guarantee better performance?

Next: [Triggers](08_triggers.md) explains code invoked automatically by data changes.
