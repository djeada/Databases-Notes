## Primary keys and Secondary keys 

Primary and secondary keys are essential components of relational databases used to establish data integrity, uniquely identify records, and set up relationships among tables. 

## Characteristics

### Primary Key

1. A primary key is a column or a set of columns that serve as a unique identifier for rows within a table.
2. Uniqueness constraints enforced by primary keys prevent the occurrence of duplicate rows in the table.
3. Only one primary key is permitted per table, ensuring a unique point of reference.
4. Primary keys cannot contain NULL values, guaranteeing a definite value for each row's key.
5. Often, primary keys are utilized in defining foreign key relationships between tables, thereby preserving the relational aspect of databases.

### Secondary Key

1. A secondary key, also referred to as an alternate key or a unique key, is a column or a set of columns that can uniquely identify records within a table but is not selected as the primary key.
2. Like primary keys, secondary keys enforce uniqueness constraints but they can contain NULL values, given they are not explicitly specified as unique.
3. Unlike primary keys, a table can be designed to have multiple secondary keys.
4. Secondary keys are used primarily for querying and indexing purposes to enhance performance and data accessibility.

## Examples

### Users Table

| user_id | first_name | last_name | email                 | phone_number   |
|---------|------------|-----------|-----------------------|----------------|
| 1       | Alice      | Smith     | alice.smith@email.com | (555) 123-4567 |
| 2       | Bob        | Johnson   | bob.johnson@email.com | (555) 987-6543 |
| 3       | Carol      | Williams  | carol.w@email.com     | (555) 555-5555 |

Primary Key: user_id
Secondary Key: email, phone_number

In the Users table, 'user_id' is a primary key and 'email' and 'phone_number' are secondary keys. While 'user_id' uniquely identifies each user, 'email' and 'phone_number' provide additional unique points of data access.

### Orders Table

| order_id | user_id | product_id | order_date | order_status |
|----------|---------|------------|------------|--------------|
| 1        | 1       | 101        | 2023-04-01 | shipped      |
| 2        | 3       | 102        | 2023-04-03 | delivered    |
| 3        | 2       | 103        | 2023-04-05 | processing   |

Primary Key: order_id
Foreign Key: user_id (references Users table)

The Orders table uses 'order_id' as the primary key to uniquely identify each order. The 'user_id' is a foreign key that references the 'user_id' primary key from the Users table, thereby establishing a relationship between the two tables.

### Products Table

| product_id | product_name  | category  | price | stock | sku          |
|------------|---------------|-----------|-------|-------|--------------|
| 101        | Laptop        | Computers | 999   | 50    | LAPTOP-12345 |
| 102        | Smart Speaker | Audio     | 49    | 200   | SPKR-67890   |
| 103        | Monitor       | Computers | 199   | 75    | MONITOR-4321 |

Primary Key: product_id
Secondary Key: sku

In the Products table, the 'product_id' column serves as the primary key. The 'sku' column, while also unique, serves as a secondary key, providing an additional axis of data identification.

## Use Cases

### Primary Key

1. Primary keys are the cornerstone of data integrity, uniquely identifying records within a table and precluding the possibility of duplicate data.
2. Primary keys form the basis of foreign key relationships, maintaining referential integrity across tables.
3. Primary keys often serve as indexes to enhance data retrieval speed, supporting faster lookup and join operations.

### Secondary Key

1. Secondary keys provide an additional avenue for enforcing uniqueness constraints outside the primary key.
2. By serving as indexes, secondary keys expedite queries involving attributes that, while not primary, are still unique.
3. Secondary keys allow for more granular data rules, such as requiring unique email addresses or usernames, thereby ensuring that business rules are respected at the database level.
