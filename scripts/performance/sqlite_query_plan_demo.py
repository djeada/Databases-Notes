"""Show how a composite index changes SQLite's plan and local timing.

Run:
    python scripts/performance/sqlite_query_plan_demo.py

The timings are intentionally presented as local measurements, not universal
benchmarks.
"""
from __future__ import annotations

import sqlite3
import time


QUERY = """
SELECT order_id, order_seq
FROM orders
WHERE customer_id = ?
  AND status = ?
ORDER BY order_seq DESC, order_id DESC
LIMIT 20
"""


def print_plan(connection: sqlite3.Connection, label: str) -> None:
    plan = connection.execute(
        "EXPLAIN QUERY PLAN " + QUERY,
        (42, "open"),
    ).fetchall()
    print(f"\n{label}")
    for row in plan:
        print(" ", row)


def measure(connection: sqlite3.Connection, repeats: int = 300) -> float:
    started = time.perf_counter()
    for _ in range(repeats):
        connection.execute(QUERY, (42, "open")).fetchall()
    return time.perf_counter() - started


def main() -> None:
    connection = sqlite3.connect(":memory:")
    connection.execute(
        """
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            order_seq INTEGER NOT NULL,
            total_cents INTEGER NOT NULL
        )
        """
    )

    rows = []
    for order_id in range(1, 120_001):
        customer_id = order_id % 1000
        status = "open" if (order_id // 1000) % 3 == 0 else "closed"
        rows.append(
            (
                order_id,
                customer_id,
                status,
                order_id,
                1000 + (order_id % 50_000),
            )
        )

    connection.executemany(
        """
        INSERT INTO orders (
            order_id,
            customer_id,
            status,
            order_seq,
            total_cents
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        rows,
    )
    connection.commit()

    print_plan(connection, "Plan before composite index:")
    before = measure(connection)

    connection.execute(
        """
        CREATE INDEX idx_orders_customer_status_seq
        ON orders (
            customer_id,
            status,
            order_seq DESC,
            order_id DESC
        )
        """
    )
    connection.commit()

    print_plan(connection, "Plan after composite index:")
    after = measure(connection)

    result = connection.execute(QUERY, (42, "open")).fetchall()

    print("\nResult rows:", len(result))
    print(f"Repeated lookup time before index: {before:.6f} s")
    print(f"Repeated lookup time after index:  {after:.6f} s")
    if after > 0:
        print(f"Local speed ratio (before / after): {before / after:.2f}x")

    connection.close()


if __name__ == "__main__":
    main()
