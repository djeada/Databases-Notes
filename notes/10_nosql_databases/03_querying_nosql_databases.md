# Querying NoSQL Databases: Query Shape Follows the Data Model

There is no universal NoSQL query language. A document database, key-value store, wide-column database, and graph database expose different query shapes because they organize data differently.

This note uses four concrete technologies already covered elsewhere in the repository:

- MongoDB for documents,
- Redis for key/value and data structures,
- Cassandra for wide-column query-first tables,
- Neo4j for graphs.

The goal is not to memorize syntax. It is to see how the **same business question changes when the data model changes**.

## One question, four models

Suppose a bookstore needs several operations:

1. load a product and its descriptive fields,
2. load a shopping cart by user ID,
3. read one customer's recent events,
4. traverse from a customer through followed customers to books they like.

Those operations naturally map to different query shapes.

```text
document    -> filter documents by fields
key-value   -> compute key, then fetch/update value
wide-column -> supply partition key, then range within partition
graph       -> match/traverse relationship pattern
```

A relational database may still solve all four well enough. Specialized systems are useful when the workload justifies them.

## MongoDB: query documents by fields

Example product document:

```json
{
  "_id": "book-101",
  "title": "Database Systems",
  "price_cents": 4990,
  "tags": ["database", "systems"],
  "publisher": {
    "name": "Example Press",
    "country": "DE"
  }
}
```

Exact lookup:

```javascript
db.products.findOne({ _id: "book-101" })
```

Filter by nested field:

```javascript
db.products.find({
  "publisher.country": "DE"
})
```

Array membership:

```javascript
db.products.find({
  tags: "database"
})
```

MongoDB query syntax expresses predicates over document fields and arrays.

## Projection

Return only required fields:

```javascript
db.products.find(
  { tags: "database" },
  { title: 1, price_cents: 1 }
)
```

Projection reduces network transfer and deserialization.

## Comparison operators

```javascript
db.products.find({
  price_cents: { $gte: 3000, $lt: 6000 }
})
```

Common operators include equality, range, membership, and logical combinations.

The exact index should follow the real filter/sort pattern.

## Compound filters

```javascript
db.orders.find({
  customer_id: "customer-42",
  status: "open",
  placed_at: {
    $gte: ISODate("2026-10-01T00:00:00Z")
  }
})
```

This query suggests an index beginning with fields used for equality and range/sort according to the measured workload.

## Sorting and limiting

```javascript
db.orders.find({
  customer_id: "customer-42"
})
.sort({ placed_at: -1 })
.limit(20)
```

A compound index such as:

```javascript
{ customer_id: 1, placed_at: -1 }
```

can support the access pattern.

Verify with `explain()`.

## Explain

```javascript
db.orders.find({
  customer_id: "customer-42"
})
.sort({ placed_at: -1 })
.explain("executionStats")
```

Inspect:

- documents returned,
- keys examined,
- documents examined,
- chosen index/scan stage.

Do not treat an index name alone as proof of efficiency.

## Aggregation pipeline

MongoDB aggregation processes documents through stages.

Example:

```javascript
db.orders.aggregate([
  {
    $match: {
      status: "paid"
    }
  },
  {
    $group: {
      _id: "$customer_id",
      orders: { $sum: 1 },
      revenue_cents: { $sum: "$total_cents" }
    }
  },
  {
    $sort: {
      revenue_cents: -1
    }
  }
])
```

Conceptually:

```text
documents
   |
   v
$match
   |
   v
$group
   |
   v
$sort
```

Aggregation pipelines are powerful, but broad analytical scans may belong in an analytical system when volume/workload requires it.

## Embedded arrays

Suppose an order embeds items:

```json
{
  "_id": "order-1001",
  "items": [
    {"product_id": "book-101", "quantity": 1},
    {"product_id": "book-205", "quantity": 2}
  ]
}
```

Find orders containing a product:

```javascript
db.orders.find({
  "items.product_id": "book-101"
})
```

An array index can support the access pattern, with write/index-size cost.

## Missing versus null

Document queries may distinguish a missing field from an explicit null.

The repository includes:

[`scripts/mongo/null_vs_missing_fields.py`](../../scripts/mongo/null_vs_missing_fields.py)

Run it against the local MongoDB setup to observe the difference.

## Replacement versus partial update

MongoDB provides both whole-document replacement and operator-based updates.

Repository demo:

[`scripts/mongo/replace_one_vs_update_one.py`](../../scripts/mongo/replace_one_vs_update_one.py)

A replacement can remove fields not included in the new document. `$set` updates selected paths.

## Document-modeling demo

The NoSQL chapter adds:

[`scripts/mongo/nosql_document_modeling.py`](../../scripts/mongo/nosql_document_modeling.py)

It demonstrates an embedded order aggregate and shows that a historical purchase price remains unchanged after the current product price changes.

Run:

```bash
cd scripts
bash setup/start_mongo.sh
cd ..
python scripts/mongo/nosql_document_modeling.py
```

## Redis: compute the key first

A key-value query often begins in application code:

```text
user ID = 42
key = cart:user:42
```

Then:

```text
HGETALL cart:user:42
```

Unlike MongoDB, the normal operation is not:

> search every cart document where customer_id = 42.

The key already encodes the lookup.

## Direct key lookup

```text
GET session:abc123
```

This is the natural key-value access pattern.

If an application repeatedly scans values to find matching properties, the model probably needs another maintained index or a different database.

## Atomic update

```text
INCR page:home:views
```

A server-side atomic command avoids application read-modify-write races.

## Set membership

```text
SISMEMBER team:7:members 42
```

or:

```text
SMEMBERS team:7:members
```

The data structure is part of the query model.

## Sorted-set ranking

```text
ZREVRANGE leaderboard:2026 0 9 WITHSCORES
```

The store can answer rank-oriented queries because the value is modeled as a sorted set.

## TTL

```text
SET session:abc123 "user=42" EX 3600
```

Expiration is part of the operation.

Query:

```text
TTL session:abc123
```

## Redis NoSQL exercise

Run:

```bash
cd scripts/redis
docker compose up -d
cat nosql_key_design.redis | docker exec -i redis-notes redis-cli
```

The file demonstrates namespaced keys, TTL, a cart hash, idempotency state, an atomic rate counter, and a sorted-set leaderboard.

## Cassandra: query the partition you designed

Wide-column querying is intentionally constrained by primary-key shape.

Table:

```sql
CREATE TABLE events_by_customer_month (
    customer_id text,
    bucket_month text,
    event_time timestamp,
    event_id uuid,
    event_type text,
    payload text,
    PRIMARY KEY (
        (customer_id, bucket_month),
        event_time,
        event_id
    )
) WITH CLUSTERING ORDER BY (event_time DESC);
```

Natural query:

```sql
SELECT *
FROM events_by_customer_month
WHERE customer_id = 'customer-42'
  AND bucket_month = '2026-10'
LIMIT 50;
```

The full partition key is known.

## Clustering range

Because `event_time` is a clustering column:

```sql
SELECT *
FROM events_by_customer_month
WHERE customer_id = 'customer-42'
  AND bucket_month = '2026-10'
  AND event_time >= '2026-10-01T00:00:00Z'
  AND event_time <  '2026-10-02T00:00:00Z';
```

This is query-first modeling: the table was built for that operation.

## Why arbitrary filtering is different

A request such as:

```text
find every event in the cluster whose payload contains "database"
```

does not match the partition model.

A search engine, analytical system, dedicated query table, or supported secondary indexing feature may be more appropriate.

## Cassandra NoSQL exercise

Start Cassandra and load the bucketed table:

```bash
cd scripts/cassandra
docker compose up -d
docker exec -i cassandra-notes cqlsh < nosql_bucketed_events.cql
```

The demo shows the same customer's September and October events in separate partitions.

## Neo4j: query a relationship pattern

Graph query:

```cypher
MATCH (:Customer {customer_id: 42})
      -[:FOLLOWS]->(:Customer)
      -[:LIKES]->(book:Book)
RETURN DISTINCT book.book_id, book.title
ORDER BY book.book_id;
```

