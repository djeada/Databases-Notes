"""
Mock Database Creator

This script demonstrates how to create and populate a SQLite database with timestamped records.
Goal: Create a sample database with a large number of rows for testing and demonstration purposes.
"""
import sqlite3
from datetime import datetime, timedelta
import os

def create_connection(db_file):
    """
    Create a database connection to a SQLite database.
    
    Args:
        db_file (str): Path to the database file
        
    Returns:
        sqlite3.Connection: Database connection object or None if error occurs
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"✓ Database connection established: {os.path.abspath(db_file)}")
        return conn
    except sqlite3.Error as e:
        print(f"✗ Error connecting to database: {e}")

    return conn

def create_table(conn):
    """
    Create a table if it does not exist.
    
    Args:
        conn (sqlite3.Connection): Database connection object
    """
    try:
        sql_create_table = """ CREATE TABLE IF NOT EXISTS example_table (
                                    id integer PRIMARY KEY AUTOINCREMENT,
                                    timestamp text NOT NULL
                                ); """
        cursor = conn.cursor()
        cursor.execute(sql_create_table)
        print("✓ Table 'example_table' created or already exists.")
    except sqlite3.Error as e:
        print(f"✗ Error creating table: {e}")

def append_rows(conn, num_rows=1):
    """
    Append rows to the table with progress indicators.
    
    Args:
        conn (sqlite3.Connection): Database connection object
        num_rows (int): Number of rows to insert
    """
    try:
        cursor = conn.cursor()
        print(f"Inserting {num_rows:,} rows...")
        
        # Batch insert for better performance
        batch_size = 1000
        start_time = datetime.now()
        
        for i in range(0, num_rows, batch_size):
            rows_to_insert = min(batch_size, num_rows - i)
            
            # Generate unique timestamps for each row
            # Each row gets a unique timestamp with microsecond precision
            timestamps = []
            for j in range(rows_to_insert):
                row_index = i + j
                # Calculate microseconds offset (up to 999999 microseconds per second)
                seconds_offset = row_index // 1000000
                microsecond = row_index % 1000000
                timestamp = start_time.replace(microsecond=0) + \
                           timedelta(seconds=seconds_offset, microseconds=microsecond)
                timestamps.append((timestamp.strftime("%Y-%m-%d %H:%M:%S.%f"),))
            
            # Insert batch
            cursor.executemany(
                "INSERT INTO example_table(timestamp) VALUES(?)",
                timestamps
            )
            
            # Progress indicator
            if (i + rows_to_insert) % 10000 == 0 or (i + rows_to_insert) == num_rows:
                print(f"  Progress: {i + rows_to_insert:,} / {num_rows:,} rows inserted")
        
        conn.commit()
        print(f"✓ Successfully inserted {num_rows:,} rows")
    except sqlite3.Error as e:
        print(f"✗ Error inserting rows: {e}")

def main():
    """
    Main function to create database, table, and populate with sample data.
    """
    database = "database.db"

    # Create a database connection
    conn = create_connection(database)
    if conn is not None:
        # Create table
        create_table(conn)

        # Append rows (change num_rows as needed)
        append_rows(conn, num_rows=100000)

        conn.close()
        print("✓ Database connection closed")
    else:
        print("✗ Error! Cannot create the database connection.")

if __name__ == '__main__':
    main()
