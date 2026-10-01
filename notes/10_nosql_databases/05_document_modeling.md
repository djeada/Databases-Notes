# Document Modeling: Embedding, References, and Schema Evolution

A document database stores records as documents rather than normalized rows spread
across many tables. The main modeling question is not "can this be JSON?" but:

> Which data is read, written, and versioned together?

A good document boundary follows application operations.

## A bookstore example

A product document might look like:

```json
{
  "_id": "book-101",
  "title": "Database Systems",
  "price_cents": 4990,
  "publisher": {
    "name": "Example Press",
    "country": "DE"
  },
  "tags": ["database", "systems"],
  "dimensions": {
    "pages": 720,
    "format": "hardcover"
  }
}
```

The document groups fields that are commonly loaded together.

A relational representation might use several tables:

```text
products
publishers
product_tags
product_dimensions
```

A document representation can retrieve one product without a join.

That is useful only if the embedded data has compatible ownership and update
semantics.

## Document boundary

Think of one document as an aggregate boundary:

```text
product
├── identity
├── descriptive fields
├── dimensions
├── tags
└── embedded publisher snapshot?
```

Ask:

1. Is the nested data owned by the parent?
2. Is it usually read with the parent?
3. Does it change at roughly the same time?
4. Can it grow without bound?
5. Does another part of the system need independent access to it?

These questions decide whether to embed or reference.

## Embedding

Embedding stores related data inside the parent document.

Example:

```json
{
  "_id": "order-1001",
  "customer_id": "customer-42",
  "placed_at": "2026-10-01T12:00:00Z",
  "items": [
    {
      "product_id": "book-101",
      "title_at_purchase": "Database Systems",
      "unit_price_cents": 4990,
      "quantity": 1
    },
    {
      "product_id": "book-205",
      "title_at_purchase": "Distributed Data",
      "unit_price_cents": 3500,
      "quantity": 2
    }
  ]
}
```

The line items belong to the order.

The order is normally read as one unit.

Embedding is a natural fit.

## Why historical snapshots are different from duplication bugs

The order stores:

```text
title_at_purchase
unit_price_cents
```

even though the current product record already has a title and price.

That duplication is intentional because the values represent historical facts.

If the product price changes tomorrow, yesterday's order should not change.

```text
current product price
        │
        ├── may change
        │
order purchase price
        └── historical fact
```

Document duplication is not automatically denormalization debt.

The meaning of the copied field matters.

## Reference instead of embed

Suppose the same publisher record is used by 100,000 books and its legal name
changes.

Embedding the current publisher name in every product creates a large fan-out
update.

A reference may be better:

```json
{
  "_id": "book-101",
  "title": "Database Systems",
  "publisher_id": "publisher-7"
}
```

Separate document:

```json
{
  "_id": "publisher-7",
  "name": "Example Press GmbH",
  "country": "DE"
}
```

Now the publisher can change independently.

## Embed or reference decision

A useful decision table:

| Question | Embed tends to fit | Reference tends to fit |
| --- | --- | --- |
| Read together? | usually | not always |
| Updated together? | usually | independently |
| Child has independent identity? | weak/no | strong |
| Child shared by many parents? | rarely | often |
| Child collection grows without bound? | no | possibly |
| Need independent queries? | rarely | often |

This is not a law. It is a way to reason about the access pattern.

## One-to-few

Embedding works especially well for bounded "one-to-few" relationships.

Example:

```text
customer
└── shipping_addresses
    ├── home
    └── office
```

The address count is naturally small.

## One-to-many with a bound

A product may embed:

```text
last 10 reviews
```

while all reviews live separately.

This hybrid design can optimize a common read:

```text
product page
  └── needs recent reviews immediately
```

The full review archive remains independently queryable.

## Unbounded arrays are dangerous

Bad model:

```json
{
  "_id": "customer-42",
  "events": [
    "... millions more over years ..."
  ]
}
```

Problems include:

- document growth,
- expensive rewrites,
- large network payloads,
- update contention,
- product-specific document-size limits.

Instead, use independent event documents or buckets.

## Bucket pattern

Group time-series/event records into bounded buckets.

Example key:

```text
customer-42 / 2026-10
```

Document:

