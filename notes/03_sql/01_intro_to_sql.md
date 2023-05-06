## Introduction to SQL

SQL (Structured Query Language) is a standardized, domain-specific language used for managing and querying relational databases.

## SQL Basics

- SQL focuses on basic and complex joins, compound queries, stored procedures, window functions, and query optimization.
- Good SQL candidates can optimize a set of tables and queries using query plans and ensuring SARGable query criteria.
- Outstanding candidates can design partitioning schemes and update and replication strategies.

## Key Concepts

- Complex joins and using aliases
- Aggregation and analytic functions
- Subqueries, Common Table Expressions (CTEs), and window functions
- Stored procedures
- Pitfalls of SQL, such as issues with NULL values in joins

## SQL Standardization

- SQL is standardized by ANSI and ISO.
- Most implementations are older than the standard.
- Example drafts of the standard: [SQL 1992 draft (txt, 1.5 MB)](http://www.contrib.andrew.cmu.edu/~shadow/sql/sql1992.txt)

## SQL Implementations

- Open source: MySQL, MariaDB, PostgreSQL, SQLite
- Proprietary: Oracle, SQL Server (Microsoft)
- [Popularity according to Stackoverflow Developer Survey](https://insights.stackoverflow.com/survey/2019#technology-_-databases)

## General SQL Syntax

- SQL statements are terminated by `;`
- Two variants of comments: `/* multi-line comment */` and `-- single-line comment`
- SQL is mostly case insensitive
- Table names and column names are converted to uppercase by SQL, with some exceptions
- Table names and column names can be quoted to maintain exact spelling

## SQL Data Types

Different SQL implementations may have slightly different data types, but most follow the ISO / ANSI SQL Standard. Here's an overview of common data types across various SQL implementations.

### ISO / ANSI SQL Standard (selection)

- `BOOLEAN`: true or false values
- `INT` / `INTEGER`, `SMALLINT`, `BIGINT`: integer values of various sizes
- `NUMERIC` / `DECIMAL`: fixed-point exact numbers, with user-defined precision and scale
- `REAL`, `DOUBLE PRECISION`: floating-point approximate numbers, with single and double precision
- `VARCHAR(n)`: variable-length character strings with a maximum length of n characters
- `VARBINARY(n)`: variable-length binary strings with a maximum length of n bytes
- `DATE`: date values (year, month, day)
- `TIME`: time values (hour, minute, second)
- `TIMESTAMP`: date and time values combined

### MySQL / MariaDB Data Types (selection)

- `TINYINT`, `SMALLINT`, `MEDIUMINT`, `INT` / `INTEGER`, `BIGINT`: integer values of various sizes
- `DECIMAL` / `NUMERIC`, `FLOAT`, `DOUBLE`: fixed-point and floating-point numbers
- `CHAR(n)`, `VARCHAR(n)`: fixed-length and variable-length character strings
- `BINARY(n)`, `VARBINARY(n)`: fixed-length and variable-length binary strings
- `DATE`, `TIME`, `DATETIME`, `TIMESTAMP`: date and time values
- `YEAR`: year values only
- `TEXT`, `MEDIUMTEXT`, `LONGTEXT`: text strings of various sizes
- `BLOB`, `MEDIUMBLOB`, `LONGBLOB`: binary strings of various sizes

### PostgreSQL Data Types (selection)

- `SMALLINT`, `INT` / `INTEGER`, `BIGINT`: integer values of various sizes
- `DECIMAL` / `NUMERIC`, `REAL`, `DOUBLE PRECISION`: fixed-point and floating-point numbers
- `CHAR(n)`, `VARCHAR(n)`, `TEXT`: fixed-length, variable-length, and unlimited-length character strings
- `BYTEA`: binary data
- `DATE`, `TIME`, `TIMESTAMP`: date and time values
- `INTERVAL`: time intervals
- `BOOLEAN`: true or false values
- `JSON`, `JSONB`: JSON data
- `UUID`: universally unique identifiers

### SQL Server (Microsoft) Data Types (selection)

- `BIT`: 0, 1, or NULL values
- `TINYINT`, `SMALLINT`, `INT` / `INTEGER`, `BIGINT`: integer values of various sizes
- `DECIMAL` / `NUMERIC`, `REAL`, `FLOAT`: fixed-point and floating-point numbers
- `CHAR(n)`, `VARCHAR(n)`, `TEXT`: fixed-length, variable-length, and unlimited-length character strings
- `BINARY(n)`, `VARBINARY(n)`, `IMAGE`: fixed-length, variable-length, and unlimited-length binary strings
- `DATE`, `TIME`, `DATETIME`, `DATETIME2`, `SMALLDATETIME`, `TIMESTAMP`: date and time values
- `MONEY`, `SMALLMONEY`: currency values
- `UNIQUEIDENTIFIER`: globally unique identifiers (GUIDs)
