"""
SQL UPDATE Query Generator

Goal: Programmatically generate SQL UPDATE statements with SET clauses and
      WHERE conditions, demonstrating safe data modification.

Use Case: Useful for data transformation scripts, API update endpoints, or admin tools.

Note: This implementation properly escapes single quotes to prevent SQL injection.

Usage:
    python update_query.py
"""
from typing import Dict, List, Tuple

def generate_update_query(table_name: str, data: Dict[str, str], conditions: List[Tuple[str, str]]) -> str:
    """
    Generate a SQL UPDATE query for a given table name, data, and conditions.

    This function constructs a SQL UPDATE query string to update specified columns
    with provided values in a given table, based on certain conditions.

    Args:
    table_name (str): The name of the table to update.
    data (Dict[str, str]): A dictionary where keys are column names and values are the new values to be set.
    conditions (List[Tuple[str, str]]): A list of conditions for the update, with each condition represented as a (column, value) tuple.

    Returns:
    str: A SQL UPDATE query string.

    Example:
    >>> generate_update_query(
            "users",
            {"email": "john.updated@example.com", "last_name": "UpdatedDoe"},
            [("first_name", "John"), ("last_name", "Doe")]
        )
    "UPDATE users SET email = 'john.updated@example.com', last_name = 'UpdatedDoe' WHERE first_name = 'John' AND last_name = 'Doe';"
    """
    # Preparing the SET part of the query
    SINGLE_QUOTE = "'"
    set_clause = ", ".join(f"{column} = '{value.replace(SINGLE_QUOTE, SINGLE_QUOTE * 2)}'" for column, value in data.items())

    # Preparing the WHERE part of the query
    where_clause = " AND ".join(f"{column} = '{value.replace(SINGLE_QUOTE, SINGLE_QUOTE * 2)}'" for column, value in conditions)

    query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause};"

    return query

if __name__ == "__main__":
    update_data = {
        "email": "john.updated@example.com",
        "last_name": "UpdatedDoe"
    }
    update_conditions = [
        ("first_name", "John"),
        ("last_name", "Doe")
    ]

    # Expected output:
    # UPDATE users SET email = 'john.updated@example.com', last_name = 'UpdatedDoe' WHERE first_name = 'John' AND last_name = 'Doe';
    print(generate_update_query("users", update_data, update_conditions))
