"""Compare local SQLite storage cost for narrow and wide secondary keys.

Run:
    python scripts/indexing/sqlite_btree_growth_demo.py

This is a teaching exercise. File/page sizes are local SQLite measurements, not
a universal database benchmark.
"""
from __future__ import annotations

import os
import sqlite3
import tempfile


ROW_COUNT = 100_000


def create_database(path: str, index_kind: str) -> tuple[int, int, int]:
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA page_size = 4096")
    connection.execute(
        """
        CREATE TABLE events (
            event_id INTEGER PRIMARY KEY,
            narrow_key INTEGER NOT NULL,
            wide_key TEXT NOT NULL,
            payload TEXT NOT NULL
        )
        """
    )

    connection.executemany(
        """
        INSERT INTO events(event_id, narrow_key, wide_key, payload)
        VALUES (?, ?, ?, ?)
        """,
        (
            (
                event_id,
                event_id % 10_000,
                f"tenant-{event_id % 10_000:05d}-"
                f"customer-{event_id:012d}-region-eu",
                f"payload-{event_id}",
            )
            for event_id in range(1, ROW_COUNT + 1)
        ),
    )

    if index_kind == "narrow":
        connection.execute(
            "CREATE INDEX idx_events_narrow ON events(narrow_key)"
        )
    elif index_kind == "wide":
        connection.execute(
            "CREATE INDEX idx_events_wide ON events(wide_key)"
        )
    elif index_kind != "none":
        raise ValueError(index_kind)

    connection.commit()
    page_count = connection.execute("PRAGMA page_count").fetchone()[0]
    page_size = connection.execute("PRAGMA page_size").fetchone()[0]
    connection.close()

    return page_count, page_size, os.path.getsize(path)


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        results = {}
        for kind in ("none", "narrow", "wide"):
            path = os.path.join(directory, f"{kind}.db")
            results[kind] = create_database(path, kind)

        base_pages, page_size, base_bytes = results["none"]

        print(f"Rows per database: {ROW_COUNT}")
        print(f"SQLite page size: {page_size} bytes")

        for kind in ("none", "narrow", "wide"):
            pages, _, size_bytes = results[kind]
            print(f"\n{kind}:")
            print(f"  page count: {pages}")
            print(f"  file size:  {size_bytes / 1024 / 1024:.2f} MiB")

        narrow_extra = results["narrow"][2] - base_bytes
        wide_extra = results["wide"][2] - base_bytes

        print("\nApproximate file growth over the no-secondary-index database:")
        print(f"  narrow integer index: {narrow_extra / 1024 / 1024:.2f} MiB")
        print(f"  wide text index:      {wide_extra / 1024 / 1024:.2f} MiB")

        if narrow_extra > 0:
            print(
                "  wide/narrow growth ratio: "
                f"{wide_extra / narrow_extra:.2f}x"
            )

        print(
            f"\nBaseline pages (table only): {base_pages}. "
            "Wider index entries usually require more index pages."
        )


if __name__ == "__main__":
    main()
