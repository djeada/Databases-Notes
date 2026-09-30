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

## Return a table when the result contains several rows

Continue with the PostgreSQL `routine_order_items` setup. A table-returning function can expose a report with an input threshold:

```sql
-- PostgreSQL
CREATE FUNCTION bookstore_large_orders(p_min_cents BIGINT)
RETURNS TABLE (order_id INTEGER, total_cents BIGINT)
LANGUAGE SQL
STABLE
AS $$
    SELECT i.order_id,
           SUM(i.quantity * i.unit_price_cents::BIGINT)::BIGINT
    FROM routine_order_items AS i
    GROUP BY i.order_id
    HAVING SUM(i.quantity * i.unit_price_cents::BIGINT) >= p_min_cents;
$$;

SELECT order_id, total_cents
FROM bookstore_large_orders(5000)
ORDER BY order_id;
```

The result is order 101 with 5500 cents. The function belongs in `FROM` because it supplies rows. The scalar total function belongs in an expression because it supplies one value. PostgreSQL's sum over `BIGINT` returns `NUMERIC`, so this function explicitly converts its total to the declared output type. A total beyond `BIGINT` range would fail; choose a numeric contract if that range is insufficient.

`STABLE` tells PostgreSQL that the function's result can depend on reads but will not modify the database and has stability within a statement under its documented snapshot rules. It is not a cache that keeps yesterday's report forever. `IMMUTABLE` would be inappropriate for a total that changes when table data changes.

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

## Make the cancellation contract report a rejected operation

The original procedure silently ignores a completed or missing order. A PL/pgSQL procedure can make that outcome explicit. Order 102 is already cancelled from the earlier exercise, so add an open order for this one:

```sql
-- PostgreSQL
INSERT INTO routine_orders VALUES (104, 'open');

CREATE PROCEDURE cancel_open_order_checked(p_order_id INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE routine_orders
    SET status = 'cancelled'
    WHERE order_id = p_order_id AND status = 'open';
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Order % is missing or is not open', p_order_id;
    END IF;
END;
$$;

CALL cancel_open_order_checked(104);
SELECT order_id, status FROM routine_orders WHERE order_id = 104;
```

The row is `104, cancelled`. `FOUND` records whether the preceding update affected a row. Calling this checked procedure again raises an exception. Its contract treats an already cancelled order as an error; another workflow could intentionally report “already cancelled” as a successful idempotent outcome. Decide that policy before naming the interface.

Run the failing call separately. If it occurs inside a transaction, recover with rollback before continuing. PL/pgSQL's `BEGIN ... END` groups procedural statements; it does not commit the update on its own. The caller can still roll back a successful call.

## A routine is not a transaction boundary by itself

Calling a routine happens within database transaction rules. These examples do not contain an internal `COMMIT`; callers can group their calls with other statements using a transaction.

Procedural languages add variables, branches, loops, and error handling. PostgreSQL's **PL/pgSQL** is one such language. Its `BEGIN ... END` groups code; it is distinct from the SQL `BEGIN` that starts a transaction. PostgreSQL permits transaction control inside procedures only under specified calling conditions. See the official [procedure documentation](https://www.postgresql.org/docs/current/sql-createprocedure.html).

## Decide whether the database is the right home

A routine can centralize behavior used by several applications and reduce network round trips. It also introduces database code to version, deploy, debug, and test. An ordinary parameterized query or view may already be enough.

Do not assume a routine is faster because it is “precompiled.” Planning and plan reuse depend on the engine, language, and query. A routine still needs suitable indexes and efficient SQL.

Privileges also require an explicit design. PostgreSQL normally runs a routine with the caller's privileges (`SECURITY INVOKER`). `SECURITY DEFINER` uses the owner's privileges and needs careful control of object resolution and access. Merely moving a query into a routine does not automatically bypass table permissions or prevent injection in dynamically assembled SQL.

## See how SQL Server expresses an output parameter

The original idea of a stored routine also appears in SQL Server, but its syntax differs substantially. This **standalone SQL Server** example uses T-SQL; `GO` is a batch separator interpreted by clients such as SSMS and `sqlcmd`, not a SQL statement sent through every driver:

