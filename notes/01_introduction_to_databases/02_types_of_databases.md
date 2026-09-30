# Database Types: Compare the Operations, Not Just the Names

The first note used tables to connect customers and orders. Other databases represent data as documents, keyed values, or graph relationships. Each representation changes what is easy to read, what must be maintained during a write, and which operations need additional structures.

This note compares database families through named technologies and concrete operations. Each executable example has its own setup. The SQL examples use SQLite unless another engine is named; MongoDB, Redis, Cassandra, and Neo4j examples require their respective services and clients. You can understand the comparisons without installing every product.

## 1. Relational databases: combine independently stored facts

**SQLite, PostgreSQL, MySQL, SQL Server, and Oracle Database** are relational DBMSs. They expose tables, keys, constraints, and SQL. Their deployment and storage details differ, but they can express relationships and calculations without forcing the application to fetch every record and combine it itself.

A bookstore account page needs customer names and orders. A finance report needs amounts by date. Relational tables let those requests combine the same base facts in different ways.

### Create and query a relational example

Run this independent SQLite setup in a fresh database:

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    total_cents INTEGER NOT NULL CHECK (total_cents >= 0)
);

INSERT INTO customers VALUES (1, 'Alice'), (2, 'Bob');
INSERT INTO orders VALUES (101, 1, 5500), (102, 1, 1500), (103, 2, 5000);

SELECT c.name, SUM(o.total_cents) AS spent_cents
FROM customers AS c
JOIN orders AS o ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name
ORDER BY c.customer_id;
```

| name | spent_cents |
|---|---|
| Alice | 7000 |
| Bob | 5000 |

`GROUP BY` forms one group per customer; `SUM` adds the amounts in each group. The stored amounts use integer cents, so 7000 means 70.00 in the chosen currency. This miniature example stores an order total directly; a line-item design can calculate it from quantities and purchase prices instead.

### Why this mechanism fits, and where it costs

Keys and constraints make cross-table references explicit. Transactions can group related writes. Joins and aggregation allow new questions to be asked without creating a separately maintained dataset for every report.

That flexibility does not make every query efficient. Large joins can read and sort substantial data; useful indexes, accurate statistics, and suitable SQL matter. A schema change also needs a migration. Relational does not mean “small,” “one machine,” or “incapable of nested data.” PostgreSQL, for example, supports `jsonb` alongside relational columns; see its [JSON type documentation](https://www.postgresql.org/docs/current/datatype-json.html).

Use the relational model when operational facts have important relationships and integrity rules, or when several queries need to combine them in different ways. Choose an engine by its actual concurrency, operations, extension, and deployment requirements.

## 2. Document databases: retrieve a record with nested detail

**MongoDB** stores BSON documents, a binary format supporting JSON-like structures and additional types. **CouchDB** is another document-oriented system, with a different API and replication design. **Couchbase** and **Amazon DocumentDB** are additional implementations with their own APIs and feature compatibility. A document can contain fields, nested objects, and arrays.

For a catalog, a printed book has page count and language, while an audiobook has duration and narrator. Grouping those attributes inside each product can make the product page straightforward to load.

### Create and query documents in MongoDB

Run this in `mongosh` connected to a MongoDB server. Use the `chapter1_catalog` practice database with an initially empty `products` collection:

```javascript
use chapter1_catalog

db.products.insertMany([
  {
    _id: 10,
    title: "Database Basics",
    format: "print",
    price_cents: 1500,
    attributes: { pages: 240, language: "en" },
    categories: ["Computing", "Databases"]
  },
  {
    _id: 20,
    title: "SQL on the Move",
    format: "audio",
    price_cents: 2500,
    attributes: { duration_minutes: 180, narrator: "Sam" },
    categories: ["Computing", "Databases"]
  }
]);

