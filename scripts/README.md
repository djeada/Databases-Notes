# Database Scripts

This directory contains practical demonstration scripts for various database concepts, **organized by database type** (SQLite, MySQL, PostgreSQL).

## Overview

These scripts are designed to be **modern, clean, and demonstrate database concepts clearly**. Each script includes:
- Clear documentation explaining the goal and concept
- Proper error handling
- Helpful output messages
- Example usage instructions

## Prerequisites

### Python Environment
All scripts require Python 3.7 or later.

### Installing Dependencies

```bash
cd scripts
pip install -r requirements.txt
```

### Database Setup

#### MySQL Setup
For MySQL-specific examples, use the setup script:

```bash
bash setup/start_mysql.sh
```

This will:
- Install Docker if needed
- Pull and run a MySQL container
- Configure it with test credentials
- Connection: `mysql://testuser:testpass@127.0.0.1:3306/testdb`

#### PostgreSQL Setup
For PostgreSQL-specific examples, use the setup script:

```bash
bash setup/start_postgres.sh
```

This will:
- Install Docker if needed
- Pull and run a PostgreSQL container
- Configure it with test credentials
- Connection: `postgres://demo:secret@127.0.0.1:5432/test`

## Scripts by Database Type

### SQLite Examples

SQLite is perfect for lightweight, embedded database demonstrations. No setup required!

#### **Full-Text Search (FTS5)**
- **sqlite_examples/full_text_search.py** - Demonstrate SQLite's powerful FTS5 capabilities
  ```bash
  python sqlite_examples/full_text_search.py
  ```
  Covers: Basic search, phrase search, boolean operators, prefix matching, column-specific search

#### **JSON Functions**
- **sqlite_examples/json_functions.py** - Store and query JSON data in SQLite
  ```bash
  python sqlite_examples/json_functions.py
  ```
  Covers: JSON extraction, filtering, array queries, modifications, aggregations

#### **Concurrency (SQLite-specific)**
- **concurrency/concurrent_readers.py** - WAL vs Exclusive locking
  ```bash
  python concurrency/concurrent_readers.py           # WAL mode
  python concurrency/concurrent_readers.py --exclusive  # Exclusive mode
  ```

- **concurrency/deadlock_file_level.py** - File-level deadlock detection
  ```bash
  python concurrency/deadlock_file_level.py          # With recovery
  python concurrency/deadlock_file_level.py --deadlock  # Indefinite deadlock
  ```

- **concurrency/mvcc.py** - Multi-Version Concurrency Control
  ```bash
  python concurrency/mvcc.py
  ```

- **concurrency/optimistic_vs_pessimistic_lock.py** - Compare locking strategies
  ```bash
  python concurrency/optimistic_vs_pessimistic_lock.py
  ```

- **concurrency/transaction_isolation.py** - Isolation levels and dirty reads
  ```bash
  python concurrency/transaction_isolation.py
  ```

### MySQL Examples

MySQL examples demonstrate features that work best with a full-featured RDBMS.

*Requires MySQL running - use `bash setup/start_mysql.sh`*

#### **Stored Procedures**
- **mysql_examples/stored_procedures.py** - Create and use stored procedures
  ```bash
  python mysql_examples/stored_procedures.py
  ```
  Covers: Procedures with parameters, calculating aggregates, returning result sets

#### **Triggers**
- **mysql_examples/triggers.py** - Automatic actions on database events
  ```bash
  python mysql_examples/triggers.py
  ```
  Covers: BEFORE/AFTER triggers, INSERT/UPDATE/DELETE events, audit logging, validation

#### **Transaction Isolation Levels**
- **mysql_examples/transaction_isolation.py** - Compare isolation levels
  ```bash
  python mysql_examples/transaction_isolation.py
  ```
  Covers: READ UNCOMMITTED, READ COMMITTED, REPEATABLE READ, dirty reads, phantom reads

### PostgreSQL Examples

PostgreSQL-specific features.

*Requires PostgreSQL running - use `bash setup/start_postgres.sh`*

#### **Row-Level Deadlocks**
- **concurrency/deadlock_row_level.py** - Row-level deadlock detection in PostgreSQL
  ```bash
  python concurrency/deadlock_row_level.py
  ```

### General Examples

These work across database types or are database-agnostic.

#### **Mock Database Creation**
- **create_mock_db.py** - Create and populate a SQLite database with sample data
  ```bash
  python create_mock_db.py
  ```

#### **Diagram Generation**
- **diagrams/hash_ring.py** - Generate consistent hashing visualizations
  ```bash
  python diagrams/hash_ring.py
  ```
  *Generates PNG files showing hash ring behavior for distributed systems*

#### **Query String Generators**
Programmatic SQL query generation (database-agnostic):

- **generating_query_strings/create_table.py** - CREATE TABLE statements
- **generating_query_strings/insert_query.py** - INSERT statements
- **generating_query_strings/select.py** - SELECT statements
- **generating_query_strings/update_query.py** - UPDATE statements
- **generating_query_strings/delete.py** - DELETE statements

Run any of them:
```bash
python generating_query_strings/create_table.py
```

## Features by Database

| Feature | SQLite | MySQL | PostgreSQL |
|---------|--------|-------|------------|
| Full-Text Search (FTS5) | ✓ | | |
| JSON Functions | ✓ | ✓ | ✓ |
| Stored Procedures | Limited | ✓ | ✓ |
| Triggers | ✓ | ✓ | ✓ |
| File-Level Locking | ✓ | | |
| Row-Level Locking | | ✓ | ✓ |
| MVCC | ✓ | ✓ | ✓ |
| Multiple Isolation Levels | Limited | ✓ | ✓ |

## Modern Code Quality

- ✓ Clear module docstrings explaining goals and concepts
- ✓ Type hints where applicable
- ✓ Proper error handling with informative messages
- ✓ Progress indicators for long-running operations
- ✓ SQL injection prevention (proper escaping)
- ✓ Visual indicators (✓, ✗, •) in output

## Educational Value

Each script:
- Explains what concept it demonstrates
- Shows practical use cases
- Includes inline comments for complex logic
- Provides clear output with visual indicators
- Can be run independently

## Troubleshooting

### "ModuleNotFoundError"
Install dependencies: `pip install -r requirements.txt`

### "Connection refused" (MySQL scripts)
Start MySQL: `bash setup/start_mysql.sh`

### "Connection refused" (PostgreSQL scripts)
Start PostgreSQL: `bash setup/start_postgres.sh`

### "Database is locked" errors
This is expected behavior in some SQLite concurrency demos that intentionally create conflicts.

## Contributing

When adding new scripts:
1. Choose the appropriate directory (sqlite_examples, mysql_examples, or general)
2. Include a module-level docstring with Goal, Concept, Prerequisites, and Usage
3. Add proper error handling
4. Use clear, informative output messages
5. Update this README with the new script
6. Add any new dependencies to requirements.txt
