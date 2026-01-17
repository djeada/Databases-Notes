"""
SQL CREATE TABLE Query Generator

Goal: Programmatically generate SQL CREATE TABLE statements from a dictionary
      of column definitions, demonstrating how to build DDL queries dynamically.

Use Case: Useful for schema generation tools, migration scripts, or ORM implementations.

Usage:
    python create_table.py
"""
from typing import Dict

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
    # Preparing the column definitions part of the query
    columns_clause = ", ".join(f"{column} {data_type}" for column, data_type in columns.items())

    query = f"CREATE TABLE {table_name} ({columns_clause});"

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
