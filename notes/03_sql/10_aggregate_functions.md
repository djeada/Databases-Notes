# Aggregate Functions in SQL

An **aggregate** calculates one result from several rows. `SUM` adds values, `COUNT` counts them, and `AVG` calculates their average. Without grouping, one aggregate can summarize the whole input. With `GROUP BY`, it summarizes each group separately.

For example, the bookstore's order items become one total per order when grouped by `order_id`. In this chapter, a separate employee dataset makes grouped salary calculations and missing values easy to inspect. Read [joins and subqueries](06_joins_subqueries_and_views.md) first.

Work through `COUNT`, `SUM`, and `AVG` before combining them with joins and `HAVING`. `WHERE` filters input rows; `HAVING` filters the resulting groups. The final window-function example prepares for the next chapter.

## Common Aggregate Functions

Here are the most commonly used aggregate functions in SQL:

- The `COUNT` function calculates the number of rows in a dataset that meet a specified condition or the total number of rows when no condition is provided.
- The `SUM` function adds together all the numeric values in a specified column.
- The `AVG` function computes the average of all numeric values in a column by dividing the sum of the values by the number of non-NULL entries.
- The `MIN` function identifies the smallest value in a dataset, including numeric, string, and date types.
- The `MAX` function returns the largest value in a dataset, similar to `MIN`, and supports numeric, string, and date types.

## Setting Up Example Tables

Run this setup once in a **fresh SQLite database**. It is separate from the bookstore database. Continue using this same database through the chapter; the null-value section explicitly adds one more employee.

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE Departments (
    DepartmentID INTEGER PRIMARY KEY,
    DepartmentName TEXT NOT NULL
);
CREATE TABLE Employees (
    EmployeeID INTEGER PRIMARY KEY,
    FirstName TEXT NOT NULL,
    LastName TEXT NOT NULL,
    DepartmentID INTEGER NOT NULL REFERENCES Departments(DepartmentID),
    Salary REAL
);
INSERT INTO Departments VALUES
    (1, 'Human Resources'), (2, 'Engineering'), (3, 'Marketing');
INSERT INTO Employees VALUES
    (1, 'John', 'Doe', 1, 60000),
    (2, 'Jane', 'Smith', 1, 65000),
    (3, 'Mike', 'Johnson', 2, 70000),
    (4, 'Emily', 'Davis', 2, 72000),
    (5, 'David', 'Wilson', 3, 55000);
