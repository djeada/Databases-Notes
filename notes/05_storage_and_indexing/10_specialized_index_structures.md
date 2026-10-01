# Specialized Index Structures: Hash, GIN, GiST, SP-GiST, BRIN, Bitmap, and Search

B-tree is the default general-purpose index for many relational workloads, but not every predicate is naturally ordered.

Different index structures are designed for different questions.

The correct starting point is:

> Which operator or access pattern must be accelerated?

not:

> Which exotic index type sounds fastest?

## Index structure follows operator semantics

Examples:

~~~text
x = 42                         -> equality
x BETWEEN 10 AND 20            -> ordered range
array contains tag             -> membership/containment
document contains term         -> inverted search
point is near polygon          -> spatial relationship
timestamp on ordered table     -> block/range summary
~~~

One index type does not optimize all of these.

## B-tree recap

B-trees are good for data with useful ordering.

Typical operations:

~~~text
=
<
<=
>
>=
BETWEEN
ORDER BY
~~~

They are often right for identifiers, timestamps, numeric ranges, and composite equality/range access.

## Hash indexes

Hash indexes map a key to a bucket.

~~~text
hash(key) -> bucket -> matching entries
~~~

They are naturally suited to equality.

They do not preserve key order.

Thus:

~~~text
x = ?
~~~

fits, while ordered range access does not.

## PostgreSQL hash index

PostgreSQL supports hash indexes for equality operators.

~~~sql
CREATE INDEX idx_sessions_token_hash
ON sessions USING hash(token);
~~~

A B-tree also supports equality and is more versatile.

Choose hash only from measured workload and engine behavior.

## Bitmap indexes versus bitmap scans

These are different concepts.

A persistent bitmap index stores bitmaps as an index structure. Some analytical databases support this directly.

PostgreSQL commonly performs bitmap index scans and bitmap heap scans using ordinary indexes.

~~~text
index A -> bitmap of row locations
index B -> bitmap of row locations
             |
             v
         combine
             |
             v
       visit table pages
~~~

Do not call every PostgreSQL bitmap scan a bitmap index.

## Bitmap-style workloads

Low-cardinality analytical filters such as:

~~~text
country
status
segment
~~~

can combine well in read-heavy systems.

Persistent bitmap structures can be expensive under frequent updates depending on the engine.

## Inverted indexes

An inverted index maps terms or elements to rows/documents.

~~~text
"database" -> documents 1, 5, 9
"index"    -> documents 2, 5, 8
~~~

Useful for:

- full-text search,
- array membership,
- JSON containment,
- tags.

## PostgreSQL GIN

GIN is a generalized inverted index.

It is commonly useful when one indexed item contains many component values.

Examples include:

- arrays,
- tsvector full-text search,
- JSONB containment/operators with suitable operator classes.

Array example:

~~~sql
CREATE INDEX idx_articles_tags
ON articles USING gin(tags);
~~~

Full-text example:

~~~sql
CREATE INDEX idx_articles_search
ON articles USING gin(search_vector);
~~~

## GIN write trade-off

One row can contribute many postings.

A document with many terms can create many index entries.

Costs can include:

- larger indexes,
- more write work,
- pending-list/maintenance behavior,
- slower update-heavy workloads.

## GiST

GiST is a framework for tree-structured search strategies.

It is commonly used for:

- geometric/spatial values,
- range types,
- nearest-neighbor searches,
- extension-defined data types.

It is not simply "the spatial index," though spatial workloads are a major use.

## Spatial example

With suitable PostgreSQL/PostGIS types and operator classes, GiST can accelerate questions such as:

~~~text
which geometries overlap this region?
which points are nearest?
~~~

The query operator must match the operator class.

## Range types

PostgreSQL range types can use GiST for overlap and containment relationships.

Conceptually:

~~~text
reservation period overlaps requested period
~~~

This is different from indexing one scalar timestamp.

## SP-GiST

SP-GiST supports space-partitioned search structures.

Depending on operator class, it can represent structures such as:

- tries,
- quadtrees,
- k-d-style partitions.

Use it when the data/query type has a compatible operator class.

## GIN versus GiST

Some workloads can use either family.

For PostgreSQL full text, general intuition is:

- GIN stores detailed postings and often favors search performance,
- GiST can be smaller/general but may require rechecks depending on operator class.

Use current engine documentation and representative tests instead of memorizing one as universally superior.

## BRIN

BRIN means Block Range INdex in PostgreSQL.

Instead of one entry per row, BRIN summarizes ranges of table pages.

