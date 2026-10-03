# Indexes in Microsoft SQL Server

Indexes are data structures that help a database find rows efficiently.

Without an appropriate index, SQL Server may have to examine a large part of a table to find the rows needed by a query. With an appropriate index, SQL Server can often navigate directly to a much smaller part of the data.

A useful analogy is the index at the back of a textbook.

Suppose a 1, 000-page book contains information about SQL transactions. Without an index, you may need to scan hundreds of pages. With an index, you can look up:

```text
Transactions → page 742
```

and jump directly to the relevant location.

A database index serves a similar purpose.

## Why indexes exist

Suppose we have this table:

```sql
CREATE TABLE Users
(
    id INT NOT NULL,
    email VARCHAR(100) NOT NULL,
    name VARCHAR(100)
);
```

and it contains one million rows.

Now consider:

```sql
SELECT *
FROM Users
WHERE email = 'alice@example.com';
```

If SQL Server has no useful index on `email`, it may have to inspect many or even all rows.

Conceptually:

```text
row 1      check email
row 2      check email
row 3      check email
...
row 999999 check email
row 1000000 check email
```

This is called a scan.

If we create an index:

```sql
CREATE INDEX IX_Users_Email
ON Users(email);
```

SQL Server can potentially locate the desired value through the index instead.

Conceptually:

```text
             email index
                 │
        ┌────────┼────────┐
        │        │        │
      A-D      E-M      N-Z
        │
      alice...
        │
        ▼
   location of row
```

This is similar to looking something up in a sorted directory rather than reading every entry.

## SQL Server indexes are normally B-tree structures

Traditional SQL Server rowstore indexes are implemented using a tree structure commonly described as a B-tree.

The structure has several levels:

```text
                 Root page
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
     Intermediate  Intermediate  Intermediate
        pages         pages         pages
          │
       ┌──┴──┐
       ▼     ▼
     Leaf   Leaf
     pages  pages
```

The upper levels tell SQL Server where to continue searching.

For example, an index on `email` might conceptually contain:

```text
Root
 │
 ├── A-F
 ├── G-M
 ├── N-S
 └── T-Z
```

If SQL Server searches for:

```text
john@example.com
```

it does not need to inspect every entry. It follows the branch containing `J`.

This operation is generally called an index seek.

## Pages

SQL Server stores data in units called pages.

A SQL Server page is normally:

```text
8 KB
```

Rows and index entries are stored inside these pages.

An index therefore does not look like one enormous sorted list in memory. It consists of many linked and organized pages.

Conceptually:

```text
Page 1
+-----------------------+
| Adams                 |
| Allen                 |
| Baker                 |
| Brown                 |
+-----------------------+

Page 2
+-----------------------+
| Carter                |
| Chen                  |
| Davis                 |
| Evans                 |
+-----------------------+
```

Pages become important when discussing:

- clustered indexes
- page splits
- fragmentation
- `FILLFACTOR`

## Heap tables

A SQL Server table without a clustered index is called a heap.

For example:

```sql
CREATE TABLE HeapUsers
(
    id INT NOT NULL,
    email VARCHAR(100) NOT NULL,
    name VARCHAR(100)
);
```

At this point there is no clustered index.

SQL Server therefore stores the table as a heap.

Conceptually:

```text
HeapUsers

Data pages
┌─────────────┐
│ row         │
│ row         │
│ row         │
└─────────────┘

┌─────────────┐
│ row         │
│ row         │
└─────────────┘
```

The rows are not organized according to a clustered-index key.

That does not mean there is literally no internal organization at all. It means there is no clustered B-tree determining the logical order of the table's rows.

## Clustered indexes

A clustered index determines how the table's rows are organized at the leaf level of a B-tree.

For example:

```sql
CREATE CLUSTERED INDEX CX_Users_Id
ON HeapUsers(id);
```

The table is no longer a heap.

Its data rows now form the leaf level of the clustered index.

Conceptually:

```text
                 Clustered index
                       id
                       │
                 ┌─────┴─────┐
                 ▼           ▼
             lower ids    higher ids
                 │
                 ▼
            leaf pages
                 │
                 ▼
             actual rows
```

