# Database Scripts

This directory contains practical demonstration scripts for various database concepts.

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

### PostgreSQL Setup
Some scripts require PostgreSQL. Use the setup script:

```bash
bash setup/start_postgres.sh
```

This will:
- Install Docker if needed
- Pull and run a PostgreSQL container
- Configure it with test credentials

## Scripts by Category

### Mock Database Creation
- **create_mock_db.py** - Create and populate a SQLite database with sample data
  ```bash
  python create_mock_db.py
  ```

### Concurrency Demonstrations

All concurrency scripts demonstrate important database concepts:

- **concurrent_readers.py** - WAL vs Exclusive locking in SQLite
  ```bash
  python concurrency/concurrent_readers.py           # WAL mode
  python concurrency/concurrent_readers.py --exclusive  # Exclusive mode
  ```

- **deadlock_file_level.py** - File-level deadlock detection and recovery
  ```bash
  python concurrency/deadlock_file_level.py          # With recovery
  python concurrency/deadlock_file_level.py --deadlock  # Indefinite deadlock
  ```

- **deadlock_row_level.py** - Row-level deadlocks in PostgreSQL
  ```bash
  python concurrency/deadlock_row_level.py
  ```
  *Requires PostgreSQL running*

- **mvcc.py** - Multi-Version Concurrency Control demonstration
  ```bash
  python concurrency/mvcc.py
  ```

- **optimistic_vs_pessimistic_lock.py** - Compare locking strategies
  ```bash
  python concurrency/optimistic_vs_pessimistic_lock.py
  ```

- **transaction_isolation.py** - Isolation levels and dirty reads
  ```bash
  python concurrency/transaction_isolation.py
  ```

### Diagram Generation

- **diagrams/hash_ring.py** - Generate consistent hashing visualizations
  ```bash
  python diagrams/hash_ring.py
  ```
  *Generates PNG files showing hash ring behavior*

### Query String Generators

These scripts demonstrate programmatic SQL query generation:

- **generating_query_strings/create_table.py** - CREATE TABLE statements
- **generating_query_strings/insert_query.py** - INSERT statements
- **generating_query_strings/select.py** - SELECT statements
- **generating_query_strings/update_query.py** - UPDATE statements
- **generating_query_strings/delete.py** - DELETE statements

Run any of them:
```bash
python generating_query_strings/create_table.py
```

## Features

### Modern Code Quality
- ✓ Clear module docstrings explaining goals and concepts
- ✓ Type hints where applicable
- ✓ Proper error handling with informative messages
- ✓ Progress indicators for long-running operations
- ✓ SQL injection prevention (proper escaping)

### Educational Value
Each script:
- Explains what concept it demonstrates
- Shows practical use cases
- Includes inline comments for complex logic
- Provides clear output with visual indicators (✓, ✗, •)

## Troubleshooting

### "ModuleNotFoundError"
Install dependencies: `pip install -r requirements.txt`

### "Connection refused" (PostgreSQL scripts)
Start PostgreSQL: `bash setup/start_postgres.sh`

### "Database is locked" errors
This is expected behavior in some concurrency demos that intentionally create conflicts.

## Contributing

When adding new scripts:
1. Include a module-level docstring with Goal, Concept, and Usage
2. Add proper error handling
3. Use clear, informative output messages
4. Update this README with the new script
5. Add any new dependencies to requirements.txt
