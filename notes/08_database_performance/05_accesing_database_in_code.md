## Accessing Databases in Code

Accessing databases in code is essential for building data-driven applications.

### Database Connection

1. **Connection Libraries**: Use appropriate libraries or drivers for the specific database and programming language
2. **Connection String**: Specify the database server, credentials, and other connection parameters
3. **Connection Pooling**: Reuse database connections to improve performance and resource utilization

Example: Connecting to a SQLite database in Python

```python
import sqlite3

conn = sqlite3.connect('my_database.db')
```

### Query Execution

1. **Parameterized Queries**: Use parameterized queries to prevent SQL injection and improve query performance
2. **CRUD Operations**: Implement Create, Read, Update, and Delete (CRUD) operations using the appropriate SQL statements
3. **Fetching Results**: Retrieve query results using the appropriate data structures (e.g., arrays, lists, dictionaries)
4. **Transactions**: Use transactions to ensure data integrity and consistency across multiple SQL statements

Example: Inserting data into a SQLite database using a parameterized query

```python
cursor = conn.cursor()

sql_insert_data = 'INSERT INTO users (name, age) VALUES (?, ?);'
user_data = ('John Doe', 30)

cursor.execute(sql_insert_data, user_data)
conn.commit()
```

### Error Handling

1. **Catching Exceptions**: Catch and handle database exceptions or errors in the application code
2. **Logging Errors**: Log errors and exceptions for analysis and troubleshooting
3. **Retrying Failed Operations**: Implement retry logic for transient errors or connection issues

Example: Error handling when executing a SQL query in Python

```python
try:
    cursor.execute(sql_query, params)
except sqlite3.Error as e:
    print(f"An error occurred: {e}")
```

### Best Practices

#### Loop in DB, not in your code

Filter data in the database, as it is often faster than using loops in your programming language. If the database isn't fast enough, it may be missing an appropriate index.

#### Do permission checking via SQL

When dealing with multiple models (e.g., users, groups, and permissions) in a relational database system, perform permission checking via SQL instead of source code to avoid redundancy and ensure consistency.

#### Use ORM (Object-Relational Mapping)

ORM makes daily work easier, simplifies tasks, and is more convenient. Use ORM by default, and switch to raw SQL only when necessary.

Example: Query using Django ORM

```python
from myapp.models import User

users = User.objects.filter(age__gte=18)
```

#### SQL as an API

In some cases, giving third-party tools access to the database can be a simple and effective solution for data exchange. Use database-specific users and permissions to limit access to specific tables or resources.

#### Other rules of thumb

* Use appropriate libraries and drivers for the specific database and programming language
* Secure database connections and credentials
* Implement parameterized queries and transactions for security and consistency
* Handle errors and exceptions gracefully
* Monitor and analyze database access patterns and performance to identify areas for improvement
* Continuously review and adjust the code for optimal performance and maintainability
