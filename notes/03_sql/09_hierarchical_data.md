## Storing Hierarchical Data in Relational Databases with SQL

In many applications, data is naturally organized in a hierarchical structure, such as organizational charts, file systems, categories and subcategories, and family trees. Representing and querying this hierarchical data efficiently in a relational database can be challenging due to the flat nature of relational tables. In this guide, we'll explore several models and techniques for storing and querying hierarchical data in SQL, including:

- **Adjacency List Model**
- **Path Enumeration Model**
- **Other Models** (Materialized Path, Nested Set, Closure Table)
- **Recursive Queries with Common Table Expressions (CTEs)**

After reading the material, you should be able to answer the following questions:

1. What is the Adjacency List Model, and what are its primary advantages and disadvantages when storing hierarchical data in a relational database?
2. How does the Path Enumeration Model enhance the Adjacency List Model, and in what scenarios is it most effectively used?
3. What are the key differences between the Nested Set Model and the Closure Table Model for representing hierarchical data, and what are the respective use cases for each?
4. How do recursive queries with Common Table Expressions (CTEs) facilitate the retrieval of hierarchical data in SQL, and what are the advantages and limitations of using this approach?
5. What best practices should be followed when choosing a model for storing hierarchical data in a relational database, and how do factors like query performance and maintenance complexity influence this decision?

### Adjacency List Model

The **Adjacency List Model** is the most straightforward way to represent hierarchical data in a relational database. In this model, each record (node) contains a reference (foreign key) to its immediate parent.

#### Structure

Consider a table representing categories:

| category_id | parent_id | category_name      |
|-------------|-----------|--------------------|
| 1           | NULL      | Electronics        |
| 2           | 1         | Computers          |
| 3           | 2         | Laptops            |
| 4           | 2         | Desktops           |
| 5           | 1         | Televisions        |
| 6           | 3         | Gaming Laptops     |
| 7           | 3         | Business Laptops   |

- **`category_id`**: Primary key of the category.
- **`parent_id`**: Foreign key referencing `category_id` of the parent category.
- **`category_name`**: Name of the category.

In this model, the root nodes (top-level categories) have a `NULL` `parent_id`.

#### Advantages

- This model is simple to understand because each node directly references its parent using a parent identifier.
- Maintenance tasks such as inserting, updating, and deleting nodes are easier since they primarily involve modifying the parent-child relationship for the affected node.
- Referential integrity is naturally supported using foreign key constraints, ensuring valid relationships between nodes in the hierarchy.

#### Disadvantages

- Queries that require retrieving the entire hierarchy or sub-tree become complex and often involve recursive queries or multiple self-joins.
- Performance issues can arise for deep hierarchies as multiple joins increase query execution time and complexity.
- Hierarchical operations, such as finding all descendants or ancestors of a node, require sophisticated and potentially resource-intensive queries.

#### Implementation Considerations

- Each node in this model contains a reference (usually a foreign key) to its parent node, forming a parent-child relationship.
- Root nodes are identified by having a null value in the parent reference column or a special indicator.
- This model works well in systems where hierarchical queries are infrequent or limited to shallow hierarchies.

#### Use Cases

- Suitable for simple hierarchical relationships like organizational charts or file systems where queries are straightforward and not too deep.
- Preferred when data modifications, such as node addition or removal, occur frequently and need to be efficient.

#### Example: Finding Immediate Children

To find all immediate subcategories of the "Computers" category:

```sql
SELECT *
FROM Categories
WHERE parent_id = (
    SELECT category_id
    FROM Categories
    WHERE category_name = 'Computers'
);
```

#### Example: Retrieving the Full Path

To find the full path of a category (from the root to the node), recursive queries are needed.

### Path Enumeration Model

The **Path Enumeration Model** enhances the adjacency list by storing the full path from the root to each node as a string.

#### Structure

The table includes a `path` column:

| category_id | path        | category_name      |
|-------------|-------------|--------------------|
| 1           | 1           | Electronics        |
| 2           | 1.2         | Computers          |
| 3           | 1.2.3       | Laptops            |
| 4           | 1.2.4       | Desktops           |
| 5           | 1.5         | Televisions        |
| 6           | 1.2.3.6     | Gaming Laptops     |
| 7           | 1.2.3.7     | Business Laptops   |

- **`path`**: Represents the hierarchy as a concatenated string of `category_id`s.

#### Advantages

