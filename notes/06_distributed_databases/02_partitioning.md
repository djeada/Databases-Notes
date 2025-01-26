## Partitioning

Partitioning involves dividing a large database table into smaller, more manageable pieces called partitions. This method helps improve query performance because the database can access only the relevant partitions when executing queries, rather than scanning the entire table. It also simplifies data management tasks like backups, archiving, and purging old data.

After reading the material, you should be able to answer the following questions:

1. What is partitioning and how does it enhance database performance and manageability?
2. What are the different types of partitioning methods and in what scenarios are they most effectively used?
3. How does range partitioning work, and what are its advantages and potential drawbacks?
4. What best practices should be followed to optimize the use of partitioning in a database environment?
5. How do composite partitioning strategies combine multiple partitioning methods, and what benefits do they offer?

### What do we mean by Partitioning?

Imagine a colossal table that stores millions of rows. Searching through this massive table every time can be time-consuming and inefficient. Partitioning slices the table into smaller sections based on specific criteria, allowing the database engine to quickly locate and retrieve the data it needs.

```
+----------------------------------------------+
|                 Large Table                  |
+----------------------------------------------+
|         |         |         |        |       |
| Part 1  | Part 2  | Part 3  | Part 4 |  ...  |
|         |         |         |        |       |
+---------+---------+---------+--------+-------+
| Rows 1- | Rows    | Rows    | Rows   |       |
| 2000    | 2001-   | 4001-   | 6001-  |       |
|         | 4000    | 6000    | 8000   |       |
+---------+---------+---------+--------+-------+
```

In this diagram, the large table is divided into multiple parts. Part 1 contains rows 1 to 2000, Part 2 holds rows 2001 to 4000, and so on. This approach allows the database to target specific partitions during queries, reducing the amount of data it needs to process.

### Purpose of Partitioning

The main goal of partitioning is to optimize database performance and enhance manageability, especially for large tables. By dividing a table into smaller partitions, queries can execute more efficiently because they only need to access the relevant partitions. This reduces query response times and improves overall system performance.

Partitioning also simplifies maintenance tasks. For example, if you need to archive data from a certain time period, you can easily identify and handle the specific partition without affecting the rest of the table. This makes tasks like backups, archiving, and purging more straightforward and less disruptive.

### Types of Partitioning

There are several partitioning methods, each suited to different types of data and query patterns. Let's explore some of the most common partitioning strategies.

#### Range Partitioning

Range partitioning splits a table based on a range of values in a particular column. This method is ideal for time-based data or continuous numerical data. For instance, you might partition sales data by date or customer data by age groups.

Consider the following employee table:

| ID  | Name  | Department | Hire Date  |
|-----|-------|------------|------------|
| 1   | Alice | HR         | 2020-01-15 |
| 2   | Bob   | IT         | 2021-03-22 |
| 3   | Carol | HR         | 2019-06-30 |
| 4   | David | IT         | 2020-11-01 |
| 5   | Eve   | Finance    | 2021-07-14 |
| 6   | Frank | HR         | 2018-12-12 |
| 7   | Grace | IT         | 2021-05-05 |
| 8   | Heidi | Finance    | 2020-08-23 |
| 9   | Ivan  | HR         | 2019-10-10 |
| 10  | Judy  | IT         | 2020-02-28 |

Using range partitioning on the "Hire Date" column, we can divide this table into partitions based on the year employees were hired.

**Partition 1: Hire Dates Before 2020**

| ID | Name  | Department | Hire Date  |
|----|-------|------------|------------|
| 3  | Carol | HR         | 2019-06-30 |
| 6  | Frank | HR         | 2018-12-12 |
| 9  | Ivan  | HR         | 2019-10-10 |

**Partition 2: Hire Dates in 2020**

| ID  | Name  | Department | Hire Date  |
|-----|-------|------------|------------|
| 1   | Alice | HR         | 2020-01-15 |
| 4   | David | IT         | 2020-11-01 |
| 8   | Heidi | Finance    | 2020-08-23 |
| 10  | Judy  | IT         | 2020-02-28 |

**Partition 3: Hire Dates After 2020**

| ID | Name  | Department | Hire Date  |
|----|-------|------------|------------|
| 2  | Bob   | IT         | 2021-03-22 |
| 5  | Eve   | Finance    | 2021-07-14 |
| 7  | Grace | IT         | 2021-05-05 |

With this setup, queries targeting employees hired in a specific year can quickly access the relevant partition, improving query performance.

#### List Partitioning

List partitioning divides a table based on a predefined list of values in a column. It's suitable for categorical data, such as departments or regions.

Using the same employee table, we can partition it based on the "Department" column.

**Partition 1: HR Department**

