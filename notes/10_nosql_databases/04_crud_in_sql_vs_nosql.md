## CRUD in SQL vs NoSQL
- Compares common CRUD operations in SQL (relational databases) and MongoDB (NoSQL document store)
- CRUD: Create, Read, Update, Delete

## Create

### SQL
- Syntax: `INSERT INTO table_name (column1, column2, ...) VALUES (value1, value2, ...)`
- Example: `INSERT INTO users (first_name, last_name, age) VALUES ('John', 'Doe', 25)`

### MongoDB
- Syntax: `db.collection.insertOne(document)`
- Example: `db.users.insertOne({first_name: 'John', last_name: 'Doe', age: 25})`

## Read

### SQL
- Syntax: `SELECT column1, column2, ... FROM table_name WHERE condition`
- Example: `SELECT first_name, last_name, age FROM users WHERE age = 25`

### MongoDB
- Syntax: `db.collection.find(query, projection)`
- Example: `db.users.find({age: 25}, {first_name: 1, last_name: 1, age: 1})`

## Update

### SQL
- Syntax: `UPDATE table_name SET column1 = value1, column2 = value2, ... WHERE condition`
- Example: `UPDATE users SET age = 26 WHERE first_name = 'John' AND last_name = 'Doe'`

### MongoDB
- Syntax: `db.collection.updateOne(filter, update, options)`
- Example: `db.users.updateOne({first_name: 'John', last_name: 'Doe'}, {$set: {age: 26}})`

## Delete

### SQL
- Syntax: `DELETE FROM table_name WHERE condition`
- Example: `DELETE FROM users WHERE first_name = 'John' AND last_name = 'Doe'`

### MongoDB
- Syntax: `db.collection.deleteOne(filter)`
- Example: `db.users.deleteOne({first_name: 'John', last_name: 'Doe'})`

## Best Practices
- Understand the differences between SQL and MongoDB CRUD operations
- Choose the appropriate database and query syntax based on application requirements
- Continuously monitor and analyze query performance to identify areas for improvement
