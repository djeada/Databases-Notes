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

## A parent reference does not guarantee a tree

To move a branch, an adjacency list often changes only the moved node's parent. But the new parent must not be that node or one of its descendants. Otherwise the move creates a cycle.

For example, setting Computing's parent to SQL would create `Computing → Databases → SQL → Computing`. The foreign key still points to existing rows, and the immediate-self-parent check still passes. A recursive query using `UNION ALL` can then keep expanding instead of terminating normally.

A production design needs cycle prevention or detection, an appropriate traversal bound, and transaction logic that handles concurrent moves. A “check, then update” sequence can race with another move. Do not assume replacing `UNION ALL` with `UNION` always solves cycles: if a changing depth or path is included, repeated visits can still produce distinct rows.

This schema also allows more than one root, which represents a **forest**. If the business requires exactly one root, that is an additional rule.

## Compare other representations after understanding adjacency

| Model | What is stored | Useful property | Maintenance cost |
|---|---|---|---|
| Adjacency list | Immediate parent on each node | Simple direct-child lookup and branch move | Full branches need recursive traversal |
| Materialized path / path enumeration | An ancestor path, such as `/1/2/4/6/` | Descendants can be found by a path prefix | A move changes paths throughout the branch |
| Nested set | Left and right positions marking a node's subtree interval | Descendants can be found by an interval | Inserts and moves can require many position updates |
| Closure table | Ancestor–descendant pairs, often with depth | Direct queries for transitive relationships | Extra rows must be maintained with the base tree |

Path encodings need unambiguous delimiters so `/1/2/` cannot accidentally match an unrelated identifier. Prefix-query indexing depends on the engine and representation. A closure table often includes each node's self-pair with depth zero; for a long chain, its number of relationships can grow quadratically.

Choose based on actual operations: are branches frequently moved, are whole subtrees read, or are ancestor checks dominant? Start with adjacency unless another model's benefits justify maintaining additional structure.

## Check your understanding

1. Why does the immediate-child query omit SQL?
2. What does the recursive query's anchor contribute?
3. Why does the descendant query include Computing itself?
4. Which invalid structure can pass the schema's foreign key and check?
5. Why can moving a branch be more expensive with materialized paths?

Next: [aggregate functions](10_aggregate_functions.md) summarize groups; [window functions](11_window_functions.md) retain rows while calculating across related records.
