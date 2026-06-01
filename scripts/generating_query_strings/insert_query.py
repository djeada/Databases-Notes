"""
SQL INSERT Query Generator

Goal: Programmatically generate parameterized SQL INSERT statements for multiple
      rows, demonstrating safe batch insert operations.

Use Case: Useful for ETL pipelines, data import tools, or seeding test databases.

Note: This implementation returns a SQL template plus parameters, which is the
safe pattern supported by Python DB-API drivers.

Usage:
    python insert_query.py
"""
from typing import List, Sequence, Tuple
import re

IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def validate_identifier(identifier: str, kind: str) -> str:
    """Allow only simple SQL identifiers in this educational example."""
    if not IDENTIFIER_RE.fullmatch(identifier):
        raise ValueError(f"Invalid {kind}: {identifier!r}")
    return identifier


def generate_insert_query(
    table_name: str, columns: Sequence[str], data: Sequence[Sequence[object]]
) -> Tuple[str, Tuple[object, ...]]:
    """
    Generate a parameterized SQL INSERT query for a given table name and data.

    This function takes the name of a database table, a list of columns, and
    a list of rows. It returns a SQL template string plus a flattened params
    tuple that can be passed directly to a DB-API driver's execute method.

    Args:
    table_name (str): The name of the table where data will be inserted.
    columns (Sequence[str]): Column names to insert into.
    data (Sequence[Sequence[object]]): A list of rows, with each row being a list of 
                            string values representing the data to be inserted.

    Returns:
    Tuple[str, Tuple[object, ...]]: A SQL template string and parameters tuple.

    Example:
    >>> generate_insert_query(
            "users",
            ["first_name", "last_name", "email"],
            [["John", "Doe", "john.doe@example.com"], ["Jane", "Doe", "jane.doe@example.com"]],
        )
    (
        "INSERT INTO users (first_name, last_name, email) VALUES (?, ?, ?), (?, ?, ?);",
        ("John", "Doe", "john.doe@example.com", "Jane", "Doe", "jane.doe@example.com"),
    )
    """
    if not columns:
        raise ValueError("INSERT requires at least one column")
    if not data:
        raise ValueError("INSERT requires at least one row")

    safe_table_name = validate_identifier(table_name, "table name")
    safe_columns = [validate_identifier(column, "column name") for column in columns]

    row_length = len(safe_columns)
    for row in data:
        if len(row) != row_length:
            raise ValueError("Every INSERT row must match the number of columns")

    row_placeholder = "(" + ", ".join("?" for _ in safe_columns) + ")"
    values_clause = ", ".join(row_placeholder for _ in data)
    columns_clause = ", ".join(safe_columns)
    params = tuple(value for row in data for value in row)
    query = f"INSERT INTO {safe_table_name} ({columns_clause}) VALUES {values_clause};"

    return query, params

if __name__ == "__main__":
    insert_columns = ["first_name", "last_name", "email"]
    sample_data = [
        ["John", "Doe", "john.doe@example.com"],
        ["Jane", "Doe", "jane.doe@example.com"],
    ]

    query, params = generate_insert_query("users", insert_columns, sample_data)
    print(query)
    print(params)
