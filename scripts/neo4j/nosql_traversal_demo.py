"""Graph modeling demo: two-hop recommendation traversal.

Prerequisites:
    cd scripts
    bash setup/start_neo4j.sh
    cd ..

Run:
    python scripts/neo4j/nosql_traversal_demo.py
"""
from neo4j import GraphDatabase

URI = "bolt://127.0.0.1:7687"
AUTH = ("neo4j", "testpass")


def main() -> None:
    driver = GraphDatabase.driver(URI, auth=AUTH)
    driver.verify_connectivity()

    with driver.session(database="neo4j") as session:
        session.run("MATCH (n:NoSQLDemo) DETACH DELETE n")

        session.run(
            """
            CREATE (alice:NoSQLDemo:Customer {customer_id: 42, name: 'Alice'})
            CREATE (bob:NoSQLDemo:Customer {customer_id: 51, name: 'Bob'})
            CREATE (carol:NoSQLDemo:Customer {customer_id: 87, name: 'Carol'})
            CREATE (bookA:NoSQLDemo:Book {book_id: 101, title: 'Database Systems'})
            CREATE (bookB:NoSQLDemo:Book {book_id: 205, title: 'Distributed Data'})
            CREATE (alice)-[:FOLLOWS]->(bob)
            CREATE (alice)-[:FOLLOWS]->(carol)
            CREATE (bob)-[:LIKES]->(bookA)
            CREATE (carol)-[:LIKES]->(bookB)
            """
        )

        rows = session.run(
            """
            MATCH (:Customer:NoSQLDemo {customer_id: $customer_id})
                  -[:FOLLOWS]->(:Customer:NoSQLDemo)
                  -[:LIKES]->(book:Book:NoSQLDemo)
            RETURN DISTINCT book.book_id AS book_id, book.title AS title
            ORDER BY book_id
            """,
            customer_id=42,
        )

        print("Books liked by people Alice follows:")
        for row in rows:
            print(dict(row))

    driver.close()


if __name__ == "__main__":
    main()
