## Database normalization

Database normalization is a process used to efficiently organize a relational database by minimizing redundancy and ensuring data integrity. Normalization deals with the problem of having the same data in multiple cells, which can cause issues with updating (requiring updates to all occurrences), deletion (losing information about a client when deleting orders), and insertion (needing an order to insert a client). The solution is decomposition, which means splitting the data into multiple tables. 

## Why do we need Normalization?

- **Eliminate redundancy** - Minimize duplicate data within tables to conserve storage space and enhance performance. Each fact stored in the database should be expressible in only one way.

- **Ensure data integrity** - Preserve consistency and accuracy of data by enforcing rules and constraints. The normalization process can be treated as a process in which relation schemas with certain undesirable characteristics are decomposed into smaller relation schemas with desired properties.

- **Simplify the database design** - Decompose complex tables into smaller, more manageable ones, making it easier to maintain and query the data.

## Example of a Denormalized Table

Consider a simple database for a library system. Here is an example of a denormalized table:

| Book_ID | Book_Title | Authors       | Publisher_ID | Publisher_Name | Publisher_Location |
|---------|------------|---------------|--------------|----------------|--------------------|
| B1      | Book A     | John Doe, Jane Doe | P1     | Publish Corp  | New York           |
| B2      | Book B     | Mary Lee     | P2     | Bookmania    | Los Angeles        |
| B3      | Book C     | John Doe     | P1     | Publish Corp  | New York           |
| B4      | Book D     | Jane Doe     | P3     | Literature Inc| San Francisco      |

In this denormalized table, information about both books and publishers are stored in the same table. You can see repeated information for 'Publisher_Name' and 'Publisher_Location' for books from the same publisher. This redundancy could lead to potential inconsistencies and anomalies. Normalization can be used to eliminate these redundancies.

## Normal Forms

In the context of database normalization, a normal form is a property or a state of a relation (a table) which helps to organize data with minimal redundancy. The idea of normal forms was first proposed by Edgar Codd, the inventor of the relational model for database management. 

There are several normal forms, each with an increasing level of strictness. These are:

1. First Normal Form (1NF)
2. Second Normal Form (2NF)
3. Third Normal Form (3NF)
4. Boyce-Codd Normal Form (BCNF)
5. Fourth Normal Form (4NF)
6. Fifth Normal Form (5NF) or Project-Join Normal Form (PJNF)
7. Sixth Normal Form (6NF)
8. Domain/Key Normal Form (DKNF)

The higher the normal form, the less redundancy in the database, but also the more complex and potentially less performant the database can become. 

Each normal form has a particular set of rules it must follow. If it follows these rules, then the database or table is said to be in that normal form. 

### Where and When to Use Each Normal Form?

1. **First Normal Form (1NF):** This is the most basic level of normalization and it is typically where you begin when normalizing a database. 1NF is used to eliminate duplicate columns from the same table and create separate tables for each group of related data.

2. **Second Normal Form (2NF):** Once your database is in 1NF, you can progress to 2NF. 2NF is used to remove subsets of data that apply to multiple rows of a table and place them in separate tables. 

3. **Third Normal Form (3NF):** A database is in 3NF if it is in 2NF and all of its columns depend only on the table’s primary key. This normal form is used to eliminate fields in a table that do not directly depend on the primary key.

4. **Boyce-Codd Normal Form (BCNF):** A database is in BCNF if it is in 3NF and for every one of its dependencies X → Y, X is a superkey. BCNF is used to handle the anomalies that are not handled by 3NF.

5. **Fourth Normal Form (4NF):** If a database needs to store multi-valued dependencies, it would be necessary to use 4NF.

6. **Fifth Normal Form (5NF):** Also known as Project-Join Normal Form, this is used to eliminate join dependencies that are not implied by candidate keys.

7. **Sixth Normal Form (6NF):** Mainly used for databases which need to manage historic data, such as time series data.

8. **Domain/Key Normal Form (DKNF):** The ultimate normalization form, but rarely used due to its complexity. It ensures that every constraint on the relation is a logical consequence of the definition of keys and domains.

Choosing the right level of normalization for a database involves a trade-off between the desire to minimize redundancy and the need to optimize performance. A more normalized database requires more CPU cycles and potentially more I/O, but it offers greater data consistency. Conversely, a less normalized database may be faster and simpler to use, but it can permit more data anomalies and inconsistencies.

