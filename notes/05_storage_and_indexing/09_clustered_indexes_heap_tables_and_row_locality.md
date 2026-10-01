# Clustered Indexes, Heap Tables, and Row Locality

A table's primary key does not imply one universal physical layout.

Different engines organize base-table rows differently, and that changes how secondary indexes behave.

The two broad patterns are:

~~~text
heap table + separate indexes
~~~

and:

~~~text
clustered/index-organized table
~~~

Understanding the difference explains why the same schema can have different storage and performance characteristics across PostgreSQL, InnoDB, SQL Server, and SQLite.

## Heap table

In a heap-style table, rows are stored independently of a particular logical index order.

Conceptually:

~~~text
table pages:
[row A] [row X] [row C] [row B]

secondary index:
A -> row location
B -> row location
C -> row location
X -> row location
~~~

The index locates a row; the table stores the full row separately.

PostgreSQL normally uses this model.

## Clustered/index-organized table

In a clustered structure, the row data is organized by an index key.

~~~text
B-tree leaves:
key 10 -> row data
key 20 -> row data
key 30 -> row data
~~~

The leaf level is effectively the table's row storage.

InnoDB uses the primary key as the clustered index.

SQLite WITHOUT ROWID tables are organized by their primary key.

SQL Server allows one clustered index per table; it does not have to be the primary key.

## Why "clustered" is overloaded

Different products use the term differently.

In PostgreSQL, CLUSTER can physically reorder a table using an index, but that order is not automatically maintained after future writes.

In SQL Server and InnoDB, clustered indexing is a persistent storage organization concept.

Always read the engine-specific meaning.

## PostgreSQL heap layout

PostgreSQL index:

~~~text
B-tree leaf entry
    |
    v
heap tuple identifier
    |
    v
heap page
~~~

An ordinary index lookup can require:

1. index traversal,
2. heap/table access,
3. visibility checks.

Index-only scans can avoid some heap visits when the index covers the query and visibility-map conditions are satisfied.

## InnoDB clustered primary key

InnoDB's clustered index leaf stores the row.

~~~text
PRIMARY KEY B-tree
       |
       v
leaf contains row columns
~~~

Secondary indexes do not point to a physical heap address.

They carry the clustered primary-key value.

~~~text
secondary key
    |
    v
primary-key value
    |
    v
clustered lookup
~~~

This makes primary-key width relevant to every secondary index.

## Wide primary-key cost in clustered engines

Suppose primary key is:

~~~text
long VARCHAR
~~~

instead of:

~~~text
BIGINT
~~~

If every secondary index stores that primary-key value, wider keys can multiply storage and cache cost.

Primary-key design can therefore affect the entire index set.

## SQL Server clustered index

SQL Server permits one clustered index because table rows can only be physically ordered through one clustered structure at a time.

A primary key constraint may create a clustered index by default in some common cases, but primary key and clustering are conceptually separate choices.

A table without a clustered index is a heap.

## SQL Server nonclustered row locator

For a clustered table, a nonclustered index uses the clustering key to locate rows.

For a heap, it uses a row identifier.

This mirrors the general trade-off:

~~~text
secondary index
  -> clustered key
or
  -> heap row locator
~~~

## SQLite rowid table

Most SQLite tables are rowid tables.

If the schema declares:

~~~sql
id INTEGER PRIMARY KEY
~~~

id becomes an alias for rowid.

Secondary indexes can use rowid to locate the table row.

## SQLite WITHOUT ROWID

A WITHOUT ROWID table stores rows according to the declared PRIMARY KEY.

Example:

~~~sql
CREATE TABLE inventory (
    warehouse_id INTEGER NOT NULL,
    sku TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    PRIMARY KEY (warehouse_id, sku)
) WITHOUT ROWID;
~~~

This can avoid maintaining a separate hidden rowid for schemas whose natural primary key is already the access key.

It is not always faster; row width and query patterns matter.

## Runnable SQLite comparison

This chapter adds:

~~~text
scripts/indexing/sqlite_rowid_vs_without_rowid.py
~~~

Run:

~~~bash
python scripts/indexing/sqlite_rowid_vs_without_rowid.py
~~~

