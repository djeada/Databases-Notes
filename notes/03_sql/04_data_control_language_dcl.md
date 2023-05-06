
## Data Control Language (DCL)

Data Control Language (DCL) is a subset of SQL that deals with permissions and security for database objects, such as tables and views. DCL statements include `GRANT` and `REVOKE`.

### Common DCL Statements

- `GRANT`: used to provide privileges to users or roles
- `REVOKE`: used to remove privileges from users or roles

### GRANT

The `GRANT` statement is used to give specific privileges to users or roles for accessing and manipulating database objects, such as tables, views, and stored procedures.

Example:

```sql
GRANT SELECT, INSERT, UPDATE
ON employees
TO user1;
```

In this example, the `GRANT` statement gives the user user1 the `SELECT`, `INSERT`, and `UPDATE` privileges on the employees table.

### REVOKE

The `REVOKE` statement is used to remove specific privileges from users or roles for accessing and manipulating database objects.

Example:

```sql
REVOKE INSERT, UPDATE
ON employees
FROM user1;
```

In this example, the `REVOKE` statement removes the `INSERT` and `UPDATE` privileges from the user user1 for the employees table.

### Roles

Roles are used to group permissions, making it easier to manage and maintain security across multiple users. You can create roles, grant privileges to roles, and then grant those roles to users.

Example:

```sql
CREATE ROLE data_entry;
GRANT INSERT, UPDATE
ON employees
TO data_entry;
GRANT data_entry
TO user1;
```

In this example, a role named data_entry is created. The INSERT and UPDATE privileges are granted to the data_entry role for the employees table. Then, the data_entry role is granted to user1.
