import sqlite3
import threading
import time

# Constants
DATABASE = 'lock_demo.db'
MAX_RETRIES = 3
RETRY_DELAY = 1

# Function to set up the database
def setup_database():
    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA journal_mode = WAL;")  # Enable Write-Ahead Logging for better concurrency
    conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT,
            quantity INTEGER,
            version INTEGER
        );
    """)
    # Initialize the table with a single product
    conn.execute("""
        INSERT OR REPLACE INTO products (id, name, quantity, version) 
        VALUES 
            (1, 'Widget', 100, 1);
    """)
    conn.commit()
    conn.close()

# Pessimistic Locking: Transaction Function
def pessimistic_transaction(thread_name, delay_before_update=2):
    try:
        conn = sqlite3.connect(DATABASE, timeout=10)
        cursor = conn.cursor()
        print(f"{thread_name}: Starting Pessimistic Transaction.")
        
        # Begin an immediate transaction to acquire a RESERVED lock
        cursor.execute("BEGIN IMMEDIATE;")
        print(f"{thread_name}: Acquired RESERVED lock.")
        
        # Simulate reading the data
        cursor.execute("SELECT quantity FROM products WHERE id = 1;")
        quantity = cursor.fetchone()[0]
        print(f"{thread_name}: Read quantity = {quantity}")
        
        # Simulate some processing time
        time.sleep(delay_before_update)
        
        # Update the quantity
        new_quantity = quantity - 10
        cursor.execute("UPDATE products SET quantity = ? WHERE id = 1;", (new_quantity,))
        print(f"{thread_name}: Updated quantity to {new_quantity}")
        
        # Commit the transaction
        conn.commit()
        print(f"{thread_name}: Transaction Committed.")
        
    except sqlite3.OperationalError as e:
        print(f"{thread_name}: OperationalError - {e}")
    finally:
        conn.close()

# Optimistic Locking: Transaction Function
def optimistic_transaction(thread_name, delay_before_update=2):
    retries = 0
    while retries < MAX_RETRIES:
        try:
            conn = sqlite3.connect(DATABASE, timeout=10)
            cursor = conn.cursor()
            print(f"{thread_name}: Starting Optimistic Transaction (Attempt {retries + 1}).")
            
            # Begin a deferred transaction
            cursor.execute("BEGIN;")
            
            # Read current quantity and version
            cursor.execute("SELECT quantity, version FROM products WHERE id = 1;")
            row = cursor.fetchone()
            if row is None:
                print(f"{thread_name}: Product not found.")
                conn.rollback()
                return
            quantity, version = row
            print(f"{thread_name}: Read quantity = {quantity}, version = {version}")
            
            # Simulate some processing time
            time.sleep(delay_before_update)
            
            # Attempt to update with version check
            new_quantity = quantity - 10
            new_version = version + 1
            cursor.execute("""
                UPDATE products 
                SET quantity = ?, version = ? 
                WHERE id = 1 AND version = ?;
            """, (new_quantity, new_version, version))
            
            if cursor.rowcount == 0:
                # No rows updated means version mismatch
                raise sqlite3.OperationalError("Version conflict detected.")
            
            print(f"{thread_name}: Updated quantity to {new_quantity}, version to {new_version}")
            
            # Commit the transaction
            conn.commit()
            print(f"{thread_name}: Transaction Committed.")
            break  # Exit loop on success
            
        except sqlite3.OperationalError as e:
            print(f"{thread_name}: {e}")
            conn.rollback()
            retries += 1
            if retries < MAX_RETRIES:
                print(f"{thread_name}: Retrying transaction ({retries}/{MAX_RETRIES}) after delay.")
                time.sleep(RETRY_DELAY)
            else:
                print(f"{thread_name}: Max retries reached. Transaction failed.")
        finally:
            conn.close()

# Function to display final state
def display_final_state():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT quantity, version FROM products WHERE id = 1;")
    row = cursor.fetchone()
    if row:
        quantity, version = row
        print(f"\nFinal State -> Quantity: {quantity}, Version: {version}")
    else:
        print("\nFinal State -> Product not found.")
    conn.close()

# Main function to run the simulations
def main():
    setup_database()
    
    print("\n--- Pessimistic Locking Simulation ---")
    # Create two threads attempting to perform pessimistic transactions
    thread1 = threading.Thread(target=pessimistic_transaction, args=("Thread 1",))
    thread2 = threading.Thread(target=pessimistic_transaction, args=("Thread 2",))
    
    thread1.start()
    time.sleep(0.5)  # Slight delay to ensure Thread 1 starts first
    thread2.start()
    
    thread1.join()
    thread2.join()
    
    # Reset the database for optimistic locking simulation
    setup_database()
    
    print("\n--- Optimistic Locking Simulation ---")
    # Create two threads attempting to perform optimistic transactions
    thread3 = threading.Thread(target=optimistic_transaction, args=("Thread 3",))
    thread4 = threading.Thread(target=optimistic_transaction, args=("Thread 4",))
    
    thread3.start()
    time.sleep(0.5)  # Slight delay to ensure Thread 3 starts first
    thread4.start()
    
    thread3.join()
    thread4.join()
    
    # Display final state
    display_final_state()
    
    print("\nDemo completed.")

if __name__ == "__main__":
    main()