The important point is:

> In a clustered index, the leaf level contains the actual table rows.

This is why the clustered index is more than a separate lookup structure.

The table itself is organized as part of that index.

### Only one clustered index per table

A table can have only one clustered index.

Why?

Because the actual table rows can only form the leaf level of one clustered B-tree organization at a time.

For example, you could organize a table primarily by:

```text
id
```

or perhaps:

```text
created_at
```

but the same physical table cannot simultaneously have two independent clustered organizations.

A table can, however, have many nonclustered indexes.

## Clustered primary keys

A common SQL Server design is:

```sql
CREATE TABLE Users
(
    id INT NOT NULL,
    email VARCHAR(100) NOT NULL,
    name VARCHAR(100),

    CONSTRAINT PK_Users
        PRIMARY KEY CLUSTERED(id)
);
```

Here:

```text
PRIMARY KEY
```

defines the uniqueness/key constraint, while:

```text
CLUSTERED
```

specifies the physical index organization used to implement it.

These ideas should not be confused.

A primary key does not conceptually mean the same thing as a clustered index.

SQL Server often creates a clustered index for a primary key by default when no clustered index already exists, but the two concepts are distinct.

You can explicitly create a nonclustered primary key:

```sql
PRIMARY KEY NONCLUSTERED(id)
```

if that design is appropriate.

## Nonclustered indexes

A nonclustered index is a separate data structure from the table's main storage.

For example:

```sql
CREATE NONCLUSTERED INDEX IX_Users_Email
ON Users(email);
```

Conceptually:

```text
Nonclustered index

email
-------------------------
alice@example.com
bob@example.com
carol@example.com
```

But SQL Server needs more than the email value.

After finding:

```text
alice@example.com
```

it still needs some way to locate Alice's full row.

Therefore a nonclustered index also contains a row locator.

Conceptually:

```text
email                      row locator
------------------------------------------------
alice@example.com          → where Alice's row is
bob@example.com            → where Bob's row is
carol@example.com          → where Carol's row is
```

What the row locator contains depends on whether the underlying table is a heap or has a clustered index.

## Row locators for heap tables

Suppose the table is a heap:

```sql
CREATE TABLE HeapUsers
(
    id INT NOT NULL,
    email VARCHAR(100) NOT NULL,
    name VARCHAR(100)
);
```

and we create:

```sql
CREATE NONCLUSTERED INDEX IX_HeapUsers_Email
ON HeapUsers(email);
```

Because the table has no clustered key, SQL Server needs another way to locate each physical row.

The nonclustered index uses a RID, or Row Identifier.

Conceptually, a RID identifies a location using information corresponding to:

```text
file
page
slot
```

So the lookup resembles:

```text
Nonclustered email index
          │
          ▼
alice@example.com
          │
          ▼
         RID
          │
          ▼
   (file, page, slot)
          │
          ▼
      heap row
```

So for a heap:

> A nonclustered index uses a physical row locator.

## Row locators when a clustered index exists

Now consider this table:

```sql
CREATE TABLE ClusteredUsers
(
    id INT NOT NULL,
    email VARCHAR(100) NOT NULL,
    name VARCHAR(100),

    CONSTRAINT PK_ClusteredUsers
        PRIMARY KEY CLUSTERED(id)
);
```

and:

```sql
CREATE NONCLUSTERED INDEX IX_ClusteredUsers_Email
ON ClusteredUsers(email);
```

The clustered index key is:

```text
id
```

The nonclustered index can therefore use the clustered key to identify the full row.

Conceptually:

```text
Nonclustered index
      email
        │
        ▼
alice@example.com
        │
        ▼
 clustered key = 42
        │
        ▼
 clustered index on id
        │
        ▼
    complete row
```

The nonclustered index might conceptually resemble:

```text
email                      clustered key
------------------------------------------------
alice@example.com               42
bob@example.com                 83
carol@example.com              105
```

SQL Server can first find the email and then use the clustered key to reach the full table row.

This operation may appear in a query execution plan as a Key Lookup.

## Heap and clustered-table comparison

The difference can be summarized as follows.

### Heap

