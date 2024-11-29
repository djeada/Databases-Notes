## Joins, Subqueries, and Views in SQL

Welcome to the fascinating world of SQL, where we can manipulate and retrieve data from relational databases using powerful tools like joins, subqueries, and views. These concepts are essential for anyone looking to master SQL and database management. Let's dive in and explore each of these techniques in detail, with examples to solidify your understanding.

### Joins: Combining Data from Multiple Tables

In relational databases, data is often spread across multiple tables to reduce redundancy and improve organization. However, there are times when we need to combine this data to get a complete picture. This is where **joins** come into play.

#### Understanding Joins

A **join** is an SQL operation that allows you to combine rows from two or more tables based on a related column between them. Think of joins as a way to connect tables "horizontally," bringing together related data to answer complex queries.

There are several types of joins:

- An **INNER JOIN** returns rows only when there is a matching value in both joined tables, excluding unmatched rows.  
- A **LEFT JOIN** (or **LEFT OUTER JOIN**) includes all rows from the left table and the matched rows from the right table, with NULLs for non-matching right-side rows.  
- A **RIGHT JOIN** (or **RIGHT OUTER JOIN**) includes all rows from the right table and the matched rows from the left table, with NULLs for non-matching left-side rows.  
- A **FULL JOIN** (or **FULL OUTER JOIN**) combines rows from both tables, including all matched and unmatched rows, filling in NULLs where no match exists.  

Let's explore each type with examples.

#### Setting Up Example Tables

We'll use two tables for our examples: `Employees` and `Departments`.

**Employees Table**

| EmployeeID | LastName | DepartmentID |
|------------|----------|--------------|
| 1          | Smith    | 1            |
| 2          | Johnson  | 1            |
| 3          | Brown    | 2            |
| 4          | Taylor   | NULL         |

**Departments Table**

| DepartmentID | DepartmentName           |
|--------------|--------------------------|
| 1            | Human Resources          |
| 2            | Information Technology   |
| 3            | Finance                  |

#### INNER JOIN

An **INNER JOIN** returns rows when there is a match in both tables. It's like finding the intersection of the two tables.

**SQL Query**

```sql
SELECT e.LastName, d.DepartmentName
FROM Employees AS e
INNER JOIN Departments AS d
ON e.DepartmentID = d.DepartmentID;
```

**Result**

| LastName | DepartmentName        |
|----------|-----------------------|
| Smith    | Human Resources       |
| Johnson  | Human Resources       |
| Brown    | Information Technology|

**Explanation**

- Only employees with a `DepartmentID` that matches an entry in the `Departments` table are returned.
- Employee Taylor is excluded because their `DepartmentID` is `NULL`.

#### LEFT JOIN (LEFT OUTER JOIN)

A **LEFT JOIN** returns all rows from the left table and matched rows from the right table. If there is no match, `NULL` values are returned for columns from the right table.

**SQL Query**

```sql
SELECT e.LastName, d.DepartmentName
FROM Employees AS e
LEFT JOIN Departments AS d
ON e.DepartmentID = d.DepartmentID;
```

**Result**

| LastName | DepartmentName        |
|----------|-----------------------|
| Smith    | Human Resources       |
| Johnson  | Human Resources       |
| Brown    | Information Technology|
| Taylor   | NULL                  |

**Explanation**

- All employees are returned.
- For Taylor, who doesn't have a `DepartmentID`, the `DepartmentName` is `NULL`.

#### RIGHT JOIN (RIGHT OUTER JOIN)

A **RIGHT JOIN** returns all rows from the right table and matched rows from the left table. If there is no match, `NULL` values are returned for columns from the left table.

**SQL Query**

```sql
SELECT e.LastName, d.DepartmentName
FROM Employees AS e
RIGHT JOIN Departments AS d
ON e.DepartmentID = d.DepartmentID;
```

**Result**

| LastName | DepartmentName        |
|----------|-----------------------|
| Smith    | Human Resources       |
| Johnson  | Human Resources       |
| Brown    | Information Technology|
| NULL     | Finance               |

**Explanation**

