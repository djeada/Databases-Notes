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

**WITH Clause**: The `WITH` clause in SQL is used to create a temporary result set that is known as a Common Table Expression (CTE). 

- A CTE is used within the scope of a single statement and is not stored as a persistent object.
- CTEs can be recursive or non-recursive. The recursive ones are used to query hierarchical data.
  
**Recursive CTE Structure**: Recursive CTEs have two components connected by a `UNION` or `UNION ALL` operator:

- **Anchor Member**: This is the base case for the recursion and usually fetches the top-level elements in the hierarchy (rows with `parent_id` as NULL in this context).
- **Recursive Member**: This part refers back to the CTE, allowing the query to iterate over the hierarchy.

**Recursive CTE in Action**:

The initial table ("Categories") looks like this:

| category_id | parent_id | category_name |
|-------------|-----------|---------------|
| 1           | NULL      | Electronics   |
| 2           | 1         | Computers     |
| 3           | 2         | Laptops       |
| 4           | 2         | Desktops      |
| 5           | 1         | TVs           |
| 6           | 3         | Gaming Laptops|
| 7           | 3         | Business Laptops|

Here's an example of a recursive CTE to fetch a full category hierarchy:

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

- In this SQL statement, the CTE "category_hierarchy" starts with an anchor member that selects all top-level categories (where `parent_id IS NULL`). The `UNION ALL` keyword then combines these results with the results of the recursive member, which refers back to the CTE itself.
- This recursive member of the CTE continues executing until it returns no new rows, meaning it has traversed all levels of the hierarchy.

The expected result of the above query would look like this:

| category_id | parent_id | category_name |
|-------------|-----------|---------------|
| 1           | NULL      | Electronics   |
| 2           | 1         | Computers     |
| 5           | 1         | TVs           |
| 3           | 2         | Laptops       |
| 4           | 2         | Desktops      |
| 6           | 3         | Gaming Laptops|
| 7           | 3         | Business Laptops|

This lists all the categories in the order of the hierarchy, starting with the root (Electronics), followed by its children (Computers and TVs), and then the children of Computers (Laptops and Desktops), and finally the children of Laptops (Gaming Laptops and Business Laptops).
