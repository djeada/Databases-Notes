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

The **Adjacency List Model** is a straightforward way to represent hierarchies in SQL by having each record point to its immediate parent in the same table. This self-referencing design makes it very intuitive to understand and maintain simple tree structures, though querying deep hierarchies can require recursive logic or iterative joins.

#### Table Schema

Before working with the model, you need to define a table that stores both the node and a reference to its parent. The example below creates a `categories` table where each category can optionally link to another category as its parent.

```sql
CREATE TABLE categories (
    category_id   INT PRIMARY KEY,
    parent_id     INT NULL REFERENCES categories(category_id)
                  ON UPDATE CASCADE
                  ON DELETE SET NULL,
    category_name TEXT NOT NULL
);

-- Helpful index for fast child look-ups
CREATE INDEX idx_categories_parent ON categories(parent_id);
```

Example data:

| category\_id | parent\_id | category\_name   |
| ------------ | ---------- | ---------------- |
| 1            | NULL       | Electronics      |
| 2            | 1          | Computers        |
| 3            | 2          | Laptops          |
| 4            | 2          | Desktops         |
| 5            | 1          | Televisions      |
| 6            | 3          | Gaming Laptops   |
| 7            | 3          | Business Laptops |

> *Root* nodes are characterised by a `NULL` `parent_id`. If sibling order matters, add a column such as `sort_order`.

#### Why Choose It?

Choosing the Adjacency List Model is often driven by its simplicity and portability. It works in any SQL database without special extensions and makes simple inserts, updates, and deletes very cheap — only a single row needs to be changed. However, reading an entire branch can become inefficient unless your database supports recursive queries or you build additional logic.

| ✔️ Strengths                                             | ❗ Trade‑offs                                                                                                    |
| -------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| Intuitive—mirrors real‑world parent–child relationships. | Reading an entire branch is costly; requires recursion or iterative joins.                                      |
| ACID‑safe, portable to **any** SQL database.             | Path constraints (preventing cycles) need application logic or triggers.                                        |
| Cheap `INSERT`/`UPDATE`/`DELETE`—only one row changes.   | Join depth grows with tree depth; performance degrades on deep hierarchies unless recursive CTEs are available. |

#### Common Queries

This section outlines typical operations you’ll perform when navigating the hierarchy, from finding direct children to retrieving full descendant trees or building breadcrumb trails.

**Immediate children**

```sql
SELECT *
FROM   categories
WHERE  parent_id = :parent;
```

**All descendants** (PostgreSQL / MySQL 8.0+ / SQL Server)

```sql
WITH RECURSIVE subtree AS (
    SELECT category_id, parent_id, category_name, 1 AS depth
    FROM   categories
    WHERE  category_id = :root

    UNION ALL

    SELECT c.category_id, c.parent_id, c.category_name, st.depth + 1
    FROM   categories AS c
    JOIN   subtree     AS st ON c.parent_id = st.category_id
)
SELECT *
FROM   subtree
ORDER  BY depth, category_name;
```

**Path from root to a node**

```sql
WITH RECURSIVE path AS (
    SELECT category_id, parent_id, category_name
    FROM   categories
    WHERE  category_id = :leaf
    UNION ALL
    SELECT c.category_id, c.parent_id, c.category_name
    FROM   categories AS c
    JOIN   path        AS p ON p.parent_id = c.category_id
)
SELECT string_agg(category_name, ' → ' ORDER BY category_id DESC) AS breadcrumb
FROM   path;
```

#### Implementation Tips

When implementing the adjacency list, consider additional constraints and indexing to maintain data integrity and performance. You can enforce sibling uniqueness, control cascading behaviors on deletes, and guard against cyclical references.

* Add `UNIQUE (parent_id, category_name)` if sibling names must be unique.
* Use `ON DELETE CASCADE` if removing a parent should delete its sub‑tree, or `ON DELETE RESTRICT` to forbid orphaning.
* Guard against cycles with a trigger (`parent_id` cannot reference the row itself or any of its descendants).

#### Suitable Scenarios

The adjacency list shines in applications where you typically read or modify small parts of the tree rather than large sub‑trees. It pairs well with vendor extensions for trees but still remains portable across systems.

