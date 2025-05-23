#!/usr/bin/env python3
import sqlite3
import time
import os
from multiprocessing import Process

# Constants
DATABASE = 'isolation_demo.db'

def setup_database():
    """(Re)create the database and initialize one product row."""
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
    with sqlite3.connect(DATABASE) as conn:
        conn.execute("PRAGMA journal_mode = DELETE;")  # default journaling
        conn.execute("""
            CREATE TABLE products (
                id       INTEGER PRIMARY KEY,
                name     TEXT,
                quantity INTEGER
            );
        """)
        conn.execute("""
            INSERT INTO products (id, name, quantity)
            VALUES (1, 'Widget', 100);
        """)
    print("[Setup] Initialized products id=1, quantity=100\n")

def writer():
    """Start a transaction, update without committing until after a delay."""
    conn = sqlite3.connect(DATABASE, isolation_level=None, timeout=10)
    cur = conn.cursor()
    cur.execute("BEGIN IMMEDIATE;")
    print("[Writer] BEGIN IMMEDIATE")
    cur.execute("UPDATE products SET quantity = 200 WHERE id = 1;")
    print("[Writer] Updated quantity to 200 but not yet committed")
    time.sleep(5)  # hold the lock / uncommitted change
    conn.commit()
    print("[Writer] COMMIT")
    conn.close()

def reader(isolated: bool):
    """
    Read quantity from the database.
    If isolated=True, uses default isolation (no dirty reads).
    If isolated=False, sets PRAGMA read_uncommitted=1 to allow dirty reads.
    """
    conn = sqlite3.connect(DATABASE, timeout=10)
    cur = conn.cursor()
    if not isolated:
        cur.execute("PRAGMA read_uncommitted = 1;")
        print("[Reader] PRAGMA read_uncommitted = 1 (dirty reads allowed)")
    else:
        print("[Reader] Default isolation (dirty reads disallowed)")
    # Wait a moment so writer's UPDATE has happened but before COMMIT
    time.sleep(1)
    cur.execute("SELECT quantity FROM products WHERE id = 1;")
    qty = cur.fetchone()[0]
    print(f"[Reader] Read quantity = {qty}")
    conn.close()

if __name__ == '__main__':
    # --- Isolated Transactions Demo ---
    setup_database()
    print("--- Isolation Demo: NO dirty reads ---")
    p_w = Process(target=writer)
    p_r = Process(target=reader, args=(True,))
    p_w.start()
    p_r.start()
    p_w.join()
    p_r.join()

    # --- Non-Isolated (Dirty Reads) Demo ---
    setup_database()
    print("\n--- Non-Isolation Demo: ALLOW dirty reads ---")
    p_w = Process(target=writer)
    p_r = Process(target=reader, args=(False,))
    p_w.start()
    p_r.start()
    p_w.join()
    p_r.join()
