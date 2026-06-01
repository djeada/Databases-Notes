"""
SQL UPDATE Query Generator

Goal: Programmatically generate parameterized SQL UPDATE statements with SET
      clauses and WHERE conditions, demonstrating safe data modification.

Use Case: Useful for data transformation scripts, API update endpoints, or admin tools.

Note: This implementation returns a SQL template plus parameters, which is the
safe pattern supported by Python DB-API drivers.

Usage:
    python update_query.py
"""
from typing import Dict, List, Tuple
import re

IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def validate_identifier(identifier: str, kind: str) -> str:
    """Allow only simple SQL identifiers in this educational example."""
    if not IDENTIFIER_RE.fullmatch(identifier):
        raise ValueError(f"Invalid {kind}: {identifier!r}")
    return identifier


def generate_update_query(
    table_name: str, data: Dict[str, object], conditions: List[Tuple[str, object]]
) -> Tuple[str, Tuple[object, ...]]:
    """
    Generate a parameterized SQL UPDATE query for a given table name, data, and conditions.

    This function constructs a SQL UPDATE query string to update specified columns
    with provided values in a given table, based on certain conditions.

    Args:
    table_name (str): The name of the table to update.
    data (Dict[str, object]): A dictionary where keys are column names and values are the new values to be set.
    conditions (List[Tuple[str, object]]): A list of conditions for the update, with each condition represented as a (column, value) tuple.

    Returns:
    Tuple[str, Tuple[object, ...]]: A SQL template string and parameters tuple.

    Example:
    >>> generate_update_query(
            "users",
            {"email": "john.updated@example.com", "last_name": "UpdatedDoe"},
            [("first_name", "John"), ("last_name", "Doe")]
        )
    (
        "UPDATE users SET email = ?, last_name = ? WHERE first_name = ? AND last_name = ?;",
        ("john.updated@example.com", "UpdatedDoe", "John", "Doe"),
    )
    """
    if not data:
        raise ValueError("UPDATE requires at least one column to modify")
    if not conditions:
        raise ValueError("UPDATE requires WHERE conditions in this example")

    safe_table_name = validate_identifier(table_name, "table name")
    set_clause = ", ".join(
        f"{validate_identifier(column, 'column name')} = ?" for column in data
    )
    where_clause = " AND ".join(
        f"{validate_identifier(column, 'column name')} = ?" for column, _ in conditions
    )
    params = tuple(data.values()) + tuple(value for _, value in conditions)

    query = f"UPDATE {safe_table_name} SET {set_clause} WHERE {where_clause};"

    return query, params

if __name__ == "__main__":
    update_data = {
        "email": "john.updated@example.com",
        "last_name": "UpdatedDoe"
    }
    update_conditions = [
        ("first_name", "John"),
        ("last_name", "Doe")
    ]

    query, params = generate_update_query("users", update_data, update_conditions)
    print(query)
    print(params)