* Menus, site navigation trees, forum threads—structures that are usually read in small slices.
* Workloads with heavy write activity, where the cost of complex read queries is acceptable.
* Systems where vendor‑specific tree extensions (e.g., Oracle `CONNECT BY`) are available.

#### Alternatives for Deep Reads

If you need faster full-tree reads at the cost of more complex writes or extra storage, consider one of these other models:

* **Materialised Path** – store the path string (`"1/2/3"`) in each row for quick prefix searches.
* **Nested Sets** – maintain left/right bounds; reads are *O(1)* but writes are slow.
* **Closure Table** – keep a second table containing every ancestor → descendant pair; both reads and writes are performant but extra storage is required.

### Path Enumeration (Materialised Path) Model – Practical Notes

The **Path Enumeration Model**, often called the *materialised path* technique, represents hierarchies by storing each node’s complete ancestry as a single delimited string. This means any descendant or ancestor lookup requires no joins or recursion, trading read simplicity for more complex writes.

#### Table Schema

To implement this model, your table must include a `path` column that uniquely holds the concatenated IDs from the root to each node, using a consistent delimiter. An index on this column enables fast prefix scans for hierarchical queries.

```sql
CREATE TABLE categories_path (
    category_id   INT PRIMARY KEY,
    path          TEXT NOT NULL UNIQUE,  -- e.g. '1.2.3.' (note the trailing delimiter)
    category_name TEXT NOT NULL
);

-- Index for blazing‑fast prefix queries (PostgreSQL)
CREATE INDEX idx_categories_path_prefix
        ON categories_path USING btree (path text_pattern_ops);
```

*Trailing delimiter (`.` here) ensures prefix matches never confuse `1.12.` with `1.1.`.*

Example rows:

| category\_id | path     | category\_name   |
| ------------ | -------- | ---------------- |
| 1            | 1.       | Electronics      |
| 2            | 1.2.     | Computers        |
| 3            | 1.2.3.   | Laptops          |
| 4            | 1.2.4.   | Desktops         |
| 5            | 1.5.     | Televisions      |
| 6            | 1.2.3.6. | Gaming Laptops   |
| 7            | 1.2.3.7. | Business Laptops |

#### Strengths / Trade‑offs

This model shines when you need lightning-fast reads at the expense of more expensive writes. By duplicating path information, prefix queries for whole sub‑trees become trivial, but moving nodes requires updating every affected row.

| ✔️ Benefits                                                                            | ⚠️ Costs                                                                |
| -------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| **Instant reads** – descendants/ancestors fetched with a single `LIKE` or prefix scan. | **Write ripple** – any move/insert/delete may touch an entire sub‑tree. |
| Works in *any* SQL engine; no recursive CTE required.                                  | Storage overhead from repeating path segments in every row.             |
| Natural ordering for breadcrumbs and hierarchical sort.                                | Deep trees risk hitting string‑length or index‑key limits.              |

#### Everyday Queries

With materialised paths, common tree operations reduce to simple text operations. Here are examples for finding descendants, children, or building breadcrumbs.

**All descendants of “Computers”**

```sql
SELECT *
FROM   categories_path
WHERE  path LIKE '1.2.%';
```

**Immediate children**

```sql
SELECT *
FROM   categories_path
WHERE  path LIKE '1.2.%'
  AND  path NOT LIKE '1.2.%._%'; -- optional depth filter if delimiter is '.'
```

**Breadcrumb / ancestors of node \:leaf** (PostgreSQL)

```sql
SELECT *
FROM   categories_path
WHERE  ':leaf_path' LIKE path || '%'
ORDER  BY length(path);
```

#### Maintenance Recipes

Writes in this model require cascaded updates to keep paths consistent. Wrap each multi-step change in a transaction to avoid partial updates.

