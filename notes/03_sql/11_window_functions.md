## Window Functions in SQL

Window functions in SQL are powerful tools that allow you to perform calculations across a set of table rows that are related to the current row. Unlike aggregate functions, window functions do not collapse rows into a single output row; instead, they retain the individual row identities while providing additional analytical capabilities. Window functions are essential for advanced data analysis, reporting, and generating insights that require comparisons or calculations across related rows.

After reading the material, you should be able to answer the following questions:

1. What are window functions in SQL, and how do they differ from aggregate functions?
2. What are some common window functions, and what are their typical use cases?
3. How does the `OVER` clause define the window for window functions, and what components can it include?
4. What are the advantages and limitations of using window functions compared to traditional methods like self-joins?
5. What best practices should be followed when implementing window functions in SQL to ensure optimal performance and maintainability?

### Common Window Functions

Here are some of the most commonly used window functions in SQL:

- **`ROW_NUMBER()`**: Assigns a unique sequential integer to rows within a partition of a result set, starting at 1 for the first row in each partition.
- **`RANK()`**: Assigns a rank to each row within a partition of a result set, with gaps in ranking values when there are ties.
- **`DENSE_RANK()`**: Similar to `RANK()`, but without gaps in ranking values when there are ties.
- **`NTILE()`**: Distributes rows into a specified number of approximately equal groups.
- **`LEAD()`**: Provides access to a subsequent row’s data without the need for a self-join.
- **`LAG()`**: Provides access to a preceding row’s data without the need for a self-join.
- **Aggregate Window Functions**: Such as `SUM()`, `AVG()`, `COUNT()`, which perform aggregate calculations over a window.

### Setting Up Example Tables

Suppose we have two tables: `Sales` and `Products`.

**Sales Table**

| SaleID | ProductID | SaleDate   | Quantity | Price |
|--------|-----------|------------|----------|-------|
| 1      | 101       | 2024-01-05 | 10       | 15.00 |
| 2      | 102       | 2024-01-07 | 5        | 25.00 |
| 3      | 101       | 2024-01-10 | 20       | 15.00 |
| 4      | 103       | 2024-01-12 | 7        | 30.00 |
| 5      | 102       | 2024-01-15 | 10       | 25.00 |
| 6      | 101       | 2024-01-20 | 15       | 15.00 |
| 7      | 103       | 2024-01-22 | 5        | 30.00 |
| 8      | 104       | 2024-01-25 | 12       | 20.00 |
| 9      | 102       | 2024-01-28 | 8        | 25.00 |
| 10     | 104       | 2024-01-30 | 10       | 20.00 |

**Products Table**

| ProductID | ProductName    | Category       |
|-----------|-----------------|----------------|
| 101       | Widget A        | Gadgets        |
| 102       | Widget B        | Gadgets        |
| 103       | Gizmo C         | Widgets        |
| 104       | Gizmo D         | Widgets        |

### Understanding the `OVER` Clause

Window functions use the `OVER` clause to define the window or the set of rows the function should operate on. The `OVER` clause can include:

- **`PARTITION BY`**: Divides the result set into partitions to which the window function is applied.
- **`ORDER BY`**: Defines the logical order of rows within each partition.
- **Window Frame Specification**: Specifies the subset of rows within the partition for frame-based calculations (e.g., `ROWS BETWEEN`).

### ROW_NUMBER Function

The `ROW_NUMBER()` function assigns a unique sequential integer to rows within a partition, starting at 1 for the first row in each partition.

#### Example: Assigning Row Numbers to Sales per Product

```sql
SELECT
    SaleID,
    ProductID,
    SaleDate,
    Quantity,
    Price,
    ROW_NUMBER() OVER (PARTITION BY ProductID ORDER BY SaleDate) AS RowNum
FROM
    Sales
ORDER BY
    ProductID,
    SaleDate;
```

**Result**