The script creates equivalent rowid and WITHOUT ROWID tables with a composite primary key, inserts the same synthetic data, and compares:

- file/page usage,
- point-lookup plans,
- local repeated lookup timing.

The numbers are local measurements only.

## Locality

If related rows are physically close, range scans can need fewer pages.

Suppose orders are clustered by:

~~~text
(customer_id, order_date)
~~~

Rows for one customer may be physically adjacent.

That can improve:

- range reads,
- cache locality,
- sequential I/O.

But maintaining strict physical order during arbitrary writes has cost.

## Secondary lookup cost

Heap model:

~~~text
secondary index
      |
      v
heap page
~~~

Clustered model:

~~~text
secondary index
      |
      v
clustered primary-key lookup
      |
      v
row
~~~

A clustered design can mean two B-tree traversals for a secondary lookup.

Whether that is expensive depends on:

- cache,
- tree depth,
- result count,
- key width.

## Primary-key lookup advantage

In a clustered table, primary-key lookup lands directly on the row-containing leaf.

That is excellent for workloads dominated by primary-key access.

But secondary-key workloads can pay for the second lookup.

## Range access advantage

Clustering by a range key can make related rows contiguous.

Example:

~~~text
(account_id, transaction_time)
~~~

can support account-history reads efficiently.

But a single table only has one primary clustering order.

Other access paths need secondary indexes or separate projections.

## Random identifiers

Random clustered keys can spread insertion across many pages.

This may:

- reduce one right-edge hotspot,
- increase random page activity,
- increase page splits.

Sequential clustered keys can do the reverse.

The right choice depends on concurrency and engine behavior.

## Clustering key stability

Changing a clustered/index-organized primary key can require moving the row and updating secondary references.

Therefore clustered keys should usually be stable.

A mutable natural identifier is often a poor clustering key.

## Surrogate versus natural key

A narrow surrogate key can reduce clustered and secondary index width.

A natural key can avoid an extra uniqueness structure if it is already compact and stable.

Consider:

- business semantics,
- width,
- stability,
- secondary index duplication,
- join ergonomics.

There is no universal winner.

## Physical clustering in PostgreSQL

PostgreSQL can reorder a table with:

~~~sql
CLUSTER orders USING idx_orders_customer_date;
~~~

This rewrites the table according to the index at that moment.

Later inserts/updates do not automatically preserve that physical order.

Therefore PostgreSQL CLUSTER is not equivalent to an InnoDB clustered index.

## Re-clustering cost

Physically rewriting a large table can consume:

- disk space,
- I/O,
- WAL depending on operation,
- locks,
- maintenance time.

Use it only when measured locality benefits justify the operational cost.

## Correlation statistics

PostgreSQL tracks correlation between physical row order and column values.

High physical correlation can make an index range scan cheaper because heap visits are more sequential.

This is one reason physical locality can influence the optimizer.

## Row locality versus columnar storage

Clustering rows by key is still row-oriented organization.

It is different from columnar storage, where values of each column are stored together.

Do not confuse:

~~~text
clustered B-tree row layout
~~~

with:

~~~text
column-oriented analytical storage
~~~

## Choosing a clustering key

Ask:

1. Which range reads matter?
2. Which point lookups dominate?
3. Is the key stable?
4. How wide is it?
5. Does the engine copy it into secondary indexes?
6. Are inserts monotonic/random?
7. Will clustering create a write hotspot?
8. Do secondary queries dominate instead?

## Common mistakes

### "Primary key means clustered"

Not in every engine.

### "Clustered means rows remain perfectly ordered forever"

Engine semantics differ.

### Very wide clustered primary key

Secondary indexes may become much larger.

### Mutable clustered key

Updates become expensive.

### Clustering for one rare report

Write/storage cost may exceed benefit.

## Related notes

- [Primary keys and secondary indexes](03_primary_key_vs_secondary_key.md)
- [Database pages](04_database_pages.md)
- [B-tree internals](06_btree_internals_and_page_splits.md)
- [Row versus column storage](02_row_based_vs_column_based_databases.md)
- [MySQL/InnoDB engine note](../12_database_engines/02_mysql.md)
- [PostgreSQL engine note](../12_database_engines/03_postgresql.md)
