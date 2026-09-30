# OpenSearch and Elasticsearch

OpenSearch and Elasticsearch are search-oriented distributed data engines built around Apache Lucene concepts such as inverted indexes, analyzers, mappings, shards, and replicas.

They are commonly used for:

- full-text search,
- log and observability search,
- product/catalog search,
- application search,
- faceted navigation,
- security analytics,
- document retrieval.

They are not general replacements for a relational database. Their biggest strength is searching and ranking documents by text and structured fields.

This note uses OpenSearch for runnable local examples because it provides a straightforward Docker quickstart.

Official documentation:

- [OpenSearch installation quickstart](https://docs.opensearch.org/latest/quickstart/)
- [OpenSearch Query DSL](https://docs.opensearch.org/latest/query-dsl/)
- [OpenSearch index settings](https://docs.opensearch.org/latest/install-and-configure/configuring-opensearch/index-settings/)

## Search-engine mental model

A relational database often answers:

```sql
SELECT *
FROM products
WHERE sku = 'BK-1001';
```

A search engine is designed for questions such as:

> Find products whose title and description are relevant to "distributed database", rank the best matches first, filter to books, and return category facets.

Conceptually:

```text
documents
   │
   ▼
analysis/tokenization
   │
   ▼
inverted index
   │
   ▼
query terms
   │
   ▼
matching postings
   │
   ▼
ranking + filters
   │
   ▼
search results
```

## Inverted index

Suppose three documents contain:

```text
doc 1: "database systems"
doc 2: "distributed database"
doc 3: "distributed systems"
```

An inverted index looks conceptually like:

```text
database    -> doc 1, doc 2
distributed -> doc 2, doc 3
systems     -> doc 1, doc 3
```

Instead of scanning every document for every search, the engine can jump to documents containing each term.

Real indexes also store positions, frequencies, statistics, and other metadata used for ranking.

## Index and document

A logical OpenSearch index contains documents.

```text
index: products

document 1
{
  "sku": "BK-1001",
  "title": "Database Systems",
  "category": "books",
  "price": 49.90
}

document 2
{
  "sku": "BK-1002",
  "title": "Distributed Data",
  "category": "books",
  "price": 59.00
}
```

Documents are JSON.

Fields have mappings that define how values are indexed and searched.

## Local setup

The repository includes:

[`scripts/opensearch/docker-compose.yml`](../../scripts/opensearch/docker-compose.yml)

Start it:

```bash
cd scripts/opensearch
docker compose up -d
docker compose ps
```

This local setup disables the security plugin to make the examples simple.

That is **development-only**.

Verify:

```bash
curl http://localhost:9200
```

Stop:

```bash
docker compose down
```

OpenSearch's official Docker quickstart also documents single-node development mode and explicitly warns against exposing an unsecured development configuration publicly.

## Runnable demo

The repository includes:

[`scripts/opensearch/demo.sh`](../../scripts/opensearch/demo.sh)

Run after the container is healthy:

```bash
bash demo.sh
```

The script:

1. creates a product index with explicit mappings,
2. indexes sample documents,
3. refreshes the index,
4. performs a full-text query,
5. performs a filtered aggregation.

## Mappings

Mappings define field behavior.

Example:

```json
{
  "mappings": {
    "properties": {
      "sku": {
        "type": "keyword"
      },
      "title": {
        "type": "text"
      },
      "category": {
        "type": "keyword"
      },
      "price": {
        "type": "double"
      }
    }
  }
}
```

The distinction between `text` and `keyword` is fundamental.

### text

Analyzed for full-text search.

Example:

```text
"Distributed Database Systems"
```

may be tokenized into terms similar to:

```text
distributed
database
systems
```

### keyword

Indexed as one exact value.

Good for:

- IDs,
- categories,
- status values,
- tags,
- exact sorting,
- aggregations.

Do not use analyzed `text` fields when exact grouping/filtering is required.

## Multi-fields

A field can be indexed in more than one way.

Example:

```json
"title": {
  "type": "text",
  "fields": {
    "raw": {
      "type": "keyword"
    }
  }
}
```

Then:

- `title` supports full-text search,
- `title.raw` supports exact sorting/aggregation.

This pattern is common for names, titles, and labels.

## Analysis pipeline

Text normally passes through an analyzer:

```text
original text
     │
     ▼
character filters
     │
     ▼
tokenizer
     │
     ▼
token filters
     │
     ▼
indexed terms
```

For example:

```text
"The Databases"
      │
lowercase
      ▼
"the databases"
      │
tokenize
      ▼
["the", "databases"]
```

Depending on the analyzer, stop words or stemming can further transform terms.

The same analysis behavior must be understood at index time and query time.

## Full-text query

OpenSearch Query DSL uses JSON.

Example:

```json
{
  "query": {
    "match": {
      "title": "distributed database"
    }
  }
}
```

Request:

```bash
curl -X POST   "http://localhost:9200/products/_search"   -H "Content-Type: application/json"   -d '{
    "query": {
      "match": {
        "title": "distributed database"
      }
    }
  }'
```

The `match` query analyzes the search text and computes relevance.

## Exact filter

Exact structured filters should not usually affect relevance scoring.

```json
{
  "query": {
    "bool": {
      "must": [
        {
          "match": {
            "title": "database"
          }
        }
      ],
      "filter": [
        {
          "term": {
            "category": "books"
          }
        }
      ]
    }
  }
}
```

This separates:

```text
must   -> relevance
filter -> boolean restriction
```

## Relevance

Search results normally have a score.

The engine considers term statistics and query structure.

Example result order:

```text
score  document
-----  ---------------------------
4.8    Distributed Databases
3.2    Database Systems Handbook
1.1    Systems Architecture
```

Ranking quality is a product requirement.

A technically fast search system can still be poor if relevance does not match user expectations.

## Aggregations

Search engines can also aggregate structured fields.

Example category counts:

```json
{
  "size": 0,
  "aggs": {
    "categories": {
      "terms": {
        "field": "category"
      }
    }
  }
}
```

This powers faceted navigation such as:

```text
Books (120)
Courses (34)
Videos (18)
```

High-cardinality aggregations can be expensive, so model fields intentionally.

## Shards

An index is split into primary shards.

```text
index: products

          ┌── primary shard 0
products ─┼── primary shard 1
          └── primary shard 2
```

Each shard is effectively a Lucene index.

Sharding allows data and query work to be distributed across nodes.

Too many shards create overhead.

Too few can limit scale.

Shard count is an architectural decision, not a tuning value to increase blindly.

## Replicas

Replica shards copy primary shards.

```text
primary shard 0
     │
     └──► replica shard 0
```

Replicas can:

- improve availability,
- increase search capacity,
- provide another copy after node failure.

A replica should be placed on a different node from its primary to provide real fault tolerance.

A single-node development cluster often has zero replicas to avoid a permanently yellow health state.

## Cluster topology

Simplified:

```text
client
  │
  ▼
node A
  │
  ├── shard P0
  ├── shard R1
  │
  └──── coordinates query ────┐
                              │
             ┌────────────────┴──────────────┐
             ▼                               ▼
          node B                          node C
          shard P1                        shard P2
          shard R2                        shard R0
```

A search may fan out to multiple shards and merge results.

This is why shard count affects query overhead.

## Refresh and near-real-time search

After indexing a document, it may not immediately appear in normal search until a refresh makes the new segment searchable.

Conceptually:

```text
index request
     │
     ▼
write buffers
     │
     ▼
refresh
     │
     ▼
searchable segment
```

Search engines are often described as **near real time**, not "every write is instantly visible to every search."

For tests, a forced refresh is convenient.

In production, forcing refresh after every document harms indexing throughput.

## Bulk indexing

Index documents in batches.

Instead of:

```text
HTTP request per document
HTTP request per document
HTTP request per document
...
```

use the bulk API.

This reduces request overhead and improves indexing throughput.

Batch size should be measured; extremely large batches can create memory and latency problems.

## Updates

Search-engine documents are not updated like fixed pages in a relational heap.

A document update conceptually produces a new indexed representation and invalidates the old one.

High-frequency tiny updates can create significant indexing/merge work.

Search engines perform best when the workload is understood as indexing documents rather than in-place row mutation.

## Segment merging

Lucene writes immutable segments.

Over time:

```text
segment A ─┐
segment B ─┼──► merged segment
segment C ─┘
```

Merging consumes:

- CPU,
- disk I/O,
- temporary disk space.

Heavy indexing plus heavy search requires resource planning for both foreground and background work.

## Search engine as a secondary index

A common architecture:

```text
PostgreSQL
    │
    │ CDC / application events
    ▼
Kafka / connector
    │
    ▼
OpenSearch
    │
    ▼
search API
```

PostgreSQL remains the transactional source of truth.

OpenSearch contains a search-optimized projection.

Benefits:

- relational constraints remain in the primary DB,
- search mappings can evolve independently,
- search can be rebuilt from durable source data.

This architecture requires synchronization and handles eventual consistency.

## Search synchronization

Suppose an order changes in PostgreSQL.

The search index may update milliseconds or seconds later.

```text
database commit
    │
    ▼
event / CDC
    │
    ▼
search indexing
    │
    ▼
new search result
```

Applications must decide whether temporary divergence is acceptable.

For strict transactional reads, query the primary database.

## OpenSearch versus Elasticsearch

OpenSearch and Elasticsearch are separate projects with shared historical Lucene-based roots.

They overlap heavily in concepts:

- indexes,
- documents,
- mappings,
- shards,
- replicas,
- full-text queries,
- aggregations.

However:

- features evolve independently,
- APIs/plugins can differ,
- operational tooling differs,
- managed-service support differs.

Do not assume every Elasticsearch plugin or API works identically in OpenSearch, or vice versa.

Use the documentation for the exact engine and version you deploy.

## Search engine versus PostgreSQL full-text search

PostgreSQL can handle substantial search needs with:

- `tsvector`,
- `tsquery`,
- GIN indexes,
- trigram indexes.

Start with PostgreSQL search when:

- search is moderate,
- data is already relational,
- keeping one system is valuable,
- relevance requirements are simple.

Use a dedicated search engine when:

- relevance tuning is central,
- faceting/autocomplete/search features are complex,
- search traffic is independently large,
- log/document indexing is dominant.

Avoid introducing a distributed search cluster before the workload requires it.

## Search engine versus ClickHouse

OpenSearch is optimized for document/text search and relevance.

ClickHouse is optimized for columnar analytical scans and aggregations.

For observability:

```text
Need free-text log search and document search?
    -> OpenSearch

Need massive aggregations over structured logs/metrics?
    -> ClickHouse can be attractive

Need both?
    -> architecture depends on query patterns
```

Do not select by the generic word "logs."

List the actual queries.

## Security

Production search clusters should use:

- TLS,
- authentication,
- role-based access,
- private networks,
- index-level permissions where required,
- audit logging,
- controlled snapshot repositories.

Never expose a development cluster with security disabled to the public internet.

## Snapshots

Use snapshot repositories for backup and recovery.

Replica shards are not backups.

A bad delete can affect both primary and replica shards.

Test restore procedures.

## Monitoring

Important metrics include:

- cluster health,
- unassigned shards,
- JVM heap,
- indexing rate,
- search latency,
- rejected thread-pool operations,
- disk watermarks,
- segment count,
- merge activity,
- query cache behavior,
- snapshot success.

Search clusters are sensitive to memory and disk pressure.

## Common mistakes

### Dynamic mappings without governance

Unexpected fields and wrong inferred types can pollute an index.

### Too many shards

Every shard has memory and coordination cost.

### One giant shard

Recovery and scaling become difficult.

### Using analyzed text for exact aggregation

Use `keyword`-style fields.

### Forcing refresh after every write

This reduces indexing throughput.

### Treating search as transactional truth

Search indexes are often derived and eventually consistent.

### No rebuild strategy

A derived search index should be reproducible from source data.

## Practical checklist

Before introducing OpenSearch/Elasticsearch:

1. What exact search features are required?
2. Can the primary database already satisfy them?
3. Which fields are `text` and which are exact `keyword`?
4. How many documents and how large are they?
5. What indexing rate is expected?
6. What search concurrency is expected?
7. How many shards are needed initially?
8. How will source data synchronize?
9. Can the index be rebuilt?
10. What is the snapshot/restore plan?

## Related notes

- [Redis](10_redis.md)
- [ClickHouse](13_clickhouse.md)
- [Choosing a database](07_choosing_database.md)
- [Data pipelines](../13_big_data/06_data_pipelines_orchestration_and_quality.md)
- [Indexing](../05_storage_and_indexing/05_indexing.md)
