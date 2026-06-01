"""
PostgreSQL Sequences Are Not Rolled Back

Goal: Demonstrate that PostgreSQL sequences keep advancing even when the
      transaction using the generated value rolls back.

Concept:
- `SERIAL` and `GENERATED ... AS IDENTITY` use a sequence behind the scenes.
- Calling `nextval()` is not transactional, so rollbacks do not put sequence
  values back.
- Gaps in IDs are normal and should not be treated as lost data.

Prerequisites:
- PostgreSQL must be running and accessible
- Use scripts/setup/start_postgres.sh to start a local PostgreSQL instance

Usage:
    python postgres/sequences_are_not_rolled_back.py
"""
import psycopg2


DSN = "dbname=test user=demo password=secret host=localhost port=5432"


def show_table(conn, title: str) -> None:
    """Print the current rows in the demo table."""
    with conn.cursor() as cur:
        cur.execute("SELECT id, description FROM sequence_demo ORDER BY id;")
        rows = cur.fetchall()
    print(title)
    for row in rows:
        print(f"  {row}")
    if not rows:
        print("  <no rows>")
    print()


if __name__ == "__main__":
    try:
        conn = psycopg2.connect(DSN)
    except psycopg2.OperationalError as exc:
        print(f"✗ Error connecting to PostgreSQL: {exc}")
        raise SystemExit(1)

    with conn:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS sequence_demo;")
            cur.execute(
                """
                CREATE TABLE sequence_demo (
                    id SERIAL PRIMARY KEY,
                    description TEXT NOT NULL
                );
                """
            )
        conn.commit()

        try:
            print("--- Transaction 1: consume an ID, then roll back ---")
            with conn.cursor() as cur:
                cur.execute("BEGIN;")
                cur.execute(
                    "INSERT INTO sequence_demo (description) VALUES (%s) RETURNING id;",
                    ("rolled back row",),
                )
                rolled_back_id = cur.fetchone()[0]
                print(f"T1 obtained id {rolled_back_id}")
                cur.execute("ROLLBACK;")

            show_table(conn, "Table contents after rollback:")

            print("--- Transaction 2: insert and commit ---")
            with conn.cursor() as cur:
                cur.execute("BEGIN;")
                cur.execute(
                    "INSERT INTO sequence_demo (description) VALUES (%s) RETURNING id;",
                    ("committed row",),
                )
                committed_id = cur.fetchone()[0]
                print(f"T2 obtained id {committed_id}")
                cur.execute("COMMIT;")

            show_table(conn, "Table contents after commit:")

            print("Takeaway: sequence values are not rolled back.")
            print("Gaps in PostgreSQL IDs are expected whenever transactions abort.")
        finally:
            with conn.cursor() as cur:
                cur.execute("DROP TABLE IF EXISTS sequence_demo;")
            conn.commit()