- All departments are returned.
- For the Finance department, there is no matching employee, so `LastName` is `NULL`.

#### FULL JOIN (FULL OUTER JOIN)

A **FULL JOIN** returns all rows when there is a match in one of the tables. If there is no match, `NULL` values are returned for the missing columns.

**Note**: Not all SQL implementations support `FULL JOIN`. In systems that don't, you can simulate it using a `UNION` of `LEFT JOIN` and `RIGHT JOIN`.

**SQL Query**

```sql
SELECT e.LastName, d.DepartmentName
FROM Employees AS e
FULL OUTER JOIN Departments AS d
ON e.DepartmentID = d.DepartmentID;
```

**Result**

| LastName | DepartmentName        |
|----------|-----------------------|
| Smith    | Human Resources       |
| Johnson  | Human Resources       |
| Brown    | Information Technology|
| Taylor   | NULL                  |
| NULL     | Finance               |

**Explanation**

- All employees and all departments are included.
- `Taylor` has no department (`DepartmentName` is `NULL`).
- The Finance department has no employees (`LastName` is `NULL`).

#### Cross Join

A **CROSS JOIN** returns the Cartesian product of the two tables, combining each row from the first table with every row from the second table.

**SQL Query**

```sql
SELECT e.LastName, d.DepartmentName
FROM Employees AS e
CROSS JOIN Departments AS d;
```

**Result**

This query would return 12 rows (4 employees × 3 departments), combining every employee with every department.

#### Visualizing Joins

SQL joins are powerful tools for combining data from two or more tables based on a related column. To better understand joins, let’s explore them visually and explain how they work.

##### Inner Join

An **Inner Join** retrieves only the rows that have matching values in both tables. For instance, if you have an `Employees` table with a `DepartmentID` column and a `Departments` table with the same column, an inner join will return only those employees who are associated with an existing department. Any rows in the `Employees` table without a matching `DepartmentID` in the `Departments` table (and vice versa) are excluded.

```
+-----------+         +--------------+
| Employees |         | Departments  |
+-----------+         +--------------+
     |                         |
     | Matching DepartmentID   |
     +-------------------------+
             |
             v
+-------------------------------+
|     Resulting Rows            |
| (Employees with matching Dept)|
+-------------------------------+
```

This join is useful when you’re interested solely in records with complete data from both sides. For example, to find employees who belong to a known department, you would use an inner join.

##### Left Join

A **Left Join** (or Left Outer Join) retrieves all rows from the left table (e.g., `Employees`) and the matching rows from the right table (e.g., `Departments`). If there’s no matching row in the right table, the result still includes the left table’s row, but with `NULL` values for the right table’s columns.

```
+-----------+         +--------------+
| Employees |         | Departments  |
+-----------+         +--------------+
     |                         |
     | Left table (all rows)   |
     +-------------------------+
             |
             v
+-------------------------------+
|     Resulting Rows            |
| (All Employees, with Dept info|
|  where available)             |
+-------------------------------+
```

For example, suppose you want a list of all employees, even those who are not currently assigned to a department. A left join ensures that even employees without a `DepartmentID` in the `Departments` table are included, with `NULL` filling in the missing department details.

##### Right Join

A **Right Join** (or Right Outer Join) retrieves all rows from the right table (e.g., `Departments`) and the matching rows from the left table (e.g., `Employees`). If there’s no matching row in the left table, the result includes the right table’s row with `NULL` values for the left table’s columns.

```
+-----------+         +--------------+
| Employees |         | Departments  |
+-----------+         +--------------+
     |                         |
     | Right table (all rows)  |
     +-------------------------+
             |
             v
+-------------------------------+
|     Resulting Rows            |
| (All Departments, with Emp info|
|  where available)             |
+-------------------------------+
```

This join is helpful when you want a list of all departments, regardless of whether they currently have any employees assigned to them. For instance, a right join can reveal departments with no staff.

##### Full Outer Join

A **Full Outer Join** retrieves all rows from both tables, combining matching rows where they exist. If a row in one table doesn’t have a match in the other, the result still includes it, with `NULL` values filling in the missing data from the unmatched table.

