"""
PostgreSQL Transactional DDL Demo

Goal: Demonstrate that PostgreSQL DDL participates in transactions and can be
      rolled back together with other changes.

Concept:
- CREATE TABLE, ALTER TABLE, and many other DDL statements are transactional.
- This is different from MySQL, where DDL often causes implicit commits.
- PostgreSQL lets you test schema changes safely before deciding to commit.

Prerequisites:
- PostgreSQL must be running and accessible
- Use scripts/setup/start_postgres.sh to start a local PostgreSQL instance

Usage:
    python postgres/transactional_ddl.py
"""
import psycopg2


DSN = "dbname=test user=demo password=secret host=localhost port=5432"


def table_exists(conn, table_name: str) -> bool:
    """Return True when the table is visible in the current schema."""
    with conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s);", (f"public.{table_name}",))
        return cur.fetchone()[0] is not None


def column_exists(conn, table_name: str, column_name: str) -> bool:
    """Return True when a column exists in the table."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = %s
                  AND column_name = %s
            );
            """,
            (table_name, column_name),
        )
        return cur.fetchone()[0]


if __name__ == "__main__":
    try:
        conn = psycopg2.connect(DSN)
    except psycopg2.OperationalError as exc:
        print(f"✗ Error connecting to PostgreSQL: {exc}")
        raise SystemExit(1)

    with conn:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS ddl_tx_demo;")
        conn.commit()

        try:
            print("--- Transaction 1: CREATE TABLE, then roll it back ---")
            with conn.cursor() as cur:
                cur.execute("BEGIN;")
                cur.execute("CREATE TABLE ddl_tx_demo (id INT PRIMARY KEY, note TEXT);")
                print(f"Inside T1, table exists: {table_exists(conn, 'ddl_tx_demo')}")
                cur.execute("ROLLBACK;")

            print(f"After rollback, table exists: {table_exists(conn, 'ddl_tx_demo')}\n")

            print("--- Transaction 2: CREATE TABLE and commit ---")
            with conn.cursor() as cur:
                cur.execute("BEGIN;")
                cur.execute("CREATE TABLE ddl_tx_demo (id INT PRIMARY KEY, note TEXT);")
                cur.execute("COMMIT;")

            print(f"After commit, table exists: {table_exists(conn, 'ddl_tx_demo')}\n")

            print("--- Transaction 3: ALTER TABLE, then roll it back ---")
            with conn.cursor() as cur:
                cur.execute("BEGIN;")
                cur.execute("ALTER TABLE ddl_tx_demo ADD COLUMN extra TEXT;")
                print(f"Inside T3, column exists: {column_exists(conn, 'ddl_tx_demo', 'extra')}")
                cur.execute("ROLLBACK;")

            print(f"After rollback, column exists: {column_exists(conn, 'ddl_tx_demo', 'extra')}\n")
            print("Takeaway: PostgreSQL treats most schema changes as transactional work.")
        finally:
            with conn.cursor() as cur:
                cur.execute("DROP TABLE IF EXISTS ddl_tx_demo;")
            conn.commit()
