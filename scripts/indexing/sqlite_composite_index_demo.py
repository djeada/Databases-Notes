"""Show how composite-index column order changes usable access paths.

Run:
    python scripts/indexing/sqlite_composite_index_demo.py
"""
from __future__ import annotations

import sqlite3


ROW_COUNT = 120_000


QUERIES = {
    "full leading prefix + ordered range": (
        """
        SELECT order_id, order_seq, payload
        FROM orders
        WHERE customer_id = ?
          AND status = ?
          AND order_seq >= ?
        ORDER BY order_seq DESC
        LIMIT 20
        """,
        (42, "open", 10_000),
    ),
    "leading column only": (
        """
        SELECT order_id, order_seq, payload
        FROM orders
        WHERE customer_id = ?
        ORDER BY status, order_seq DESC
        LIMIT 20
        """,
        (42,),
    ),
    "suffix column only": (
        """
        SELECT order_id, order_seq, payload
        FROM orders
        WHERE status = ?
        ORDER BY order_seq DESC
        LIMIT 20
        """,
        ("open",),
    ),
}


def main() -> None:
    connection = sqlite3.connect(":memory:")
    connection.execute(
        """
        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            order_seq INTEGER NOT NULL,
            payload TEXT NOT NULL
        )
        """
    )

    connection.executemany(
        """
        INSERT INTO orders(
            order_id,
            customer_id,
            status,
            order_seq,
            payload
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            (
                order_id,
                order_id % 1000,
                "open" if order_id % 5 == 0 else "closed",
                order_id,
                f"order-{order_id}",
            )
            for order_id in range(1, ROW_COUNT + 1)
        ),
    )

    connection.execute(
        """
        CREATE INDEX idx_orders_customer_status_seq
        ON orders(customer_id, status, order_seq DESC)
        """
    )
    connection.commit()

    print(
        "Composite index: "
        "(customer_id, status, order_seq DESC)"
    )

    for label, (query, params) in QUERIES.items():
        print(f"\n{label}:")
        plan = connection.execute(
            "EXPLAIN QUERY PLAN " + query,
            params,
        ).fetchall()
        for row in plan:
            print(" ", row)

        result = connection.execute(query, params).fetchall()
        print("  result rows:", len(result))

    connection.close()


if __name__ == "__main__":
    main()
