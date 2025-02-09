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

- A table is stored in files composed of fixed-size units known as **pages**, which serve as the fundamental building blocks for simplifying **I/O operations** by standardizing data access and storage.  
- Each **row** of data is stored within these disk pages, typically packed tightly end-to-end to maximize storage efficiency. However, gaps can occur due to **fragmentation**, which can degrade performance over time.  
- Many databases define a **page** as their basic unit of storage, with typical sizes of 8KB in PostgreSQL and 16KB in MySQL, though this can often be configured to suit specific workload requirements or **storage hardware**.  
- The database performs all data **reads and writes** at the page level instead of accessing individual bytes or rows, enabling more efficient interaction with storage systems.  
- When the database fetches **data** from disk, it must load the entire page into memory, even if the query requires only a small portion of the data on that page, which can lead to inefficiencies if **data locality** is poor.  
- **Disk I/O performance** is heavily influenced by how efficiently the database can access pages, often relying on caching frequently accessed pages in memory to minimize the need for repeated disk reads.  
- **Data locality**, where rows frequently accessed together are stored on adjacent pages, helps reduce the number of pages the database must read for common queries, improving performance.  
- Allocating pages in **contiguous blocks**, often grouped into larger units called extents, improves the efficiency of sequential scans by reducing the number of separate I/O operations needed to access large datasets.  
- Aligning **page size** with the underlying storage device’s block size or performance characteristics can reduce unnecessary fragmentation, minimize overhead, and improve overall I/O efficiency.  
- When a single **row** of data is scattered across multiple pages, the database must perform additional I/O operations to retrieve the data, slowing down queries that would otherwise benefit from quick lookups.  
- Storage devices often operate on **fixed-size blocks**; matching the database’s page size to the block size can avoid partial block reads or writes, which waste resources and degrade performance.  
- Reorganizing or **vacuuming tables** helps reclaim freed space within pages, making it available for future inserts and improving the database’s ability to store data compactly and efficiently.  

### Table and Heap Organization

- Tables without **clustered ordering** store rows in a heap-like structure where rows are appended as new inserts occur, without maintaining any particular logical order.  
- The heap does not enforce a logical order, so retrieving specific **rows** without the use of indexes often requires scanning multiple pages sequentially, which can be inefficient for large datasets.  
- A heap can become **sparse** if many rows are deleted, leaving gaps and unused space on pages. This empty space can be reused by future inserts, but excessive sparsity may require maintenance to optimize storage.  
- Heap scans involve reading all the **pages** of a table sequentially from start to end, which can be slow for large tables if queries lack selective conditions to filter rows early.  
- Physical **row identifiers** (such as TIDs in PostgreSQL) directly point to a specific page and item offset, enabling the database to quickly locate and access particular rows without additional lookups.  
- The database engine tracks **free space** on each page using internal structures, helping it efficiently determine where to place new rows without unnecessarily extending the heap or wasting storage.  
- High **update frequency** on variable-length columns can lead to row movement or page splits, which increase fragmentation and can degrade performance if left unchecked over time.  
- **Compressing data** within each page allows more rows to fit into memory or storage, improving data density and reducing I/O, but at the cost of additional CPU overhead during compression and decompression processes.  
- Dedicated **space management structures**, sometimes in the form of metadata pages, monitor how full each page is, guiding the database in selecting optimal locations for inserting new rows and minimizing fragmentation.  
- **Row headers**, stored alongside user data, occupy part of the available space on each page. This overhead can reduce the capacity available for actual row data, especially for tables with many small rows.  
- When a single **row** is too large to fit into one page, the database may split it into multiple segments, linked together with pointers. While this enables storage of large rows, it increases the cost of accessing them due to the need for multiple I/O operations.  
- **Heap fragmentation** can be reduced through periodic maintenance operations, such as table vacuuming or reorganization, which compact data and ensure higher density of rows within pages, improving query performance.  

