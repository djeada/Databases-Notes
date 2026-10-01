# How Tables and Indexes Reach Storage

The SQL table is a logical view of data. The engine must represent its rows, indexes, and recovery information as bytes. Understanding that representation helps explain why returning a few rows can require many reads, why indexes cost space, and why committed data can survive a crash.

Read [transactions](../04_acid_properties_and_transactions/01_transactions_intro.md) first. This chapter introduces the main layers; the later [page](04_database_pages.md) and [index](05_indexing.md) notes explain their details.

## Start with the path of a product lookup

When the bookstore runs `SELECT title FROM products WHERE product_id = 10`, a typical engine:

1. Uses schema metadata to interpret the table and column names.
2. Chooses an access path, such as an index lookup or table scan.
3. Finds the required storage pages in memory or reads them from storage.
4. Checks which row version is visible to the transaction, where versioning is used.
5. Decodes the title and returns it to the client.

The query's result is one title. The internal work can include index pages, table pages, visibility information, and additional reads. A query plan describes the chosen operations, not a literal file address for each row.

## Separate logical objects from physical files

| Layer | What it describes |
|---|---|
| Table and index | Objects queried or maintained by the database |
| Page or block | A chunk used for storage and memory management |
| Data file | A file containing database data structures |
| Filesystem and device | The layers that store and retrieve the file's bytes |

One table is not universally one file, and one row is not universally one line of text. Engines can place objects in separate files, shared files, or more complex arrangements. A **tablespace** or **filegroup**, where supported, is an engine-specific way of organizing storage locations or allocation.

Some engines allocate groups of pages called **extents**. Their sizes and ownership rules vary. A page is not a universal guarantee of an indivisible hardware write; recovery must handle the storage engine's actual failure assumptions.

## Tables can use different organizations

A **heap table** stores rows without maintaining a table-wide key order. An index entry can point to a row location, so a lookup searches the index and then obtains the row.

A **clustered** or **index-organized** table stores its main row data in an index structure ordered by a key. In that design, reaching a leaf of the main structure can also reach the row's fields. This describes the engine's layout; it does not promise that a query without `ORDER BY` returns rows in that order.

| Example engine | Simplified organization |
|---|---|
| PostgreSQL | Ordinary tables use heap storage; indexes are separate structures |
| MySQL InnoDB | Main row data is organized by a clustered key; secondary indexes identify rows through that key |
| SQLite | Ordinary rowid tables use table B-trees keyed by rowid; an `INTEGER PRIMARY KEY` aliases that rowid; `WITHOUT ROWID` tables use a different primary-key organization |

These descriptions introduce the differences rather than specifying every file-format detail. Column-oriented analytical engines organize values differently, as the [next note](02_row_based_vs_column_based_databases.md) explains.

## An index is stored data too

A B-tree-family index keeps searchable keys in a tree of pages. Upper levels guide the search; leaf pages hold entries or row data according to the engine's design. Finding one key follows a route through the tree instead of scanning every table row.

That route still costs work. A non-covering index may lead to additional table-page reads. Matching many rows can make those reads more expensive than scanning. Changes to indexed values require maintaining the index and can sometimes split a full page into additional pages.

A **secondary index** supplies another access path, such as finding customers by email rather than their identifier. The [key comparison](03_primary_key_vs_secondary_key.md) separates the logical meaning of a key from the physical role of an index.

## Memory changes the read cost

Database engines commonly keep pages in a **buffer pool** or **page cache**. Repeated access can reuse a page already in memory. A new or larger workload may need to load pages that are absent.

This is why the same query can take different times with a cold cache and a warm cache. An operating-system cache adds another layer, so a database's reported storage read does not always imply a physical device access.

An application's cache of query results is a different layer. It can skip a database request, but needs its own freshness policy. See [caching](../08_database_performance/03_database_caching.md).

## Writes involve recovery information

The engine may modify a page in memory before writing that page back to a data file. A **dirty page** is a modified cached page whose changes have not yet been flushed to its persistent data location.

With **write-ahead logging (WAL)**, the engine persists the required recovery information before the corresponding data-page changes. Durable commit can depend on persisting log records rather than immediately flushing every changed data page. Recovery uses that information to reconstruct the accepted state after a crash.

The implementation differs by engine, and some engines use other journal arrangements. Do not infer a universal on-disk sequence from the high-level idea. [Durability](../04_acid_properties_and_transactions/05_durability.md) connects persistence ordering to transaction guarantees.

## Space needs maintenance over time

Deletes and updates do not always make file sizes shrink immediately. Engines may retain old versions until they are no longer needed, leave reusable free space, or require maintenance to reclaim it.

**Vacuuming**, **purging**, and compaction are engine-specific maintenance concepts, not interchangeable commands. Index rebuilds also have their own costs and locking or concurrency behavior. Diagnose actual space and query problems before scheduling broad rebuilds.

## Check your understanding

1. Why can a one-row result require several page accesses?
2. How does a heap differ from an index-organized table?
3. Why does a secondary index require additional storage and write work?
4. Why does a warm cache change timing without changing the result?
5. Why need a deleted row not immediately shrink a database file?

Next: [row-oriented versus column-oriented storage](02_row_based_vs_column_based_databases.md), followed by [keys](03_primary_key_vs_secondary_key.md), [pages](04_database_pages.md), and the [indexing overview](05_indexing.md). For physical index behavior, continue to [B-tree internals](06_btree_internals_and_page_splits.md) and [clustered versus heap storage](09_clustered_indexes_heap_tables_and_row_locality.md).
