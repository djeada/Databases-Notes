## Stored Procedures and Functions

In the realm of relational databases, stored procedures and functions are powerful tools that allow developers to encapsulate reusable pieces of SQL code. They enhance performance by caching execution plans, promote code reusability, and keep business logic close to the data. By understanding how to create and use stored procedures and functions, you can write more efficient and maintainable database applications.

### Stored Procedures

A **stored procedure** is a pre-compiled collection of one or more SQL statements (plus optional control-of-flow logic) saved in the database under a single name. Procedures can

* accept **input** parameters,
* return **output** parameters (scalars),
* and/or return **result sets** (tables).

They shine when you need to run the same multi-statement operation repeatedly or enforce consistent business rules.

#### Advantages of Stored Procedures

| Benefit         | Why it matters                                                                                |
| --------------- | --------------------------------------------------------------------------------------------- |
| Performance     | Execution plan is compiled once and reused, reducing parsing/optimization overhead.           |
| Reusability     | One definition can be called from many places (apps, jobs, other procs).                      |
| Security        | GRANT rights on the procedure even if callers have no direct rights on the tables it touches. |
| Maintainability | Fix or extend business logic in one spot without redeploying application code.                |

#### Example Schema & Seed Data

To make our examples concrete, we’ll first create a simple `Customers` table and insert a couple of rows. This seed data will serve as the foundation for demonstrating stored procedure operations.

```sql
-- Customers table used in the examples
CREATE TABLE dbo.Customers
(
    CustomerID INT IDENTITY(1,1) PRIMARY KEY,
    FirstName  VARCHAR(50) NOT NULL,
    LastName   VARCHAR(50) NOT NULL,
    Email      VARCHAR(100) UNIQUE,
    Phone      VARCHAR(20) NULL
);

-- A couple of starter rows
INSERT INTO dbo.Customers (FirstName, LastName, Email, Phone) VALUES
('Alice', 'Smith', 'alice.smith@example.com', '555-0100'),
('Bob',   'Brown', 'bob.brown@example.com',  '555-0110');
```

*Current contents before we add anything else:*

| CustomerID | FirstName | LastName | Email                                                     | Phone    |
| ---------: | --------- | -------- | --------------------------------------------------------- | -------- |
|          1 | Alice     | Smith    | [alice.smith@example.com](mailto:alice.smith@example.com) | 555-0100 |
|          2 | Bob       | Brown    | [bob.brown@example.com](mailto:bob.brown@example.com)     | 555-0110 |

#### Creating a Stored Procedure

Creating a stored procedure involves specifying its name, parameters, and the logic to execute. The example below defines a procedure to insert a new customer and return its generated primary key.

```sql
CREATE PROCEDURE dbo.AddCustomer
    @FirstName  VARCHAR(50),
    @LastName   VARCHAR(50),
    @Email      VARCHAR(100),
    @CustomerID INT OUTPUT      -- Returns the newly created PK
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO dbo.Customers (FirstName, LastName, Email)
    VALUES (@FirstName, @LastName, @Email);

    -- Return the identity generated in THIS scope
    SET @CustomerID = SCOPE_IDENTITY();
END;
```

* `SET NOCOUNT ON;` keeps the “(1 row affected)” message from interfering with client libraries expecting a clean result set.
* `SCOPE_IDENTITY()` is safer than `@@IDENTITY` because it ignores inserts done by triggers further down the chain.

#### Calling the Stored Procedure

Once created, you invoke a stored procedure using `EXEC` (or `EXECUTE`). You can pass input values and capture any output parameters. The example below adds “John Doe” to our `Customers` table and retrieves the new ID.

```sql
DECLARE @NewID INT;

EXEC dbo.AddCustomer
     @FirstName  = 'John',
     @LastName   = 'Doe',
     @Email      = 'john.doe@example.com',
     @CustomerID = @NewID OUTPUT;

SELECT @NewID AS NewCustomerID;
```

*Sample output:*

| NewCustomerID |
| ------------: |
|             3 |

*Table contents afterwards:*

| CustomerID | FirstName | LastName | Email                                                     | Phone    |
| ---------: | --------- | -------- | --------------------------------------------------------- | -------- |
|          1 | Alice     | Smith    | [alice.smith@example.com](mailto:alice.smith@example.com) | 555-0100 |
|          2 | Bob       | Brown    | [bob.brown@example.com](mailto:bob.brown@example.com)     | 555-0110 |
|          3 | John      | Doe      | [john.doe@example.com](mailto:john.doe@example.com)       | **NULL** |

