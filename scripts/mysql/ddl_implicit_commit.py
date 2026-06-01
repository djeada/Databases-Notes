"""
MySQL DDL Implicit Commit Demo

Goal: Demonstrate that DDL statements in MySQL implicitly commit the current
      transaction, so later ROLLBACK does not undo the earlier work.

Concept:
- InnoDB supports transactional DML such as INSERT, UPDATE, and DELETE.
- DDL such as CREATE TABLE causes an implicit commit before and after the statement.
- Many users assume "everything inside START TRANSACTION rolls back together";
  that is not true once MySQL DDL is involved.

Prerequisites:
- MySQL must be running and accessible
- Use scripts/setup/start_mysql.sh to start a local MySQL instance

Usage:
    python mysql/ddl_implicit_commit.py
"""
import mysql.connector
from mysql.connector import Error


DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "database": "testdb",
    "user": "testuser",
    "password": "testpass",
}


def create_connection():
    """Create a MySQL connection."""
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as exc:
        print(f"✗ Error connecting to MySQL: {exc}")
        return None


if __name__ == "__main__":
    conn = create_connection()
    if conn is None:
        raise SystemExit(1)

    cursor = conn.cursor()
    try:
        cursor.execute("DROP TABLE IF EXISTS ddl_commit_demo;")
        cursor.execute("DROP TABLE IF EXISTS ddl_side_effect;")
        cursor.execute(
            """
            CREATE TABLE ddl_commit_demo (
                id INT AUTO_INCREMENT PRIMARY KEY,
                note VARCHAR(100) NOT NULL
            ) ENGINE=InnoDB;
            """
        )
        conn.commit()

        print("--- Starting transaction ---")
        cursor.execute("START TRANSACTION;")
        cursor.execute("INSERT INTO ddl_commit_demo (note) VALUES ('inserted before DDL');")
        print("Inserted one row into ddl_commit_demo")

        cursor.execute(
            """
            CREATE TABLE ddl_side_effect (
                id INT AUTO_INCREMENT PRIMARY KEY,
                note VARCHAR(100) NOT NULL
            ) ENGINE=InnoDB;
            """
        )
        print("Created ddl_side_effect inside the same transaction")

        conn.rollback()
        print("Issued ROLLBACK")

        cursor.execute("SELECT COUNT(*) FROM ddl_commit_demo;")
        persisted_rows = cursor.fetchone()[0]
        cursor.execute("SHOW TABLES LIKE 'ddl_side_effect';")
        side_effect_exists = cursor.fetchone() is not None

        print(f"Rows still present in ddl_commit_demo: {persisted_rows}")
        print(f"ddl_side_effect still exists: {side_effect_exists}")
        print("\nTakeaway: MySQL DDL implicitly commits the transaction.")
        print("Do not expect CREATE/ALTER/DROP TABLE to roll back with surrounding DML.")
    finally:
        cursor.execute("DROP TABLE IF EXISTS ddl_side_effect;")
        cursor.execute("DROP TABLE IF EXISTS ddl_commit_demo;")
        conn.commit()
        cursor.close()
        conn.close()
