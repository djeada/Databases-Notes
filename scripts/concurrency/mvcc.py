#!/usr/bin/env python3
"""
Multi-Version Concurrency Control (MVCC) Demo

Goal: Demonstrate a simplified MVCC implementation using SQLite where multiple
      versions of the same row can exist, allowing concurrent transactions.

Concept:
- Each row update creates a new version with a unique version_id
- Versions have valid_from and valid_to timestamps
- Transactions read the appropriate version based on their snapshot time
- Conflicts are detected when trying to update a version that's already been updated
- One transaction succeeds, the conflicting one is aborted

Usage:
    python mvcc.py
"""
import sqlite3, time, uuid, os
from multiprocessing import Process

DB = "mvcc.db"
TBL = "products_versioned"
SENTINEL = 1e12  # "infinite" timestamp

def setup():
    if os.path.exists(DB):
        os.remove(DB)
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute(f"""
            CREATE TABLE {TBL} (
                id           INTEGER,
                name         TEXT,
                quantity     INTEGER,
                version_id   TEXT,
                valid_from   REAL,
                valid_to     REAL DEFAULT {SENTINEL},
                PRIMARY KEY(id, version_id)
            );
        """)
        now = time.time()
        c.execute(f"""
            INSERT INTO {TBL}(id,name,quantity,version_id,valid_from)
            VALUES(1,'Widget',100,?,?);
        """, (str(uuid.uuid4()), now))
        conn.commit()

def transaction(label, delta, sleep_secs):
    conn = sqlite3.connect(DB, isolation_level=None)  # autocommit off
    c = conn.cursor()
    # 1) start a snapshot
    c.execute("BEGIN;")
    start_ts = time.time()
    print(f"[{label}] BEGIN at {start_ts:.3f}")

    # 2) read
    c.execute(f"""
        SELECT quantity, version_id
        FROM {TBL}
        WHERE id=1 AND valid_from <= ? AND valid_to > ?
        ORDER BY valid_from DESC LIMIT 1;
    """, (start_ts, start_ts))
    row = c.fetchone()
    if not row:
        print(f"[{label}] nothing to read!")
        c.execute("ROLLBACK;")
        return
    qty, vid = row
    print(f"[{label}] read qty={qty} vid={vid}")

    time.sleep(sleep_secs)  # simulate work

    # 3) attempt to expire & insert new version
    now = time.time()
    # expire *only if* version_id still matches, otherwise conflict
    updated = c.execute(f"""
        UPDATE {TBL}
          SET valid_to=?
        WHERE id=1
          AND version_id=?
          AND valid_to={SENTINEL};
    """, (now, vid)).rowcount

    if updated != 1:
        print(f"[{label}] ABORT: concurrent write detected")
        c.execute("ROLLBACK;")
        return

    new_qty = qty + delta
    c.execute(f"""
        INSERT INTO {TBL}(id,name,quantity,version_id,valid_from)
        VALUES(1,'Widget',?, ?, ?);
    """, (new_qty, str(uuid.uuid4()), now))
    c.execute("COMMIT;")
    print(f"[{label}] COMMIT new_qty={new_qty}")

def show_versions():
    with sqlite3.connect(DB) as conn:
        for row in conn.execute(f"""
            SELECT version_id, quantity, valid_from, valid_to
            FROM {TBL} ORDER BY valid_from;
        """):
            print(row)

if __name__ == "__main__":
    setup()
    # two processes, they’ll run concurrently
    pA = Process(target=transaction, args=("A", +50, 2))
    pB = Process(target=transaction, args=("B", -30, 1))
    pA.start(); pB.start()
    pA.join();  pB.join()

    print("\nAll versions:")
    show_versions()
