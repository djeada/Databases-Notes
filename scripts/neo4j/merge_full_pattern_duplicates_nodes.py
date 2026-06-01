"""
Neo4j MERGE on a full pattern can duplicate nodes

Goal: Demonstrate that `MERGE` on an entire pattern can create duplicate nodes
      when you really meant to reuse existing nodes and create only a relation.

Concept:
- `MERGE (a)-[:REL]->(b)` matches or creates the whole pattern.
- If `a` and `b` are not already bound in the query, Neo4j may create new
  nodes even when matching nodes already exist separately.
- The safer pattern is to `MERGE` the nodes first, then `MERGE` the
  relationship between those bound nodes.

Prerequisites:
- Neo4j must be running and accessible
- Use scripts/setup/start_neo4j.sh to start a local Neo4j instance

Usage:
    python neo4j/merge_full_pattern_duplicates_nodes.py
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


def print_person_counts(driver, label: str) -> None:
    """Print the current number of Ada and Grace nodes."""
    with driver.session(database=DATABASE) as session:
        ada_count = session.run(
            "MATCH (:Person {name: 'Ada'}) RETURN count(*) AS count;"
        ).single()["count"]
        grace_count = session.run(
            "MATCH (:Person {name: 'Grace'}) RETURN count(*) AS count;"
        ).single()["count"]
        rel_count = session.run(
            "MATCH (:Person {name: 'Ada'})-[r:KNOWS]->(:Person {name: 'Grace'}) "
            "RETURN count(r) AS count;"
        ).single()["count"]
    print(f"{label}: Ada nodes={ada_count}, Grace nodes={grace_count}, KNOWS rels={rel_count}")


if __name__ == "__main__":
    driver = create_driver()
    if driver is None:
        raise SystemExit(1)

    try:
        cleanup(driver)
        with driver.session(database=DATABASE) as session:
            session.run("CREATE (:Person {name: 'Ada'}), (:Person {name: 'Grace'});")

        print("--- Starting graph with one Ada and one Grace ---")
        print_person_counts(driver, "Before full-pattern MERGE")

        with driver.session(database=DATABASE) as session:
            session.run(
                """
                MERGE (:Person {name: 'Ada'})-[:KNOWS]->(:Person {name: 'Grace'});
                """
            )

        print_person_counts(driver, "After full-pattern MERGE")

        print("\nResetting data to show the safer approach...")
        cleanup(driver)
        with driver.session(database=DATABASE) as session:
            session.run("CREATE (:Person {name: 'Ada'}), (:Person {name: 'Grace'});")
            session.run("MERGE (:Person {name: 'Ada'});")
            session.run("MERGE (:Person {name: 'Grace'});")
            session.run(
                """
                MATCH (ada:Person {name: 'Ada'}), (grace:Person {name: 'Grace'})
                MERGE (ada)-[:KNOWS]->(grace);
                """
            )

        print_person_counts(driver, "After separate node MERGE + relationship MERGE")
        print("\nTakeaway: MERGE on a whole pattern is not the same as")
        print("MERGE the nodes first, then MERGE only the relationship.")
    except Neo4jError as exc:
        print(f"✗ Neo4j operation failed: {exc}")
        raise SystemExit(1)
    finally:
        cleanup(driver)
        driver.close()
