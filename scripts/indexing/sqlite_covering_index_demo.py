"""Show the plan difference between a normal and covering SQLite index.

Run:
    python scripts/indexing/sqlite_covering_index_demo.py
"""
from __future__ import annotations

import sqlite3


QUERY = """
SELECT order_seq, total_cents
FROM orders
WHERE customer_id = ?
ORDER BY order_seq DESC
LIMIT 20
"""


def show_plan(connection: sqlite3.Connection, label: str) -> None:
    print(f"\n{label}")
    plan = connection.execute(
        "EXPLAIN QUERY PLAN " + QUERY,
        (42,),
    ).fetchall()
    for row in plan:
        print(" ", row)


def main() -> None:
    connection = sqlite3.connect(":memory:")
    connection.execute(
        """
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            order_seq INTEGER NOT NULL,
            total_cents INTEGER NOT NULL,
            notes TEXT NOT NULL
        )
        """
    )

    connection.executemany(
        """
        INSERT INTO orders(
            order_id,
            customer_id,
            order_seq,
            total_cents,
            notes
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            (
                order_id,
                order_id % 1000,
                order_id,
                1000 + (order_id % 100_000),
                f"notes-{order_id}",
            )
            for order_id in range(1, 100_001)
        ),
    )

    connection.execute(
        """
        CREATE INDEX idx_orders_customer_seq
        ON orders(customer_id, order_seq DESC)
        """
    )
    connection.commit()

    show_plan(
        connection,
        "Filter/order index; total_cents still comes from table row:",
    )

    connection.execute(
        """
        CREATE INDEX idx_orders_customer_seq_total
        ON orders(customer_id, order_seq DESC, total_cents)
        """
    )
    connection.commit()

    show_plan(
        connection,
        "Covering index; selected columns are available from the index:",
    )

    rows = connection.execute(QUERY, (42,)).fetchall()
    print("\nExample result rows:", len(rows))
    print("First result:", rows[0] if rows else None)

    connection.close()


if __name__ == "__main__":
    main()