| SaleID | ProductID | SaleDate   | Quantity | Price | RowNum |
|--------|-----------|------------|----------|-------|--------|
| 1      | 101       | 2024-01-05 | 10       | 15.00 | 1      |
| 3      | 101       | 2024-01-10 | 20       | 15.00 | 2      |
| 6      | 101       | 2024-01-20 | 15       | 15.00 | 3      |
| 2      | 102       | 2024-01-07 | 5        | 25.00 | 1      |
| 5      | 102       | 2024-01-15 | 10       | 25.00 | 2      |
| 9      | 102       | 2024-01-28 | 8        | 25.00 | 3      |
| 4      | 103       | 2024-01-12 | 7        | 30.00 | 1      |
| 7      | 103       | 2024-01-22 | 5        | 30.00 | 2      |
| 8      | 104       | 2024-01-25 | 12       | 20.00 | 1      |
| 10     | 104       | 2024-01-30 | 10       | 20.00 | 2      |

- The `ROW_NUMBER()` function assigns a unique row number to each sale within its `ProductID` partition based on the `SaleDate`.
- Useful for tasks like pagination or identifying specific rows within partitions.

### RANK and DENSE_RANK Functions

Both `RANK()` and `DENSE_RANK()` assign a rank to each row within a partition. The difference lies in how they handle ties.

- **`RANK()`**: Assigns the same rank to tied rows but leaves gaps in the ranking sequence.
- **`DENSE_RANK()`**: Assigns the same rank to tied rows without leaving gaps.

#### Example: Ranking Sales by Quantity per Product

```sql
SELECT
    SaleID,
    ProductID,
    SaleDate,
    Quantity,
    Price,
    RANK() OVER (PARTITION BY ProductID ORDER BY Quantity DESC) AS Rank,
    DENSE_RANK() OVER (PARTITION BY ProductID ORDER BY Quantity DESC) AS DenseRank
FROM
    Sales
ORDER BY
    ProductID,
    Quantity DESC;
```

**Result**

| SaleID | ProductID | SaleDate   | Quantity | Price | Rank | DenseRank |
|--------|-----------|------------|----------|-------|------|-----------|
| 101    | 101       | 2024-01-10 | 20       | 15.00 | 1    | 1         |
| 6      | 101       | 2024-01-20 | 15       | 15.00 | 2    | 2         |
| 1      | 101       | 2024-01-05 | 10       | 15.00 | 3    | 3         |
| 102    | 102       | 2024-01-15 | 10       | 25.00 | 1    | 1         |
| 9      | 102       | 2024-01-28 | 8        | 25.00 | 2    | 2         |
| 2      | 102       | 2024-01-07 | 5        | 25.00 | 3    | 3         |
| 103    | 103       | 2024-01-12 | 7        | 30.00 | 1    | 1         |
| 7      | 103       | 2024-01-22 | 5        | 30.00 | 2    | 2         |
| 104    | 104       | 2024-01-25 | 12       | 20.00 | 1    | 1         |
| 10     | 104       | 2024-01-30 | 10       | 20.00 | 2    | 2         |

- **`RANK()`** and **`DENSE_RANK()`** are useful for identifying the position of rows within partitions, especially when dealing with ties.

### NTILE Function

The `NTILE()` function distributes the rows in an ordered partition into a specified number of roughly equal groups.

#### Example: Dividing Sales into Quartiles per Product

```sql
SELECT
    SaleID,
    ProductID,
    SaleDate,
    Quantity,
    Price,
    NTILE(4) OVER (PARTITION BY ProductID ORDER BY Quantity DESC) AS Quartile
FROM
    Sales
ORDER BY
    ProductID,
    Quantity DESC;
```

**Result**

| SaleID | ProductID | SaleDate   | Quantity | Price | Quartile |
|--------|-----------|------------|----------|-------|----------|
| 101    | 101       | 2024-01-10 | 20       | 15.00 | 1        |
| 6      | 101       | 2024-01-20 | 15       | 15.00 | 2        |
| 1      | 101       | 2024-01-05 | 10       | 15.00 | 3        |
| 102    | 102       | 2024-01-15 | 10       | 25.00 | 1        |
| 9      | 102       | 2024-01-28 | 8        | 25.00 | 2        |
| 2      | 102       | 2024-01-07 | 5        | 25.00 | 3        |
| 103    | 103       | 2024-01-12 | 7        | 30.00 | 1        |
| 7      | 103       | 2024-01-22 | 5        | 30.00 | 2        |
| 104    | 104       | 2024-01-25 | 12       | 20.00 | 1        |
| 10     | 104       | 2024-01-30 | 10       | 20.00 | 2        |

