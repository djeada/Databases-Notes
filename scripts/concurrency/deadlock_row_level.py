"""
Row-Level Deadlock Demo (PostgreSQL)

Goal: Demonstrate row-level deadlocks in PostgreSQL when two threads try to lock
      the same rows in different orders.

Concept:
- Thread A locks row 1 (FOR UPDATE), then tries to lock row 2
- Thread B locks row 2 (FOR UPDATE), then tries to lock row 1
- PostgreSQL detects the deadlock and aborts one transaction
- The aborted transaction should be retried

Prerequisites:
- PostgreSQL must be running and accessible at the DSN specified below
- Use scripts/setup/start_postgres.sh to start a local PostgreSQL instance

Usage:
    python deadlock_row_level.py
"""
import threading
import time
import psycopg2
from psycopg2 import sql, OperationalError, errors

DSN = "dbname=test user=postgres password=secret host=localhost port=5432"

def setup_db():
    with psycopg2.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                DROP TABLE IF EXISTS deadlock_demo;
                CREATE TABLE deadlock_demo (
                    id   SERIAL PRIMARY KEY,
                    val  TEXT
                );
                INSERT INTO deadlock_demo (val) VALUES ('A'), ('B');
            """)
        conn.commit()
    print("✅ Table created and initialized.")

def cleanup_db():
    with psycopg2.connect(DSN) as conn:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS deadlock_demo;")
        conn.commit()
    print("🧹 Table dropped, cleanup complete.")

def worker(name, first_id, second_id, delay):
    conn = psycopg2.connect(DSN)
    conn.autocommit = False
    cur = conn.cursor()
    try:
        cur.execute("BEGIN;")
        # Lock the first row
        cur.execute(
            sql.SQL("SELECT val FROM deadlock_demo WHERE id = %s FOR UPDATE;"),
            [first_id]
        )
        print(f"{name}: locked row {first_id}")
        
        time.sleep(delay)
        
        # Now try to lock the second row
        print(f"{name}: attempting to lock row {second_id}")
        cur.execute(
            sql.SQL("SELECT val FROM deadlock_demo WHERE id = %s FOR UPDATE;"),
            [second_id]
        )
        print(f"{name}: locked row {second_id} — no deadlock?")
        
        conn.commit()
    except OperationalError as e:
        # Psycopg2 raises a generic OperationalError for deadlocks
        print(f"{name}: DEADLOCK detected! → {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    setup_db()

    # Thread A: locks row 1 then row 2
    t1 = threading.Thread(target=worker, args=("Thread-A", 1, 2, 1))
    # Thread B: locks row 2 then row 1
    t2 = threading.Thread(target=worker, args=("Thread-B", 2, 1, 1))

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    cleanup_db()
    print("🏁 Demo complete.")
