"""
MySQL Stored Procedures Demo

Goal: Demonstrate how to create and use stored procedures in MySQL to encapsulate
      complex business logic and improve code reusability.

Concept:
- Stored procedures are precompiled SQL statements stored in the database
- They can accept parameters, contain control flow logic, and return results
- Benefits: Performance, security, maintainability, reduced network traffic

Prerequisites:
- MySQL must be running and accessible
- Use scripts/setup/start_mysql.sh to start a local MySQL instance

Usage:
    python mysql_examples/stored_procedures.py
"""
import mysql.connector
from mysql.connector import Error

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
    """Create demo tables and stored procedures."""
    cursor = conn.cursor()
    
    try:
        # Drop existing objects
        cursor.execute("DROP PROCEDURE IF EXISTS calculate_order_total;")
        cursor.execute("DROP PROCEDURE IF EXISTS get_customer_orders;")
        cursor.execute("DROP TABLE IF EXISTS order_items;")
        cursor.execute("DROP TABLE IF EXISTS orders;")
        cursor.execute("DROP TABLE IF EXISTS customers;")
        
        # Create tables
        cursor.execute("""
            CREATE TABLE customers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL
            );
        """)
        
        cursor.execute("""
            CREATE TABLE orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                customer_id INT NOT NULL,
                order_date DATE NOT NULL,
                total DECIMAL(10, 2) DEFAULT 0.00,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            );
        """)
        
        cursor.execute("""
            CREATE TABLE order_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                order_id INT NOT NULL,
                product_name VARCHAR(100) NOT NULL,
                quantity INT NOT NULL,
                price DECIMAL(10, 2) NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id)
            );
        """)
        
        # Insert sample data
        cursor.execute("""
            INSERT INTO customers (name, email) VALUES
            ('Alice Smith', 'alice@example.com'),
            ('Bob Jones', 'bob@example.com'),
            ('Carol White', 'carol@example.com');
        """)
        
        cursor.execute("""
            INSERT INTO orders (customer_id, order_date) VALUES
            (1, '2024-01-15'),
            (1, '2024-02-20'),
            (2, '2024-01-18');
        """)
        
        cursor.execute("""
            INSERT INTO order_items (order_id, product_name, quantity, price) VALUES
            (1, 'Widget A', 2, 19.99),
            (1, 'Widget B', 1, 29.99),
            (2, 'Widget C', 3, 9.99),
            (3, 'Widget A', 1, 19.99);
        """)
        
        # Create stored procedure to calculate order total
        cursor.execute("""
            CREATE PROCEDURE calculate_order_total(IN p_order_id INT)
            BEGIN
                DECLARE v_total DECIMAL(10, 2);
                
                SELECT SUM(quantity * price) INTO v_total
                FROM order_items
                WHERE order_id = p_order_id;
                
                UPDATE orders
                SET total = IFNULL(v_total, 0.00)
                WHERE id = p_order_id;
                
                SELECT v_total AS order_total;
            END;
        """)
        
        # Create stored procedure to get customer orders
        cursor.execute("""
            CREATE PROCEDURE get_customer_orders(IN p_customer_id INT)
            BEGIN
                SELECT 
                    o.id AS order_id,
                    o.order_date,
                    o.total,
                    COUNT(oi.id) AS item_count
                FROM orders o
                LEFT JOIN order_items oi ON o.id = oi.order_id
                WHERE o.customer_id = p_customer_id
                GROUP BY o.id, o.order_date, o.total
                ORDER BY o.order_date DESC;
            END;
        """)
        
        conn.commit()
        print("✓ Demo tables and stored procedures created")
        
    except Error as e:
        print(f"✗ Error setting up demo: {e}")
        conn.rollback()
    finally:
        cursor.close()

def demo_calculate_order_total(conn):
    """Demonstrate calculating order totals using stored procedure."""
    print("\n--- Demo: Calculate Order Total ---")
    cursor = conn.cursor()
    
    try:
        order_id = 1
        print(f"Calculating total for order #{order_id}...")
        
        cursor.callproc('calculate_order_total', [order_id])
        
        # Fetch the result
        for result in cursor.stored_results():
            for (total,) in result:
                print(f"  Order #{order_id} total: ${total:.2f}")
        
        conn.commit()
        print("✓ Order total calculated and updated")
        
    except Error as e:
        print(f"✗ Error: {e}")
    finally:
        cursor.close()

def demo_get_customer_orders(conn):
    """Demonstrate retrieving customer orders using stored procedure."""
    print("\n--- Demo: Get Customer Orders ---")
    cursor = conn.cursor()
    
    try:
        customer_id = 1
        print(f"Retrieving orders for customer #{customer_id}...")
        
        cursor.callproc('get_customer_orders', [customer_id])
        
        # Fetch the results
        for result in cursor.stored_results():
            print(f"\n  {'Order ID':<10} {'Date':<12} {'Total':<10} {'Items':<10}")
            print("  " + "-" * 42)
            for (order_id, order_date, total, item_count) in result:
                print(f"  {order_id:<10} {str(order_date):<12} ${total:<9.2f} {item_count:<10}")
        
        print("✓ Customer orders retrieved")
        
    except Error as e:
        print(f"✗ Error: {e}")
    finally:
        cursor.close()

def cleanup_demo(conn):
    """Clean up demo tables and procedures."""
    cursor = conn.cursor()
    try:
        cursor.execute("DROP PROCEDURE IF EXISTS calculate_order_total;")
        cursor.execute("DROP PROCEDURE IF EXISTS get_customer_orders;")
        cursor.execute("DROP TABLE IF EXISTS order_items;")
        cursor.execute("DROP TABLE IF EXISTS orders;")
        cursor.execute("DROP TABLE IF EXISTS customers;")
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
        demo_calculate_order_total(conn)
        demo_get_customer_orders(conn)
        cleanup_demo(conn)
    finally:
        if conn.is_connected():
            conn.close()
            print("✓ Database connection closed")

if __name__ == '__main__':
    main()
