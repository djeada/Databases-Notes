from typing import List, Tuple

def generate_select_query(table_name: str, columns: List[str], conditions: List[Tuple[str, str]]) -> str:
    """
    Generate a SQL SELECT query for a given table name, columns, and conditions.

    Args:
    table_name (str): The name of the table from which to select records.
    columns (List[str]): A list of columns to be selected.
    conditions (List[Tuple[str, str]]): A list of conditions for the selection, each represented as a (column, value) tuple.

    Returns:
    str: A SQL SELECT query string.

    Example:
    >>> generate_select_query("students", ["name", "email"], [("age", "20")])
    "SELECT name, email FROM students WHERE age = '20';"
    """
    # Preparing the SELECT and WHERE parts of the query
    columns_clause = ", ".join(columns)
    where_clause = " AND ".join(f"{column} = '{value.replace(\"'\", \"''\")}'" for column, value in conditions)

    query = f"SELECT {columns_clause} FROM {table_name} WHERE {where_clause};"

    return query

if __name__ == "__main__":
    select_columns = ["name", "email"]
    select_conditions = [
        ("age", "20")
    ]

    # Expected output:
    # SELECT name, email FROM students WHERE age = '20';
    print(generate_select_query("students", select_columns, select_conditions))