```text
Nonclustered index
       email
         │
         ▼
        RID
         │
         ▼
(file, page, slot)
         │
         ▼
     heap row
```

### Clustered table

```text
Nonclustered index
       email
         │
         ▼
 clustered key
        id
         │
         ▼
 clustered index
         │
         ▼
   actual data row
```

This distinction is one of the most important SQL Server storage concepts.

## Creating both designs

The following example creates both kinds of table.

```sql
CREATE DATABASE IndexDemo;
GO

USE IndexDemo;
GO

CREATE TABLE HeapUsers
(
    id INT NOT NULL,
    email VARCHAR(100) NOT NULL,
    name VARCHAR(100)
);

CREATE NONCLUSTERED INDEX IX_HeapUsers_Email
ON HeapUsers(email);
GO


CREATE TABLE ClusteredUsers
(
    id INT NOT NULL,
    email VARCHAR(100) NOT NULL,
    name VARCHAR(100),

    CONSTRAINT PK_ClusteredUsers
        PRIMARY KEY CLUSTERED(id)
);

CREATE NONCLUSTERED INDEX IX_ClusteredUsers_Email
ON ClusteredUsers(email);
GO
```

We can inspect their indexes through SQL Server's catalog views:

```sql
SELECT
    OBJECT_NAME(object_id) AS table_name,
    name AS index_name,
    index_id,
    type_desc
FROM sys.indexes
WHERE object_id IN
(
    OBJECT_ID('HeapUsers'),
    OBJECT_ID('ClusteredUsers')
);
```

Typical output is conceptually:

```text
table_name       index_name               type_desc
---------------- ------------------------ ----------------
HeapUsers        NULL                     HEAP
HeapUsers        IX_HeapUsers_Email       NONCLUSTERED

ClusteredUsers   PK_ClusteredUsers        CLUSTERED
ClusteredUsers   IX_ClusteredUsers_Email  NONCLUSTERED
```

Notice:

```text
HeapUsers → HEAP
```

because no clustered index exists.

The second table has:

```text
CLUSTERED
NONCLUSTERED
```

because its rows are stored through a clustered index and it also has a separate index on `email`.

## Clustered and nonclustered are not the only index technologies

When learning traditional SQL Server rowstore indexing, the two most important index organizations are:

```text
Clustered
Nonclustered
```

However, SQL Server supports additional specialized index technologies, including concepts such as:

```text
columnstore indexes
XML indexes
spatial indexes
full-text indexes
```

Therefore it is more accurate to say:

> Clustered and nonclustered indexes are the two fundamental organizations normally discussed for SQL Server rowstore B-tree indexes.

It would be misleading to claim that SQL Server supports only two possible kinds of index in every sense.

## Composite indexes

An index does not have to contain only one column.

A composite index, also called a multicolumn index, uses multiple columns as its key.

For example:

```sql
CREATE INDEX IX_Users_Name_Email
ON ClusteredUsers(name, email);
```

This creates one index whose key is:

```text
(name, email)
```

It does not create two separate indexes.

Conceptually the entries are ordered approximately like:

```text
name       email
-------------------------------
Alice      alice1@example.com
Alice      alice2@example.com
Bob        bob@example.com
Charlie    charlie@example.com
```

The first key is `name`.

Within equal `name` values, entries are then ordered by `email`.

## Column order in a composite index matters

These indexes are not equivalent:

```sql
CREATE INDEX IX_A
ON Users(name, email);
```

and:

```sql
CREATE INDEX IX_B
ON Users(email, name);
```

The first is primarily ordered by:

```text
name
```

while the second is primarily ordered by:

```text
email
```

Suppose the index is:

```sql
(name, email)
```

It is naturally useful for queries such as:

```sql
WHERE name = 'Alice'
```

and:

```sql
WHERE name = 'Alice'
  AND email = 'alice@example.com'
```

because SQL Server can navigate using the leading `name` portion of the index.

A query containing only:

```sql
WHERE email = 'alice@example.com'
```

cannot generally exploit the ordering of `(name, email)` as efficiently for a direct seek because `name`, the leading key, is unknown.

This is sometimes described as the leftmost-prefix principle.

