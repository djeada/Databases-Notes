## How tables and indexes are stored on disk?

Tables and indexes are essential components of relational databases, and their storage on disk plays a crucial role in the performance and efficiency of database operations. This note focuses on how tables and indexes are stored on disk and the implications for database performance.

II. Storage Structure

A. Pages and Blocks

1. Data in tables and indexes are stored in fixed-size units called pages or blocks (typically 4KB, 8KB, or 16KB).
2. Pages are grouped into extents, which are contiguous allocations of a specific number of pages.
3. The database management system (DBMS) manages the allocation and deallocation of pages and extents for efficient storage and retrieval.

B. Tables

1. Tables are stored as a collection of pages on disk, with each page containing multiple rows or records.
2. Row-based storage (also called N-ary storage model, or NSM) stores entire rows together in a page, while columnar storage (also called Decomposition Storage Model, or DSM) stores each column separately in different pages.
3. Row-based storage is typically used in OLTP systems, where transactions access complete rows, while columnar storage is more suitable for OLAP systems, where analytical queries access specific columns.

C. Indexes

1. Indexes are auxiliary data structures that provide fast access to rows in a table based on specific column values.
2. Common index structures include B-trees, bitmap indexes, and hash indexes.
3. B-trees are balanced tree structures that allow for efficient searching, insertion, and deletion of data.
4. Bitmap indexes are bitmaps representing the presence or absence of a value in a column, suitable for low-cardinality columns and efficient for set-based operations.
5. Hash indexes use hash functions to map column values to corresponding row locations, providing fast access for exact-match queries.

III. Implications for Performance

A. Data Locality

1. Storing related data in close proximity on disk can improve performance by reducing disk I/O and cache misses.
2. For row-based storage, clustering rows with similar values can improve performance for range queries, while for columnar storage, compression techniques can be applied to improve storage efficiency and query performance.

B. Indexing Strategies

1. The choice of index structure depends on the access patterns and query requirements of the application.
2. B-trees are well-suited for a broad range of queries and access patterns, while bitmap indexes and hash indexes are more specialized for specific use cases.
3. Over-indexing can lead to increased storage and maintenance overhead, so it is essential to choose appropriate indexes for the application's requirements.
