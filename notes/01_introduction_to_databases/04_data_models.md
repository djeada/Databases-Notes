## Data Models

A data model provides a framework that determines how data is stored, organized, and manipulated within a database.

## Types of Data Models

### Hierarchical Model

- **Overview:** Data is structured in a tree-like format, featuring parent-child relationships and a single root node.
- **Characteristics:** While parent nodes can have multiple child nodes, each child node can have only one parent.
- **Strengths:** Direct and efficient for querying hierarchical data.
- **Weaknesses:** Limited flexibility and challenges in representing complex relationships.

```
Root
│
├── Child_1
│   ├── Grandchild_1_1
│   └── Grandchild_1_2
└── Child_2
    └── Grandchild_2_1
```

### Network Model

- **Overview:** Data is organized in a flexible, network-like structure, allowing for multiple relationships between records.
- **Characteristics:** Both parent and child nodes can have multiple counterparts.
- **Strengths:** Greater flexibility compared to the hierarchical model.
- **Weaknesses:** Navigation and query construction can be complex.
  
```
        ┌───────┐
        │Parent │
        └──┬─┬──┘
      ┌────┘ └────┐
 ┌────┴────┐ ┌────┴────┐
 │Child_1  │ │Child_2  │
 └────┬────┘ └────┬────┘
      │  ┌────────┴───┐
      └──│ Grandchild │
         └────────────┘
```

### Relational Model

- **Overview:** Data is represented as tables (also known as relations) consisting of rows (tuples) and columns (attributes).
- **Characteristics:** Tables are linked via keys (primary and foreign), ensuring referential integrity.
- **Strengths:** User-friendly, flexible, and offers robust consistency.
- **Weaknesses:** May struggle with horizontal scaling and handling unstructured data.

```
Table_1                         Table_2
+------+-------+               +------+--------+
| Key  | Attr  |               | Key  | Attr   |
+------+-------+               +------+--------+
| K1   | A1    |-------+------>| K2   | A2     |
| K2   | A3    |<------+-------| K3   | A4     |
+------+-------+               +------+--------+
```

### Entity-Relationship Model (ER Model)

- **Overview:** This high-level data model illustrates the relationships between entities and their attributes.
- **Characteristics:** Consists of entities, attributes, and relationships.
- **Strengths:** Simple to understand and provides a solid foundation for designing relational databases.
- **Weaknesses:** Not a database implementation model but a design tool.

```
[ Entity1 ]<---( Relationship )--->[ Entity2 ]
   |           /    |    \            |
Attribute1   Attribute2  Attribute3  Attribute4
```

### Object-Oriented Model

- **Overview:** Combines database and object-oriented programming concepts, enabling data storage as objects.
- **Characteristics:** Supports object persistence, inheritance, encapsulation, and polymorphism.
- **Strengths:** Handles complex data structures and relationships effectively.
- **Weaknesses:** Less mature and not as widely adopted as the relational model.

```
Class
│
├── Object1
│   ├── Attribute1
│   └── Method1
└── Object2
    ├── Attribute2
    └── Method2
```

### Document Model

- **Overview:** Data is stored and managed as documents, typically using formats like JSON or BSON.
- **Characteristics:** Offers flexible schema, embedded documents, and compatibility with complex data types.
- **Strengths:** High performance, ease of use, and scalability.
- **Weaknesses:** Limited support for complex transactions and joins.

```
Document
│
├── Key1: Value1
└── Key2: { Nested_Key: Value2 }
```

### Column-Family Model

- **Overview:** Data is organized in columns rather than rows, optimized for reading and writing large data sets.
- **Characteristics:** Uses column families, wide rows, and distributed storage.
- **Strengths:** Excellent write performance, horizontal scalability, and efficient data compression.
- **Weaknesses:** Limited support for joins and complex queries.

```
RowKey: Object1
│
├── ColumnFamily1
│   ├── Column1: Value1
│   └── Column2: Value2
│
└── ColumnFamily2
    ├── Column3: Value3
    └── Column4: Value4
```

### Graph Model

- **Overview:** Data is represented as nodes, edges, and properties in a graph structure.
- **Characteristics:** Comprises nodes (entities), edges (relationships), and properties (attributes).
- **Strengths:** Superior performance for graph traversal and relationship-oriented querying, flexible data modeling.
- **Weaknesses:** Limited support for operations outside of graph traversal and complex aggregations.
  
```
     Node1
    /     \
Node6-----Node2
|   \     /   |
|    Node7    |
|   /     \   |
Node5-----Node3
    \     /
     Node4
```
