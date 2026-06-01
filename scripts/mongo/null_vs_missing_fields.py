"""
MongoDB null vs missing fields

Goal: Demonstrate that `{field: null}` matches both explicit `null` values and
      documents where the field is missing.

Concept:
- `{nickname: null}` does not mean "nickname is explicitly null".
- Add `$exists: true` when you only want explicit nulls.
- Use `$exists: false` when you only want missing fields.

Prerequisites:
- MongoDB must be running and accessible
- Use scripts/setup/start_mongo.sh to start a local MongoDB instance

Usage:
    python mongo/null_vs_missing_fields.py
"""
from pymongo import MongoClient
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError

MONGO_URI = "mongodb://mongoadmin:secret@127.0.0.1:27017/?authSource=admin"
DB_NAME = "testdb"
COLLECTION_NAME = "null_vs_missing_demo"


def create_client():
    """Create a MongoDB client and verify connectivity."""
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        return client
    except ServerSelectionTimeoutError as exc:
        print(f"✗ Error connecting to MongoDB: {exc}")
        return None


def print_matches(collection, label: str, query: dict) -> None:
    """Print matching documents for a query."""
    rows = list(
        collection.find(query, {"_id": 1, "name": 1, "nickname": 1}).sort("_id", 1)
    )
    print(label)
    for row in rows:
        print(f"  {row}")
    if not rows:
        print("  <no matches>")
    print()


if __name__ == "__main__":
    client = create_client()
    if client is None:
        raise SystemExit(1)

    collection = client[DB_NAME][COLLECTION_NAME]
    try:
        collection.drop()
        collection.insert_many(
            [
                {"_id": 1, "name": "Alice", "nickname": None},
                {"_id": 2, "name": "Bob"},
                {"_id": 3, "name": "Carol", "nickname": "carolyn"},
            ]
        )

        print("--- Stored documents ---")
        print_matches(collection, "All rows:", {})

        print_matches(
            collection,
            "Query 1: {nickname: null} matches explicit null AND missing fields",
            {"nickname": None},
        )
        print_matches(
            collection,
            "Query 2: explicit null only",
            {"$and": [{"nickname": None}, {"nickname": {"$exists": True}}]},
        )
        print_matches(
            collection,
            "Query 3: missing field only",
            {"nickname": {"$exists": False}},
        )

        print("Takeaway: `{field: null}` is broader than many people expect.")
        print("Use `$exists` whenever null and missing must be distinguished.")
    except PyMongoError as exc:
        print(f"✗ MongoDB operation failed: {exc}")
        raise SystemExit(1)
    finally:
        collection.drop()
        client.close()
