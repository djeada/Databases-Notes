"""
SQLite INTEGER PRIMARY KEY vs AUTOINCREMENT

Goal: Show that `INTEGER PRIMARY KEY` already auto-generates row IDs and that
      `AUTOINCREMENT` mainly changes reuse semantics while adding overhead.

Concept:
- `INTEGER PRIMARY KEY` aliases the hidden rowid and auto-generates IDs.
- Deleting the highest rowid lets SQLite reuse that value later.
- `AUTOINCREMENT` prevents reuse of old rowids, but updates `sqlite_sequence`
  and is usually unnecessary.

Usage:
    python sqlite/integer_primary_key_vs_autoincrement.py
"""
import sqlite3
import time


BENCHMARK_ROWS = 5_000


def show_id_reuse() -> None:
    """Compare ID reuse behavior after deleting the highest row."""
    conn = sqlite3.connect(":memory:")
    conn.executescript(
        """
        CREATE TABLE plain_ids (
            id INTEGER PRIMARY KEY,
            note TEXT
        );

        CREATE TABLE strict_ids (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note TEXT
        );
        """
    )

    for label in ("first", "second", "third"):
        conn.execute("INSERT INTO plain_ids (note) VALUES (?);", (label,))
        conn.execute("INSERT INTO strict_ids (note) VALUES (?);", (label,))
    conn.commit()

    conn.execute("DELETE FROM plain_ids WHERE id = 3;")
    conn.execute("DELETE FROM strict_ids WHERE id = 3;")
    conn.commit()

    plain_cursor = conn.execute(
        "INSERT INTO plain_ids (note) VALUES ('replacement');"
    )
    strict_cursor = conn.execute(
        "INSERT INTO strict_ids (note) VALUES ('replacement');"
    )
    plain_id = plain_cursor.lastrowid
    strict_id = strict_cursor.lastrowid
    conn.commit()

    print("--- ID reuse after deleting the highest row ---")
    print(f"INTEGER PRIMARY KEY reused id {plain_id}")
    print(f"AUTOINCREMENT generated id {strict_id}\n")
    conn.close()


def benchmark_insert_speed() -> None:
    """Measure the small but real extra work done by AUTOINCREMENT."""
    conn = sqlite3.connect(":memory:")
    conn.executescript(
        """
        CREATE TABLE plain_bench (
            id INTEGER PRIMARY KEY,
            payload TEXT
        );

        CREATE TABLE auto_bench (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payload TEXT
        );
        """
    )

    started = time.perf_counter()
    for _ in range(BENCHMARK_ROWS):
        conn.execute("INSERT INTO plain_bench (payload) VALUES ('x');")
    conn.commit()
    plain_time = time.perf_counter() - started

    started = time.perf_counter()
    for _ in range(BENCHMARK_ROWS):
        conn.execute("INSERT INTO auto_bench (payload) VALUES ('x');")
    conn.commit()
    auto_time = time.perf_counter() - started

    print(f"Inserted {BENCHMARK_ROWS:,} rows with INTEGER PRIMARY KEY in {plain_time:.4f}s")
    print(f"Inserted {BENCHMARK_ROWS:,} rows with AUTOINCREMENT in {auto_time:.4f}s")
    print("AUTOINCREMENT is usually slower because SQLite must maintain sqlite_sequence.\n")
    conn.close()


if __name__ == "__main__":
    show_id_reuse()
    benchmark_insert_speed()
    print("Takeaway: prefer INTEGER PRIMARY KEY unless you specifically need")
    print("a guarantee that old rowids will never be reused.")
