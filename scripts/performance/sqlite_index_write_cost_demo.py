"""Measure local insert cost with and without several secondary indexes.

Run:
    python scripts/performance/sqlite_index_write_cost_demo.py

The script uses two temporary SQLite database files and prints local elapsed
time plus file size. It is a teaching example, not a cross-database benchmark.
"""
from __future__ import annotations

import os
import sqlite3
import tempfile
import time


ROW_COUNT = 100_000


def populate(path: str, with_secondary_indexes: bool) -> tuple[float, int]:
    connection = sqlite3.connect(path)
    connection.execute(
        """
        CREATE TABLE events (
            event_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            category TEXT NOT NULL,
            payload TEXT NOT NULL
        )
        """
    )

    if with_secondary_indexes:
        connection.executescript(
            """
            CREATE INDEX idx_events_customer
            ON events(customer_id);

            CREATE INDEX idx_events_status_created
            ON events(status, created_at DESC);

            CREATE INDEX idx_events_category_customer
            ON events(category, customer_id);
            """
        )

    rows = (
        (
            event_id,
            event_id % 5000,
            "open" if event_id % 4 == 0 else "closed",
            event_id,
            f"category-{event_id % 20}",
            f"payload-{event_id}",
        )
        for event_id in range(1, ROW_COUNT + 1)
    )

    started = time.perf_counter()
    connection.executemany(
        """
        INSERT INTO events (
            event_id,
            customer_id,
            status,
            created_at,
            category,
            payload
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    connection.commit()
    elapsed = time.perf_counter() - started
    connection.close()

    return elapsed, os.path.getsize(path)


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        minimal_path = os.path.join(directory, "minimal.db")
        indexed_path = os.path.join(directory, "indexed.db")

        minimal_time, minimal_size = populate(
            minimal_path,
            with_secondary_indexes=False,
        )
        indexed_time, indexed_size = populate(
            indexed_path,
            with_secondary_indexes=True,
        )

        print(f"Rows inserted per database: {ROW_COUNT}")
        print("\nMinimal indexing:")
        print(f"  insert time: {minimal_time:.6f} s")
        print(f"  file size:   {minimal_size / 1024 / 1024:.2f} MiB")

        print("\nThree secondary indexes:")
        print(f"  insert time: {indexed_time:.6f} s")
        print(f"  file size:   {indexed_size / 1024 / 1024:.2f} MiB")

        if minimal_time > 0:
            print(
                "\nLocal insert-time ratio "
                f"(indexed / minimal): {indexed_time / minimal_time:.2f}x"
            )
        if minimal_size > 0:
            print(
                "Local file-size ratio "
                f"(indexed / minimal): {indexed_size / minimal_size:.2f}x"
            )


if __name__ == "__main__":
    main()
