## Aggregate Functions in SQL

Aggregate functions in SQL are powerful tools that allow you to perform calculations on a set of values to return a single scalar value. They are commonly used with the `GROUP BY` clause to group rows that share a common attribute and then perform calculations on each group. Aggregate functions are essential for data analysis, reporting, and generating insights from your data.

### Common Aggregate Functions

Here are the most commonly used aggregate functions in SQL:

- The `COUNT` function calculates the number of rows in a dataset that meet a specified condition or the total number of rows when no condition is provided.
- The `SUM` function adds together all the numeric values in a specified column.
- The `AVG` function computes the average of all numeric values in a column by dividing the sum of the values by the number of non-NULL entries.
- The `MIN` function identifies the smallest value in a dataset, including numeric, string, and date types.
- The `MAX` function returns the largest value in a dataset, similar to `MIN`, and supports numeric, string, and date types.

Let's explore each of these functions in detail with practical examples.

### Setting Up Example Tables

Suppose we have two tables: `Employees` and `Departments`.

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

### COUNT Function

The `COUNT` function returns the number of rows that match a specified condition.

#### Example: Counting Total Employees

```sql
SELECT COUNT(*) AS TotalEmployees
FROM Employees;
```

**Result**

| TotalEmployees |
|----------------|
| 5              |

#### Example: Counting Employees per Department

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

### SUM Function

The `SUM` function adds up all the values in a numeric column.

#### Example: Calculating Total Salary Expenditure

```sql
SELECT SUM(Salary) AS TotalSalary
FROM Employees;
```

**Result**

| TotalSalary |
|-------------|
| 322000      |

#### Example: Calculating Total Salary per Department

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

### AVG Function

The `AVG` function calculates the average value of a numeric column.

#### Example: Calculating Average Salary

```sql
SELECT AVG(Salary) AS AverageSalary
FROM Employees;
```

**Result**

| AverageSalary |
|---------------|
| 64400         |

#### Example: Calculating Average Salary per Department

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

### MIN and MAX Functions

The `MIN` and `MAX` functions return the smallest and largest values in a set, respectively.

#### Example: Finding Minimum and Maximum Salaries

```sql
SELECT MIN(Salary) AS MinimumSalary, MAX(Salary) AS MaximumSalary
FROM Employees;
```

**Result**

| MinimumSalary | MaximumSalary |
|---------------|---------------|
| 55000         | 72000         |

#### Example: Finding Minimum and Maximum Salaries per Department

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

### GROUP BY Clause

The `GROUP BY` clause is used with aggregate functions to group the result set by one or more columns.

#### Example: Counting Employees by Department Name

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

### HAVING Clause

The `HAVING` clause is used to filter groups based on a condition, similar to how the `WHERE` clause filters rows.

#### Example: Departments with More Than One Employee

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

### Combining Aggregate Functions

You can use multiple aggregate functions in a single query to get comprehensive insights.

#### Example: Employee Statistics per Department

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

### Dealing with NULL Values

Aggregate functions generally ignore `NULL` values except for the `COUNT(*)` function.

#### Example: Impact of NULL on Aggregate Functions

Suppose we have an additional employee with a `NULL` salary.

**Updated Employees Table**

| EmployeeID | FirstName | LastName | DepartmentID | Salary  |
|------------|-----------|----------|--------------|---------|
| 6          | Susan     | Miller   | 1            | NULL    |

#### Query: Calculating Average Salary with NULL Values

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

### Using DISTINCT with Aggregate Functions

The `DISTINCT` keyword can be used inside aggregate functions to consider only unique values.

#### Example: Counting Unique Salaries

```sql
SELECT COUNT(DISTINCT Salary) AS UniqueSalaries
FROM Employees;
```

**Result**

| UniqueSalaries |
|----------------|
| 5              |

The `COUNT(DISTINCT Salary)` function counts the number of unique salary values, excluding `NULL`.

### Aggregate Functions with Subqueries

Aggregate functions can be used in subqueries to compare individual rows to aggregate values.

#### Example: Employees Earning Above Average Salary

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
| Mike      | Johnson  | 70000  |
| Emily     | Davis    | 72000  |

- The subquery calculates the average salary.
- The outer query selects employees whose salary is greater than this average.

### Window Functions (Analytic Functions)

In addition to aggregate functions, SQL supports window functions that perform calculations across a set of rows related to the current row.

#### Example: Calculating Running Total of Salaries

```sql
SELECT
    EmployeeID,
    FirstName,
    LastName,
    Salary,
    SUM(Salary) OVER (ORDER BY EmployeeID) AS RunningTotal
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
| 6          | Susan     | Miller   | NULL   | NULL         |

- The `SUM(Salary) OVER (ORDER BY EmployeeID)` calculates a running total of salaries.
- `NULL` values are handled according to the window function's rules.

### Practical Tips for Using Aggregate Functions

- Assign meaningful aliases to aggregate results to improve the readability of the output.
- Apply the `WHERE` clause to filter rows before performing aggregation, ensuring only relevant data is included in calculations.
- Be mindful that most aggregate functions (e.g., `SUM`, `AVG`) ignore `NULL` values, which might lead to unexpected results.
- Limit the number of columns in the `GROUP BY` clause to only those essential for your analysis, as excessive grouping can increase query complexity and runtime.
- Use the `HAVING` clause to filter groups after aggregation, allowing conditions based on aggregated results.