#### Modifying a Stored Procedure

As requirements evolve, you can alter an existing procedure to accept new parameters or change logic without dropping and recreating it. Here we add a `Phone` parameter so the procedure can store customer phone numbers as well.

```sql
ALTER PROCEDURE dbo.AddCustomer
    @FirstName  VARCHAR(50),
    @LastName   VARCHAR(50),
    @Email      VARCHAR(100),
    @Phone      VARCHAR(20),     -- NEW parameter
    @CustomerID INT OUTPUT
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO dbo.Customers (FirstName, LastName, Email, Phone)
    VALUES (@FirstName, @LastName, @Email, @Phone);

    SET @CustomerID = SCOPE_IDENTITY();
END;
```

*New call using the updated procedure:*

```sql
DECLARE @NewID INT;

EXEC dbo.AddCustomer
     @FirstName  = 'Carla',
     @LastName   = 'Mendez',
     @Email      = 'carla.mendez@example.com',
     @Phone      = '555-0122',
     @CustomerID = @NewID OUTPUT;

SELECT @NewID AS NewCustomerID;
```

| NewCustomerID |
| ------------: |
|             4 |

| CustomerID | FirstName | LastName | Email                                                       | Phone    |
| ---------: | --------- | -------- | ----------------------------------------------------------- | -------- |
|          … | …         | …        | …                                                           | …        |
|          4 | Carla     | Mendez   | [carla.mendez@example.com](mailto:carla.mendez@example.com) | 555-0122 |

#### Deleting a Stored Procedure

If a stored procedure is no longer needed or must be replaced entirely, you can drop it from the database. Be cautious—dependent code will break until it’s recreated.

```sql
DROP PROCEDURE dbo.AddCustomer;
```

> **Irreversible:** once dropped, dependent code will fail until the procedure is recreated.

### Functions

Functions in SQL Server let you encapsulate reusable logic that computes and returns a value or a table. Unlike stored procedures, functions can be embedded directly within queries—such as in `SELECT`, `WHERE`, or `JOIN` clauses—making them highly composable. They’re ideal for encapsulating calculations, formatting routines, or filtering logic that you want to reuse across multiple queries or views.

A **function** encapsulates logic that returns **exactly one** scalar value or a **table**. Unlike procedures, functions can be used inline in `SELECT`, `WHERE`, or `JOIN` clauses. They cannot use side-effects such as `INSERT`/`UPDATE` (with the exception of special CLR or system functions).

#### Types of Functions

SQL Server supports several function types, each suited to different scenarios. Scalar functions return a single value, while table-valued functions return result sets that you can query as if they were regular tables or views. Multi-statement TVFs allow more complex row-by-row processing but can incur more overhead.

| Type                       | Returns                                | Typical use-case                   |
| -------------------------- | -------------------------------------- | ---------------------------------- |
| Scalar                     | Single value                           | Calculations, formatting, lookups  |
| Inline table-valued (iTVF) | Table defined by one `SELECT`          | Reusable filtered views            |
| Multi-statement TVF        | Table assembled through multiple steps | Complex row-by-row transformations |

#### Advantages of Functions

Functions promote modularity and code reuse by abstracting complex computations behind a simple call. Inline TVFs, in particular, can yield performance benefits because the optimizer can expand them directly into the calling query.

* **Reusability & abstraction** – one central definition of complex math or business rules.
* **Composable** – drop straight into any expression, `JOIN`, or view.
* **Potential performance win** – especially inline TVFs, which the optimizer can treat almost like a view.

#### Example Schema & Seed Data for Functions

To illustrate functions, we’ll create a basic `Orders` table linked to our `Customers` table and populate it with sample orders. This provides a dataset for demonstrating both scalar and table-valued functions.

```sql
-- Orders table used in the examples
CREATE TABLE dbo.Orders
(
    OrderID    INT IDENTITY(1,1) PRIMARY KEY,
    CustomerID INT       NOT NULL FOREIGN KEY REFERENCES dbo.Customers(CustomerID),
    OrderDate  DATE      NOT NULL,
    Amount     DECIMAL(10,2) NOT NULL
);

INSERT INTO dbo.Orders (CustomerID, OrderDate, Amount) VALUES
(1, '2025-05-01', 120.00),
(1, '2025-05-03',  60.50),
(3, '2025-05-04', 210.75);
```

