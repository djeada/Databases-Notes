"""Demonstrate SQL injection and parameter binding with an in-memory database.

This script is intentionally safe to run: it uses only an in-memory SQLite
database populated with synthetic users. The "attack" changes only a SELECT
predicate and cannot reach an external system.

Run:
    python scripts/security/sql_injection_demo.py
"""

from __future__ import annotations

import sqlite3


def seed_database() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.execute(
        """
        CREATE TABLE users (
            user_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            role TEXT NOT NULL
        )
        """
    )
    connection.executemany(
        "INSERT INTO users (username, role) VALUES (?, ?)",
        [
            ("alice", "user"),
            ("bob", "user"),
            ("carol", "admin"),
        ],
    )
    return connection


def unsafe_lookup(connection: sqlite3.Connection, username: str):
    query = (
        "SELECT user_id, username, role "
        f"FROM users WHERE username = '{username}'"
    )
    print("Unsafe SQL:")
    print(" ", query)
    return connection.execute(query).fetchall()


def safe_lookup(connection: sqlite3.Connection, username: str):
    query = (
        "SELECT user_id, username, role "
        "FROM users WHERE username = ?"
    )
    return connection.execute(query, (username,)).fetchall()


def safe_sort(
    connection: sqlite3.Connection,
    requested_sort: str,
):
    allowed_columns = {
        "name": "username",
        "role": "role",
    }
    try:
        sort_column = allowed_columns[requested_sort]
    except KeyError as exc:
        raise ValueError("unsupported sort option") from exc

    query = (
        "SELECT user_id, username, role "
        f"FROM users ORDER BY {sort_column}, user_id"
    )
    return connection.execute(query).fetchall()


def main() -> None:
    connection = seed_database()

    payload = "alice' OR '1'='1"

    print(f"Input value: {payload!r}")
    print()

    unsafe_rows = unsafe_lookup(connection, payload)
    print(f"Unsafe result count: {len(unsafe_rows)}")
    print("Unsafe rows:", unsafe_rows)
    print()

    safe_rows = safe_lookup(connection, payload)
    print(f"Parameterized result count: {len(safe_rows)}")
    print("Parameterized rows:", safe_rows)
    print()

    print("Safe dynamic identifier selection:")
    print(safe_sort(connection, "name"))


if __name__ == "__main__":
    main()