- Efficient hierarchical queries are possible because all descendants or ancestors of a node can be retrieved using string pattern matching on the path column.
- Joins are not required for hierarchical traversals since the entire hierarchy is encoded within the path stored in each record, simplifying query construction.

#### Disadvantages

- Data redundancy arises due to the duplication of path information in each record, which increases storage requirements.
- Maintenance complexity is high because inserting, updating, or deleting nodes necessitates updating the path values for all affected descendants.
- Extremely deep hierarchies may encounter limitations due to string length constraints, especially in databases with fixed-size fields for storing paths.

#### Implementation Considerations

- Each node includes a `path` attribute representing its position in the hierarchy, typically in a delimited format (e.g., `1/3/5`).
- Root nodes are represented with a single identifier in the `path` column, while child nodes concatenate their identifier to their parent’s path.
- Queries use string pattern matching, such as `LIKE` in SQL, to find nodes based on their path relationships.

#### Use Cases

- This model is ideal for scenarios where fast, read-heavy hierarchical queries are required, and the hierarchy does not change frequently.
- It is commonly used in applications with relatively shallow hierarchies or where the depth is well-defined and manageable.

#### Example: Finding All Descendants

To find all descendants of the "Computers" category:

```sql
SELECT *
FROM Categories
WHERE path LIKE '1.2.%';
```

#### Example: Finding All Ancestors

To find the path (all ancestors) of the "Gaming Laptops" category:

```sql
SELECT *
FROM Categories
WHERE category_id IN (1, 2, 3, 6);
```

But with the path enumeration, you can split the `path` string to get the ancestors.

### Materialized Path Model

Similar to the path enumeration, but uses a delimiter in the `path`:

| category_id | path              | category_name      |
|-------------|-------------------|--------------------|
| 1           | '/1/'             | Electronics        |
| 2           | '/1/2/'           | Computers          |
| 3           | '/1/2/3/'         | Laptops            |
| 6           | '/1/2/3/6/'       | Gaming Laptops     |

#### Advantages

- Hierarchical queries are highly efficient because descendants or ancestors of a node can be easily retrieved using string pattern matching on the materialized path.
- There is no need for joins to navigate the hierarchy since the full path is embedded in each record, simplifying query structure.

#### Disadvantages

- Data redundancy occurs because the path is stored in every record, leading to increased storage requirements, especially in large hierarchies.
- Maintenance operations, such as inserting, updating, or deleting nodes, are complex and require recalculating the `path` for all affected descendants.
- Deep hierarchies may encounter challenges with string length limitations, depending on the database system's maximum string size.

#### Implementation Considerations

- Each node includes a `path` field representing its position in the hierarchy as a delimited string (e.g., `1/2/4`).
- Root nodes are represented by their unique identifier, while child nodes append their identifier to the parent’s path with a delimiter.
- Queries typically use string operations like `LIKE` to retrieve nodes related by hierarchy.

#### Use Cases

- Suitable for scenarios where read-heavy workloads dominate and hierarchical queries, such as retrieving descendants or ancestors, need to be efficient.
- Preferred in systems with relatively stable hierarchies where structural updates are infrequent.

**Example**: Finding all descendants:

```sql
SELECT *
FROM Categories
WHERE path LIKE '/1/2/%';
```

### Nested Set Model

The **Nested Set Model** represents hierarchy through left and right bounds.

#### Structure

Each node is assigned two numbers (`lft` and `rgt`):

| category_id | lft | rgt | category_name      |
|-------------|-----|-----|--------------------|
| 1           | 1   | 14  | Electronics        |
| 2           | 2   | 9   | Computers          |
| 3           | 3   | 6   | Laptops            |
| 6           | 4   | 5   | Gaming Laptops     |
| 4           | 7   | 8   | Desktops           |
| 5           | 10  | 13  | Televisions        |
| 7           | 11  | 12  | Smart TVs          |

#### Advantages

- Efficient hierarchical queries are possible for retrieving all descendants or ancestors of a node because the hierarchy is represented using `left` and `right` values.
- Pre-order traversal eliminates the need for recursive queries or joins, making read operations straightforward and fast.
- Hierarchical operations, such as counting descendants or determining the depth of a subtree, can be performed with simple arithmetic operations.

#### Disadvantages

- Maintenance operations, including inserting, updating, or deleting nodes, are complex and require recalculating the `left` and `right` values for multiple nodes.
- Modifications to the hierarchy can be time-consuming, especially for large trees, as they involve significant updates to the nested set values.
- The model is less intuitive and harder to understand compared to simpler models like adjacency lists or path enumeration.

