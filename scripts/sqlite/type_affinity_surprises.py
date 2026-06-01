"""
SQLite Type Affinity Surprises

Goal: Demonstrate that SQLite column types are affinities, not rigid storage
      contracts, and that storing numbers as text leads to surprising results.

Concept:
- SQLite will store values even when they do not exactly match the declared type.
- TEXT values sort lexicographically, so numeric-looking strings can sort wrong.
- Numeric affinity columns convert compatible values on insert, producing the
  comparisons most people expect.

Usage:
    python sqlite/type_affinity_surprises.py
"""
import sqlite3


def print_rows(title: str, query: str, conn: sqlite3.Connection) -> None:
    """Print query results with a short heading."""
    print(title)
    for row in conn.execute(query):
        print(f"  {row}")
    print()


if __name__ == "__main__":
    conn = sqlite3.connect(":memory:")
    conn.executescript(
        """
        CREATE TABLE prices_as_text (
            label TEXT,
            price TEXT
        );

        CREATE TABLE prices_as_real (
            label TEXT,
            price REAL
        );
        """
    )

    sample_rows = [
        ("cheap", "2"),
        ("mid", "10"),
        ("expensive", "100"),
        ("bad_import", "oops"),
    ]
    conn.executemany("INSERT INTO prices_as_text (label, price) VALUES (?, ?);", sample_rows)
    conn.executemany("INSERT INTO prices_as_real (label, price) VALUES (?, ?);", sample_rows[:-1])
    conn.commit()

    print_rows(
        "--- Values stored in the TEXT column (notice typeof stays text) ---",
        "SELECT label, price, typeof(price) FROM prices_as_text ORDER BY rowid;",
        conn,
    )

    print_rows(
        "--- ORDER BY on TEXT prices is lexicographic, not numeric ---",
        "SELECT label, price FROM prices_as_text ORDER BY price;",
        conn,
    )

    print_rows(
        "--- Numeric range query on TEXT prices is also lexicographic ---",
        "SELECT label, price FROM prices_as_text WHERE price >= '10' ORDER BY price;",
        conn,
    )

    print_rows(
        "--- REAL affinity converts compatible values to numbers ---",
        "SELECT label, price, typeof(price) FROM prices_as_real ORDER BY price;",
        conn,
    )

    conn.close()
    print("Takeaway: SQLite is flexible, but flexible schemas can hide bad data.")
    print("Store numbers in numeric-affinity columns if you want numeric behavior.")
