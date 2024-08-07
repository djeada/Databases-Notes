## Transaction Control Language (TCL)

Transaction Control Language (TCL) is a subset of SQL that deals with managing transactions in a database. Transactions are a sequence of one or more SQL statements executed as a single unit of work, ensuring data consistency and integrity.

### Common TCL Statements

- `BEGIN TRANSACTION`: marks the starting point of a transaction
- `COMMIT`: saves the changes made within a transaction
- `ROLLBACK`: undoes the changes made within a transaction
- `SAVEPOINT`: creates a savepoint within the current transaction
- `ROLLBACK TO savepoint`: rolls back the transaction to a specified savepoint

### BEGIN TRANSACTION

The `BEGIN TRANSACTION` statement marks the starting point of a transaction. Any SQL statements executed after this point will be part of the transaction.

Example:

```sql
BEGIN TRANSACTION;
```

### COMMIT

The `COMMIT` statement is used to save all changes made within the transaction permanently to the database.

Example:

```sql
BEGIN TRANSACTION;

UPDATE employees
SET salary = salary * 1.1
WHERE department_id = 1;

COMMIT;
```

In this example, the `COMMIT` statement saves the salary update for employees in department 1.

**employees** before:

| employee_id | department_id | salary  |
|-------------|---------------|---------|
| 1           | 1             | 1000    |
| 2           | 1             | 1200    |
| 3           | 2             | 1500    |

**employees** after:

| employee_id | department_id | salary  |
|-------------|---------------|---------|
| 1           | 1             | 1100    |
| 2           | 1             | 1320    |
| 3           | 2             | 1500    |

### ROLLBACK

The `ROLLBACK` statement is used to undo all changes made within the transaction and revert the database to the state it was in before the transaction started.

Example:

```sql
BEGIN TRANSACTION;

UPDATE employees
SET salary = salary * 1.1
WHERE department_id = 1;

ROLLBACK;
```

In this example, the `ROLLBACK` statement undoes the salary update for employees in department 1.

Before:

**employees**
| employee_id | department_id | salary  |
|-------------|---------------|---------|
| 1           | 1             | 1000    |
| 2           | 1             | 1200    |
| 3           | 2             | 1500    |

After:

**employees**
| employee_id | department_id | salary  |
|-------------|---------------|---------|
| 1           | 1             | 1000    |
| 2           | 1             | 1200    |
| 3           | 2             | 1500    |

### SAVEPOINT

The `SAVEPOINT` statement creates a savepoint within the current transaction, allowing you to partially roll back a transaction to a specific point.

Example:

```sql
BEGIN TRANSACTION;

UPDATE employees
SET salary = salary * 1.1
WHERE department_id = 1;

SAVEPOINT salary_update;

UPDATE employees
SET salary = salary * 1.05
WHERE department_id = 2;
```

In this example, a savepoint named `salary_update` is created after updating the salaries for employees in department 1.

Before:

**employees**
| employee_id | department_id | salary  |
|-------------|---------------|---------|
| 1           | 1             | 1000    |
| 2           | 1             | 1200    |
| 3           | 2             | 1500    |

After:

**employees**
| employee_id | department_id | salary  |
|-------------|---------------|---------|
| 1           | 1             | 1100    |
| 2           | 1             | 1320    |
| 3           | 2             | 1575    |

### ROLLBACK TO savepoint

The `ROLLBACK TO` savepoint statement rolls back the transaction to a specified savepoint, undoing the changes made after the savepoint.

Example:

```sql
BEGIN TRANSACTION;

UPDATE employees
SET salary = salary * 1.1
WHERE department_id = 1;

SAVEPOINT salary_update;

UPDATE employees
SET salary = salary * 1.05
WHERE department_id = 2;

ROLLBACK TO salary_update;
```

In this example, the `ROLLBACK TO salary_update` statement undoes the salary update for employees in department 2 while preserving the salary update for employees in department 1.

Before:

**employees**
| employee_id | department_id | salary  |
|-------------|---------------|---------|
| 1           | 1             | 1000    |
| 2           | 1             | 1200    |
| 3           | 2             | 1500    |

After:

**employees**
| employee_id | department_id | salary  |
|-------------|---------------|---------|
| 1           | 1             | 1100    |
| 2           | 1             | 1320    |
| 3           | 2             | 1500    |


## Rollback Capabilities Across Different SQL Databases 

Here's a table summarizing the rollback capabilities and safety features across different SQL databases like PostgreSQL, SQLite, MySQL, Oracle, and SQL Server:

| Feature                  | PostgreSQL                      | SQLite                            | MySQL                             | Oracle                            | SQL Server                        |
|--------------------------|---------------------------------|-----------------------------------|-----------------------------------|-----------------------------------|-----------------------------------|
| **Transactions**         | Yes                             | Yes                               | Yes                               | Yes                               | Yes                               |
| **Atomicity**            | Yes                             | Yes                               | Yes                               | Yes                               | Yes                               |
| **Rollback Support**     | Yes                             | Yes                               | Yes                               | Yes                               | Yes                               |
| **Nested Transactions**  | Yes (savepoints)                | Yes (savepoints)                  | Yes (savepoints)                  | Yes (savepoints)                  | Yes (savepoints)                  |
| **DML Rollback**         | Yes (INSERT, UPDATE, DELETE)    | Yes (INSERT, UPDATE, DELETE)      | Yes (INSERT, UPDATE, DELETE)      | Yes (INSERT, UPDATE, DELETE)      | Yes (INSERT, UPDATE, DELETE)      |
| **DDL Rollback**         | Limited (via transactional DDL in PostgreSQL 13+) | No                                | Limited (mostly no)               | No                                | Limited (mostly no)               |
| **Safe Operations**      | All DML within transactions     | All DML within transactions       | All DML within transactions       | All DML within transactions       | All DML within transactions       |
| **Unsafe Operations**    | Most DDL, certain system commands | Most DDL, certain system commands | Most DDL, certain system commands | Most DDL, certain system commands | Most DDL, certain system commands |
| **Autocommit**           | No                              | Yes                               | Yes                               | No                                | Yes                               |
| **Isolation Levels**     | Read Committed, Repeatable Read, Serializable | Serializable                     | Read Uncommitted, Read Committed, Repeatable Read, Serializable | Read Committed, Serializable       | Read Uncommitted, Read Committed, Repeatable Read, Serializable |
| **Savepoints**           | Yes                             | Yes                               | Yes                               | Yes                               | Yes                               |
| **Implicit Transactions**| No                              | No                                | Yes                               | No                                | Yes                               |
| **Partial Rollback**     | Yes (via savepoints)            | Yes (via savepoints)              | Yes (via savepoints)              | Yes (via savepoints)              | Yes (via savepoints)              |

