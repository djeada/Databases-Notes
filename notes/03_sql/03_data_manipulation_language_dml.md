## Data Manipulation Language (DML)

Data Manipulation Language, or DML for short, is like the practical toolkit for interacting with the data stored in your database. If you think of a database as a filing cabinet full of information, DML provides the commands to add new files, update existing ones, retrieve information, and remove files you no longer need. These operations are essential for managing the day-to-day data needs of any application or system that relies on a database.

### The Core DML Statements

There are four fundamental DML commands that you'll use to manipulate data:

- The **SELECT** statement is used to retrieve data from one or more tables based on specified criteria.  
- The **INSERT** statement allows the addition of new records into a table by specifying values for the columns.  
- The **UPDATE** statement modifies existing data in a table by changing values in specified columns.  
- The **DELETE** statement removes records from a table based on specified conditions.

Let's explore each of these commands in detail, with examples that illustrate how they work and how you might use them in real-world scenarios.

### Retrieving Data with SELECT

The `SELECT` statement is perhaps the most commonly used SQL command. It allows you to query data from tables or views, specifying exactly what information you want to retrieve.

Imagine you have the following `employees` and `departments` tables in your database:

**employees**

| employee_id | first_name | last_name | date_of_birth | department_id |
|-------------|------------|-----------|---------------|---------------|
| 1           | John       | Doe       | 1990-01-01    | 1             |
| 2           | Jane       | Smith     | 1985-05-15    | 1             |
| 3           | Alice      | Johnson   | 1992-07-30    | 2             |

**departments**

| department_id | department_name |
|---------------|-----------------|
| 1             | Sales           |
| 2             | Marketing       |

Suppose you want to retrieve a list of employees along with their department names, sorted by their last names. You can write the following SQL query:

```sql
SELECT employees.first_name, employees.last_name, departments.department_name
FROM employees
JOIN departments ON employees.department_id = departments.department_id
ORDER BY employees.last_name;
```

**What's Happening Here:**

- The `SELECT` clause specifies the columns to retrieve: `first_name`, `last_name`, and `department_name`.
- The `FROM` clause indicates the primary table to query, which is `employees`.
- The `JOIN` operation combines rows from `employees` and `departments` based on a related column (`department_id`).
- The `ON` keyword specifies the condition for the join.
- The `ORDER BY` clause sorts the results by `last_name`.

**Resulting Data:**

| first_name | last_name | department_name |
|------------|-----------|-----------------|
| John       | Doe       | Sales           |
| Alice      | Johnson   | Marketing       |
| Jane       | Smith     | Sales           |

**Interpreting the Output:**

- The query returns each employee's first name, last name, and their department name.
- Employees are sorted alphabetically by their last names.
- The `JOIN` ensures that each employee is matched with the correct department.

This example demonstrates how `SELECT` can be used to retrieve and organize data from multiple tables.

### Adding New Records with INSERT

The `INSERT` statement allows you to add new rows to a table. This is useful when new data needs to be recorded, such as when a new employee is hired.

Let's say a new employee named Bob Brown joins the Marketing department. Here's how you can insert his information into the `employees` table:

```sql
INSERT INTO employees (employee_id, first_name, last_name, date_of_birth, department_id)
VALUES (4, 'Bob', 'Brown', '1988-03-20', 2);
```

**Understanding the Command:**

- `INSERT INTO` specifies the table to insert data into.
- The column names in parentheses indicate which columns you're providing values for.
- The `VALUES` clause lists the corresponding values for those columns.

**Updated employees Table:**

| employee_id | first_name | last_name | date_of_birth | department_id |
|-------------|------------|-----------|---------------|---------------|
| 1           | John       | Doe       | 1990-01-01    | 1             |
| 2           | Jane       | Smith     | 1985-05-15    | 1             |
| 3           | Alice      | Johnson   | 1992-07-30    | 2             |
| 4           | Bob        | Brown     | 1988-03-20    | 2             |

**What This Means:**

- Bob Brown has been added to the `employees` table.
- His `department_id` is 2, linking him to the Marketing department.
- The table now contains four employees.

### Modifying Existing Data with UPDATE

Data can change over time, and the `UPDATE` statement allows you to modify existing records. For example, if an employee changes departments, you'll need to update their `department_id`.

Suppose John Doe transfers from the Sales department (department_id 1) to the Marketing department (department_id 2). Here's how you can update his record:

```sql
UPDATE employees
SET department_id = 2
WHERE employee_id = 1;
```

**Breaking It Down:**

- `UPDATE employees` specifies the table to update.
- The `SET` clause indicates the new value for `department_id`.
- The `WHERE` clause ensures that only John Doe's record (employee_id 1) is updated.

**Updated employees Table:**

| employee_id | first_name | last_name | date_of_birth | department_id |
|-------------|------------|-----------|---------------|---------------|
| 1           | John       | Doe       | 1990-01-01    | 2             |
| 2           | Jane       | Smith     | 1985-05-15    | 1             |
| 3           | Alice      | Johnson   | 1992-07-30    | 2             |
| 4           | Bob        | Brown     | 1988-03-20    | 2             |

**Result of the Update:**

- John Doe's `department_id` has changed from 1 to 2.
- He is now part of the Marketing department.
- Other employees' records remain unchanged.

