TODO:

- smaller table first when JOIN
  
## Query Optimization Techniques

Query optimization is a fundamental aspect of database management that focuses on improving the efficiency of SQL queries. By selecting the most effective execution strategies, query optimization reduces resource consumption and accelerates response times. This enhances the overall performance of database systems and provides a better experience for users and applications relying on the data.

After reading the material, you should be able to answer the following questions:

1. What is query optimization, and why is it essential for improving the efficiency and performance of SQL queries in a database system?
2. What are the various query optimization techniques, such as indexing, query rewriting, join optimization, partitioning, materialized views, caching, and maintaining statistics, and how does each technique contribute to enhancing query performance?
3. How do indexes improve query performance, and what are the best practices for selecting which columns to index and creating effective indexes in SQL?
4. How can tools like the EXPLAIN command be used to analyze and optimize SQL queries, and what insights can they provide into query execution plans?
5. What are the best practices for query optimization, including balancing read and write operations, avoiding excessive indexing, rewriting complex queries, and regularly reviewing and maintaining query performance?

### Overview

There are several techniques that can be used to optimize SQL queries. Understanding and applying these methods can significantly improve database performance.

#### Indexing

Indexes are data structures that allow databases to find and retrieve specific rows much faster than scanning the entire table. They function similarly to an index in a book, where you can quickly locate information without reading every page.

##### How Indexes Improve Query Performance

Consider a table with millions of records. Without an index, a query searching for a specific value would need to examine each row one by one. An index allows the database to jump directly to the rows that match the query conditions.

##### Creating an Index Example

```sql
CREATE INDEX idx_customers_lastname ON customers(last_name);
```

This command creates an index on the `last_name` column of the `customers` table. Queries that filter or sort by `last_name` will now perform more efficiently.

**Example Output**

After creating the index, running `EXPLAIN` on a query that uses `last_name` shows that the database uses the index:

```sql
EXPLAIN SELECT * FROM customers WHERE last_name = 'Smith';
```

Example output:

```
Index Scan using idx_customers_lastname on customers  (cost=0.29..8.31 rows=1 width=83)
```

- **Index Scan** indicates that the index is being used.
- **cost=0.29..8.31** shows the estimated cost range for the operation.
- **rows=1** estimates that one row matches the condition.

#### Query Rewriting

Rewriting queries can make them more efficient without altering their results. This involves restructuring the SQL statements to enable the optimizer to generate better execution plans.

##### Simplifying Complex Queries

Breaking down complex queries into simpler components can help the optimizer. For example, replacing subqueries with joins can improve performance.

##### Rewriting Example

Inefficient query:

```sql
SELECT * FROM orders WHERE customer_id IN (SELECT customer_id FROM customers WHERE city = 'London');
```

Optimized query:

```sql
SELECT orders.* FROM orders JOIN customers ON orders.customer_id = customers.customer_id WHERE customers.city = 'London';
```

By using a join instead of a subquery, the database can more efficiently combine the data.

#### Join Optimization

Joins are common in SQL queries but can be resource-intensive. Optimizing joins can have a substantial impact on performance.

##### Choosing the Right Join Type

Different join types (INNER, LEFT, RIGHT, FULL) serve different purposes. Selecting the appropriate type ensures that only the necessary data is processed.

##### Example of Join Order Impact

Suppose you have two tables, `large_table` and `small_table`. Joining `small_table` to `large_table` can be more efficient than the reverse.

Optimized join:

```sql
SELECT lt.*, st.info FROM small_table st JOIN large_table lt ON st.id = lt.st_id;
```

#### Using EXPLAIN to Analyze Queries

Most databases provide an `EXPLAIN` command that shows how a query will be executed. This tool is invaluable for understanding and optimizing query performance.

```sql
EXPLAIN SELECT * FROM customers WHERE last_name = 'Smith';
```

Example output:

```
Seq Scan on customers  (cost=0.00..12.00 rows=1 width=83)
  Filter: (last_name = 'Smith')
```

- **Seq Scan** indicates a sequential scan, meaning the database is reading the entire table.
- Adding an index on `last_name` would change this to an **Index Scan**, improving performance.

#### Partitioning

Partitioning divides a large table into smaller, more manageable pieces. This can improve query performance by allowing the database to scan only relevant partitions.

##### Partitioning Example

Partitioning a table by date:

```sql
CREATE TABLE orders_2021 PARTITION OF orders FOR VALUES FROM ('2021-01-01') TO ('2022-01-01');
```

