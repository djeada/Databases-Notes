# Accessing Databases in Code

Accessing databases through code is a fundamental skill for developers building applications that rely on data storage and retrieval. Whether you're developing a web application, mobile app, or any software that requires data persistence, understanding how to interact with databases programmatically is essential.

## Understanding Databases

### Types of Databases

**Relational Databases (SQL)**:

- **MySQL**: Popular open-source relational database.
- **PostgreSQL**: Advanced open-source relational database with extensive features.
- **SQLite**: Lightweight, file-based relational database.
- **Microsoft SQL Server**: Enterprise-level relational database by Microsoft.
- **Oracle Database**: Comprehensive database solution for large-scale applications.

**NoSQL Databases**:

- **MongoDB**: Document-oriented database storing JSON-like documents.
- **Redis**: In-memory key-value store, often used for caching.
- **Cassandra**: Distributed database for handling large amounts of data.
- **CouchDB**: Database that uses JSON for documents, JavaScript for MapReduce queries.

### Choosing the Right Database

Selecting the appropriate database depends on:

- **Data Structure**: Structured vs. unstructured data.
- **Scalability Requirements**: Read/write performance, horizontal scaling.
- **Consistency Needs**: Strong consistency vs. eventual consistency.
- **Community and Support**: Documentation, community support, third-party tools.
- **Licensing and Cost**: Open-source vs. proprietary solutions.

---

## Database Connection

Establishing a connection to the database is the first step in interacting with it programmatically.

### Connection Libraries

Each programming language and database system requires specific libraries or drivers to facilitate communication.

**Examples**:

- **Python**:
  - **MySQL**: `mysql-connector-python`, `PyMySQL`
  - **PostgreSQL**: `psycopg2`, `asyncpg`
  - **SQLite**: Built-in `sqlite3` module
- **Java**:
  - **JDBC Drivers**: Database-specific JDBC drivers like `mysql-connector-java`, `postgresql-jdbc`
- **C#/.NET**:
  - **SQL Server**: `System.Data.SqlClient`
  - **MySQL**: `MySql.Data`
- **JavaScript (Node.js)**:
  - **MySQL**: `mysql`, `mysql2`
  - **PostgreSQL**: `pg`

**Installing a Python Library for PostgreSQL**:

```bash
pip install psycopg2-binary
```

### Connection Strings

A connection string contains the information required to establish a connection to the database.

**Components**:

- **Hostname**: The server's address.
- **Port**: The port number (default for MySQL is 3306, PostgreSQL is 5432).
- **Database Name**: The specific database to connect to.
- **Username and Password**: Credentials for authentication.
- **Additional Parameters**: SSL mode, timeouts, charset.

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

### Connection Pooling

Connection pooling manages a pool of database connections, reusing them instead of creating new ones for each request.

**Benefits**:

- **Performance Improvement**: Reduces overhead of establishing connections.
- **Resource Management**: Limits the number of connections to the database.

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

---

## Query Execution

Executing SQL queries is the core of database interactions.

### Parameterized Queries

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

- **Security**: Prevents attackers from injecting malicious SQL code.
- **Performance**: Allows database to cache execution plans.

### CRUD Operations

CRUD stands for Create, Read, Update, Delete—fundamental operations in data manipulation.

#### Create

**Inserting Data**:

```python
sql = "INSERT INTO users (username, email) VALUES (%s, %s);"
data = ('john_doe', 'john@example.com')

cursor.execute(sql, data)
conn.commit()
```

#### Read

**Selecting Data**:

```python
sql = "SELECT id, username FROM users WHERE active = %s;"
cursor.execute(sql, (True,))
users = cursor.fetchall()
```

#### Update

**Updating Data**:

```python
sql = "UPDATE users SET email = %s WHERE id = %s;"
cursor.execute(sql, ('new_email@example.com', user_id))
conn.commit()
```

#### Delete

**Deleting Data**:

```python
sql = "DELETE FROM users WHERE id = %s;"
cursor.execute(sql, (user_id,))
conn.commit()
```

### Fetching Results

After executing a SELECT query, you need to retrieve the results.

