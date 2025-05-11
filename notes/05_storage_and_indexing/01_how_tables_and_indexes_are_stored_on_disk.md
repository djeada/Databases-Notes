## Storage of Tables and Indexes on Disk

Exploring how databases store tables and indexes on disk can provide valuable insights into optimizing performance and managing data efficiently. Let's delve into the fundamental concepts of disk storage in relational databases, focusing on the structures and mechanisms that underlie data organization.

### Operating-System Files (“Datafiles”)

```
┌──────────────────────────────────────────────────────────────────────┐
│ tablespace_sales                                                     │
│┌───────────────┐┌───────────────┐┌───────────────┐                  │
││ sales01.dbf   ││ sales02.dbf   ││ sales03.dbf   │  ← ordinary files│
│└───────────────┘└───────────────┘└───────────────┘                  │
└──────────────────────────────────────────────────────────────────────┘
```

* A tablespace/filegroup is a logical pool of one or more datafiles.
* Every byte of every table, index, and catalog record is somewhere inside those files.
* Growing a table means extending a file or adding another file; the DBA chooses the policy.
* File layout on the physical platter/SSD is up to the OS unless the DBA pre-allocates contiguous space.

### Extents & Pages (Allocation Units)

```
DATAFILE  (sales01.dbf)
│
├─ Extent #17  (8 pages @ 8 KB = 64 KB)
│  ├─ Page 0  (heap rows)
│  ├─ Page 1  (heap rows)
│  ├─ Page 2  (B-tree branch)
│  ├─ Page 3  (free)
│  ├─ Page 4  (B-tree leaf)
│  ├─ Page 5  (row-overflow chain)
│  ├─ Page 6  (heap rows)
│  └─ Page 7  (free)
└─ Extent #18  …
```

* A **page** (a.k.a. block) is the atomic I/O unit; common sizes: 4 KB, 8 KB, 16 KB.
* Eight or sixteen consecutive pages form an **extent**; allocating extents keeps related pages adjacent.
* The buffer pool caches whole pages; a single row read always drags its entire page into RAM.
* Sequential scans jump extent-to-extent, minimizing head seeks on spinning media.

### Anatomy of a Data Page

```
8 KB PAGE (heap)
┌──────────────────┐ 0x0000
│ Page Header      │ ← checksum, LSN, page-type flag, free-space pointers
├──────────────────┤
│ Item Slot Array  │ ← 2-byte offsets, newest rows grow this downward
│ ─┬─┬─┬─┬─┬─┬─┬─  │
├─↓─↓─↓─↓─↓─↓─↓─↓──┤
│                  │
│   Tuple Data     │ ← rows grow upward
│                  │
└──────────────────┘ 0x2000 (end)
```

* The header tells the engine what page type it is and where free space begins/ends.
* The slot array lets rows move inside the page without breaking external row IDs.
* A delete clears the slot; an update that no longer fits may move the row elsewhere and leave a forwarding stub.
* Free space in the middle is coalesced during a **VACUUM / OPTIMIZE / REORG** pass.

### Heap Table Lifecycle

```
INSERT PATH
Client → Buffer Pool → find page w/ ≥ row_size free → write row → mark page dirty
                                                             ↓
                                            checkpoint writes dirty page back to disk
```

* Rows are appended to the first page listed as “enough-free” in the free-space map.
* Delete = mark slot unused; data bytes may linger until vacuum to avoid extra WAL.
* Update that grows = move row; original slot now a redirect pointer; causes internal fragmentation.
* Heap scans read every page from first to last; index scans use row IDs to jump directly.

### Clustered (Index-Organized) Tables

```
CLUSTERED B-TREE
          (root p500)
        /               \
   (p510)               (p560)   ← branch nodes
   /   \                 /   \
p512  p518           p562   p570 ← leaf nodes = full rows
```

* The primary-key index *is* the table; leaf pages hold whole rows in key order.
* Range predicates (`BETWEEN`, `>=`) read consecutive leaf pages with almost no random I/O.
* Random UUID keys scatter inserts → many page splits → higher write amplification.
* Enlarging a row may push it to another leaf, updating parent pointers.

### Secondary (Non-Clustered) Index Walk

```
SELECT … WHERE sku = 'A42';
┌─────────────┐
│  index root │
└──────┬──────┘
       │  (binary search)
       ▼
┌─────────────┐
│  index leaf │  contains (sku, page#, slot#)
└──────┬──────┘
       │  (single pointer hop)
       ▼
┌─────────────┐
│  heap page  │  contains actual row
└─────────────┘
```

* Leaf stores only key + **RID** (page#, slot#) so it stays compact.
* Query path: traverse the B-tree → fetch heap page → return row.
* If the leaf already includes every column in the `SELECT` list, the engine performs an **index-only scan** and never touches the heap page.

### Other Index Types in One Picture

```
┌──────────── HASH ────────────┐   equality only
│ key → hash → bucket page     │
└──────────────────────────────┘
┌────────── BITMAP ────────────┐   low-cardinality columns
│ value1  1010011001           │
│ value2  0101100100           │
└──────────────────────────────┘
┌───── GIN / INVERTED ─────────┐   arrays, JSON, full-text
│ term → posting list of RIDs  │
└──────────────────────────────┘
```

* Hash = O(1) equality, no range support, directory may need re-splitting.
* Bitmap = 1 bit per row; logical AND/OR of bitmaps solves multi-column predicates quickly.
* Partial index = any type restricted by a `WHERE` clause; rows outside predicate are invisible to the index.
* Covering/index-include = copy extra columns into leaf → query satisfied directly from index.

### Free-Space & Extent Maps

```
FREE SPACE MAP (FSM)
page_id │ free_bytes
────────┼─────────────
   100  │  800
   101  │    0
   102  │ 1600
…
```

* FSM answers “which page has ≥ N free bytes?” in O(1) time.
* When no page qualifies, the engine grabs a free page from the **Extent Map**.
* Extent Map tracks which extents are allocated vs. brand-new vs. totally empty and reusable.
* Large deletes make extents 100 % empty; a background task hands them back to the file so other objects can grow there.

### Write-Ahead Log (WAL) Relationship

```
┌──────────────┐   (1) change row
│ client query │ ───────────────────────────────────┐
└──────────────┘                                    │
                 (2) append redo record to WAL file │ (sequential)
                                                    ▼
                                             (3) commit-ack
                                                    │
                             (4) later: flush dirty page to datafile
```

* All page changes first land in the sequential WAL so commits are fast and crash-safe.
* Background checkpoints write dirty pages in large batches, turning many random page writes into fewer sequential WAL writes.
* After a crash, the engine replays WAL records newer than the last checkpoint to rebuild all pages to a consistent state.


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

* Align database page size with SSD/HDD physical block (4 KB or 16 KB) to avoid partial-block I/O.
* Keep hot rows small; overflow chaining kills cache hit rates.
* Cluster by monotonically increasing keys when you can; if you must use UUIDs, batch inserts or use time-sorted UUID variants to reduce page splits.
* Rebuild or `VACUUM FULL` tables that show > 20 % dead rows or 2× bloat.
* Create covering indexes for frequent read-only analytics, but remember each extra column burdens INSERT/UPDATE.
* Watch the free-space map: if every page shows “full” but the table keeps extending, you have bloat.
