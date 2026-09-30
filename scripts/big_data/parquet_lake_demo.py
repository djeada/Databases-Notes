"""Write and query a small partitioned Parquet data lake with DuckDB.

Run from the repository root:
    python -m pip install -r scripts/big_data/requirements.txt
    python scripts/big_data/parquet_lake_demo.py
"""

from pathlib import Path
from tempfile import TemporaryDirectory

import duckdb


def main() -> None:
    con = duckdb.connect(":memory:")

    con.execute("""
        CREATE TABLE events (
            event_time TIMESTAMP,
            event_date DATE,
            user_id INTEGER,
            event_type VARCHAR,
            revenue DECIMAL(10, 2)
        )
    """)

    con.execute("""
        INSERT INTO events VALUES
            (TIMESTAMP '2026-09-29 10:00:00', DATE '2026-09-29', 101, 'view', 0),
            (TIMESTAMP '2026-09-29 10:01:00', DATE '2026-09-29', 101, 'purchase', 19.95),
            (TIMESTAMP '2026-09-30 09:00:00', DATE '2026-09-30', 205, 'view', 0),
            (TIMESTAMP '2026-09-30 09:02:00', DATE '2026-09-30', 205, 'purchase', 39.00),
            (TIMESTAMP '2026-09-30 09:05:00', DATE '2026-09-30', 101, 'view', 0)
    """)

    with TemporaryDirectory(prefix="duckdb_lake_") as tmpdir:
        lake = Path(tmpdir) / "events"
        lake_sql = lake.as_posix().replace("'", "''")

        con.execute(f"""
            COPY events
            TO '{lake_sql}'
            (FORMAT PARQUET, PARTITION_BY (event_date))
        """)

        print("Partitioned files:")
        for path in sorted(lake.rglob("*.parquet")):
            print(" ", path.relative_to(lake.parent))

        day_glob = (
            lake / "event_date=2026-09-30" / "*.parquet"
        ).as_posix().replace("'", "''")

        rows = con.execute(f"""
            SELECT
                event_type,
                COUNT(*) AS event_count,
                SUM(revenue) AS revenue
            FROM read_parquet('{day_glob}')
            GROUP BY event_type
            ORDER BY event_type
        """).fetchall()

        print("\n2026-09-30:")
        for event_type, event_count, revenue in rows:
            print(
                f"{event_type:<10} count={event_count} "
                f"revenue={revenue:.2f}"
            )


if __name__ == "__main__":
    main()
