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
    where_clause = " AND ".join(f"{column} = '{value.replace(\"'\", \"''\")}'" for column, value in conditions)

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