- The `NTILE(4)` function divides each `ProductID` partition into four quartiles based on `Quantity`.
- Useful for categorizing data into percentile-based groups.

### LEAD and LAG Functions

`LEAD()` and `LAG()` functions allow you to access subsequent and preceding rows' data without the need for self-joins.

#### Example: Comparing Current Sale with Previous Sale Quantity per Product

```sql
SELECT
    SaleID,
    ProductID,
    SaleDate,
    Quantity,
    Price,
    LAG(Quantity, 1) OVER (PARTITION BY ProductID ORDER BY SaleDate) AS PreviousQuantity,
    Quantity - LAG(Quantity, 1) OVER (PARTITION BY ProductID ORDER BY SaleDate) AS QuantityChange
FROM
    Sales
ORDER BY
    ProductID,
    SaleDate;
```

**Result**

| SaleID | ProductID | SaleDate   | Quantity | Price | PreviousQuantity | QuantityChange |
|--------|-----------|------------|----------|-------|-------------------|-----------------|
| 1      | 101       | 2024-01-05 | 10       | 15.00 | NULL              | NULL            |
| 3      | 101       | 2024-01-10 | 20       | 15.00 | 10                | 10              |
| 6      | 101       | 2024-01-20 | 15       | 15.00 | 20                | -5              |
| 2      | 102       | 2024-01-07 | 5        | 25.00 | NULL              | NULL            |
| 5      | 102       | 2024-01-15 | 10       | 25.00 | 5                 | 5               |
| 9      | 102       | 2024-01-28 | 8        | 25.00 | 10                | -2              |
| 4      | 103       | 2024-01-12 | 7        | 30.00 | NULL              | NULL            |
| 7      | 103       | 2024-01-22 | 5        | 30.00 | 7                 | -2              |
| 8      | 104       | 2024-01-25 | 12       | 20.00 | NULL              | NULL            |
| 10     | 104       | 2024-01-30 | 10       | 20.00 | 12                | -2              |

- **`LAG(Quantity, 1)`** retrieves the quantity from the previous sale within the same `ProductID` partition.
- **`LEAD()`** can similarly retrieve data from subsequent rows.
- Useful for trend analysis and calculating differences between consecutive rows.

### Aggregate Window Functions

Aggregate functions like `SUM()`, `AVG()`, and `COUNT()` can also be used as window functions to perform calculations across a window of rows.

#### Example: Calculating Running Total of Sales Amount per Product

```sql
SELECT
    SaleID,
    ProductID,
    SaleDate,
    Quantity,
    Price,
    Quantity * Price AS SaleAmount,
    SUM(Quantity * Price) OVER (PARTITION BY ProductID ORDER BY SaleDate ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS RunningTotal
FROM
    Sales
ORDER BY
    ProductID,
    SaleDate;
```

**Result**

| SaleID | ProductID | SaleDate   | Quantity | Price | SaleAmount | RunningTotal |
|--------|-----------|------------|----------|-------|------------|--------------|
| 1      | 101       | 2024-01-05 | 10       | 15.00 | 150.00     | 150.00       |
| 3      | 101       | 2024-01-10 | 20       | 15.00 | 300.00     | 450.00       |
| 6      | 101       | 2024-01-20 | 15       | 15.00 | 225.00     | 675.00       |
| 2      | 102       | 2024-01-07 | 5        | 25.00 | 125.00     | 125.00       |
| 5      | 102       | 2024-01-15 | 10       | 25.00 | 250.00     | 375.00       |
| 9      | 102       | 2024-01-28 | 8        | 25.00 | 200.00     | 575.00       |
| 4      | 103       | 2024-01-12 | 7        | 30.00 | 210.00     | 210.00       |
| 7      | 103       | 2024-01-22 | 5        | 30.00 | 150.00     | 360.00       |
| 8      | 104       | 2024-01-25 | 12       | 20.00 | 240.00     | 240.00       |
| 10     | 104       | 2024-01-30 | 10       | 20.00 | 200.00     | 440.00       |