```

`REAL` keeps the arithmetic simple for this demonstration; production money fields need an intentional exact representation and rounding policy. The initial tables contain:

**Employees Table**

| EmployeeID | FirstName | LastName | DepartmentID | Salary |
|------------|-----------|----------|--------------|--------|
| 1          | John      | Doe      | 1            | 60000  |
| 2          | Jane      | Smith    | 1            | 65000  |
| 3          | Mike      | Johnson  | 2            | 70000  |
| 4          | Emily     | Davis    | 2            | 72000  |
| 5          | David     | Wilson   | 3            | 55000  |

**Departments Table**

| DepartmentID | DepartmentName      |
|--------------|---------------------|
| 1            | Human Resources     |
| 2            | Engineering         |
| 3            | Marketing           |

## COUNT Function

The `COUNT` function returns the number of rows that match a specified condition.

### Example: Counting Total Employees

```sql
SELECT COUNT(*) AS TotalEmployees
FROM Employees;
```

**Result**

| TotalEmployees |
|----------------|
| 5              |

### Example: Counting Employees per Department

```sql
SELECT DepartmentID, COUNT(*) AS NumberOfEmployees
FROM Employees
GROUP BY DepartmentID;
```

**Result**

| DepartmentID | NumberOfEmployees |
|--------------|-------------------|
| 1            | 2                 |
| 2            | 2                 |
| 3            | 1                 |

- The `GROUP BY` clause groups the rows by `DepartmentID`.
- The `COUNT(*)` function counts the number of employees in each department.

## SUM Function

The `SUM` function adds up all the values in a numeric column.

### Example: Calculating Total Salary Expenditure

```sql
SELECT SUM(Salary) AS TotalSalary
FROM Employees;
```

**Result**

| TotalSalary |
|-------------|
| 322000      |

### Example: Calculating Total Salary per Department

```sql
SELECT DepartmentID, SUM(Salary) AS TotalSalary
FROM Employees
GROUP BY DepartmentID;
```

**Result**

| DepartmentID | TotalSalary |
|--------------|-------------|
| 1            | 125000      |
| 2            | 142000      |
| 3            | 55000       |

The `SUM(Salary)` function calculates the total salary for each department.

## AVG Function

The `AVG` function calculates the average value of a numeric column.

### Example: Calculating Average Salary

```sql
SELECT AVG(Salary) AS AverageSalary
FROM Employees;
```

**Result**

| AverageSalary |
|---------------|
| 64400         |

### Example: Calculating Average Salary per Department

```sql
SELECT DepartmentID, AVG(Salary) AS AverageSalary
FROM Employees
GROUP BY DepartmentID;
```

**Result**

| DepartmentID | AverageSalary |
|--------------|---------------|
| 1            | 62500         |
| 2            | 71000         |
| 3            | 55000         |

The `AVG(Salary)` function computes the average salary for each department.

## MIN and MAX Functions

The `MIN` and `MAX` functions return the smallest and largest values in a set, respectively.

### Example: Finding Minimum and Maximum Salaries

```sql
SELECT MIN(Salary) AS MinimumSalary, MAX(Salary) AS MaximumSalary
FROM Employees;
```

**Result**

| MinimumSalary | MaximumSalary |
|---------------|---------------|
| 55000         | 72000         |

### Example: Finding Minimum and Maximum Salaries per Department

```sql
SELECT DepartmentID, MIN(Salary) AS MinimumSalary, MAX(Salary) AS MaximumSalary
FROM Employees
GROUP BY DepartmentID;
```

**Result**

| DepartmentID | MinimumSalary | MaximumSalary |
|--------------|---------------|---------------|
| 1            | 60000         | 65000         |
| 2            | 70000         | 72000         |
| 3            | 55000         | 55000         |

The `MIN(Salary)` and `MAX(Salary)` functions find the lowest and highest salaries in each department.

## GROUP BY Clause

The `GROUP BY` clause is used with aggregate functions to group the result set by one or more columns.

### Example: Counting Employees by Department Name

To make the results more readable, let's join the `Employees` and `Departments` tables.

```sql
SELECT d.DepartmentName, COUNT(*) AS NumberOfEmployees
FROM Employees e
JOIN Departments d ON e.DepartmentID = d.DepartmentID
GROUP BY d.DepartmentName;
```

**Result**

| DepartmentName   | NumberOfEmployees |
|------------------|-------------------|
| Human Resources  | 2                 |
| Engineering      | 2                 |
| Marketing        | 1                 |

- The `JOIN` clause combines the `Employees` and `Departments` tables.
- The `GROUP BY` clause groups the results by `DepartmentName`.

## HAVING Clause

The `HAVING` clause is used to filter groups based on a condition, similar to how the `WHERE` clause filters rows.

### Example: Departments with More Than One Employee

```sql
SELECT DepartmentID, COUNT(*) AS NumberOfEmployees
FROM Employees
GROUP BY DepartmentID
HAVING COUNT(*) > 1;
```

**Result**

| DepartmentID | NumberOfEmployees |
|--------------|-------------------|
| 1            | 2                 |
| 2            | 2                 |

The `HAVING` clause filters groups where the count of employees is greater than one.

## Combining Aggregate Functions

You can use multiple aggregate functions in a single query to get comprehensive insights.

### Example: Employee Statistics per Department

```sql
SELECT
    d.DepartmentName,
    COUNT(*) AS NumberOfEmployees,
    MIN(e.Salary) AS MinimumSalary,
    MAX(e.Salary) AS MaximumSalary,
    AVG(e.Salary) AS AverageSalary,
    SUM(e.Salary) AS TotalSalary
