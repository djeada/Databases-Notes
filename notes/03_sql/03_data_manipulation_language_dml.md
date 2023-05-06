## Data Manipulation Language (DML)

Data Manipulation Language (DML) is a subset of SQL that deals with manipulating and querying data stored in database tables. DML statements include `SELECT`, `INSERT`, `UPDATE`, and `DELETE`.

### Common DML Statements

- `SELECT`: used to query data from tables or views
- `INSERT`: used to insert new rows into a table
- `UPDATE`: used to modify existing rows in a table
- `DELETE`: used to delete rows from a table

### SELECT

The `SELECT` statement is used to retrieve data from one or more tables or views. It can include various clauses like `WHERE`, `ORDER BY`, `GROUP BY`, and `HAVING` to filter, sort, and aggregate data. Additionally, when querying multiple tables, refer to them using table_name.column_name syntax.

Example:

| employee_id | first_name | last_name | date_of_birth | department_id |
|-------------|------------|-----------|---------------|---------------|
| 1           | John       | Doe       | 1990-01-01    | 1             |
| 2           | Jane       | Smith     | 1985-05-15    | 1             |
| 3           | Alice      | Johnson   | 1992-07-30    | 2             |


```sql
SELECT employees.first_name, employees.last_name, departments.department_name
FROM employees, departments
WHERE employees.department_id = departments.department_id
ORDER BY employees.last_name;
```
Result:

| first_name | last_name | department_id |
|------------|-----------|---------------|
| John       | Doe       | 1             |
| Jane       | Smith     | 1             |

### INSERT

The `INSERT` statement is used to add new rows to a table. You can specify the column names and the corresponding values to be inserted.

Example:

| employee_id | first_name | last_name | date_of_birth | department_id |
|-------------|------------|-----------|---------------|---------------|
| 1           | John       | Doe       | 1990-01-01    | 1             |
| 2           | Jane       | Smith     | 1985-05-15    | 1             |
| 3           | Alice      | Johnson   | 1992-07-30    | 2             |

```sql
INSERT INTO employees (employee_id, first_name, last_name, date_of_birth, department_id)
VALUES (1, 'John', 'Doe', '1990-01-01', 1);
```
Table after `INSERT`:

| employee_id | first_name | last_name | date_of_birth | department_id |
|-------------|------------|-----------|---------------|---------------|
| 1           | John       | Doe       | 1990-01-01    | 1             |
| 2           | Jane       | Smith     | 1985-05-15    | 1             |
| 3           | Alice      | Johnson   | 1992-07-30    | 2             |
| 4           | Bob        | Brown     | 1980-03-20    | 2             |

### UPDATE

The `UPDATE` statement is used to modify existing rows in a table. You can set new values for specific columns and use the WHERE clause to filter the rows to be updated.

Example:

| employee_id | first_name | last_name | date_of_birth | department_id |
|-------------|------------|-----------|---------------|---------------|
| 1           | John       | Doe       | 1990-01-01    | 1             |
| 2           | Jane       | Smith     | 1985-05-15    | 1             |
| 3           | Alice      | Johnson   | 1992-07-30    | 2             |

```sql
UPDATE employees
SET department_id = 2
WHERE employee_id = 1;
```

Table after `UPDATE`:

| employee_id | first_name | last_name | date_of_birth | department_id |
|-------------|------------|-----------|---------------|---------------|
| 1           | John       | Doe       | 1990-01-01    | 2             |
| 2           | Jane       | Smith     | 1985-05-15    | 1             |
| 3           | Alice      | Johnson   | 1992-07-30    | 2             |

### DELETE

The `DELETE` statement is used to remove rows from a table. You can use the WHERE clause to specify which rows should be deleted.

Example:

| employee_id | first_name | last_name | date_of_birth | department_id |
|-------------|------------|-----------|---------------|---------------|
| 1           | John       | Doe       | 1990-01-01    | 1             |
| 2           | Jane       | Smith     | 1985-05-15    | 1             |
| 3           | Alice      | Johnson   | 1992-07-30    | 2             |

```sql
DELETE FROM employees
WHERE department_id = 2;
```

Table after `DELETE`:

| employee_id | first_name | last_name | date_of_birth | department_id |
|-------------|------------|-----------|---------------|---------------|
| 1           | John       | Doe       | 1990-01-01    | 1             |
| 2           | Jane       | Smith     | 1985-05-15    | 1             |

## Built-in SQL Functions

SQL provides built-in functions to transform, calculate, or create new data based on existing values. These functions can be divided into:

* `Row functions`: operate on values of a single record
* `Group functions`: operate on values of multiple records

### Row Functions

Row functions can be placed in the `SELECT` or `WHERE` clauses.

Example:

```sql
SELECT
    LOWER(last_name) AS lower_last_name
FROM employees;
```

### Group Functions

Group functions can be used in conjunction with the `GROUP BY` clause.

Example:

```sql
SELECT department_id, COUNT(*) AS num_employees
FROM employees
GROUP BY department_id;
```

### Conversion Functions

Conversion functions, such as `CAST` and `CONVERT`, are used to change data types of values.

Example:

```sql
SELECT last_name + ' has been with us since: ' + CAST(hire_date AS varchar(100)) AS info
FROM employees;
```

### Conditional Expressions

The `CASE` expression allows for conditional logic in SQL queries. It can be simple or searched, with the following syntax:

I. Simple:

| employee_id | first_name | last_name | date_of_birth | department_id |
|-------------|------------|-----------|---------------|---------------|
| 1           | John       | Doe       | 1990-01-01    | 1             |
| 2           | Jane       | Smith     | 1985-05-15    | 1             |
| 3           | Alice      | Johnson   | 1992-07-30    | 2             |

```sql
SELECT employee_id, first_name, last_name,
       CASE department_id
           WHEN 1 THEN 'IT'
           WHEN 2 THEN 'HR'
           ELSE 'Unknown'
       END as department
FROM employees;
```

Result:

| employee_id | first_name | last_name | department |
|-------------|------------|-----------|------------|
| 1           | John       | Doe       | IT         |
| 2           | Jane       | Smith     | IT         |
| 3           | Alice      | Johnson   | HR         |


II. Searched:


```sql
SELECT employee_id, first_name, last_name, department_id,
       CASE
           WHEN department_id = 1 THEN 'IT'
           WHEN department_id = 2 THEN 'HR'
           ELSE 'Unknown'
       END as department
FROM employees;
```

Result:

| employee_id | first_name | last_name | department_id | department |
|-------------|------------|-----------|---------------|------------|
| 1           | John       | Doe       | 1             | IT         |
| 2           | Jane       | Smith     | 1             | IT         |
| 3           | Alice      | Johnson   | 2             | HR         |

