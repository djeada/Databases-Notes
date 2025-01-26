import sqlite3
import threading
import time

# Flag to control whether the deadlock should occur
deadlock_mode = True  # Set to False to demonstrate without deadlock

# Maximum number of retries for a transaction
MAX_RETRIES = 3

# Delay between retries in seconds
RETRY_DELAY = 1

# Function for connection 1 with retry logic
def conn1_behavior():
    retries = 0
    while retries < MAX_RETRIES:
        try:
            conn1 = sqlite3.connect('test.db', timeout=5)  # timeout for locks
            conn1.execute("BEGIN TRANSACTION;")
            conn1.execute("UPDATE test_table SET value = 'X' WHERE id = 1;")
            print("Connection 1: Locked row 1.")

            # Simulate some processing time before trying to lock row 2
            if deadlock_mode:
                time.sleep(1)  # Ensure overlap with conn2's lock
            else:
                time.sleep(2)  # Avoid overlap, preventing deadlock

            conn1.execute("UPDATE test_table SET value = 'Y' WHERE id = 2;")
            print("Connection 1: Successfully updated row 2.")
            conn1.commit()
            conn1.close()
            break  # Exit loop if successful

        except sqlite3.OperationalError as e:
            print(f"Connection 1: Deadlock detected! {e}")
            conn1.rollback()
            conn1.close()
            retries += 1
            if retries < MAX_RETRIES:
                print(f"Connection 1: Retrying transaction ({retries}/{MAX_RETRIES})...")
                time.sleep(RETRY_DELAY)
            else:
                print("Connection 1: Max retries reached. Transaction failed.")

# Function for connection 2 with retry logic
def conn2_behavior():
    retries = 0
    while retries < MAX_RETRIES:
        try:
            conn2 = sqlite3.connect('test.db', timeout=5)  # timeout for locks
            conn2.execute("BEGIN TRANSACTION;")
            conn2.execute("UPDATE test_table SET value = 'Y' WHERE id = 2;")
            print("Connection 2: Locked row 2.")

            # Simulate some processing time before trying to lock row 1
            if deadlock_mode:
                time.sleep(1)  # Ensure overlap with conn1's lock
            else:
                time.sleep(0.5)  # Avoid overlap, preventing deadlock

            conn2.execute("UPDATE test_table SET value = 'X' WHERE id = 1;")
            print("Connection 2: Successfully updated row 1.")
            conn2.commit()
            conn2.close()
            break  # Exit loop if successful

        except sqlite3.OperationalError as e:
            print(f"Connection 2: Deadlock detected! {e}")
            conn2.rollback()
            conn2.close()
            retries += 1
            if retries < MAX_RETRIES:
                print(f"Connection 2: Retrying transaction ({retries}/{MAX_RETRIES})...")
                time.sleep(RETRY_DELAY)
            else:
                print("Connection 2: Max retries reached. Transaction failed.")

# Set up the test table
def setup_database():
    conn = sqlite3.connect('test.db')
    conn.execute("PRAGMA journal_mode = WAL;")  # Use WAL for better concurrency
    conn.execute("""
        CREATE TABLE IF NOT EXISTS test_table (
            id INTEGER PRIMARY KEY,
            value TEXT
        );
    """)
    # Initialize the table with two rows
    conn.execute("""
        INSERT OR REPLACE INTO test_table (id, value) 
        VALUES 
            (1, 'A'),
            (2, 'B');
    """)
    conn.commit()
    conn.close()

# Main function
if __name__ == "__main__":
    setup_database()

    # Create threads for both connections
    thread1 = threading.Thread(target=conn1_behavior)
    thread2 = threading.Thread(target=conn2_behavior)

    # Start the threads
    thread1.start()
    thread2.start()

    # Wait for both threads to complete
    thread1.join()
    thread2.join()

    print("Demo completed.")
