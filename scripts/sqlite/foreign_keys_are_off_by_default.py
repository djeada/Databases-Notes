"""
SQLite Foreign Keys Are Off By Default

Goal: Demonstrate that SQLite does not enforce foreign keys unless the current
      connection enables `PRAGMA foreign_keys = ON`.

Concept:
- Foreign key declarations alone do not enable enforcement in SQLite.
- The setting is per connection, so every new connection must enable it again.
- Without the pragma, invalid child rows can be inserted silently.

Usage:
    python sqlite/foreign_keys_are_off_by_default.py
"""
import sqlite3


SCHEMA = """
CREATE TABLE authors (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE books (
    id INTEGER PRIMARY KEY,
    author_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    FOREIGN KEY (author_id) REFERENCES authors(id)
);
"""


def try_invalid_insert(enforce_foreign_keys: bool) -> None:
    """Attempt the same invalid insert with and without enforcement."""
    conn = sqlite3.connect(":memory:")
    conn.execute(f"PRAGMA foreign_keys = {'ON' if enforce_foreign_keys else 'OFF'};")
    conn.executescript(SCHEMA)

    status = conn.execute("PRAGMA foreign_keys;").fetchone()[0]
    print(f"foreign_keys pragma = {status}")

    try:
        conn.execute(
            "INSERT INTO books (author_id, title) VALUES (?, ?);",
            (999, "Ghost Writer"),
        )
        conn.commit()
        print("Inserted a book pointing at missing author_id=999")
    except sqlite3.IntegrityError as exc:
        print(f"Insert failed as expected: {exc}")
    finally:
        count = conn.execute("SELECT COUNT(*) FROM books;").fetchone()[0]
        print(f"books row count = {count}\n")
        conn.close()


if __name__ == "__main__":
    print("--- Connection A: pragma left OFF ---")
    try_invalid_insert(enforce_foreign_keys=False)

    print("--- Connection B: pragma turned ON ---")
    try_invalid_insert(enforce_foreign_keys=True)

    print("Takeaway: in SQLite, declaring a foreign key is not enough.")
    print("Enable PRAGMA foreign_keys = ON on every connection that should enforce it.")
