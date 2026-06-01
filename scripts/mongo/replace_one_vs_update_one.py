"""
MongoDB replace_one vs update_one($set)

Goal: Demonstrate that `replace_one()` swaps the entire document, while
      `update_one(..., {"$set": ...})` patches only the named fields.

Concept:
- `replace_one()` is a full-document replacement operation.
- `update_one()` requires update operators such as `$set`.
- Many people expect both calls to "just update one field", but they behave
  very differently.

Prerequisites:
- MongoDB must be running and accessible
- Use scripts/setup/start_mongo.sh to start a local MongoDB instance

Usage:
    python mongo/replace_one_vs_update_one.py
"""
from pymongo import MongoClient
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError

MONGO_URI = "mongodb://mongoadmin:secret@127.0.0.1:27017/?authSource=admin"
DB_NAME = "testdb"
COLLECTION_NAME = "replace_vs_update_demo"


def create_client():
    """Create a MongoDB client and verify connectivity."""
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        return client
    except ServerSelectionTimeoutError as exc:
        print(f"✗ Error connecting to MongoDB: {exc}")
        return None


def print_document(collection, label: str) -> None:
    """Print the current demo document."""
    document = collection.find_one({"_id": 1})
    print(f"{label}: {document}")


if __name__ == "__main__":
    client = create_client()
    if client is None:
        raise SystemExit(1)

    collection = client[DB_NAME][COLLECTION_NAME]
    try:
        collection.drop()
        original_document = {
            "_id": 1,
            "name": "Ada",
            "role": "Engineer",
            "favorite_topics": ["graphs", "distributed systems"],
            "preferences": {"dark_mode": True, "newsletter": True},
        }
        collection.insert_one(original_document)

        print("--- Starting document ---")
        print_document(collection, "Original")

        print("\n--- replace_one() swaps the whole document ---")
        collection.replace_one(
            {"_id": 1},
            {
                "_id": 1,
                "name": "Ada",
                "role": "Architect",
            },
        )
        print_document(collection, "After replace_one")

        print("\nResetting the original document...")
        collection.replace_one({"_id": 1}, original_document)
        print_document(collection, "Reset document")

        print("\n--- update_one() with $set changes only the named fields ---")
        collection.update_one(
            {"_id": 1},
            {"$set": {"role": "Architect"}},
        )
        print_document(collection, "After update_one + $set")

        print("\nTakeaway: use replace_one() only when you really mean to replace")
        print("the entire document. Use update operators such as $set for patches.")
    except PyMongoError as exc:
        print(f"✗ MongoDB operation failed: {exc}")
        raise SystemExit(1)
    finally:
        collection.drop()
        client.close()
