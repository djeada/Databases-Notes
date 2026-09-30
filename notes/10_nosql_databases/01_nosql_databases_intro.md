# NoSQL: Choose a Data Model from the Operations You Need

**NoSQL** is an umbrella label for databases built around models such as documents, key-value pairs, wide-column records, and graphs. It is not one query language or one set of guarantees. Some products support transactions, joins, validation, or SQL-like queries; others expose different operations.

Read [data models](../01_introduction_to_databases/04_data_models.md) and [transactions](../04_acid_properties_and_transactions/01_transactions_intro.md) first. We will revisit the bookstore and ask which facts are read together, which change together, and which relationships need traversal.

## Start with an access pattern

An **access pattern** describes an actual operation, not just a kind of data. Compare these requests:

| Request | Model worth examining | Why |
|---|---|---|
| Load one product with its varying descriptive attributes | Document | Related fields can be retrieved as one document |
| Retrieve a temporary shopping cart by its cart identifier | Key-value | The known key directly identifies the value |
| Read one customer's events in a date range | Wide-column | A partition and clustering order can align with this lookup |
| Traverse authors connected through collaborations | Graph | Explicit connections support relationship traversal |

These are examples to reason from, not rules that require a separate database for every feature. A relational database may support several of them well enough. Adding another system also adds deployment, backup, security, and synchronization work.

## Documents group a record's fields

A bookstore product document might be:

```json
{
  "product_id": 10,
  "title": "Database Basics",
  "price_cents": 1500,
  "attributes": {
    "pages": 240,
    "language": "en"
  }
}
```

A different product can have different attributes. That flexibility does not remove the schema: applications still expect types and required fields, and the database may enforce validation rules.

**Embedding** puts related values inside the document. **Referencing** stores an identifier pointing elsewhere. Embedding can make one read convenient, but repeated copies of shared facts need updates. If every order embeds the customer's current display name, a name change creates multiple copies to maintain. A historical billing name may intentionally remain unchanged. The same ownership question appeared in [normalization](../02_database_design/02_normalization.md).

## Key-value access begins with a known key

A cart can use the key `cart:abc123` with a value containing product identifiers and quantities. Looking it up by that key is straightforward. Finding all carts containing product 10 is a different request and may require a supported secondary index or another maintained representation.

A key-value API is not automatically a safe multi-user cart editor. If two callers read a value, change it independently, and overwrite it, one update can be lost. Check the product's atomic update, compare-and-set, transaction, and expiration features.

## Wide-column designs plan the lookup first

A wide-column database often uses a **partition key** to group related records and **clustering keys** to order records within that group. For customer events, the partition might be a customer and month, with event time as the clustering order.

That structure can suit “this customer's events this month.” It does not automatically make “all customers' events matching any attribute” efficient. Partition size, skew, and supported queries become central modeling concerns.

Wide-column storage is distinct from the [column-oriented analytical layout](../05_storage_and_indexing/02_row_based_vs_column_based_databases.md). Similar names describe different choices.

## Graphs make connections explicit

A graph stores **nodes**, such as authors, and **edges**, such as collaborations. Traversal follows those edges to answer questions about paths or neighborhoods.

This can make relationship-heavy queries natural to express. It does not mean a graph always beats a relational join: required traversal depth, selectivity, indexes, and implementation still matter. A general graph can contain cycles and many incoming relationships; it is broader than a tree.

## Compare guarantees separately from the model

Choosing documents instead of rows does not answer any of these questions:

- Is a write atomic for one record, a partition, or several records?
- Which validation and uniqueness rules are enforced?
- When will a replica read observe a recent write?
- What happens to an acknowledged write after failover?
- How are conflicts detected and retries handled?
- Which indexes support the actual queries, and what does maintaining them cost?

Likewise, NoSQL does not imply eventual consistency, and relational does not imply one machine. Model, distribution, transaction scope, and consistency settings are separate dimensions. Review [CAP](../06_distributed_databases/06_cap_theorem.md) for partition-time guarantees rather than using “choose any two” as a product-selection shortcut.

## Validate a choice with one complete workflow

For a bookstore checkout, model the product lookup, stock reservation, order creation, confirmation read, failure handling, and report requirements together. A fast individual lookup is not enough if the whole workflow cannot preserve its rules.

Use representative data and skew. Examine the difficult case as well as the happy path: concurrent edits, an unavailable node, a duplicate request, a missing reference, or a query across many partitions. Choose the model whose tradeoffs you can explain and operate.

## Check your understanding

1. Why does a flexible document still have an application schema?
2. How does loading a cart by key differ from finding all carts containing one product?
3. Why does an embedded current customer name create a different maintenance problem from a historical billing name?
4. Which guarantees remain undecided after choosing a document database?

Next: [types of NoSQL databases](02_types_of_nosql_databases.md), then [querying NoSQL](03_querying_nosql_databases.md) and [CRUD comparisons](04_crud_in_sql_vs_nosql.md).
