## Primary Keys and Secondary Keys

Grasping the concepts of primary and secondary keys is essential when working with relational databases. These keys play a pivotal role in ensuring data integrity, uniquely identifying records, and establishing relationships among different tables. Let's dive into what they are, how they function, and why they're important.

### Understanding Primary Keys

A primary key in a database table is a column, or a set of columns, that uniquely identifies each row within that table. This means that no two rows can have the same primary key value, ensuring the uniqueness of every record. Additionally, primary keys cannot contain `NULL` values, meaning that every row must have a valid and unique identifier.

For example, consider a `Users` table where each user has a unique `user_id`:

| user_id | first_name | last_name | email                   | phone_number     |
|---------|------------|-----------|-------------------------|------------------|
| 1       | Alice      | Smith     | alice.smith@example.com | (555) 123-4567   |
| 2       | Bob        | Johnson   | bob.johnson@example.com | (555) 987-6543   |
| 3       | Carol      | Williams  | carol.w@example.com     | (555) 555-5555   |

In this table, `user_id` serves as the primary key, uniquely identifying each user.

#### Key Characteristics of Primary Keys

- **Uniqueness**: Every value in the primary key column must be unique across the table.
- **Non-nullability**: Primary keys cannot have `NULL` values; each record must have a value.
- **Single Primary Key per Table**: A table can have only one primary key, which may consist of multiple columns (known as a composite key).
- **Indexing**: Databases automatically create an index on the primary key to speed up data retrieval.
- **Referential Integrity**: Primary keys can be referenced by foreign keys in other tables, establishing relationships between tables.

### Exploring Secondary Keys

Secondary keys, also known as alternate or unique keys, are columns that also contain unique values but are not designated as the primary key. They provide additional ways to identify records uniquely and can be used to enforce uniqueness constraints on other important columns.

Continuing with the `Users` table, the `email` and `phone_number` columns can serve as secondary keys since they are unique for each user:

| user_id | first_name | last_name | email                   | phone_number     |
|---------|------------|-----------|-------------------------|------------------|
| 1       | Alice      | Smith     | alice.smith@example.com | (555) 123-4567   |
| 2       | Bob        | Johnson   | bob.johnson@example.com | (555) 987-6543   |
| 3       | Carol      | Williams  | carol.w@example.com     | (555) 555-5555   |

#### Key Characteristics of Secondary Keys

- **Uniqueness Constraints**: They ensure that values in the secondary key columns are unique, preventing duplicate entries.
- **Multiple per Table**: A table can have multiple secondary keys.
- **Nullable Values**: Secondary keys can contain `NULL` values unless explicitly defined as `NOT NULL`.
- **Indexing for Performance**: Secondary keys are often indexed to improve query performance when searching by those columns.
- **Alternate Access Paths**: They provide additional ways to access and reference records.

### How Primary and Secondary Keys Work Together

Primary and secondary keys enhance the functionality and integrity of a database by ensuring unique identification and providing multiple ways to access data.

#### Example: Orders Table

Consider an `Orders` table where each order is uniquely identified by an `order_id`, the primary key:

| order_id | user_id | product_id | order_date | order_status |
|----------|---------|------------|------------|--------------|
| 1        | 1       | 101        | 2023-04-01 | shipped      |
| 2        | 3       | 102        | 2023-04-03 | delivered    |
| 3        | 2       | 103        | 2023-04-05 | processing   |

Here, `order_id` is the primary key, and `user_id` serves as a foreign key that references the `user_id` in the `Users` table. This relationship links each order to the user who placed it.

#### Visualizing Relationships

An ASCII diagram can help illustrate the relationship between the `Users` and `Orders` tables:

```
+-----------+            +------------+
| Users     |            | Orders     |
|-----------|            |------------|
| user_id   |<-----------| user_id    |
| first_name|            | order_id   |
| last_name |            | product_id |
| ...       |            | ...        |
+-----------+            +------------+
```

The arrow indicates that `user_id` in the `Orders` table references `user_id` in the `Users` table.

### Practical Commands and Outputs

Understanding how to define and use primary and secondary keys involves working with SQL commands. Let's look at some examples.

#### Creating a Table with Primary and Secondary Keys

```sql
CREATE TABLE Users (
    user_id INT PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100) UNIQUE NOT NULL,
    phone_number VARCHAR(20) UNIQUE
);
```

**Interpretation**:

- The `user_id` column is set as the primary key.
- The `email` column is defined as a unique secondary key and cannot be `NULL`.
- The `phone_number` column is also a unique secondary key but can be `NULL`.

#### Inserting Data and Enforcing Uniqueness

When inserting data into the `Users` table:

```sql
INSERT INTO Users (user_id, first_name, last_name, email, phone_number)
VALUES (4, 'Dave', 'Brown', 'dave.brown@example.com', '(555) 222-3333');
```

If you try to insert another user with the same `email`:

```sql
INSERT INTO Users (user_id, first_name, last_name, email, phone_number)
VALUES (5, 'Eve', 'Davis', 'dave.brown@example.com', '(555) 444-5555');
```

**Output and Interpretation**:

- The database will return an error: `ERROR: duplicate key value violates unique constraint "users_email_key"`.
- This occurs because the `email` column must be unique, and using an existing email violates the uniqueness constraint enforced by the secondary key.

#### Querying Data Using Secondary Keys

To find a user by their `email`:

```sql
SELECT * FROM Users WHERE email = 'dave.brown@example.com';
```

**Output**:

| user_id | first_name | last_name | email                  | phone_number     |
|---------|------------|-----------|------------------------|------------------|
| 4       | Dave       | Brown     | dave.brown@example.com | (555) 222-3333   |

**Interpretation**:

- The query efficiently retrieves the user's information using the `email` secondary key, thanks to the index created on that column.

### Importance and Use Cases

#### Primary Keys in Action

Primary keys are vital for:

- **Ensuring Data Integrity**: They prevent duplicate records, maintaining the uniqueness of each row.
- **Establishing Relationships**: Primary keys are used in other tables as foreign keys to create links between data.
- **Optimizing Performance**: Indexes on primary keys speed up query execution and data retrieval.

#### Leveraging Secondary Keys

Secondary keys enhance database functionality by:

- **Enforcing Additional Uniqueness**: They ensure that important columns like `email` or `username` remain unique.
- **Improving Query Performance**: Indexes on secondary keys allow for faster searches on those columns.
- **Providing Flexibility**: They offer alternative ways to access and reference records beyond the primary key.

### Real-World Scenario: Products Table

Consider a `Products` table where each product has a unique `product_id` as the primary key and a unique `sku` (Stock Keeping Unit) as a secondary key:

| product_id | product_name  | category  | price | stock | sku          |
|------------|---------------|-----------|-------|-------|--------------|
| 101        | Laptop        | Computers | 999   | 50    | LAPTOP-12345 |
| 102        | Smart Speaker | Audio     | 49    | 200   | SPKR-67890   |
| 103        | Monitor       | Computers | 199   | 75    | MONITOR-4321 |

- **Primary Key**: `product_id` uniquely identifies each product.
- **Secondary Key**: `sku` provides another unique identifier, useful in inventory management and sales.