db.products.find(
  { "attributes.language": "en" },
  { _id: 1, title: 1 }
).sort({ _id: 1 });
```

The query returns the print book:

```json
{ "_id": 10, "title": "Database Basics" }
```

`use` is a `mongosh` command selecting the database, rather than ordinary JavaScript. The insertion creates the collection if necessary. `_id` identifies each document. Dot notation accesses the nested language field, and the second argument selects returned fields.

Add an index for a recurring language lookup:

```javascript
db.products.createIndex({ "attributes.language": 1 });
```

The `1` specifies ascending index order. This makes a language-field access path available; whether the planner chooses it depends on the data and query. MongoDB's [insertion documentation](https://www.mongodb.com/docs/manual/reference/method/db.collection.insertone/) describes collection creation and identifiers, and its [embedded-field indexing guide](https://www.mongodb.com/docs/manual/core/indexes/index-types/index-single/create-embedded-object-index/) distinguishes whole-object indexes from indexes on specific nested fields.

### Embedding is a modeling decision

An order document can embed its bounded list of purchased lines because they are often read together. Embedding a customer's entire lifelong order history is different: that array can grow without bound, and independent order queries become awkward.

**Embedding** places related values inside a document; **referencing** stores another record's identifier. Repeating a current price in many documents creates an update obligation. A price charged in a historical order is intentionally a separate fact and should not follow later catalog edits.

A flexible document structure still needs a schema contract. The application must understand missing fields and expected types, and the DBMS may enforce document validation. MongoDB also supports multi-document transactions in suitable deployments. “Document” does not automatically mean “no rules” or “no transactions.”

## 3. Key-value databases: address a value directly

**Redis** provides commands over named keys and supports values such as strings, hashes, lists, and sets. A minimal key-value interaction starts with a key the application already knows. **DynamoDB** also offers key-based access, using table keys, attributes, and optional secondary indexes rather than Redis's command model. **Riak KV** is another key-value implementation with a different architecture and API.

A login session is a good example: the browser supplies a token, and the application needs to find that token's associated user and expiry.

### Create an expiring session in Redis

Run these commands in `redis-cli` connected to a Redis server. `chapter1:session:abc123` is a practice key:

```text
SET chapter1:session:abc123 '{"customer_id":1}' EX 900
GET chapter1:session:abc123
TTL chapter1:session:abc123
```

The first command returns `OK`. An immediate `GET` returns the stored JSON string, and `TTL` returns its remaining lifetime in seconds. `EX 900` sets a 15-minute expiration. After expiration, `GET` returns a nil reply rather than the old session.

Redis treats this value as a string; it does not automatically interpret the JSON's fields. The application parses it. The official [SET documentation](https://redis.io/docs/latest/commands/set/) describes the value and expiration options.

For a cart, a hash exposes separate fields:

```text
HSET chapter1:cart:abc123 product:10 2 product:20 1
HGETALL chapter1:cart:abc123
```

The hash contains quantities `2` for product 10 and `1` for product 20; the [HSET documentation](https://redis.io/docs/latest/commands/hset/) describes field updates. The result's display order is not the cart's business ordering. A stored cart is an intention to buy, not a stock reservation.

### Direct access is useful but does not answer every query

Loading this one cart needs its key. Finding every cart containing product 10 is a different access pattern and requires another supported structure, search feature, or maintained representation. Do not assume a direct lookup API can efficiently answer arbitrary cross-record questions.

Redis commonly keeps working data in memory. Persistence options such as snapshots and an append-only file address recovery separately; expiration and eviction address entry lifetime and memory pressure. An entry can be unavailable for more than one reason. See [Redis persistence](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/) for the recovery mechanisms.

## 4. Wide-column databases: design partitions around known queries

**Apache Cassandra, HBase, and Google Cloud Bigtable** belong to the wide-column family, though their APIs and storage models differ. In Cassandra, a table has a declared schema, a partition key that places related records together, and clustering columns that order records inside a partition.

Suppose the bookstore records customer activity. Its usual request is “show customer 1's events this month, newest first.” Partitioning by customer and month groups that request's data while bounding the growth of each time bucket.

### Create and query a Cassandra example

Run this CQL in `cqlsh` against a one-node **local practice cluster**. CQL resembles SQL but has different query restrictions:

```cql
CREATE KEYSPACE chapter1
WITH replication = {
    'class': 'SimpleStrategy',
    'replication_factor': 1
};

CREATE TABLE chapter1.events_by_customer_month (
    customer_id int,
    month text,
    occurred_at timestamp,
    event_id int,
    action text,
    PRIMARY KEY ((customer_id, month), occurred_at, event_id)
) WITH CLUSTERING ORDER BY (occurred_at DESC, event_id ASC);