```json
{
  "_id": "customer-42:2026-10",
  "customer_id": "customer-42",
  "month": "2026-10",
  "events": [
    {"ts": "...", "type": "login"},
    {"ts": "...", "type": "purchase"}
  ]
}
```

Now each bucket has a planned upper size.

## Atomic document updates

Document databases often provide atomicity at the document level.

That makes document boundary a correctness decision.

Suppose an inventory document stores:

```json
{
  "_id": "sku-101",
  "available": 7,
  "reserved": 3
}
```

Updating both fields in one document can preserve an invariant more simply than
coordinating several independent records.

But do not assume every product/database offers the same transaction scope.
Check the exact engine.

## Multi-document transactions

Modern document databases may support multi-document transactions.

That does not make document design irrelevant.

A transaction spanning many documents can still increase:

- coordination,
- lock/transaction duration,
- failure handling,
- latency.

Prefer natural aggregate boundaries first.

Use multi-document transactions when the business rule genuinely spans them.

## Denormalization

Document models often duplicate derived/read-optimized data.

Example:

```text
orders
  ├── customer_id
  └── customer_display_name_snapshot
```

Possible strategies:

### Historical snapshot

Value is intentionally frozen.

No propagation required.

### Current projection

Value should track another source.

Requires update propagation.

### Rebuildable derived view

Value can be regenerated from source data.

The strategy must be explicit.

## Source of truth

When values appear in several places, define an authority.

Example:

```text
customers.name = authoritative current display name

orders.customer_name_at_purchase
    = immutable historical snapshot

search_index.customer_name
    = rebuildable projection
```

Without this distinction, teams cannot tell which copy should win after a conflict.

## Schema flexibility does not mean no schema

Documents still have expectations.

Example:

```text
orders
├── _id
├── customer_id
├── placed_at
└── items[]
    ├── product_id
    ├── quantity
    └── unit_price_cents
```

Applications, indexes, validators, and analytics all depend on these fields.

The schema may be:

- application-enforced,
- database-validated,
- versioned,
- partly optional.

It still exists.

## Validation

MongoDB, for example, can apply collection validation rules.

A simplified validation shape:

```javascript
{
  $jsonSchema: {
    bsonType: "object",
    required: ["customer_id", "placed_at", "items"]
  }
}
```

Validation reduces accidental malformed documents.

It does not replace business validation.

## Missing versus null

Document systems often distinguish:

```text
field missing
```

from:

```json
{"field": null}
```

These may mean different things.

For example:

```text
middle_name missing -> not collected
middle_name null    -> explicitly no value
```

The repository already contains a MongoDB demonstration:

[`scripts/mongo/null_vs_missing_fields.py`](../../scripts/mongo/null_vs_missing_fields.py)

Use it to inspect how those cases behave in queries.

## Replacement versus partial update

Document databases often support both:

- replacing the whole document,
- updating selected fields.

Those operations have different risks.

Repository demo:

[`scripts/mongo/replace_one_vs_update_one.py`](../../scripts/mongo/replace_one_vs_update_one.py)

A replacement can accidentally remove fields the caller did not include.

A partial update can preserve unrelated fields.

Choose based on ownership semantics.

## Schema evolution

Suppose version 1 stores:

```json
{
  "name": "Alice"
}
```

Version 2 wants:

```json
{
  "first_name": "Alice",
  "last_name": null
}
```

A rolling migration may temporarily need to read both shapes.

```text
old app -> old shape
new app -> understands old + new
migration -> rewrites records
new app -> writes new only
cleanup -> remove old compatibility
```

This is an expand-and-contract pattern.

## Version field

Some systems include an explicit schema version:

```json
{
  "_id": "customer-42",
  "schema_version": 3,
  ...
}
```

This can help application migration logic.

Do not add version fields mechanically. Use them when records genuinely need
version-dependent interpretation.

## Lazy migration

Instead of rewriting every document at deployment time, the application can
upgrade a document when it is read or changed.

Advantages:

- lower migration burst,
- easier gradual rollout.

Risks:

- old shapes persist for a long time,
- reads become more complex,
- rare records may never migrate.

## Eager migration

Rewrite all matching documents in a controlled job.

Advantages:

- consistent final state,
- simpler application after completion.

Risks:

- high write volume,
- large replication load,
- long-running backfill,
- rollback complexity.

