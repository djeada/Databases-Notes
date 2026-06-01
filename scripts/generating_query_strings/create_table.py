"""
SQL CREATE TABLE Query Generator

Goal: Programmatically generate SQL CREATE TABLE statements from trusted schema
      metadata, demonstrating how to build DDL queries while validating identifiers.

Use Case: Useful for schema generation tools, migration scripts, or ORM implementations.

Note: DB-API placeholders do not apply to table names, column names, or SQL type
declarations, so this example focuses on identifier validation instead.

Usage:
    python create_table.py
"""
from typing import Dict
import re

IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def validate_identifier(identifier: str, kind: str) -> str:
    """Allow only simple SQL identifiers in this educational example."""
    if not IDENTIFIER_RE.fullmatch(identifier):
        raise ValueError(f"Invalid {kind}: {identifier!r}")
    return identifier

def generate_create_table_query(table_name: str, columns: Dict[str, str]) -> str:
    """
    Generate a SQL CREATE TABLE query for a given table name and column definitions.

    Args:
    table_name (str): The name of the table to create.
    columns (Dict[str, str]): A dictionary where keys are column names and values are their data types.

    Returns:
    str: A SQL CREATE TABLE query string.

    Example:
    >>> generate_create_table_query(
            "students",
            {"id": "INT PRIMARY KEY", "name": "VARCHAR(100)", "age": "INT", "email": "VARCHAR(100)"}
        )
    "CREATE TABLE students (id INT PRIMARY KEY, name VARCHAR(100), age INT, email VARCHAR(100));"
    """
    if not columns:
        raise ValueError("CREATE TABLE requires at least one column definition")

    safe_table_name = validate_identifier(table_name, "table name")
    column_definitions = []
    for column, data_type in columns.items():
        safe_column = validate_identifier(column, "column name")
        clean_type = data_type.strip()
        if not clean_type:
            raise ValueError(f"Column {column!r} must have a non-empty type declaration")
        column_definitions.append(f"{safe_column} {clean_type}")

    columns_clause = ", ".join(column_definitions)
    query = f"CREATE TABLE {safe_table_name} ({columns_clause});"

    return query

if __name__ == "__main__":
    table_columns = {
        "id": "INT PRIMARY KEY",
        "name": "VARCHAR(100)",
        "age": "INT",
        "email": "VARCHAR(100)"
    }

    # Expected output:
    # CREATE TABLE students (id INT PRIMARY KEY, name VARCHAR(100), age INT, email VARCHAR(100));
    print(generate_create_table_query("students", table_columns))
