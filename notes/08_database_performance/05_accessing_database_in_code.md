## Accessing Databases in Code

Accessing databases through code is a fundamental skill for developers building applications that rely on data storage and retrieval. Whether you're developing a web application, mobile app, or any software that requires data persistence, understanding how to interact with databases programmatically is essential.

### Database Connection

Establishing a connection to the database is the first step in interacting with it programmatically.

#### Connection Libraries

Each programming language and database system requires specific libraries or drivers to facilitate communication.

**Examples**:

| Programming Language | Database              | Library/Driver                     |
|-----------------------|-----------------------|-------------------------------------|
| Python                | MySQL                | `mysql-connector-python`, `PyMySQL`|
|                       | PostgreSQL           | `psycopg2`, `asyncpg`              |
|                       | SQLite               | Built-in `sqlite3` module          |
| Java                  | JDBC Drivers         | `mysql-connector-java`, `postgresql-jdbc` |
| C#/.NET               | SQL Server           | `System.Data.SqlClient`            |
|                       | MySQL                | `MySql.Data`                       |
| JavaScript (Node.js)  | MySQL                | `mysql`, `mysql2`                  |
|                       | PostgreSQL           | `pg`                               |

**Installing a Python Library for PostgreSQL**:

```bash
pip install psycopg2-binary
```

#### Connection Strings

A connection string contains the information required to establish a connection to the database.

**Components**:

| Component             | Description                                     |
|------------------------|-------------------------------------------------|
| Hostname              | The server's address.                           |
| Port                  | The port number (default: MySQL is 3306, PostgreSQL is 5432). |
| Database Name         | The specific database to connect to.            |
| Username and Password | Credentials for authentication.                 |
| Additional Parameters | SSL mode, timeouts, charset, and other options. |

**Example in Python using psycopg2**:

```python
import psycopg2

conn = psycopg2.connect(
    dbname="my_database",
    user="my_user",
    password="my_password",
    host="localhost",
    port="5432"
)
```

**Example in Java using JDBC**:

```java
String url = "jdbc:postgresql://localhost:5432/my_database";
Properties props = new Properties();
props.setProperty("user", "my_user");
props.setProperty("password", "my_password");
Connection conn = DriverManager.getConnection(url, props);
```

#### Connection Pooling

Connection pooling manages a pool of database connections, reusing them instead of creating new ones for each request.

**Benefits**:

- Reduces overhead of establishing connections.
- Limits the number of connections to the database.

**Implementing Connection Pooling in Python with psycopg2**:

```python
from psycopg2 import pool

db_pool = pool.SimpleConnectionPool(
    1,  # Minimum number of connections
    20,  # Maximum number of connections
    dbname="my_database",
    user="my_user",
    password="my_password",
    host="localhost",
    port="5432"
)

# Getting a connection from the pool
conn = db_pool.getconn()

# Returning the connection to the pool
db_pool.putconn(conn)
```

### Query Execution

Executing SQL queries is the core of database interactions.

#### Parameterized Queries

Parameterized queries prevent SQL injection by separating SQL code from data.

**Example in Python with psycopg2**:

```python
cursor = conn.cursor()
sql = "SELECT * FROM users WHERE username = %s;"
username = 'john_doe'

cursor.execute(sql, (username,))
results = cursor.fetchall()
```

**Benefits**:

- Prevents attackers from injecting malicious SQL code.
- Allows database to cache execution plans.

#### CRUD Operations

CRUD stands for Create, Read, Update, Delete—fundamental operations in data manipulation.

##### Create

**Inserting Data**:

```python
sql = "INSERT INTO users (username, email) VALUES (%s, %s);"
data = ('john_doe', 'john@example.com')

cursor.execute(sql, data)
conn.commit()
```

##### Read

**Selecting Data**:

```python
sql = "SELECT id, username FROM users WHERE active = %s;"
cursor.execute(sql, (True,))
users = cursor.fetchall()
```

##### Update

**Updating Data**:

```python
sql = "UPDATE users SET email = %s WHERE id = %s;"
cursor.execute(sql, ('new_email@example.com', user_id))
conn.commit()
```

##### Delete

**Deleting Data**:

```python
sql = "DELETE FROM users WHERE id = %s;"
cursor.execute(sql, (user_id,))
conn.commit()
```

#### Fetching Results

After executing a SELECT query, you need to retrieve the results.

- `fetchone()` retrieves the next row of a query result set.
- `fetchmany(size)` retrieves the next set of rows.
- `fetchall()` retrieves all remaining rows.

**Example**:

```python
cursor.execute("SELECT * FROM users;")
all_users = cursor.fetchall()

for user in all_users:
    print(user)
```

#### Transactions

Transactions ensure that a series of operations either all succeed or all fail, maintaining data integrity.

**Example**:

```python
try:
    cursor.execute("BEGIN;")
    cursor.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1;")
    cursor.execute("UPDATE accounts SET balance = balance + 100 WHERE id = 2;")
    conn.commit()
except Exception as e:
    conn.rollback()
    print(f"Transaction failed: {e}")
```

**ACID Properties**:

- **Atomicity** ensures that all operations in a transaction either complete successfully or do not occur at all, preventing partial updates.  
- **Consistency** guarantees that a database moves from one valid state to another after a transaction, maintaining data integrity.  
- **Isolation** ensures that concurrent transactions do not interfere with each other, preserving correctness.  
- **Durability** ensures that once a transaction is committed, its changes are permanently saved, even in the event of a system failure.  

### Error Handling

Proper error handling is crucial for building robust applications.

#### Catching Exceptions

Use try-except blocks to handle exceptions gracefully.

**Example in Python**:

```python
try:
    cursor.execute("SELECT * FROM non_existing_table;")
except psycopg2.Error as e:
    print(f"Database error: {e}")
```

#### Logging Errors

Logging errors helps in diagnosing issues, especially in production environments.

**Example**:

```python
import logging

logging.basicConfig(filename='app.log', level=logging.ERROR)

try:
    cursor.execute("SELECT * FROM users;")
except Exception as e:
    logging.error(f"Error executing query: {e}")
```

#### Retrying Failed Operations

Implement retry logic for transient errors like network issues.

**Example**:

```python
import time

max_retries = 5
for attempt in range(max_retries):
    try:
        cursor.execute("SELECT * FROM users;")
        break
    except psycopg2.OperationalError as e:
        if attempt < max_retries - 1:
            time.sleep(2 ** attempt)  # Exponential backoff
        else:
            raise
```

### Best Practices

#### Perform Data Processing in the Database

**Why**:

- Databases are optimized for data operations.
- Reduces data transfer between database and application.

**Example**:

Instead of fetching all data and filtering in code:

```python
cursor.execute("SELECT * FROM orders;")
orders = cursor.fetchall()
large_orders = [order for order in orders if order['amount'] > 1000]
```

Filter directly in SQL:

```python
cursor.execute("SELECT * FROM orders WHERE amount > %s;", (1000,))
large_orders = cursor.fetchall()
```

#### Implement Permission Checking via SQL

Enforce permissions at the database level for consistency and security.

**Methods**:

- **Views** allow the creation of predefined queries that expose only permitted data to users.  
- **Stored Procedures** encapsulate complex operations into reusable database functions.  
- **Row-Level Security** provides control over access to specific rows in a table, available in databases like PostgreSQL.  

**Example of a View**:

```sql
CREATE VIEW active_users AS
SELECT id, username, email FROM users WHERE active = TRUE;

GRANT SELECT ON active_users TO regular_user_role;
```

#### Use Object-Relational Mapping (ORM)

ORMs allow you to interact with the database using objects instead of raw SQL.

**Benefits**:

- **Productivity** improves as ORMs reduce the need for repetitive boilerplate code in database interactions.  
- **Maintainability** is improved through centralized models that represent database tables in code.  
- **Database Agnostic** design allows easier switching between different database systems without major code changes.  

**Popular ORMs**:

| Programming Language | ORM (Object-Relational Mapping) Tool |
|-----------------------|---------------------------------------|
| Python                | SQLAlchemy, Django ORM               |
| Java                  | Hibernate                            |
| C#                    | Entity Framework                     |
| JavaScript            | Sequelize                            |

**Example with SQLAlchemy**:

```python
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String)
    email = Column(String)

engine = create_engine('sqlite:///users.db')
Base.metadata.create_all(engine)
```

#### Treat SQL as an API

Expose specific database functionalities securely.

**Methods**:

- **Stored Procedures** encapsulate complex logic within the database, enabling reusable and secure operations.  
- **APIs** provide an indirect way to interact with the database, often using RESTful methods for controlled access.  
- **Database Roles and Permissions** help restrict and manage user access based on their responsibilities.  

**Example of a Stored Procedure in MySQL**:

```sql
DELIMITER //

CREATE PROCEDURE GetUserByEmail(IN userEmail VARCHAR(255))
BEGIN
    SELECT id, username FROM users WHERE email = userEmail;
END //

DELIMITER ;
```

#### Secure Database Connections and Credentials

- **Use Environment Variables** to store credentials securely instead of hard-coding them in the application.  
- **Encrypt Connections** with SSL/TLS to ensure data transmission is secure.  
- **Restrict Access** by limiting database connectivity to only necessary hosts.  
- **Regularly Update Credentials** to enhance security by periodically changing passwords.  

**Example**:

```python
import os

conn = psycopg2.connect(
    dbname=os.environ['DB_NAME'],
    user=os.environ['DB_USER'],
    password=os.environ['DB_PASSWORD'],
    host=os.environ['DB_HOST'],
    sslmode='require'
)
```

#### Handle Errors and Exceptions Gracefully

Ensure your application remains stable under unexpected conditions.

- **User-Friendly Messages** help inform users about issues without revealing sensitive details.  
- **Fallback Mechanisms** provide alternative solutions or retry options to ensure application reliability.  
- **Alerting** ensures administrators are notified promptly about critical issues for timely resolution.  

#### Monitor and Analyze Database Performance

Regularly assess performance to optimize and prevent issues.

- **Database Logs** are useful for analyzing slow queries and identifying performance bottlenecks.  
- **Monitoring Software** such as New Relic and Datadog provides insights into database performance and health.  
- **Query Profiling** with tools like `EXPLAIN` helps understand how queries are executed and optimized.

**Example of Query Profiling**:

```sql
EXPLAIN SELECT * FROM users WHERE email = 'john@example.com';
```

#### Continuously Review and Refactor Code

Maintain code quality and adapt to changing requirements.

- **Code Reviews** involve peer evaluations to identify and address potential issues in the code.  
- **Automated Testing** ensures reliability by using unit and integration tests to validate functionality.  
- **Refactoring** focuses on regularly improving the structure and maintainability of the code.  

#### Use Migrations for Schema Changes

Manage database schema changes systematically.

| Programming Language | Migration Tool                       |
|-----------------------|---------------------------------------|
| Python                | Alembic (SQLAlchemy), Django Migrations |
| Ruby                  | ActiveRecord Migrations              |
| JavaScript            | Knex.js Migrations                   |

**Example with Alembic**:

```bash
alembic revision --autogenerate -m "Added new column to users"
alembic upgrade head
```
