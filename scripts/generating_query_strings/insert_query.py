"""
SQL INSERT Query Generator

Goal: Programmatically generate SQL INSERT statements for multiple rows,
      demonstrating batch insert operations with proper SQL escaping.

Use Case: Useful for ETL pipelines, data import tools, or seeding test databases.

Note: This implementation properly escapes single quotes to prevent SQL injection.

Usage:
    python insert_query.py
"""
from typing import List

def generate_insert_query(table_name: str, data: List[List[str]]) -> str:
    """
    Generate a SQL INSERT query for a given table name and data.

    This function takes the name of a database table and a list of rows,
    where each row is a list of string values. It returns a SQL INSERT 
    query string that can be used to insert the provided data into the 
    specified table.

    Args:
    table_name (str): The name of the table where data will be inserted.
    data (List[List[str]]): A list of rows, with each row being a list of 
                            string values representing the data to be inserted.

    Returns:
    str: A SQL INSERT query string.

    Example:
    >>> generate_insert_query("users", [["John", "Doe", "john.doe@example.com"], ["Jane", "Doe", "jane.doe@example.com"]])
    "INSERT INTO users VALUES ('John', 'Doe', 'john.doe@example.com'), ('Jane', 'Doe', 'jane.doe@example.com');"
    """
    # Escaping single quotes in data and formatting rows
    SINGLE_QUOTE = "'"
    escaped_data = [
        ", ".join(f"'{str(value).replace(SINGLE_QUOTE, SINGLE_QUOTE * 2)}'" for value in row)
        for row in data
    ]

    # Joining all rows into a single query
    values = "), (".join(escaped_data)
    query = f"INSERT INTO {table_name} VALUES ({values});"

    return query

if __name__ == "__main__":
    sample_data = [
        ["John", "Doe", "john.doe@example.com"],
        ["Jane", "Doe", "jane.doe@example.com"],
    ]

    # Expected output:
    # INSERT INTO users VALUES ('John', 'Doe', 'john.doe@example.com'), ('Jane', 'Doe', 'jane.doe@example.com');
    print(generate_insert_query("users", sample_data))
