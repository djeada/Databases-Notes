# Partitioning

Partitioning splits one logical table into smaller physical pieces according to a declared key. **Partition pruning** can reduce query work when the filter identifies relevant pieces; it is not automatic for every query and does not replace suitable indexes. Partition management can also make retention and bulk removal simpler, subject to engine-specific locking, storage, and backup behavior.

## What do we mean by Partitioning?

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

## Purpose of Partitioning

The main goal of partitioning is to optimize database performance and enhance manageability, especially for large tables. By dividing a table into smaller partitions, queries can execute more efficiently because they only need to access the relevant partitions. This reduces query response times and improves overall system performance.

Partitioning also simplifies maintenance tasks. For example, if you need to archive data from a certain time period, you can easily identify and handle the specific partition without affecting the rest of the table. This makes tasks like backups, archiving, and purging more straightforward and less disruptive.

## Types of Partitioning

There are several partitioning methods, each suited to different types of data and query patterns. Let's explore some of the most common partitioning strategies.

### Range Partitioning

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

### List Partitioning

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

### Hash Partitioning

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

### Key Partitioning

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

### Composite Partitioning

Composite partitioning combines two or more partitioning methods, such as range-hash or range-list partitioning. This approach is suitable for complex data and query requirements, allowing for more granular data management and performance optimization.

For example, a table might first be range-partitioned by date and then hash-partitioned within each date range partition. This method provides the benefits of both partitioning strategies, catering to specific query patterns and data distribution needs.

## Example Table: Historical Stock Prices

When managing large volumes of time-series financial data, partitioning can dramatically improve query performance and maintenance operations. The following example targets **MySQL 8.x** and stores daily OHLC (Open-High-Low-Close) prices by year. MariaDB has related but not identical partitioning and event behavior; test its syntax separately.

### Create the Partitioned Table

Begin by defining your main table schema and specifying a partitioning strategy. Here we use **RANGE** partitioning on the integer expression `YEAR(trade_date)`, creating one partition per calendar year plus a catch-all for future dates.

```sql
DROP TABLE IF EXISTS stock_prices;
CREATE TABLE stock_prices (
  id            BIGINT NOT NULL AUTO_INCREMENT,
  ticker        VARCHAR(10)   NOT NULL,
  trade_date    DATE          NOT NULL,
  open_price    DECIMAL(10,4),
  high_price    DECIMAL(10,4),
  low_price     DECIMAL(10,4),
  close_price   DECIMAL(10,4),
  volume        BIGINT,
  PRIMARY KEY (id, trade_date)
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

* **Primary-key rule:** MySQL requires every `PRIMARY KEY` and `UNIQUE` key on a partitioned table to contain all columns referenced by the partition expression. Because the expression uses `trade_date`, `PRIMARY KEY (id)` would make this `CREATE TABLE` fail; `PRIMARY KEY (id, trade_date)` satisfies the rule while keeping `id` first for `AUTO_INCREMENT`. This means `id` alone is **not** guaranteed globally unique by this table's declared primary key.
* **Partitions:** p2018…p2024 cover past years; p_future holds dates from 2025 onward, and earlier dates fall into the first partition. Add a lower-bound strategy or validation if pre-2018 data must be rejected.
* **Reference:** [MySQL partitioning keys and unique keys](https://dev.mysql.com/doc/refman/8.4/en/partitioning-limitations-partitioning-keys-unique-keys.html).

### SHOW CREATE TABLE

After creating the table, verify that the partitioning clause is in place by inspecting the full DDL. This ensures your partition definitions are correctly applied.

```sql
SHOW CREATE TABLE stock_prices\G
```

### INFORMATION_SCHEMA.PARTITIONS

MySQL exposes partition metadata in `INFORMATION_SCHEMA.PARTITIONS`. Querying this view lets you confirm partition names, methods, expressions, and boundary values.

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

| PARTITION_NAME | METHOD | EXPRESSION         | DESCRIPTION |
| --------------- | ------ | ------------------ | ----------- |
| p2018           | RANGE  | YEAR(`trade_date`) | 2019        |
| …               | …      | …                  | …           |
| p_future       | RANGE  | YEAR(`trade_date`) | MAXVALUE    |

### Querying with Partition Pruning

Partition pruning tells the optimizer to scan only relevant partitions based on the `WHERE` clause. This avoids full-table scans and speeds up queries dramatically for time-restricted filters.

```sql
EXPLAIN
SELECT ticker, close_price
FROM stock_prices
WHERE trade_date BETWEEN '2022-01-01' AND '2022-12-31'
  AND ticker = 'AAPL';
