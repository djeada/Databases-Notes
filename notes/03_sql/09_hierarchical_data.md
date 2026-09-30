# Hierarchical Data: Represent and Query a Tree

A bookstore's categories form a hierarchy: Books contains Computing, and Computing contains Databases and Programming. A **tree** represents that structure using nodes and parent–child relationships. A **root** has no parent. A **leaf** has no children. A node's **descendants** are its children, their children, and so on; its **ancestors** lie on the path toward the root.

Relational tables can represent trees. The main question is which relationships to store directly and which to calculate when querying. Start with [joins](06_joins_subqueries_and_views.md); this note introduces recursion through a complete SQLite example.

## Store each node's immediate parent

An **adjacency list** gives each row a reference to its parent in the same table. Run this standalone setup in a fresh SQLite database:

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    parent_id INTEGER REFERENCES categories(category_id),
    CHECK (parent_id IS NULL OR parent_id <> category_id)
);

CREATE INDEX idx_categories_parent ON categories(parent_id);

INSERT INTO categories VALUES
    (1, 'Books', NULL),
    (2, 'Computing', 1),
    (3, 'Fiction', 1),
    (4, 'Databases', 2),
    (5, 'Programming', 2),
    (6, 'SQL', 4);
```

```text
Books (1)
├── Computing (2)
│   ├── Databases (4)
│   │   └── SQL (6)
│   └── Programming (5)
└── Fiction (3)
```

The foreign key prevents a reference to a missing parent. The check prevents a node from being its own immediate parent. Neither prevents a longer cycle, such as making Computing a child of SQL. We return to that issue after learning the queries.

## Find children with an ordinary filter

```sql
SELECT category_id, name
FROM categories
WHERE parent_id = 2
ORDER BY category_id;
```

| category_id | name |
|---|---|
| 4 | Databases |
| 5 | Programming |

This returns Computing's **immediate children**. It does not include SQL, which is two levels below Computing.

## Name an intermediate result with a CTE

A **common table expression (CTE)** names a query result for use within one SQL statement. An ordinary CTE makes steps easier to read:

```sql
WITH computing_children AS (
    SELECT category_id, name
    FROM categories
    WHERE parent_id = 2
)
SELECT name FROM computing_children ORDER BY category_id;
```

It returns Databases and Programming again. The name does not create a permanent table or view. A CTE also does not guarantee a particular physical execution strategy.

## Extend the result one level at a time

A **recursive CTE** repeatedly uses rows found so far to find more rows. This query starts with Computing and walks downward:

```sql
WITH RECURSIVE subtree(category_id, name, depth) AS (
    SELECT category_id, name, 0
    FROM categories
    WHERE category_id = 2

    UNION ALL

    SELECT child.category_id, child.name, parent.depth + 1
    FROM categories AS child
    JOIN subtree AS parent ON child.parent_id = parent.category_id
)
SELECT category_id, name, depth
FROM subtree
ORDER BY depth, category_id;
```

| category_id | name | depth |
|---|---|---|
| 2 | Computing | 0 |
| 4 | Databases | 1 |
| 5 | Programming | 1 |
| 6 | SQL | 2 |

The first query is the **anchor**: it supplies the starting row. The second is the **recursive step**: it finds children of previously found rows and adds one to their depth. `UNION ALL` combines those rows without removing duplicates. In this tree, expansion ends when there are no more children.

This result includes the starting node. To return only its descendants, add `WHERE depth > 0` to the final query. `ORDER BY` determines display order; do not rely on the engine's internal traversal order. See SQLite's official [WITH documentation](https://www.sqlite.org/lang_with.html) for recursion rules and limits.

## Walk upward for a breadcrumb

To find SQL's ancestors, reverse the relationship: each current node points to its parent.

```sql
WITH RECURSIVE ancestors(category_id, name, parent_id, distance) AS (
    SELECT category_id, name, parent_id, 0
    FROM categories
    WHERE category_id = 6

    UNION ALL

    SELECT parent.category_id, parent.name, parent.parent_id,
           child.distance + 1
    FROM categories AS parent
    JOIN ancestors AS child ON parent.category_id = child.parent_id
)
SELECT name, distance
FROM ancestors
ORDER BY distance DESC;
```

| name | distance |
|---|---|
| Books | 3 |
| Computing | 2 |
| Databases | 1 |
| SQL | 0 |

Ordering largest distance first produces the path from root to selected category.

## Find leaves and carry a readable path

A leaf is a node with no children, not necessarily a node at the deepest level. The adjacency setup can answer that directly:

```sql
SELECT c.category_id, c.name
FROM categories AS c
WHERE NOT EXISTS (
    SELECT 1 FROM categories AS child WHERE child.parent_id = c.category_id
)
ORDER BY c.category_id;
```

The leaves are Fiction (3), Programming (5), and SQL (6). Fiction is close to the root but still a leaf. To display a path while traversing, carry a value into each recursive step:

```sql
WITH RECURSIVE category_paths(category_id, name, path) AS (
    SELECT category_id, name, name FROM categories WHERE parent_id IS NULL
    UNION ALL
    SELECT c.category_id, c.name, p.path || ' / ' || c.name
    FROM categories AS c
    JOIN category_paths AS p ON c.parent_id = p.category_id
)
SELECT category_id, path FROM category_paths ORDER BY category_id;
```

SQL's path is `Books / Computing / Databases / SQL`. This calculates a display path; it does not store another copy of every ancestor's name. A rename is reflected on the next query. If names contain the chosen separator, a UI should format a structured list of nodes rather than treat this string as an unambiguous identifier encoding.

## A parent reference does not guarantee a tree

To move a branch, an adjacency list often changes only the moved node's parent. But the new parent must not be that node or one of its descendants. Otherwise the move creates a cycle.

For example, setting Computing's parent to SQL would create `Computing → Databases → SQL → Computing`. The foreign key still points to existing rows, and the immediate-self-parent check still passes. A recursive query using `UNION ALL` can then keep expanding instead of terminating normally.

A production design needs cycle prevention or detection, an appropriate traversal bound, and transaction logic that handles concurrent moves. A “check, then update” sequence can race with another move. Do not assume replacing `UNION ALL` with `UNION` always solves cycles: if a changing depth or path is included, repeated visits can still produce distinct rows.

This schema also allows more than one root, which represents a **forest**. If the business requires exactly one root, that is an additional rule.

## Detect cycles instead of trusting a depth counter

A maximum depth is useful for limiting work, but it does not identify which node was revisited. For diagnostic traversal in SQLite, carry a delimited list of visited IDs and reject a repeated ID:

```sql
WITH RECURSIVE safe_walk(category_id, name, visited) AS (
    SELECT category_id, name, ',' || category_id || ','
    FROM categories WHERE category_id = 2
    UNION ALL
    SELECT c.category_id, c.name, p.visited || c.category_id || ','
    FROM categories AS c
    JOIN safe_walk AS p ON c.parent_id = p.category_id
    WHERE instr(p.visited, ',' || c.category_id || ',') = 0
)
SELECT category_id, name FROM safe_walk ORDER BY category_id;
```

On the valid setup it returns IDs 2, 4, 5, 6. This avoids revisiting a node along a path; it does not repair invalid parent relationships or make a cycle-producing update acceptable. A production traversal should also consider the size of the reachable set and whether the structure is actually a tree or a graph with multiple paths to a node.

References: [SQLite recursive CTEs](https://www.sqlite.org/lang_with.html) and [PostgreSQL ltree](https://www.postgresql.org/docs/current/ltree.html).

## Compare other representations after understanding adjacency

| Model | What is stored | Useful property | Maintenance cost |
|---|---|---|---|
| Adjacency list | Immediate parent on each node | Simple direct-child lookup and branch move | Full branches need recursive traversal |
| Materialized path / path enumeration | An ancestor path, such as `/1/2/4/6/` | Descendants can be found by a path prefix | A move changes paths throughout the branch |
| Nested set | Left and right positions marking a node's subtree interval | Descendants can be found by an interval | Inserts and moves can require many position updates |
| Closure table | Ancestor–descendant pairs, often with depth | Direct queries for transitive relationships | Extra rows must be maintained with the base tree |

Path encodings need unambiguous delimiters so `/1/2/` cannot accidentally match an unrelated identifier. Prefix-query indexing depends on the engine and representation. A closure table often includes each node's self-pair with depth zero; for a long chain, its number of relationships can grow quadratically.

Choose based on actual operations: are branches frequently moved, are whole subtrees read, or are ancestor checks dominant? Start with adjacency unless another model's benefits justify maintaining additional structure.

## Materialized paths store the traversal result

A **materialized path** encodes each node's location directly. This independent SQLite table uses delimited IDs rather than names, so renaming Computing does not change descendant identifiers:

```sql
CREATE TABLE hier_paths (
    category_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    path TEXT NOT NULL UNIQUE
);
INSERT INTO hier_paths VALUES
    (1, 'Books', '/1/'),
    (2, 'Computing', '/1/2/'),
    (3, 'Fiction', '/1/3/'),
    (4, 'Databases', '/1/2/4/'),
    (5, 'Programming', '/1/2/5/'),
    (6, 'SQL', '/1/2/4/6/');