- **`fetchone()`**: Retrieves the next row of a query result set.
- **`fetchmany(size)`**: Retrieves the next set of rows.
- **`fetchall()`**: Retrieves all remaining rows.

**Example**:

```python
cursor.execute("SELECT * FROM users;")
all_users = cursor.fetchall()

for user in all_users:
    print(user)
```

### Transactions

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

- **Atomicity**: All operations complete successfully or none do.
- **Consistency**: Transforms the database from one valid state to another.
- **Isolation**: Concurrent transactions are isolated from each other.
- **Durability**: Committed transactions are saved permanently.

---

## Error Handling

Proper error handling is crucial for building robust applications.

### Catching Exceptions

Use try-except blocks to handle exceptions gracefully.

**Example in Python**:

```python
try:
    cursor.execute("SELECT * FROM non_existing_table;")
except psycopg2.Error as e:
    print(f"Database error: {e}")
```

### Logging Errors

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

### Retrying Failed Operations

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

---

## Best Practices

### Perform Data Processing in the Database

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

### Implement Permission Checking via SQL

Enforce permissions at the database level for consistency and security.

**Methods**:

- **Views**: Create views that expose only permitted data.
- **Stored Procedures**: Encapsulate complex operations.
- **Row-Level Security**: Available in some databases like PostgreSQL.

**Example of a View**:

```sql
CREATE VIEW active_users AS
SELECT id, username, email FROM users WHERE active = TRUE;

GRANT SELECT ON active_users TO regular_user_role;
```

### Use Object-Relational Mapping (ORM)

ORMs allow you to interact with the database using objects instead of raw SQL.

**Benefits**:

- **Productivity**: Less boilerplate code.
- **Maintainability**: Centralized models.
- **Database Agnostic**: Easier to switch databases.

**Popular ORMs**:

- **Python**: SQLAlchemy, Django ORM
- **Java**: Hibernate
- **C#**: Entity Framework
- **JavaScript**: Sequelize

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

### Treat SQL as an API

Expose specific database functionalities securely.

**Methods**:

- **Stored Procedures**: Encapsulate logic in the database.
- **APIs**: Use RESTful APIs to interact with the database indirectly.
- **Database Roles and Permissions**: Grant limited access to users.

**Example of a Stored Procedure in MySQL**:

```sql
DELIMITER //

CREATE PROCEDURE GetUserByEmail(IN userEmail VARCHAR(255))
BEGIN
    SELECT id, username FROM users WHERE email = userEmail;
END //

DELIMITER ;
```

### Secure Database Connections and Credentials

**Best Practices**:

- **Use Environment Variables**: Do not hard-code credentials.
- **Encrypt Connections**: Use SSL/TLS.
- **Restrict Access**: Limit database access to necessary hosts.
- **Regularly Update Credentials**: Change passwords periodically.

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

### Handle Errors and Exceptions Gracefully

Ensure your application remains stable under unexpected conditions.

**Strategies**:

- **User-Friendly Messages**: Inform users without exposing sensitive details.
- **Fallback Mechanisms**: Provide alternative solutions or retries.
- **Alerting**: Notify administrators of critical issues.

### Monitor and Analyze Database Performance

Regularly assess performance to optimize and prevent issues.

**Tools**:

- **Database Logs**: Analyze slow queries.
- **Monitoring Software**: Use tools like New Relic, Datadog.
- **Query Profiling**: Use `EXPLAIN` to understand query execution.

**Example of Query Profiling**:

```sql
EXPLAIN SELECT * FROM users WHERE email = 'john@example.com';
```

### Continuously Review and Refactor Code

Maintain code quality and adapt to changing requirements.

**Practices**:

- **Code Reviews**: Peer reviews to catch potential issues.
- **Automated Testing**: Write unit and integration tests.
- **Refactoring**: Regularly improve code structure.

### Use Migrations for Schema Changes

Manage database schema changes systematically.

**Tools**:

- **Python**: Alembic (SQLAlchemy), Django Migrations
- **Ruby**: ActiveRecord Migrations
- **JavaScript**: Knex.js Migrations

**Example with Alembic**:

```bash
alembic revision --autogenerate -m "Added new column to users"
alembic upgrade head
```