## First Normal Form (1NF)

The first normal form (1NF) is the simplest level of data normalization. A table is in 1NF if:

1. It has a primary key: a unique identifier for each row of data.
2. All of its attributes (columns) contain only atomic (indivisible) values. In other words, each column should contain only one value from the domain of that column.
3. Each column name is unique and each column data type is consistent.
4. Each row is unique and there are no duplicate rows.

Consider the following table:

| StudentID | Subject           |
|-----------|-------------------|
| 1         | Math, Science     |
| 2         | English, History  |
| 3         | Art, Music        |

This table is not in 1NF because the 'Subject' column contains multiple values. To bring this table to 1NF, we could adjust it to:

| StudentID | Subject  |
|-----------|----------|
| 1         | Math     |
| 1         | Science  |
| 2         | English  |
| 2         | History  |
| 3         | Art      |
| 3         | Music    |

Now, each cell in the table has a single value and each record is unique. The 'StudentID' and 'Subject' columns together form the primary key of the table, ensuring unique identification of each record.

## Second Normal Form (2NF)

A table is in Second Normal Form (2NF) if it meets all the rules of 1NF and in addition:

1. It has no partial dependencies.
2. Every non-prime attribute of the table must be functionally dependent on the whole of a candidate key.

Partial dependency means that a column depends on only part of the primary key, not the entire key.

Consider the following table:

| StudentID | Subject | Teacher |
|-----------|---------|---------|
| 1         | Math    | Mr. A   |
| 1         | Science | Ms. B   |
| 2         | English | Ms. C   |
| 2         | History | Mr. D   |
| 3         | Art     | Mr. E   |
| 3         | Music   | Ms. F   |

Here, 'Teacher' depends on 'Subject', not on the whole primary key 'StudentID' and 'Subject'. To bring this table to 2NF, we can split it into two tables:

**Student_Subject Table**

| StudentID | Subject |
|-----------|---------|
| 1         | Math    |
| 1         | Science |
| 2         | English |
| 2         | History |
| 3         | Art     |
| 3         | Music   |

**Subject_Teacher Table**

| Subject | Teacher |
|---------|---------|
| Math    | Mr. A   |
| Science | Ms. B   |
| English | Ms. C   |
| History | Mr. D   |
| Art     | Mr. E   |
| Music   | Ms. F   |

In these new tables, each non-prime attribute is fully functionally dependent on the primary key.

## Third Normal Form (3NF)

A table is in Third Normal Form (3NF) if it satisfies the following conditions:

1. It is in Second Normal Form (2NF).
2. It has no transitive functional dependencies.
3. Every non-prime attribute of the table is non-transitively dependent on every key of the table.

A transitive dependency occurs when one non-key column depends on another non-key column, which depends on the key. 

Consider the following table:

| StudentID | Course  | CourseLeader | LeaderPhone |
|-----------|---------|--------------|-------------|
| 1         | Math    | Mr. A        | 1234567890  |
| 2         | English | Ms. B        | 0987654321  |
| 3         | Art     | Mr. C        | 1122334455  |

In this table, 'LeaderPhone' is transitively dependent on the 'StudentID' through the 'CourseLeader'. This table is not in 3NF. To convert it to 3NF, we can split it into two tables:

**Student_Course Table**

| StudentID | Course  | CourseLeader |
|-----------|---------|--------------|
| 1         | Math    | Mr. A        |
| 2         | English | Ms. B        |
| 3         | Art     | Mr. C        |

**Leader_Contact Table**

| CourseLeader | LeaderPhone |
|--------------|-------------|
| Mr. A        | 1234567890  |
| Ms. B        | 0987654321  |
| Mr. C        | 1122334455  |

In these new tables, all non-prime attributes are non-transitively dependent on the primary key.

## Boyce-Codd Normal Form (BCNF)

The Boyce-Codd Normal Form (BCNF) is an extension of the Third Normal Form (3NF). A table is in BCNF if it is in 3NF and every determinant is a candidate key. In simple terms, it deals with certain type of anomaly that is not handled by 3NF. A relation is in BCNF if for every one of its dependencies X → Y, at least one of the following conditions hold:

1. X is a superkey.
2. Each attribute in Y-X, the set difference between the attributes in Y and X, is a prime attribute (i.e., each attribute in Y-X is part of some candidate key).

