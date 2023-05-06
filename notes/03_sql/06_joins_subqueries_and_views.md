## Joins, Subqueries, and Views
Views, joins, and subqueries are techniques used in SQL to manipulate and retrieve data from databases.

* **Joins**: Joins are used to combine rows from multiple tables based on a related column. They help retrieve data from different tables that share a relationship. Common types of joins include inner join, left join, right join, and full join.
* **Subqueries**: A subquery is an SQL query nested inside another query. Subqueries help break down complex queries into smaller, more manageable parts. They can be used in SELECT, WHERE, or HAVING clauses and can return a single value, a list of values, or a table.
* **Views**: A view is a virtual table that represents the result of an SQL query. It doesn't store data but references data in the underlying tables. Views can simplify complex queries, restrict access to specific data, and improve performance.

## Joins

Joins are used to combine rows from multiple tables based on a related column.

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

## Subqueries

Subqueries are SQL queries nested inside another query. They can be used in `SELECT`, `WHERE`, or `HAVING` clauses and can return a single value, a list of values, or a table.

There are two types of subqueries:

- Non-correlated subquery: a subquery that can be run independently and doesn't depend on the outer query
- Correlated subquery: a subquery that depends on the outer query and is executed once for each row of the outer query

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

This updated view now includes the `Department_ID` in addition to the previous columns.

### Deleting a view

To delete a view, use the `DROP VIEW` statement:

```sql
DROP VIEW EmployeeDepartmentView;
```

Dropping a view does not affect the underlying tables or data. It only removes the view definition.

