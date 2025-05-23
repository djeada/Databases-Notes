#!/usr/bin/env python3
import sqlite3
import time
import uuid
import os
from multiprocessing import Process

# Constants
DATABASE = 'lock_demo.db'
MAX_RETRIES = 3
RETRY_DELAY = 1

class VersionConflict(Exception):
    pass

def setup_database():
    """Create the products table and initialize one row."""
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
    with sqlite3.connect(DATABASE) as conn:
        # Use WAL so readers aren’t blocked during pessimistic locks
        conn.execute("PRAGMA journal_mode = WAL;")
        conn.execute("""
            CREATE TABLE products (
                id       INTEGER PRIMARY KEY,
                name     TEXT,
                quantity INTEGER,
                version  INTEGER
            );
        """)
        conn.execute("""
            INSERT INTO products (id, name, quantity, version)
            VALUES (1, 'Widget', 100, 1);
        """)
    print("[Setup] Database initialized.\n")

def pessimistic_transaction(name, delay_before_update=2):
    """Pessimistic: BEGIN IMMEDIATE to acquire RESERVED lock up-front."""
    try:
        with sqlite3.connect(DATABASE, timeout=10) as conn:
            conn.execute("PRAGMA journal_mode = WAL;")
            cur = conn.cursor()
            print(f"{name}: BEGIN IMMEDIATE")
            cur.execute("BEGIN IMMEDIATE;")
            cur.execute("SELECT quantity FROM products WHERE id = 1;")
            qty = cur.fetchone()[0]
            print(f"{name}: read quantity = {qty}")
            time.sleep(delay_before_update)
            new_qty = qty - 10
            cur.execute("UPDATE products SET quantity = ? WHERE id = 1;", (new_qty,))
            print(f"{name}: updated quantity to {new_qty}")
        print(f"{name}: COMMIT\n")
    except sqlite3.OperationalError as e:
        print(f"{name}: OperationalError - {e}\n")

def optimistic_transaction(name, delay_before_update=2):
    """Optimistic: read-version, check-and-set, retry on conflict."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            with sqlite3.connect(DATABASE, timeout=5) as conn:
                conn.execute("PRAGMA journal_mode = WAL;")
                cur = conn.cursor()
                print(f"{name}: BEGIN (attempt {attempt})")
                cur.execute("BEGIN;")
                cur.execute("SELECT quantity, version FROM products WHERE id = 1;")
                row = cur.fetchone()
                if row is None:
                    print(f"{name}: no row found, aborting\n")
                    return
                qty, ver = row
                print(f"{name}: read quantity = {qty}, version = {ver}")
                time.sleep(delay_before_update)
                new_qty = qty - 10
                new_ver = ver + 1
                cur.execute("""
                    UPDATE products
                       SET quantity = ?, version = ?
                     WHERE id = 1 AND version = ?;
                """, (new_qty, new_ver, ver))
                if cur.rowcount == 0:
                    raise VersionConflict()
                print(f"{name}: updated to quantity = {new_qty}, version = {new_ver}")
            print(f"{name}: COMMIT\n")
            return
        except VersionConflict:
            print(f"{name}: version conflict, retrying after {RETRY_DELAY}s...\n")
            time.sleep(RETRY_DELAY)
        except sqlite3.OperationalError as e:
            print(f"{name}: OperationalError - {e}\n")
            return
    print(f"{name}: failed after {MAX_RETRIES} attempts\n")

def display_final_state():
    """Show the final quantity and version."""
    with sqlite3.connect(DATABASE) as conn:
        cur = conn.cursor()
        cur.execute("SELECT quantity, version FROM products WHERE id = 1;")
        row = cur.fetchone()
    if row:
        qty, ver = row
        print(f"[Final State] quantity = {qty}, version = {ver}\n")
    else:
        print("[Final State] Product not found\n")

if __name__ == '__main__':
    # Pessimistic locking demo
    setup_database()
    print("--- Pessimistic Locking Demo ---")
    p1 = Process(target=pessimistic_transaction, args=("ProcA", 4))
    p2 = Process(target=pessimistic_transaction, args=("ProcB", 0))
    p1.start()
    time.sleep(0.5)  # ProcA grabs RESERVED lock first
    p2.start()
    p1.join()
    p2.join()
    display_final_state()

    # Optimistic locking demo
    setup_database()
    print("--- Optimistic Locking Demo ---")
    o1 = Process(target=optimistic_transaction, args=("ProcX", 3))
    o2 = Process(target=optimistic_transaction, args=("ProcY", 1))
    o1.start()
    time.sleep(0.5)
    o2.start()
    o1.join()
    o2.join()
    display_final_state()