A good mental model is a telephone directory sorted by:

```text
last_name, first_name
```

It is easy to find:

```text
Smith
```

and then:

```text
Smith, Alice
```

but it is much harder to efficiently locate every person whose first name is Alice when their last names are unknown.

## Inspecting composite-index columns

SQL Server exposes index metadata through system catalog views.

For example:

```sql
SELECT
    i.name AS index_name,
    c.name AS column_name,
    ic.key_ordinal
FROM sys.indexes AS i
JOIN sys.index_columns AS ic
  ON i.object_id = ic.object_id
 AND i.index_id = ic.index_id
JOIN sys.columns AS c
  ON c.object_id = ic.object_id
 AND c.column_id = ic.column_id
WHERE i.object_id = OBJECT_ID('ClusteredUsers')
  AND i.name = 'IX_Users_Name_Email'
ORDER BY ic.key_ordinal;
```

For:

```sql
CREATE INDEX IX_Users_Name_Email
ON ClusteredUsers(name, email);
```

the result should resemble:

```text
index_name               column_name    key_ordinal
------------------------ -------------- -----------
IX_Users_Name_Email      name           1
IX_Users_Name_Email      email          2
```

This tells us that:

```text
name  = first index key
email = second index key
```

## Indexes improve reads but have costs

Indexes are not free.

Every additional index requires:

```text
disk/storage space
memory when cached
maintenance during INSERT
maintenance during UPDATE
maintenance during DELETE
```

Suppose we insert:

```sql
INSERT INTO Users(id, email, name)
VALUES (100, 'new@example.com', 'New User');
```

SQL Server may need to modify:

```text
the table/clustered index
+
the email index
+
the name index
+
any other indexes affected by the row
```

Therefore:

> More indexes can improve some reads while making writes more expensive.

Good index design involves choosing indexes that support important queries without creating unnecessary maintenance overhead.

## Covering indexes and INCLUDE

Suppose we have:

```sql
CREATE INDEX IX_Users_Email
ON Users(email);
```

and run:

```sql
SELECT name
FROM Users
WHERE email = 'alice@example.com';
```

The index knows how to find the matching email, but SQL Server may still need to retrieve `name` from the underlying table.

One way to avoid that extra lookup is an included column:

```sql
CREATE INDEX IX_Users_Email
ON Users(email)
INCLUDE(name);
```

Conceptually:

```text
Index key             Included data
------------------------------------------
alice@example.com     Alice
bob@example.com       Bob
```

Now the index may contain everything necessary to satisfy:

```sql
SELECT name
FROM Users
WHERE email = ...
```

without visiting the underlying table row.

This is called a covering index when the index contains everything needed by a particular query.

Included columns are not part of the index's sorting key.

That distinction is important.

```sql
ON Users(email, name)
```

means both columns participate in the key ordering.

Whereas:

```sql
ON Users(email)
INCLUDE(name)
```

means:

```text
email → key
name  → stored at leaf level for retrieval
```

## What is FILLFACTOR?

Index pages have limited space.

Suppose a leaf page can conceptually hold ten entries.

A completely full page might look like:

```text
┌────────────────────────────┐
│ row │ row │ row │ row │ row│
│ row │ row │ row │ row │ row│
└────────────────────────────┘
```

If another value needs to be inserted into the middle of this page, SQL Server may need to reorganize the page and potentially perform a page split.

A page split generally means allocating another page and redistributing entries.

Conceptually:

```text
Before

Page A
[10][20][30][40][50][60][70][80]
```

Insert:

```text
35
```

If the page has no room, SQL Server may need something conceptually like:

```text
Page A
[10][20][30][35]

Page B
[40][50][60][70][80]
```

Page splits involve additional work and can contribute to index fragmentation.

## FILLFACTOR leaves room on index pages

`FILLFACTOR` tells SQL Server approximately how full to make leaf-level pages when an index is created or rebuilt.

For example:

```sql
CREATE INDEX IX_Test
ON SomeTable(id)
WITH (FILLFACTOR = 80);
```

means SQL Server tries to leave roughly:

```text
80% used
20% free
```

on appropriate leaf pages during index creation or rebuilding.

