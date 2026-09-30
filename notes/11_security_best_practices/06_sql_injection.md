# SQL Injection

SQL injection occurs when untrusted input becomes part of a query's SQL syntax. The primary defense is to bind values as parameters while keeping the query structure under application control. Input validation and limited database permissions provide additional protection.

## How a vulnerable query changes

This PHP example is deliberately unsafe:

```php
$query = "SELECT user_id FROM users WHERE username = '$username'";
```

If the username is `x' OR '1'='1`, the resulting predicate is:

```sql
WHERE username = 'x' OR '1'='1'
```

The added condition changes what the query means. The exact attack effects depend on SQL syntax, the driver, and account permissions. Running multiple injected statements is possible only when the execution interface permits it.

## Bind values separately

A prepared query keeps the predicate fixed:

```php
$stmt = $pdo->prepare('SELECT user_id FROM users WHERE username = :username');
$stmt->execute(['username' => $username]);
$user = $stmt->fetch(PDO::FETCH_ASSOC);
```

The username is now one value, even if it contains quotes or SQL-looking text. Do not use `PDOStatement::rowCount()` to determine whether a portable `SELECT` returned a row; fetch the result instead. See the [PDO rowCount documentation](https://www.php.net/manual/en/pdostatement.rowcount.php).

## A safer authentication example

Assume `$pdo` is an established connection, usernames are unique, and registration stored a hash created with `password_hash()` in `password_hash`. This snippet checks credentials; a complete login flow also needs secure session handling and rate limiting.

```php
<?php
$username = $_POST['username'] ?? null;
$password = $_POST['password'] ?? null;
if (!is_string($username) || !is_string($password)) {
    http_response_code(400);
    exit('Invalid input.');
}

$stmt = $pdo->prepare(
    'SELECT user_id, password_hash FROM users WHERE username = :username'
);
$stmt->execute(['username' => $username]);
$user = $stmt->fetch(PDO::FETCH_ASSOC);

if ($user !== false && password_verify($password, $user['password_hash'])) {
    echo 'Credentials verified.';
} else {
    echo 'Invalid username or password.';
}
?>
```

Store a password hash, not a plaintext password, and verify it with [PHP password_verify](https://www.php.net/manual/en/function.password-verify.php). Do not alter passwords with HTML encoding before verification. HTML escaping protects output rendered into HTML; it does not protect an SQL query.

## Parameters represent values, not identifiers

A placeholder cannot generally replace a table name, column name, sort direction, or arbitrary SQL expression. Map requested identifiers to a fixed allowlist:

```python
# Python DB-API sketch; %s is the placeholder used by this chosen driver.
allowed_sort_columns = {"name": "name", "created": "created_at"}
sort_column = allowed_sort_columns[requested_sort]  # Reject unknown choices.
cursor.execute(
    f"SELECT user_id, name FROM users WHERE status = %s ORDER BY {sort_column}",
    (requested_status,),
)
```

The interpolated identifier comes only from application constants; the status remains a bound value. Placeholder syntax differs by driver: Python's SQLite driver uses `?` or named placeholders.

## Stored procedures and ORMs

A stored procedure using bound parameters and fixed SQL can protect its values. A procedure that concatenates those parameters into dynamic SQL can still be vulnerable. ORMs also allow unsafe raw SQL, so the presence of an ORM is not proof of safe query construction.

## Defense in depth

Validate types, lengths, and permitted business values. Give the application only the database privileges it needs. Keep database errors out of public responses, while recording sufficient diagnostic information in protected logs. Check every path that builds queries, including reporting, sorting, search filters, and administrative features.

The crucial review question is: **can any untrusted value change the structure of the executed SQL?**

## Related notes

- [Database security](02_database_security.md)
- [Database access in code](../08_database_performance/05_accessing_database_in_code.md)
- [ORM introduction](../14_orm/01_introduction_to_orm.md)
