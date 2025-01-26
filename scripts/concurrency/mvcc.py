import sqlite3
import threading
import time
import uuid

# Constants
DATABASE = 'mvcc_simulation.db'
VERSION_TABLE = 'products_versioned'

# Function to set up the database with versioned products table
def setup_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create a versioned products table
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {VERSION_TABLE} (
            id INTEGER PRIMARY KEY,
            name TEXT,
            quantity INTEGER,
            version_id TEXT,
            valid_from REAL,
            valid_to REAL
        );
    """)
    
    # Initialize the table with a single product version
    cursor.execute(f"DELETE FROM {VERSION_TABLE};")  # Clear existing data
    current_time = time.time()
    cursor.execute(f"""
        INSERT INTO {VERSION_TABLE} (id, name, quantity, version_id, valid_from, valid_to)
        VALUES (?, ?, ?, ?, ?, ?);
    """, (1, 'Widget', 100, str(uuid.uuid4()), current_time, float('inf')))
    
    conn.commit()
    conn.close()

# Function to read the latest valid version of a product
def read_product(conn, product_id, transaction_start_time):
    cursor = conn.cursor()
    cursor.execute(f"""
        SELECT name, quantity FROM {VERSION_TABLE}
        WHERE id = ? AND valid_from <= ? AND valid_to > ?
        ORDER BY valid_from DESC
        LIMIT 1;
    """, (product_id, transaction_start_time, transaction_start_time))
    result = cursor.fetchone()
    if result:
        return {'name': result[0], 'quantity': result[1]}
    else:
        return None

# Function to write a new version of a product
def write_product(conn, product_id, new_quantity, transaction_start_time):
    cursor = conn.cursor()
    current_time = time.time()
    
    # End the validity of the old version
    cursor.execute(f"""
        UPDATE {VERSION_TABLE}
        SET valid_to = ?
        WHERE id = ? AND valid_to = float('inf');
    """, (current_time, product_id))
    
    # Insert the new version
    cursor.execute(f"""
        INSERT INTO {VERSION_TABLE} (id, name, quantity, version_id, valid_from, valid_to)
        VALUES (?, ?, ?, ?, ?, ?);
    """, (product_id, 'Widget', new_quantity, str(uuid.uuid4()), current_time, float('inf')))
    
    conn.commit()

# Transaction A: Reads, waits, then updates
def transaction_a():
    conn = sqlite3.connect(DATABASE)
    transaction_start_time = time.time()
    print("Transaction A: Started.")
    
    product = read_product(conn, 1, transaction_start_time)
    print(f"Transaction A: Read product - {product}")
    
    # Simulate some processing time
    time.sleep(2)
    
    # Update the product
    new_quantity = product['quantity'] + 50
    write_product(conn, 1, new_quantity, transaction_start_time)
    print(f"Transaction A: Updated product quantity to {new_quantity}")
    
    conn.close()
    print("Transaction A: Committed.")

# Transaction B: Reads, waits, then updates
def transaction_b():
    conn = sqlite3.connect(DATABASE)
    transaction_start_time = time.time()
    print("Transaction B: Started.")
    
    product = read_product(conn, 1, transaction_start_time)
    print(f"Transaction B: Read product - {product}")
    
    # Simulate some processing time
    time.sleep(1)
    
    # Update the product
    new_quantity = product['quantity'] - 30
    write_product(conn, 1, new_quantity, transaction_start_time)
    print(f"Transaction B: Updated product quantity to {new_quantity}")
    
    conn.close()
    print("Transaction B: Committed.")

# Function to display all versions of the product
def display_versions():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute(f"SELECT name, quantity, valid_from, valid_to FROM {VERSION_TABLE} WHERE id = 1 ORDER BY valid_from;")
    versions = cursor.fetchall()
    print("\nAll Versions of Product 'Widget':")
    for v in versions:
        print(f"Name: {v[0]}, Quantity: {v[1]}, Valid From: {v[2]}, Valid To: {v[3]}")
    conn.close()

# Function to perform garbage collection (remove obsolete versions)
def garbage_collect():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    current_time = time.time()
    # Delete versions that are no longer valid and not the latest
    cursor.execute(f"""
        DELETE FROM {VERSION_TABLE}
        WHERE valid_to < ? AND id = 1;
    """, (current_time,))
    conn.commit()
    conn.close()

# Main function to run the simulation
def main():
    setup_database()
    
    # Create threads for Transaction A and Transaction B
    thread_a = threading.Thread(target=transaction_a)
    thread_b = threading.Thread(target=transaction_b)
    
    # Start the transactions
    thread_a.start()
    time.sleep(0.5)  # Slight delay to overlap transactions
    thread_b.start()
    
    # Wait for both transactions to complete
    thread_a.join()
    thread_b.join()
    
    # Display all versions after transactions
    display_versions()
    
    # Perform garbage collection
    garbage_collect()
    
    # Display versions after garbage collection
    display_versions()
    
    print("\nDemo completed.")

if __name__ == "__main__":
    main()