```
+----------------------------------------------------+
|                       Heap File                    |
+----------------------------------------------------+
|  Page 1         |  Page 2         |  Page 3        |
+------------------+-----------------+---------------+
| [Row1] [Row2]   | [Row3] [Row4]   | [Row5] [Row6]  |
| [Free Space]    | [Row7]          | [Free Space]   |
+------------------+-----------------+---------------+
```

- Pages are fixed-size units of storage, containing rows and free space.
- Rows (e.g., Row1, Row2) are stored in the order of insertion unless affected by updates or deletes.

**Scenario: Fragmentation caused by deletions**

```
+----------------------------------------------------+
|                       Heap File                    |
+----------------------------------------------------+
|  Page 1         |  Page 2         |  Page 3        |
+------------------+-----------------+---------------+
| [Row1] [Deleted]| [Row4] [Deleted]| [Row6] [Row7]  |
| [Free Space]    | [Free Space]    | [Free Space]   |
+------------------+-----------------+---------------+
```

Deletions leave gaps in pages, creating free space that can be reused.

**Scenario: Large row spanning multiple pages**

```
+----------------------------------------------------+
|                       Heap File                    |
+----------------------------------------------------+
|  Page 1         |  Page 2         |  Page 3        |
+------------------+-----------------+---------------+
| [Row1] [Row2]   | [Part of Row8]  | [Part of Row8] |
| [Free Space]    | [Free Space]    | [Free Space]   |
+------------------+-----------------+---------------+
```

A large row (Row8) is split across multiple pages, linked by pointers.

**Scenario: Post-maintenance compacted heap**

```
+----------------------------------------------------+
|                       Heap File                    |
+----------------------------------------------------+
|  Page 1         |  Page 2         |  Page 3        |
+------------------+-----------------+---------------+
| [Row1] [Row2]   | [Row4] [Row6]   | [Row7]         |
| [Free Space]    | [Free Space]    | [Free Space]   |
+------------------+-----------------+---------------+
```

Periodic maintenance (e.g., VACUUM) reorganizes rows to reclaim space and reduce fragmentation.

#### Table Storage Models

Tables are stored on disk as collections of pages, but the way data is organized within these pages can vary.

- **Row-Oriented Storage** organizes data by storing entire **rows** together within a single **page**, making it efficient for **transactional databases** where queries often require access to all columns of a **row**. For example, customer records in a **sales database** would store all associated fields in the same row for fast retrieval.  
- **Column-Oriented Storage** arranges data by storing each **column** separately across multiple **rows**, making it advantageous for **analytical databases** where queries target specific **columns** across many rows. For instance, calculating the **average sales amount** would only involve reading data from the **sales amount column**, reducing unnecessary reads.

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

- Indexes are important on-disk structures that optimize database query performance by directing queries to the appropriate pages without scanning the entire heap.
- They come in various types, each suited to different query patterns and data characteristics.

```
+-----------------+
|    Query        |
+--------+--------+
         |
         v
+--------+--------+
|    Index Pages  |
+--------+--------+
         |
         v
+--------+--------+
|   Heap Pages    |
+-----------------+
```

**B-Tree Indexes**

- B-tree indexes have a balanced tree structure, supporting efficient searches, insertions, and deletions with logarithmic lookup time by navigating through a hierarchy of 
- Suitable for a variety of query types, including range queries.
  
```
Tree:
        (root page)
       /          \
   (index page)  (index page)
   /       \        /      \
(data)   (data)  (data)  (data)
```

**Hash Indexes**

- Use a hash function to map keys to specific hash buckets, offering high efficiency for equality searches.
- Do not support range queries or sorting of rows across different pages.

```
[Diagram: Hash Index Mapping]
Key1 --> Bucket A
Key2 --> Bucket B
Key3 --> Bucket A
```

**Bitmap Indexes**

- Represent data using bitmaps, effective for columns with low cardinality (few distinct values).
- Commonly employed in data warehousing for complex analytical queries, as they can compactly represent row sets and quickly combine multiple conditions, reducing unnecessary page reads.

```
[Diagram: Bitmap Index Example]
Value1: 101010
Value2: 110011
Value3: 100101
```

**Non-Clustered Indexes**