- **`SUM(Quantity * Price) OVER (...)`** calculates a running total of sales amounts within each `ProductID` partition ordered by `SaleDate`.
- The window frame `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` defines the range from the first row to the current row for cumulative calculations.

### Handling NULL Values in Window Functions

Window functions typically handle `NULL` values based on the specific function's behavior. For example, `SUM()` ignores `NULL` values, while `ROW_NUMBER()` assigns a unique number regardless of `NULL`s.

#### Example: Assigning Row Numbers with NULL Quantities

Suppose we have an additional sale with a `NULL` quantity.

**Updated Sales Table**

| SaleID | ProductID | SaleDate   | Quantity | Price |
|--------|-----------|------------|----------|-------|
| 11     | 101       | 2024-01-25 | NULL     | 15.00 |

**Query: Assigning Row Numbers Including NULL Quantities**

```sql
SELECT
    SaleID,
    ProductID,
    SaleDate,
    Quantity,
    Price,
    ROW_NUMBER() OVER (PARTITION BY ProductID ORDER BY SaleDate) AS RowNum
FROM
    Sales
ORDER BY
    ProductID,
    SaleDate;
```

**Result**

| SaleID | ProductID | SaleDate   | Quantity | Price | RowNum |
|--------|-----------|------------|----------|-------|--------|
| 1      | 101       | 2024-01-05 | 10       | 15.00 | 1      |
| 3      | 101       | 2024-01-10 | 20       | 15.00 | 2      |
| 6      | 101       | 2024-01-20 | 15       | 15.00 | 3      |
| 11     | 101       | 2024-01-25 | NULL     | 15.00 | 4      |
| ...    | ...       | ...        | ...      | ...   | ...    |

- The `ROW_NUMBER()` function assigns a row number to the sale with `NULL` quantity without any issues.
- Other window functions may handle `NULL` values differently, depending on their logic.

### Practical Tips for Using Window Functions

- **Use Meaningful Aliases**: Assign descriptive aliases to window function results to improve query readability.
  
  ```sql
  ROW_NUMBER() OVER (...) AS RowNumber
  ```

- **Combine with `PARTITION BY` and `ORDER BY`**: Leverage `PARTITION BY` to segment data and `ORDER BY` to define the sequence within each partition.
  
  ```sql
  RANK() OVER (PARTITION BY Category ORDER BY SaleAmount DESC) AS SaleRank
  ```

- **Leverage Window Frames for Advanced Calculations**: Use window frame specifications like `ROWS BETWEEN` to define dynamic ranges for calculations.
  
  ```sql
  AVG(Quantity) OVER (PARTITION BY ProductID ORDER BY SaleDate ROWS BETWEEN 3 PRECEDING AND CURRENT ROW) AS MovingAverage
  ```

- **Avoid Overusing Window Functions**: While powerful, excessive use of window functions can lead to complex and less performant queries. Use them judiciously.

- **Understand Performance Implications**: Window functions can impact query performance, especially on large datasets. Ensure proper indexing and consider query optimization techniques.

- **Combine with Other SQL Features**: Window functions can be combined with CTEs (Common Table Expressions), subqueries, and other SQL features for more complex analyses.
  
  ```sql
  WITH RankedSales AS (
      SELECT
          SaleID,
          ProductID,
          SaleDate,
          Quantity,
          Price,
          RANK() OVER (PARTITION BY ProductID ORDER BY Quantity DESC) AS SaleRank
      FROM
          Sales
  )
  SELECT
      rs.SaleID,
      rs.ProductID,
      rs.SaleDate,
      rs.Quantity,
      rs.Price
  FROM
      RankedSales rs
  WHERE
      rs.SaleRank = 1;
  ```

### Window Functions vs. Aggregate Functions

While both window functions and aggregate functions perform calculations over sets of rows, they differ in key ways:

- **Row Retention**: 
  - **Aggregate Functions**: Collapse multiple rows into a single summary row per group.
  - **Window Functions**: Retain individual row identities while providing additional calculated data.

