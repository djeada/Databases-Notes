"""Document modeling demo: embedded order lines and historical snapshots.

Prerequisites:
    cd scripts
    bash setup/start_mongo.sh
    cd ..

Run:
    python scripts/mongo/nosql_document_modeling.py
"""
from pymongo import ASCENDING, DESCENDING, MongoClient

MONGO_URI = "mongodb://mongoadmin:secret@127.0.0.1:27017/?authSource=admin"
DB_NAME = "testdb"


def main() -> None:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    db = client[DB_NAME]

    products = db["nosql_products"]
    orders = db["nosql_orders"]
    products.drop()
    orders.drop()

    products.insert_many(
        [
            {
                "_id": "book-101",
                "title": "Database Systems",
                "price_cents": 4990,
                "tags": ["database", "systems"],
            },
            {
                "_id": "book-205",
                "title": "Distributed Data",
                "price_cents": 3500,
                "tags": ["distributed", "nosql"],
            },
        ]
    )

    orders.insert_one(
        {
            "_id": "order-1001",
            "customer_id": "customer-42",
            "placed_at": "2026-10-01T12:00:00Z",
            "status": "placed",
            "items": [
                {
                    "product_id": "book-101",
                    "title_at_purchase": "Database Systems",
                    "unit_price_cents": 4990,
                    "quantity": 1,
                },
                {
                    "product_id": "book-205",
                    "title_at_purchase": "Distributed Data",
                    "unit_price_cents": 3500,
                    "quantity": 2,
                },
            ],
        }
    )

    orders.create_index(
        [("customer_id", ASCENDING), ("placed_at", DESCENDING)]
    )

    print("Order as one aggregate:")
    print(orders.find_one({"_id": "order-1001"}))

    products.update_one(
        {"_id": "book-101"},
        {"$set": {"price_cents": 5190}},
    )

    print("\nCurrent product price:")
    print(products.find_one({"_id": "book-101"})["price_cents"])

    print("Historical order price stays unchanged:")
    order = orders.find_one({"_id": "order-1001"})
    print(order["items"][0]["unit_price_cents"])

    print("\nCustomer order query:")
    for row in orders.find(
        {"customer_id": "customer-42"},
        {"_id": 1, "placed_at": 1, "status": 1},
    ).sort("placed_at", DESCENDING):
        print(row)

    print("\nIndexes:")
    for index in orders.list_indexes():
        print(index["name"], index["key"])

    client.close()


if __name__ == "__main__":
    main()