```

Inspect the `partitions` field in MySQL's `EXPLAIN` result to see which partitions are considered. The optimizer can prune to `p2022` for this date range, but **check the actual plan** instead of assuming the partitioning key forces pruning in every SQL expression. The ticker predicate still needs its own useful access path if that lookup is selective.

### Adding Next Year’s Partition

As the calendar rolls over, you need to split the catch-all partition to include a new yearly partition and maintain the future placeholder. Execute this once at the start of each year.

```sql
ALTER TABLE stock_prices
  REORGANIZE PARTITION p_future INTO (
    PARTITION p2025 VALUES LESS THAN (2026),
    PARTITION p_future VALUES LESS THAN MAXVALUE
  );
```

### Dropping an Out-of-Scope Year

To remove historical data in bulk (e.g., before 2018), drop the corresponding partition. This can remove many rows without issuing individual `DELETE` statements, but it can still require metadata locks, storage work, and a retention/backup decision. Do not describe it as universally instantaneous.

```sql
ALTER TABLE stock_prices
  DROP PARTITION p2018;
```

### Automate partition maintenance without fake static DDL

The yearly `ALTER TABLE` shown above names a literal partition and boundary. It cannot be turned into valid dynamic DDL merely by writing placeholders such as `p{YEAR(CURDATE())}` inside an event; that is **not valid MySQL partition syntax**. A similarly named `drop_old_stock_partitions()` procedure must exist before an event can call it.

For a real maintenance job, calculate the next boundary and partition name in application or stored-procedure code, quote and validate the identifier, construct the DDL, and run it through the engine's supported dynamic-SQL mechanism. Schedule it *ahead* of the first insert into the new year; check existing partitions, monitor locks and failures, and test it in staging. Deleting old partitions must follow explicit retention and backup policy. The static `REORGANIZE PARTITION` example above is the **runnable exercise**; no unimplemented event template is presented as executable SQL.

### Effects on “Normal” Queries

* **No query syntax change**: You still `SELECT * FROM stock_prices WHERE …`.
* Date-range filters **may** prune partitions when the optimizer can infer the partition-key range; verify the plan.
* Secondary indexes (e.g. on `ticker`) are local to each partition.
* **Retention maintenance**: Dropping old partitions can avoid row-by-row deletes, but still requires operational planning.

## Best Practices for Partitioning

To make the most of partitioning, it's important to consider your data characteristics and query patterns.

* Choose a partitioning strategy that fits your data and access patterns (e.g., range-by-date for time-series, hash for unkeyed data).
* Include the partitioning key in all PRIMARY KEY and UNIQUE constraints.
* Avoid non-deterministic functions on the partition key in WHERE clauses to enable pruning.
* Write queries to leverage partition pruning so the engine skips irrelevant partitions.
* Verify pruning with MySQL `EXPLAIN` and its `partitions` field whenever you introduce new filters.
* Monitor your partitioning scheme and adjust or redistribute partitions as data volume and access patterns evolve.
* Reorganize partitions when measurements or retention boundaries justify it; rebuilding everything periodically is not a universal requirement.
* Balance partition sizes—if annual data becomes too large, switch to monthly ranges, for example:

For a **different, new table**, MySQL can range-partition directly by dates with `RANGE COLUMNS(trade_date)`; its unique keys must still include `trade_date`:

```sql
PARTITION BY RANGE COLUMNS (trade_date) (
  PARTITION p_before_2024 VALUES LESS THAN ('2024-01-01'),
  PARTITION p2024_01 VALUES LESS THAN ('2024-02-01'),
  PARTITION p2024_02 VALUES LESS THAN ('2024-03-01'),
  PARTITION p_future VALUES LESS THAN (MAXVALUE)
);
```

## Review questions

1. What is partitioning and how does it enhance database performance and manageability?
2. What are the different types of partitioning methods and in what scenarios are they most effectively used?
3. How does range partitioning work, and what are its advantages and potential drawbacks?
4. What best practices should be followed to optimize the use of partitioning in a database environment?
5. How do composite partitioning strategies combine multiple partitioning methods, and what benefits do they offer?