- **Usage with `GROUP BY`**:
  - **Aggregate Functions**: Require `GROUP BY` to define grouping.
  - **Window Functions**: Use the `OVER` clause to define partitions and ordering without collapsing rows.

#### Example: Comparing Aggregate and Window Functions

**Aggregate Function Example: Total Sales per Product**

```sql
SELECT
    ProductID,
    SUM(Quantity * Price) AS TotalSales
FROM
    Sales
GROUP BY
    ProductID;
```

**Window Function Example: Total Sales per Product Alongside Each Sale**

```sql
SELECT
    SaleID,
    ProductID,
    SaleDate,
    Quantity,
    Price,
    SUM(Quantity * Price) OVER (PARTITION BY ProductID) AS TotalSalesPerProduct
FROM
    Sales
ORDER BY
    ProductID,
    SaleDate;
```

- The **aggregate function** provides a summarized view with one row per `ProductID`.
- The **window function** adds the total sales per product to each individual sale row without reducing the number of rows.

### Combining Multiple Window Functions

You can use multiple window functions within a single query to perform various analyses simultaneously.

#### Example: Sales Analysis with Multiple Window Functions

```sql
SELECT
    SaleID,
    ProductID,
    SaleDate,
    Quantity,
    Price,
    ROW_NUMBER() OVER (PARTITION BY ProductID ORDER BY SaleDate) AS RowNum,
    RANK() OVER (PARTITION BY ProductID ORDER BY Quantity DESC) AS QuantityRank,
    SUM(Quantity * Price) OVER (PARTITION BY ProductID ORDER BY SaleDate ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS RunningTotal
FROM
    Sales
ORDER BY
    ProductID,
    SaleDate;
```

**Result**

| SaleID | ProductID | SaleDate   | Quantity | Price | RowNum | QuantityRank | RunningTotal |
|--------|-----------|------------|----------|-------|--------|--------------|--------------|
| 1      | 101       | 2024-01-05 | 10       | 15.00 | 1      | 2            | 150.00       |
| 3      | 101       | 2024-01-10 | 20       | 15.00 | 2      | 1            | 450.00       |
| 6      | 101       | 2024-01-20 | 15       | 15.00 | 3      | 3            | 675.00       |
| 11     | 101       | 2024-01-25 | NULL     | 15.00 | 4      | 4            | 675.00       |
| 2      | 102       | 2024-01-07 | 5        | 25.00 | 1      | 3            | 125.00       |
| 5      | 102       | 2024-01-15 | 10       | 25.00 | 2      | 1            | 375.00       |
| 9      | 102       | 2024-01-28 | 8        | 25.00 | 3      | 2            | 575.00       |
| 4      | 103       | 2024-01-12 | 7        | 30.00 | 1      | 1            | 210.00       |
| 7      | 103       | 2024-01-22 | 5        | 30.00 | 2      | 2            | 360.00       |
| 8      | 104       | 2024-01-25 | 12       | 20.00 | 1      | 1            | 240.00       |
| 10     | 104       | 2024-01-30 | 10       | 20.00 | 2      | 2            | 440.00       |

- **`ROW_NUMBER()`** assigns a unique row number within each `ProductID` partition.
- **`RANK()`** assigns ranks based on `Quantity` within each `ProductID`.
- **`SUM() OVER (...)`** calculates a running total of sales amounts per `ProductID`.

### Window Frames

Window frames define the subset of rows within the partition to be used for calculations in window functions. They are specified using the `ROWS BETWEEN` or `RANGE BETWEEN` clauses.

#### Example: Calculating a Moving Average of Quantity

```sql
SELECT
    SaleID,
    ProductID,
    SaleDate,
    Quantity,
    Price,
    AVG(Quantity) OVER (
        PARTITION BY ProductID
        ORDER BY SaleDate
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS MovingAverage
FROM
    Sales
ORDER BY
    ProductID,
    SaleDate;
```

**Result**

