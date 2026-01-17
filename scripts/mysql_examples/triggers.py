"""
MySQL Triggers Demo

Goal: Demonstrate how triggers automatically execute in response to database events,
      useful for maintaining audit trails, enforcing business rules, and data validation.

Concept:
- Triggers are stored procedures that automatically execute before or after INSERT, UPDATE, or DELETE
- BEFORE triggers: Can modify the new row before it's written
- AFTER triggers: Used for audit logs, cascading updates, validation

Prerequisites:
- MySQL must be running and accessible
- Use scripts/setup/start_mysql.sh to start a local MySQL instance

Usage:
    python mysql_examples/triggers.py
"""
import mysql.connector
from mysql.connector import Error
from datetime import datetime

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
            print("✓ Connected to MySQL database")
            return conn
    except Error as e:
        print(f"✗ Error connecting to MySQL: {e}")
        return None

def setup_demo(conn):
    """Create demo tables and triggers."""
    cursor = conn.cursor()
    
    try:
        # Drop existing objects
        cursor.execute("DROP TRIGGER IF EXISTS before_product_update;")
        cursor.execute("DROP TRIGGER IF EXISTS after_product_insert;")
        cursor.execute("DROP TRIGGER IF EXISTS after_product_delete;")
        cursor.execute("DROP TABLE IF EXISTS product_audit_log;")
        cursor.execute("DROP TABLE IF EXISTS products;")
        
        # Create products table
        cursor.execute("""
            CREATE TABLE products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                stock INT NOT NULL DEFAULT 0,
                last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            );
        """)
        
        # Create audit log table
        cursor.execute("""
            CREATE TABLE product_audit_log (
                id INT AUTO_INCREMENT PRIMARY KEY,
                product_id INT,
                action VARCHAR(20) NOT NULL,
                old_value TEXT,
                new_value TEXT,
                changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # BEFORE UPDATE trigger - Validate price changes
        cursor.execute("""
            CREATE TRIGGER before_product_update
            BEFORE UPDATE ON products
            FOR EACH ROW
            BEGIN
                IF NEW.price < 0 THEN
                    SIGNAL SQLSTATE '45000'
                    SET MESSAGE_TEXT = 'Price cannot be negative';
                END IF;
                
                IF NEW.stock < 0 THEN
                    SIGNAL SQLSTATE '45000'
                    SET MESSAGE_TEXT = 'Stock cannot be negative';
                END IF;
            END;
        """)
        
        # AFTER INSERT trigger - Log new products
        cursor.execute("""
            CREATE TRIGGER after_product_insert
            AFTER INSERT ON products
            FOR EACH ROW
            BEGIN
                INSERT INTO product_audit_log (product_id, action, new_value)
                VALUES (NEW.id, 'INSERT', 
                        CONCAT('name=', NEW.name, ', price=', NEW.price, ', stock=', NEW.stock));
            END;
        """)
        
        # AFTER DELETE trigger - Log deletions
        cursor.execute("""
            CREATE TRIGGER after_product_delete
            AFTER DELETE ON products
            FOR EACH ROW
            BEGIN
                INSERT INTO product_audit_log (product_id, action, old_value)
                VALUES (OLD.id, 'DELETE',
                        CONCAT('name=', OLD.name, ', price=', OLD.price, ', stock=', OLD.stock));
            END;
        """)
        
        conn.commit()
        print("✓ Demo tables and triggers created")
        
    except Error as e:
        print(f"✗ Error setting up demo: {e}")
        conn.rollback()
    finally:
        cursor.close()

def demo_insert_trigger(conn):
    """Demonstrate AFTER INSERT trigger logging."""
    print("\n--- Demo: INSERT Trigger (Audit Logging) ---")
    cursor = conn.cursor()
    
    try:
        print("Inserting new products...")
        cursor.execute("""
            INSERT INTO products (name, price, stock) VALUES
            ('Laptop', 999.99, 10),
            ('Mouse', 24.99, 50),
            ('Keyboard', 79.99, 30);
        """)
        conn.commit()
        print("✓ Products inserted")
        
        # Show audit log
        cursor.execute("SELECT * FROM product_audit_log ORDER BY changed_at;")
        results = cursor.fetchall()
        
        print("\nAudit Log:")
        print(f"  {'ID':<5} {'Product ID':<12} {'Action':<10} {'Details':<50}")
        print("  " + "-" * 77)
        for (log_id, product_id, action, old_val, new_val, changed_at) in results:
            value = new_val if new_val else old_val
            print(f"  {log_id:<5} {product_id:<12} {action:<10} {value:<50}")
        
    except Error as e:
        print(f"✗ Error: {e}")
        conn.rollback()
    finally:
        cursor.close()

def demo_update_trigger(conn):
    """Demonstrate BEFORE UPDATE trigger validation."""
    print("\n--- Demo: UPDATE Trigger (Validation) ---")
    cursor = conn.cursor()
    
    try:
        # Valid update
        print("Attempting valid price update...")
        cursor.execute("UPDATE products SET price = 899.99 WHERE name = 'Laptop';")
        conn.commit()
        print("✓ Valid update succeeded")
        
        # Invalid update (negative price)
        print("\nAttempting invalid update (negative price)...")
        try:
            cursor.execute("UPDATE products SET price = -100 WHERE name = 'Mouse';")
            conn.commit()
            print("✗ Invalid update should have been rejected!")
        except Error as e:
            print(f"✓ Trigger validation worked: {e.msg}")
            conn.rollback()
        
    except Error as e:
        print(f"✗ Error: {e}")
        conn.rollback()
    finally:
        cursor.close()

def demo_delete_trigger(conn):
    """Demonstrate AFTER DELETE trigger logging."""
    print("\n--- Demo: DELETE Trigger (Audit Logging) ---")
    cursor = conn.cursor()
    
    try:
        print("Deleting a product...")
        cursor.execute("DELETE FROM products WHERE name = 'Mouse';")
        conn.commit()
        print("✓ Product deleted")
        
        # Show latest audit log entry
        cursor.execute("""
            SELECT * FROM product_audit_log 
            WHERE action = 'DELETE' 
            ORDER BY changed_at DESC 
            LIMIT 1;
        """)
        result = cursor.fetchone()
        
        if result:
            log_id, product_id, action, old_val, new_val, changed_at = result
            print(f"\nLatest Audit Log Entry:")
            print(f"  Action: {action}")
            print(f"  Product ID: {product_id}")
            print(f"  Details: {old_val}")
            print(f"  Time: {changed_at}")
        
    except Error as e:
        print(f"✗ Error: {e}")
        conn.rollback()
    finally:
        cursor.close()

def cleanup_demo(conn):
    """Clean up demo tables and triggers."""
    cursor = conn.cursor()
    try:
        cursor.execute("DROP TRIGGER IF EXISTS before_product_update;")
        cursor.execute("DROP TRIGGER IF EXISTS after_product_insert;")
        cursor.execute("DROP TRIGGER IF EXISTS after_product_delete;")
        cursor.execute("DROP TABLE IF EXISTS product_audit_log;")
        cursor.execute("DROP TABLE IF EXISTS products;")
        conn.commit()
        print("\n✓ Cleanup complete")
    except Error as e:
        print(f"✗ Error during cleanup: {e}")
    finally:
        cursor.close()

def main():
    """Main function to run all demonstrations."""
    conn = create_connection()
    if not conn:
        print("✗ Cannot proceed without database connection")
        return
    
    try:
        setup_demo(conn)
        demo_insert_trigger(conn)
        demo_update_trigger(conn)
        demo_delete_trigger(conn)
        cleanup_demo(conn)
    finally:
        if conn.is_connected():
            conn.close()
            print("✓ Database connection closed")

if __name__ == '__main__':
    main()
