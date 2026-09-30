# Database Pages: The Chunks Behind a Table

SQL presents a table as rows and columns. Storage works with chunks of bytes. In many database engines, a **page** is a fixed-size unit used to organize data and transfer it between storage and memory. A table or index usually spans many pages.

This distinction helps explain query performance: finding one row may require reading a page containing several rows. The cost depends partly on which pages the engine must visit, not only on how many rows it returns.

## Follow a read from query to storage

Suppose the bookstore looks up product 10 by its primary key.

1. The engine chooses a way to find the row, often through an index.
2. It checks whether the needed pages are already in its memory cache.
3. For missing pages, it reads data from storage.
4. It interprets the stored row and returns the requested columns.

The memory cache for database pages is commonly called a **buffer pool** or **page cache**. A **cache hit** means the needed page is already there. A **cache miss** means it must be obtained from a lower storage layer. Operating-system caches can also affect whether an engine read reaches the physical device.

## What fits inside a page?

A simplified row-storage page looks like this:

```text
+----------------------------------+
| Header: information about page   |
| Row locations / slot information |
| Free space                       |
| Encoded row data                 |
+----------------------------------+
```

The **header** stores bookkeeping information. A **slot** can identify a row's location within the page. The row data contains encoded values rather than the formatted text shown by a SQL client. Actual layouts vary: SQLite B-tree pages, PostgreSQL heap pages, and InnoDB pages do not share one universal layout.

Rows have different lengths, and one large value need not fit on one page. Engines may use overflow pages or separate storage for large values. Updates can create new row versions or change space requirements, so free space and cleanup matter as well.

## Why an index can save page reads

Imagine a table spread across 1,000 data pages. A query for one customer's orders can follow either of two broad paths:

| Path | Work |
|---|---|
| Scan | Visit the table's pages and test each row |
| Index lookup | Search the index, then fetch matching data when needed |

An index is useful when its route visits substantially fewer pages. It is not free: the index occupies pages, and inserts or updates may need to modify them. A query matching most of the table can make a scan cheaper than many separate row lookups.

A **covering index** includes everything needed by a query, which can reduce table-page visits. Whether an engine actually avoids those visits also depends on its visibility rules and implementation. See [Indexing](05_indexing.md) for B-tree search and query-plan examples.

## Writes, logs, and checkpoints

Changing a row generally changes a page in memory. A changed page is often called **dirty** until its current contents are written to persistent storage. A database may flush pages later rather than writing every data page immediately at commit.

With **write-ahead logging**, recovery information reaches durable storage before the corresponding data-page changes do. This can let the engine acknowledge a durable commit using the log and recover the data pages after a crash. A **checkpoint** advances the recovery process by recording a recovery boundary and, depending on the engine, flushing or coordinating relevant data.

These are engine-specific mechanisms, not a promise that every commit rewrites every affected data page. Read [Durability](../04_acid_properties_and_transactions/05_durability.md) before the detailed [crash recovery note](../11_security_best_practices/07_crash_recovery_in_databases.md).

## Page size is a tradeoff, not a speed setting

Larger pages can hold more rows or index entries, but a small lookup may read more unrelated bytes. Smaller pages can reduce that extra data while requiring more pages and bookkeeping. Row size, access patterns, caching, and the engine's supported settings all matter.

For a beginner, understanding the access path is more useful than changing the page size. Start by asking: is this query scanning many pages, making repeated lookups, or reusing pages already cached?

## Check your understanding

1. Why can returning one row involve reading more than that row's bytes?
2. What is the difference between a cache hit and a cache miss?
3. Why might a scan beat an index lookup for a query matching most rows?
4. How can a commit be durable before all changed data pages are flushed?

Next: [Indexing](05_indexing.md) builds a search structure from these storage units.