- Store key values along with references (pointers) to heap rows.
- Allow quick lookups of pages even if the heap is not sorted.
- Queries navigate through index pages to find pointers to heap pages containing matching rows.

```
[Diagram: Non-Clustered Index]
+------------+       +------------+
| Index Page | ----> | Heap Page  |
+------------+       +------------+
```

**Clustered Indexes**

- Physically order the table heap based on the index key, placing related rows close together on pages.
- Improves the performance of range queries and ensures related data is stored contiguously.
- Using random primary keys can scatter inserts across many pages, potentially degrading write performance.
- Row updates that increase size may require moving the row to a different page, necessitating pointer adjustments.

**Partial Indexes**

- Store index entries only for specific rows that meet certain conditions.
- Reduce the number of index pages used and improve performance for specialized queries.

```
+--------------+
| Condition    |
+--------------+
| Indexed Rows |
+--------------+
```

**Covering Indexes**

- Include all the necessary columns for a query within the index itself.
- Allow the query to retrieve data directly from the index, avoiding access to heap pages and reducing disk I/O.

```
+------------+
| Key + Data |
+------------+
```

**Index-Only Scans**

- Utilize indexes that contain all the requested data.
- Enable queries to bypass heap pages, further reducing disk I/O and improving performance.

**Free Space Maps**

- Some databases maintain a map of free space across pages.
- Quickly identify where new rows can be inserted, optimizing storage utilization.

```
+------------+------------+------------+
| Page 1     | Page 2     | Page 3     |
| Free Space | Used Space | Free Space |
+------------+------------+------------+
```

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

Managing and optimizing database storage is crucial for maintaining performance and ensuring efficient use of resources. Below are practical commands for PostgreSQL and MySQL that help inspect and manage storage aspects. Each command includes its purpose, when to use it, expected output, and how to interpret the results.

#### **PostgreSQL Commands**

I. **Check Table and Index Sizes**

- Retrieves the size of a specific table, its indexes, and the total combined size in a human-readable format.
- Use when you need to understand the storage footprint of a table and its indexes to manage disk space or optimize performance.

```sql
SELECT
 pg_size_pretty(pg_relation_size('your_table')) AS table_size,
 pg_size_pretty(pg_indexes_size('your_table')) AS indexes_size,
 pg_size_pretty(pg_total_relation_size('your_table')) AS total_size;
```

**Expected Output:**

| table_size | indexes_size | total_size |
|------------|--------------|------------|
| 120 MB     | 30 MB        | 150 MB     |

- **table_size:** Disk space used by the table's raw data.
- **indexes_size:** Disk space used by all indexes associated with the table.
- **total_size:** Combined disk space of the table and its indexes, indicating the overall storage footprint.

II. **Analyze Query Execution with Buffer Usage**

- Provides detailed execution plans for a query, including the number of disk pages read from memory and disk.
- Use when diagnosing query performance issues to understand how much data is being read from different sources.

```sql
EXPLAIN (ANALYZE, BUFFERS) your_query;
```

**Expected Output:**

```
Seq Scan on your_table  (cost=0.00..431.00 rows=21000 width=...)
 Buffers: shared hit=123 read=45
 ...
```

- **shared hit:** Pages read from shared memory (cache).
- **read:** Pages read from disk.
- High disk reads may indicate the need for better indexing or increased memory allocation.

III. **Reclaim Dead Space with VACUUM**

- Cleans up dead rows and reclaims space for future inserts, optimizing storage usage.
- Regular maintenance to prevent table bloat and maintain optimal performance, especially after大量的INSERTs, UPDATEs, or DELETEs.

```sql
VACUUM your_table;
```

**Expected Output:**

```
VACUUM
```

Successful execution indicates that dead space has been reclaimed. Use `VACUUM VERBOSE your_table;` for detailed output.

IV. **Check Space Usage with pgstattuple**

- Provides detailed statistics about table space usage, including dead tuples and fragmentation.
- Use when assessing how much space is wasted due to dead rows and fragmentation, guiding maintenance actions like `VACUUM`.

```sql
SELECT * FROM pgstattuple('your_table');
```

**Expected Output:**

