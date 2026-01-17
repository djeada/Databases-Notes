"""
SQL DELETE Query Generator

Goal: Programmatically generate SQL DELETE statements with WHERE conditions,
      demonstrating safe deletion with proper SQL escaping.

Use Case: Useful for building data cleanup scripts, admin tools, or API backends.

Note: This implementation properly escapes single quotes to prevent SQL injection.

Usage:
    python delete.py
"""
from typing import List, Tuple

def generate_delete_query(table_name: str, conditions: List[Tuple[str, str]]) -> str:
    """
    Generate a SQL DELETE query for a given table name and conditions.

    Args:
    table_name (str): The name of the table from which to delete records.
    conditions (List[Tuple[str, str]]): A list of conditions for the deletion, each represented as a (column, value) tuple.

    Returns:
    str: A SQL DELETE query string.

    Example:
    >>> generate_delete_query("students", [("name", "John Doe"), ("age", "20")])
    "DELETE FROM students WHERE name = 'John Doe' AND age = '20';"
    """
    # Preparing the WHERE part of the query
    where_clause = " AND ".join(f"{column} = '{value.replace(chr(39), chr(39)*2)}'" for column, value in conditions)

    query = f"DELETE FROM {table_name} WHERE {where_clause};"

    return query

if __name__ == "__main__":
    delete_conditions = [
        ("name", "John Doe"),
        ("age", "20")
    ]

    # Expected output:
    # DELETE FROM students WHERE name = 'John Doe' AND age = '20';
    print(generate_delete_query("students", delete_conditions))
