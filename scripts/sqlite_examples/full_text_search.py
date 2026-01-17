"""
SQLite Full-Text Search (FTS5) Demo

Goal: Demonstrate SQLite's powerful full-text search capabilities using FTS5
      for searching large text collections efficiently.

Concept:
- FTS5 is SQLite's full-text search extension
- Supports phrase queries, prefix matching, and NEAR operator
- Much faster than LIKE for text searches
- Includes built-in ranking and highlighting

Usage:
    python sqlite_examples/full_text_search.py
"""
import sqlite3
import os

DB = 'fts_demo.db'

def setup_database():
    """Create database with FTS5 table and sample data."""
    if os.path.exists(DB):
        os.remove(DB)
    
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    
    # Create FTS5 virtual table
    cursor.execute("""
        CREATE VIRTUAL TABLE articles USING fts5(
            title,
            content,
            author,
            tokenize = 'porter unicode61'
        );
    """)
    
    # Insert sample articles
    articles_data = [
        ("Introduction to Databases", 
         "Databases are organized collections of data that can be easily accessed, managed, and updated. "
         "Relational databases use tables with rows and columns.",
         "Alice Smith"),
        ("SQL Query Optimization", 
         "Query optimization is crucial for database performance. Proper indexing and query structure "
         "can dramatically improve response times.",
         "Bob Johnson"),
        ("NoSQL Databases Explained",
         "NoSQL databases provide flexible schemas and horizontal scaling. Popular options include "
         "MongoDB, Cassandra, and Redis.",
         "Carol Davis"),
        ("Database Indexing Strategies",
         "Indexes speed up data retrieval but slow down writes. B-tree and hash indexes serve different purposes.",
         "Alice Smith"),
        ("Understanding Transactions",
         "Database transactions ensure data integrity through ACID properties: Atomicity, Consistency, "
         "Isolation, and Durability.",
         "Bob Johnson"),
    ]
    
    cursor.executemany(
        "INSERT INTO articles (title, content, author) VALUES (?, ?, ?)",
        articles_data
    )
    
    conn.commit()
    print("✓ Database initialized with FTS5 table and sample articles\n")
    return conn

def demo_basic_search(conn):
    """Demonstrate basic full-text search."""
    print("--- Demo: Basic Full-Text Search ---")
    cursor = conn.cursor()
    
    search_term = "database"
    print(f"Searching for: '{search_term}'")
    
    cursor.execute("""
        SELECT title, author, snippet(articles, 1, '<b>', '</b>', '...', 15) as snippet
        FROM articles
        WHERE articles MATCH ?
        ORDER BY rank;
    """, (search_term,))
    
    results = cursor.fetchall()
    print(f"\nFound {len(results)} result(s):\n")
    
    for i, (title, author, snippet) in enumerate(results, 1):
        print(f"{i}. {title} (by {author})")
        print(f"   ...{snippet}...\n")

def demo_phrase_search(conn):
    """Demonstrate phrase search."""
    print("\n--- Demo: Phrase Search ---")
    cursor = conn.cursor()
    
    phrase = '"query optimization"'
    print(f"Searching for exact phrase: {phrase}")
    
    cursor.execute("""
        SELECT title, content
        FROM articles
        WHERE articles MATCH ?;
    """, (phrase,))
    
    results = cursor.fetchall()
    print(f"\nFound {len(results)} result(s):\n")
    
    for title, content in results:
        print(f"• {title}")
        print(f"  {content[:100]}...\n")

def demo_boolean_search(conn):
    """Demonstrate boolean operators."""
    print("\n--- Demo: Boolean Search (AND, OR, NOT) ---")
    cursor = conn.cursor()
    
    # AND operator
    query = "database AND indexing"
    print(f"Searching for: {query}")
    
    cursor.execute("""
        SELECT title, author
        FROM articles
        WHERE articles MATCH ?;
    """, (query,))
    
    results = cursor.fetchall()
    print(f"Found {len(results)} result(s):")
    for title, author in results:
        print(f"  • {title} (by {author})")
    
    # NOT operator
    print(f"\nSearching for: database NOT NoSQL")
    cursor.execute("""
        SELECT title
        FROM articles
        WHERE articles MATCH 'database NOT NoSQL';
    """)
    
    results = cursor.fetchall()
    print(f"Found {len(results)} result(s):")
    for (title,) in results:
        print(f"  • {title}")

def demo_prefix_search(conn):
    """Demonstrate prefix matching."""
    print("\n\n--- Demo: Prefix Search ---")
    cursor = conn.cursor()
    
    prefix = "optim*"
    print(f"Searching for words starting with: {prefix}")
    
    cursor.execute("""
        SELECT title, snippet(articles, 1, '[', ']', '...', 10) as snippet
        FROM articles
        WHERE articles MATCH ?;
    """, (prefix,))
    
    results = cursor.fetchall()
    print(f"\nFound {len(results)} result(s):\n")
    
    for title, snippet in results:
        print(f"• {title}")
        print(f"  ...{snippet}...\n")

def demo_author_search(conn):
    """Demonstrate column-specific search."""
    print("\n--- Demo: Column-Specific Search ---")
    cursor = conn.cursor()
    
    author_query = "author: Alice"
    print(f"Searching for: {author_query}")
    
    cursor.execute("""
        SELECT title, author
        FROM articles
        WHERE articles MATCH ?
        ORDER BY title;
    """, (author_query,))
    
    results = cursor.fetchall()
    print(f"\nFound {len(results)} result(s):\n")
    
    for title, author in results:
        print(f"• {title} (by {author})")

def cleanup():
    """Remove the demo database."""
    if os.path.exists(DB):
        os.remove(DB)
        print("\n\n✓ Cleanup complete - database removed")

def main():
    """Run all FTS5 demonstrations."""
    conn = setup_database()
    
    try:
        demo_basic_search(conn)
        demo_phrase_search(conn)
        demo_boolean_search(conn)
        demo_prefix_search(conn)
        demo_author_search(conn)
    finally:
        conn.close()
        cleanup()

if __name__ == '__main__':
    main()