~~~text
pages 0-127:
min timestamp = Jan 1
max timestamp = Jan 3

pages 128-255:
min timestamp = Jan 3
max timestamp = Jan 6
~~~

A query for Jan 5 can skip page ranges whose summaries cannot contain Jan 5.

## BRIN and physical correlation

BRIN is especially useful when the indexed value correlates with physical row order.

Examples:

- append-only timestamp,
- increasing sequence,
- naturally clustered measurement time.

If values are randomly distributed across every page range, summaries become broad and less useful.

## BRIN size advantage

Because BRIN summarizes page ranges rather than indexing every row, it can be much smaller than a B-tree on a huge correlated table.

Trade-off:

- it is lossy,
- candidate page ranges still require checking,
- it is weaker on uncorrelated data.

## Runnable BRIN exercise

This chapter adds:

~~~text
scripts/indexing/postgres_brin_demo.sql
~~~

Run:

~~~bash
docker exec -i postgres-local \
  psql -U demo -d test \
  < scripts/indexing/postgres_brin_demo.sql
~~~

The exercise creates a time-ordered event table, builds B-tree and BRIN indexes, reports their sizes, and shows EXPLAIN output for a narrow time window.

The exact plan depends on local statistics and table size.

## Full-text indexing

Searching:

~~~sql
WHERE body LIKE '%database%'
~~~

cannot generally use a normal B-tree for arbitrary substring search.

Full-text search tokenizes and normalizes text into searchable terms.

~~~text
document
  |
tokenize/normalize
  |
term postings
  |
rank/search
~~~

Use the database's full-text feature or a search engine when appropriate.

## Trigram indexes

PostgreSQL's pg_trgm extension can support similarity and certain LIKE/ILIKE patterns through GiST or GIN operator classes.

This is different from linguistic full-text search.

## JSON indexing

Different JSON operations need different access structures.

Scalar extraction:

~~~text
payload country = DE
~~~

may fit an expression B-tree.

Containment/membership may fit GIN.

There is no universal JSON index.

## Spatial indexes

Spatial predicates include:

- intersects,
- contains,
- distance,
- nearest neighbor.

A B-tree over raw latitude and longitude is not equivalent to a true spatial index for arbitrary geometry operations.

## Zone maps and data skipping

Analytical systems often maintain min/max or other metadata per block.

~~~text
block 1 amount: 0..100
block 2 amount: 100..200
block 3 amount: 10000..20000
~~~

A query for amount > 5000 can skip blocks 1 and 2.

This resembles BRIN's summary idea but belongs to the analytical engine's implementation.

## Bloom filters

A Bloom filter can answer:

~~~text
definitely not present
or
possibly present
~~~

It is a probabilistic membership structure.

Bloom filters are common in LSM/storage systems and some extensions.

They do not support ordering or ranges.

## Operator classes matter

In PostgreSQL, index access methods rely on operator classes defining:

- representation,
- supported operators,
- search/comparison behavior.

So "use GIN" is incomplete without the data type and operator class.

## Decision table

| Query pattern | Candidate structure |
| --- | --- |
| equality/range/order | B-tree |
| equality only | B-tree or engine hash |
| array/JSON containment | GIN/inverted, depending on operator |
| full-text terms | inverted/full-text |
| geometry/ranges/nearest-neighbor | GiST/SP-GiST or spatial index |
| huge physically correlated table | BRIN/data-skipping summary |
| low-cardinality analytical filters | bitmap-style indexing where supported |

Always validate against the specific engine.

## Index versus external system

A database index is not always the right answer.

Advanced search may need:

- language analyzers,
- typo tolerance,
- relevance ranking,
- autocomplete,
- distributed search.

An engine such as OpenSearch/Elasticsearch can be more suitable.

Large analytics may benefit more from columnar storage and data skipping than from many OLTP indexes.

## Common mistakes

- Assuming hash is automatically faster than B-tree for equality.
- Assuming low cardinality automatically means bitmap index.
- Expecting one GIN index to optimize every JSON query.
- Treating BRIN as a tiny B-tree.
- Treating latitude/longitude B-trees as full spatial indexing.

## Related notes

- [Indexing](05_indexing.md)
- [Covering, partial, and expression indexes](08_covering_partial_and_expression_indexes.md)
- [Row vs column storage](02_row_based_vs_column_based_databases.md)
- [Query optimization](../08_database_performance/01_query_optimization_techniques.md)
- [OpenSearch and Elasticsearch](../12_database_engines/12_elasticsearch_and_opensearch.md)