FROM Employees e
JOIN Departments d ON e.DepartmentID = d.DepartmentID
GROUP BY d.DepartmentName;
```

**Result**

| DepartmentName   | NumberOfEmployees | MinimumSalary | MaximumSalary | AverageSalary | TotalSalary |
|------------------|-------------------|---------------|---------------|---------------|-------------|
| Human Resources  | 2                 | 60000         | 65000         | 62500         | 125000      |
| Engineering      | 2                 | 70000         | 72000         | 71000         | 142000      |
| Marketing        | 1                 | 55000         | 55000         | 55000         | 55000       |

The query provides a comprehensive overview of salary statistics for each department.

## Dealing with NULL Values

Aggregate functions generally ignore `NULL` values except for the `COUNT(*)` function.

### Example: Impact of NULL on Aggregate Functions

Now add an employee whose salary is unknown. Run this insert once before the remaining examples:

```sql
INSERT INTO Employees VALUES (6, 'Susan', 'Miller', 1, NULL);
```

**The additional row**

| EmployeeID | FirstName | LastName | DepartmentID | Salary  |
|------------|-----------|----------|--------------|---------|
| 6          | Susan     | Miller   | 1            | NULL    |

### Query: Calculating Average Salary with NULL Values

```sql
SELECT DepartmentID, AVG(Salary) AS AverageSalary
FROM Employees
GROUP BY DepartmentID;
```

**Result**

| DepartmentID | AverageSalary |
|--------------|---------------|
| 1            | 62500         |
| 2            | 71000         |
| 3            | 55000         |

- The `AVG` function ignores the `NULL` salary for Susan Miller.
- The average salary for department 1 remains the same.

## Using DISTINCT with Aggregate Functions

The `DISTINCT` keyword can be used inside aggregate functions to consider only unique values.

### Example: Counting Unique Salaries

```sql
SELECT COUNT(DISTINCT Salary) AS UniqueSalaries
FROM Employees;
```

**Result**

| UniqueSalaries |
|----------------|
| 5              |

The `COUNT(DISTINCT Salary)` function counts the number of unique salary values, excluding `NULL`.

## Aggregate Functions with Subqueries

Aggregate functions can be used in subqueries to compare individual rows to aggregate values.

### Example: Employees Earning Above Average Salary

```sql
SELECT FirstName, LastName, Salary
FROM Employees
WHERE Salary > (
    SELECT AVG(Salary)
    FROM Employees
);
```

**Result**

| FirstName | LastName | Salary |
|-----------|----------|--------|
| Jane      | Smith    | 65000  |
| Mike      | Johnson  | 70000  |
| Emily     | Davis    | 72000  |

- The subquery calculates the average salary.
- The outer query selects employees whose salary is greater than this average.

## Window Functions (Analytic Functions)

In addition to aggregate functions, SQL supports window functions that perform calculations across a set of rows related to the current row.

### Example: Calculating Running Total of Salaries

```sql
SELECT
    EmployeeID,
    FirstName,
    LastName,
    Salary,
    SUM(Salary) OVER (ORDER BY EmployeeID ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS RunningTotal
FROM Employees;
```

**Result**

| EmployeeID | FirstName | LastName | Salary | RunningTotal |
|------------|-----------|----------|--------|--------------|
| 1          | John      | Doe      | 60000  | 60000        |
| 2          | Jane      | Smith    | 65000  | 125000       |
| 3          | Mike      | Johnson  | 70000  | 195000       |
| 4          | Emily     | Davis    | 72000  | 267000       |
| 5          | David     | Wilson   | 55000  | 322000       |
| 6          | Susan     | Miller   | NULL   | 322000       |

- The `SUM(Salary) OVER (ORDER BY EmployeeID)` calculates a running total of salaries.
- `SUM` ignores Susan’s null salary, so the running total remains 322000.

## Practical Tips for Using Aggregate Functions

- Assign meaningful aliases to aggregate results to improve the readability of the output.
- Apply the `WHERE` clause to filter rows before performing aggregation, ensuring only relevant data is included in calculations.
- Be mindful that most aggregate functions (e.g., `SUM`, `AVG`) ignore `NULL` values, which might lead to unexpected results.
- Limit the number of columns in the `GROUP BY` clause to only those essential for your analysis, as excessive grouping can increase query complexity and runtime.
- Use the `HAVING` clause to filter groups after aggregation, allowing conditions based on aggregated results.

## Distinguish no rows, unknown values, and a known zero

A report with no qualifying salaries has a different input from a report containing employees whose salaries are unknown:

```sql
SELECT COUNT(*) AS row_count,
       COUNT(Salary) AS known_salary_count,
       SUM(Salary) AS salary_sum,
       AVG(Salary) AS salary_average,
       COALESCE(SUM(Salary), 0) AS displayed_sum
FROM Employees
WHERE EmployeeID < 0;
```

The result is `0, 0, NULL, NULL, 0`. An aggregate without `GROUP BY` still returns a result row on empty input: counts are zero, while `SUM` and `AVG` are null. With a grouping key, empty input has no groups and therefore produces no result rows.

Displaying zero may be appropriate for “no payroll entries this period.” It can be misleading for “payroll total unavailable,” so choose the fallback from the report's meaning. `AVG(COALESCE(Salary, 0))` treats unknown salaries as actual zero salaries and changes the denominator. `COALESCE(AVG(Salary), 0)` leaves unknown salaries out of the calculation and only replaces an absent final average. These expressions answer different questions.

## Count known and missing values together

Continue after the earlier null-value section has inserted Susan, whose salary is null. A conditional aggregate makes completeness visible beside the report:

```sql
SELECT DepartmentID,
       COUNT(*) AS employee_count,
       COUNT(Salary) AS known_salary_count,
       SUM(CASE WHEN Salary IS NULL THEN 1 ELSE 0 END) AS missing_salary_count
FROM Employees
GROUP BY DepartmentID
ORDER BY DepartmentID;
```

Human Resources has 3 employees, 2 known salaries, and 1 missing salary. Engineering has 2, 2, 0; Marketing has 1, 1, 0. `CASE` produces one or zero for every input row, then `SUM` counts the selected condition. This technique generalizes to approved orders, overdue invoices, or available stock while keeping one row per reporting group.

PostgreSQL and SQLite also support aggregate `FILTER` clauses, but `CASE` is widely portable. If a left join is used to include empty departments, account for its null-extended row: `COUNT(*)` would count that preserved row, and a null-salary condition could confuse “no employee” with “employee with missing salary.” Test the employee ID's presence as well.

## Define the report's grain and unit before summing

A sum is meaningful only when each input row represents the intended fact once. Employee salary is annual pay in this example. Summing it does not calculate the cost of a particular month unless the report defines the conversion, employment dates, and other adjustments. Likewise, different currencies should not be added as if they shared one unit.

Joining Employees to a table of projects can duplicate an employee who has several projects. Summing salary after that join then counts their salary several times. If the report needs payroll per department, aggregate the employees independently. If it needs allocated payroll per project, store and validate an allocation rule rather than deduplicating arbitrary result values.

`SUM(DISTINCT Salary)` does not repair this problem. John and another employee can legitimately earn the same amount; distinct salary values would count that shared amount only once. Deduplication must use the identity of the fact being counted, not merely its numeric value.

## Filter groups after deciding which employees belong

For “departments with at least two known salaries above 60000,” apply the salary requirement to rows first:

```sql
SELECT DepartmentID, COUNT(*) AS qualifying_employees
FROM Employees
WHERE Salary > 60000
GROUP BY DepartmentID
HAVING COUNT(*) >= 2
ORDER BY DepartmentID;
```

Only Engineering qualifies, with 2 employees. Jane qualifies individually in Human Resources, but John at exactly 60000 does not pass the strict inequality, and Susan's unknown salary does not pass either. `HAVING` tests the resulting group count. Moving `Salary > 60000` into an arbitrary non-grouped expression changes or invalidates the query.

An index on a selective filter can reduce the input to aggregate, but an aggregate still needs an appropriate plan to group or sort that input. A report over almost every row can legitimately use a scan. Inspect the actual plan and workload rather than indexing every aggregated column.

## Review questions

1. What are aggregate functions in SQL, and how are they typically used with the `GROUP BY` clause?
2. How does the `COUNT` function work, and what is the difference between `COUNT(*)` and `COUNT(column)`?
3. In what scenarios would you use the `SUM`, `AVG`, `MIN`, and `MAX` functions, and how do they operate on data?
4. What is the purpose of the `HAVING` clause, and how does it differ from the `WHERE` clause when filtering aggregated data?
5. How do window functions differ from aggregate functions, and what are some practical applications of window functions in SQL?
