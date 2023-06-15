## Storing Hierarchical Data in Relational Databases with SQL

Hierarchical data is a common form of data representation where data entities are related to each other in a parent-child fashion. To store this type of data in relational databases, we often use the Adjacency List Model and the Path Enumeration Model.

### Adjacency List Model

The adjacency list model is a simple and intuitive approach, where each record has a foreign key that refers to its parent.

Example Table:

| category_id | parent_id | category_name |
|-------------|-----------|---------------|
| 1           | NULL      | Electronics   |
| 2           | 1         | Computers     |
| 3           | 2         | Laptops       |
| 4           | 2         | Desktops      |
| 5           | 1         | TVs           |

Here, the `parent_id` of a category refers to the `category_id` of its parent category. 

However, this model can be inefficient when retrieving an entire tree or subtree, as each level of the tree requires an additional self-join.

### Path Enumeration Model

The path enumeration model addresses some of the issues with the adjacency list model. In this model, the path from the root to a node is stored for each node, providing an efficient way to find the entire subtree or the path to a node.

Example Table:

| category_id | path        | category_name |
|-------------|-------------|---------------|
| 1           | 1           | Electronics   |
| 2           | 1.2         | Computers     |
| 3           | 1.2.3       | Laptops       |
| 4           | 1.2.4       | Desktops      |
| 5           | 1.5         | TVs           |

Here, the `path` column stores the path from the root to the current node. This makes it easy to find all children of a node (all categories that have a path starting with a given path), or to find the path from the root to a node. However, this model can be more complex to maintain, as changes in the tree structure require updating multiple path values.

### Other Models

Other models for storing hierarchical data in SQL include:

- **Materialized Path Model**: Similar to path enumeration, but paths are stored as strings with delimiters. For instance, using a path like '1/2/3', where '/' is the delimiter.

- **Nested Set Model**: Each node is assigned a range of numbers, with child nodes falling within their parent's range. This makes it easy to find all descendants of a node and all ancestors of a node but can be complicated when inserting or deleting nodes.

- **Closure Table Model**: A separate table is used to store relationships between nodes, allowing for efficient querying but requiring more storage space. The closure table consists of pairs of nodes; each pair identifies a descendant and its ancestor.


## Storing Hierarchical Data in SQL with Recursive Queries

In SQL, you often encounter situations where data is stored in a hierarchical manner, a common form of which is a parent-child relationship. This kind of data is typically represented in an "Adjacency List Model" in relational databases. In this model, each record has a foreign key that refers to its parent record.

Example Table ("Categories"):

| category_id | parent_id | category_name |
|-------------|-----------|---------------|
| 1           | NULL      | Electronics   |
| 2           | 1         | Computers     |
| 3           | 2         | Laptops       |
| 4           | 2         | Desktops      |
| 5           | 1         | TVs           |
| 6           | 3         | Gaming Laptops|
| 7           | 3         | Business Laptops|

Here, each category has a `parent_id` that refers to the `category_id` of its parent category. 

### Recursive Queries and WITH Clause

SQL offers recursive queries as a way to work with hierarchical data. These queries are especially useful with the adjacency list model. 

A recursive query is basically a query that refers to itself. Recursive queries are often paired with the `WITH` clause in SQL. This clause allows you to define a temporary result set (known as a Common Table Expression or CTE) that you can later refer to within your query.

### Understanding Recursive CTEs

The structure of a recursive CTE is generally a `UNION` (or `UNION ALL`) of two subqueries: the anchor member (which returns the initial result set that forms the base result) and the recursive member (which returns the rest of the results by referring back to the CTE).

Note that UNION returns only distinct rows, while UNION ALL returns all rows, including duplicates. In recursive CTEs, UNION ALL is often preferred to maintain the full structure of the hierarchy.

Here's how you could write a recursive CTE to retrieve all categories and their hierarchy:

```sql
WITH RECURSIVE category_hierarchy AS (
    -- Anchor Member
    SELECT category_id, parent_id, category_name
    FROM Categories
    WHERE parent_id IS NULL

    UNION ALL

    -- Recursive Member
    SELECT c.category_id, c.parent_id, c.category_name
    FROM Categories c
    INNER JOIN category_hierarchy ch ON ch.category_id = c.parent_id
)
SELECT * FROM category_hierarchy;
```

In the above SQL statement, we first define our CTE (category_hierarchy) with the WITH clause. The CTE starts with an anchor member that selects all root-level categories (where parent_id IS NULL). We then use the UNION ALL keyword to combine these results with the results of the recursive member, which refers back to category_hierarchy itself.

The recursive member of the CTE continues executing until it returns no new rows, meaning it has traversed through all levels of the hierarchy. In each iteration of the recursive member, the join condition ch.category_id = c.parent_id climbs one level up the hierarchy.

| category_id | parent_id | category_name |
|-------------|-----------|---------------|
| 1           | NULL      | Electronics   |
| 2           | 1         | Computers     |
| 5           | 1         | TVs           |
| 3           | 2         | Laptops       |
| 4           | 2         | Desktops      |
| 6           | 3         | Gaming Laptops|
| 7           | 3         | Business Laptops|

This result gives us all categories in the order of the hierarchy, starting from the root level ("Electronics") down to the leaf nodes ("Gaming Laptops" and "Business Laptops").
