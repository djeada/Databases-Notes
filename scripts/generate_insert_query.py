from typing import List

def generate_insert_query(table_name: str, data: List[List[str]]) -> str:
    """
    Generate a SQL INSERT query for a given table name and data.

    Args:
    table_name (str): The name of the table.
    data (List[List[str]]): A list of rows, with each row being a list of values.

    Returns:
    str: A SQL INSERT query string.
    """
    # Escaping single quotes in data and formatting rows
    escaped_data = [
        ", ".join(f"'{str(value).replace("'", "''")}'" for value in row)
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

    print(generate_insert_query("users", sample_data))
