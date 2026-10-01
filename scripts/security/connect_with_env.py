"""Connect to PostgreSQL without embedding the connection string in source.

This demonstrates configuration injection, not a complete production secret
manager. For production, prefer a secret manager or workload identity when
available.

Run against the repository's local PostgreSQL demo:

    export DATABASE_URL='postgresql://demo:secret@127.0.0.1:5432/test'
    python scripts/security/connect_with_env.py
"""

from __future__ import annotations

import os

import psycopg2


def main() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise SystemExit(
            "DATABASE_URL is required; keep connection secrets outside source code."
        )

    with psycopg2.connect(database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    current_database(),
                    current_user,
                    inet_server_addr()::text,
                    inet_server_port()
                """
            )
            database, user, host, port = cursor.fetchone()

    print("Connected successfully.")
    print(f"database={database}")
    print(f"user={user}")
    print(f"server={host}:{port}")
    print("Password/connection URL intentionally not printed.")


if __name__ == "__main__":
    main()
