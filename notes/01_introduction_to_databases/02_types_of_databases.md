# Database Types: Choose a Model for the Questions You Ask

A data model is a way to represent information and its relationships. The bookstore can represent customers and orders as tables, store a customer profile as a document, or look up a session by a key. Each arrangement makes some operations natural and others more work.

First ask what the application needs to read and change. A product being called “NoSQL” or “distributed” does not establish its performance, transaction guarantees, or suitability.

## Relational: connect facts stored in tables

A relational database represents data as tables. A row holds one record, columns hold its attributes, and keys identify rows and connect tables.

For the bookstore, `customers` holds customer information and `orders` holds purchases. Both contain a customer ID where appropriate. A query can join them to answer “which customers placed orders this week?”

This separation helps when one fact must change everywhere. Correct Alice's name in the customer row and queries of her previous orders can show the corrected name without rewriting every order.

Relational systems are useful when several entities are related, different reports ask different questions, and rules must be enforced across the data. SQL is their usual query language. Examples include SQLite, PostgreSQL, MySQL, and SQL Server.

A declared schema does not mean the design can never change. Changes need a deliberate migration: a controlled alteration of the existing structure and, sometimes, existing rows.

## Document: store a record with nested detail

A document groups related fields, often in a JSON-like structure:

```json
{
  "customer_id": 1,
  "name": "Alice",
  "preferences": {
    "language": "en",
    "favorite_categories": ["History", "Science"]
  }
}
```

Here `preferences` belongs inside the customer profile. Reading the document can retrieve that nested detail together. MongoDB is a familiar document database.

Before embedding orders inside a customer document, consider whether the list grows indefinitely and whether orders need independent updates and queries. Embedding can simplify a read while making growth and shared facts harder to manage. Documents can also reference other documents rather than embedding everything.

Flexible fields do not remove the need for a schema in the broader sense: the application still needs to know what `customer_id` means and how to handle missing or mistyped fields.

## Key-value: find a value by an exact key

A key-value store associates a key with a value:

```text
key:   session:abc123
value: {customer_id: 1, expires_at: "2025-01-12T18:00:00Z"}
```

If the application already knows `session:abc123`, it can ask for that session directly. This suits session lookup and caching, where a predictable key answers the usual question. Redis and DynamoDB support key-based access, with additional capabilities beyond a minimal key-value model.

Finding “all sessions belonging to customers who bought history books” is a different problem. A simple key lookup does not answer it. The application needs an additional access structure, a different representation, or a database that supports the required query.

## Wide-column: organize keyed groups of related values

A wide-column store organizes data around row or partition keys and related columns. Cassandra, HBase, and Bigtable belong to this family, although their schemas and query capabilities differ.

For a sensor service, a key might identify a device and a day, with readings organized within that group. The key design decides which reads can target one group and how writes are distributed. It is usually chosen from known access patterns rather than from arbitrary future reports.

**Wide-column** does not mean the same thing as **columnar analytical storage**. The latter places values from the same column together to make large scans and compression efficient. See [row and column storage](../05_storage_and_indexing/02_row_based_vs_column_based_databases.md).

## Graph: follow relationships as part of the query

A graph represents entities as **nodes** and relationships as **edges**:

```text
Alice --follows--> Bob --likes--> Book 17
```

The bookstore might ask “which books are liked by people Alice follows?” A graph query follows the relationships and returns the connected books. Neo4j is one graph database.

Relational databases can also answer relationship questions using joins. A graph model is worth considering when repeated traversal of relationship paths is central to the workload, rather than merely because the data has relationships.

## Other labels describe other dimensions

These descriptions can apply alongside a data model:

| Label | What it tells you | What it does not establish |
| --- | --- | --- |
| In-memory | Working data primarily resides in RAM, the computer's main memory. | Whether durable copies exist or data survives a restart. |
| Distributed | Data or processing spans several machines. | Which failures it tolerates or what reads can observe. |
| Time-series | Data and operations emphasize time-stamped measurements or events. | One universal physical layout or query language. |
| Analytical warehouse | The workload emphasizes historical scans and reporting. | Suitability for the checkout transaction path. |

A database can be relational and distributed, or key-value and in-memory. These are not mutually exclusive boxes.

## Compare the bookstore's needs

| Main question | A model to investigate | Why |
| --- | --- | --- |
| Which customer placed each order? | Relational | Tables and joins connect the facts. |
| What are this customer's nested preferences? | Document | The detail can be read as one record. |
| Which user owns this session token? | Key-value | The token directly identifies the value. |
| Which readings belong to device 5 on a given day? | Wide-column | A planned key can group the relevant readings. |
| Which books do friends of friends recommend? | Graph | The query repeatedly follows relationships. |

These are starting points, not guarantees. Check the chosen product's transactions, constraints, supported queries, and measured costs.

## Check your understanding

1. Why might a document suit preferences but an unbounded embedded order list cause problems?
2. What information must you already have for a direct key-value lookup?
3. Can a relational database be distributed?
4. Why are wide-column stores different from columnar warehouses?

Continue with [what a DBMS does](03_database_management_systems_dbms_.md), which follows a request through the software rather than repeating the product categories.