SELECT category_id, name, path
FROM hier_paths
WHERE path LIKE '/1/2/%'
ORDER BY category_id;
```

The result contains Computing, Databases, Programming, and SQL. The trailing delimiter makes `/1/2/` different from `/1/20/`. This query includes the starting node. To exclude it, add `category_id <> 2`.

Moving SQL from Databases to Programming changes its prefix. If SQL had children, they would need the same prefix replacement:

```sql
BEGIN;
UPDATE hier_paths
SET path = '/1/2/5/6/' || substr(path, length('/1/2/4/6/') + 1)
WHERE path LIKE '/1/2/4/6/%';
SELECT path FROM hier_paths WHERE category_id = 6;
ROLLBACK;
```

The intermediate path is `/1/2/5/6/`; rollback restores the old one. `substr` preserves any suffix below the moved root. The update must run only after validating that the proposed parent is outside the moved subtree. A string path alone does not guarantee that every encoded ancestor exists or that concurrent moves cannot conflict.

An index can sometimes accelerate prefix lookup, but the details depend on collation, operator, and engine. PostgreSQL's `ltree` extension provides a dedicated path type and tree operators, rather than asking ordinary text to handle every operation. Materialized paths favor frequent subtree reads when branch moves are relatively rare.

## Nested sets replace traversal with an interval

A **nested set** stores a left and right traversal position. Imagine entering a node, numbering its left boundary, visiting its children, and numbering its right boundary on exit. A descendant's whole interval lies inside its ancestor's interval:

```sql
CREATE TABLE hier_nested (
    category_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    lft INTEGER NOT NULL,
    rgt INTEGER NOT NULL,
    CHECK (lft < rgt)
);
INSERT INTO hier_nested VALUES
    (1, 'Books', 1, 12),
    (2, 'Computing', 2, 9),
    (3, 'Fiction', 10, 11),
    (4, 'Databases', 3, 6),
    (5, 'Programming', 7, 8),
    (6, 'SQL', 4, 5);

