## SQLite
- SQLite: a self-contained, serverless, zero-configuration, transactional SQL database engine
- Lightweight and easy to use, suitable for small to medium-sized applications
- Ideal for embedded systems, mobile applications, and local data storage

## Features

### Serverless and Self-Contained
- No separate server process or setup required
- Database stored in a single file on disk

### Transactional
Supports ACID transactions, ensuring data consistency

### Cross-Platform
Compatible with various operating systems, including Windows, macOS, Linux, and Android

### Small Footprint
Low memory and storage requirements, making it suitable for embedded systems and mobile applications

### Extensive Language Support
APIs available for several programming languages, including C, C++, Java, Python, and more

### Public Domain
Free and open-source, with no licensing restrictions

## Limitations

### Not Suitable for Large Applications
Limited scalability compared to more robust database engines like MySQL or PostgreSQL

### Limited Concurrency
Write transactions lock the entire database, which may cause contention in multi-user applications

### Lack of User Management and Access Control
No built-in support for user authentication or role-based access control

### Subset of SQL Features
Some SQL features, such as RIGHT JOINs and complete ALTER TABLE support, are not available in SQLite

## Use Cases

### Embedded Systems
Ideal for applications that require a lightweight, self-contained database engine

### Mobile Applications
Popular choice for Android and iOS app development due to its low footprint and ease of use

### Desktop Applications
Suitable for local data storage in desktop applications where a full-fledged database server is not required

### Prototyping and Testing
Provides a simple and convenient way to prototype and test applications before deploying to a production database server

## SQLite Commands
### Creating a Database
SQLite databases are created by opening a file with the appropriate API or command-line tool

### Creating Tables

```
CREATE TABLE table_name (
 column_name1 datatype PRIMARY KEY,
 column_name2 datatype NOT NULL,
 ...
);
```

### Inserting Data

```
INSERT INTO table_name (column1, column2, ...)
VALUES (value1, value2, ...);
```

### Querying Data

```
SELECT column1, column2, ...
FROM table_name
WHERE condition;
```

### Updating Data

```
UPDATE table_name
SET column1 = value1, column2 = value2, ...
WHERE condition;
```

### Deleting Data

```
DELETE FROM table_name
WHERE condition;
```

### Dropping Tables

```
DROP TABLE table_name;
```