Measure on production-scale data.

## Indexes follow access patterns

Suppose the application loads:

```text
all open orders for customer 42
ordered newest first
```

The index should reflect the filter/sort pattern.

In MongoDB-style notation:

```javascript
{ customer_id: 1, status: 1, placed_at: -1 }
```

Do not create indexes just because fields exist.

Each index costs:

- disk,
- memory,
- write amplification.

## Array indexes

An array field can create multiple index entries per document.

Example:

```json
{
  "tags": ["database", "distributed", "sql"]
}
```

Indexing `tags` supports membership queries.

But large arrays increase index size and write cost.

## Compound index order

Index field order matters.

A typical reasoning sequence is:

1. equality filters,
2. range filters,
3. sort requirements.

Always verify with the engine's query planner rather than applying a formula blindly.

## Projection

Return only needed fields.

Instead of fetching a full product document containing:

- large description,
- images metadata,
- supplier history,
- reviews,

a listing page may need only:

```text
_id
title
price
thumbnail
```

Projection reduces network and deserialization work.

## Pagination

Offset pagination can become expensive for deep pages.

Keyset-style pagination can use a stable sort key:

```text
placed_at DESC, _id DESC
```

Then request records after the last seen pair.

The exact syntax depends on the database.

## Duplicate data and write amplification

Suppose product title appears in:

- product document,
- open cart items,
- search index,
- recommendation projection.

Changing the title may require several updates.

A document design should list all derived copies and define:

- update mechanism,
- tolerated staleness,
- rebuild procedure.

## Event-driven propagation

One pattern:

```text
product update
    │
    ▼
database commit
    │
    ▼
event / CDC
    │
    ├──► search projection
    └──► recommendation projection
```

Derived copies become eventually consistent.

That may be acceptable for search but not for payment totals.

## Optimistic concurrency

A version field can detect lost updates.

Document:

```json
{
  "_id": "product-101",
  "version": 7,
  "price_cents": 4990
}
```

Update condition:

```text
_id = product-101
AND version = 7
```

Update:

```text
price = 5190
version = 8
```

If zero documents match, another writer changed the record first.

## Idempotent writes

Retries happen in distributed systems.

A create operation can include a business idempotency key:

```text
checkout_request_id = 6f...
```

The database/application can reject duplicate processing.

Do not rely on "the client only sends once."

## Sharding implications

Document key design matters when the database is sharded.

A shard key affects:

- distribution,
- query routing,
- hotspots,
- resharding complexity.

Bad keys can concentrate writes.

Example:

```text
created_at increasing forever
```

may route all newest writes to one range/shard depending on the engine.

Choose from actual workload and engine behavior.

## Document modeling workflow

For each feature:

1. List the exact reads.
2. List the exact writes.
3. Identify data that changes together.
4. Identify unbounded relationships.
5. Mark historical snapshots versus current projections.
6. Decide embed versus reference.
7. Define validation.
8. Design required indexes.
9. Define schema-evolution strategy.
10. Test concurrency and retry behavior.
11. Estimate maximum document size/growth.
12. Check sharding implications if distributed.

## Common mistakes

### "Documents remove joins, so embed everything"

Unbounded/shared data becomes painful.

### "Schema-less means migration-less"

Applications still depend on structure.

### Current values copied as if they were historical

Updates become inconsistent.

### Unbounded arrays

Documents grow indefinitely.

### Whole-document replacement from partial input

Fields disappear unexpectedly.

### Index every field

Write and memory cost grows.

### No source-of-truth definition

Conflicting copies cannot be reconciled.

## When a relational model may be simpler

Prefer a relational design when:

- many entities change independently,
- joins are central,
- constraints across records matter,
- ad-hoc query patterns evolve frequently,
- transactional rules span several entities.

A document database is not a default replacement for normalized relational
models.

## Related notes

- [NoSQL introduction](01_nosql_databases_intro.md)
- [Types of NoSQL databases](02_types_of_nosql_databases.md)
- [Querying NoSQL databases](03_querying_nosql_databases.md)
- [CRUD in SQL vs NoSQL](04_crud_in_sql_vs_nosql.md)
- [MongoDB engine note](../12_database_engines/04_mongodb.md)
- [Consistency, transactions, and replication](09_consistency_transactions_and_replication.md)
