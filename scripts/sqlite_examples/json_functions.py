"""
SQLite JSON Functions Demo

Goal: Demonstrate SQLite's JSON support for storing and querying semi-structured data
      without requiring a separate NoSQL database.

Concept:
- SQLite has built-in JSON functions since version 3.9.0
- Can store, query, and modify JSON data directly
- Supports JSON path expressions for extracting values
- Useful for flexible schemas and nested data

Usage:
    python sqlite_examples/json_functions.py
"""
import sqlite3
import json
import os

DB = 'json_demo.db'

def setup_database():
    """Create database with JSON data."""
    if os.path.exists(DB):
        os.remove(DB)
    
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    
    # Create table with JSON column
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            profile JSON
        );
    """)
    
    # Insert users with JSON profiles
    users_data = [
        ("Alice Smith", json.dumps({
            "age": 28,
            "email": "alice@example.com",
            "interests": ["databases", "python", "hiking"],
            "address": {
                "city": "Seattle",
                "state": "WA",
                "zip": "98101"
            }
        })),
        ("Bob Johnson", json.dumps({
            "age": 35,
            "email": "bob@example.com",
            "interests": ["sql", "optimization", "coffee"],
            "address": {
                "city": "Portland",
                "state": "OR",
                "zip": "97201"
            }
        })),
        ("Carol Davis", json.dumps({
            "age": 42,
            "email": "carol@example.com",
            "interests": ["nosql", "scaling", "databases"],
            "address": {
                "city": "San Francisco",
                "state": "CA",
                "zip": "94102"
            }
        })),
    ]
    
    cursor.executemany(
        "INSERT INTO users (name, profile) VALUES (?, ?)",
        users_data
    )
    
    conn.commit()
    print("✓ Database initialized with JSON data\n")
    return conn

def demo_extract_json(conn):
    """Demonstrate extracting values from JSON."""
    print("--- Demo: Extract JSON Values ---")
    cursor = conn.cursor()
    
    print("Extracting email and city from JSON profiles:\n")
    
    cursor.execute("""
        SELECT 
            name,
            json_extract(profile, '$.email') as email,
            json_extract(profile, '$.address.city') as city
        FROM users
        ORDER BY name;
    """)
    
    print(f"{'Name':<20} {'Email':<25} {'City':<15}")
    print("-" * 60)
    
    for name, email, city in cursor.fetchall():
        print(f"{name:<20} {email:<25} {city:<15}")

def demo_filter_by_json(conn):
    """Demonstrate filtering using JSON values."""
    print("\n\n--- Demo: Filter by JSON Values ---")
    cursor = conn.cursor()
    
    print("Finding users older than 30:\n")
    
    cursor.execute("""
        SELECT 
            name,
            json_extract(profile, '$.age') as age,
            json_extract(profile, '$.email') as email
        FROM users
        WHERE json_extract(profile, '$.age') > 30
        ORDER BY age;
    """)
    
    for name, age, email in cursor.fetchall():
        print(f"  • {name} (age {age}) - {email}")

def demo_json_array(conn):
    """Demonstrate working with JSON arrays."""
    print("\n\n--- Demo: Query JSON Arrays ---")
    cursor = conn.cursor()
    
    print("Finding users interested in 'databases':\n")
    
    cursor.execute("""
        SELECT 
            name,
            profile
        FROM users
        WHERE EXISTS (
            SELECT 1
            FROM json_each(profile, '$.interests')
            WHERE json_each.value = 'databases'
        );
    """)
    
    for name, profile_json in cursor.fetchall():
        profile = json.loads(profile_json)
        interests = ", ".join(profile['interests'])
        print(f"  • {name}")
        print(f"    Interests: {interests}")

def demo_json_modify(conn):
    """Demonstrate modifying JSON data."""
    print("\n\n--- Demo: Modify JSON Data ---")
    cursor = conn.cursor()
    
    print("Adding 'premium' flag to Alice's profile...\n")
    
    cursor.execute("""
        UPDATE users
        SET profile = json_set(profile, '$.premium', true)
        WHERE name = 'Alice Smith';
    """)
    conn.commit()
    
    cursor.execute("""
        SELECT name, profile
        FROM users
        WHERE name = 'Alice Smith';
    """)
    
    name, profile_json = cursor.fetchone()
    profile = json.loads(profile_json)
    
    print(f"Updated profile for {name}:")
    print(f"  Premium: {profile.get('premium', False)}")
    print(f"  Email: {profile['email']}")

def demo_json_aggregate(conn):
    """Demonstrate creating JSON from query results."""
    print("\n\n--- Demo: Create JSON from Query Results ---")
    cursor = conn.cursor()
    
    print("Creating a JSON array of all users in Washington and Oregon:\n")
    
    cursor.execute("""
        SELECT json_group_array(
            json_object(
                'name', name,
                'city', json_extract(profile, '$.address.city'),
                'state', json_extract(profile, '$.address.state')
            )
        ) as users_json
        FROM users
        WHERE json_extract(profile, '$.address.state') IN ('WA', 'OR');
    """)
    
    (users_json,) = cursor.fetchone()
    users = json.loads(users_json)
    
    print(json.dumps(users, indent=2))

def demo_json_tree(conn):
    """Demonstrate exploring JSON structure."""
    print("\n\n--- Demo: Explore JSON Structure ---")
    cursor = conn.cursor()
    
    print("Exploring Alice's profile structure:\n")
    
    cursor.execute("""
        SELECT 
            key,
            value,
            type
        FROM users, json_tree(users.profile)
        WHERE users.name = 'Alice Smith'
          AND json_tree.type != 'object'
        ORDER BY json_tree.path;
    """)
    
    print(f"{'Path':<30} {'Value':<30} {'Type':<10}")
    print("-" * 70)
    
    for key, value, value_type in cursor.fetchall():
        if value:
            print(f"{key:<30} {str(value):<30} {value_type:<10}")

def cleanup():
    """Remove the demo database."""
    if os.path.exists(DB):
        os.remove(DB)
        print("\n\n✓ Cleanup complete - database removed")

def main():
    """Run all JSON demonstrations."""
    conn = setup_database()
    
    try:
        demo_extract_json(conn)
        demo_filter_by_json(conn)
        demo_json_array(conn)
        demo_json_modify(conn)
        demo_json_aggregate(conn)
        demo_json_tree(conn)
    finally:
        conn.close()
        cleanup()

if __name__ == '__main__':
    main()
