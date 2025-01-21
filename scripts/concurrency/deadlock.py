import sqlite3
import threading
import time

# Flag to control whether the deadlock should occur
deadlock_mode = True  # Set to False to demonstrate without deadlock

# Function for connection 1
def conn1_behavior():
    conn1 = sqlite3.connect('test.db', timeout=5)  # timeout for locks
    conn1.execute("BEGIN TRANSACTION;")
    conn1.execute("UPDATE test_table SET value = 'X' WHERE id = 1;")
    print("Connection 1: Locked row 1.")

    # Simulate some processing time before trying to lock row 2
    if deadlock_mode:
        time.sleep(1)  # Ensure overlap with conn2's lock
    else:
        time.sleep(2)  # Avoid overlap, preventing deadlock

    try:
        conn1.execute("UPDATE test_table SET value = 'Y' WHERE id = 2;")
        print("Connection 1: Successfully updated row 2.")
    except sqlite3.OperationalError as e:
        print(f"Connection 1: Deadlock detected! {e}")
    conn1.rollback()  # Rollback after deadlock or success
    conn1.close()

# Function for connection 2
def conn2_behavior():
    conn2 = sqlite3.connect('test.db', timeout=5)  # timeout for locks
    conn2.execute("BEGIN TRANSACTION;")
    conn2.execute("UPDATE test_table SET value = 'Y' WHERE id = 2;")
    print("Connection 2: Locked row 2.")

    # Simulate some processing time before trying to lock row 1
    if deadlock_mode:
        time.sleep(1)  # Ensure overlap with conn1's lock
    else:
        time.sleep(0.5)  # Avoid overlap, preventing deadlock

    try:
        conn2.execute("UPDATE test_table SET value = 'X' WHERE id = 1;")
        print("Connection 2: Successfully updated row 1.")
    except sqlite3.OperationalError as e:
        print(f"Connection 2: Deadlock detected! {e}")
    conn2.rollback()  # Rollback after deadlock or success
    conn2.close()

# Set up the test table
def setup_database():
    conn = sqlite3.connect('test.db')
    conn.execute("PRAGMA journal_mode = WAL;")  # Use WAL for concurrency
    conn.execute("CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY, value TEXT);")
    conn.execute("INSERT OR REPLACE INTO test_table (id, value) VALUES (1, 'A'), (2, 'B');")
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
