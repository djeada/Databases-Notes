# SQL Injection

SQL injection occurs when untrusted input changes the **structure** of a SQL statement.

The primary defense is simple:

> Keep SQL structure under application control and send untrusted data as bound parameters.

Input validation, least privilege, safe error handling, and monitoring provide additional layers.

## Data versus code

A safe query has two channels:

```text
SQL structure:
SELECT user_id
FROM users
WHERE username = ?

parameter data:
"alice"
```

The driver sends the input as a value.

The database does not reinterpret the value as new SQL syntax.

## Vulnerable string construction

Unsafe PHP:

```php
$query =
    "SELECT user_id FROM users " .
    "WHERE username = '$username'";
```

The application combines code and untrusted text before the database parses it.

That makes it possible for the input to alter the predicate.

## Harmless local demonstration

The repository includes:

[`scripts/security/sql_injection_demo.py`](../../scripts/security/sql_injection_demo.py)

Run:

```bash
python scripts/security/sql_injection_demo.py
```

The script uses an **in-memory SQLite database only**.

It compares:

- unsafe string concatenation,
- safe parameter binding,
- safe allowlisting for a dynamic sort column.

The demonstration cannot reach any external database.

## How the vulnerable predicate changes

The demo supplies a harmless tautology-style string.

The unsafe code produces a predicate whose structure changes.

Conceptually:

```text
expected:
username = <one value>

unsafe result:
username = <value>
OR another condition
```

The safe parameterized query treats the entire input as one username value.

## Parameter binding

Python SQLite:

```python
cursor.execute(
    "SELECT user_id FROM users WHERE username = ?",
    (username,),
)
```

PostgreSQL with psycopg-style placeholders:

```python
cursor.execute(
    "SELECT user_id FROM users WHERE username = %s",
    (username,),
)
```

Placeholder syntax depends on the driver.

Do not manually add quotes around the placeholder.

## PHP PDO

```php
$stmt = $pdo->prepare(
    'SELECT user_id
     FROM users
     WHERE username = :username'
);

$stmt->execute([
    'username' => $username
]);
```

The SQL template remains fixed.

## Java JDBC

```java
PreparedStatement stmt = connection.prepareStatement(
    "SELECT user_id FROM users WHERE username = ?"
);

stmt.setString(1, username);
```

Use driver prepared/bound values rather than string concatenation.

## .NET

Parameterized command:

```csharp
using var command = new SqlCommand(
    "SELECT user_id FROM users WHERE username = @username",
    connection
);

command.Parameters.AddWithValue("@username", username);
```

For performance/type precision, explicit parameter types can be preferable to generic type inference.

The security property is that values are bound separately.

## Values are parameterizable

Typical value positions include:

```sql
WHERE customer_id = ?
```

```sql
WHERE created_at >= ?
```

```sql
INSERT INTO users(name) VALUES (?)
```

```sql
UPDATE orders SET status = ? WHERE order_id = ?
```

Use parameters for every untrusted value.

## Identifiers usually are not values

A table name or column name is SQL structure.

This generally does not work:

```sql
SELECT * FROM ?;
```

Use an application allowlist.

Python:

```python
allowed_sort_columns = {
    "name": "name",
    "created": "created_at",
}

sort_column = allowed_sort_columns[requested_sort]

query = (
    "SELECT user_id, name "
    "FROM users "
    f"ORDER BY {sort_column}"
)
```

The interpolated text comes only from trusted constants.

## Sort direction

Do not concatenate arbitrary:

```text
ASC/DESC
```

from the request.

Map:

```python
directions = {
    "ascending": "ASC",
    "descending": "DESC",
}
```

Then use the mapped constant.

## Dynamic table selection

If an application genuinely supports several tables:

```python
tables = {
    "customers": "reporting.customers",
    "orders": "reporting.orders",
}
```

Reject every unknown key.

Do not use regex validation alone when a small fixed allowlist exists.

## IN lists

Do not build:

```text
WHERE id IN (<concatenated input>)
```

Use:

- driver array support,
- generated placeholders,
- temporary table,
- table-valued parameter,
- ORM list binding.

Example with three values:

```sql
WHERE id IN (?, ?, ?)
```

and bind all three values separately.

## LIKE patterns

Parameters also work with `LIKE`.

Example:

```python
cursor.execute(
    "SELECT id, title FROM products WHERE title LIKE ?",
    (f"%{search_text}%",),
)
```

The wildcard behavior is now a search-semantics issue, not SQL syntax injection.

If literal `%` or `_` must be searched, use the database's escaping rules for `LIKE`.

## LIMIT and OFFSET

Do not concatenate unvalidated pagination values.

Many drivers/databases allow binding numeric limit/offset values.

If the database syntax does not, parse them as integers and enforce strict range limits before composing SQL.

Example policy:

```text
1 <= page_size <= 100
0 <= offset <= 100000
```

## Authentication query

A safe login flow retrieves the password hash by username:

```sql
SELECT user_id, password_hash
FROM users
WHERE username = ?
```

Then verify the password with the language/framework password-hashing API.

Do not compare plaintext passwords in SQL.

## Password handling

Registration:

```text
password
   │
password hash function
   ▼
stored verifier
```

Login:

```text
submitted password
       │
verify against stored hash
       ▼
success / failure
```

SQL injection defense and password hashing solve different problems.

## Escaping is not the primary defense

Manual quote escaping is fragile because behavior can depend on:

- character encoding,
- SQL mode,
- driver configuration,
- database syntax.

Use parameters.

