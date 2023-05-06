## Primary keys and secondary keys 

Primary keys and secondary keys are two types of keys used in relational databases to uniquely identify records and establish relationships between tables. This note focuses on the differences, characteristics, and use cases of primary keys and secondary keys.

## Characteristics

A. Primary Key

1. A primary key is a column or a set of columns that uniquely identify each row in a table.
2. Primary keys enforce uniqueness constraints and ensure that there are no duplicate records in the table.
3. A table can have only one primary key.
4. Primary keys cannot contain NULL values.
5. Primary keys are often used as a reference in foreign key relationships between tables.

B. Secondary Key

1. A secondary key is a column or a set of columns that can uniquely identify rows in a table but is not the primary key.
2. Secondary keys are also known as alternative keys or unique keys.
3. A table can have multiple secondary keys.
4. Secondary keys also enforce uniqueness constraints but can contain NULL values (unless specified as unique).
5. Secondary keys are often used for indexing and querying purposes to improve performance.

## Examples

I. Users Table

| user_id | first_name | last_name | email                 | phone_number   |
|---------|------------|-----------|-----------------------|----------------|
| 1       | Alice      | Smith     | alice.smith@email.com | (555) 123-4567 |
| 2       | Bob        | Johnson   | bob.johnson@email.com | (555) 987-6543 |
| 3       | Carol      | Williams  | carol.w@email.com     | (555) 555-5555 |

Primary Key: user_id
Secondary Key: email

In the Users table, the 'user_id' column is the primary key, uniquely identifying each user. The 'email' column is a secondary key, enforcing uniqueness for each email address.

II. Orders Table

| order_id | user_id | product_id | order_date | order_status |
|----------|---------|------------|------------|--------------|
| 1        | 1       | 101        | 2023-04-01 | shipped      |
| 2        | 3       | 102        | 2023-04-03 | delivered    |
| 3        | 2       | 103        | 2023-04-05 | processing   |

Primary Key: order_id
Foreign Key: user_id (references Users table)

In the Orders table, the 'order_id' column is the primary key, uniquely identifying each order. The 'user_id' column is a foreign key that references the primary key in the Users table, establishing a relationship between the two tables.

III. Products Table

| product_id | product_name  | category  | price | stock | sku          |
|------------|---------------|-----------|-------|-------|--------------|
| 101        | Laptop        | Computers | 999   | 50    | LAPTOP-12345 |
| 102        | Smart Speaker | Audio     | 49    | 200   | SPKR-67890   |
| 103        | Monitor       | Computers | 199   | 75    | MONITOR-4321 |

Primary Key: product_id
Secondary Key: sku

In the Products table, the 'product_id' column is the primary key, uniquely identifying each product. The 'sku' column is a secondary key, enforcing uniqueness for each SKU (Stock Keeping Unit).

## Use Cases

A. Primary Key

1. Primary keys are used to uniquely identify records in a table and prevent duplicate data.
2. They are used to establish relationships between tables through foreign key constraints, ensuring referential integrity.
3. Primary keys can be used as indexes to speed up lookups and join operations.

B. Secondary Key

1. Secondary keys are used to enforce uniqueness constraints on columns other than the primary key.
2. They can be used as indexes to improve query performance when searching for data based on unique attributes other than the primary key.
3. Secondary keys can help to enforce business rules or requirements, such as ensuring unique email addresses for users in a table.