```
  table_len    |  1000000
  tuple_count  |   20000
  tuple_len    |    800000
  dead_tuple_count |  5000
  dead_tuple_len   |  200000
  free_space        |  0
```

- **dead_tuple_count & dead_tuple_len:** Amount of space occupied by obsolete rows.
- High values suggest the need for vacuuming to reclaim space.

V. **Enable Page-Level Checksums**

- Initializes a PostgreSQL database cluster with page-level checksums to detect data corruption.
- Use during database initialization to enhance data integrity by detecting corrupted pages.

```bash
initdb --data-checksums -D /path/to/data
```

**Expected Output:**

```
Data page checksums are enabled.
```

Ensures that any corrupted data pages are identified, enhancing reliability and data integrity.

VI. **Monitor I/O Statistics with pg_stat_io**

- Provides insights into the number of pages read and written for each query.
- Use when analyzing I/O performance to identify queries that cause excessive disk access.

```sql
SELECT * FROM pg_stat_io;
```

**Expected Output:**

```
query_id | read_pages | write_pages
---------|------------|------------
1        |     500    |     20
2        |    1500    |     50
```

- **read_pages:** Number of pages read from disk or memory.
- **write_pages:** Number of pages written to disk.
- High read/write counts may indicate inefficient queries or the need for indexing.

VII. **Optimize Memory Usage with shared_buffers**

- Sets the amount of memory allocated for PostgreSQL to cache data pages, reducing physical I/O.
- Use when performance tuning to allow more data to reside in memory, thus minimizing disk access.

```conf
shared_buffers = 2GB
```

- Increasing `shared_buffers` can improve performance by reducing disk reads.
- Balance is required to ensure sufficient memory for other system operations.

VIII. **Update Statistics with ANALYZE**

- Updates the statistics about the distribution of data in the table, aiding the query planner in choosing efficient execution paths.
- Use after significant data changes (INSERTs, UPDATEs, DELETEs) to ensure the query planner has accurate information.

```sql
ANALYZE your_table;
```

**Expected Output:**

```
ANALYZE
```

Successful execution means statistics are updated. Use `EXPLAIN` to see how updated statistics affect query plans.

IX. **Reorder Table Data with CLUSTER**

- Reorders the physical storage of a table based on an index, improving data locality for queries that use that index.
- Use when queries frequently access data in the order of a specific index, enhancing I/O performance.

```sql
CLUSTER your_table USING your_index;
```

**Expected Output:**

```
CLUSTER
```

The table is physically reordered, which can lead to faster sequential scans and better cache utilization for indexed queries.

#### **MySQL Commands**

I. **Show Table Status**

- Provides detailed information about a table, including the number of rows, data length, and index length.
- To assess table size, row count, and index usage for storage optimization and performance tuning.

```sql
SHOW TABLE STATUS LIKE 'your_table';
```

**Expected Output:**

| Name      | Engine | Version | Row_format | Rows  | Avg_row_length | Data_length | Max_data_length | Index_length | ... |
|-----------|--------|---------|------------|-------|----------------|-------------|-----------------|--------------|-----|
| your_table | InnoDB |      10 | Compact    | 20000 |            100 |   2000000   |        ...        |   500000     | ... |

- **Rows:** Number of records in the table.
- **Data_length:** Amount of space used for storing data.
- **Index_length:** Amount of space used for indexes.
- High `Data_length` or `Index_length` may indicate the need for optimization.

II. **Monitor InnoDB Buffer Pool Metrics**

Used to determine how effectively the buffer pool is caching data and to identify if more memory allocation is needed.

```sql
SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool_read_requests';
SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool_reads';
```

- **Innodb_buffer_pool_read_requests:** Number of logical read requests.
- **Innodb_buffer_pool_reads:** Number of reads that had to fetch data from disk.

**Expected Output:**

```
+---------------------------------+---------+
| Variable_name                   | Value   |
+---------------------------------+---------+
| Innodb_buffer_pool_read_requests | 100000 |
+---------------------------------+---------+

+--------------------------+-------+
| Variable_name            | Value |
+--------------------------+-------+
| Innodb_buffer_pool_reads | 500   |
+--------------------------+-------+
```