#### Implementation Considerations

- Each node is assigned a `left` and `right` value representing its position in a pre-ordered traversal of the hierarchy.
- Root nodes have the smallest `left` value and the largest `right` value encompassing all its descendants.
- Queries rely on conditions like `left` and `right` containment to retrieve hierarchical relationships.

#### Use Cases

- Best suited for read-heavy applications where the hierarchy is relatively static and frequent modifications are not required.
- Commonly used in applications that require efficient subtree retrievals, such as content management systems or organizational charts.

**Example: Finding All Descendants**

To find all descendants of the "Electronics" category:

```sql
SELECT *
FROM Categories
WHERE lft > 1 AND rgt < 14;
```

### Closure Table Model

The **Closure Table Model** uses a separate table to store all ancestor-descendant relationships.

#### Structure

**Categories Table**:

| category_id | category_name      |
|-------------|--------------------|
| 1           | Electronics        |
| 2           | Computers          |
| 3           | Laptops            |
| 6           | Gaming Laptops     |

**Closure Table**:

| ancestor_id | descendant_id | depth |
|-------------|---------------|-------|
| 1           | 1             | 0     |
| 1           | 2             | 1     |
| 1           | 3             | 2     |
| 1           | 6             | 3     |
| 2           | 2             | 0     |
| 2           | 3             | 1     |
| 2           | 6             | 2     |
| 3           | 3             | 0     |
| 3           | 6             | 1     |
| 6           | 6             | 0     |

#### Advantages

- Hierarchical queries, such as retrieving all descendants, ancestors, or paths between nodes, are highly efficient because the relationships are precomputed and stored.
- Supports complex hierarchical operations, such as finding the depth, level, or specific paths, with simple and fast queries.
- Flexibility allows for easy traversal of both upward (ancestors) and downward (descendants) relationships in the hierarchy.

#### Disadvantages

- Increased storage requirements arise because the closure table stores every possible pair of ancestor and descendant for the hierarchy.
- Maintenance operations, such as inserting, updating, or deleting nodes, require updating multiple rows in the closure table, which can be time-consuming for large hierarchies.
- The model is less intuitive than simpler models like adjacency lists, making it harder to understand and implement without prior knowledge.

#### Implementation Considerations

- The closure table is a separate table that stores pairs of nodes along with their relationships, typically including a `parent_id`, `child_id`, and optionally, a `depth` column.
- Root nodes are represented with a self-referential relationship in the closure table, where `parent_id` equals `child_id`.
- Queries leverage joins on the closure table to retrieve hierarchical relationships efficiently.

#### Use Cases

- Suitable for applications requiring frequent and complex hierarchical queries, such as social networks, organizational charts, and tree-like structures.
- Ideal for scenarios where the hierarchy changes infrequently, or batch updates can be used to recalculate relationships.

**Example: Finding All Descendants**

To find all descendants of the "Computers" category:

```sql
SELECT c.*
FROM Categories c
JOIN CategoryClosure cc ON c.category_id = cc.descendant_id
WHERE cc.ancestor_id = (
    SELECT category_id FROM Categories WHERE category_name = 'Computers'
) AND cc.depth > 0;
```

### Storing Hierarchical Data in SQL with Recursive Queries

Most modern relational databases support recursive queries using Common Table Expressions (CTEs). This allows you to traverse hierarchical data stored in the adjacency list model efficiently.

#### Recursive CTE Structure

A recursive CTE consists of:

**Anchor Member**

- The anchor member is the initial query in the recursive CTE that defines the starting point of the recursion, typically the root nodes or base cases of the hierarchy.
- It is executed once and serves as the foundation upon which the recursive part builds additional rows.
- For example, in an organizational hierarchy, the anchor member might select all top-level managers with no superiors.

**Recursive Member**

- The recursive member is a query within the CTE that references the CTE itself, enabling it to iterate through the hierarchy by progressively adding rows.
- This query is executed repeatedly, appending its results to the results of the anchor member until no new rows are generated.
- It typically joins the hierarchical data source to itself, using a parent-child relationship to navigate the structure.

**Termination Condition**

- The termination condition is implicitly defined by the recursive member and occurs when the query returns no new rows to add to the result set.
- This ensures that the recursion stops automatically, preventing infinite loops and completing the query execution.
- Proper design of the recursive logic is critical to avoid unintentional infinite recursion, especially for improperly structured hierarchies.

#### Syntax

