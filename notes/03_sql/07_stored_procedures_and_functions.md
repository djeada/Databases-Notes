## Stored Procedures and Functions in SQL

In the realm of relational databases, stored procedures and functions are powerful tools that allow developers to encapsulate reusable pieces of SQL code. They enhance performance, promote code reusability, and encapsulate business logic within the database itself. By understanding how to create and use stored procedures and functions, you can write more efficient and maintainable database applications.

### Stored Procedures

A **stored procedure** is a precompiled collection of SQL statements and optional control-of-flow statements, stored under a name and processed as a unit. They can accept input parameters, return output parameters, and even return a result set of records. Stored procedures are primarily used for performing repetitive tasks and complex operations that involve multiple SQL statements.

#### Advantages of Stored Procedures

- Stored procedures often execute faster than dynamic SQL queries because they are precompiled and stored in the database, improving performance.
- They promote code reusability by allowing multiple applications to call the same procedure, reducing redundancy in code.
- Security is enhanced as permissions can be granted directly on stored procedures, limiting access to underlying tables and data.
- Maintainability is improved since business logic is centralized within the database, simplifying updates and ensuring consistency across applications.

#### Creating a Stored Procedure

To create a stored procedure, you use the `CREATE PROCEDURE` statement. The exact syntax may vary slightly depending on the database system, but the general structure is as follows:

```sql
CREATE PROCEDURE procedure_name
    @param1 data_type,
    @param2 data_type OUTPUT,
    ...
AS
BEGIN
    -- SQL statements
    -- You can include control-of-flow statements like IF, WHILE, etc.
END;
```

**Example:**

Suppose we have a `Customers` table, and we want to create a stored procedure to insert a new customer.

```sql
CREATE PROCEDURE AddCustomer
    @FirstName VARCHAR(50),
    @LastName VARCHAR(50),
    @Email VARCHAR(100),
    @CustomerID INT OUTPUT
AS
BEGIN
    INSERT INTO Customers (FirstName, LastName, Email)
    VALUES (@FirstName, @LastName, @Email);

    SET @CustomerID = SCOPE_IDENTITY();
END;
```

- `AddCustomer` is the name of the stored procedure.
- It accepts `@FirstName`, `@LastName`, and `@Email` as input parameters.
- `@CustomerID` is an output parameter that returns the ID of the newly inserted customer.
- `SCOPE_IDENTITY()` retrieves the last identity value inserted into an identity column in the same scope.

#### Calling a Stored Procedure

To execute a stored procedure, you use the `EXEC` or `EXECUTE` statement (in some systems, you can also use `CALL`).

**Example:**

```sql
DECLARE @NewCustomerID INT;

EXEC AddCustomer
    @FirstName = 'John',
    @LastName = 'Doe',
    @Email = 'john.doe@example.com',
    @CustomerID = @NewCustomerID OUTPUT;

SELECT @NewCustomerID AS 'New Customer ID';
```

- We declare a variable `@NewCustomerID` to receive the output parameter.
- We execute the `AddCustomer` procedure, passing in the values for the new customer.
- We specify `@CustomerID = @NewCustomerID OUTPUT` to capture the output parameter.
- Finally, we select the new customer ID to verify the insertion.

#### Modifying a Stored Procedure

If you need to change the logic inside a stored procedure, you can use the `ALTER PROCEDURE` statement.

**Example:**

```sql
ALTER PROCEDURE AddCustomer
    @FirstName VARCHAR(50),
    @LastName VARCHAR(50),
    @Email VARCHAR(100),
    @Phone VARCHAR(20),          -- Added new parameter
    @CustomerID INT OUTPUT
AS
BEGIN
    INSERT INTO Customers (FirstName, LastName, Email, Phone)
    VALUES (@FirstName, @LastName, @Email, @Phone);

    SET @CustomerID = SCOPE_IDENTITY();
END;
```

- We've added a new input parameter `@Phone`.
- The `INSERT` statement now includes the `Phone` column.

#### Deleting a Stored Procedure

To remove a stored procedure from the database, you use the `DROP PROCEDURE` statement.

**Example:**

```sql
DROP PROCEDURE AddCustomer;
```

**Caution:** Dropping a stored procedure is irreversible, and any applications relying on it will fail unless the procedure is recreated.

### Functions

