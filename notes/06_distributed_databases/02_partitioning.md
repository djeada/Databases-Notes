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

Example:

| ID  | Name  | Department | Hire Date |
| --- | ----- | ---------- | --------- |
| 1   | Alice | HR         | 2020-01-15|
| 2   | Bob   | IT         | 2021-03-22|
| 3   | Carol | HR         | 2019-06-30|
| 4   | David | IT         | 2020-11-01|
| 5   | Eve   | Finance    | 2021-07-14|
| 6   | Frank | HR         | 2018-12-12|
| 7   | Grace | IT         | 2021-05-05|
| 8   | Heidi | Finance    | 2020-08-23|
| 9   | Ivan  | HR         | 2019-10-10|
| 10  | Judy  | IT         | 2020-02-28|

Partition 1: Hire Dates Before 2020

| ID | Name  | Department | Hire Date |
| -- | ----- | ---------- | --------- |
| 3  | Carol | HR         | 2019-06-30|
| 6  | Frank | HR         | 2018-12-12|
| 9  | Ivan  | HR         | 2019-10-10|

Partition 2: Hire Dates in 2020

| ID  | Name  | Department | Hire Date |
| --- | ----- | ---------- | --------- |
| 1   | Alice | HR         | 2020-01-15|
| 4   | David | IT         | 2020-11-01|
| 8   | Heidi | Finance    | 2020-08-23|
| 10  | Judy  | IT         | 2020-02-28|

Partition 3: Hire Dates After 2020

| ID | Name  | Department | Hire Date |
| -- | ----- | ---------- | --------- |
| 2  | Bob   | IT         | 2021-03-22|
| 5  | Eve   | Finance    | 2021-07-14|
| 7  | Grace | IT         | 2021-05-05|

## List Partitioning

- List partitioning splits a table based on a list of predefined values in a specific column.
- Suitable for categorical data (e.g., partitioning by country or department)
- Useful for non-contiguous or discrete values

| ID  | Name  | Department | Hire Date |
| --- | ----- | ---------- | --------- |
| 1   | Alice | HR         | 2020-01-15|
| 2   | Bob   | IT         | 2021-03-22|
| 3   | Carol | HR         | 2019-06-30|
| 4   | David | IT         | 2020-11-01|
| 5   | Eve   | Finance    | 2021-07-14|
| 6   | Frank | HR         | 2018-12-12|
| 7   | Grace | IT         | 2021-05-05|
| 8   | Heidi | Finance    | 2020-08-23|
| 9   | Ivan  | HR         | 2019-10-10|
| 10  | Judy  | IT         | 2020-02-28|

Partition 1: HR Department

| ID | Name  | Department | Hire Date |
| -- | ----- | ---------- | --------- |
| 1  | Alice | HR         | 2020-01-15|
| 3  | Carol | HR         | 2019-06-30|
| 6  | Frank | HR         | 2018-12-12|
| 9  | Ivan  | HR         | 2019-10-10|

Partition 2: IT Department

| ID | Name  | Department | Hire Date |
| -- | ----- | ---------- | --------- |
| 2  | Bob   | IT         | 2021-03-22|
| 4  | David | IT         | 2020-11-01|
| 7  | Grace | IT         | 2021-05-05|
| 10 | Judy  | IT         | 2020-02-28|

Partition 3: Finance Department

| ID | Name  | Department | Hire Date |
| -- | ----- | ---------- | --------- |
| 5  | Eve   | Finance    | 2021-07-14|
| 8  | Heidi | Finance    | 2020-08-23|

## Hash Partitioning

- Hash partitioning splits a table based on a hash function applied to a specific column.
- Suitable for evenly distributing data across partitions
- Useful when there is no clear range or list partitioning criteria
- Helps to balance I/O load across multiple disks