For example, a full outer join would provide a comprehensive view of all employees and all departments, including:

- Employees without departments (`NULL` in the department-related columns).
- Departments without employees (`NULL` in the employee-related columns).

```
+-----------+         +--------------+
| Employees |         | Departments  |
+-----------+         +--------------+
     |                         |
     | All rows from both      |
     +-------------------------+
             |
             v
+-------------------------------+
|     Resulting Rows            |
| (All Employees and Departments|
|  with matching where possible)|
+-------------------------------+
```

This join is ideal for scenarios where you want a complete overview of both datasets, even when some relationships are missing.

### Subqueries: Queries within Queries

Subqueries allow you to nest one query inside another, enabling you to perform complex data retrieval in a structured and organized way.

#### Understanding Subqueries

Subqueries can be used in various parts of an SQL statement:

- In the `SELECT` clause to compute a value.
- In the `FROM` clause as a table.
- In the `WHERE` clause to filter results based on dynamic criteria.

There are two main types:

- **Non-correlated subqueries** are independent of the outer query and can be executed separately, as they do not reference columns from the outer query.   
- **Correlated subqueries** depend on the outer query, referencing its columns and evaluating row by row, which can impact performance due to multiple executions.    

##### Example Tables

We'll use the following tables:

**Employees Table**

| EmployeeID | LastName | Salary |
|------------|----------|--------|
| 1          | Smith    | 3000   |
| 2          | Johnson  | 3500   |
| 3          | Brown    | 2700   |
| 4          | Taylor   | 4200   |

**Departments Table**

| DepartmentID | DepartmentName     |
|--------------|--------------------|
| 1            | Human Resources    |
| 2            | Information Technology|
| 3            | Finance            |

**DepartmentEmployees Table**

| DepartmentID | EmployeeID |
|--------------|------------|
| 1            | 1          |
| 1            | 2          |
| 2            | 3          |
| 3            | 4          |

#### Non-correlated Subquery Example

**Goal**: Find employees who earn more than the average salary.

**SQL Query**

```sql
SELECT EmployeeID, LastName, Salary
FROM Employees
WHERE Salary > (SELECT AVG(Salary) FROM Employees);
```

**Explanation**

- The subquery `(SELECT AVG(Salary) FROM Employees)` calculates the average salary.
- The outer query selects employees with a salary greater than this average.

**Result**

| EmployeeID | LastName | Salary |
|------------|----------|--------|
| 2          | Johnson  | 3500   |
| 4          | Taylor   | 4200   |

#### Correlated Subquery Example

**Goal**: Find employees who earn more than the average salary in their department.

**SQL Query**

```sql
SELECT e.EmployeeID, e.LastName, e.Salary, d.DepartmentName
FROM Employees AS e
JOIN DepartmentEmployees AS de ON e.EmployeeID = de.EmployeeID
JOIN Departments AS d ON de.DepartmentID = d.DepartmentID
WHERE e.Salary > (
    SELECT AVG(e2.Salary)
    FROM Employees AS e2
    JOIN DepartmentEmployees AS de2 ON e2.EmployeeID = de2.EmployeeID
    WHERE de2.DepartmentID = de.DepartmentID
);
```

**Explanation**

- The subquery calculates the average salary for the employee's department.
- The outer query selects employees whose salary is above this average.
- This is a correlated subquery because it depends on the `DepartmentID` from the outer query.

**Result**

| EmployeeID | LastName | Salary | DepartmentName     |
|------------|----------|--------|--------------------|
| 2          | Johnson  | 3500   | Human Resources    |
| 4          | Taylor   | 4200   | Finance            |

#### Subquery in SELECT Clause

**Goal**: Display each employee's salary and the average salary across all employees.

**SQL Query**

```sql
SELECT
    EmployeeID,
    LastName,
    Salary,
    (SELECT AVG(Salary) FROM Employees) AS AverageSalary
FROM Employees;
```

**Result**

| EmployeeID | LastName | Salary | AverageSalary |
|------------|----------|--------|---------------|
| 1          | Smith    | 3000   | 3350          |
| 2          | Johnson  | 3500   | 3350          |
| 3          | Brown    | 2700   | 3350          |
| 4          | Taylor   | 4200   | 3350          |

