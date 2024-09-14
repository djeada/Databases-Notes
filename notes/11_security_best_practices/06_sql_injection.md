# SQL Injection Attacks

SQL Injection is a critical security vulnerability that allows attackers to interfere with the queries an application makes to its database. By manipulating user input, attackers can inject malicious SQL code, potentially accessing, modifying, or destroying data without proper authorization.

**Key Objectives:**

- Explain how SQL Injection attacks occur.
- Provide examples of vulnerabilities and attack types.
- Offer prevention techniques and best practices.
- Enhance understanding with illustrative diagrams and code examples.

---

## How SQL Injection Occurs

SQL Injection occurs when an application incorporates untrusted user input into SQL queries without proper validation or sanitization. Attackers manipulate input fields to alter the intended SQL command, potentially executing malicious queries.

**Mechanism:**

1. **User Input Submission:**

   - The application accepts input from users (e.g., form fields, URL parameters).

2. **Dynamic SQL Query Construction:**

   - User input is concatenated directly into SQL statements.

3. **Execution of Altered Query:**

   - The database executes the modified SQL query, which may include unintended commands.

**Illustrative Diagram:**

```
[ User Input ]
     |
     v
[ Application ]
     |
     v
[ SQL Query Construction ]
     |
     v
[ SQL Database ]
```

- Without proper handling, user input flows through the application and alters the SQL query sent to the database.

---

## Vulnerability Example: Authentication Form

A common vulnerability arises in authentication forms where user credentials are checked against the database.

**Vulnerable Code Example (Pseudo-code):**

```javascript
// User-provided input
let username = params['username'];
let password = params['password'];

// Vulnerable SQL query construction
let query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "';";

// Execute the query
let user = database.execute(query);

// Authenticate the user
if (user) {
    logInUser(user);
}
```

**Issue:**

- User input is directly concatenated into the SQL query without validation.
- Allows attackers to inject SQL code via the `username` or `password` fields.

**Illustrative Diagram:**

```
[ User Input ]
     |
     | (username and password)
     v
[ Vulnerable Query Construction ]
     |
     | ("SELECT * FROM users WHERE username = 'input' AND password = 'input';")
     v
[ Database Execution ]
```

---

## Attack Types and Examples

### 1. Authentication Bypass

**Objective:**

- Gain unauthorized access by bypassing authentication mechanisms.

**Attack Example:**

- Inputting a crafted username or password to manipulate the SQL query.

**Malicious Input:**

- Username: `' OR '1'='1`
- Password: `' OR '1'='1`

**Resulting Query:**

```sql
SELECT * FROM users WHERE username = '' OR '1'='1' AND password = '' OR '1'='1';
```

**Effect:**

- The condition `'1'='1'` is always true.
- The query returns all users, potentially logging in the attacker without valid credentials.

**Diagram of Attack Flow:**

```
[ User Input ]
     |
     | (malicious username and password)
     v
[ Vulnerable Query Construction ]
     |
     | ("SELECT * FROM users WHERE username = '' OR '1'='1' ...")
     v
[ Database Execution ]
     |
     v
[ Authentication Bypassed ]
```

### 2. Data Exfiltration

**Objective:**

- Retrieve sensitive data from the database.

**Attack Example:**

- Exploiting the query to return additional data.

**Malicious Input:**

- Username: `admin' UNION SELECT credit_card_number FROM credit_cards --`
- Password: `anything`

**Resulting Query:**

```sql
SELECT * FROM users WHERE username = 'admin' UNION SELECT credit_card_number FROM credit_cards --' AND password = 'anything';
```

**Effect:**

- Combines results from the `users` table and the `credit_cards` table.
- Exposes sensitive information.

### 3. Data Manipulation

**Objective:**

- Modify or delete data within the database.

**Attack Example:**

- Inserting commands to alter database records.

**Malicious Input:**

- Username: `'; UPDATE users SET role='admin' WHERE username='attacker';--`
- Password: `anything`

**Resulting Query:**

```sql
SELECT * FROM users WHERE username = ''; UPDATE users SET role='admin' WHERE username='attacker';--' AND password = 'anything';
```

**Effect:**

- Executes an `UPDATE` command, elevating the attacker's privileges.

### 4. Denial of Service

**Objective:**

- Disrupt database operations, causing downtime or resource exhaustion.

**Attack Example:**

- Injecting code to create long-running queries.

**Malicious Input:**

- Username: `admin'; WAITFOR DELAY '0:0:10';--`
- Password: `anything`

**Resulting Query:**

```sql
SELECT * FROM users WHERE username = 'admin'; WAITFOR DELAY '0:0:10';--' AND password = 'anything';
```

**Effect:**

- Introduces a delay, potentially overloading the database with concurrent requests.

---

## Preventing SQL Injection Attacks

Implementing robust defense strategies is crucial to prevent SQL Injection vulnerabilities.

### Input Validation

- **Definition:**

  - Check user input for expected format, length, type, and allowable characters.

- **Techniques:**

  - **Whitelist Validation:** Accept only known good input.
  - **Blacklist Validation:** Reject known malicious patterns (less effective).

- **Example:**

  ```javascript
  if (!/^[a-zA-Z0-9_]{3,20}$/.test(username)) {
      throw new Error('Invalid username');
  }
  ```

### Parameterized Queries (Prepared Statements)

- **Definition:**

  - Use placeholders for user input in SQL statements, allowing the database to distinguish between code and data.

- **Benefits:**

  - Prevents attackers from altering the intent of the query.
  - Simplifies code maintenance.

- **Example in Java using JDBC:**

  ```java
  String query = "SELECT * FROM users WHERE username = ? AND password = ?";
  PreparedStatement stmt = connection.prepareStatement(query);
  stmt.setString(1, username);
  stmt.setString(2, password);
  ResultSet rs = stmt.executeQuery();
  ```

**Illustrative Diagram:**

```
[ User Input ]
     |
     v
[ Parameterized Query ]
     |
     | (SQL code and parameters sent separately)
     v
[ Database Execution ]
```

### Stored Procedures

- **Definition:**

  - Predefined SQL statements stored in the database, executed with provided parameters.

- **Benefits:**

  - Centralizes query logic within the database.
  - Limits direct interaction with SQL statements.

- **Example in SQL Server:**

  ```sql
  -- Create stored procedure
  CREATE PROCEDURE AuthenticateUser
      @Username NVARCHAR(50),
      @Password NVARCHAR(50)
  AS
  BEGIN
      SELECT * FROM users WHERE username = @Username AND password = @Password;
  END
  ```

  ```csharp
  // Call stored procedure from application
  SqlCommand cmd = new SqlCommand("AuthenticateUser", connection);
  cmd.CommandType = CommandType.StoredProcedure;
  cmd.Parameters.AddWithValue("@Username", username);
  cmd.Parameters.AddWithValue("@Password", password);
  SqlDataReader reader = cmd.ExecuteReader();
  ```

### Escaping User Input

- **Definition:**

  - Sanitize user input by escaping special characters that could alter SQL syntax.

- **Considerations:**

  - Must be implemented carefully for each database type.
  - Not a standalone solution; should be combined with other methods.

- **Example:**

  ```python
  import MySQLdb

  username = MySQLdb.escape_string(user_input)
  ```

### Least Privilege Principle

- **Definition:**

  - Grant the minimum necessary permissions to database accounts used by applications.

- **Benefits:**

  - Limits the impact of a compromised application.
  - Prevents unauthorized access to sensitive data or operations.

- **Implementation:**

  - Use separate accounts for different application functions.
  - Restrict accounts to specific tables and queries.

