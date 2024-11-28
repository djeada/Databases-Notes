## Understanding the Storage of Tables and Indexes on Disk

Exploring how databases store tables and indexes on disk can provide valuable insights into optimizing performance and managing data efficiently. Let's delve into the fundamental concepts of disk storage in relational databases, focusing on the structures and mechanisms that underlie data organization.

### Storage Structures

Databases organize data on disk using structured approaches to ensure efficient access and manipulation.

#### Pages and Extents

At the core of data storage are pages, sometimes called blocks. These are fixed-size chunks of data, commonly 4KB, 8KB, or 16KB in size, depending on the database system. Pages serve as the basic units for reading from and writing to the disk.

To manage storage more effectively, pages are grouped into extents. An extent is a collection of contiguous pages, which helps reduce fragmentation and improves read/write performance by allowing larger chunks of data to be processed in a single operation.

Here's a simple illustration of pages grouped into extents:

```
+-------------------+
|      Extent       |
| +-----+  +-----+  |
| |Page1|  |Page2|  |
| +-----+  +-----+  |
| +-----+  +-----+  |
| |Page3|  |Page4|  |
| +-----+  +-----+  |
+-------------------+
```

In this diagram, we see an extent containing four pages, each holding part of the table's data.

#### Table Storage Models

Tables are stored on disk as collections of pages, but the way data is organized within these pages can vary.

- **Row-Oriented Storage**: This traditional model stores entire rows together within a page. It's efficient for transactional databases where queries often need all columns of a row. For example, customer records in a sales database would be stored with all their associated fields in the same row.

- **Column-Oriented Storage**: In this model, data is stored by columns, with each page containing data from a single column across multiple rows. This approach is beneficial for analytical databases where queries may focus on specific columns across many rows. For instance, calculating the average sales amount would only require reading the sales amount column.

Here's how a page might look in a row-oriented storage:

```
+-----------------------------------+
| Row1: [Col1, Col2, Col3, Col4]    |
| Row2: [Col1, Col2, Col3, Col4]    |
| Row3: [Col1, Col2, Col3, Col4]    |
+-----------------------------------+
```

And in a column-oriented storage:

```
+--------------------+
| Column1 Data       |
| [Value1, Value2,   |
|  Value3, ...]      |
+--------------------+
```

#### Indexes

Indexes are data structures that improve the speed of data retrieval operations on a database table. They are essential for efficient querying, especially in large databases.

Different types of indexes include:

- **B-Tree Indexes** are widely used due to their balanced tree structure, which supports efficient searches, insertions, and deletions, making them suitable for a variety of query types, including range queries.
- **Hash Indexes** rely on a hash function to map keys to specific locations, offering high efficiency for equality searches but lacking support for range queries.
- **Bitmap Indexes** use bitmaps to represent data, making them effective for columns with low cardinality (few distinct values), and they are commonly employed in data warehousing for complex analytical queries.

A simplified illustration of a B-tree index might look like this:

```
        [50]
       /    \
    [25]    [75]
   /   \    /   \
[10] [30][60] [90]
```

Each node in the tree represents a page, and the structure allows for quick navigation to the desired data.

### Implications for Performance

Understanding how tables and indexes are stored can have significant implications for database performance and optimization strategies.

#### Data Locality

Storing related data close together on disk improves data locality, which enhances performance by reducing the number of disk I/O operations required to retrieve data.

For example, when a query requests several rows that are stored sequentially on the same page or extent, the database can read them all in a single disk operation, speeding up the retrieval process.

#### Choosing the Right Storage Model

Selecting between row-oriented and column-oriented storage depends on the workload and query patterns.

- **Row-Oriented Storage** organizes data by rows, making it optimal for transactional workloads where operations require accessing entire rows, such as inserting or updating customer orders.
- **Column-Oriented Storage** organizes data by columns, making it suitable for analytical workloads that perform operations like aggregations on specific columns over large datasets, such as generating sales trend reports.

#### Effective Indexing Strategies

Indexes improve query performance by allowing the database to locate data without scanning every row in a table. However, they also consume disk space and can slow down write operations because the index must be updated whenever data is modified.

Balancing the number and types of indexes is crucial. Over-indexing can lead to unnecessary overhead, while under-indexing can result in slow query performance.

### Practical Examples and Commands

In systems like PostgreSQL, you can inspect and manage storage aspects using specific commands.

To check the size of a table and its indexes:

```sql
SELECT
  pg_size_pretty(pg_relation_size('your_table')) AS table_size,
  pg_size_pretty(pg_indexes_size('your_table')) AS indexes_size,
  pg_size_pretty(pg_total_relation_size('your_table')) AS total_size;
```

This command returns the sizes in a human-readable format.

Example output:

| table_size | indexes_size | total_size |
|------------|--------------|------------|
| 120 MB     | 30 MB        | 150 MB     |

Interpreting the results:

- **table_size** refers to the amount of disk space allocated specifically for storing the table's raw data.
- **indexes_size** represents the total disk space used by all indexes associated with the table, which facilitate faster query operations.
- **total_size** is the sum of the table's data size and the space consumed by its indexes, indicating the overall storage footprint of the table.