```sql
-- SQL Server; run in SSMS or sqlcmd
CREATE TABLE dbo.RoutineCustomers (
    CustomerId INT IDENTITY(1, 1) PRIMARY KEY,
    CustomerName NVARCHAR(100) NOT NULL
);
GO
CREATE PROCEDURE dbo.AddRoutineCustomer
    @CustomerName NVARCHAR(100),
    @NewCustomerId INT OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    INSERT INTO dbo.RoutineCustomers (CustomerName)
    VALUES (@CustomerName);
    SET @NewCustomerId = CONVERT(INT, SCOPE_IDENTITY());
END;
GO
DECLARE @CreatedId INT;
EXEC dbo.AddRoutineCustomer
    @CustomerName = N'Dana',
    @NewCustomerId = @CreatedId OUTPUT;
SELECT CustomerId, CustomerName
FROM dbo.RoutineCustomers
WHERE CustomerId = @CreatedId;
GO
```

In this fresh table the result is customer 1, Dana. An output parameter returns a value separately from a result set. Both the definition and the call mark it `OUTPUT`. `SCOPE_IDENTITY()` retrieves the identity generated in the current scope; using a global or session-wide “latest ID” without understanding triggers and other inserts can retrieve the wrong value.

Identity values can have gaps. A failed or rolled-back insert does not make an identity sequence a gapless receipt-number service. Use a dedicated, correctly coordinated numbering process if a business rule requires gapless document numbers.

## Choose the interface by the caller's needs

| Interface | Typical call | Suitable result |
| --- | --- | --- |
| View | `SELECT ... FROM view_name` | A reusable query without input parameters. |
| Scalar function | `SELECT function_name(argument)` | One value used in an expression. |
| Table-returning function | `SELECT ... FROM function_name(argument)` | A parameterized relation. |
| Procedure | PostgreSQL `CALL`, SQL Server `EXEC` | An explicitly invoked operation with its engine's output mechanisms. |

SQL Server also has scalar functions and inline or multi-statement table-valued functions. Their optimizer behavior and restrictions differ; a multi-statement function should not be assumed to optimize like a view. PostgreSQL procedures can have output parameters and can sometimes control transactions, but only in documented call contexts. A function that is part of a surrounding SQL statement cannot independently commit the caller's transaction.

## Version routines as part of the schema

PostgreSQL identifies overloaded functions by their name and input argument types. Two functions can share a name while accepting different types. Dropping one requires identifying the intended signature:

```sql
-- PostgreSQL; cleanup after the exercises
DROP FUNCTION bookstore_large_orders(BIGINT);
DROP PROCEDURE cancel_open_order_checked(INTEGER);
```

`CREATE OR REPLACE FUNCTION` can update a compatible body, but it cannot arbitrarily change the existing function's return type. Changing an interface may require a new routine and a migration of its callers. Deployment order matters if a new application expects a routine the database has not received yet.

Keep object resolution explicit, especially with `SECURITY DEFINER`. An attacker-controlled object found through an unsafe `search_path` can change privileged behavior. Review execute grants as well as table grants, because PostgreSQL grants routine execution to `PUBLIC` by default unless changed. Parameterization is still necessary for any dynamic SQL; a routine that concatenates input into SQL can be injectable.

Choose routines when centralizing the behavior helps multiple clients or gives a clear database interface. Keep test cases for valid inputs, missing rows, permission failures, and rollback. Moving complex business code into a database does not eliminate its maintenance cost.

References: [PostgreSQL function volatility](https://www.postgresql.org/docs/current/xfunc-volatility.html), [SQL Server CREATE PROCEDURE](https://learn.microsoft.com/en-us/sql/t-sql/statements/create-procedure-transact-sql), and [SQL Server SCOPE_IDENTITY](https://learn.microsoft.com/en-us/sql/t-sql/functions/scope-identity-transact-sql).

## Check your understanding

1. Why is the total function used in `SELECT`, while the cancellation procedure is invoked with `CALL`?
2. What does the total function return when no items match, and what ambiguity does that create?
3. Why does the cancellation procedure not guarantee a complete business cancellation?
4. Why does storing code in the database not guarantee better performance?

Next: [Triggers](08_triggers.md) explains code invoked automatically by data changes.
