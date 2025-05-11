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

### Example Table: Historical Stock Prices

Suppose you store daily OHLC (Open-High-Low-Close) data for multiple tickers. As years of data accumulate, full-table scans slow down analytics and archiving. Partitioning by date (e.g. by year or month) keeps each chunk manageable.

#### Create the Partitioned Table

We’ll partition by **RANGE** on the integer expression `YEAR(trade_date)`, one partition per calendar year plus a catch-all for the future.

```sql
DROP TABLE IF EXISTS stock_prices;
CREATE TABLE stock_prices (
  id            BIGINT AUTO_INCREMENT PRIMARY KEY,
  ticker        VARCHAR(10)   NOT NULL,
  trade_date    DATE          NOT NULL,
  open_price    DECIMAL(10,4),
  high_price    DECIMAL(10,4),
  low_price     DECIMAL(10,4),
  close_price   DECIMAL(10,4),
  volume        BIGINT
)
PARTITION BY RANGE ( YEAR(trade_date) ) (
  PARTITION p2018 VALUES LESS THAN (2019),
  PARTITION p2019 VALUES LESS THAN (2020),
  PARTITION p2020 VALUES LESS THAN (2021),
  PARTITION p2021 VALUES LESS THAN (2022),
  PARTITION p2022 VALUES LESS THAN (2023),
  PARTITION p2023 VALUES LESS THAN (2024),
  PARTITION p2024 VALUES LESS THAN (2025),
  PARTITION p_future VALUES LESS THAN MAXVALUE
);
```

* **Partition key**: `YEAR(trade_date)` must appear in every UNIQUE/PRIMARY index (it’s in the PK).
* **Partitions**: p2018…p2024 cover past years; **p\_future** for 2025 onward.

#### SHOW CREATE TABLE

```sql
SHOW CREATE TABLE stock_prices\G
```

Confirms your `PARTITION BY RANGE` clause.

#### INFORMATION\_SCHEMA.PARTITIONS

```sql
SELECT
  PARTITION_NAME,
  PARTITION_METHOD,
  PARTITION_EXPRESSION,
  PARTITION_DESCRIPTION
FROM INFORMATION_SCHEMA.PARTITIONS
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME = 'stock_prices';
```

| PARTITION\_NAME | METHOD | EXPRESSION         | DESCRIPTION |
| --------------- | ------ | ------------------ | ----------- |
| p2018           | RANGE  | YEAR(`trade_date`) | 2019        |
| …               | …      | …                  | …           |
| p\_future       | RANGE  | YEAR(`trade_date`) | MAXVALUE    |

#### Querying with Partition Pruning

Partition pruning means MariaDB only reads partitions relevant to your filter.

```sql
EXPLAIN PARTITIONS
SELECT ticker, close_price
FROM stock_prices
WHERE trade_date BETWEEN '2022-01-01' AND '2022-12-31'
  AND ticker = 'AAPL';
```

In the `EXPLAIN` output you’ll see `partitions: p2022`—only that partition is scanned, then the `ticker='AAPL'` filter applies within it.

#### Adding Next Year’s Partition

At the start of 2025:

```sql
ALTER TABLE stock_prices
  REORGANIZE PARTITION p_future INTO (
    PARTITION p2025 VALUES LESS THAN (2026),
    PARTITION p_future VALUES LESS THAN MAXVALUE
  );
```

This splits `p_future` into `p2025` and an updated catch-all.

#### Dropping an Out-of-Scope Year

To remove data before 2018 in one instant operation:

```sql
ALTER TABLE stock_prices
  DROP PARTITION p2018;
```

Dropping the partition deletes all its rows without row-by-row deletes—very fast.

#### Automating with EVENTS

You can schedule two MariaDB EVENTS:

1. **Add new year’s partition** on January 1st each year.
2. **Drop partitions older than N years** (e.g. keep only the last 7 years).

```sql
-- 1. Add partition
CREATE EVENT ev_add_stock_year
ON SCHEDULE EVERY 1 YEAR
  STARTS '2025-01-01 00:00:00'
DO
  ALTER TABLE stock_prices
    REORGANIZE PARTITION p_future INTO (
      PARTITION p{YEAR(CURDATE())} VALUES LESS THAN (YEAR(CURDATE())+1),
      PARTITION p_future VALUES LESS THAN MAXVALUE
    );

-- 2. Drop old partitions
CREATE EVENT ev_drop_old_stock
ON SCHEDULE EVERY 1 YEAR
  STARTS '2025-01-01 01:00:00'
DO
  SET @cutoff := YEAR(CURDATE()) - 7;
  -- dynamic SQL: drop each partition pYYYY where YYYY <= @cutoff
  -- implement via prepared statements or stored procedure
  CALL drop_old_stock_partitions(@cutoff);
```

#### Effects on “Normal” Queries

* **No query syntax change**: You still `SELECT * FROM stock_prices WHERE …`.
* Date‐range filters only scan relevant partitions.
* Secondary indexes (e.g. on `ticker`) are local to each partition.
* **Fast maintenance**: Archiving or deleting old data is a single `DROP PARTITION`.

### Best Practices for Partitioning

To make the most of partitioning, it's important to consider your data characteristics and query patterns.

- Choose a partitioning method that aligns with your data and how it's accessed. For time-series data, range partitioning by date might be most effective. For data without a natural partitioning key, hash partitioning could be more suitable.
- Regularly review your partitioning scheme to ensure it continues to meet performance goals. As data grows and access patterns change, you may need to adjust partitions or redistribute data.
- Design queries to take advantage of partition pruning, where the database engine skips irrelevant partitions. This can significantly improve query performance by reducing the amount of data scanned.
- Periodically reorganize or rebuild partitions as part of routine maintenance. This helps optimize storage and can improve performance, especially if partitions become unbalanced over time.
* **Include partitioning key in all UNIQUE/PK** definitions.
* **Avoid non-deterministic functions** on the partition key in WHERE clauses.
* **Balance partition size**: If a year’s data grows too large, consider monthly partitions:

  ```sql
  PARTITION BY RANGE (TO_DAYS(trade_date)) (
    PARTITION p2024_01 VALUES LESS THAN (TO_DAYS('2024-02-01')),
    PARTITION p2024_02 VALUES LESS THAN (TO_DAYS('2024-03-01')),
    … 
  );
  ```
* **Test EXPLAIN PARTITIONS** whenever you add new filters to ensure pruning works.
