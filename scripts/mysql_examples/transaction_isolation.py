"""
MySQL Transactions and Isolation Levels Demo

Goal: Demonstrate different transaction isolation levels in MySQL and their effects
      on concurrent transactions, preventing issues like dirty reads and phantom reads.

Concept:
- Isolation levels: READ UNCOMMITTED, READ COMMITTED, REPEATABLE READ, SERIALIZABLE
- Each level provides different trade-offs between consistency and concurrency
- MySQL default is REPEATABLE READ (with InnoDB engine)

Prerequisites:
- MySQL must be running and accessible
- Use scripts/setup/start_mysql.sh to start a local MySQL instance

Usage:
    python mysql_examples/transaction_isolation.py
"""
import mysql.connector
from mysql.connector import Error
import threading
import time

# Connection configuration
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'database': 'testdb',
    'user': 'testuser',
    'password': 'testpass'
}

def create_connection():
    """Create a database connection to MySQL."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"✗ Error connecting to MySQL: {e}")
        return None

def setup_demo():
    """Create demo table."""
    conn = create_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        cursor.execute("DROP TABLE IF EXISTS accounts;")
        
        cursor.execute("""
            CREATE TABLE accounts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                balance DECIMAL(10, 2) NOT NULL DEFAULT 0.00
            ) ENGINE=InnoDB;
        """)
        
        cursor.execute("""
            INSERT INTO accounts (name, balance) VALUES
            ('Alice', 1000.00),
            ('Bob', 1500.00);
        """)
        
        conn.commit()
        print("✓ Demo table created\n")
        return True
        
    except Error as e:
        print(f"✗ Error setting up demo: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def demo_read_uncommitted():
    """Demonstrate READ UNCOMMITTED - allows dirty reads."""
    print("--- Demo: READ UNCOMMITTED (Dirty Reads) ---\n")
    
    def transaction1():
        conn = create_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;")
            cursor.execute("START TRANSACTION;")
            print("[T1] Started transaction (READ UNCOMMITTED)")
            
            # Update but don't commit
            cursor.execute("UPDATE accounts SET balance = balance + 500 WHERE name = 'Alice';")
            print("[T1] Updated Alice's balance (uncommitted)")
            
            time.sleep(2)  # Give T2 time to read
            
            # Rollback the change
            conn.rollback()
            print("[T1] Rolled back transaction")
            
        except Error as e:
            print(f"[T1] Error: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def transaction2():
        time.sleep(0.5)  # Let T1 start first
        conn = create_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;")
            cursor.execute("START TRANSACTION;")
            
            # Read uncommitted data (dirty read)
            cursor.execute("SELECT balance FROM accounts WHERE name = 'Alice';")
            balance = cursor.fetchone()[0]
            print(f"[T2] Read Alice's balance: ${balance:.2f} (dirty read!)")
            
            conn.commit()
            print("[T2] Committed transaction")
            
        except Error as e:
            print(f"[T2] Error: {e}")
        finally:
            cursor.close()
            conn.close()
    
    t1 = threading.Thread(target=transaction1)
    t2 = threading.Thread(target=transaction2)
    
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    
    print("✓ Demo complete: T2 read uncommitted data that was later rolled back\n")

def demo_read_committed():
    """Demonstrate READ COMMITTED - prevents dirty reads."""
    print("\n--- Demo: READ COMMITTED (No Dirty Reads) ---\n")
    
    def transaction1():
        conn = create_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
            cursor.execute("START TRANSACTION;")
            print("[T1] Started transaction (READ COMMITTED)")
            
            cursor.execute("UPDATE accounts SET balance = balance + 500 WHERE name = 'Bob';")
            print("[T1] Updated Bob's balance (uncommitted)")
            
            time.sleep(2)  # Give T2 time to try reading
            
            conn.commit()
            print("[T1] Committed transaction")
            
        except Error as e:
            print(f"[T1] Error: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def transaction2():
        time.sleep(0.5)
        conn = create_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;")
            cursor.execute("START TRANSACTION;")
            
            # This will wait for T1's commit
            print("[T2] Attempting to read Bob's balance...")
            cursor.execute("SELECT balance FROM accounts WHERE name = 'Bob';")
            balance = cursor.fetchone()[0]
            print(f"[T2] Read Bob's balance: ${balance:.2f} (after T1 committed)")
            
            conn.commit()
            
        except Error as e:
            print(f"[T2] Error: {e}")
        finally:
            cursor.close()
            conn.close()
    
    t1 = threading.Thread(target=transaction1)
    t2 = threading.Thread(target=transaction2)
    
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    
    print("✓ Demo complete: T2 waited for T1 to commit (no dirty read)\n")

def demo_repeatable_read():
    """Demonstrate REPEATABLE READ - consistent reads within transaction."""
    print("\n--- Demo: REPEATABLE READ (Consistent Snapshot) ---\n")
    
    def transaction1():
        conn = create_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ;")
            cursor.execute("START TRANSACTION;")
            print("[T1] Started transaction (REPEATABLE READ)")
            
            # First read
            cursor.execute("SELECT balance FROM accounts WHERE name = 'Alice';")
            balance1 = cursor.fetchone()[0]
            print(f"[T1] First read - Alice's balance: ${balance1:.2f}")
            
            time.sleep(2)  # Let T2 make changes
            
            # Second read - should see same value
            cursor.execute("SELECT balance FROM accounts WHERE name = 'Alice';")
            balance2 = cursor.fetchone()[0]
            print(f"[T1] Second read - Alice's balance: ${balance2:.2f} (unchanged)")
            
            conn.commit()
            print("[T1] Committed transaction")
            
        except Error as e:
            print(f"[T1] Error: {e}")
        finally:
            cursor.close()
            conn.close()
    
    def transaction2():
        time.sleep(0.5)
        conn = create_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("START TRANSACTION;")
            print("[T2] Started transaction")
            
            cursor.execute("UPDATE accounts SET balance = balance - 100 WHERE name = 'Alice';")
            conn.commit()
            print("[T2] Updated and committed Alice's balance")
            
        except Error as e:
            print(f"[T2] Error: {e}")
        finally:
            cursor.close()
            conn.close()
    
    t1 = threading.Thread(target=transaction1)
    t2 = threading.Thread(target=transaction2)
    
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    
    print("✓ Demo complete: T1 saw consistent snapshot despite T2's changes\n")

def cleanup_demo():
    """Clean up demo table."""
    conn = create_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    try:
        cursor.execute("DROP TABLE IF EXISTS accounts;")
        conn.commit()
        print("\n✓ Cleanup complete")
    except Error as e:
        print(f"✗ Error during cleanup: {e}")
    finally:
        cursor.close()
        conn.close()

def main():
    """Run all isolation level demonstrations."""
    print("MySQL Transaction Isolation Levels Demo\n")
    print("=" * 50 + "\n")
    
    if not setup_demo():
        print("✗ Cannot proceed without database setup")
        return
    
    try:
        demo_read_uncommitted()
        setup_demo()  # Reset data
        
        demo_read_committed()
        setup_demo()  # Reset data
        
        demo_repeatable_read()
        
    finally:
        cleanup_demo()

if __name__ == '__main__':
    main()
