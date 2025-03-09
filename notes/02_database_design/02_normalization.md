## Database Normalization

Database normalization is a systematic approach to organizing data in a relational database. By minimizing redundancy and ensuring data integrity, normalization helps in efficiently structuring databases. The process addresses issues that arise when the same data is stored in multiple places, which can lead to complications during updates, deletions, or insertions. To resolve these problems, data is decomposed into multiple related tables.

After reading the material, you should be able to answer the following questions:

1. What is database normalization, and why is it important in organizing and managing relational databases?
2. What are the different normal forms (1NF through 6NF), and what specific rules must a table meet to achieve each normal form?
3. How does normalization help in eliminating data redundancy and ensuring data integrity within a database?
4. Can you provide examples of how to apply the first three normal forms (1NF, 2NF, and 3NF) to transform denormalized tables into normalized ones?
5. What are the benefits and potential challenges associated with implementing higher normal forms like BCNF, 4NF, and 5NF in database design?

### The Importance of Normalization

Understanding why normalization is necessary involves recognizing its key benefits. First and foremost, normalization eliminates redundancy by minimizing duplicate data within tables. This not only conserves storage space but also enhances database performance. Each piece of information should be stored only once to maintain consistency.

Ensuring data integrity is another crucial aspect. By enforcing rules and constraints, normalization preserves the accuracy and consistency of the data throughout the database. It essentially transforms complex schemas with undesirable characteristics into smaller, well-structured schemas.

Simplifying database design is also a significant advantage. Breaking down complex tables into smaller, more manageable ones makes it easier to maintain and query data. This modular approach streamlines database interactions and reduces the potential for errors.

### Example of a Denormalized Table

To illustrate the concept, consider a simple database for a library system. In a denormalized table, information about books and publishers might be stored together:

| Book_ID | Book_Title | Authors           | Publisher_ID | Publisher_Name | Publisher_Location |
|---------|------------|-------------------|--------------|----------------|--------------------|
| B1      | Book A     | John Doe, Jane Doe| P1           | Publish Corp   | New York           |
| B2      | Book B     | Mary Lee          | P2           | Bookmania      | Los Angeles        |
| B3      | Book C     | John Doe          | P1           | Publish Corp   | New York           |
| B4      | Book D     | Jane Doe          | P3           | Literature Inc | San Francisco      |

In this table, publisher information is repeated for each book from the same publisher. This redundancy can lead to inconsistencies and anomalies, such as outdated or conflicting data about publishers. Normalization helps eliminate these issues by separating related data into different tables.

### Normal Forms

Normal forms are guidelines that help in structuring relational databases to reduce redundancy and dependency. Edgar Codd, the inventor of the relational model, introduced these concepts. Each normal form represents a set of rules that a database must follow to achieve a certain level of normalization.

The normal forms, in order of increasing strictness, are:

1. **First Normal Form (1NF)**
2. **Second Normal Form (2NF)**
3. **Third Normal Form (3NF)**
4. **Boyce-Codd Normal Form (BCNF)**
5. **Fourth Normal Form (4NF)**
6. **Fifth Normal Form (5NF)**
7. **Sixth Normal Form (6NF)**
8. **Domain/Key Normal Form (DKNF)**

Higher normal forms reduce redundancy but may increase complexity and affect performance. Deciding how far to normalize depends on the specific requirements and constraints of the database system.

#### When to Use Each Normal Form

