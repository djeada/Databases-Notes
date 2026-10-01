# Graph Modeling: Nodes, Relationships, Paths, and Traversal

Graph databases model connected data explicitly:

```text
node -[relationship]-> node
```

They are useful when the **relationship itself is part of the query**, especially when queries traverse several hops. Typical workloads include social connections, fraud networks, recommendation graphs, dependencies, routing, organizational relationships, and knowledge graphs.

## Start from the traversal

Suppose a bookstore asks:

> Recommend books liked by people followed by Alice.

```text
(Alice)-[:FOLLOWS]->(Bob)-[:LIKES]->(Book A)
   |
   `--------------->(Carol)-[:LIKES]->(Book B)
```

The requested operation is a path traversal. That is the reason to examine a graph model.

## Nodes

Nodes represent entities such as:

```text
Customer
Book
Author
Publisher
Account
Device
IP
```

A node normally has labels/types, properties, and a stable identity.

Conceptually:

```text
(:Customer {
  customer_id: 42,
  name: "Alice"
})
```

## Relationships

Relationships connect nodes:

```text
(:Customer)-[:FOLLOWS]->(:Customer)
```

Relationships can carry properties:

```text
(:Customer)-[:PURCHASED {
  quantity: 2,
  purchased_at: ...
}]->(:Book)
```

Use relationship properties only for facts that truly belong to the connection.

## When an intermediate node is better

Suppose an order has its own identifier, payment/shipping state, several line items, refunds, and lifecycle transitions.

A direct edge loses too much structure:

```text
(Customer)-[:PURCHASED]->(Book)
```

A better model is:

```text
(Customer)-[:PLACED]->(Order)
(Order)-[:CONTAINS {quantity: 2}]->(Book)
```

The order is a first-class entity. Graph modeling does not mean turning every relational join table into an edge.

## Labels, relationship types, and direction

Prefer meaningful types:

```text
(:Customer)
(:Book)
(:Author)

-[:FOLLOWS]->
-[:LIKES]->
-[:WROTE]->
```

Avoid generic `RELATED_TO` relationships when the business meaning matters.

Relationships are directed:

```text
(Alice)-[:FOLLOWS]->(Bob)
```

is different from:

```text
(Bob)-[:FOLLOWS]->(Alice)
```

For symmetric concepts such as friendship, choose a consistent representation: one relationship queried as undirected, two directed relationships, or a first-class relationship entity.

## Property or node?

A genre can be a property:

```text
(:Book {genre: "Database"})
```

if it is only a label value.

It can be a node:

```text
(:Book)-[:IN_GENRE]->(:Genre)
```

if genre has identity, metadata, hierarchy, or traversal behavior.

Choose from the queries, not from a universal modeling rule.

## Graph versus relational joins

A relational model can represent the same facts with tables such as:

```text
customers
follows
books
likes
```

SQL can traverse them with joins.

A graph database becomes attractive when path length varies, many relationship types matter, traversal depth is central, and pattern matching dominates the workload.

Do not choose a graph merely because the domain has relationships. Every relational system models relationships too.

## Cypher pattern matching

Neo4j uses Cypher.

```cypher
MATCH (alice:Customer {customer_id: 42})
      -[:FOLLOWS]->(:Customer)
      -[:LIKES]->(book:Book)
RETURN DISTINCT book.title;
```

The query visually resembles the graph pattern.

## Runnable Neo4j demo

The repository already contains:

- [`scripts/neo4j/merge_full_pattern_duplicates_nodes.py`](../../scripts/neo4j/merge_full_pattern_duplicates_nodes.py)
- [`scripts/neo4j/detach_delete_vs_delete.py`](../../scripts/neo4j/detach_delete_vs_delete.py)

This NoSQL chapter adds:

[`scripts/neo4j/nosql_traversal_demo.py`](../../scripts/neo4j/nosql_traversal_demo.py)

Start Neo4j and run it:

```bash
cd scripts
bash setup/start_neo4j.sh
cd ..
python scripts/neo4j/nosql_traversal_demo.py
```

The demo creates customers/books, adds `FOLLOWS` and `LIKES` relationships, and executes a two-hop recommendation query.

## Identity and uniqueness

Graph databases still need identity rules.

Examples:

```text
Customer.customer_id unique
Book.book_id unique
```

Without constraints, repeated imports can create duplicate logical nodes. Define uniqueness constraints where the engine supports them.

## MERGE semantics

In Neo4j, `MERGE` finds or creates a pattern. A full-pattern merge can have surprising behavior when only part of the pattern exists. It is often safer to establish unique node identities separately and then merge the relationship.

The existing repository demo shows why this matters.

## Path length and branching factor

Fixed traversal:

```text
Alice -> friend -> book
```

Variable traversal:

```text
Alice -> friend -> friend -> friend -> ...
```

Variable-depth traversal is powerful and can be expensive.

Prefer an explicit maximum depth:

```cypher
MATCH p =
  (:Customer {customer_id: 42})
  -[:FOLLOWS*1..3]->
  (:Customer)
RETURN p;
```

If each node has 100 outgoing edges:

```text
depth 1 -> 100 candidates
depth 2 -> 10,000
depth 3 -> 1,000,000
```

Graph overlap may reduce this, but path depth and node degree are core performance dimensions.

## Supernodes

A supernode has extremely high degree.

Example:

```text
(:Country {name: "US"})
```

connected to hundreds of millions of users.

Traversing through it may be expensive. Alternatives can include property filtering, hierarchy, relationship partitioning, or avoiding traversal through global hubs.

## Recommendation graph

```text
Customer
   | LIKES
   v
Book
   ^
   | LIKES
