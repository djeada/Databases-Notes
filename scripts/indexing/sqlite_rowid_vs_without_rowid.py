"""Compare a composite key in SQLite rowid and WITHOUT ROWID tables.

Run:
    python scripts/indexing/sqlite_rowid_vs_without_rowid.py

The measurements are local teaching results, not universal claims.
"""
from __future__ import annotations

import os
import sqlite3
import tempfile
import time


ROW_COUNT = 100_000
LOOKUP_REPEATS = 2_000


def build(path: str, without_rowid: bool) -> tuple[int, int]:
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA page_size = 4096")

    suffix = " WITHOUT ROWID" if without_rowid else ""
    connection.execute(
        f"""
        CREATE TABLE inventory (
            warehouse_id INTEGER NOT NULL,
            sku TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            description TEXT NOT NULL,
            PRIMARY KEY (warehouse_id, sku)
        ){suffix}
        """
    )

    connection.executemany(
        """
        INSERT INTO inventory(
            warehouse_id,
            sku,
            quantity,
            description
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            (
                event_id % 100,
                f"SKU-{event_id:010d}",
                event_id % 500,
                f"inventory-row-{event_id}",
            )
            for event_id in range(1, ROW_COUNT + 1)
        ),
    )
    connection.commit()
    pages = connection.execute("PRAGMA page_count").fetchone()[0]
    connection.close()
    return pages, os.path.getsize(path)


def measure(path: str) -> tuple[float, list[tuple]]:
    connection = sqlite3.connect(path)
    query = """
        SELECT quantity, description
        FROM inventory
        WHERE warehouse_id = ?
          AND sku = ?
    """
    params = (42, "SKU-0000050042")

    plan = connection.execute(
        "EXPLAIN QUERY PLAN " + query,
        params,
    ).fetchall()

    started = time.perf_counter()
    for _ in range(LOOKUP_REPEATS):
        connection.execute(query, params).fetchone()
    elapsed = time.perf_counter() - started
    connection.close()

    return elapsed, plan


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        rowid_path = os.path.join(directory, "rowid.db")
        without_path = os.path.join(directory, "without_rowid.db")

        rowid_pages, rowid_size = build(rowid_path, False)
        without_pages, without_size = build(without_path, True)

        rowid_time, rowid_plan = measure(rowid_path)
        without_time, without_plan = measure(without_path)

        print(f"Rows per table: {ROW_COUNT}")
        print(f"Repeated point lookups: {LOOKUP_REPEATS}")

        print("\nRowid table:")
        print("  plan:", rowid_plan)
        print(f"  pages: {rowid_pages}")
        print(f"  file:  {rowid_size / 1024 / 1024:.2f} MiB")
        print(f"  lookup time: {rowid_time:.6f} s")

        print("\nWITHOUT ROWID table:")
        print("  plan:", without_plan)
        print(f"  pages: {without_pages}")
        print(f"  file:  {without_size / 1024 / 1024:.2f} MiB")
        print(f"  lookup time: {without_time:.6f} s")


if __name__ == "__main__":
    main()