| Operation                                                                  | Example (SQL pseudo‑code)                                           |        |   |                 |
| -------------------------------------------------------------------------- | ------------------------------------------------------------------- | ------ | - | --------------- |
| **Insert** child under `parent_id = p`                                     | \`INSERT INTO categories\_path (category\_id, path, category\_name) |        |   |                 |
| VALUES (\:id, (SELECT path FROM categories\_path WHERE category\_id = \:p) |                                                                     | :id    |   | '.', \:name);\` |
| **Move** a sub‑tree                                                        | 1️⃣ Fetch `old_prefix`, `new_prefix`.                               |        |   |                 |
| 2️⃣ \`UPDATE categories\_path                                              |                                                                     |        |   |                 |
| SET path = REPLACE(path, old\_prefix, new\_prefix)                         |                                                                     |        |   |                 |
| WHERE path LIKE old\_prefix                                                |                                                                     | '%';\` |   |                 |
| **Delete** a node + sub‑tree                                               | `DELETE FROM categories_path WHERE path LIKE '1.2.3.%';`            |        |   |                 |

> *Tip:* Wrap these statements in a transaction to keep the tree consistent.

#### Implementation Tips

To keep your materialised paths robust:

* Choose a delimiter unlikely to appear in IDs (e.g., `.` or `/`).
* Enforce trailing delimiter via `CHECK (path LIKE '%.')` to simplify queries.
* Add a **prefix index** (or functional index on `substring(path, 1, N)` in MySQL) for speed.
* Guard against cycles by ensuring `path` never contains `'.' || category_id || '.'` beyond the tail.
* For deep trees, store `path` in `VARCHAR(2048)` or `TEXT`; most RDBMS support long keys with in‑page overflow.

#### When to Use It

This pattern excels when read performance is paramount and writes are rare or batched.

* Read‑heavy workloads: CMS menus, product catalogs, comment threads, category breadcrumbs.
* Databases lacking or throttling recursive CTEs.
* Systems where tree edits are infrequent or batched (daily ETL refresh).

#### Limitations & Mitigations

Although materialised paths speed up reads, they can introduce maintenance challenges. Use these strategies to mitigate common issues:

| Issue                                              | Mitigation                                                                                          |
| -------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| Large string updates during *move* operations      | Buffer changes in staging table, then swap; or migrate to Closure Table model for heavy mutability. |
| Index key length limits (e.g., MySQL < 3072 bytes) | Hash long prefixes into an additional column and index that.                                        |
| Human error constructing paths                     | Provide stored procedures or application service layer to encapsulate path math.                    |

#### Alternatives for Mutable Trees

When write complexity becomes a bottleneck, consider these alternatives:

* **Nested Sets (MPTT)** – fastest bulk reads; costly writes due to range shifts.
* **Closure Table** – separate table of ancestor → descendant pairs gives fast reads *and* manageable writes at the price of extra storage.

### Nested Set (Modified Preorder Tree Traversal) Model

The **Nested Set Model**, also known as *Modified Preorder Tree Traversal (MPTT)*, encodes hierarchical structures by assigning two numerical bounds (`lft` and `rgt`) to each node. These bounds encompass all descendants, allowing entire subtrees to be retrieved with a simple range query.

#### Table Schema

Before using MPTT, your table must include left and right bound columns, and optionally a `depth` to save computing levels. Unique indexes on the bounds prevent overlapping subtrees.

```sql
CREATE TABLE categories_nested (
    category_id   INT PRIMARY KEY,
    lft           INT NOT NULL,
    rgt           INT NOT NULL,
    depth         INT NOT NULL,           -- optional, but saves a COUNT(*)
    category_name TEXT NOT NULL,
    CONSTRAINT chk_bounds CHECK (lft < rgt)
);