Conceptually:

```text
FILLFACTOR = 80

┌───────────────────────────────┐
│ DATA DATA DATA DATA           │
│ DATA DATA DATA DATA           │
│                     FREE FREE │
└───────────────────────────────┘
```

The free space gives future inserts room to fit without immediately causing page splits.

## A low fill factor leaves more free space

Consider:

```sql
FILLFACTOR = 20
```

Conceptually:

```text
20% used
80% free
```

while:

```sql
FILLFACTOR = 40
```

means approximately:

```text
40% used
60% free
```

Visualized:

```text
FILLFACTOR 20

| DATA |              FREE SPACE              |
  20%                    80%
```

versus:

```text
FILLFACTOR 40

|      DATA      |          FREE SPACE         |
      40%                    60%
```

If we compare the theoretical free-space percentages:

```text
80 / 60 = 1.333...
```

So a page initially rebuilt to approximately 20% fullness has around:

```text
1.33 ×
```

as much free percentage as one rebuilt to approximately 40% fullness.

This is a simplified mathematical model.

It should not be interpreted to mean that SQL Server guarantees an exact number of free rows per page. Rows can have different sizes, pages contain internal overhead, and real storage behavior is more complicated.

## FILLFACTOR is not continuously enforced

A very important detail is that `FILLFACTOR` is mainly applied when an index is:

```text
created
or
rebuilt
```

Suppose an index is rebuilt with:

```sql
FILLFACTOR = 80
```

It starts with space intentionally left available.

As new rows are inserted, that free space can gradually be consumed:

```text
After rebuild:

| 80% DATA | 20% FREE |
```

later:

```text
| 90% DATA | 10% FREE |
```

and perhaps eventually:

```text
| 100% DATA |
```

SQL Server does not continuously keep every page at exactly 80% occupancy.

`FILLFACTOR` is therefore better understood as:

> An initial page-fill target used when building or rebuilding an index.

## Why not always use a very low FILLFACTOR?

At first it may sound beneficial to leave enormous amounts of empty space.

For example:

```text
FILLFACTOR = 20
```

leaves a great deal of space for future changes.

But there is a tradeoff.

If pages contain very little data, SQL Server needs more pages to store the same number of rows.

That can mean:

```text
more storage
more pages read from disk
more pages cached in memory
more I/O for scans
```

Therefore extremely low fill factors are normally useful only in particular workloads.

The design tradeoff is:

```text
Higher fill factor
    ↓
denser pages
less storage
better scan efficiency
but less room for inserts


Lower fill factor
    ↓
more free space
potentially fewer page splits
but larger indexes
and potentially more I/O
```

## Demonstrating FILLFACTOR

Create two tables:

```sql
CREATE TABLE Fill20
(
    id INT NOT NULL,
    payload CHAR(500) NOT NULL
);

CREATE TABLE Fill40
(
    id INT NOT NULL,
    payload CHAR(500) NOT NULL
);
GO
```

Populate them:

```sql
WITH numbers AS
(
    SELECT TOP (10000)
        ROW_NUMBER() OVER (ORDER BY (SELECT NULL)) AS n
    FROM sys.all_objects AS a
    CROSS JOIN sys.all_objects AS b
)
INSERT INTO Fill20
SELECT
    n,
    REPLICATE('X', 500)
FROM numbers;

INSERT INTO Fill40
SELECT *
FROM Fill20;
GO
```

Create clustered indexes using different fill factors:

```sql
CREATE CLUSTERED INDEX CX_Fill20
ON Fill20(id)
WITH (FILLFACTOR = 20);

CREATE CLUSTERED INDEX CX_Fill40
ON Fill40(id)
WITH (FILLFACTOR = 40);
GO
```

Now inspect their physical characteristics:

```sql
SELECT
    OBJECT_NAME(object_id) AS table_name,
    index_type_desc,
    page_count,
    avg_page_space_used_in_percent,
    100 - avg_page_space_used_in_percent
        AS approx_free_percent
FROM sys.dm_db_index_physical_stats
(
    DB_ID(),
    NULL,
    NULL,
    NULL,
    'DETAILED'
)
WHERE OBJECT_NAME(object_id) IN ('Fill20', 'Fill40')
  AND index_level = 0;
```