INSERT INTO chapter1.events_by_customer_month
    (customer_id, month, occurred_at, event_id, action)
VALUES (1, '2025-01', '2025-01-10T10:00:00Z', 1, 'viewed product 10');

INSERT INTO chapter1.events_by_customer_month
    (customer_id, month, occurred_at, event_id, action)
VALUES (1, '2025-01', '2025-01-12T11:00:00Z', 2, 'placed order 102');

SELECT occurred_at, action
FROM chapter1.events_by_customer_month
WHERE customer_id = 1 AND month = '2025-01';
```

The result contains the January 12 event before the January 10 event. The nested parentheses in the primary key make `(customer_id, month)` the partition key. The remaining columns identify and order records within it, with `event_id` distinguishing events at the same timestamp.

A **keyspace** is Cassandra's namespace and replication configuration. The single-copy `SimpleStrategy` setting keeps the local exercise small; it provides no replica redundancy. Production deployments generally use `NetworkTopologyStrategy` with appropriate datacenter settings. See Cassandra's [data-definition documentation](https://cassandra.apache.org/doc/latest/cassandra/developing/cql/ddl.html).

### Why the query shapes the table

Cassandra uses the partition key to target data placement and retrieval. Filtering only by `action`, without this partition key, is not the same efficient lookup. Another recurring query may need another table, a suitable supported index, or an analytical pipeline. Keeping multiple query-oriented representations introduces maintenance work.

This is why Cassandra's [logical-modeling guide](https://cassandra.apache.org/doc/latest/cassandra/developing/data-modeling/data-modeling_logical.html) starts from queries. Large or popular partitions can still create hotspots; choosing a key does not guarantee an evenly distributed workload.

A wide-column database is not a columnar analytical database. The latter groups values by column for scans and compression, as the next section explains.

## 5. Columnar analytical databases: scan the fields a report needs

**ClickHouse** and **DuckDB** are examples of systems with columnar storage suited to analytical work. Instead of keeping only the logical row shape in mind, consider a report that sums one numeric column across millions of sales. A columnar layout can read the relevant column without reading every unrelated field of each record.

The following standalone SQL works in DuckDB:

```sql
CREATE TABLE sales (
    sale_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    amount_cents BIGINT
);

INSERT INTO sales VALUES
    (101, 10, 2, 3000),
    (102, 20, 1, 2500),
    (103, 20, 2, 5000);

SELECT product_id, SUM(amount_cents) AS revenue_cents
FROM sales
GROUP BY product_id
ORDER BY product_id;
```

| product_id | revenue_cents |
|---|---|
| 10 | 3000 |
| 20 | 7500 |

The analytical benefit comes from the storage and execution design, not from the SQL spelling: a row-oriented engine can run this query too. Similar column values can compress well, and engines can process batches efficiently. A tiny three-row example shows the result but cannot prove a performance advantage.

A transactional store with frequent small updates and an analytical store scanning broad history have different workloads. DuckDB is commonly embedded for analytics; ClickHouse offers a different operational architecture. DuckDB's [architecture overview](https://www.duckdb.org/why_duckdb) and [FAQ](https://duckdb.org/faq) explain its in-process operation and columnar representation; ClickHouse describes its own [columnar design](https://clickhouse.com/resources/engineering/what-is-columnar-database). The [row-versus-column note](../05_storage_and_indexing/02_row_based_vs_column_based_databases.md) explains the layout tradeoff.

## 6. Graph databases: make traversal a first-class operation

**Neo4j** represents data as nodes, directed relationships, and properties. **Amazon Neptune** and **OrientDB** offer other graph capabilities; their interfaces and model combinations differ, so this example uses Neo4j explicitly. It uses **Cypher**, a language in which a pattern describes the relationships to match.

The bookstore wants “books liked by people Alice follows.” That is a two-step path: Alice follows someone, and that person likes a book.

### Create and query a Neo4j graph

Run this in an empty Neo4j practice database:

```cypher
CREATE (alice:Customer {customer_id: 1, name: 'Alice'}),
       (bob:Customer {customer_id: 2, name: 'Bob'}),
       (book:Book {product_id: 10, title: 'Database Basics'}),
       (alice)-[:FOLLOWS]->(bob),
       (bob)-[:LIKES]->(book);
