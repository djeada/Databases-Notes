"""Compare deep OFFSET pagination with keyset continuation in SQLite.

Run:
    python scripts/performance/sqlite_pagination_demo.py

The dataset is synthetic. Treat the printed timings as local measurements only.
"""
from __future__ import annotations

import sqlite3
import time


ROW_COUNT = 200_000
PAGE_SIZE = 100
OFFSET = 150_000

OFFSET_QUERY = """
SELECT event_id, created_bucket, payload
FROM events
ORDER BY created_bucket DESC, event_id DESC
LIMIT ? OFFSET ?
"""

KEYSET_QUERY = """
SELECT event_id, created_bucket, payload
FROM events
WHERE created_bucket < ?
   OR (created_bucket = ? AND event_id < ?)
ORDER BY created_bucket DESC, event_id DESC
LIMIT ?
"""


def measure(
    connection: sqlite3.Connection,
    query: str,
    params: tuple,
    repeats: int,
) -> float:
    started = time.perf_counter()
    for _ in range(repeats):
        connection.execute(query, params).fetchall()
    return time.perf_counter() - started


def print_plan(
    connection: sqlite3.Connection,
    label: str,
    query: str,
    params: tuple,
) -> None:
    print(f"\n{label}")
    rows = connection.execute(
        "EXPLAIN QUERY PLAN " + query,
        params,
    ).fetchall()
    for row in rows:
        print(" ", row)


def main() -> None:
    connection = sqlite3.connect(":memory:")
    connection.execute(
        """
        CREATE TABLE events (
            event_id INTEGER PRIMARY KEY,
            created_bucket INTEGER NOT NULL,
            payload TEXT NOT NULL
        )
        """
    )

    connection.executemany(
        """
        INSERT INTO events(event_id, created_bucket, payload)
        VALUES (?, ?, ?)
        """,
        (
            (event_id, event_id // 10, f"event-{event_id}")
            for event_id in range(1, ROW_COUNT + 1)
        ),
    )
    connection.execute(
        """
        CREATE INDEX idx_events_created_id
        ON events(created_bucket DESC, event_id DESC)
        """
    )
    connection.commit()

    # The item just before OFFSET=150000 in descending event_id order is 50001.
    cursor_event_id = ROW_COUNT - OFFSET + 1
    cursor_bucket = cursor_event_id // 10

    offset_params = (PAGE_SIZE, OFFSET)
    keyset_params = (
        cursor_bucket,
        cursor_bucket,
        cursor_event_id,
        PAGE_SIZE,
    )

    offset_rows = connection.execute(
        OFFSET_QUERY,
        offset_params,
    ).fetchall()
    keyset_rows = connection.execute(
        KEYSET_QUERY,
        keyset_params,
    ).fetchall()

    print_plan(
        connection,
        "OFFSET plan:",
        OFFSET_QUERY,
        offset_params,
    )
    print_plan(
        connection,
        "Keyset plan:",
        KEYSET_QUERY,
        keyset_params,
    )

    print("\nSame page returned:", offset_rows == keyset_rows)
    print("First row:", offset_rows[0] if offset_rows else None)
    print("Last row:", offset_rows[-1] if offset_rows else None)

    repeats = 40
    offset_time = measure(
        connection,
        OFFSET_QUERY,
        offset_params,
        repeats,
    )
    keyset_time = measure(
        connection,
        KEYSET_QUERY,
        keyset_params,
        repeats,
    )

    print(f"\n{repeats} deep OFFSET pages: {offset_time:.6f} s")
    print(f"{repeats} keyset pages:     {keyset_time:.6f} s")
    if keyset_time > 0:
        print(
            "Local speed ratio (OFFSET / keyset): "
            f"{offset_time / keyset_time:.2f}x"
        )

    connection.close()


if __name__ == "__main__":
    main()
