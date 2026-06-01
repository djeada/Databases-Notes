"""
SQL DELETE Query Generator

Goal: Programmatically generate parameterized SQL DELETE statements with WHERE
      conditions, demonstrating safe deletion.

Use Case: Useful for building data cleanup scripts, admin tools, or API backends.

Note: This implementation returns a SQL template plus parameters, which is the
safe pattern supported by Python DB-API drivers.

Usage:
    python delete.py
"""
from typing import List, Tuple
import re

IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def validate_identifier(identifier: str, kind: str) -> str:
    """Allow only simple SQL identifiers in this educational example."""
    if not IDENTIFIER_RE.fullmatch(identifier):
        raise ValueError(f"Invalid {kind}: {identifier!r}")
    return identifier


def generate_delete_query(
    table_name: str, conditions: List[Tuple[str, object]]
) -> Tuple[str, Tuple[object, ...]]:
    """
    Generate a SQL DELETE query for a given table name and conditions.

    Args:
    table_name (str): The name of the table from which to delete records.
    conditions (List[Tuple[str, object]]): A list of conditions for the deletion, each represented as a (column, value) tuple.

    Returns:
    Tuple[str, Tuple[object, ...]]: A SQL template string and parameters tuple.

    Example:
    >>> generate_delete_query("students", [("name", "John Doe"), ("age", "20")])
    ("DELETE FROM students WHERE name = ? AND age = ?;", ("John Doe", "20"))
    """
    if not conditions:
        raise ValueError("DELETE requires WHERE conditions in this example")

    safe_table_name = validate_identifier(table_name, "table name")
    where_clause = " AND ".join(
        f"{validate_identifier(column, 'column name')} = ?" for column, _ in conditions
    )
    params = tuple(value for _, value in conditions)
    query = f"DELETE FROM {safe_table_name} WHERE {where_clause};"

    return query, params

if __name__ == "__main__":
    delete_conditions = [
        ("name", "John Doe"),
        ("age", "20")
    ]

    query, params = generate_delete_query("students", delete_conditions)
    print(query)
    print(params)
