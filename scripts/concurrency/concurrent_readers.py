#!/usr/bin/env python3
"""
Concurrent Readers Demo

Goal: Demonstrate the difference between exclusive locking and Write-Ahead Logging (WAL)
      in SQLite when multiple readers attempt to access data during a write operation.

Concept:
- With EXCLUSIVE locking mode, readers are blocked while a writer holds the lock
- With WAL mode, readers can read a consistent snapshot while writes are in progress

Usage:
    python concurrent_readers.py              # Run with WAL mode (concurrent reads allowed)
    python concurrent_readers.py --exclusive  # Run with EXCLUSIVE mode (readers blocked)
"""
import sqlite3
import multiprocessing
import argparse
import os
import time

DB = 'demo.sqlite'

def setup_database():
    """Create the database and test table."""
    if os.path.exists(DB):
        os.remove(DB)
    conn = sqlite3.connect(DB)
    conn.execute("""
        CREATE TABLE test (
            id    INTEGER PRIMARY KEY,
            value TEXT
        );
    """)
    conn.execute("INSERT INTO test (id, value) VALUES (1, 'initial');")
    conn.commit()
    conn.close()
    print("[Setup] Initialized database with one row.\n")

def writer(exclusive_mode):
    """Begin a long transaction as writer."""
    conn = sqlite3.connect(DB, isolation_level=None, timeout=30)
    cur = conn.cursor()
    if exclusive_mode:
        # Force all locks to be exclusive; readers will block
        conn.execute("PRAGMA locking_mode = EXCLUSIVE;")
        conn.execute("PRAGMA journal_mode = DELETE;")
        print("[Writer] PRAGMA locking_mode=EXCLUSIVE; journal_mode=DELETE")
        conn.execute("BEGIN EXCLUSIVE;")
    else:
        # WAL gives concurrent readers during writes
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("PRAGMA wal_autocheckpoint = 1000;")
        print("[Writer] PRAGMA journal_mode=WAL; wal_autocheckpoint=1000")
        conn.execute("BEGIN;")
    print(f"[Writer] Started transaction; updating row...")
    conn.execute("UPDATE test SET value = ? WHERE id = 1;", 
                 ('written-'+('X' if exclusive_mode else 'W'),))
    print(f"[Writer] Update done, sleeping for 5s to hold lock...")
    time.sleep(5)
    conn.commit()
    print("[Writer] Committed and released locks.\n")
    conn.close()

def reader(name):
    """Attempt to read the single row."""
    print(f"[{name}] Attempting to read...")
    conn = sqlite3.connect(DB, timeout=30)
    try:
        cur = conn.execute("SELECT value FROM test WHERE id = 1;")
        val = cur.fetchone()[0]
        print(f"[{name}] Read value = {val!r}")
    except sqlite3.OperationalError as e:
        print(f"[{name}] ERROR: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Demo: Exclusive lock vs. WAL concurrency in SQLite"
    )
    parser.add_argument(
        '--exclusive', action='store_true',
        help='If set, writer uses EXCLUSIVE locking (readers will block)'
    )
    args = parser.parse_args()

    setup_database()

    # Start the writer process
    w = multiprocessing.Process(target=writer, args=(args.exclusive,))
    w.start()

    # Give writer a moment to acquire its lock
    time.sleep(1)

    # Start a few readers concurrently
    readers = []
    for i in range(3):
        p = multiprocessing.Process(target=reader, args=(f"Reader#{i+1}",))
        readers.append(p)
        p.start()
        time.sleep(0.2)  # stagger the readers slightly

    # Wait for all to finish
    for p in readers:
        p.join()
    w.join()

    # Final read after writer is done
    print("\n[Main] Final read after writer commits:")
    reader("FinalReader")
