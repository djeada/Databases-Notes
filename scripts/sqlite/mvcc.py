#!/usr/bin/env python3
"""
Multi-Version Concurrency Control (MVCC) Versioning Demo

Goal: Demonstrate a simplified MVCC-style versioning approach using SQLite
      where multiple versions of the same row can exist and stale writers are
      rejected cleanly.

Concept:
- Each update creates a new row version with a unique version_id.
- Versions have valid_from and valid_to timestamps.
- A worker first reads a snapshot, then later tries to promote that snapshot
  into a new version.
- The final write uses a conditional UPDATE to ensure the original version is
  still current. If another worker updated it first, the stale worker aborts.
- SQLite still allows only one writer at a time, so the long "thinking" phase
  stays outside the write transaction to focus on MVCC conflict detection.

Usage:
    python sqlite/mvcc.py
"""
import os
import sqlite3
import time
import uuid
from multiprocessing import Process

DB = "mvcc.db"
TBL = "products_versioned"
SENTINEL = 1e12  # "infinite" timestamp

def setup():
    if os.path.exists(DB):
        os.remove(DB)
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("PRAGMA journal_mode = WAL;")
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
    conn = sqlite3.connect(DB, isolation_level=None, timeout=10)
    c = conn.cursor()
    c.execute("PRAGMA journal_mode = WAL;")

    # 1) read a snapshot of the current version
    start_ts = time.time()
    print(f"[{label}] snapshot at {start_ts:.3f}")

    # 2) read the currently visible version
    c.execute(f"""
        SELECT quantity, version_id
        FROM {TBL}
        WHERE id=1 AND valid_from <= ? AND valid_to > ?
        ORDER BY valid_from DESC LIMIT 1;
    """, (start_ts, start_ts))
    row = c.fetchone()
    if not row:
        print(f"[{label}] nothing to read!")
        conn.close()
        return
    qty, vid = row
    print(f"[{label}] read qty={qty} vid={vid}")

    time.sleep(sleep_secs)  # simulate work outside the write transaction

    # 3) attempt to expire the old version and insert a new one
    now = time.time()
    c.execute("BEGIN IMMEDIATE;")
    updated = c.execute(
        f"""
        UPDATE {TBL}
           SET valid_to=?
         WHERE id=1
           AND version_id=?
           AND valid_to={SENTINEL};
        """,
        (now, vid),
    ).rowcount

    if updated != 1:
        print(f"[{label}] ABORT: snapshot is stale")
        c.execute("ROLLBACK;")
        conn.close()
        return

    new_qty = qty + delta
    c.execute(
        f"""
        INSERT INTO {TBL}(id,name,quantity,version_id,valid_from)
        VALUES(1,'Widget',?, ?, ?);
        """,
        (new_qty, str(uuid.uuid4()), now),
    )
    c.execute("COMMIT;")
    print(f"[{label}] COMMIT new_qty={new_qty}")
    conn.close()

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
