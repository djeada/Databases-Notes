# Indexing Strategies: Design for a Specific Query

An **index** is an additional structure that helps the database find selected rows. It is comparable to a book's index: look up a topic, find its location, and then read the relevant pages. The database still has to retrieve and return the answer.

Assume you know tables and basic `SELECT` queries. The [SQL introduction](../03_sql/01_intro_to_sql.md) provides that starting point.

## Begin with the question the application asks

A customer opens an order-history page. The query looks for that customer's recent orders:

```sql
SELECT order_id, order_date
FROM orders
WHERE customer_id = 1
ORDER BY order_date, order_id;
```

Without a suitable index, the engine may examine the orders table to find matching rows. With millions of orders and only a few belonging to this customer, avoiding that work can matter. With three rows, a scan may be simpler and faster.

The **optimizer** is the part of the DBMS that chooses an execution strategy. Declaring an index makes another strategy possible; it does not force the engine to use it.

## Start with one useful index

For customer lookup:

```sql
CREATE INDEX idx_orders_customer ON orders (customer_id);
```

The index organizes entries by customer ID and lets the engine locate that customer's orders. It may still need to sort the matching rows by date.

For customer lookup with the requested order, consider:

```sql
CREATE INDEX idx_orders_customer_date
ON orders (customer_id, order_date, order_id);
```

This is a **composite index**: one index containing several columns, ordered by customer first, date within that customer, and order ID within that date. Choose this alternative when it fits the workload; do not keep both examples automatically.

## Column order changes the access path

Imagine an address book sorted first by country and then by surname. It is easy to find Smiths within one country, but all Smiths across countries are scattered.

Similarly, `(customer_id, order_date)` and `(order_date, customer_id)` are different indexes. The first fits one customer's date range; the second may fit all orders in a date range. Engine-specific optimizations can help with other patterns, but the order is still a design decision.

## Match the amount of data requested

A query returning one email match may benefit greatly from an index. A query returning almost every customer may benefit little: it still needs to retrieve almost every row.

**Selectivity** describes how much a condition narrows the data. Look at how many rows the actual predicate matches rather than assuming a column is useful because it has an index. A boolean status may still be valuable in a partial index for a rare status.

## Other index choices, after the basics

| Choice | What it does | Question to ask |
| --- | --- | --- |
| Unique index or constraint | Prevents duplicate key values. | Is uniqueness a business rule or only a search need? |
| Covering index | Contains the values needed by a particular query. | Does avoiding extra table access justify the larger index? |
| Partial or filtered index | Indexes a subset of rows when supported. | Can the engine establish that the query needs only that subset? |
| Expression index | Indexes a calculation such as a lowercased email. | Does the query use the corresponding expression? |

These are engine-dependent options. The basic point is to match the access path to the repeated query, not to accumulate every available index type.

## Every extra index has a write cost

When an order is inserted, the database may need to insert its index entries too. Updating an indexed customer or date can require index maintenance. More indexes use more storage and memory and can increase write work.

A primary or unique constraint may already have a supporting index. Check the existing definitions before adding another identical one. A foreign-key declaration does not universally create an index on the referencing columns.

## Verify with a plan and a representative workload

An **execution plan** shows how a query will or did access data. Use the chosen engine's plan tools to check rows examined, sorting, estimates, and elapsed time. Some analysis commands execute the query, so understand the tool before applying it to a write.

Compare the read improvement with insertion and update costs. Test customers with a few orders and customers with many; one convenient test value can hide a different workload.

## Check your understanding

1. Why might a scan be reasonable for the three-row introductory example?
2. How is an index on `(customer_id, order_date)` different from the reverse order?
3. Why would an index help one email lookup more than a query returning every customer?
4. What work does an extra index add to an order insert?

[Database Indexing](../05_storage_and_indexing/05_indexing.md) explains the storage structures and engine-specific maintenance. Continue with [data integrity](05_data_integrity.md) to separate finding data quickly from enforcing its rules.