Queries that filter by date can now target the specific partition, reducing the amount of data scanned.

#### Materialized Views

Materialized views store the result of a query physically, allowing for faster access to complex or resource-intensive computations.

##### Creating a Materialized View Example

```sql
CREATE MATERIALIZED VIEW sales_summary AS
SELECT product_id, SUM(quantity) AS total_quantity FROM sales GROUP BY product_id;
```

This materialized view precomputes total quantities sold per product, speeding up queries that need this information.

##### Refreshing the Materialized View

To update the materialized view with the latest data:

```sql
REFRESH MATERIALIZED VIEW sales_summary;
```

#### Caching

Caching frequently accessed data can significantly reduce query response times. This can be done at various levels, from database caching mechanisms to application-level caching.

##### Application-Level Caching Example

Using Redis in a Python application:

```python
import redis
cache = redis.Redis(host='localhost', port=6379)

def get_product_details(product_id):
    cache_key = f'product:{product_id}'
    product = cache.get(cache_key)
    if product:
        return product  # Data retrieved from cache
    else:
        product = fetch_product_from_db(product_id)
        cache.set(cache_key, product, ex=3600)  # Cache expires in 1 hour
        return product
```

By caching the product details, subsequent requests for the same product are served quickly without querying the database.

#### Statistics and Histograms

Databases rely on statistics about the data to make optimization decisions. Keeping these statistics up-to-date helps the optimizer choose the best execution plans.

##### Updating Statistics Example

In PostgreSQL:

```sql
ANALYZE customers;
```

This command updates the statistics for the `customers` table.

##### Verifying Updated Statistics

```sql
SELECT attname, n_distinct, most_common_vals FROM pg_stats WHERE tablename = 'customers';
```

This query shows statistics like the number of distinct values and most common values for each column, which the optimizer uses.

### Practical Examples

Let's explore a practical scenario to see how these techniques come together.

**Optimizing a Slow Query**

Suppose we have a query that retrieves orders placed by customers in a specific city:

```sql
SELECT orders.* FROM orders JOIN customers ON orders.customer_id = customers.customer_id WHERE customers.city = 'New York';
```

**Initial Execution Plan**

```sql
EXPLAIN SELECT orders.* FROM orders JOIN customers ON orders.customer_id = customers.customer_id WHERE customers.city = 'New York';
```

Example output:

```
Nested Loop  (cost=0.00..5000.00 rows=100 width=...)
  -> Seq Scan on customers  (cost=0.00..1000.00 rows=50 width=...)
        Filter: (city = 'New York')
  -> Seq Scan on orders  (cost=0.00..80.00 rows=1 width=...)
        Filter: (customer_id = customers.customer_id)
```

- **Seq Scan on customers** indicates a full table scan.
- **Nested Loop** shows that for each customer in New York, the database scans the `orders` table.

##### Optimizing with Indexes

Creating indexes on the `city` and `customer_id` columns:

```sql
CREATE INDEX idx_customers_city ON customers(city);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
```

**Optimized Execution Plan**

After creating the indexes, running `EXPLAIN` again:

```sql
EXPLAIN SELECT orders.* FROM orders JOIN customers ON orders.customer_id = customers.customer_id WHERE customers.city = 'New York';
```

Example output:

```
Hash Join  (cost=... rows=100 width=...)
  -> Index Scan on customers  (cost=... rows=50 width=...)
        Index Cond: (city = 'New York')
  -> Index Scan on orders  (cost=... rows=1 width=...)
        Index Cond: (customer_id = customers.customer_id)
```

- **Index Scan** on `customers` uses the `idx_customers_city` index.
- **Index Scan** on `orders` uses the `idx_orders_customer_id` index.
- **Hash Join** is more efficient for joining large datasets.

We can illustrate the optimized query execution in the following way:

```
[Customers Index Scan] --> [Hash Table of Customer IDs]
                                   |
                                   V
                         [Hash Join on Customer ID]
                                   |
                                   V
                    [Orders Index Scan using Customer ID]
                                   |
                                   V
                             [Result Set]
```

### Best Practices for Query Optimization

- Regularly check the execution time and resource usage of your queries.
- Analyze query execution plans to identify bottlenecks.
- Ensure that database statistics are current for accurate optimization.
- Create indexes on columns that are frequently used in WHERE clauses, joins, and sorting operations.
- Too many indexes can slow down write operations and increase storage requirements.
- Rewrite complex queries to be more efficient and easier for the optimizer to handle.
- Always test query optimizations in a development environment before deploying to production.

