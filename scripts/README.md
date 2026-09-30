# Database Scripts

This directory groups database-specific demos under engine-specific folders:

- `sqlite/`
- `mysql/`
- `postgres/`
- `mongo/`
- `neo4j/`
- `sqlserver/`
- `big_data/`
- `orm/`

Examples that clearly belong to one engine now live in that engine's folder,
including the former concurrency demos.

## Prerequisites

### Python

Use Python 3.7+ for the existing demos and Python 3.10+ for the SQL Server
console. Install the script dependencies:

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
├── sqlserver/
├── big_data/
├── orm/
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

- **[postgres/acid_escape_room/](postgres/acid_escape_room/README.md)**  
  Eight multiprocessing scenarios: intentionally BAD and GOOD implementations
  of **Atomicity, Consistency, Isolation, and Durability**. Includes a dedicated
  PostgreSQL Docker Compose stack, sample-data seeding, run assertions, and a
  post-restart durability check. **Use its separate README and disposable
  `acid_lab` database**, not the generic PostgreSQL setup above.
  ```bash
  python postgres/acid_escape_room/lab.py seed --workers 8
  python postgres/acid_escape_room/lab.py run --property all --mode both --workers 8
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

## SQL Server

### Multiline Docker console

`sqlserver/sql_docker_console.py` connects to an existing SQL Server container
through the Docker CLI and keeps one `sqlcmd` session alive between scripts.
The container must be running and have `sqlcmd` installed (default path:
`/opt/mssql-tools18/bin/sqlcmd`). Install `prompt-toolkit` in the Python
environment used to launch the console:

```bash
python3 -m pip install prompt-toolkit
python3 sqlserver/sql_docker_console.py
```

Run these commands from `scripts/`. The default container is `sqlserver-demo`,
with server `localhost`, login `sa`, and initial database `master`. The console
prompts for connection settings and a hidden password. Override prompt defaults
with `--container`, `--server`, `--user`, `--database`, and `--sqlcmd`:

```bash
python3 sqlserver/sql_docker_console.py --container my-sqlserver --database mydb
```

`SQL_DOCKER_CONTAINER` also sets the default container. `SQLCMDPASSWORD` can
supply the password; otherwise it is requested interactively. The password is
passed to the container through stdin rather than the Docker command line.

- Paste multiline SQL, including `GO` batch separators.
- Enter inserts a newline; Ctrl+R or Esc then Enter executes the entire script.
- Arrow keys move through the editor; Ctrl+C clears the buffer.
- Enter submits commands on their own line: `:help`, `:use DATABASE`, `:status`,
  and `:quit`.
- Ctrl+D exits when the buffer is empty.

Results and SQL messages appear separately. Database changes and session state
persist across executions because the connection remains open.

## Big Data

These demos are local teaching examples for the final Big Data chapter. They keep
the data small so the execution model is visible without requiring a cluster.

Install their optional dependencies:

```bash
pip install -r big_data/requirements.txt
```

- **big_data/warehouse_demo.py** - Builds a small star schema in DuckDB and runs
  an analytical aggregation.
  ```bash
  python big_data/warehouse_demo.py
  ```

- **big_data/spark_sql_demo.py** - Starts Spark in local mode, runs SQL over a
  DataFrame, prints the execution plan, writes Parquet, and reads it back.
  A compatible Java runtime is required.
  ```bash
  java -version
  python big_data/spark_sql_demo.py
  ```

- **big_data/parquet_lake_demo.py** - Writes a partitioned Parquet dataset with
  DuckDB, shows the resulting lake-style directory layout, and queries one
  partition directly.
  ```bash
  python big_data/parquet_lake_demo.py
  ```

- **big_data/kafka/docker-compose.yml** - Runs a single-node Kafka 4.3.1 broker
  in KRaft mode for the streaming/CDC note.
  ```bash
  cd big_data/kafka
  docker compose up -d
  docker compose down
  ```

## ORM

Install the ORM demo dependency:

```bash
pip install -r orm/requirements.txt
```

- **orm/sqlalchemy_demo.py** - Maps users and posts with SQLAlchemy 2.x, runs a
  transaction, demonstrates select-in relationship loading, updates a row, and
  enables SQL logging so the generated statements are visible.
  ```bash
  python orm/sqlalchemy_demo.py
  ```

- **orm/n_plus_one_demo.py** - Counts SQL statements for lazy relationship
  loading versus `selectinload()`, making the N+1 problem measurable.
  ```bash
  python orm/n_plus_one_demo.py
  ```

- **orm/optimistic_concurrency_demo.py** - Opens two sessions on the same
  versioned row and shows SQLAlchemy rejecting a stale update.
  ```bash
  python orm/optimistic_concurrency_demo.py
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

1. Put SQLite examples in `sqlite/`, MySQL examples in `mysql/`, PostgreSQL examples in `postgres/`, MongoDB examples in `mongo/`, Neo4j examples in `neo4j/`, and SQL Server utilities in `sqlserver/`.
2. Keep engine-specific concurrency examples in the matching engine folder.
3. Update this README when you add, move, or remove a script.