#### Using EXISTS with Subqueries

**Goal**: Find departments that have employees.

**SQL Query**

```sql
SELECT DepartmentName
FROM Departments AS d
WHERE EXISTS (
    SELECT 1
    FROM DepartmentEmployees AS de
    WHERE de.DepartmentID = d.DepartmentID
);
```

**Explanation**

- The `EXISTS` clause checks if the subquery returns any rows.
- If it does, the department is included in the result.

**Result**

| DepartmentName        |
|-----------------------|
| Human Resources       |
| Information Technology|
| Finance               |

#### Common Table Expressions (CTEs)

CTEs are similar to subqueries but are defined before the main query using the `WITH` keyword, providing better readability.

**Example**

```sql
WITH DepartmentSalaries AS (
    SELECT de.DepartmentID, AVG(e.Salary) AS AvgSalary
    FROM Employees AS e
    JOIN DepartmentEmployees AS de ON e.EmployeeID = de.EmployeeID
    GROUP BY de.DepartmentID
)
SELECT d.DepartmentName, ds.AvgSalary
FROM Departments AS d
JOIN DepartmentSalaries AS ds ON d.DepartmentID = ds.DepartmentID;
```

**Result**

| DepartmentName        | AvgSalary |
|-----------------------|-----------|
| Human Resources       | 3250      |
| Information Technology| 2700      |
| Finance               | 4200      |

### Views: Creating Virtual Tables

A **view** is a virtual table that is based on the result set of an SQL query. Views simplify complex queries, enhance security by limiting data access, and can improve performance in certain situations.

#### Creating a View

**Goal**: Create a view that shows employee details along with their department names.

**SQL Query**

```sql
CREATE VIEW EmployeeDetails AS
SELECT e.EmployeeID, e.LastName, e.Salary, d.DepartmentName
FROM Employees AS e
JOIN DepartmentEmployees AS de ON e.EmployeeID = de.EmployeeID
JOIN Departments AS d ON de.DepartmentID = d.DepartmentID;
```

**Explanation**

- The view `EmployeeDetails` encapsulates the join logic.
- Users can query `EmployeeDetails` as if it were a table.

### Querying a View

**SQL Query**

```sql
SELECT * FROM EmployeeDetails
WHERE Salary > 3000;
```

**Result**

| EmployeeID | LastName | Salary | DepartmentName     |
|------------|----------|--------|--------------------|
| 2          | Johnson  | 3500   | Human Resources    |
| 4          | Taylor   | 4200   | Finance            |

#### Advantages of Using Views

- Complex queries can be simplified for end-users.
- Restrict access to specific data by exposing only certain columns or rows.
- Centralize query logic; changes in the underlying tables require updates only in the view.

#### Updating a View

If you need to modify a view, you can use `CREATE OR REPLACE VIEW`.

**SQL Query**

```sql
CREATE OR REPLACE VIEW EmployeeDetails AS
SELECT e.EmployeeID, e.LastName, e.Salary, d.DepartmentName, de.DepartmentID
FROM Employees AS e
JOIN DepartmentEmployees AS de ON e.EmployeeID = de.EmployeeID
JOIN Departments AS d ON de.DepartmentID = d.DepartmentID;
```

The view now includes the `DepartmentID` column.

#### Deleting a View

To remove a view from the database:

```sql
DROP VIEW EmployeeDetails;
```

**Note**: Deleting a view does not affect the underlying data.

#### Updatable Views

Some databases allow views to be updatable, meaning you can perform `INSERT`, `UPDATE`, or `DELETE` operations on the view, which then affect the underlying tables. Certain conditions must be met:

- The view must reference exactly one table.
- The view must include all NOT NULL columns without default values.
- The view must not contain GROUP BY, HAVING, or DISTINCT clauses.

**Example**

Assuming our view meets the criteria:

```sql
UPDATE EmployeeDetails
SET Salary = Salary * 1.05
WHERE EmployeeID = 3;
```

This would increase Brown's salary by 5% in the `Employees` table.