--  Ensure no overlapping ranges
CREATE UNIQUE INDEX idx_categories_lft  ON categories_nested(lft);
CREATE UNIQUE INDEX idx_categories_rgt  ON categories_nested(rgt);
```

*Rule*: a parent’s `lft` is less than any value in its subtree and its `rgt` is greater.

Example rows:

| category\_id | lft | rgt | depth | category\_name |
| ------------ | --- | --- | ----- | -------------- |
| 1            | 1   | 14  | 0     | Electronics    |
| 2            | 2   | 9   | 1     | Computers      |
| 3            | 3   | 6   | 2     | Laptops        |
| 6            | 4   | 5   | 3     | Gaming Laptops |
| 4            | 7   | 8   | 2     | Desktops       |
| 5            | 10  | 13  | 1     | Televisions    |
| 7            | 11  | 12  | 2     | Business TVs   |

`width = rgt - lft + 1`; leaves have width = 2.

#### Strengths / Trade‑offs

MPTT delivers constant-time reads for whole subtrees, but at the cost of complex writes: inserting or moving nodes requires shifting bounds for many rows. It’s ideal for static or read-heavy hierarchies.

| ✔️ Benefits                                                                    | ⚠️ Costs                                                                                   |
| ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------ |
| **O(1) reads** of any subtree—no recursion, just `BETWEEN lft AND rgt`.        | Inserts / moves require shifting (updating) `lft`/`rgt` for *every* node right of the gap. |
| Easy aggregate queries (e.g., counts, sums) over subtrees with one `GROUP BY`. | Heavy write contention; large trees can lock many rows.                                    |
| Works on all SQL engines; no special features needed.                          | Can exhaust integer range if tree mutates frequently.                                      |

#### Everyday Queries

MPTT makes tree retrieval simple. Here are common patterns for subtrees, children, and breadcrumbs.

**Entire subtree of node \:id**

```sql
SELECT *
FROM   categories_nested AS c
JOIN   categories_nested AS root ON root.category_id = :id
WHERE  c.lft BETWEEN root.lft AND root.rgt
ORDER  BY c.lft;
```

**Immediate children**

```sql
SELECT *
FROM   categories_nested AS c
JOIN   categories_nested AS p ON p.category_id = :parent
WHERE  c.depth = p.depth + 1
  AND  c.lft BETWEEN p.lft AND p.rgt
ORDER  BY c.lft;
```

**Breadcrumb / ancestors of node \:id**

```sql
SELECT *
FROM   categories_nested AS anc
JOIN   categories_nested AS leaf ON leaf.category_id = :id
WHERE  anc.lft < leaf.lft AND anc.rgt > leaf.rgt
ORDER  BY anc.lft;
```

#### Maintenance Recipes

Writes in the Nested Set Model involve multi-step bound shifts. Always wrap these operations in one transaction to maintain consistency.

| Operation                                   | Steps (SQL pseudo-code)                                                                                                                                                                                                                                                        |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Insert** leaf as last child of parent \:p | 1️⃣ Compute `new_lft = p.rgt`, `new_rgt = p.rgt + 1`.<br>2️⃣ `UPDATE categories_nested SET rgt = rgt + 2 WHERE rgt >= new_lft;`<br>3️⃣ `UPDATE categories_nested SET lft = lft + 2 WHERE lft > new_lft;`<br>4️⃣ `INSERT ... VALUES (:id, new_lft, new_rgt, p.depth+1, :name);` |
| **Delete** a node + subtree                 | 1️⃣ `DELETE FROM categories_nested WHERE lft BETWEEN n.lft AND n.rgt;`<br>2️⃣ Compute `gap = n.rgt - n.lft + 1`.<br>3️⃣ Shift remaining nodes: `UPDATE ... SET lft = lft - gap WHERE lft > n.rgt;` and similarly for `rgt`.                                                    |
| **Move** subtree                            | Complex: remove (gap), shift, compute new position, re-insert with offset. Best done in stored procedure.                                                                                                                                                                      |

> *Tip:* All steps must run in a single transaction to avoid window overlap.

#### Implementation Tips

To make MPTT robust in production:

* Keep `lft` and `rgt` odd/even (e.g., parent `lft` odd) to detect leaves (`rgt = lft + 1`).
* Use `BIGINT` if the tree may exceed 2^31 nodes or undergo frequent reorganisations.
* For bulk imports, load rows with provisional numbers, then run a recursive counter to assign `lft`/`rgt` in one pass.
* Add `CHECK (rgt % 2 = 0 AND lft % 2 = 1)` if employing a parity scheme.

#### When to Use It

MPTT fits static, read-heavy hierarchies requiring fast subtree aggregations and reports:

* Reporting/analytics where tree structure is mostly static.
* Systems requiring lightning-fast subtotal queries over entire branches.
* Legacy applications already using MPTT numbering.

#### Limitations & Mitigations

Heavy shifts and concurrency can challenge MPTT; consider these strategies:

| Issue                                             | Mitigation                                                                                 |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| Heavy lock during large shifts                    | Use *gap strategy*: leave spare numbers (e.g., increment by 10) to amortise small inserts. |
| Integer exhaustion after many moves               | Periodically renumber tree offline (re-index).                                             |
| Concurrency conflicts (two inserts same location) | Wrap shifts in pessimistic locks (`SELECT ... FOR UPDATE`).                                |

#### Alternatives for Mutable Trees

When write performance becomes critical, explore these models:

* **Closure Table** – stores ancestor ↔ descendant pairs; moderate writes, fast reads.
* **Path Enumeration** – path string for quick reads, simpler though writes can be expensive.
* **Adjacency List + Recursive CTE** – minimal write cost, acceptable reads if depth is small or database supports fast recursion.


### Closure Table Model

The **Closure Table Model** captures every ancestor–descendant relationship, including self-relations, in a dedicated table. By precomputing the transitive closure of the hierarchy, queries become simple joins, offering consistent performance for both upward and downward navigations.

#### Table Schema

Implementing a closure table requires two tables: one for the nodes themselves and another for all their ancestor–descendant pairs. Each row in the closure table holds an `ancestor_id`, a `descendant_id`, and the `depth` between them.

```sql
CREATE TABLE categories (
    category_id   INT PRIMARY KEY,
    category_name TEXT NOT NULL
);

