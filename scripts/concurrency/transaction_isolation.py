#!/usr/bin/env python3
"""
Transaction Isolation Demo

Goal: Demonstrate transaction isolation levels in SQLite using Write-Ahead Logging (WAL).

Concepts Demonstrated:
1. Snapshot Isolation: Readers see a consistent snapshot from when their transaction began,
   preventing dirty reads even if a writer updates data.
   
2. Dirty Reads: When using shared cache mode with read_uncommitted pragma, readers can
   see uncommitted changes from concurrent transactions.

Usage:
    python transaction_isolation.py
"""
import sqlite3, threading, time, os

DB = 'isolation_demo.db'

def cleanup():
    # Remove main DB and any WAL/SHM files
    for suffix in ('', '-wal', '-shm'):
        try:
            os.remove(DB + suffix)
        except FileNotFoundError:
            pass

def setup_db_journal(journal):
    """Initialize a fresh DB with the given journal_mode and quantity=100."""
    cleanup()
    conn = sqlite3.connect(DB)
    # Set journal mode (WAL in both demos)
    conn.execute(f"PRAGMA journal_mode = {journal};")
    conn.execute("DROP TABLE IF EXISTS products;")
    conn.execute("""
        CREATE TABLE products (
            id       INTEGER PRIMARY KEY,
            quantity INTEGER
        );
    """)
    conn.execute("INSERT INTO products (id, quantity) VALUES (1, 100);")
    conn.commit()
    conn.close()
    print(f"\n[Setup: journal_mode={journal}] initialized quantity=100")

def isolation_demo():
    print("\n--- Isolation Demo (WAL): NO dirty reads ---")
    setup_db_journal('WAL')

    def writer():
        conn = sqlite3.connect(DB, isolation_level=None)
        cur = conn.cursor()
        # Deferred transaction: snapshot taken at BEGIN
        cur.execute("BEGIN;")
        cur.execute("UPDATE products SET quantity = 200 WHERE id = 1;")
        print("[Writer] updated to 200 but NOT yet committed")
        time.sleep(2)
        conn.commit()
        print("[Writer] committed")
        conn.close()

    def reader():
        conn = sqlite3.connect(DB, isolation_level=None)
        cur = conn.cursor()
        # Start snapshot BEFORE writer updates
        cur.execute("BEGIN;")
        print("[Reader] began snapshot transaction")
        time.sleep(3)
        qty = cur.execute("SELECT quantity FROM products WHERE id = 1;").fetchone()[0]
        print(f"[Reader] read quantity = {qty}  (should be 100)")
        conn.rollback()  # end the transaction
        conn.close()

    t_r = threading.Thread(target=reader)
    t_w = threading.Thread(target=writer)

    t_r.start()
    time.sleep(1)  # ensure reader has its snapshot open
    t_w.start()

    t_w.join()
    t_r.join()

    final_qty = sqlite3.connect(DB).execute(
        "SELECT quantity FROM products WHERE id = 1;"
    ).fetchone()[0]
    print(f"[Final State] quantity = {final_qty}")

def dirty_read_demo():
    print("\n--- Dirty-Read Demo (WAL + shared cache): ALLOW dirty reads ---")
    setup_db_journal('WAL')

    # Use a URI to enable shared cache
    uri = f'file:{DB}?cache=shared'

    def writer():
        conn = sqlite3.connect(uri, uri=True, isolation_level=None)
        cur = conn.cursor()
        cur.execute("BEGIN;")
        cur.execute("UPDATE products SET quantity = 200 WHERE id = 1;")
        print("[Writer] updated to 200 but NOT yet committed")
        time.sleep(2)
        conn.commit()
        print("[Writer] committed")
        conn.close()

    def reader():
        conn = sqlite3.connect(uri, uri=True, isolation_level=None)
        cur = conn.cursor()
        # Allow dirty reads
        cur.execute("PRAGMA read_uncommitted = 1;")
        time.sleep(1)
        qty = cur.execute("SELECT quantity FROM products WHERE id = 1;").fetchone()[0]
        print(f"[Reader] read quantity = {qty}  (dirty read of 200)")
        conn.close()

    t_w = threading.Thread(target=writer)
    t_r = threading.Thread(target=reader)

    t_w.start()
    t_r.start()

    t_w.join()
    t_r.join()

    final_qty = sqlite3.connect(DB).execute(
        "SELECT quantity FROM products WHERE id = 1;"
    ).fetchone()[0]
    print(f"[Final State] quantity = {final_qty}")

if __name__ == "__main__":
    isolation_demo()
    dirty_read_demo()
    print("\nDone.")
