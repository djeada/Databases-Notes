
## Stored Procedures and Functions

Stored procedures and functions are reusable pieces of SQL code that can be stored in the database and called by applications, triggers, or other SQL statements. They can improve performance, encapsulate business logic, and simplify complex queries.

## Stored Procedures

Stored procedures are named, precompiled SQL scripts that can accept input parameters and return output parameters or a result set. They are used primarily for data manipulation tasks.

### Creating a stored procedure

To create a stored procedure, use the CREATE PROCEDURE statement:

```sql
CREATE PROCEDURE procedure_name(param1 data_type, param2 data_type, ...)
AS
BEGIN
  -- SQL code
END;
```

### Calling a stored procedure

To call a stored procedure, use the CALL or EXECUTE statement:

```sql
CALL procedure_name(param1, param2, ...);
```

### Modifying a stored procedure

To modify a stored procedure, use the ALTER PROCEDURE statement:

```sql
ALTER PROCEDURE procedure_name(param1 data_type, param2 data_type, ...)
AS
BEGIN
  -- SQL code
END;
```

### Deleting a stored procedure

To delete a stored procedure, use the DROP PROCEDURE statement:

```sql
DROP PROCEDURE procedure_name;
```

## Functions

Functions are named, precompiled SQL scripts that can accept input parameters and return a single value. They are used primarily for data retrieval tasks and can be used in SELECT, WHERE, and HAVING clauses.

### Creating a function

To create a function, use the CREATE FUNCTION statement:

```sql
CREATE FUNCTION function_name(param1 data_type, param2 data_type, ...)
RETURNS data_type
AS
BEGIN
  -- SQL code
  RETURN value;
END;
```

### Calling a function

To call a function, use the function name and parameters in an SQL statement:

```sql
SELECT column1, column2, function_name(param1, param2, ...) AS result
FROM table_name;
```

### Modifying a function

To modify a function, use the ALTER FUNCTION statement:

```sql
ALTER FUNCTION function_name(param1 data_type, param2 data_type, ...)
RETURNS data_type
AS
BEGIN
  -- SQL code
  RETURN value;
END;
```

### Deleting a function

To delete a function, use the DROP FUNCTION statement:

```sql
DROP FUNCTION function_name;
```
