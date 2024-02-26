import sqlite3
from datetime import datetime
import os

def create_connection(db_file):
    """ Create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Creating or reading database at: {os.path.abspath(db_file)}")
        return conn
    except sqlite3.Error as e:
        print(e)

    return conn

def create_table(conn):
    """ Create a table if it does not exist """
    try:
        sql_create_table = """ CREATE TABLE IF NOT EXISTS example_table (
                                    id integer PRIMARY KEY AUTOINCREMENT,
                                    timestamp text NOT NULL
                                ); """
        cursor = conn.cursor()
        cursor.execute(sql_create_table)
        print("Table 'example_table' created or already exists.")
    except sqlite3.Error as e:
        print(e)

def append_rows(conn, num_rows=1):
    """ Append rows to the table """
    try:
        cursor = conn.cursor()
        for _ in range(num_rows):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sql_insert_row = """ INSERT INTO example_table(timestamp)
                                 VALUES(?) """
            cursor.execute(sql_insert_row, (timestamp,))
            print(f"Row added with timestamp: {timestamp}")
        conn.commit()
    except sqlite3.Error as e:
        print(e)

def main():
    database = "database.db"

    # create a database connection
    conn = create_connection(database)
    if conn is not None:
        # create table
        create_table(conn)

        # append rows
        append_rows(conn, num_rows=100000)  # Change num_rows as needed

        conn.close()
    else:
        print("Error! cannot create the database connection.")

if __name__ == '__main__':
    main()