| SaleID | ProductID | SaleDate   | Quantity | Price | MovingAverage |
|--------|-----------|------------|----------|-------|----------------|
| 1      | 101       | 2024-01-05 | 10       | 15.00 | 10.00          |
| 3      | 101       | 2024-01-10 | 20       | 15.00 | 15.00          |
| 6      | 101       | 2024-01-20 | 15       | 15.00 | 15.00          |
| 11     | 101       | 2024-01-25 | NULL     | 15.00 | 12.50          |
| 2      | 102       | 2024-01-07 | 5        | 25.00 | 5.00           |
| 5      | 102       | 2024-01-15 | 10       | 25.00 | 7.50           |
| 9      | 102       | 2024-01-28 | 8        | 25.00 | 7.67           |
| 4      | 103       | 2024-01-12 | 7        | 30.00 | 7.00           |
| 7      | 103       | 2024-01-22 | 5        | 30.00 | 6.00           |
| 8      | 104       | 2024-01-25 | 12       | 20.00 | 12.00          |
| 10     | 104       | 2024-01-30 | 10       | 20.00 | 11.00          |

- The `AVG(Quantity)` function calculates the average quantity over the current row and the two preceding rows within each `ProductID` partition.
- Useful for trend analysis and smoothing out short-term fluctuations.

### Practical Use Cases for Window Functions

- **Pagination**: Assign row numbers to implement pagination in queries.
- **Running Totals and Moving Averages**: Calculate cumulative sums or averages over a specified window.
- **Ranking and Top-N Analysis**: Determine the top performers or items within categories.
- **Comparative Analysis**: Compare current row values with previous or next rows without self-joins.
- **Data Transformation**: Restructure data for reporting and analytics purposes.

### Combining Window Functions with Other SQL Features

Window functions can be combined with Common Table Expressions (CTEs), subqueries, and other SQL constructs to perform complex data transformations and analyses.

#### Example: Identifying Top 2 Sales per Product

```sql
WITH RankedSales AS (
    SELECT
        SaleID,
        ProductID,
        SaleDate,
        Quantity,
        Price,
        RANK() OVER (PARTITION BY ProductID ORDER BY Quantity DESC) AS SaleRank
    FROM
        Sales
)
SELECT
    rs.SaleID,
    rs.ProductID,
    rs.SaleDate,
    rs.Quantity,
    rs.Price
FROM
    RankedSales rs
WHERE
    rs.SaleRank <= 2
ORDER BY
    rs.ProductID,
    rs.SaleRank;
```

**Result**

| SaleID | ProductID | SaleDate   | Quantity | Price |
|--------|-----------|------------|----------|-------|
| 3      | 101       | 2024-01-10 | 20       | 15.00 |
| 6      | 101       | 2024-01-20 | 15       | 15.00 |
| 5      | 102       | 2024-01-15 | 10       | 25.00 |
| 9      | 102       | 2024-01-28 | 8        | 25.00 |
| 4      | 103       | 2024-01-12 | 7        | 30.00 |
| 7      | 103       | 2024-01-22 | 5        | 30.00 |
| 8      | 104       | 2024-01-25 | 12       | 20.00 |
| 10     | 104       | 2024-01-30 | 10       | 20.00 |

- The CTE `RankedSales` assigns a rank to each sale based on `Quantity` within each `ProductID`.
- The outer query filters to include only the top 2 sales per product.

### Comparing Window Functions with Self-Joins

Before window functions were widely supported, similar analyses often required complex self-joins. Window functions simplify these operations, making queries more readable and efficient.

#### Example: Using Window Functions vs. Self-Joins to Compare Current and Previous Sales

**Using Window Functions**

```sql
SELECT
    SaleID,
    ProductID,
    SaleDate,
    Quantity,
    Price,
    LAG(Quantity) OVER (PARTITION BY ProductID ORDER BY SaleDate) AS PreviousQuantity
FROM
    Sales
ORDER BY
    ProductID,
    SaleDate;
```

**Using Self-Joins**

```sql
SELECT
    s1.SaleID,
    s1.ProductID,
    s1.SaleDate,
    s1.Quantity,
    s1.Price,
    s2.Quantity AS PreviousQuantity
FROM
    Sales s1
LEFT JOIN
    Sales s2
    ON s1.ProductID = s2.ProductID
    AND s1.SaleDate > s2.SaleDate
    AND NOT EXISTS (
        SELECT 1
        FROM Sales s3
        WHERE s3.ProductID = s1.ProductID
        AND s3.SaleDate > s2.SaleDate
        AND s3.SaleDate < s1.SaleDate
    )
ORDER BY
    s1.ProductID,
    s1.SaleDate;
```