- **Ratio:** `Innodb_buffer_pool_reads / Innodb_buffer_pool_read_requests`
- A low ratio indicates most reads are served from memory. A high ratio suggests insufficient buffer pool size, leading to more disk I/O.

III. **Adjust Buffer Pool Size**

- Sets the size of the InnoDB buffer pool, which caches data and indexes in memory to reduce disk I/O
- Use during performance tuning to allocate more memory for caching, thereby improving read performance.

```conf
innodb_buffer_pool_size = 4G
```

- Increasing `innodb_buffer_pool_size` can reduce disk reads.
- Ensure the server has sufficient memory to accommodate the buffer pool alongside other processes.

### Other Considerations

- Some storage engines optimize **sequential scans** by prefetching pages of data into memory before they are needed. This approach takes advantage of the predictable access patterns in large analytical queries, reducing the number of individual I/O operations and significantly improving throughput for workloads that process data in sequence.  
- **Partitioning** large tables involves splitting the data into smaller, more manageable chunks that are stored across multiple files. Each partition manages its own set of blocks or pages, which allows the database to handle queries more efficiently by accessing only the relevant partitions. This can improve performance by minimizing unnecessary I/O and increasing the concurrency of queries accessing different partitions.  
- **Compression** techniques reduce the amount of storage required by encoding data in a more compact format. By fitting more rows into a single block, compression decreases disk usage and I/O operations. However, the tradeoff is increased CPU utilization, as the database needs to decompress data during reads and compress it again during writes. This balance is crucial in environments where both storage efficiency and processing power are important considerations.  
- Large **indexes** can grow so much that they span multiple blocks and levels within the database’s storage hierarchy. This can slow down lookup operations due to the increased number of I/O operations needed to navigate the index. Keeping index keys short and efficient reduces the overall depth of the index structure, leading to faster searches and lower storage overhead.  
- **Write-ahead logging (WAL)** is a mechanism that ensures data integrity by recording changes to a log file before applying them to the main data files. This approach provides crash recovery capabilities, as the log can be replayed to restore changes in the event of a failure. However, WAL requires additional storage and generates extra I/O, which can impact write performance.  
- **SSD storage** significantly enhances the speed of random data access compared to traditional HDDs. This makes certain indexing and layout strategies, such as those optimizing for random reads, more beneficial. For example, B-tree and hash indexes perform better on SSDs due to the hardware's ability to quickly retrieve scattered blocks of data.  
- The database engine tracks **dirty blocks** in memory—those that have been modified but not yet written back to disk. Periodically, the system flushes these blocks to disk to maintain data durability. This process can temporarily impact performance, especially if a large number of dirty blocks are written simultaneously or during peak system activity.  
- Performing **bulk inserts** can improve data ingestion performance by writing data in large, contiguous blocks rather than executing many small, random writes. This reduces fragmentation and the overhead associated with managing multiple small I/O operations, making bulk inserts an efficient choice for loading large datasets.  
- Monitoring **fragmentation** at the storage block level helps identify inefficiencies where data is scattered or stored in non-contiguous locations. High fragmentation can lead to increased random access patterns, slowing down query performance. Reorganizing data or rebuilding indexes can reduce fragmentation and improve access times.  
- **Striped storage volumes**, created using techniques such as RAID, distribute data across multiple disks in a way that allows concurrent reads and writes. This parallelism enables the database to access multiple blocks simultaneously, significantly improving throughput for read-heavy and write-heavy workloads.  
- **In-memory databases** eliminate the need for disk-based I/O, offering extremely low-latency data access by storing all data in RAM. Despite this, many in-memory systems organize their data into logical blocks or pages to maintain compatibility with traditional database algorithms and to manage memory efficiently.  
- Queries that rely on **sequential I/O** perform well when the database can read blocks of data in order without unnecessary seeks. Read-ahead mechanisms, where the database preloads data before it is requested, further enhance performance for workloads that access data sequentially, such as table scans or range queries. 
