# Row Storage and Column Storage

A table's logical shape does not determine its physical layout. Both row-oriented and column-oriented systems can expose rows and columns to SQL. The difference is which values they keep together in storage.

Consider a small sales table:

| sale_id | customer_id | product_id | quantity | amount_cents |
|---|---|---|---|---|
| 101 | 1 | 10 | 2 | 3000 |
| 102 | 1 | 20 | 1 | 2500 |
| 103 | 2 | 20 | 2 | 5000 |

## Row storage keeps one record together

A simplified row layout is:

```text
(101, 1, 10, 2, 3000)
(102, 1, 20, 1, 2500)
(103, 2, 20, 2, 5000)
```

When the application opens sale 101, it usually needs several of that sale's fields. Keeping those values together suits this access pattern. Small inserts and updates also operate naturally on individual records, although actual costs depend on indexes, logging, and concurrency.

This pattern is common in **online transaction processing (OLTP)**: many short operations such as placing an order or changing a customer's address.

## Column storage keeps one field's values together

A simplified column layout is:

```text
sale_id:      101, 102, 103
customer_id:    1,   1,   2
product_id:    10,  20,  20
quantity:      2,   1,   2
amount_cents: 3000, 2500, 5000
```

A report asking for `SUM(amount_cents)` needs the amount column, not every customer's identifier or product field. For a much larger table, reading only the relevant columns can avoid substantial work.

Similar values stored together also often compress well. **Compression** represents data with fewer bytes; for example, repeated customer identifiers can be encoded compactly. Less data to read can improve throughput, though decoding has a cost too.

This pattern is common in **online analytical processing (OLAP)**: reports and aggregations that examine many records. Engines may process groups of column values in batches, often called **vectorized execution**.

## Compare the work, not just the label

| Request | Why row storage may suit it | Why column storage may suit it |
|---|---|---|
| Open one sale by its identifier | Related fields are stored together | Needs an efficient lookup and reconstruction across columns |
| Sum amounts across millions of sales | May scan unrelated fields too | Can read and aggregate the amount column |
| Insert one small order at a time | Fits individual-record operations | May rely on buffering before writing column segments |
| Load a large batch for reporting | Supported, but layout may read more for later scans | Bulk loading and analytical scans often fit the design |

These are tendencies, not guarantees. Indexes, partitions, memory, compression, and the engine's implementation can change the result. Hybrid engines and columnar indexes can support both access patterns.

## Do not confuse column storage with wide-column databases

A **columnar analytical engine** organizes values by column to process scans efficiently. A **wide-column database**, such as Cassandra, organizes records around partition keys and clustering keys for distributed access patterns. “Column” appears in both names, but they describe different design decisions.

Similarly, choosing row storage does not mean queries are limited to one row, and choosing column storage does not mean SQL joins are unavailable.

## Choose from a concrete workload

For the bookstore's checkout system, ask how individual orders are written and retrieved. For its annual revenue dashboard, ask which columns reports scan and how fresh the reports must be. It can be sensible to keep operational data in a transactional database and load a separate analytical store.

That separation introduces a data pipeline: a process that copies or transforms data between systems. The report may lag behind recent sales, so freshness becomes part of the requirements. [Data warehousing](../13_big_data/01_data_warehousing.md) develops this design.

## Check your understanding

1. Which values does a revenue sum actually need to read?
2. Why can storing similar values together help compression?
3. How does OLTP differ from OLAP in its typical work?
4. Why is a wide-column database not simply a columnar SQL engine?

Continue with [primary and secondary keys](03_primary_key_vs_secondary_key.md), then [database pages](04_database_pages.md).