1. *First Normal Form (1NF)* requires that each table has a unique identifier (a primary key) and that every cell in the table holds only a single, simple value. For example, instead of having a column with a list of phone numbers, you would create separate rows or a separate table for phone numbers. It also means you shouldn’t have repeated groups or columns that store the same type of information.
2. Building on 1NF, *Second Normal Form (2NF)* ensures that every column in the table is fully dependent on the entire primary key—not just part of it. This is important when the primary key consists of more than one column (a composite key). For instance, in a table with order details where the key is a combination of order ID and product ID, every other column should relate to both the order and the product. If some data applies only to the order, you would move it to a separate table.
3. *Third Normal Form (3NF)* goes further by making sure that every non-key column depends only on the primary key, not on any other non-key column. This prevents situations where one piece of data indirectly determines another. For example, if a table has a column for city and another for state, and the state can be determined from the city, then state should be stored in a different table or handled separately, ensuring each piece of information is directly linked to the primary key.
4. *Boyce-Codd Normal Form (BCNF)* is a stricter version of 3NF. It deals with issues that may arise from the way columns determine each other (functional dependencies). In a BCNF table, whenever one set of columns determines another set, that set must be a candidate key (unique for every row). This approach helps eliminate any odd cases where the data structure might allow unexpected duplication or inconsistency.
5. *Fourth Normal Form (4NF)* focuses on tables that might contain two or more independent one-to-many relationships. In simple terms, if a table has columns that can each have multiple values independently (such as a person’s hobbies and skills), these should be split into separate tables. This separation keeps the data clean and avoids duplicate rows with repeating groups of information.
6. *Fifth Normal Form (5NF)* also known as Project-Join Normal Form, 5NF aims to remove redundancy that might occur when joining several tables together. It ensures that complex relationships between data are broken into the simplest parts without losing any essential links. For example, if a table can be split into several smaller tables that can perfectly recreate the original data through joins, then the design meets 5NF.
7. *Sixth Normal Form (6NF)* is used mainly for databases that track changes over time (temporal databases). It involves breaking tables into even smaller parts so that each record represents a single point in time. This structure makes it easier to manage historical data and understand how information has changed over time without mixing data from different time periods in one record.
8. *Domain/Key Normal Form (DKNF)* represents the highest level of normalization. It ensures that every rule (or constraint) in the database comes directly from the definitions of keys and the allowed values (domains) for each column. Although it is an ideal approach, it is often very difficult to achieve in practice because it requires all business rules to be captured through keys and domains. As a result, DKNF is more of a theoretical goal than something most practical systems fully implement.

### First Normal Form (1NF)

The first normal form sets the foundation for normalization. A table is in 1NF if it meets the following criteria:

- It has a primary key that uniquely identifies each row.
- Each column contains atomic, indivisible values.
- Column names are unique, and data types are consistent.
- There are no duplicate rows.

For example, consider a table of students and their subjects:

| StudentID | Subject           |
|-----------|-------------------|
| 1         | Math, Science     |
| 2         | English, History  |
| 3         | Art, Music        |

This table violates 1NF because the 'Subject' column contains multiple values. To conform to 1NF, the table should be restructured so that each cell contains only one value:

| StudentID | Subject  |
|-----------|----------|
| 1         | Math     |
| 1         | Science  |
| 2         | English  |
| 2         | History  |
| 3         | Art      |
| 3         | Music    |

Now, each record is unique, and each cell contains a single value, satisfying the requirements of 1NF.

### Second Normal Form (2NF)

Advancing to the second normal form involves ensuring that every non-prime attribute is fully functionally dependent on the entire primary key. A table in 2NF must:

- Be in 1NF.
- Have no partial dependencies; non-key attributes cannot depend on only part of a composite primary key.

Consider the following table:

| StudentID | Subject | Teacher |
|-----------|---------|---------|
| 1         | Math    | Mr. A   |
| 1         | Science | Ms. B   |
| 2         | English | Ms. C   |
| 2         | History | Mr. D   |
| 3         | Art     | Mr. E   |
| 3         | Music   | Ms. F   |

Here, 'Teacher' depends only on 'Subject', not on the composite key of 'StudentID' and 'Subject'. To achieve 2NF, the table should be split:

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

| Subject  | Teacher |
|----------|---------|
| Math     | Mr. A   |
| Science  | Ms. B   |
| English  | Ms. C   |
| History  | Mr. D   |
| Art      | Mr. E   |
| Music    | Ms. F   |

By separating the tables, each non-key attribute depends on the whole primary key, satisfying 2NF.

### Third Normal Form (3NF)

