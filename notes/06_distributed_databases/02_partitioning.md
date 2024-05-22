## Partitioning
- Partitioning is a database optimization technique
- Improves performance and manageability of large tables
  
```
+----------------------------------------------+
|                Large Table                   |
+----------------------------------------------+
|         |         |         |        |       |
| Part 1  | Part 2  | Part 3  | Part 4 | ...   |
|         |         |         |        |       |
+---------+---------+---------+--------+-------+
| Rows 1- | Rows    | Rows    | Rows   |       |
| 2000    | 2001-   | 4001-   | 6001-  | ...   |
|         | 4000    | 6000    | 8000   |       |
+---------+---------+---------+--------+-------+
```

In this example, the Large Table is partitioned into smaller parts, each containing a portion of the rows. For example, Part 1 contains Rows 1-2000, Part 2 contains Rows 2001-4000, and so on. This is just one way to partition a table, and different database systems might implement partitioning differently.

## Purpose

- Partitioning involves dividing large tables into smaller, more manageable pieces.
- It improves query performance by allowing queries to access only the relevant partitions.
- Partitioning also simplifies data management tasks like backup, archiving, etc.

## Range Partitioning

- Range partitioning splits a table based on a range of values in a specific column.
- Suitable for time-based data (e.g., sales data partitioned by date or month)
- Useful for continuous numerical data (e.g., income range or age groups)

## List Partitioning

- List partitioning splits a table based on a list of predefined values in a specific column.
- Suitable for categorical data (e.g., partitioning by country or department)
- Useful for non-contiguous or discrete values

## Hash Partitioning

- Hash partitioning splits a table based on a hash function applied to a specific column.
- Suitable for evenly distributing data across partitions
- Useful when there is no clear range or list partitioning criteria
- Helps to balance I/O load across multiple disks

## Key Partitioning

- Key partitioning is similar to hash partitioning but uses primary key columns for the hash function.
- Suitable for evenly distributing data across partitions using primary keys
- Useful when primary key columns are the most accessed columns in queries

## Composite Partitioning

- Composite partitioning combines two or more partitioning types (e.g., range-hash, range-list, etc.)
- Suitable for complex partitioning requirements
- Useful to further subdivide partitions for more granular data management or performance optimization

## Best Practices for Partitioning

- Choose the type of partitioning based on query patterns and data characteristics.
- Regularly monitor and adjust partitioning schemes to maintain optimal performance.
- Consider partition pruning to optimize query performance.
- Periodically reorganize or rebuild partitions for maintenance.
