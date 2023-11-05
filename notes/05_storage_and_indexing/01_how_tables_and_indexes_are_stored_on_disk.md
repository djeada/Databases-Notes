## Understanding the Storage of Tables and Indexes on Disk

Tables and indexes, as crucial components of relational databases, significantly influence the performance and efficiency of database operations. This note delves into how tables and indexes are stored on disk and explores the implications this has on database performance.

### Storage Structure

#### Pages and Blocks

1. **Units of Storage**: Data in tables and indexes are stored in fixed-size units, referred to as pages or blocks, with common sizes being 4KB, 8KB, or 16KB.
2. **Extents**: Pages are grouped into extents, contiguous allocations that consist of a specific number of pages.
3. **Management**: The Database Management System (DBMS) is responsible for the allocation and deallocation of pages and extents, ensuring efficient storage and retrieval.

```
+---------------------+       +---------------------+
|      Extent 1       |       |      Extent 2       |
| +-------+-------+   |       | +-------+-------+   |
| | Page 1| Page 2|   |       | | Page 3| Page 4|   |
| |+-----+|+-----+|   |       | |+-----+|+-----+|   |
| ||Block||Block||...||       | ||Block||Block||...||
| |+-----+|+-----+|   |       | |+-----+|+-----+|   |
| +-------+-------+   |       | +-------+-------+   |
+---------------------+       +---------------------+
```

#### Tables

1. **Collection of Pages**: Tables are stored on disk as a collection of pages, with each page containing multiple rows or records.
2. **Storage Models**:
   - **Row-based Storage** (N-ary Storage Model, NSM): This model stores entire rows contiguously in a page.
   - **Columnar Storage** (Decomposition Storage Model, DSM): This model stores each column's data separately across different pages.
3. **Use Cases**: Row-based storage is favored in Online Transaction Processing (OLTP) systems for transactions accessing complete rows, while columnar storage is advantageous in Online Analytical Processing (OLAP) systems where queries access specific columns.

#### Indexes

1. **Purpose**: Indexes are data structures designed to provide fast access to rows in a table based on the values of one or more columns.
2. **Types of Indexes**:
   - **B-trees**: Balanced tree structures that ensure efficient searching, insertion, and deletion of data.
   - **Bitmap Indexes**: Bitmaps that indicate the presence or absence of a value in a column, suitable for columns with low cardinality.
   - **Hash Indexes**: These use hash functions to map column values to row locations, ideal for exact-match queries.
3. **Implementation**: Indexes can be created and managed using SQL commands or database-specific tools.

### Implications for Performance

#### Data Locality

1. **Proximity**: Storing related data close to each other on the disk can boost performance by minimizing disk I/O and cache misses.
2. **Clustering and Compression**: Clustering similar rows in row-based storage can enhance performance for range queries. In columnar storage, compression techniques can be employed to improve both storage efficiency and query performance.

#### Indexing Strategies

1. **Choice of Index**: The selection of an index structure should align with the application's access patterns and query needs.
2. **Versatility vs. Specialization**: B-trees are versatile, catering to various queries, while bitmap and hash indexes are specialized for specific scenarios.
3. **Over-Indexing**: Excessive indexing can lead to increased storage requirements and maintenance overhead. Thus, it is crucial to strategically choose indexes that align with the application's needs.
