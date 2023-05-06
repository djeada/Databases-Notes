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
