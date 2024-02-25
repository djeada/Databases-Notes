## Joins, Subqueries, and Views
Views, joins, and subqueries are techniques used in SQL to manipulate and retrieve data from databases.

* **Joins**: Joins are used to combine rows from multiple tables based on a related column. They help retrieve data from different tables that share a relationship. Common types of joins include inner join, left join, right join, and full join.
* **Subqueries**: A subquery is an SQL query nested inside another query. Subqueries help break down complex queries into smaller, more manageable parts. They can be used in SELECT, WHERE, or HAVING clauses and can return a single value, a list of values, or a table.
* **Views**: A view is a virtual table that represents the result of an SQL query. It doesn't store data but references data in the underlying tables. Views can simplify complex queries, restrict access to specific data, and improve performance.

## Joins

Joins in SQL are essential for combining rows from two or more tables based on a common field between them. Think of joins as a way to connect tables "horizontally," similar to placing bricks side by side, each brick representing a table.

Here's a simplified way to understand different types of joins:

- **INNER JOIN**: Retrieves rows with an exact match in both tables. It's like finding a common area where both tables overlap.

- **OUTER JOIN**: Includes rows with an exact match and also those rows from one or both tables that do not have a matching counterpart in the other table. There are three types:
  - **LEFT OUTER JOIN (or LEFT JOIN)**: Includes all rows from the left table and matched rows from the right table. If there is no match, NULL values are used to fill in columns from the right table.
  - **RIGHT OUTER JOIN (or RIGHT JOIN)**: Includes all rows from the right table and matched rows from the left table. If there is no match, NULL values are used to fill in columns from the left table.
  - **FULL OUTER JOIN (or FULL JOIN)**: Combines the results of both LEFT JOIN and RIGHT JOIN. It includes all rows from both tables, with NULLs in place where there is no match.

Example Tables:

I. Employees table

| ID | lastname | Department_ID |
| -- | -------- | ------------- |
| 1 | Smith | 1 |
| 2 | Johnson | 1 |
| 3 | Brown | 2 |
| 4 | Taylor | NULL |

II. Departments table

| ID | department_name |
| -- | --------------- |
| 1 | HR |
| 2 | IT |
| 3 | Finance |

### INNER JOIN

`INNER JOIN`: returns rows where there's a match in both tables

```sql
SELECT e.lastname, d.department_name
FROM Employees AS e
INNER JOIN Departments AS d
ON e.Department_ID = d.ID
```

Result:

| lastname | department_name |
| -------- | --------------- |
| Smith | HR |
| Johnson | HR |
| Brown | IT |

### LEFT JOIN

`LEFT JOIN` / `LEFT OUTER JOIN`: returns all rows from the left table and matched rows from the right table; if no match, NULL values are returned

```sql
SELECT d.id, d.department_name, e.lastname
FROM Departments AS d
LEFT JOIN Employees AS e
ON d.Id = e.Department_ID
```
Result:

| id | department_name | lastname |
| -- | --------------- | -------- |
| 1 | HR | Smith |
| 1 | HR | Johnson |
| 2 | IT | Brown |
| 3 | Finance | NULL |

### RIGHT JOIN

`RIGHT JOIN` / `RIGHT OUTER JOIN`: returns all rows from the right table and matched rows from the left table; if no match, NULL values are returned

```sql
SELECT d.id, d.department_name, e.lastname
FROM Departments AS d
RIGHT JOIN Employees AS e
ON d.Id = e.Department_ID
```

Result (id, department_name, lastname):

| id | department_name | lastname |
| -- | --------------- | -------- |
| 1 | HR | Smith |
| 1 | HR | Johnson |
| 2 | IT | Brown |
| NULL | NULL | Taylor |

### FULL JOIN  

`FULL JOIN` / `FULL OUTER JOIN`: returns all rows when there's a match in either the left or right table; if no match, NULL values are returned

```sql
SELECT d.id, d.department_name, e.lastname
FROM Departments AS d
FULL JOIN Employees AS e
ON d.Id = e.Department_ID
```

Result:

| id | department_name | lastname |
| -- | --------------- | -------- |
| 1 | HR | Smith |
| 1 | HR | Johnson |
| 2 | IT | Brown |
| 3 | Finance | NULL |
| NULL | NULL | Taylor |

## Subqueries in SQL

Subqueries are a powerful feature in SQL, allowing you to use one query inside another. They are particularly useful in `SELECT`, `WHERE`, or `HAVING` clauses and can return various types of results: a single value, a list of values, or an entire table.

Here's a more intuitive way to understand subqueries:

1. Think of SQL as a language that operates on sets of data. A table is a set of data, and so is the result of a query.
2. Subqueries essentially say, "Take the result of this query, treat it as a temporary table (often giving it a name), and then use it as if it were a regular table."
3. This approach aligns with how Common Table Expressions (CTEs) work, providing a named temporary result set that you can reference within a SQL statement.

There are two main types of subqueries:

- **Non-correlated subqueries**: These are standalone queries that can be executed independently of the outer query. They are evaluated once and their result is used by the outer query.
   