Other Customer
```

A collaborative query can ask:

> Find books liked by customers who like some of the same books as Alice.

Production recommendation systems may still combine graph features with ranking models, embeddings, popularity, and business rules.

## Fraud graph

Possible nodes:

```text
Account
Card
Device
IP
Email
Phone
```

Relationships:

```text
USED_DEVICE
USED_CARD
LOGGED_IN_FROM
HAS_EMAIL
HAS_PHONE
```

A fraud query might ask:

> Find accounts connected within two hops through the same device or payment card.

Graph traversal can reveal shared infrastructure that is awkward to discover through repeated joins.

## Dependency graph

Nodes:

```text
Service
Database
Queue
Library
```

Relationships:

```text
CALLS
DEPENDS_ON
READS_FROM
WRITES_TO
```

Questions include:

- what breaks if database X is unavailable?
- which services depend indirectly on library Y?

Graphs fit impact analysis well.

## Hierarchies and cycles

Graphs can support ancestors, descendants, and multiple parents. They can also contain cycles:

```text
A -> B -> C -> A
```

Some domains allow cycles. Others do not.

An organizational hierarchy may require acyclicity. The database may not automatically enforce every global graph invariant, so application/procedure logic can still be necessary.

## Relationship uniqueness

If Alice can follow Bob only once, prevent duplicate logical relationships through supported constraints/patterns and transaction logic.

Duplicate edges can distort counts, recommendations, and traversals.

## Traversal versus aggregation

Graph databases excel at connectivity.

They may not be the best system for:

```text
SUM(revenue) by country for 10 years
```

Use analytical databases or warehouses for broad scans and aggregations. A production system can use both.

## Graph as a derived projection

A common architecture:

```text
transactional database
        |
        v
     CDC/batch
        |
        v
graph projection
        |
        v
fraud/recommendation queries
```

The graph becomes a traversal-optimized projection while the transactional database remains the source of truth.

If updates are asynchronous, define tolerated lag, idempotent updates, ordering expectations, and a rebuild procedure.

## Indexes and starting nodes

Graph queries often begin from a known node:

```text
Customer.customer_id = 42
```

An index/constraint helps find the start node. Traversal then follows relationships.

A poor starting lookup can make every graph query slower.

## EXPLAIN and PROFILE

Neo4j provides planner/profiling tools:

```cypher
EXPLAIN ...
```

and:

```cypher
PROFILE ...
```

Inspect starting-node lookup, expansions, rows produced, and expensive Cartesian products.

## Avoid Cartesian products

A pattern such as:

```cypher
MATCH (a:Customer), (b:Book)
RETURN a, b;
```

without relationship/filter constraints can create a large Cartesian product.

Graph query languages can express very expensive patterns; model and profile them deliberately.

## OPTIONAL MATCH

`OPTIONAL MATCH` is useful when a relationship may be absent:

```cypher
MATCH (c:Customer)
OPTIONAL MATCH (c)-[:LIKES]->(b:Book)
RETURN c.name, b.title;
```

Customers without matching books remain in the result.

## Aggregation

Graph queries can aggregate:

```cypher
MATCH (:Customer)-[:LIKES]->(b:Book)
RETURN b.title, count(*) AS likes
ORDER BY likes DESC;
```

Use graphs where traversal is the primary value, not just because aggregation exists.

## Shortest paths and graph algorithms

Graph systems can support shortest paths, PageRank, community detection, centrality, and similarity.

These may have very different resource profiles from online point traversals. Do not run large graph algorithms on a production transactional graph without capacity planning.

## Import workflow

A safe bulk-load sequence:

1. load nodes with stable IDs,
2. create/verify uniqueness constraints,
3. load relationships referencing stable IDs,
4. validate node and relationship counts,
5. inspect high-degree nodes.

Identity mistakes during import are difficult to repair later.

## Delete semantics

Deleting a node with relationships may require explicit handling.

Neo4j distinguishes:

```cypher
DELETE n
```

from:

```cypher
DETACH DELETE n
```

The repository's delete demo shows the difference.

## Multi-tenancy and privacy

A shared graph needs tenant boundaries.

One model:

```text
(:Customer {
  tenant_id: "acme",
  customer_id: 42
})
```

Every query must maintain tenant scope.

Relationships can themselves be sensitive:

```text
person -> clinic
person -> support_group
```

Protect topology as well as node properties.

## Modeling workflow

1. State the traversal question in plain language.
2. Identify node types.
3. Identify relationship types and direction.
4. Decide which facts belong on relationships.
5. Introduce intermediate nodes when entities have their own lifecycle.
6. Define stable identifiers and uniqueness.
7. Estimate degrees and path depth.
8. Identify potential supernodes.
9. Define tenant/security boundaries.
10. Profile representative queries.
11. Decide source-of-truth versus derived graph.
12. Define synchronization and rebuild behavior.

## Common mistakes

### "Our data has relationships, so use a graph"

Every data model has relationships.

### Generic `RELATED_TO` relationships

Business meaning disappears.

### Unbounded traversal

Query expansion can explode.

### Duplicate nodes after import

Identity was not constrained.

### Order represented only as a `PURCHASED` edge

Independent order state/lifecycle is lost.

### Graph used for global warehouse analytics

Wrong workload.

### Derived graph has no rebuild process

Synchronization failures become permanent.

## Related notes

- [Types of NoSQL databases](02_types_of_nosql_databases.md)
- [Querying NoSQL databases](03_querying_nosql_databases.md)
- [Document modeling](05_document_modeling.md)
- [Consistency, transactions, and replication](09_consistency_transactions_and_replication.md)
- [Neo4j engine note](../12_database_engines/05_neo4j.md)
