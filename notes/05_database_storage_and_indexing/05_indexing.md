## Indexing
- Indexing is a database optimization technique
- Improves speed and efficiency of data retrieval

## Basics

A. Purpose
  1. Speed up query execution
  2. Enforce unique constraints on columns
  3. Locate information quickly

B. Types
  1. B-trees, bitmap indexes, and hash indexes
  2. Choice depends on data nature, query type, and DBMS used

##  Types of Indexes

A. Clustered Index
  - Determines physical order of data
  - One per table
  - Faster data retrieval

B. Non-clustered Index
  - Doesn't affect physical order of data
  - Multiple per table
  - Index contains pointers to data rows

## Creating Indexes
A. Clustered Index

```sql
CREATE CLUSTERED INDEX index_name ON table_name(column_name)
```

B. Non-clustered Index

```sql
CREATE NONCLUSTERED INDEX index_name ON table_name(column_name)
```

## Dropping Indexes

```sql
DROP INDEX table_name.index_name
```

## Benefits of Indexing
- Faster data retrieval
- Improved query performance
- Efficient use of resources

## Drawbacks of Indexing
- Increased storage space
- Slower insert, update, and delete operations
- Requires maintenance

## Index Maintenance
- Regularly reorganize or rebuild indexes
- Monitor index fragmentation and usage
- Adjust indexes based on performance analysis

## Best Practices
- Index columns with high selectivity
- Avoid indexing frequently updated columns
- Use appropriate index types based on the use case
- Limit the number of indexes per table
- Periodically review and optimize indexes

## Example

Table: employees
   
| EmployeeID | FirstName | LastName | Department |
| ---------- | --------- | -------- | ---------- |
| 1          | John      |  Doe     |   HR       |
| 2          | Jane      |  Smith   |   IT       |
| 3          | Michael   |  Brown   |   Finance  |
| 4          | Emily     |  White   |   IT |
| 5          | Robert    |  Green   |   HR |

Command to create index on Department column:
   
```sql
CREATE NONCLUSTERED INDEX idx_department ON employees(Department)
```

After adding the index:

| Department | Row Pointer |
| ---------- | ----------- |
| Finance    |  3 |
| HR         |  1 |
| HR         |  5 |
| IT         |  2 |
| IT         |  4 |

- Index on Department column speeds up queries filtering or sorting by Department
- Table doesn't change, only index structure is added for faster querying

## Key vs. Non-Key Column Indexing

A. Key Column Indexing
  1. Index on unique identifying columns
  2. Improves performance for filtering, sorting, or joining
  
B. Non-Key Column Indexing
  1. Index on non-unique columns
  2. Improves performance for filtering or sorting

## Index Scan vs. Index-Only Scan

A. Index Scan
  1. Uses index to locate rows, reads data from table
  2. Improves query performance, may still read data from disk
  
B. Index-Only Scan
  1. Uses index to retrieve necessary data without accessing table
  2. Minimizes data read from disk, improves query performance

## Combining Database Indexes

A. Composite Indexes
  1. Indexes with multiple columns
  2. Consider column order for performance

B. Covering Indexes
  1. Index includes all columns required for a query
  2. Improves performance for specific queries, may consume more space and require more maintenance
