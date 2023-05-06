## Database normalization

Database normalization is a process used to efficiently organize a relational database by minimizing redundancy and ensuring data integrity. Normalization deals with the problem of having the same data in multiple cells, which can cause issues with updating (requiring updates to all occurrences), deletion (losing information about a client when deleting orders), and insertion (needing an order to insert a client). The solution is decomposition, which means splitting the data into multiple tables. 

## Objectives of Normalization

### Eliminate redundancy

Minimize duplicate data within tables to conserve storage space and enhance performance. Each fact stored in the database should be expressible in only one way.

### Ensure data integrity

Preserve consistency and accuracy of data by enforcing rules and constraints. The normalization process can be treated as a process in which relation schemas with certain undesirable characteristics are decomposed into smaller relation schemas with desired properties.

### Simplify the database design

Decompose complex tables into smaller, more manageable ones, making it easier to maintain and query the data.

## Normal Forms

Normalization is accomplished through a series of progressive normal forms, each addressing specific issues related to redundancy and data integrity. The following sections provide example tables for each normal form.

### First Normal Form (1NF)

- Each column must contain atomic values (i.e., indivisible values).
- Each column must have a unique name.
- The order of rows and columns is irrelevant.

Example table:
| Order_ID | Customer_Name     | Products         |
|----------|-------------------|------------------|
| 1        | John Doe          | {TV, Headphones} |
| 2        | Jane Smith        | {Laptop, Phone}  |

1NF solution:
| Order_ID | Customer_Name |
|----------|---------------|
| 1        | John Doe      |
| 2        | Jane Smith    |

| Order_ID | Product      |
|----------|--------------|
| 1        | TV           |
| 1        | Headphones   |
| 2        | Laptop       |
| 2        | Phone        |

### Second Normal Form (2NF)

- The table must be in 1NF.
- All non-key columns must be fully dependent on the primary key (i.e., no partial dependencies).

Example table:
| Order_ID | Product_ID | Customer_Name | Product_Price |
|----------|------------|---------------|---------------|
| 1        | 101        | John Doe      | 1200          |
| 1        | 102        | John Doe      | 300           |
| 2        | 103        | Jane Smith    | 800           |
| 2        | 104        | Jane Smith    | 1000          |

2NF solution:
| Order_ID | Customer_Name |
|----------|---------------|
| 1        | John Doe      |
| 2        | Jane Smith    |

| Order_ID | Product_ID | Product_Price |
|----------|------------|---------------|
| 1        | 101        | 1200          |
| 1        | 102        | 300           |
| 2        | 103        | 800           |
| 2        | 104        | 1000          |

### Third Normal Form (3NF)

- The table must be in 2NF.
- All non-key columns must be directly dependent on the primary key (i.e., no transitive dependencies).

Example table:
| Student_ID | Student_Name | Course_ID | Course_Name |
|------------|--------------|-----------|-------------|
| 1          | Alice        | C1        | Math        |
| 2          | Bob          | C1        | Math        |
| 3          | Carol        | C2        | Science     |

3NF solution:
| Student_ID | Student_Name | Course_ID |
|------------|--------------|-----------|
| 1          | Alice        | C1        |
| 2          | Bob          | C1        |
| 3          | Carol        | C2        |

| Course_ID | Course_Name |
|-----------|-------------|
| C1        | Math        |
| C2        | Science     |

### Boyce-Codd Normal Form (BCNF)

- The table must be in 3NF.
- Every determinant (i.e., a column or set of columns that determines the value of another column) must be a candidate key.

| Employee_ID | Department_ID | Department_Name | Department_Head |
|-------------|---------------|-----------------|-----------------|
| 1           | D1            | HR              | Susan           |
| 2           | D1            | HR              | Susan           |
| 3           | D2            | IT              | Robert          |

BCNF solution:
| Employee_ID | Department_ID |
|-------------|---------------|
| 1           | D1            |
| 2           | D1            |
| 3           | D2            |

| Department_ID | Department_Name | Department_Head |
|---------------|-----------------|-----------------|
| D1            | HR              | Susan           |
| D2            | IT              | Robert          |

### Fourth Normal Form (4NF)

- The table must be in BCNF.
- There should be no multi-valued dependencies.

Example table:
| Student_ID | Course_ID | Course_Name | Professor |
|------------|-----------|-------------|-----------|
| 1          | C1        | Math        | Mr. X     |
| 1          | C2        | Science     | Mr. Y     |
| 1          | C3        | History     | Mr. Z     |
| 2          | C1        | Math        | Mr. X     |
| 2          | C2        | Science     | Mr. Y     |

4NF solution:
| Student_ID | Course_ID |
|------------|-----------|
| 1          | C1        |
| 1          | C2        |
| 1          | C3        |
| 2          | C1        |
| 2          | C2        |

| Course_ID | Course_Name | Professor |
|-----------|-------------|-----------|
| C1        | Math        | Mr. X     |
| C2        | Science     | Mr. Y     |
| C3        | History     | Mr. Z     |

### Fifth Normal Form (5NF)

- The table must be in 4NF.
- There should be no join dependencies that are not implied by the candidate keys.

Example table:
| Supplier_ID | Supplier_Name | Part_ID | Part_Name | Shipment_Date |
|-------------|---------------|---------|-----------|---------------|
| S1          | Acme Corp     | P1      | Widget    | 2023-05-01    |
| S1          | Acme Corp     | P2      | Gizmo     | 2023-05-02    |
| S2          | Mega Inc      | P1      | Widget    | 2023-05-03    |
| S2          | Mega Inc      | P3      | Thingy    | 2023-05-04    |

5NF solution:
| Supplier_ID | Supplier_Name |
|-------------|---------------|
| S1          | Acme Corp     |
| S2          | Mega Inc      |

| Part_ID | Part_Name |
|---------|-----------|
| P1      | Widget    |
| P2      | Gizmo     |
| P3      | Thingy    |

| Supplier_ID | Part_ID | Shipment_Date |
|-------------|---------|---------------|
| S1          | P1      | 2023-05-01    |
| S1          | P2      | 2023-05-02    |
| S2          | P1      | 2023-05-03    |
| S2          | P3      | 2023-05-04    |

## Denormalization

In some instances, denormalizing the database to improve performance may be necessary. Denormalization involves reintroducing redundant data into the database to reduce the complexity of queries and decrease response times. This should be done cautiously, considering the trade-offs between performance and data integrity.