```sql
WITH RECURSIVE cte_name AS (
    -- Anchor member
    SELECT ...

    UNION ALL

    -- Recursive member
    SELECT ...
    FROM cte_name
    JOIN ...
)
SELECT * FROM cte_name;
```

#### Example: Retrieving the Full Hierarchy

Given our `Categories` table in the adjacency list model:

| category_id | parent_id | category_name      |
|-------------|-----------|--------------------|
| 1           | NULL      | Electronics        |
| 2           | 1         | Computers          |
| 3           | 2         | Laptops            |
| 4           | 2         | Desktops           |
| 5           | 1         | Televisions        |
| 6           | 3         | Gaming Laptops     |
| 7           | 3         | Business Laptops   |

We can use a recursive CTE to retrieve the full hierarchy:

```sql
WITH RECURSIVE category_hierarchy AS (
    -- Anchor member: select root nodes
    SELECT
        category_id,
        parent_id,
        category_name,
        CAST(category_name AS VARCHAR(255)) AS full_path,
        0 AS depth
    FROM Categories
    WHERE parent_id IS NULL

    UNION ALL

    -- Recursive member: join with child nodes
    SELECT
        c.category_id,
        c.parent_id,
        c.category_name,
        CONCAT(ch.full_path, ' > ', c.category_name) AS full_path,
        ch.depth + 1 AS depth
    FROM Categories c
    INNER JOIN category_hierarchy ch ON ch.category_id = c.parent_id
)
SELECT *
FROM category_hierarchy
ORDER BY full_path;
```

**Explanation**:

- **`CAST`**: Ensures that `full_path` starts as a string.
- **`CONCAT`**: Builds the full path by appending the current category name.
- **`depth`**: Tracks the level in the hierarchy.

**Result**:

| category_id | parent_id | category_name    | full_path                                 | depth |
|-------------|-----------|------------------|-------------------------------------------|-------|
| 1           | NULL      | Electronics      | Electronics                               | 0     |
| 2           | 1         | Computers        | Electronics > Computers                   | 1     |
| 3           | 2         | Laptops          | Electronics > Computers > Laptops         | 2     |
| 6           | 3         | Gaming Laptops   | Electronics > Computers > Laptops > Gaming Laptops | 3 |
| 7           | 3         | Business Laptops | Electronics > Computers > Laptops > Business Laptops | 3 |
| 4           | 2         | Desktops         | Electronics > Computers > Desktops        | 2     |
| 5           | 1         | Televisions      | Electronics > Televisions                 | 1     |

#### Finding a Subtree

To retrieve a specific category and all its descendants, modify the anchor member:

```sql
WITH RECURSIVE subcategories AS (
    -- Anchor member: select the starting category
    SELECT
        category_id,
        parent_id,
        category_name
    FROM Categories
    WHERE category_name = 'Computers'

    UNION ALL

    -- Recursive member: find children
    SELECT
        c.category_id,
        c.parent_id,
        c.category_name
    FROM Categories c
    INNER JOIN subcategories s ON s.category_id = c.parent_id
)
SELECT *
FROM subcategories;
```

**Result**:

| category_id | parent_id | category_name    |
|-------------|-----------|------------------|
| 2           | 1         | Computers        |
| 3           | 2         | Laptops          |
| 4           | 2         | Desktops         |
| 6           | 3         | Gaming Laptops   |
| 7           | 3         | Business Laptops |

#### Advantages

- Dynamic queries can process hierarchical data of arbitrary depth, making them highly versatile for a wide range of hierarchy sizes and structures.
- This approach does not require any changes to the schema, as it works seamlessly with the adjacency list model without needing extra columns or additional tables.
- The flexibility of recursive CTEs allows retrieving various hierarchical relationships, including ancestors, descendants, or specific paths, through adaptable query structures.

#### Limitations

- Performance can degrade significantly for very large or deep hierarchies, as recursive operations can be computationally intensive and memory-consuming.
- Database support is a limiting factor, as only certain databases (e.g., PostgreSQL, SQL Server, Oracle, MySQL 8.0+) offer built-in support for recursive CTEs, restricting its use in other database systems.

#### Implementation Considerations

- Recursive CTEs start with a base case query to define the root nodes and then recursively union subsequent queries to fetch child or parent nodes.
- They are defined using SQL syntax like `WITH RECURSIVE` and include termination conditions to prevent infinite loops.

#### Use Cases

- Ideal for querying hierarchical relationships in systems that use the adjacency list model and require minimal schema modifications.
- Suitable for dynamic hierarchies where the depth is unknown or variable.