The query expresses a path rather than joins assembled from foreign-key tables.

## Start-node lookup matters

A graph traversal usually begins from a selective node:

```text
Customer.customer_id = 42
```

Use an index/uniqueness constraint for stable identifiers where appropriate.

Then the engine follows relationships.

## Variable-depth path

```cypher
MATCH p =
  (:Customer {customer_id: 42})
  -[:FOLLOWS*1..3]->
  (:Customer)
RETURN p;
```

Always consider fan-out. A small depth in a high-degree graph can visit many candidates.

## Neo4j NoSQL exercise

Run:

```bash
cd scripts
bash setup/start_neo4j.sh
cd ..
python scripts/neo4j/nosql_traversal_demo.py
```

It creates a small recommendation graph and executes the two-hop traversal.

## Same requirement, different query

Requirement:

> Retrieve the state for customer 42.

Possible representations:

### Document

```javascript
db.customers.findOne({ _id: "customer-42" })
```

### Key-value

```text
GET customer:42
```

### Wide-column

```sql
SELECT *
FROM customer_state
WHERE customer_id = 'customer-42';
```

### Graph

```cypher
MATCH (c:Customer {customer_id: 42})
RETURN c;
```

The syntax differs, but the deeper difference is how the store expects data to be addressed and what surrounding operations are cheap.

## Cross-entity query

Requirement:

> List every customer who bought product DB-101 last year and currently follows an author of that product.

This combines:

- historical orders,
- product relationships,
- current social/author graph.

Trying to make one specialized NoSQL model perfect for every part may be worse than using:

- a transactional source,
- an analytical projection,
- a graph projection.

This is where polyglot persistence can emerge from actual requirements.

## Pagination

Every model needs pagination appropriate to its access pattern.

Avoid deep offset pagination when the database has to skip enormous result sets.

Prefer stable cursors/keysets when supported:

```text
last_seen_time
last_seen_id
```

For Cassandra-style partitions, clustering-key continuation is natural.

For graphs, paginate final result sets rather than unbounded path expansion.

## Parameterization and injection

NoSQL query APIs can also be abused if applications build executable query structures directly from untrusted input.

Defenses include:

- use typed driver APIs,
- do not accept arbitrary operators/query documents,
- allowlist dynamic field/sort choices,
- validate IDs and limits,
- use least-privilege database credentials.

"No SQL text" does not mean "no injection risk."

## Query plans and profiling

Use each engine's tools:

- MongoDB `explain()`,
- Redis latency/command metrics,
- Cassandra tracing/metrics cautiously,
- Neo4j `EXPLAIN` / `PROFILE`.

The goal is always the same:

1. determine how much data/work the operation touches,
2. compare that to the intended access pattern,
3. remove unnecessary fan-out/scans.

## Do not compare syntax alone

A short query is not automatically fast.

For example:

```text
GET key
```

is cheap because the key is known.

A MongoDB filter can be cheap with the right index.

A Cassandra query can be cheap because it targets one partition.

A Cypher pattern can be cheap when it begins from one indexed node and traverses bounded relationships.

Performance comes from alignment between model, physical layout, and access pattern.

## Query-design checklist

For each query:

1. What identity/partition/start node is known?
2. How many records/keys/edges can it touch?
3. What ordering is required?
4. What index or data structure supports it?
5. Can the result grow without bound?
6. What projection/fields are actually needed?
7. What consistency/freshness is required?
8. How is pagination handled?
9. Can untrusted input alter query structure?
10. What planner/metrics prove the operation is efficient?

## Related notes

- [NoSQL introduction](01_nosql_databases_intro.md)
- [Types of NoSQL databases](02_types_of_nosql_databases.md)
- [CRUD in SQL vs NoSQL](04_crud_in_sql_vs_nosql.md)
- [Document modeling](05_document_modeling.md)
- [Key-value modeling](06_key_value_modeling.md)
- [Wide-column modeling](07_wide_column_modeling.md)
- [Graph modeling](08_graph_modeling.md)
- [Consistency, transactions, and replication](09_consistency_transactions_and_replication.md)
