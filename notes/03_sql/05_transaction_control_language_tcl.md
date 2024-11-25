# Transaction Control Language (TCL)

In the world of databases, maintaining data integrity and consistency is crucial, especially when multiple operations are involved. Imagine you're at a bank's ATM, transferring money from your savings to your checking account. You wouldn't want the system to deduct the amount from your savings without adding it to your checking due to some error, right? This is where Transaction Control Language (TCL) comes into play, ensuring that all related operations either complete successfully together or fail without affecting the database's consistency.

## Understanding Transactions

A transaction is a sequence of one or more SQL statements that are executed as a single unit of work. The primary goal is to ensure that either all operations within the transaction are completed successfully or none are, preserving the database's integrity.

### The ACID Properties

Transactions adhere to the ACID properties:

- **Atomicity**: Ensures that all operations within a transaction are completed; if not, the transaction is aborted.
- **Consistency**: Guarantees that a transaction brings the database from one valid state to another, maintaining all predefined rules.
- **Isolation**: Ensures that concurrent transactions occur independently without interference.
- **Durability**: Once a transaction is committed, the changes are permanent, even in the case of a system failure.

## Key TCL Commands

TCL provides several commands to manage transactions effectively:

- `BEGIN TRANSACTION`
- `COMMIT`
- `ROLLBACK`
- `SAVEPOINT`
- `ROLLBACK TO SAVEPOINT`

Let's delve into each of these commands with examples to understand how they work.

### BEGIN TRANSACTION

Starting a transaction is like saying to the database, "I'm about to perform several operations that should be treated as a single, indivisible unit."

```sql
BEGIN TRANSACTION;
```

After this command, all subsequent operations are part of the transaction until it's either committed or rolled back.

### COMMIT

The `COMMIT` command saves all changes made during the transaction to the database permanently.

**Example Scenario:**

Suppose we have an `employees` table and want to increase the salary of all employees in department 1 by 10%.

**Employees Table Before:**

| employee_id | department_id | salary |
|-------------|---------------|--------|
| 1           | 1             | 1000   |
| 2           | 1             | 1200   |
| 3           | 2             | 1500   |

**SQL Commands:**

```sql
BEGIN TRANSACTION;

UPDATE employees
SET salary = salary * 1.10
WHERE department_id = 1;

COMMIT;
```

**Employees Table After:**

| employee_id | department_id | salary |
|-------------|---------------|--------|
| 1           | 1             | 1100   |
| 2           | 1             | 1320   |
| 3           | 2             | 1500   |

**Interpretation:**

- The transaction starts.
- Salaries for department 1 employees are updated.
- `COMMIT` saves these changes permanently.

### ROLLBACK

If something goes wrong during a transaction, you can undo all changes made within it using `ROLLBACK`.

**Example Scenario:**

We attempt the same salary update but realize there's a mistake before committing.

```sql
BEGIN TRANSACTION;

UPDATE employees
SET salary = salary * 1.10
WHERE department_id = 1;

-- Oops! Realized we should only increase by 5%
ROLLBACK;
```

**Employees Table After Rollback:**

| employee_id | department_id | salary |
|-------------|---------------|--------|
| 1           | 1             | 1000   |
| 2           | 1             | 1200   |
| 3           | 2             | 1500   |

**Interpretation:**

- The transaction starts.
- Salaries are updated incorrectly.
- `ROLLBACK` undoes the changes, restoring the original salaries.

### SAVEPOINT

A savepoint allows you to set a point within a transaction to which you can later roll back, without affecting the entire transaction.

**Example Scenario:**

We decide to update salaries in two departments but want the option to undo the second update without losing the first.

```sql
BEGIN TRANSACTION;

UPDATE employees
SET salary = salary * 1.10
WHERE department_id = 1;

SAVEPOINT dept1_updated;

UPDATE employees
SET salary = salary * 1.05
WHERE department_id = 2;
```

**Employees Table After Updates:**

| employee_id | department_id | salary |
|-------------|---------------|--------|
| 1           | 1             | 1100   |
| 2           | 1             | 1320   |
| 3           | 2             | 1575   |

**Interpretation:**

- Salaries in department 1 are increased by 10%.
- A savepoint named `dept1_updated` is created.
- Salaries in department 2 are increased by 5%.

### ROLLBACK TO SAVEPOINT

If we decide to undo the changes made after a savepoint, we can roll back to it.

```sql
ROLLBACK TO dept1_updated;

COMMIT;
```

**Employees Table After Rollback to Savepoint and Commit:**

| employee_id | department_id | salary |
|-------------|---------------|--------|
| 1           | 1             | 1100   |
| 2           | 1             | 1320   |
| 3           | 2             | 1500   |

**Interpretation:**

- Changes made after `dept1_updated` are undone.
- The salary increase for department 2 is rolled back.
- `COMMIT` saves the salary increase for department 1.

### Full Transaction Flow

Here's the entire process in one go:

```sql
BEGIN TRANSACTION;

UPDATE employees
SET salary = salary * 1.10
WHERE department_id = 1;

SAVEPOINT dept1_updated;

UPDATE employees
SET salary = salary * 1.05
WHERE department_id = 2;

-- Decide to undo the last update
ROLLBACK TO dept1_updated;

COMMIT;
```

## Transactions in Real Life

Transactions are essential in scenarios where multiple operations need to be treated atomically.

### Banking Example

Imagine transferring $500 from Account A to Account B.

```sql
BEGIN TRANSACTION;

UPDATE accounts
SET balance = balance - 500
WHERE account_id = 'A';

UPDATE accounts
SET balance = balance + 500
WHERE account_id = 'B';

COMMIT;
```

If any part of this transaction fails (e.g., insufficient funds in Account A), a `ROLLBACK` ensures neither account balance is changed, maintaining financial integrity.

## Rollback Capabilities Across Databases

Different databases handle transactions in slightly different ways. Here's a comparison:

| Feature                  | PostgreSQL | MySQL         | Oracle        | SQL Server    |
|--------------------------|------------|---------------|---------------|---------------|
| Transactions             | Yes        | Yes           | Yes           | Yes           |
| Rollback Support         | Yes        | Yes           | Yes           | Yes           |
| Savepoints               | Yes        | Yes           | Yes           | Yes           |
| DML Rollback             | Yes        | Yes           | Yes           | Yes           |
| DDL Rollback             | Limited    | Limited       | No            | Limited       |
| Autocommit Default       | Off        | On            | Off           | On            |
| Isolation Levels         | Multiple   | Multiple      | Multiple      | Multiple      |

**Key Points:**

- **DML Statements** (`INSERT`, `UPDATE`, `DELETE`) can be rolled back in all databases.
- **DDL Statements** (`CREATE`, `ALTER`, `DROP`) rollback support varies; some databases don't allow rolling back DDL operations.
- **Autocommit Behavior**: In MySQL and SQL Server, changes are committed automatically unless a transaction is explicitly started.

## Best Practices for Using Transactions

- **Group Related Operations**: Use transactions to ensure that all related changes are committed together.
- **Keep Transactions Short**: Long transactions can lock resources and affect performance.
- **Handle Exceptions**: Always include error handling to `ROLLBACK` in case of failures.
- **Use Savepoints Wisely**: They are helpful for complex transactions but can add overhead.
- **Understand Isolation Levels**: Choose the appropriate isolation level to balance performance and data integrity.
