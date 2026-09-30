# Primary Keys, Alternate Keys, and Secondary Indexes

A **key** expresses an identification rule. An **index** is a physical access structure. The two are related because engines often use indexes to enforce keys, but they are not interchangeable.

## Terminology

| Term | Meaning | Example |
| --- | --- | --- |
| Superkey | A set of columns that uniquely identifies a row; it can include unnecessary columns. | `(user_id, email)` when `user_id` alone is unique. |
| Candidate key | A minimal superkey. | `user_id`, or a required unique email. |
| Primary key | The candidate key selected as the table's main identifier. | `PRIMARY KEY (user_id)`. |
| Alternate key | A candidate key not selected as the primary key. | A required unique email. |
| Secondary index | An additional access path, which can be unique or non-unique. | An index on `last_name`. |
| Foreign key | A constraint connecting referencing values to a permitted referenced key. | `orders.user_id` references `users.user_id`. |

“Secondary key” is used inconsistently: some texts mean an alternate identifier, others mean a search attribute. Prefer the precise terms above.

## Example schema

The following runs in PostgreSQL and SQLite. Enable `PRAGMA foreign_keys = ON` on each SQLite connection when using foreign keys.

```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    last_name VARCHAR(100) NOT NULL
);

CREATE INDEX idx_users_last_name ON users (last_name);

INSERT INTO users (user_id, email, last_name)
VALUES (1, 'alice@example.com', 'Smith'),
       (2, 'bob@example.com', 'Smith');
```

`user_id` is the primary key, `email` is an alternate key, and `last_name` has a non-unique secondary index. Both Smith rows are valid. Duplicate emails are rejected.

```sql
SELECT user_id, email FROM users WHERE last_name = 'Smith';
```

The optimizer can use the secondary index but may prefer a scan for a small table or a predicate matching many rows. An index does not guarantee a particular query plan or output order; add `ORDER BY` when order matters.

## Nullability and composite keys

A primary key is unique and non-null in the relational model. Some legacy SQLite rowid-table declarations permit nulls in primary-key columns; use explicit `NOT NULL`, `INTEGER PRIMARY KEY`, or an appropriate strict/without-rowid table to avoid that exception.

A composite key identifies a row by the whole tuple:

```sql
CREATE TABLE enrollments (
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    PRIMARY KEY (student_id, course_id)
);
```

Neither column must be unique by itself. Nullable `UNIQUE` columns are not automatically candidate keys: null handling differs by engine, and an identifier should be required.

## Keys do not determine one universal storage layout

InnoDB stores rows in its clustered index, normally keyed by the primary key. SQL Server can use a clustered or nonclustered primary-key index. PostgreSQL normally stores table rows in a heap with separate indexes. SQLite's `INTEGER PRIMARY KEY` aliases the rowid in a rowid table.

Choose identifiers for stability and correct uniqueness rules; choose additional indexes for measured access patterns. Wider keys can increase storage and write costs, especially when secondary indexes also carry the clustered key.

## Related notes

- [Storage on disk](01_how_tables_and_indexes_are_stored_on_disk.md)
- [Indexing](05_indexing.md)
- [SQLite primary-key behavior](https://www.sqlite.org/lang_createtable.html#the_primary_key)
