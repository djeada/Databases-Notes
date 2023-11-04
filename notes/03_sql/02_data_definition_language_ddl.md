## Data Definition Language (DDL)

Data Definition Language (DDL) is a subset of SQL that deals with defining, modifying, and managing database structures like tables, views, and indexes.

### Common DDL Statements

- `CREATE`: used to create a new database, table, index, or other schema objects
- `ALTER`: used to modify the structure of existing schema objects (e.g., adding, renaming, or dropping columns in a table)
- `DROP`: used to delete schema objects from the database
- `TRUNCATE`: used to delete all data from a table, but keep the table structure
- `RENAME`: used to rename schema objects (e.g., tables or columns)

### CREATE TABLE

The `CREATE TABLE` statement is used to define a new table in the database. It includes the table name, columns, and their data types, as well as constraints.

Example:

```sql
CREATE TABLE employees (
    employee_id INT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    date_of_birth DATE,
    department_id INT
);
```

After executing this query, the following table will appear in our database:

**employees**
| employee_id | first_name | last_name | date_of_birth | department_id |
|-------------|------------|-----------|---------------|---------------|
|             |            |           |               |               |

### ALTER TABLE

The `ALTER TABLE` statement is used to modify the structure of an existing table.

Example:

```sql
ALTER TABLE employees
ADD email VARCHAR(100);
```

Before:

**employees**
| employee_id | first_name | last_name | date_of_birth | department_id |
|-------------|------------|-----------|---------------|---------------|
|             |            |           |               |               |

After:

**employees**
| employee_id | first_name | last_name | date_of_birth | department_id | email       |
|-------------|------------|-----------|---------------|---------------|-------------|
|             |            |           |               |               |             |

### DROP TABLE

The `DROP TABLE` statement is used to remove an existing table from the database.

Example:

```sql
DROP TABLE employees;
```

Before:

**employees**
| employee_id | first_name | last_name | date_of_birth | department_id |
|-------------|------------|-----------|---------------|---------------|
| x           |  x         | x         | x             | x             |

After:

    No table exists.

### TRUNCATE TABLE

The `TRUNCATE TABLE` statement is used to delete all data from a table, but the table structure remains intact for future use.

Example:

```sql
TRUNCATE TABLE employees;
```

Before:

**employees**
| employee_id | first_name | last_name | date_of_birth | department_id |
|-------------|------------|-----------|---------------|---------------|
| x           |  x         | x         | x             | x             |

After:

**employees**
| employee_id | first_name | last_name | date_of_birth | department_id |
|-------------|------------|-----------|---------------|---------------|
|             |            |           |               |               |

### RENAME TABLE

The `RENAME TABLE` statement is used to rename an existing table. The syntax may vary depending on the SQL implementation.

Example (PostgreSQL):

```sql
ALTER TABLE employees RENAME TO staff;
```

Example (MySQL):

```sql
RENAME TABLE employees TO staff;
```

Before:

**employees**
| employee_id | first_name | last_name | date_of_birth | department_id |
|-------------|------------|-----------|---------------|---------------|
| x           |  x         | x         | x             | x             |

After:

**staff**
| employee_id | first_name | last_name | date_of_birth | department_id |
|-------------|------------|-----------|---------------|---------------|
| x           |  x         | x         | x             | x             |
