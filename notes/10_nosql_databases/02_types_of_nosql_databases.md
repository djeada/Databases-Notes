## Types of NoSQL Databases

NoSQL databases are categorized based on their data models, each addressing different requirements and use cases by providing unique advantages in handling specific kinds of data and workloads.

The main types of NoSQL databases are:

- **Key-Value Stores**
- **Document Stores**
- **Column-Family Stores**
- **Graph Databases**

### 1. Key-Value Stores

#### Description

- Key-value stores manage data as a collection of key-value pairs, where the key is a unique identifier and the value is the data associated with that key.
- This model is similar to a **dictionary** or hash table.
- They are characterized by simple and fast data **access**.
- Key-value stores are highly **scalable** and distributed.
- They are optimized for **read** and write operations.

#### Use Cases

- Key-value stores are useful for **caching** frequently accessed data to improve application performance.
- They are used in **session** management to maintain user session information in web applications.
- These databases store application **configuration** settings for configuration management.
- They handle high-speed data ingestion and retrieval, making them suitable for **real-time** analytics.

#### Examples

- **Redis** is an in-memory data structure store used as a database, cache, and message broker.
- **Riak** is a distributed NoSQL key-value data store that offers high availability.
- **Amazon DynamoDB** is a fully managed NoSQL database service supporting key-value and document data structures.

#### Sample Data

- **Key**: `user123`, **Value**: `"John Smith"`
- **Key**: `user456`, **Value**: `"Jane Doe"`
- **Key**: `session789`, **Value**: `{"id": 789, "user": "John Smith", "timestamp": "2024-09-14T12:34:56Z"}`

**Example Usage in Redis:**

```bash
# Set key-value pairs
SET user123 "John Smith"
SET user456 "Jane Doe"

# Retrieve values
GET user123  # Returns "John Smith"
```

### 2. Document Stores

#### Description

- Document stores manage data in **documents**, typically using formats like JSON or BSON.
- Each document contains semi-structured data that can vary in structure, allowing for **flexibility**.
- Documents are grouped into **collections** within the database.
- They support complex data structures and **nested** data.
- Document stores offer rich **query** capabilities and indexing for faster query performance.

#### Use Cases

- Document stores are used in content management systems to manage and store website **content**.
- They handle user **profiles** and personalization, accommodating data that can differ significantly.
- These databases are suitable for e-commerce applications to store product **catalogs** with varying attributes.
- They are used in analytics platforms to store and analyze semi-structured **data**.

#### Examples

- **MongoDB** is a popular open-source document database known for its flexibility and scalability.
- **CouchDB** uses JSON to store data and JavaScript for queries.
- **RavenDB** is a transactional, open-source document database designed for the .NET platform.

#### Sample Data

**Example Document in MongoDB:**

```json
{
  "_id": "user123",
  "name": "John Smith",
  "email": "john@example.com",
  "orders": [
    {"id": 1, "product": "Laptop", "price": 1200},
    {"id": 2, "product": "Mouse", "price": 30}
  ]
}
```

- The `orders` field contains an array of **order** documents.
- A dynamic **schema** allows additional fields to be added without affecting other documents.

**Query Examples:**

```javascript
// Find user by ID
db.users.find({ "_id": "user123" })

// Retrieve users with orders over $1000
db.users.find({ "orders.price": { $gt: 1000 } })
```

### 3. Column-Family Stores

#### Description

- Column-family stores organize data into rows and dynamic **columns** grouped into column families.
- Each row can have a large number of columns, and columns can be added on the fly.
- They are optimized for high **write** throughput and designed for horizontal scalability.
- These databases are suitable for handling **sparse** data and large-scale, distributed data.

#### Use Cases

- Column-family stores are used for **time-series** data, recording events over time like logs or sensor data.
- They handle big data **analytics** by managing massive datasets for analytical processing.
- These databases are suitable for **IoT** data management, storing and querying data from interconnected devices.
- They are used in recommendation systems to manage large amounts of user interaction **data**.

#### Examples

- **Apache Cassandra** handles large amounts of data across commodity servers.
- **Apache HBase** is modeled after Google's Bigtable for non-relational, distributed data.
- **ScyllaDB** is a drop-in replacement for Cassandra designed for low latency and high throughput.

#### Sample Data

| Row Key   | Column Family: **UserInfo**             | Column Family: **UserOrders**          |
|-----------|-----------------------------------------|----------------------------------------|
| `user123` | `name: John`, `email: john@example.com` | `order1: Laptop`, `order2: Mouse`      |
| `user456` | `name: Jane`, `email: jane@example.com` | `order1: Keyboard`, `order2: Monitor`  |

Data is organized with a row key and column families like **UserInfo** and **UserOrders**, containing relevant columns.

**CQL (Cassandra Query Language) Example:**

```sql
-- Create Keyspace
CREATE KEYSPACE ecommerce WITH replication = {'class': 'SimpleStrategy', 'replication_factor' : 3};

-- Create Table
CREATE TABLE ecommerce.users (
    user_id text PRIMARY KEY,
    name text,
    email text,
    orders map<text, text>
);

-- Insert Data
INSERT INTO ecommerce.users (user_id, name, email, orders)
VALUES ('user123', 'John', 'john@example.com', {'order1': 'Laptop', 'order2': 'Mouse'});
```

### 4. Graph Databases

#### Description

- Graph databases use **nodes**, **edges**, and properties to represent and store data.
- They excel at handling data with complex **relationships** and are optimized for traversing connections.
- Nodes represent entities, and edges represent relationships between these entities.
- Graph databases offer flexible **schemas** for evolving data models.

#### Use Cases

- They are used in social networks to model and query relationships between **users**.
- Graph databases power recommendation engines by suggesting products based on user **behavior**.
- They assist in fraud detection by identifying suspicious patterns and **connections**.
- These databases are used in knowledge graphs to represent complex interlinked **information**.

#### Examples

- **Neo4j** is a leading open-source graph database implemented in Java.
- **OrientDB** supports graph, document, key-value, and object models.
- **Amazon Neptune** is a fully managed graph database service.

#### Sample Data

**Nodes:**

- **User**: `{ "id": 1, "name": "John Smith" }`
- **User**: `{ "id": 2, "name": "Jane Doe" }`
- **Product**: `{ "id": 101, "name": "Laptop" }`

**Edges:**

- `(User:1)-[:FRIEND]->(User:2)` indicates John is friends with Jane.
- `(User:1)-[:PURCHASED]->(Product:101)` indicates John purchased a laptop.

**Cypher Query Examples (Neo4j):**

```cypher
// Find friends of John
MATCH (john:User {name: 'John Smith'})-[:FRIEND]->(friend)
RETURN friend.name;

// Recommend products purchased by friends
MATCH (john:User {name: 'John Smith'})-[:FRIEND]->(friend)-[:PURCHASED]->(product)
RETURN product.name;
```

### Characteristics of NoSQL Databases

- NoSQL databases offer schema **flexibility**, allowing for dynamic and evolving data structures.
- They are designed for horizontal **scalability**, scaling out across multiple servers or nodes.
- High **availability** is achieved through built-in replication and fault tolerance mechanisms.
- Their distributed **architecture** partitions and distributes data to optimize performance.
- They often provide eventual **consistency**, prioritizing availability and partition tolerance.
