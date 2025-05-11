## SQL Injection Attacks

SQL Injection Attacks are a security concern in web applications. We'll explore how these attacks occur, examine concrete examples, and discuss effective prevention strategies. By the end of this journey, you'll have a solid understanding of SQL Injection and how to protect your applications from such vulnerabilities.

After reading the material, you should be able to answer the following questions:

- What is SQL Injection, and why is it a significant security threat in web applications?
- How do SQL Injection attacks occur, and what makes an application vulnerable to them?
- Can you describe common examples of SQL Injection attacks and their potential impacts?
- What are the most effective strategies for preventing SQL Injection attacks in applications?
- How do parameterized queries and input validation contribute to securing applications against SQL Injection?

### What is SQL Injection?

SQL Injection is a technique where attackers exploit vulnerabilities in an application's interaction with its database. By inserting malicious SQL code into input fields, they can manipulate queries to access unauthorized data, modify or delete records, and even take control of the entire database. Think of it as someone sneaking harmful instructions into a conversation between your application and its database.

### How Does SQL Injection Happen?

At the core, SQL Injection occurs when user input is incorporated directly into SQL queries without proper validation or sanitization. This unfiltered input can alter the structure of the SQL commands, leading to unintended and potentially dangerous outcomes.

I. **User Input Submission**

Users provide input through forms, URL parameters, or other data entry points.

II. **Query Construction**

The application builds SQL queries by combining static code with user input.

III. **Query Execution**

The database executes the constructed query, which may have been tampered with if the input was malicious.

```
[ User Input ] --> [ Application ] --> [ Query Construction ] --> [ Database Execution ]
```

### Vulnerable Code Example

Imagine a login form where users enter their username and password. A vulnerable application might handle this input as follows:

```php
<?php
// User-provided input
$username = $_POST['username'];
$password = $_POST['password'];

// Vulnerable SQL query construction
$query = "SELECT * FROM users WHERE username = '$username' AND password = '$password'";

// Execute the query
$result = mysqli_query($connection, $query);

// Check if user exists
if (mysqli_num_rows($result) > 0) {
    echo "Welcome, $username!";
} else {
    echo "Invalid username or password.";
}
?>
```

In this example, user inputs `$username` and `$password` are directly embedded into the SQL query without any checks. This opens the door for SQL Injection.

### Examples of SQL Injection Attacks

Let's explore how attackers can exploit such vulnerabilities with real-world scenarios.

#### Authentication Bypass

An attacker aims to gain unauthorized access by bypassing the login authentication.

The attacker inputs the following:

- **Username:** `admin' --`
- **Password:** `irrelevant`

```sql
SELECT * FROM users WHERE username = 'admin' --' AND password = 'irrelevant'
```

- The `--` sequence comments out the rest of the SQL query.
- The query effectively becomes:

```sql
SELECT * FROM users WHERE username = 'admin'
```

- The password check is bypassed, granting access to the 'admin' account.
- The attacker successfully logs in as 'admin' without knowing the password.
- They gain full administrative privileges within the application.

```
[ Malicious Input ]
        |
        v
[ Altered Query ]
        |
        v
[ Unauthorized Access ]
```

#### Data Extraction

An attacker tries to retrieve sensitive information from the database.

The attacker inputs:

- **Username:** `john' UNION SELECT username, password FROM users --`
- **Password:** `irrelevant`

```sql
SELECT * FROM users WHERE username = 'john' UNION SELECT username, password FROM users --' AND password = 'irrelevant'
```

- The `UNION` operator combines the results of two queries.
- The attacker forces the database to return all usernames and passwords.
- The application may display or process the combined data.
- The attacker gains access to credentials of all users.

#### Data Manipulation

An attacker wants to modify data, such as elevating their privileges.

The attacker inputs:

- **Username:** `'; UPDATE users SET role='admin' WHERE username='attacker'; --`
- **Password:** `irrelevant`

```sql
SELECT * FROM users WHERE username = ''; UPDATE users SET role='admin' WHERE username='attacker'; --' AND password = 'irrelevant'
```

