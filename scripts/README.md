# Database Scripts

This directory groups database-specific demos under engine-specific folders:

- `sqlite/`
- `mysql/`
- `postgres/`
- `mongo/`
- `neo4j/`

Examples that clearly belong to one engine now live in that engine's folder,
including the former concurrency demos.

## Prerequisites

### Python

Use Python 3.7+ and install the script dependencies:

```bash
cd scripts
pip install -r requirements.txt
```

### MySQL setup

```bash
bash setup/start_mysql.sh
```

Connection used by the MySQL demos:
`mysql://testuser:testpass@127.0.0.1:3306/testdb`

### PostgreSQL setup

```bash
bash setup/start_postgres.sh
```

Connection used by the PostgreSQL demos:
`postgres://demo:secret@127.0.0.1:5432/test`

### MongoDB setup

```bash
bash setup/start_mongo.sh
```

Connection used by the MongoDB demos:
`mongodb://mongoadmin:secret@127.0.0.1:27017/?authSource=admin`

### Neo4j setup

```bash
bash setup/start_neo4j.sh
```

Connection used by the Neo4j demos:
Bolt URI `bolt://127.0.0.1:7687`, user `neo4j`, password `testpass`

SQLite demos need no server setup.

## Layout

```text
scripts/
├── sqlite/
├── mysql/
├── postgres/
├── mongo/
├── neo4j/
├── diagrams/
├── generating_query_strings/
├── setup/
├── README.md
└── requirements.txt
```

## SQLite

SQLite examples are fully self-contained and now include the SQLite-specific
concurrency lessons directly in the same folder.

### Commonly misunderstood concepts

- **sqlite/foreign_keys_are_off_by_default.py**  
  `PRAGMA foreign_keys = ON` is required per connection.
  ```bash
  python sqlite/foreign_keys_are_off_by_default.py
  ```

- **sqlite/integer_primary_key_vs_autoincrement.py**  
  `INTEGER PRIMARY KEY` already auto-generates rowids; `AUTOINCREMENT` mainly
  changes reuse semantics and adds overhead.
  ```bash
  python sqlite/integer_primary_key_vs_autoincrement.py
  ```

- **sqlite/type_affinity_surprises.py**  
  Shows why storing numeric data as text produces surprising sorting and filters.
  ```bash
  python sqlite/type_affinity_surprises.py
  ```

### SQLite features and behavior

- **sqlite/full_text_search.py** - FTS5 queries  
  ```bash
  python sqlite/full_text_search.py
  ```

- **sqlite/json_functions.py** - JSON queries and updates  
  ```bash
  python sqlite/json_functions.py
  ```

- **sqlite/create_mock_db.py** - Create and populate a sample SQLite database  
  ```bash
  python sqlite/create_mock_db.py
  ```

- **sqlite/concurrent_readers.py** - WAL snapshot reads vs exclusive locking  
  ```bash
  python sqlite/concurrent_readers.py
  python sqlite/concurrent_readers.py --exclusive
  ```

- **sqlite/deadlock_file_level.py** - File-level deadlock behavior  
  ```bash
  python sqlite/deadlock_file_level.py
  python sqlite/deadlock_file_level.py --deadlock
  ```

- **sqlite/mvcc.py** - MVCC-style versioning and stale snapshots  
  ```bash
  python sqlite/mvcc.py
  ```

- **sqlite/optimistic_vs_pessimistic_lock.py** - Version checks vs immediate write locking  
  ```bash
  python sqlite/optimistic_vs_pessimistic_lock.py
  ```

- **sqlite/transaction_isolation.py** - SQLite isolation and dirty-read caveats  
  ```bash
  python sqlite/transaction_isolation.py
  ```

## MySQL

- **mysql/ddl_implicit_commit.py**  
  Shows that MySQL DDL implicitly commits the surrounding transaction.
  ```bash
  python mysql/ddl_implicit_commit.py
  ```

- **mysql/stored_procedures.py**  
  Stored procedures with parameters and result sets.
  ```bash
  python mysql/stored_procedures.py
  ```

- **mysql/triggers.py**  
  BEFORE/AFTER triggers, validation, and audit logging.
  ```bash
  python mysql/triggers.py
  ```

- **mysql/transaction_isolation.py**  
  READ UNCOMMITTED, READ COMMITTED, and REPEATABLE READ examples.
  ```bash
  python mysql/transaction_isolation.py
  ```

## PostgreSQL

- **postgres/sequences_are_not_rolled_back.py**  
  Explains why sequence-based IDs can have gaps after rollbacks.
  ```bash
  python postgres/sequences_are_not_rolled_back.py
  ```

- **postgres/transactional_ddl.py**  
  Shows that PostgreSQL DDL is usually transactional.
  ```bash
  python postgres/transactional_ddl.py
  ```

- **postgres/deadlock_row_level.py**  
  Row-level deadlock detection and retry behavior.
  ```bash
  python postgres/deadlock_row_level.py
  ```

## MongoDB

- **mongo/replace_one_vs_update_one.py**  
  Shows that `replace_one()` replaces the entire document, while
  `update_one(..., {"$set": ...})` patches only the named fields.
  ```bash
  python mongo/replace_one_vs_update_one.py
  ```

- **mongo/null_vs_missing_fields.py**  
  Demonstrates that `{field: null}` matches both explicit null and missing fields.
  ```bash
  python mongo/null_vs_missing_fields.py
  ```

## Neo4j

- **neo4j/merge_full_pattern_duplicates_nodes.py**  
  Shows why `MERGE` on a full pattern can create duplicate nodes when you
  really meant to reuse existing nodes and create only the relationship.
  ```bash
  python neo4j/merge_full_pattern_duplicates_nodes.py
  ```

- **neo4j/detach_delete_vs_delete.py**  
  Demonstrates that `DELETE` fails on nodes with attached relationships, while
  `DETACH DELETE` removes the node and its edges together.
  ```bash
  python neo4j/detach_delete_vs_delete.py
  ```

## Cross-database utilities

- **generating_query_strings/\*.py**  
  Database-agnostic SQL construction examples using identifier validation and
  DB-API placeholders for values.
  ```bash
  python generating_query_strings/select.py
  ```

- **diagrams/hash_ring.py**  
  Consistent hashing visualization utility.
  ```bash
  python diagrams/hash_ring.py
  ```

## Troubleshooting

### `ModuleNotFoundError`

Install dependencies:

```bash
pip install -r requirements.txt
```

### `Connection refused`

Start the matching database first:

- MySQL: `bash setup/start_mysql.sh`
- PostgreSQL: `bash setup/start_postgres.sh`
- MongoDB: `bash setup/start_mongo.sh`
- Neo4j: `bash setup/start_neo4j.sh`

### `database is locked`

Some SQLite examples intentionally create write contention to demonstrate how
SQLite locking works.

## Contributing

1. Put SQLite examples in `sqlite/`, MySQL examples in `mysql/`, PostgreSQL examples in `postgres/`, MongoDB examples in `mongo/`, and Neo4j examples in `neo4j/`.
2. Keep engine-specific concurrency examples in the matching engine folder.
3. Update this README when you add, move, or remove a script.