| ID | Name  | Department | Hire Date  |
|----|-------|------------|------------|
| 1  | Alice | HR         | 2020-01-15 |
| 3  | Carol | HR         | 2019-06-30 |
| 6  | Frank | HR         | 2018-12-12 |
| 9  | Ivan  | HR         | 2019-10-10 |

**Partition 2: IT Department**

| ID | Name  | Department | Hire Date  |
|----|-------|------------|------------|
| 2  | Bob   | IT         | 2021-03-22 |
| 4  | David | IT         | 2020-11-01 |
| 7  | Grace | IT         | 2021-05-05 |
| 10 | Judy  | IT         | 2020-02-28 |

**Partition 3: Finance Department**

| ID | Name  | Department | Hire Date  |
|----|-------|------------|------------|
| 5  | Eve   | Finance    | 2021-07-14 |
| 8  | Heidi | Finance    | 2020-08-23 |

List partitioning allows queries that target a specific department to access only the relevant partition, reducing query execution time.

#### Hash Partitioning

Hash partitioning uses a hash function on a column to distribute rows evenly across partitions. This method is useful when there's no clear range or list partitioning criteria and helps balance the data load.

Suppose we apply a hash function to the "ID" column using modulus 3 (hash(ID) mod 3). This will assign each row to one of three partitions.

**Partition 1: hash(ID) mod 3 = 1**

| ID  | Name  | Department | Hire Date  |
|-----|-------|------------|------------|
| 1   | Alice | HR         | 2020-01-15 |
| 4   | David | IT         | 2020-11-01 |
| 7   | Grace | IT         | 2021-05-05 |
| 10  | Judy  | IT         | 2020-02-28 |

**Partition 2: hash(ID) mod 3 = 2**

| ID | Name  | Department | Hire Date  |
|----|-------|------------|------------|
| 2  | Bob   | IT         | 2021-03-22 |
| 5  | Eve   | Finance    | 2021-07-14 |
| 8  | Heidi | Finance    | 2020-08-23 |

**Partition 3: hash(ID) mod 3 = 0**

| ID | Name  | Department | Hire Date  |
|----|-------|------------|------------|
| 3  | Carol | HR         | 2019-06-30 |
| 6  | Frank | HR         | 2018-12-12 |
| 9  | Ivan  | HR         | 2019-10-10 |

Hash partitioning ensures that data is evenly distributed, which can improve performance for queries that access data randomly.

#### Key Partitioning

Key partitioning is similar to hash partitioning but specifically uses the primary key columns for the hash function. This method is effective when queries frequently access data based on primary keys.

Using the employee table, we can partition it based on ranges of the "ID" primary key.

**Partition 1: IDs 1-3**

| ID  | Name  | Department | Hire Date  |
|-----|-------|------------|------------|
| 1   | Alice | HR         | 2020-01-15 |
| 2   | Bob   | IT         | 2021-03-22 |
| 3   | Carol | HR         | 2019-06-30 |

**Partition 2: IDs 4-6**

| ID  | Name  | Department | Hire Date  |
|-----|-------|------------|------------|
| 4   | David | IT         | 2020-11-01 |
| 5   | Eve   | Finance    | 2021-07-14 |
| 6   | Frank | HR         | 2018-12-12 |

**Partition 3: IDs 7-10**

| ID  | Name  | Department | Hire Date  |
|-----|-------|------------|------------|
| 7   | Grace | IT         | 2021-05-05 |
| 8   | Heidi | Finance    | 2020-08-23 |
| 9   | Ivan  | HR         | 2019-10-10 |
| 10  | Judy  | IT         | 2020-02-28 |

Key partitioning can improve performance for queries that target specific ranges of primary keys.

#### Composite Partitioning

Composite partitioning combines two or more partitioning methods, such as range-hash or range-list partitioning. This approach is suitable for complex data and query requirements, allowing for more granular data management and performance optimization.

For example, a table might first be range-partitioned by date and then hash-partitioned within each date range partition. This method provides the benefits of both partitioning strategies, catering to specific query patterns and data distribution needs.

### Best Practices for Partitioning

To make the most of partitioning, it's important to consider your data characteristics and query patterns.

- Choose a partitioning method that aligns with your data and how it's accessed. For time-series data, range partitioning by date might be most effective. For data without a natural partitioning key, hash partitioning could be more suitable.
- Regularly review your partitioning scheme to ensure it continues to meet performance goals. As data grows and access patterns change, you may need to adjust partitions or redistribute data.
- Design queries to take advantage of partition pruning, where the database engine skips irrelevant partitions. This can significantly improve query performance by reducing the amount of data scanned.
- Periodically reorganize or rebuild partitions as part of routine maintenance. This helps optimize storage and can improve performance, especially if partitions become unbalanced over time.