### Removing Records with DELETE

When data is no longer needed, the `DELETE` statement allows you to remove records from a table.

Imagine that Alice Johnson has left the company, and you need to delete her record from the `employees` table:

```sql
DELETE FROM employees
WHERE employee_id = 3;
```

**Explanation:**

- `DELETE FROM employees` specifies the table from which to delete records.
- The `WHERE` clause identifies the record to delete based on `employee_id`.

**Updated employees Table:**

| employee_id | first_name | last_name | date_of_birth | department_id |
|-------------|------------|-----------|---------------|---------------|
| 1           | John       | Doe       | 1990-01-01    | 2             |
| 2           | Jane       | Smith     | 1985-05-15    | 1             |
| 4           | Bob        | Brown     | 1988-03-20    | 2             |

**Outcome:**

- Alice Johnson's record has been removed.
- The table now contains three employees.
- Data integrity is maintained by only deleting the intended record.

### Enhancing Queries with Built-in Functions

SQL provides a variety of built-in functions that allow you to perform calculations, transform data, and aggregate results. These functions can be categorized as row functions, group functions, and conversion functions.

#### Row Functions

Row functions operate on individual rows, allowing you to manipulate data at a granular level. For example, you might want to convert text to lowercase for consistency.

**Example: Converting Last Names to Lowercase**

```sql
SELECT LOWER(last_name) AS lower_last_name
FROM employees;
```

**Result:**

| lower_last_name |
|-----------------|
| doe             |
| smith           |
| brown           |

**Explanation:**

- The `LOWER` function converts the `last_name` field to lowercase.
- The `AS` keyword renames the output column to `lower_last_name`.

#### Group Functions

Group functions perform calculations on sets of rows, often used with the `GROUP BY` clause to aggregate data.

**Example: Counting Employees per Department**

```sql
SELECT department_id, COUNT(*) AS num_employees
FROM employees
GROUP BY department_id;
```

**Result:**

| department_id | num_employees |
|---------------|---------------|
| 1             | 1             |
| 2             | 2             |

**Interpretation:**

- `COUNT(*)` tallies the number of employees in each department.
- The `GROUP BY` clause groups records by `department_id`.

#### Conversion Functions

Conversion functions change the data type of a value, which can be useful when combining different types of data.

**Example: Combining Text and Dates**

Suppose you want to create a sentence that includes an employee's last name and date of birth:

```sql
SELECT last_name || ' was born on ' || TO_CHAR(date_of_birth, 'YYYY-MM-DD') AS info
FROM employees;
```

**Result:**

| info                          |
|-------------------------------|
| Doe was born on 1990-01-01    |
| Smith was born on 1985-05-15  |
| Brown was born on 1988-03-20  |

**Explanation:**

- The `||` operator concatenates strings.
- `TO_CHAR` converts the `date_of_birth` to a string format.

#### Conditional Expressions

Conditional expressions like `CASE` allow you to apply logic within your queries.

**Example: Displaying Department Names**

```sql
SELECT employee_id, first_name, last_name,
       CASE department_id
           WHEN 1 THEN 'Sales'
           WHEN 2 THEN 'Marketing'
           ELSE 'Unknown'
       END AS department_name
FROM employees;
```

**Result:**

| employee_id | first_name | last_name | department_name |
|-------------|------------|-----------|-----------------|
| 1           | John       | Doe       | Marketing       |
| 2           | Jane       | Smith     | Sales           |
| 4           | Bob        | Brown     | Marketing       |

**Explanation:**

- The `CASE` expression checks the `department_id` and returns the corresponding department name.
- The `ELSE 'Unknown'` handles any `department_id` not explicitly listed.

### Practical Tips for Using DML Commands

When working with DML, it's important to use best practices to ensure data integrity and optimal performance.

- It is important to always include a `WHERE` clause in `UPDATE` and `DELETE` statements to target specific records; omitting it can unintentionally alter or delete all records in the table.  
- Queries should be tested in a development environment or with transactions to safely evaluate their effects before executing them on production data.  
- Regular backups of your database are essential to safeguard against data loss due to errors or system failures.  
- Understanding and using transactions allows you to group multiple operations into a single unit, ensuring that all operations either succeed together or fail together.

### Transactions in DML

Transactions are a crucial concept in database operations, ensuring that a series of DML statements are executed as a single unit of work.

**Example: Transferring an Employee Between Departments**

Suppose you need to transfer Bob Brown back to the Sales department and log this change:

```sql
START TRANSACTION;

UPDATE employees
SET department_id = 1
WHERE employee_id = 4;

INSERT INTO department_transfers (employee_id, from_department_id, to_department_id, transfer_date)
VALUES (4, 2, 1, CURRENT_DATE);

COMMIT;
```

**Explanation:**

- `START TRANSACTION` begins the transaction block.
- The `UPDATE` statement changes Bob's `department_id`.
- The `INSERT` logs the transfer in the `department_transfers` table.
- `COMMIT` saves the changes if all statements succeed.

If any statement fails, you can roll back the entire transaction:

```sql
ROLLBACK;
```

**Benefits:**

- Ensures data consistency.
- Prevents partial updates that could leave the database in an inconsistent state.
