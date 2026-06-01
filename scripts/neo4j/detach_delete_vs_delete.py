"""
Neo4j DETACH DELETE vs DELETE

Goal: Demonstrate that `DELETE` fails on nodes that still have relationships,
      while `DETACH DELETE` removes the node and its attached relationships.

Concept:
- `DELETE` works only when the target node has no remaining relationships.
- Neo4j protects graph integrity and raises an error otherwise.
- `DETACH DELETE` is the explicit way to remove both the node and its edges.

Prerequisites:
- Neo4j must be running and accessible
- Use scripts/setup/start_neo4j.sh to start a local Neo4j instance

Usage:
    python neo4j/detach_delete_vs_delete.py
"""
from neo4j import GraphDatabase
from neo4j.exceptions import AuthError, Neo4jError, ServiceUnavailable

URI = "bolt://127.0.0.1:7687"
AUTH = ("neo4j", "testpass")
DATABASE = "neo4j"


def create_driver():
    """Create a Neo4j driver and verify connectivity."""
    try:
        driver = GraphDatabase.driver(URI, auth=AUTH)
        driver.verify_connectivity()
        return driver
    except (AuthError, ServiceUnavailable, Neo4jError) as exc:
        print(f"✗ Error connecting to Neo4j: {exc}")
        return None


def cleanup(driver) -> None:
    """Remove demo data so reruns stay predictable."""
    with driver.session(database=DATABASE) as session:
        session.run("MATCH (n) DETACH DELETE n;")


if __name__ == "__main__":
    driver = create_driver()
    if driver is None:
        raise SystemExit(1)

    try:
        cleanup(driver)
        with driver.session(database=DATABASE) as session:
            session.run(
                """
                CREATE (:Person {name: 'Ada'})-[:KNOWS]->(:Person {name: 'Grace'});
                """
            )

        print("--- Attempting plain DELETE on a node with relationships ---")
        try:
            with driver.session(database=DATABASE) as session:
                session.run("MATCH (p:Person {name: 'Ada'}) DELETE p;").consume()
        except Neo4jError as exc:
            print(f"DELETE failed as expected: {exc.message}")

        print("\n--- Using DETACH DELETE instead ---")
        with driver.session(database=DATABASE) as session:
            session.run("MATCH (p:Person {name: 'Ada'}) DETACH DELETE p;").consume()
            remaining_nodes = session.run(
                "MATCH (n) RETURN count(n) AS count;"
            ).single()["count"]
            remaining_relationships = session.run(
                "MATCH ()-[r]->() RETURN count(r) AS count;"
            ).single()["count"]

        print(f"Remaining nodes: {remaining_nodes}")
        print(f"Remaining relationships: {remaining_relationships}")
        print("\nTakeaway: use DELETE only for detached nodes.")
        print("Use DETACH DELETE when you intend to remove attached relationships too.")
    except Neo4jError as exc:
        print(f"✗ Neo4j operation failed: {exc}")
        raise SystemExit(1)
    finally:
        cleanup(driver)
        driver.close()
