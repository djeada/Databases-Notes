# Storing Hierarchical Data in Relational Databases with SQL

In many applications, data is naturally organized in a hierarchical structure, such as organizational charts, file systems, categories and subcategories, and family trees. Representing and querying this hierarchical data efficiently in a relational database can be challenging due to the flat nature of relational tables. In this guide, we'll explore several models and techniques for storing and querying hierarchical data in SQL, including:

- **Adjacency List Model**
- **Path Enumeration Model**
- **Other Models** (Materialized Path, Nested Set, Closure Table)
- **Recursive Queries with Common Table Expressions (CTEs)**

## Adjacency List Model

The **Adjacency List Model** is the most straightforward way to represent hierarchical data in a relational database. In this model, each record (node) contains a reference (foreign key) to its immediate parent.

### Structure

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

### Advantages

- **Simplicity**: Easy to implement and understand.
- **Maintenance**: Inserting, updating, and deleting nodes is straightforward.
- **Referential Integrity**: Enforced through foreign key constraints.

### Disadvantages

- **Complex Queries**: Retrieving an entire hierarchy or sub-tree requires recursive queries or multiple self-joins.
- **Performance**: Can be inefficient for deep hierarchies due to multiple joins.
- **Limited Hierarchical Operations**: Difficult to perform operations like finding all descendants or ancestors without complex queries.

### Example: Finding Immediate Children

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

### Example: Retrieving the Full Path

To find the full path of a category (from the root to the node), recursive queries are needed.

## Path Enumeration Model

The **Path Enumeration Model** enhances the adjacency list by storing the full path from the root to each node as a string.

### Structure

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

### Advantages

- **Efficient Hierarchical Queries**: Easy to retrieve all descendants or ancestors using string pattern matching.
- **No Joins Needed**: Simplifies queries since hierarchical relationships are stored within each record.

### Disadvantages

- **Data Redundancy**: The path information is duplicated in each record.
- **Maintenance Complexity**: Inserting, updating, or deleting nodes requires updating the `path` values of all affected descendants.
- **Limited Depth**: String length may become an issue in very deep hierarchies.

### Example: Finding All Descendants

To find all descendants of the "Computers" category:

```sql
SELECT *
FROM Categories
WHERE path LIKE '1.2.%';
```

### Example: Finding All Ancestors

To find the path (all ancestors) of the "Gaming Laptops" category:

```sql
SELECT *
FROM Categories
WHERE category_id IN (1, 2, 3, 6);
```

But with the path enumeration, you can split the `path` string to get the ancestors.

## Other Models

### Materialized Path Model

Similar to the path enumeration, but uses a delimiter in the `path`:

| category_id | path              | category_name      |
|-------------|-------------------|--------------------|
| 1           | '/1/'             | Electronics        |
| 2           | '/1/2/'           | Computers          |
| 3           | '/1/2/3/'         | Laptops            |
| 6           | '/1/2/3/6/'       | Gaming Laptops     |

**Advantages**:

- Easier string parsing using standard string functions.
- Supports variable-length IDs.

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

**Advantages**:

- Efficiently retrieves all descendants or ancestors using range queries.
- No recursion or joins needed for hierarchy traversal.

**Disadvantages**:

- Complex maintenance: Inserting or deleting nodes requires recalculating `lft` and `rgt` values for many nodes.
- Difficult to understand and implement.

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

**Advantages**:

- Efficient queries for ancestors and descendants.
- Supports complex hierarchical queries.

**Disadvantages**:

- Additional storage required for the closure table.
- Maintenance overhead when modifying the hierarchy.

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

## Storing Hierarchical Data in SQL with Recursive Queries

Most modern relational databases support recursive queries using Common Table Expressions (CTEs). This allows you to traverse hierarchical data stored in the adjacency list model efficiently.

### Recursive CTE Structure

A recursive CTE consists of:

- **Anchor Member**: The base query that provides the starting point of recursion.
- **Recursive Member**: A query that references the CTE itself, allowing the recursion to proceed.
- **Termination Condition**: The recursion stops when no new rows are returned.

### Syntax

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

### Example: Retrieving the Full Hierarchy

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

### Finding a Subtree

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

### Advantages of Recursive CTEs

- **Dynamic Queries**: Can handle hierarchies of arbitrary depth.
- **No Additional Schema**: Works with the adjacency list model without additional columns or tables.
- **Flexibility**: Can be used to retrieve ancestors, descendants, or paths.

### Limitations

- **Performance**: May not be efficient for very large hierarchies.
- **Database Support**: Requires a database that supports recursive CTEs (e.g., PostgreSQL, SQL Server, Oracle, MySQL 8.0+).