CREATE TABLE category_closure (
    ancestor_id   INT NOT NULL,
    descendant_id INT NOT NULL,
    depth         INT NOT NULL,
    PRIMARY KEY (ancestor_id, descendant_id),
    FOREIGN KEY (ancestor_id)   REFERENCES categories(category_id)
          ON DELETE CASCADE,
    FOREIGN KEY (descendant_id) REFERENCES categories(category_id)
          ON DELETE CASCADE
);

-- Fast look-ups
CREATE INDEX idx_closure_desc ON category_closure(descendant_id);
```

*Rule*: Every node has a **self-row** `(id, id, 0)`; direct children use `depth = 1`, grandchildren `depth = 2`, and so on.

#### Strengths / Trade‑offs

The closure table excels at query performance, providing constant-time joins for ancestor and descendant lookups. However, it incurs extra storage proportional to the number of relationships and adds complexity to write operations.

| ✔️ Benefits                                                                                   | ⚠️ Costs                                                                     |
| --------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| **Consistent O(1) reads** for any ancestor/descendant query—just a join on the closure table. | Storage overhead can grow from O(n·log n) to O(n²) in dense trees.           |
| Inserts and moves only touch paths related to the changed branch, not the entire tree.        | Managing closure logic often requires stored procedures or triggers.         |
| Excellent concurrency characteristics—no global bound shifts and minimal row locking.         | Deletions and moves require careful cascading updates to maintain integrity. |
| Easy to track aggregates (e.g., subtree size) by adding columns to the closure table.         | Additional indexes can become large; careful tuning is needed.               |

#### Everyday Queries

With all relationships precomputed, typical hierarchy operations reduce to straightforward joins and filters.

**All descendants of a node**

```sql
SELECT c.*
FROM   categories         AS c
JOIN   category_closure   AS cc ON cc.descendant_id = c.category_id
WHERE  cc.ancestor_id   = :id
  AND  cc.depth         > 0  -- exclude the node itself
ORDER  BY cc.depth, c.category_name;
```

**All ancestors (breadcrumbs)**

```sql
SELECT c.*
FROM   categories         AS c
JOIN   category_closure   AS cc ON cc.ancestor_id   = c.category_id
WHERE  cc.descendant_id = :id
  AND  cc.depth         > 0
ORDER  BY cc.depth DESC;  -- root first
```

**Immediate children**

```sql
SELECT c.*
FROM   categories         AS c
JOIN   category_closure   AS cc ON cc.descendant_id = c.category_id
WHERE  cc.ancestor_id = :id
  AND  cc.depth       = 1;