- The first query selects a user with an empty username.
- The second query updates the attacker's role to 'admin'.
- The `--` comments out the rest of the original query.
- The attacker's account now has administrative privileges.
- They can perform actions reserved for admins, compromising security.

#### Denial of Service

An attacker aims to disrupt the database's functionality.

The attacker inputs:

- **Username:** `'; DROP TABLE users; --`
- **Password:** `irrelevant`

```sql
SELECT * FROM users WHERE username = ''; DROP TABLE users; --' AND password = 'irrelevant'
```

- The `DROP TABLE users` command deletes the entire users table.
- The application loses all user data, causing it to fail.
- The database is severely compromised.
- Recovery may require restoring from backups, resulting in downtime.

### Preventing SQL Injection Attacks

Understanding prevention is crucial to safeguard applications from SQL Injection.

#### Use Parameterized Queries (Prepared Statements)

Parameterized queries ensure that user input is treated strictly as data, not executable code.

**Secure Code Example in PHP using PDO:**

```php
<?php
// User-provided input
$username = $_POST['username'];
$password = $_POST['password'];

// Prepare the SQL statement
$stmt = $pdo->prepare('SELECT * FROM users WHERE username = :username AND password = :password');

// Bind parameters
$stmt->bindParam(':username', $username);
$stmt->bindParam(':password', $password);

// Execute the statement
$stmt->execute();

// Check if user exists
if ($stmt->rowCount() > 0) {
    echo "Welcome, $username!";
} else {
    echo "Invalid username or password.";
}
?>
```

- The query structure is fixed, and parameters are bound separately.
- Even if an attacker supplies malicious input, it won't alter the query's logic.

```
[ User Input ] --> [ Application ] --> [ Parameterized Query ] --> [ Safe Execution ]
```

#### Validate and Sanitize User Input

Always check that inputs meet expected criteria before using them.

```php
<?php
// Validate username (e.g., only letters and numbers)
if (!preg_match('/^[a-zA-Z0-9]+$/', $_POST['username'])) {
    die('Invalid username.');
}

// Sanitize inputs
$username = htmlspecialchars($_POST['username']);
$password = htmlspecialchars($_POST['password']);
?>
```

- Prevents injection of special characters.
- Ensures input conforms to expected patterns.

#### Use Stored Procedures

Stored procedures are precompiled SQL statements stored in the database, which can be executed with parameters.

```sql
DELIMITER //
CREATE PROCEDURE AuthenticateUser(IN p_username VARCHAR(50), IN p_password VARCHAR(50))
BEGIN
    SELECT * FROM users WHERE username = p_username AND password = p_password;
END //
DELIMITER ;
```

Calling the Stored Procedure in PHP:

```php
<?php
// User-provided input
$username = $_POST['username'];
$password = $_POST['password'];

// Prepare and execute the stored procedure
$stmt = $pdo->prepare('CALL AuthenticateUser(:username, :password)');
$stmt->bindParam(':username', $username);
$stmt->bindParam(':password', $password);
$stmt->execute();

// Check if user exists
if ($stmt->rowCount() > 0) {
    echo "Welcome, $username!";
} else {
    echo "Invalid username or password.";
}
?>
```

- The SQL code is predefined and not altered by user input.
- Parameters are handled securely by the database.

#### Implement Least Privilege Principle

Limit the database permissions of the application's user account.

- Grant only necessary privileges (e.g., `SELECT`, `INSERT`).
- Avoid using database admin accounts in the application.

Example of Restricting Privileges in MySQL:

```sql
GRANT SELECT, INSERT, UPDATE ON mydatabase.users TO 'app_user'@'localhost' IDENTIFIED BY 'securepassword';
```

- Even if an attacker gains some level of access, the damage is limited.
- Critical operations like dropping tables are not permitted.

#### Escape User Input

If parameterized queries aren't available, ensure special characters are properly escaped.

```php
<?php
// Escape special characters
$username = mysqli_real_escape_string($connection, $_POST['username']);
$password = mysqli_real_escape_string($connection, $_POST['password']);

// Construct the query
$query = "SELECT * FROM users WHERE username = '$username' AND password = '$password'";
?>
```

- Escaping reduces risk but isn't foolproof.
- Prefer parameterized queries when possible.
