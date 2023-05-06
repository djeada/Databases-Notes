## Accessing databases in code
Accessing databases in code is essential for building data-driven applications

## Database Connection
### Connection Libraries
Use appropriate libraries or drivers for the specific database and programming language

### Connection String
Specify the database server, credentials, and other connection parameters

### Connection Pooling
Reuse database connections to improve performance and resource utilization

## Query Execution

### Parameterized Queries
Use parameterized queries to prevent SQL injection and improve query performance

### CRUD Operations
Implement Create, Read, Update, and Delete (CRUD) operations using the appropriate SQL statements

### Fetching Results
Retrieve query results using the appropriate data structures (e.g., arrays, lists, dictionaries)

### Transactions
Use transactions to ensure data integrity and consistency across multiple SQL statements

##  Error Handling
### Catching Exceptions
Catch and handle database exceptions or errors in the application code

### Logging Errors
Log errors and exceptions for analysis and troubleshooting

### Retrying Failed Operations
Implement retry logic for transient errors or connection issues

## Best Practices
- Use appropriate libraries and drivers for the specific database and programming language
- Secure database connections and credentials
- Implement parameterized queries and transactions for security and consistency
- Handle errors and exceptions gracefully
- Monitor and analyze database access patterns and performance to identify areas for improvement
- Continuously review and adjust the code for optimal performance and maintainability

### Loop in DB, not in your code
Do the filtering in the database. In most cases, it is faster than the
loops in your programming language. And if the DB is not fast enough,
then I guess there is just the matching index missing up until now.
### Do permission checking via SQL
Imagine you have three models (users, groups, and permissions) as tables
in a relational database system.
Most systems do the permission checking via source code. Example: `if
user.is_admin then return True`. 
Sooner or later you need the list of items: Show all items which the
current user may see.
Now you write SQL (or use your ORM) to create a queryset that returns
all items which satisfy the needed conditions.
Now you have two implementations. The first `if user.is_admin then
return True` and one which uses set operations (SQL). This is redundant and looking
for trouble. Sooner or later your permission checks get more complex and then one 
implementation will get out of sync.
That's why I think: do permission checking via SQL
Some call this "Authorization predicate push-down"
### Real men use ORM
[ORM (Object-relational mapping)](https://en.wikipedia.org/wiki/Objectrelational_mapping) makes daily
work much easier. The above heading is a stupid joke. Clever people use tools to 
make work simpler, more fun, and more
convenient. ORMs are great. 
Some (usually elderly) developers fear that an ORM is slower than hand-crafted and 
optimized SQL. Maybe
there are corner cases where this prejudice is true. But that's not a reason to 
avoid ORMs. Just use them,
and if you hit a corner case, then use raw SQL.
See [premature optimization is the root of all evil](#premature-optimization-isthe-root-of-all-evil)
Make your life easy, use ORM.
Example: [Django ORM "Filtering on a Subquery() or Exists() 
expressions"](https://docs.djangoproject.com/en/dev/ref/models/expressions/
#filtering-on-a-subquery-or-exists-expressions). 
```
# Select all rows of the model Post, which have a comment which was created a day 
ago:
one_day_ago = timezone.now() - timedelta(days=1)
recent_comments = Comment.objects.filter(
 post=OuterRef('pk'),
 created_at__gte=one_day_ago,
)
Post.objects.filter(Exists(recent_comments))
```
For me above code is super easy to read.
### SQL is an API
If you have a database-driven application and a third party tool wants
to send data to the application, then sometimes the easiest solution is
to give the third party access to the database.
You can create a special database user that has only access to one table.
That's easy.
Nitpickers will disagree: If the database schema changes, then the
communication between both systems will break. Of course, that's true.
But in most cases, this will be the same if you use a "real" API. If
there is a change to the data structure, then the API needs to be
changed, too.
I don't say that SQL is always the best solution. Of course, HTTP based
APIs are better in general. But in some use cases doing more is not
needed.


Note 1: Creating a SQLite database and connecting to it in Python
To create a SQLite database in Python, you'll need to import the sqlite3 module and use the connect() function to create a connection object. If the database doesn't exist, it will be created automatically.

python

import sqlite3

conn = sqlite3.connect('my_database.db')

Note 2: Removing a SQLite database
To remove a SQLite database, you can delete the file containing the database. Use the os module to remove the file.

python

import os

os.remove('my_database.db')

Note 3: Creating a table in SQLite
To create a table, you need to execute a SQL CREATE TABLE statement using the execute() method on a cursor object.

python

cursor = conn.cursor()

sql_create_table = '''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    age INTEGER
);
'''

cursor.execute(sql_create_table)
conn.commit()

Note 4: Removing a table in SQLite
To remove a table, you can execute a SQL DROP TABLE statement.

python

sql_drop_table = 'DROP TABLE IF EXISTS users;'

cursor.execute(sql_drop_table)
conn.commit()

Note 5: Inserting data into a table
To insert data into a table, you can execute a SQL INSERT statement.

python

sql_insert_data = 'INSERT INTO users (name, age) VALUES (?, ?);'
user_data = ('John Doe', 30)

cursor.execute(sql_insert_data, user_data)
conn.commit()

Note 6: Reading data from a table
To read data from a table, you can execute a SQL SELECT statement and use the fetchall() method to retrieve the results.

python

sql_select_data = 'SELECT * FROM users;'

cursor.execute(sql_select_data)
result = cursor.fetchall()

for row in result:
    print(row)

Note 7: Updating data in a table
To update data in a table, you can execute a SQL UPDATE statement.

python

sql_update_data = 'UPDATE users SET age = ? WHERE name = ?;'
new_data = (31, 'John Doe')

cursor.execute(sql_update_data, new_data)
conn.commit()

Note 8: Deleting data from a table
To delete data from a table, you can execute a SQL DELETE statement.

python

sql_delete_data = 'DELETE FROM users WHERE name = ?;'
name = ('John Doe',)

cursor.execute(sql_delete_data, name)
conn.commit()

Remember to close the connection after you're done working with the database.

python

conn.close()
