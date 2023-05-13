def create_insert_query(table_name, data):
    # Create the base INSERT statement
    query = f"INSERT INTO {table_name} VALUES "

    # Add each row of data
    for i, row in enumerate(data):
        # Convert each value to a string and escape quotes
        row = ["'{}'".format(str(val).replace("'", "''")) for val in row]

        # Join the values together, separated by commas
        row_str = ", ".join(row)

        # Add the row to the query
        query += f"({row_str})"

        # If this is not the last row, add a comma and a space
        if i < len(data) - 1:
            query += ", "

    # Add a semicolon at the end of the query
    query += ";"

    return query


if __name__ == "__main__":
    data = [
        ["John", "Doe", "john.doe@example.com"],
        ["Jane", "Doe", "jane.doe@example.com"],
    ]

    print(create_insert_query("users", data))