The exact numbers will vary because real database pages contain overhead and boundary pages may not be filled uniformly.

The general expectation immediately after index construction is approximately:

```text
table     used space     free space
--------  -------------  ------------
Fill20       ~20%           ~80%
Fill40       ~40%           ~60%
```

The purpose of the experiment is to observe the effect of page-fill policy rather than expect mathematically exact page occupancy.

## SQL Server versus PostgreSQL and SQLite

The general idea of an index exists in all three systems:

```text
SQL Server
PostgreSQL
SQLite
```

All can create indexes such as:

```sql
CREATE INDEX index_name
ON table_name(column1, column2);
```

However, their internal storage architectures are not identical.

### SQL Server

Traditional SQL Server rowstore tables can be organized as:

```text
heap
```

or:

```text
clustered B-tree
```

A nonclustered index uses:

```text
RID
```

when the underlying table is a heap, and typically uses the:

```text
clustered index key
```

when the table has a clustered index.

This architecture is specific to SQL Server and closely related systems.

### PostgreSQL

PostgreSQL normally keeps table rows in a heap structure and stores indexes separately.

Its architecture is therefore not equivalent to SQL Server's clustered-index model.

PostgreSQL does have a command named:

```sql
CLUSTER
```

but it should not be confused with a SQL Server clustered index.

PostgreSQL's `CLUSTER` operation physically reorganizes a table according to an index at that point in time. It does not turn the table into the same persistent clustered-B-tree structure used by SQL Server.

PostgreSQL also supports several index methods, including:

```text
B-tree
Hash
GIN
GiST
SP-GiST
BRIN
```

These are designed for different types of searches and data.

### SQLite

SQLite also supports indexes such as:

```sql
CREATE INDEX ix_users_name_email
ON users(name, email);
```

Normal SQLite tables commonly use an internal:

```text
rowid
```

to identify rows.

SQLite also supports:

```sql
WITHOUT ROWID
```

tables, which use a different storage organization.

Again, this is not the same architecture as SQL Server's heap versus clustered-index design.

## What can safely be practiced in PostgreSQL or SQLite?

The following concepts transfer quite well:

```text
why indexes improve lookups
B-tree concepts
single-column indexes
composite indexes
importance of column order
index maintenance cost
query plans
covering-index ideas
```

But these SQL Server concepts should be practiced directly in SQL Server:

```text
heap RID row locators
clustered-index row storage
clustered keys inside nonclustered indexes
SQL Server page behavior
SQL Server FILLFACTOR behavior
SQL Server catalog/DMV inspection
```

If the goal is to understand SQL Server internals, using PostgreSQL or SQLite as a replacement can create confusion because similar terminology sometimes describes different mechanisms.

## Running SQL Server on Linux

SQL Server can be run on Linux using a container.

A typical Docker setup is:

```bash
docker pull mcr.microsoft.com/mssql/server:2025-latest
```

Then:

```bash
docker run \
  -e "ACCEPT_EULA=Y" \
  -e "MSSQL_SA_PASSWORD=StrongPassword123!" \
  -p 1433:1433 \
  --name sqlserver-demo \
  --hostname sqlserver-demo \
  -d mcr.microsoft.com/mssql/server:2025-latest
```

This exposes SQL Server on:

```text
localhost:1433
```

The container approach is particularly convenient for experiments because the database environment can be created and discarded without permanently changing the host system.

## A useful mental model

The most important relationships can be summarized like this:

```text
TABLE
│
├── No clustered index
│      │
│      └── HEAP
│            │
│            └── Nonclustered index
│                   │
│                   └── RID → physical heap row
│
└── Clustered index
       │
       ├── leaf pages contain actual table rows
       │
       └── Nonclustered index
              │
              └── clustered key → clustered index → row
```

For a composite index:

```text
INDEX(name, email)

sort/search hierarchy:

name
 │
 └── email
```

And for fill factor:

```text
FILLFACTOR 80
≈ build leaf pages around 80% full

FILLFACTOR 40
≈ build leaf pages around 40% full
```