- **Correlated subqueries**: These depend on data from the outer query. Unlike non-correlated subqueries, a correlated subquery is executed repeatedly, once for each row processed by the outer query. This is because its result can vary depending on the row from the outer query.


Example Tables:

I. Employees table 

| ID | lastname | salary |
| -- | -------- | ------ |
| 1 | Smith | 3000 |
| 2 | Johnson | 3500 |
| 3 | Brown | 2700 |
| 4 | Taylor | 4200 |

II. Departments table 

| ID | department_name |
| -- | --------------- |
| 1 | HR |
| 2 | IT |
| 3 | Finance |

III. Department Employees table 

| Department_ID | Employee_ID |
| ------------- | ----------- |
| 1 | 1 |
| 1 | 2 |
| 2 | 3 |
| 3 | 4 |

Example 1: Non-correlated subquery (used in WHERE clause)

Here, the subquery calculates the average salary from the Employees table and returns a single value. The outer query then retrieves employees who have a salary greater than this average.

```sql
SELECT e.ID, e.lastname, e.salary
FROM Employees AS e
WHERE e.salary > (SELECT AVG(salary) FROM Employees);
```

Result:

| ID | lastname | salary |
| -- | -------- | ------ |
| 2 | Johnson | 3500 |
| 4 | Taylor | 4200 |

Example 2: Correlated subquery (used in WHERE clause)

```sql
SELECT e.ID, e.lastname, e.salary, d.department_name
FROM Employees AS e
INNER JOIN Department_Employees AS de ON e.ID = de.Employee_ID
INNER JOIN Departments AS d ON de.Department_ID = d.ID
WHERE e.salary > (SELECT AVG(salary) FROM Employees AS e2 WHERE e2.ID = de.Employee_ID);
```

In this case, the subquery calculates the average salary for each employee by referencing data from the outer query (e2.ID = de.Employee_ID). The outer query then retrieves employees whose salary is above this calculated average and displays the department name as well.

Result: 

| ID | lastname | salary | department_name |
| -- | -------- | ------ | --------------- |
| 1 | Smith | 3000 | HR |
| 3 | Brown | 2700 | IT |

## Views

A view is a virtual table based on the result of an SQL query. It doesn't store data but references the data in the underlying tables. Views can be used to simplify complex queries, restrict access to specific data, and improve performance through materialized views.

I. Employees table 

| ID | lastname | salary |
| -- | -------- | ------ |
| 1 | Smith | 3000 |
| 2 | Johnson | 3500 |
| 3 | Brown | 2700 |
| 4 | Taylor | 4200 |

II. Departments table 

| ID | department_name |
| -- | --------------- |
| 1 | HR |
| 2 | IT |
| 3 | Finance |

III. Department Employees table 

| Department_ID | Employee_ID |
| ------------- | ----------- |
| 1 | 1 |
| 1 | 2 |
| 2 | 3 |
| 3 | 4 |

### Creating a view

To create a view, use the `CREATE VIEW` statement:

```sql
CREATE VIEW EmployeeDepartmentView AS
SELECT e.ID, e.lastname, e.salary, d.department_name
FROM Employees AS e
INNER JOIN Department_Employees AS de ON e.ID = de.Employee_ID
INNER JOIN Departments AS d ON de.Department_ID = d.ID;
```

Result (View):

| ID | lastname | salary | department_name |
| -- | -------- | ------ | --------------- |
| 1  | Smith    | 3000   | HR              |
| 2  | Johnson  | 3500   | HR              |
| 3  | Brown    | 2700   | IT              |
| 4  | Taylor   | 4200   | Finance         |

This view shows the employee ID, lastname, salary, and department name for each employee.

### Querying a view

To query a view, use the SELECT statement:

```sql
SELECT ID, lastname, salary, department_name
FROM EmployeeDepartmentView
WHERE salary > 3000;
```

Result:

| ID | lastname | salary | department_name |
| -- | -------- | ------ | --------------- |
| 2 | Johnson | 3500 | HR |
| 4 | Taylor | 4200 | Finance |

### Updating a view

To update a view, use the `CREATE OR REPLACE VIEW` statement:

```sql
CREATE OR REPLACE VIEW EmployeeDepartmentView AS
SELECT e.ID, e.lastname, e.salary, d.department_name, de.Department_ID
FROM Employees AS e
INNER JOIN Department_Employees AS de ON e.ID = de.Employee_ID
INNER JOIN Departments AS d ON de.Department_ID = d.ID;
```

Result:

| ID | lastname | salary | department_name | Department_ID |
| -- | -------- | ------ | --------------- | ------------- |
| 1  | Smith    | 3000   | HR              | 1             |
| 2  | Johnson  | 3500   | HR              | 1             |
| 3  | Brown    | 2700   | IT              | 2             |
| 4  | Taylor   | 4200   | Finance         | 3             |

This updated view now includes the `Department_ID` in addition to the previous columns.

### Deleting a view

To delete a view, use the `DROP VIEW` statement:

```sql
DROP VIEW EmployeeDepartmentView;
```

Dropping a view does not affect the underlying tables or data. It only removes the view definition.
