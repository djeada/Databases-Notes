import sqlite3
import threading
import time

# Function to set up the database
def setup_database():
    conn = sqlite3.connect('test.db')
    conn.execute("PRAGMA journal_mode = WAL;")  # Enable Write-Ahead Logging for better concurrency
    conn.execute("""
        CREATE TABLE IF NOT EXISTS test_table (
            id INTEGER PRIMARY KEY,
            value TEXT
        );
    """)
    # Initialize the table with a single row
    conn.execute("""
        INSERT OR REPLACE INTO test_table (id, value) 
        VALUES 
            (1, 'Initial');
    """)
    conn.commit()
    conn.close()

# Transaction A: Reads data (Simulating Read Committed or Serializable)
def transaction_a(isolation_level='READ COMMITTED'):
    conn_a = sqlite3.connect('test.db', timeout=10, isolation_level=None)
    cursor_a = conn_a.cursor()
    
    if isolation_level == 'SERIALIZABLE':
        cursor_a.execute("BEGIN IMMEDIATE;")  # Starts a transaction with RESERVED lock
    else:
        cursor_a.execute("BEGIN;")  # Starts a deferred transaction

    print(f"Transaction A ({isolation_level}): Started.")

    # Read the value
    cursor_a.execute("SELECT value FROM test_table WHERE id = 1;")
    value = cursor_a.fetchone()[0]
    print(f"Transaction A ({isolation_level}): Read value = {value}")

    # Simulate some processing time
    time.sleep(2)

    # Read the value again
    cursor_a.execute("SELECT value FROM test_table WHERE id = 1;")
    new_value = cursor_a.fetchone()[0]
    print(f"Transaction A ({isolation_level}): Read value again = {new_value}")

    conn_a.commit()
    print(f"Transaction A ({isolation_level}): Committed.")
    conn_a.close()

# Transaction B: Writes data
def transaction_b():
    conn_b = sqlite3.connect('test.db', timeout=10, isolation_level=None)
    cursor_b = conn_b.cursor()

    cursor_b.execute("BEGIN IMMEDIATE;")  # Starts a transaction with RESERVED lock
    print("Transaction B: Started.")

    # Update the value
    cursor_b.execute("UPDATE test_table SET value = 'Updated by B' WHERE id = 1;")
    print("Transaction B: Updated value to 'Updated by B'.")

    # Simulate some processing time
    time.sleep(1)

    conn_b.commit()
    print("Transaction B: Committed.")
    conn_b.close()

# Main function to run the simulation
def main():
    setup_database()

    print("\n--- Simulating Read Committed Isolation Level ---")
    # Start Transaction A with Read Committed
    thread_a = threading.Thread(target=transaction_a, args=('READ COMMITTED',))
    # Start Transaction B shortly after
    thread_b = threading.Thread(target=transaction_b)

    thread_a.start()
    time.sleep(0.5)  # Ensure Transaction A starts first
    thread_b.start()

    thread_a.join()
    thread_b.join()

    # Reset the table for the next simulation
    setup_database()

    print("\n--- Simulating Serializable Isolation Level ---")
    # Start Transaction A with Serializable
    thread_a_serial = threading.Thread(target=transaction_a, args=('SERIALIZABLE',))
    # Start Transaction B shortly after
    thread_b_serial = threading.Thread(target=transaction_b)

    thread_a_serial.start()
    time.sleep(0.5)  # Ensure Transaction A starts first
    thread_b_serial.start()

    thread_a_serial.join()
    thread_b_serial.join()

    # Final state of the table
    conn_final = sqlite3.connect('test.db')
    cursor_final = conn_final.cursor()
    cursor_final.execute("SELECT value FROM test_table WHERE id = 1;")
    final_value = cursor_final.fetchone()[0]
    print(f"\nFinal value in test_table: {final_value}")
    conn_final.close()

    print("\nDemo completed.")

if __name__ == "__main__":
    main()