Escaping may still matter for other contexts such as `LIKE` semantics, but it should not be the primary SQL injection control.

## HTML escaping is unrelated

```htmlspecialchars()``, HTML encoding, and output escaping defend browser-rendering contexts.

They do not make SQL concatenation safe.

Different interpreter:

```text
HTML parser != SQL parser
```

Use context-specific controls.

## ORMs

An ORM can generate safe parameterized queries.

Example:

```python
session.execute(
    select(User).where(User.name == supplied_name)
)
```

But raw SQL escape hatches can reintroduce injection:

```text
ORM
 └── raw SQL string concatenation
       -> vulnerable again
```

Review raw query APIs carefully.

## Query builders

Query builders are safe when values remain parameters.

Unsafe usage can still occur if the API exposes:

- raw fragments,
- literal SQL,
- unescaped identifier interpolation.

The library name is not a security guarantee.

## Stored procedures

Stored procedures can be safe:

```text
fixed SQL + parameters
```

or unsafe:

```text
procedure receives text
   │
concatenates dynamic SQL
   │
EXECUTE
```

Review dynamic SQL inside procedures the same way as application code.

## Dynamic SQL in PostgreSQL

PL/pgSQL provides safe formatting tools for identifiers and values.

Use:

- `format('%I', identifier)` for identifiers,
- `EXECUTE ... USING` for data values.

Prefer fixed SQL when possible.

## First-order injection

Input immediately changes the query that receives it.

This is the classic case.

## Second-order injection

An unsafe value may be stored first and only later concatenated into dynamic SQL.

```text
untrusted value stored
        │
        ▼
later admin/report job
        │
concatenates stored text into SQL
        │
        ▼
injection
```

"Data came from our database" does not make it trusted SQL structure.

## Injection surfaces beyond login forms

Review:

- search,
- filters,
- reporting,
- export,
- admin panels,
- bulk imports,
- API sort/order fields,
- migration tools,
- background jobs.

The highest-risk injection point may be an internal tool.

## Error behavior

Detailed database errors should not be shown directly to untrusted users.

Public response:

```text
request could not be processed
```

Protected logs:

```text
database error code
request ID
query identifier
stack trace
```

Do not log bound secret values unnecessarily.

## Blind behavior

An application does not need to display database rows for injection to matter.

Different:

- success/failure,
- response timing,
- status code,

can still reveal whether injected logic changed behavior.

The defensive lesson remains the same: no untrusted text should become SQL syntax.

## Multi-statement execution

Some drivers/interfaces allow multiple SQL statements in one call; others disable it.

Do not rely on "our driver blocks semicolons" as the defense.

A single manipulated predicate can already violate authorization.

## Database permissions as containment

Assume an injection bug might happen.

The application database account should not be able to:

- create superusers,
- drop unrelated schemas,
- read every sensitive table,
- modify audit logs.

Least privilege reduces blast radius.

See the identity/access-control note.

## Read-only services

A search/reporting endpoint may need only:

```text
SELECT
```

Give it a read-only role.

Then an injection flaw cannot directly modify tables through that credential.

Confidentiality risk can still remain, so parameters are still required.

## Separate migration credentials

Do not run the public web application using the same role that migrations use.

```text
migration role -> DDL
runtime role   -> narrow DML
```

A runtime injection should not automatically gain schema-changing privileges.

## Input validation

Validation is useful for business constraints.

Examples:

- customer ID must be integer,
- sort option must be one of four names,
- date must parse,
- page size must be within range.

Validation improves correctness.

But it should not replace parameterization for values.

## WAFs

A Web Application Firewall can detect some suspicious patterns.

It is defense in depth.

It cannot reliably understand every application query path, encoding, or database dialect.

Do not use a WAF as the primary SQL injection defense.

## Static analysis

Code scanners can detect patterns such as:

```text
"SELECT ..." + user_input
```

Useful, but incomplete.

Dynamic query builders and indirect flows may be missed.

Combine:

- code review,
- static analysis,
- tests.

## Security tests

Add regression tests for risky query-building functions.

Example:

```text
input contains quotes and SQL-looking characters
expected:
treated as one literal value
```

The goal is not to maintain a giant attack payload list.

The goal is to verify the query structure cannot be changed by input.

## Review checklist

For every data-access path:

1. Is SQL structure fixed?
2. Are all values bound?
3. Are dynamic identifiers selected from allowlists?
4. Are sort direction and operators allowlisted?
5. Are list values safely expanded/bound?
6. Does any stored value later become dynamic SQL?
7. Are ORM raw-query APIs reviewed?
8. Are stored procedures free from unsafe concatenation?
9. Does the runtime DB role use least privilege?
10. Are detailed DB errors protected?
11. Are secrets excluded from SQL logs?

## Common mistakes

### "We sanitize quotes"

Parameterize instead.

### "The ORM prevents SQL injection"

Raw SQL paths still exist.

### "This value came from our database"

Stored data can still be attacker-controlled.

### "Only SELECT is exposed"

Injected predicates can still reveal unauthorized rows.

### "The account is read-only, so it is safe"

Read-only injection can disclose sensitive data.

### "The WAF blocks SQL keywords"

Attack syntax and encodings vary; fix the code.

## Related notes

- [Database security overview](02_database_security.md)
- [Identity and access control](08_identity_authentication_and_access_control.md)
- [Database hardening](11_database_hardening_and_patch_management.md)
- [Database access in code](../08_database_performance/05_accessing_database_in_code.md)
- [ORM introduction](../14_orm/01_introduction_to_orm.md)
