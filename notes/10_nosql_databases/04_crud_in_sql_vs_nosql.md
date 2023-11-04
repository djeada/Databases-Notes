## CRUD in SQL vs NoSQL

- Compares common CRUD operations in SQL (relational databases) and MongoDB (NoSQL document store)
- **CRUD**: Create, Read, Update, Delete
  
| Operation | SQL Syntax                                   | SQL Example                                      | MongoDB Syntax                               | MongoDB Example                                    |
|-----------|----------------------------------------------|--------------------------------------------------|-----------------------------------------------|----------------------------------------------------|
| Create    | `INSERT INTO table_name (column1, column2, ...)` | `INSERT INTO users (first_name, last_name, age) VALUES ('John', 'Doe', 25)` | `db.collection.insertOne(document)`          | `db.users.insertOne({first_name: 'John', last_name: 'Doe', age: 25})` |
| Read      | `SELECT column1, column2, ... FROM table_name WHERE condition` | `SELECT first_name, last_name, age FROM users WHERE age = 25` | `db.collection.find(query, projection)`     | `db.users.find({age: 25}, {first_name: 1, last_name: 1, age: 1})` |
| Update    | `UPDATE table_name SET column1 = value1, column2 = value2, ... WHERE condition` | `UPDATE users SET age = 26 WHERE first_name = 'John' AND last_name = 'Doe'` | `db.collection.updateOne(filter, update, options)` | `db.users.updateOne({first_name: 'John', last_name: 'Doe'}, {$set: {age: 26}})` |
| Delete    | `DELETE FROM table_name WHERE condition`    | `DELETE FROM users WHERE first_name = 'John' AND last_name = 'Doe'` | `db.collection.deleteOne(filter)`            | `db.users.deleteOne({first_name: 'John', last_name: 'Doe'})` |

## Best Practices
- Understand the differences between SQL and MongoDB CRUD operations
- Choose the appropriate database and query syntax based on application requirements
- Continuously monitor and analyze query performance to identify areas for improvement