```

Now find the path:

```cypher
MATCH (:Customer {customer_id: 1})-[:FOLLOWS]->(friend)-[:LIKES]->(book:Book)
RETURN DISTINCT book.title AS recommended_title
ORDER BY recommended_title;
```

| recommended_title |
|---|
| Database Basics |

Parentheses describe nodes, `:Customer` and `:Book` are labels, and square brackets describe relationships. `friend` and `book` bind matched nodes so later clauses can use them. `DISTINCT` avoids returning the same title several times when several friends like it; a production query should normally identify recommendations by product identifier rather than title alone.

`CREATE` always creates the requested pattern, so rerunning the setup creates additional nodes unless the design prevents that. `MATCH` searches the graph without creating it. The official [CREATE](https://neo4j.com/docs/cypher-manual/current/clauses/create/) and [MATCH](https://neo4j.com/docs/cypher-manual/current/clauses/match/) guides describe these operations.

### Why traversal can fit, and what to check

A graph model makes variable paths, neighborhoods, and relationship-specific properties natural to express. It can suit recommendations, dependency analysis, or fraud-relationship investigation. It is not automatically better whenever two entities are related: a relational join may already answer a fixed one-hop request well.

High-degree nodes and broad path expansion can still produce expensive work. Identity constraints, starting-node indexes, path limits, and transaction behavior remain important. A graph model does not eliminate schema or integrity decisions.

## 7. Historical and object-oriented families

The main operational examples above are not an exhaustive taxonomy. **IBM IMS** uses a hierarchical segment model, and **IDMS** is associated with the network model. **ObjectDB** persists Java objects through object-oriented APIs. These families matter when maintaining an existing system or evaluating a workload organized around their structures.

The [data-models note](04_data_models.md) explains hierarchical, network, entity-relationship, and object-oriented structures with examples and distinguishes them from modern documents and graphs. Do not interpret “NoSQL” as a synonym for every non-relational historical system.

## 8. Keep model, deployment, and workload separate

A product can fit several descriptions at once:

| Dimension | Question | Examples |
|---|---|---|
| Data model | How are facts represented and addressed? | Tables, documents, keys, graphs |
| Storage layout | Which bytes are stored together? | Row-oriented or column-oriented |
| Deployment | Where does the engine run? | Embedded library, server, managed service |
| Distribution | How many nodes hold or process data? | Single node, replicas, shards |
| Workload | What operations dominate? | Checkout transactions, reports, time-stamped events |
| Persistence | What survives restart and which failures? | Memory-only operation, configured logs or snapshots, durable storage |

“In-memory,” “distributed,” and “time-series” are not mutually exclusive alternatives to “relational.” PostgreSQL can use JSON fields, a graph can run on a server, and an analytical engine can be embedded. **NoSQL** groups several model families; it does not establish one universal transaction, scaling, or consistency guarantee.

## 9. Choose using one complete workflow

For checkout, identify the reads, stock reservation, order writes, immediate confirmation, and failure cases together. Ask what must be atomic and what a retry can duplicate. For reporting, identify scan volume, required freshness, joins, and the cost of loading analytical data.

Compare candidates against those requirements:

- Can the actual queries target the stored structure efficiently?
- Which keys, validation rules, and uniqueness constraints are enforced?
- What transaction scope is available, and what can concurrent writers do?
- What does an acknowledged write mean after failover?
- How much maintenance is needed when facts are repeated?
- Can the team secure, back up, restore, monitor, and migrate the system?

A small bookstore may use one relational database for nearly everything. Add another system when its concrete benefits justify the extra data movement and operational work.

## Practice and check your understanding

1. Explain why the relational result has one row per customer despite Alice having two orders.
2. Change the MongoDB filter to select audio products. Which document should match?
3. Why is an expired Redis session different from a durable customer record?
4. Which fields identify the Cassandra partition, and which fields order its events?
5. Why is “find events with this action across all customers” a new access-pattern problem?
6. What path does the Neo4j query match, and why might it need duplicate handling?
7. Why can a relational engine and a columnar engine both execute an aggregate query?

Continue with [DBMS responsibilities](03_database_management_systems_dbms_.md) to follow how requests are executed, secured, and recovered.