The third normal form eliminates transitive dependencies, ensuring that non-key columns are dependent only on the primary key. A table is in 3NF if it:

- Is in 2NF.
- Has no transitive functional dependencies.

Consider the following table:

| StudentID | Course   | CourseLeader | LeaderPhone |
|-----------|----------|--------------|-------------|
| 1         | Math     | Mr. A        | 1234567890  |
| 2         | English  | Ms. B        | 0987654321  |
| 3         | Art      | Mr. C        | 1122334455  |

Here, 'LeaderPhone' is dependent on 'CourseLeader', which is dependent on 'Course', introducing a transitive dependency through 'CourseLeader'. To achieve 3NF, the table should be divided:

**Student_Course Table**

| StudentID | Course   | CourseLeader |
|-----------|----------|--------------|
| 1         | Math     | Mr. A        |
| 2         | English  | Ms. B        |
| 3         | Art      | Mr. C        |

**Leader_Contact Table**

| CourseLeader | LeaderPhone |
|--------------|-------------|
| Mr. A        | 1234567890  |
| Ms. B        | 0987654321  |
| Mr. C        | 1122334455  |

This separation removes the transitive dependency, placing the table in 3NF.

### Boyce-Codd Normal Form (BCNF)

The Boyce-Codd Normal Form is a stricter version of 3NF. A table is in BCNF if:

- It is in 3NF.
- For every functional dependency X → Y, X is a superkey.

BCNF addresses anomalies that 3NF doesn't cover. Consider the table:

| EmployeeID | Project  | Department | DepartmentHead |
|------------|----------|------------|----------------|
| 1          | ProjectA | Dept1      | Mr. A          |
| 2          | ProjectB | Dept1      | Mr. A          |
| 3          | ProjectC | Dept2      | Ms. B          |

In this table, 'DepartmentHead' depends on 'Department', not on the primary key 'EmployeeID' and 'Project'. 'Department' is not a superkey, violating BCNF. To correct this, split the table:

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

Now, every determinant is a candidate key, satisfying BCNF.

### Fourth Normal Form (4NF)

Fourth Normal Form deals with multi-valued dependencies. A table is in 4NF if:

- It is in BCNF.
- It has no multi-valued dependencies.

Multi-valued dependencies occur when one attribute in a table depends on multiple independent attributes. For example:

| EmployeeID | Skill    | Hobby     |
|------------|----------|-----------|
| 1          | Coding   | Football  |
| 1          | Design   | Football  |
| 2          | Design   | Music     |

Here, 'Skill' and 'Hobby' are independent of each other but depend on 'EmployeeID'. To achieve 4NF, split the table:

**Employee_Skill Table**

| EmployeeID | Skill    |
|------------|----------|
| 1          | Coding   |
| 1          | Design   |
| 2          | Design   |

**Employee_Hobby Table**

| EmployeeID | Hobby     |
|------------|-----------|
| 1          | Football  |
| 2          | Music     |

This removes the multi-valued dependencies, placing the tables in 4NF.

### Fifth Normal Form (5NF)

Fifth Normal Form, or Project-Join Normal Form, addresses cases where information can be reconstructed from smaller pieces. A table is in 5NF if:

- It is in 4NF.
- Every join dependency in the table is implied by the candidate keys.

Consider a table involving suppliers, parts, and projects:

| Supplier | Part | Project |
|----------|------|---------|
| S1       | P1   | J1      |
| S1       | P2   | J1      |
| S2       | P1   | J2      |
| S2       | P3   | J2      |
| S3       | P1   | J3      |

This table represents multiple relationships that can be decomposed:

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

By decomposing the original table, we eliminate redundancy and ensure that the join dependencies are maintained, achieving 5NF.

### Sixth Normal Form (6NF)

Although not mentioned earlier, the sixth normal form is mainly used in databases that handle historical or time-variant data. A table is in 6NF if it satisfies no non-trivial join dependencies at all—that is, the table cannot be decomposed any further. This form is particularly useful in data warehousing and complex data analysis.