SELECT child.name
FROM hier_nested AS parent
JOIN hier_nested AS child
  ON child.lft >= parent.lft AND child.rgt <= parent.rgt
WHERE parent.category_id = 2
ORDER BY child.lft;
```

The result is Computing, Databases, SQL, Programming, in traversal order. Strict inequalities would exclude Computing itself. SQL's breadcrumb can reverse the containment test:

```sql
SELECT ancestor.name
FROM hier_nested AS node
JOIN hier_nested AS ancestor
  ON ancestor.lft <= node.lft AND ancestor.rgt >= node.rgt
WHERE node.category_id = 6
ORDER BY ancestor.lft;
```

It returns Books, Computing, Databases, SQL. Both queries avoid recursive expansion because the stored interval already encodes transitive containment.

## Make room before inserting into a nested set

Fiction's current right boundary is 11. To insert a child there, shift later positions and enclosing right boundaries by two:

```sql
BEGIN;
UPDATE hier_nested SET rgt = rgt + 2 WHERE rgt >= 11;
UPDATE hier_nested SET lft = lft + 2 WHERE lft >= 11;
INSERT INTO hier_nested VALUES (7, 'Mysteries', 11, 12);
SELECT category_id, name, lft, rgt
FROM hier_nested
WHERE category_id IN (1, 3, 7)
ORDER BY category_id;
ROLLBACK;
```

The intermediate rows are Books `(1, 14)`, Fiction `(10, 13)`, and Mysteries `(11, 12)`, where the pairs are left/right boundaries. The transaction keeps the position changes and new node together. Rollback restores the original tree.

This exercise has no unique boundary indexes. Naively adding uniqueness and using bulk increments can cause transient collisions under some update strategies; maintenance algorithms must account for the constraints actually declared. The row check only guarantees `lft < rgt`, not a valid tree's entire interval structure. Concurrent insertions and moves require coordination across the affected tree. Nested sets are attractive for relatively static reporting hierarchies, while frequent changes can rewrite many rows.

## Closure tables store each reachable pair

A **closure table** materializes the relation “ancestor reaches descendant.” Nodes remain separate from their transitive relationships:

```sql
CREATE TABLE hier_closure_nodes (
    category_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE hier_closure (
    ancestor_id INTEGER NOT NULL REFERENCES hier_closure_nodes(category_id),
    descendant_id INTEGER NOT NULL REFERENCES hier_closure_nodes(category_id),
    depth INTEGER NOT NULL CHECK (depth >= 0),
    PRIMARY KEY (ancestor_id, descendant_id)
);
CREATE INDEX hier_closure_by_descendant
ON hier_closure(descendant_id, depth);

INSERT INTO hier_closure_nodes VALUES
    (1, 'Books'), (2, 'Computing'), (3, 'Fiction'),
    (4, 'Databases'), (5, 'Programming'), (6, 'SQL');
INSERT INTO hier_closure VALUES
    (1, 1, 0), (2, 2, 0), (3, 3, 0),
    (4, 4, 0), (5, 5, 0), (6, 6, 0),
    (1, 2, 1), (1, 3, 1), (1, 4, 2), (1, 5, 2), (1, 6, 3),
    (2, 4, 1), (2, 5, 1), (2, 6, 2), (4, 6, 1);

SELECT n.name, c.depth
FROM hier_closure AS c
JOIN hier_closure_nodes AS n ON n.category_id = c.descendant_id
WHERE c.ancestor_id = 2
ORDER BY c.depth, n.category_id;
```

The rows are Computing 0, Databases 1, Programming 1, SQL 2. Each node's self-pair has depth zero. Looking up a breadcrumb instead filters `descendant_id` and joins node names through `ancestor_id`; order by depth descending to put the root first.

The primary key prevents duplicate pairs; it does not prove the pairs describe one correct tree. The maintenance code must insert all required paths and remove obsolete ones. Foreign keys only verify that referenced nodes exist.

## Insert and move a leaf in the closure model

To put Indexes beneath Databases, copy all of Databases' ancestors and increase their distances by one, then add Indexes' self-pair:

```sql
BEGIN;
INSERT INTO hier_closure_nodes VALUES (7, 'Indexes');
INSERT INTO hier_closure VALUES (7, 7, 0);
INSERT INTO hier_closure (ancestor_id, descendant_id, depth)
SELECT ancestor_id, 7, depth + 1
FROM hier_closure WHERE descendant_id = 4;

SELECT n.name, c.depth
FROM hier_closure AS c
JOIN hier_closure_nodes AS n ON n.category_id = c.ancestor_id
WHERE c.descendant_id = 7
ORDER BY c.depth DESC;
ROLLBACK;
```

The breadcrumb is Books 3, Computing 2, Databases 1, Indexes 0. Three ancestor rows and one self-pair are added. A long chain needs more pairs for each new node than a shallow tree does.

For the existing leaf SQL, a move beneath Programming removes its old external ancestor paths and builds new ones:

```sql
BEGIN;
DELETE FROM hier_closure WHERE descendant_id = 6 AND ancestor_id <> 6;
INSERT INTO hier_closure (ancestor_id, descendant_id, depth)
SELECT ancestor_id, 6, depth + 1
FROM hier_closure WHERE descendant_id = 5;

SELECT n.name
FROM hier_closure AS c
JOIN hier_closure_nodes AS n ON n.category_id = c.ancestor_id
WHERE c.descendant_id = 6
ORDER BY c.depth DESC;
ROLLBACK;
```

It temporarily produces Books, Computing, Programming, SQL. This algorithm is specifically for a **leaf**. Moving a non-leaf branch must preserve paths inside that branch, remove paths from old external ancestors to every descendant, and add combinations of new ancestors with branch descendants. New depth is the new ancestor-to-parent distance plus one plus the moved-root-to-descendant distance. Merely replacing the moved root's paths would leave its children attached to obsolete ancestors.

Validate a move's cycle rule and coordinate competing mutations in the same transaction. Some designs retain an adjacency `parent_id` as the direct relationship and maintain the closure table as a derived structure. Then both must be updated together, and a rebuild procedure should be able to regenerate the closure from valid parents.

## Delete a subtree according to the representation

Deleting a category raises a business question before it raises a SQL question: should its books be reassigned, should only an empty branch be removable, or should the whole branch disappear? None of these practice schemas models book assignments. Their deletion exercises demonstrate structural changes only, inside transactions that are rolled back.

For the materialized-path table, the branch prefix identifies all affected nodes:

```sql
BEGIN;
DELETE FROM hier_paths WHERE path LIKE '/1/2/4/%';
SELECT category_id, name FROM hier_paths ORDER BY category_id;
ROLLBACK;
```

IDs 4 and 6 disappear temporarily; IDs 1, 2, 3, and 5 remain. With adjacency, deleting only node 4 would fail its incoming foreign key because SQL still references it. A `CASCADE` policy would be a separate deliberate choice. A safe adjacency deletion can identify the full subtree first and remove it according to the engine's reference rules.

In the closure representation, delete the pairs involving a branch's nodes before deleting those nodes. Capture the target IDs before changing the closure, so later commands do not lose the traversal they depend on:

```sql
BEGIN;
CREATE TEMP TABLE hier_delete_targets AS
SELECT descendant_id AS category_id
FROM hier_closure WHERE ancestor_id = 4;
DELETE FROM hier_closure
WHERE ancestor_id IN (SELECT category_id FROM hier_delete_targets)
   OR descendant_id IN (SELECT category_id FROM hier_delete_targets);
DELETE FROM hier_closure_nodes
WHERE category_id IN (SELECT category_id FROM hier_delete_targets);
DROP TABLE hier_delete_targets;
SELECT category_id, name FROM hier_closure_nodes ORDER BY category_id;
ROLLBACK;
```

Again, only IDs 1, 2, 3, and 5 remain during the transaction. Removing merely the pair `(4, 6)` would not delete SQL or its other ancestor relationships. The closure's transitive rows are facts that must remain consistent with the chosen tree.

For nested sets, subtree deletion also leaves a gap in traversal positions. Removing Databases' interval `[3, 6]` frees four positions:

```sql
BEGIN;
DELETE FROM hier_nested WHERE lft >= 3 AND rgt <= 6;
UPDATE hier_nested SET lft = lft - 4 WHERE lft > 6;
UPDATE hier_nested SET rgt = rgt - 4 WHERE rgt > 6;
SELECT category_id, name, lft, rgt FROM hier_nested ORDER BY lft;
ROLLBACK;
```

The remaining intervals are Books `[1, 8]`, Computing `[2, 5]`, Programming `[3, 4]`, and Fiction `[6, 7]`. This algorithm uses the example's unconstrained boundary columns and one coordinated writer. A production implementation must handle concurrent structural writes and any additional uniqueness rules.

## Choose from the workload, then validate maintenance

For an organizational chart with frequent reporting-line changes, adjacency keeps a move small, and recursive queries can calculate reporting chains. For a largely static category taxonomy with frequent subtree reports, nested sets can make reads simple. For breadcrumb and ancestor checks that dominate traffic, closure tables precompute exactly those relationships. Materialized paths fit prefix-based navigation, especially when paths are supported by a dedicated type such as PostgreSQL `ltree`.

These are workload choices, not a ranking from primitive to advanced. A chain of N nodes needs N(N+1)/2 closure pairs when self-pairs are included. A wide shallow tree can need far fewer. Materialized paths can grow with depth, and nested-set edits can affect unrelated nodes whose traversal positions follow the edited branch.

Useful validation includes detecting cycles, checking parent existence, checking path prefixes against actual ancestors, checking that nested intervals are nested or disjoint rather than crossing, and comparing closure depths with an adjacency traversal. Preserve a rebuild path when extra structures are derived. A graph allowing several parents needs different maintenance rules from this tree: deleting one edge may leave a node reachable through another path, and one closure pair cannot necessarily represent every path's distinct length.

## Check your understanding

1. Why does the immediate-child query omit SQL?
2. What does the recursive query's anchor contribute?
3. Why does the descendant query include Computing itself?
4. Which invalid structure can pass the schema's foreign key and check?
5. Why can moving a branch be more expensive with materialized paths?

Next: [aggregate functions](10_aggregate_functions.md) summarize groups; [window functions](11_window_functions.md) retain rows while calculating across related records.