| OrderID | CustomerID | OrderDate  | Amount |
| ------: | ---------: | ---------- | -----: |
|       1 |          1 | 2025-05-01 | 120.00 |
|       2 |          1 | 2025-05-03 |  60.50 |
|       3 |          3 | 2025-05-04 | 210.75 |

#### Creating a **Scalar** Function

Scalar functions let you encapsulate formulae or lookups that return a single value. In the example below, we calculate sales tax based on an amount and tax rate.

```sql
CREATE FUNCTION dbo.CalculateTax
(
    @Amount   DECIMAL(10,2),
    @TaxRate  DECIMAL(5,2)   -- e.g. 8.25 means 8.25 %
)
RETURNS DECIMAL(10,2)
AS
BEGIN
    RETURN @Amount * (@TaxRate / 100);
END;
```

*Usage – compute sales tax in a query:*

```sql
SELECT
    OrderID,
    Amount,
    dbo.CalculateTax(Amount, 8.25) AS TaxAmount
FROM dbo.Orders;
```

| OrderID | Amount | TaxAmount |
| ------: | -----: | --------: |
|       1 | 120.00 |      9.90 |
|       2 |  60.50 |      4.99 |
|       3 | 210.75 |     17.38 |

#### Creating an **Inline Table-Valued** Function

Inline TVFs are essentially parameterized views. You define a single `SELECT` that returns a result set. The optimizer can integrate this directly into your queries for efficient execution.

```sql
CREATE FUNCTION dbo.GetCustomerOrders (@CustomerID INT)
RETURNS TABLE
AS
RETURN
(
    SELECT OrderID, OrderDate, Amount
    FROM   dbo.Orders
    WHERE  CustomerID = @CustomerID
);
```

*Querying orders for customer #1:*

```sql
SELECT *
FROM dbo.GetCustomerOrders(1);
```

| OrderID | OrderDate  | Amount |
| ------: | ---------- | -----: |
|       1 | 2025-05-01 | 120.00 |
|       2 | 2025-05-03 |  60.50 |

#### Modifying a Function

When you need to extend or tweak logic, you can alter an existing function. For example, adding a discount parameter to our tax calculation function allows for more flexible scenarios.

```sql
ALTER FUNCTION dbo.CalculateTax
(
    @Amount    DECIMAL(10,2),
    @TaxRate   DECIMAL(5,2),
    @Discount  DECIMAL(10,2) = 0  -- default 0
)
RETURNS DECIMAL(10,2)
AS
BEGIN
    RETURN (@Amount - @Discount) * (@TaxRate / 100);
END;
```

*Test the new logic:*

```sql
SELECT dbo.CalculateTax(100.00, 8.25, 10.00) AS TaxOnDiscounted100;
```

| TaxOnDiscounted100 |
| -----------------: |
|               7.43 |

#### Deleting a Function

If a function is obsolete or must be replaced entirely, you can remove it with `DROP`. As with stored procedures, any dependent code will break until the function is recreated.

```sql
DROP FUNCTION dbo.CalculateTax;
```

#### Differences Between Stored Procedures and Functions

- Functions are required to return a value, which can be scalar, table, or any defined data type, whereas stored procedures are not obligated to return a value but can use output parameters or return result sets.
- Functions can be directly used within SQL expressions, such as in `SELECT` or `WHERE` clauses, while stored procedures must be invoked independently and cannot be part of an SQL expression.
- Stored procedures can have side effects as they can modify the database state through operations like `INSERT`, `UPDATE`, or `DELETE`, whereas functions are typically designed to be deterministic and avoid modifying database state.

#### Best Practices

- Ensure naming conventions are consistent and descriptive, often beginning with verbs like `Get`, `Add`, `Update`, or `Calculate`, to clarify their purpose.
- Validate all input parameters within the procedure or function to prevent errors and ensure proper operation.
- Include robust error handling by using `TRY...CATCH` blocks to gracefully handle and log exceptions during execution.
- Assign appropriate permissions to procedures and functions to ensure secure access and protect sensitive data from unauthorized use.
1. **Name objects with schema prefixes** (`dbo.AddCustomer`) to avoid ambiguity.
2. **Use `SET NOCOUNT ON;`** inside procs to reduce unnecessary network traffic.
3. **Favor inline TVFs** over multi-statement TVFs when possible; they integrate more cleanly with the optimizer.
4. **Keep business rules in one place** – either in your procedures/functions *or* in application code, but avoid duplicating logic.
5. **Version-control your DDL** just like application code so changes are traceable and repeatable.