BCNF is very useful in reducing redundancy, but it can sometimes lead to fragmentation of the database, which might make it less efficient in some cases.

Consider the following table:

| EmployeeID | Project  | Department | DepartmentHead |
|------------|----------|------------|----------------|
| 1          | ProjectA | Dept1      | Mr. A          |
| 2          | ProjectB | Dept1      | Mr. A          |
| 3          | ProjectC | Dept2      | Ms. B          |

In this table, DepartmentHead is dependent on Department, not on the combination of EmployeeID and Project. This violates BCNF as Department is not a superkey. The table can be split into two tables to satisfy BCNF:

**Employee_Project Table**

| EmployeeID | Project  | Department |
|------------|----------|------------|
| 1          | ProjectA | Dept1      |
| 2          | ProjectB | Dept1      |
| 3          | ProjectC | Dept2      |

**Department_Head Table**

| Department | DepartmentHead |
|------------|----------------|
| Dept1      | Mr. A          |
| Dept2      | Ms. B          |

These tables now conform to BCNF as every determinant is a candidate key.

## Fourth Normal Form (4NF)

Fourth Normal Form (4NF) is a level of database normalization where we deal with multi-valued dependency. A table is said to be in 4NF if it is in Boyce-Codd Normal Form (BCNF) and it does not have multi-valued dependencies.

A multi-valued dependency occurs when the presence of one or more rows in a table implies the presence of one or more other rows in that same table.

A table is in the Fourth Normal Form (4NF) if, for no non-trivial multi-valued dependencies X →→ Y, X is not a subset of (or equal to) a candidate key.

Just like BCNF, 4NF also aids in reducing redundancy from a relation schema.

Consider the following table:

| EmployeeID | Skills  | Hobbies  |
|------------|---------|----------|
| 1          | Coding  | Football |
| 1          | Design  | Football |
| 2          | Design  | Music    |

In this table, EmployeeID →→ Skills and EmployeeID →→ Hobbies are multi-valued dependencies. The table can be decomposed into two tables to eliminate the multi-valued dependencies:

**Employee_Skills Table**

| EmployeeID | Skills  |
|------------|---------|
| 1          | Coding  |
| 1          | Design  |
| 2          | Design  |

**Employee_Hobbies Table**

| EmployeeID | Hobbies  |
|------------|----------|
| 1          | Football |
| 2          | Music    |

These tables now conform to 4NF as they have no multi-valued dependencies.

## Fifth Normal Form (5NF)

Fifth Normal Form (5NF), also known as Project-Join Normal Form (PJNF), is a level of database normalization designed to reduce redundancy in relational databases recording multi-valued facts by isolating semantically related multiple relationships. A table is in 5NF if every join dependency in it is implied by the candidate keys.

This form deals with cases where information can be reconstructed from smaller pieces which can be maintained with less redundancy.

5NF is used in situations where the interactions of multiple components need to be handled. Often, these tables will seem to be in 3NF or BCNF, but further inspection reveals hidden redundancy.

Consider the following table representing suppliers, parts, and projects:

| Supplier | Part | Project |
|----------|------|---------|
| S1       | P1   | J1      |
| S1       | P2   | J1      |
| S2       | P1   | J2      |
| S2       | P3   | J2      |
| S3       | P1   | J3      |

This table represents the facts that:

- Supplier S1 supplies parts P1 and P2 for project J1
- Supplier S2 supplies parts P1 and P3 for project J2
- Supplier S3 supplies part P1 for project J3

This table is not in 5NF because it represents three separate relationships:

1. The supplier can supply multiple parts
2. A part can be used in multiple projects
3. A supplier can supply to multiple projects

We can decompose it into three separate tables to bring it into 5NF:

**Supplier_Part Table**

| Supplier | Part |
|----------|------|
| S1       | P1   |
| S1       | P2   |
| S2       | P1   |
| S2       | P3   |
| S3       | P1   |

**Part_Project Table**

| Part | Project |
|------|---------|
| P1   | J1      |
| P2   | J1      |
| P1   | J2      |
| P3   | J2      |
| P1   | J3      |

**Supplier_Project Table**

| Supplier | Project |
|----------|---------|
| S1       | J1      |
| S2       | J2      |
| S3       | J3      |

These tables now conform to 5NF as every join dependency in each table is implied by the candidate keys.