A **function** in SQL is a database object that encapsulates a set of SQL statements and returns a single value. Functions can be used in SQL statements wherever expressions are allowed, such as in `SELECT`, `WHERE`, or `HAVING` clauses. They are primarily used for computations and data retrieval.

#### Types of Functions

- **Scalar functions** return a single value, often used for tasks such as calculating tax or formatting dates.
- **Table-valued** functions return a table data type, allowing them to be used in `FROM` clauses as though they were tables.

#### Advantages of Functions

- Functions can be reused across multiple queries, which helps minimize code duplication and promotes consistency.
- Complex calculations or logic can be encapsulated within functions, enhancing modularity and simplifying query design.
- Functions can simplify queries by abstracting repetitive logic and, in certain scenarios, may improve performance by reducing redundant computation.

#### Creating a Scalar Function

To create a function, use the `CREATE FUNCTION` statement.

**Example:**

Suppose we need a function to calculate the sales tax for a given amount.

```sql
CREATE FUNCTION CalculateTax
(
    @Amount DECIMAL(10, 2),
    @TaxRate DECIMAL(4, 2)
)
RETURNS DECIMAL(10, 2)
AS
BEGIN
    DECLARE @TaxAmount DECIMAL(10, 2);
    SET @TaxAmount = @Amount * (@TaxRate / 100);
    RETURN @TaxAmount;
END;
```

- `CalculateTax` is the name of the function.
- It accepts `@Amount` and `@TaxRate` as input parameters.
- It returns a `DECIMAL(10, 2)` value representing the calculated tax.
- The function calculates the tax amount and returns it.

#### Using the Function in a Query

You can use the function in SQL statements as follows:

```sql
SELECT OrderID, Amount, dbo.CalculateTax(Amount, 8.25) AS TaxAmount
FROM Orders;
```

For each order, we calculate the tax amount using the `CalculateTax` function with a tax rate of 8.25%.

#### Creating a Table-Valued Function

Table-valued functions return a table data type.

**Example:**

Suppose we want a function that returns all orders for a given customer.

```sql
CREATE FUNCTION GetCustomerOrders
(
    @CustomerID INT
)
RETURNS TABLE
AS
RETURN
(
    SELECT OrderID, OrderDate, Amount
    FROM Orders
    WHERE CustomerID = @CustomerID
);
```

**Using the Table-Valued Function:**

```sql
SELECT * FROM dbo.GetCustomerOrders(123);
```

#### Modifying a Function

To change a function, use the `ALTER FUNCTION` statement.

**Example:**

```sql
ALTER FUNCTION CalculateTax
(
    @Amount DECIMAL(10, 2),
    @TaxRate DECIMAL(4, 2),
    @Discount DECIMAL(10, 2) = 0      -- Added optional parameter with default value
)
RETURNS DECIMAL(10, 2)
AS
BEGIN
    DECLARE @TaxAmount DECIMAL(10, 2);
    SET @TaxAmount = (@Amount - @Discount) * (@TaxRate / 100);
    RETURN @TaxAmount;
END;
```

- Added an optional parameter `@Discount`.
- The tax is now calculated on the discounted amount.

#### Deleting a Function

To remove a function, use the `DROP FUNCTION` statement.

**Example:**

```sql
DROP FUNCTION CalculateTax;
```

#### Differences Between Stored Procedures and Functions

- Functions are required to return a value, which can be scalar, table, or any defined data type, whereas stored procedures are not obligated to return a value but can use output parameters or return result sets.
- Functions can be directly used within SQL expressions, such as in `SELECT` or `WHERE` clauses, while stored procedures must be invoked independently and cannot be part of an SQL expression.
- Stored procedures can have side effects as they can modify the database state through operations like `INSERT`, `UPDATE`, or `DELETE`, whereas functions are typically designed to be deterministic and avoid modifying database state.

#### Best Practices for Using Stored Procedures and Functions

- Ensure naming conventions are consistent and descriptive, often beginning with verbs like `Get`, `Add`, `Update`, or `Calculate`, to clarify their purpose.
- Validate all input parameters within the procedure or function to prevent errors and ensure proper operation.
- Include robust error handling by using `TRY...CATCH` blocks to gracefully handle and log exceptions during execution.
- Assign appropriate permissions to procedures and functions to ensure secure access and protect sensitive data from unauthorized use.
