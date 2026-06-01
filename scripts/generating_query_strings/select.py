"""
SQL SELECT Query Generator

Goal: Programmatically generate parameterized SQL SELECT statements with column
      selection and optional WHERE conditions.

Use Case: Useful for query builders, reporting tools, or data export utilities.

Note: This implementation returns a SQL template plus parameters, which is the
safe pattern supported by Python DB-API drivers.

Usage:
    python select.py
"""
from typing import List, Tuple
import re

IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def validate_identifier(identifier: str, kind: str) -> str:
    """Allow only simple SQL identifiers in this educational example."""
    if not IDENTIFIER_RE.fullmatch(identifier):
        raise ValueError(f"Invalid {kind}: {identifier!r}")
    return identifier


def generate_select_query(
    table_name: str, columns: List[str], conditions: List[Tuple[str, object]]
) -> Tuple[str, Tuple[object, ...]]:
    """
    Generate a parameterized SQL SELECT query for a table, columns, and conditions.

    Args:
    table_name (str): The name of the table from which to select records.
    columns (List[str]): A list of columns to be selected.
    conditions (List[Tuple[str, object]]): A list of conditions for the selection, each represented as a (column, value) tuple.

    Returns:
    Tuple[str, Tuple[object, ...]]: A SQL template string and parameters tuple.

    Example:
    >>> generate_select_query("students", ["name", "email"], [("age", "20")])
    ("SELECT name, email FROM students WHERE age = ?;", ("20",))
    """
    if not columns:
        raise ValueError("SELECT requires at least one column")

    safe_table_name = validate_identifier(table_name, "table name")
    if columns == ["*"]:
        columns_clause = "*"
    else:
        safe_columns = [validate_identifier(column, "column name") for column in columns]
        columns_clause = ", ".join(safe_columns)

    query = f"SELECT {columns_clause} FROM {safe_table_name}"
    params: Tuple[object, ...] = ()
    if conditions:
        where_clause = " AND ".join(
            f"{validate_identifier(column, 'column name')} = ?" for column, _ in conditions
        )
        params = tuple(value for _, value in conditions)
        query += f" WHERE {where_clause}"

    return query + ";", params

if __name__ == "__main__":
    select_columns = ["name", "email"]
    select_conditions = [
        ("age", "20")
    ]

    query, params = generate_select_query("students", select_columns, select_conditions)
    print(query)
    print(params)