```

#### Maintenance Recipes

Updating the closure table involves inserting or deleting multiple relationship rows. Wrap these operations in transactions to preserve tree consistency.

| Operation                          | Steps                                                                                                                                                                                         |
| ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Insert** new node under parent p | 1️⃣ Insert the node into `categories`.<br>2️⃣ For each ancestor of p (including p itself), insert `(ancestor, new_node, depth+1)` rows.<br>3️⃣ Insert the self-row `(new_node, new_node, 0)`. |
| **Move** subtree from old to new p | 1️⃣ Delete closure rows where `ancestor` is in old ancestors and `descendant` in the subtree.<br>2️⃣ Insert new rows by pairing new parent’s ancestors with subtree nodes.                    |
| **Delete** node and its subtree    | Delete from `categories` where `category_id` in `(SELECT descendant_id FROM category_closure WHERE ancestor_id = :id)`; cascading drops closure rows.                                         |

#### Implementation Tips

To streamline closure table maintenance in production:

* Use triggers or stored procedures to automate insertion and deletion of closure rows.
* Consider materialised or indexed views for frequently used aggregates like subtree counts.
* Set `depth` as `SMALLINT` if tree depth is limited; otherwise use `INT`.
* For very large hierarchies, partition the closure table by `ancestor_id` range.
* Add a composite index on `(ancestor_id, depth)` for depth‑filtered lookups.

#### When to Use It

Closure tables are ideal for systems requiring both high-performance reads and frequent writes across the hierarchy:

* Interactive applications like task managers, ACL trees, or social graphs.
* Multi-tenant architectures where isolation of subtree operations is critical.
* Analytical workloads that need dynamic ancestor/descendant aggregations without the write penalty of Nested Sets.

#### Limitations & Mitigations

While powerful, closure tables can grow quickly and involve complex write logic. Use these strategies to address common challenges:

| Issue                                   | Mitigation                                                                                  |
| --------------------------------------- | ------------------------------------------------------------------------------------------- |
| Quadratic growth in dense trees         | Limit stored depths (e.g., only `depth ≤ k` rows) or prune distant ancestors if not needed. |
| Complex move operations                 | Encapsulate logic in atomic stored procedures rather than application code.                 |
| Large indexes due to many relationships | Employ partial or filtered indexes and consider table partitioning.                         |

#### Alternatives

When different trade-offs are needed, consider:

* **Nested Sets** – best for static trees with heavy read analytics; costly writes.
* **Path Enumeration** – simpler schema with fast reads but heavy write ripples.
* **Adjacency List + Recursive CTE** – minimal storage, simple writes, but slower deep-tree reads.


### Storing Hierarchical Data in SQL with **Recursive CTEs**

Using *Recursive Common Table Expressions* (CTEs) lets you navigate arbitrarily deep hierarchies within a single table. This method is fully declarative: the database optimizer figures out the traversal, so you write less procedural code.

#### Why Bother?

Recursive CTEs provide a portable, one-table solution for unlimited depth hierarchies. They work across major SQL vendors (PostgreSQL, SQL Server, Oracle, MySQL, MariaDB, SQLite, DuckDB) and can retrieve descendants, ancestors, paths, and even leaf nodes—all with a consistent query structure.

#### Table Layout (Adjacency-List)

To use recursive CTEs, your table only needs an ID and a self-reference to its parent. This simple schema underpins the traversal logic without extra helper tables.

```sql
CREATE TABLE categories (
  category_id   INT PRIMARY KEY,
  parent_id     INT REFERENCES categories(category_id),
  category_name TEXT NOT NULL
);
```

##### Visual Map of Demo Data

Below is the tree we'll query in examples. It shows categories and subcategories connected by parent–child links.

```
Electronics
├─ Computers
│  ├─ Laptops
│  │  ├─ Gaming Laptops
│  │  └─ Business Laptops
│  └─ Desktops
└─ Televisions
```

#### The Recursive-CTE Template

Recursive CTEs follow a three-part pattern: an *anchor* to seed the starting rows, a *recursive step* that joins to the CTE itself to add layers, and a *final query* to filter or order the results.

```sql
WITH RECURSIVE cte_name AS (
    -- ① Anchor: select initial rows (e.g., roots)
    SELECT ... FROM base_table WHERE ...

    UNION ALL

    -- ② Recursive step: join new rows to previous layer
    SELECT ...
    FROM   base_table
    JOIN   cte_name ON ...
)
SELECT *            -- ③ Final query: retrieve or filter the accumulated set
FROM   cte_name;
```

The engine executes the anchor once, then repeats the recursive step until no new rows emerge.

#### Example A – Breadcrumb Path for Every Category

This query builds a `full_path` column by concatenating names from root to each node. Each recursion appends the child’s name and increments the depth.

```sql
WITH RECURSIVE category_path AS (
    -- ① Anchor: top-level categories
    SELECT
        category_id,
        parent_id,
        category_name,
        category_name            AS full_path,
        0                        AS depth
    FROM   categories
    WHERE  parent_id IS NULL

    UNION ALL

    -- ② Recursive step: append child names
    SELECT
        c.category_id,
        c.parent_id,
        c.category_name,
        cp.full_path || ' > ' || c.category_name AS full_path,
        cp.depth + 1                         AS depth
    FROM   categories      c
    JOIN   category_path   cp ON cp.category_id = c.parent_id
)
SELECT *
FROM   category_path
ORDER  BY full_path;
```

*Key Ideas:* use `UNION ALL` to preserve duplicates, `depth` for ordering or indenting, and string concatenation (`||` or `CONCAT()`).

#### Example B – Subtree of a Chosen Node

To extract a subtree, seed the CTE with the chosen node, then recur downward to include all descendants.

```sql
WITH RECURSIVE sub_tree AS (
    -- ① Anchor: the selected category
    SELECT * FROM categories WHERE category_name = 'Computers'

    UNION ALL

    -- ② Recursive step: find children of the current layer
    SELECT c.*
    FROM   categories c
    JOIN   sub_tree  s ON s.category_id = c.parent_id
)
SELECT *
FROM   sub_tree;
```

Swap the join direction (`ON c.category_id = s.parent_id`) to climb upward and list ancestors instead.

#### Example C – Leaf Nodes Only

This pattern discovers nodes that never appear as a parent. The CTE collects all nodes, then a final `LEFT JOIN` filters out those with children.

```sql
WITH RECURSIVE walker AS (
    SELECT category_id, parent_id FROM categories
    UNION ALL
    SELECT c.category_id, c.parent_id
    FROM   categories c
    JOIN   walker     w ON w.category_id = c.parent_id
)
SELECT w.category_id
FROM   walker w
LEFT   JOIN categories x ON x.parent_id = w.category_id
WHERE  x.category_id IS NULL;
```

#### Performance & Safety Checklist

Recursive CTEs are powerful but can misbehave on large or cyclic graphs. Follow these guidelines for robust, efficient queries.

| ✔︎ Do                                                                 | ✘ Avoid                                                          |
| --------------------------------------------------------------------- | ---------------------------------------------------------------- |
| Index `parent_id` (and `category_id`).                                | Cartesian joins in the recursive part.                           |
| Add `WHERE depth < 30` if depth is bounded.                           | Deep recursion on un-indexed columns.                            |
| Test with small data first – verify that recursion stops.             | Recursing on cyclic graphs without depth guards.                 |
| Use `UNION ALL` (not `UNION`) unless duplicate elimination is needed. | Heavy aggregates inside the recursive member – separate queries. |

#### Quick Reference

A handy cheat sheet for common tasks:

```sql
-- Descendants: JOIN cte ON cte.category_id = base.parent_id
-- Ancestors:   JOIN cte ON cte.parent_id   = base.category_id
-- Path string: full_path || ' > ' || child.name
-- Depth:       parent.depth + 1
```

#### When Recursive CTEs Are **Not** Enough

While versatile, recursive CTEs can struggle with very deep or wide trees, frequent full-branch reads, or legacy systems lacking support. In such cases, explore **Closure Tables**, **Nested Sets**, **Materialised Paths**, or specialized graph databases (e.g., Neo4j).
