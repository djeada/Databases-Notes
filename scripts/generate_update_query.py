from typing import Dict, List, Tuple

def generate_update_query(table_name: str, data: Dict[str, str], conditions: List[Tuple[str, str]]) -> str:
    """
    Generate a SQL UPDATE query for a given table name, data, and conditions.

    Args:
    table_name (str): The name of the table to update.
    data (Dict[str, str]): A dictionary of column-value pairs to update.
    conditions (List[Tuple[str, str]]): A list of conditions for the update, each represented as a (column, value) tuple.

    Returns:
    str: A SQL UPDATE query string.
    """
    # Preparing the SET part of the query
    set_clause = ", ".join(f"{column} = '{value.replace("'", "''")}'" for column, value in data.items())

    # Preparing the WHERE part of the query
    where_clause = " AND ".join(f"{column} = '{value.replace("'", "''")}'" for column, value in conditions)

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

    print(generate_update_query("users", update_data, update_conditions))