| ID  | Name  | Department | Hire Date |
| --- | ----- | ---------- | --------- |
| 1   | Alice | HR         | 2020-01-15|
| 2   | Bob   | IT         | 2021-03-22|
| 3   | Carol | HR         | 2019-06-30|
| 4   | David | IT         | 2020-11-01|
| 5   | Eve   | Finance    | 2021-07-14|
| 6   | Frank | HR         | 2018-12-12|
| 7   | Grace | IT         | 2021-05-05|
| 8   | Heidi | Finance    | 2020-08-23|
| 9   | Ivan  | HR         | 2019-10-10|
| 10  | Judy  | IT         | 2020-02-28|

Partition 1: Hash mod 3 = 1
  
| ID  | Name  | Department | Hire Date |
| --- | ----- | ---------- | --------- |
| 1   | Alice | HR         | 2020-01-15|
| 4   | David | IT         | 2020-11-01|
| 7   | Grace | IT         | 2021-05-05|
| 10  | Judy  | IT         | 2020-02-28|

Partition 2: Hash mod 3 = 2

| ID | Name  | Department | Hire Date |
| -- | ----- | ---------- | --------- |
| 2  | Bob   | IT         | 2021-03-22|
| 5  | Eve   | Finance    | 2021-07-14|
| 8  | Heidi | Finance    | 2020-08-23|

Partition 3: Hash mod 3 = 0

| ID | Name  | Department | Hire Date |
| -- | ----- | ---------- | --------- |
| 3  | Carol | HR         | 2019-06-30|
| 6  | Frank | HR         | 2018-12-12|
| 9  | Ivan  | HR         | 2019-10-10|

## Key Partitioning

- Key partitioning is similar to hash partitioning but uses primary key columns for the hash function.
- Suitable for evenly distributing data across partitions using primary keys
- Useful when primary key columns are the most accessed columns in queries

| ID  | Name  | Department | Hire Date |
| --- | ----- | ---------- | --------- |
| 1   | Alice | HR         | 2020-01-15|
| 2   | Bob   | IT         | 2021-03-22|
| 3   | Carol | HR         | 2019-06-30|
| 4   | David | IT         | 2020-11-01|
| 5   | Eve   | Finance    | 2021-07-14|
| 6   | Frank | HR         | 2018-12-12|
| 7   | Grace | IT         | 2021-05-05|
| 8   | Heidi | Finance    | 2020-08-23|
| 9   | Ivan  | HR         | 2019-10-10|
| 10  | Judy  | IT         | 2020-02-28|

Partition 1: Keys 1-3

| ID  | Name  | Department | Hire Date |
| --- | ----- | ---------- | --------- |
| 1   | Alice | HR         | 2020-01-15|
| 2   | Bob   | IT         | 2021-03-22|
| 3   | Carol | HR         | 2019-06-30|

Partition 2: Keys 4-6

| ID  | Name  | Department | Hire Date |
| --- | ----- | ---------- | --------- |
| 4   | David | IT         | 2020-11-01|
| 5   | Eve   | Finance    | 2021-07-14|
| 6   | Frank | HR         | 2018-12-12|

Partition 3: Keys 7-10

| ID  | Name  | Department | Hire Date |
| --- | ----- | ---------- | --------- |
| 7   | Grace | IT         | 2021-05-05|
| 8   | Heidi | Finance    | 2020-08-23|
| 9   | Ivan  | HR         | 2019-10-10|
| 10  | Judy  | IT         | 2020-02-28|

## Composite Partitioning

- Composite partitioning combines two or more partitioning types (e.g., range-hash, range-list, etc.)
- Suitable for complex partitioning requirements
- Useful to further subdivide partitions for more granular data management or performance optimization

## Best Practices for Partitioning

- Choose the type of partitioning based on query patterns and data characteristics.
- Regularly monitor and adjust partitioning schemes to maintain optimal performance.
- Consider partition pruning to optimize query performance.
- Periodically reorganize or rebuild partitions for maintenance.