- The **window function** approach is more straightforward, readable, and performs better.
- The **self-join** approach is more complex and can be less efficient, especially on large datasets.

### Limitations and Considerations

- **Performance**: Window functions can be resource-intensive on large datasets. Proper indexing and query optimization are crucial.
- **Compatibility**: Ensure that your SQL database system supports the window functions you intend to use (e.g., PostgreSQL, SQL Server, Oracle, MySQL 8.0+).
- **Complexity**: While window functions simplify many operations, overusing them or using them in overly complex ways can make queries harder to maintain.
- **Understanding Window Frames**: Properly defining window frames is essential for accurate calculations, especially for running totals and moving averages.

### Advanced Window Function Features

- **Frame Specifications**: Define dynamic ranges for window functions to perform calculations like moving averages, cumulative sums, etc.
  
  ```sql
  SUM(Quantity) OVER (
      PARTITION BY ProductID
      ORDER BY SaleDate
      ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING
  ) AS SumQuantity
  ```

- **Multiple Partitioning and Ordering**: Combine multiple columns in `PARTITION BY` and `ORDER BY` for more granular control.

  ```sql
  ROW_NUMBER() OVER (
      PARTITION BY Category, SubCategory
      ORDER BY SaleDate DESC
  ) AS RowNum
  ```

- **Using `RANGE` Instead of `ROWS`**: Define frames based on logical ranges rather than physical row counts.

  ```sql
  AVG(Price) OVER (
      PARTITION BY ProductID
      ORDER BY SaleDate
      RANGE BETWEEN INTERVAL '7' DAY PRECEDING AND CURRENT ROW
  ) AS WeeklyAveragePrice
  ```

### Example Use Case: Sales Trend Analysis

Suppose you want to analyze sales trends by calculating the percentage change in quantity compared to the previous sale for each product.

```sql
SELECT
    SaleID,
    ProductID,
    SaleDate,
    Quantity,
    Price,
    LAG(Quantity) OVER (PARTITION BY ProductID ORDER BY SaleDate) AS PreviousQuantity,
    CASE 
        WHEN LAG(Quantity) OVER (PARTITION BY ProductID ORDER BY SaleDate) IS NULL THEN NULL
        ELSE ((Quantity - LAG(Quantity) OVER (PARTITION BY ProductID ORDER BY SaleDate)) * 100.0) / LAG(Quantity) OVER (PARTITION BY ProductID ORDER BY SaleDate)
    END AS PercentageChange
FROM
    Sales
ORDER BY
    ProductID,
    SaleDate;
```

**Result**

| SaleID | ProductID | SaleDate   | Quantity | Price | PreviousQuantity | PercentageChange |
|--------|-----------|------------|----------|-------|-------------------|-------------------|
| 1      | 101       | 2024-01-05 | 10       | 15.00 | NULL              | NULL              |
| 3      | 101       | 2024-01-10 | 20       | 15.00 | 10                | 100.00            |
| 6      | 101       | 2024-01-20 | 15       | 15.00 | 20                | -25.00            |
| 11     | 101       | 2024-01-25 | NULL     | 15.00 | 15                | -100.00           |
| 2      | 102       | 2024-01-07 | 5        | 25.00 | NULL              | NULL              |
| 5      | 102       | 2024-01-15 | 10       | 25.00 | 5                 | 100.00            |
| 9      | 102       | 2024-01-28 | 8        | 25.00 | 10                | -20.00            |
| 4      | 103       | 2024-01-12 | 7        | 30.00 | NULL              | NULL              |
| 7      | 103       | 2024-01-22 | 5        | 30.00 | 7                 | -28.57            |
| 8      | 104       | 2024-01-25 | 12       | 20.00 | NULL              | NULL              |
| 10     | 104       | 2024-01-30 | 10       | 20.00 | 12                | -16.67            |

- This query calculates the percentage change in `Quantity` compared to the previous sale for each `ProductID`.
- Useful for identifying trends, growth, or decline in sales over time.
