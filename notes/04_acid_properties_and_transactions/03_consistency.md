## Consistency

Consistency is one of the ACID properties of database transactions, ensuring that the database remains in a consistent state before and after the transaction. This note delves into the concept of consistency, its significance in preserving data integrity, and examples that illustrate its importance.

## Importance of Consistency

### Data Integrity
Consistency ensures that the data in the database adheres to predefined rules and constraints, preventing data anomalies and maintaining data accuracy.

### Error Prevention
By enforcing consistency, the database system can detect and prevent potential errors or conflicts that could lead to an inconsistent state.

## Real-world Examples

### Upholding Unique Constraints

- **Scenario**: In an e-commerce platform, every user must possess a unique email address.
- **Application**: The database enforces a unique constraint on the email column in the users table.
- **Outcome**: When a user attempts to register with an already-existing email, the unique constraint ensures consistency by disallowing duplicate entries.

### Adhering to Foreign Key Constraints

- **Scenario**: An online ticket booking system creates a booking record for a customer and updates available seats for an event. The booking record references the event using a foreign key.
- **Application**: Consistency mandates adherence to the foreign key constraint, validating that every booking corresponds to a legitimate event.
- **Outcome**: If a booking attempt is made for an invalid event, the foreign key constraint prevents the transaction, thereby upholding consistency.

### Enforcing Domain Constraints

- **Scenario**: A payroll system restricts the salary values within the employees table to positive numbers using domain constraints.
- **Application**: Consistency ensures that any transaction aiming to update the salary adheres to this constraint.
- **Outcome**: Transactions attempting to set a negative salary value are prevented, ensuring data integrity and consistency.

## Mechanisms for Ensuring Consistency

To maintain consistency in a database, several mechanisms and techniques are used to manage concurrent transactions and prevent conflicts. These mechanisms ensure that the database remains in a consistent state even when multiple operations are performed simultaneously.

### Transaction Isolation

- **Description**: Transaction isolation levels determine how the changes made by one transaction are visible to other concurrent transactions.
- **How it Works**:
  - **Read Uncommitted**: This level allows a transaction to read uncommitted changes made by another transaction, potentially leading to dirty reads.
  - **Read Committed**: A transaction may only read changes that have been committed, preventing dirty reads.
  - **Repeatable Read**: This level ensures that if a transaction reads a value, it sees the same value on subsequent reads. However, it may lead to phantom reads.
  - **Serializable**: This is the strictest level, preventing dirty, non-repeatable, and phantom reads by ensuring complete isolation from other transactions.
- **Role in Consistency**: By selecting an appropriate isolation level, a balance can be struck between performance and the risk of reading inconsistent data, thereby maintaining consistency as per the application's needs.

### Concurrency Control Techniques

#### Locking

- **Description**: Locking prevents multiple transactions from accessing the same data concurrently.
- **How it Works**:
  - **Shared Locks**: Multiple transactions can read a data item but cannot write to it.
  - **Exclusive Locks**: Only one transaction can write to a data item, and no other transaction can read or write to it concurrently.
- **Role in Consistency**: Locking ensures that no two transactions modify the same data simultaneously, thus preventing conflicts and maintaining data consistency.

#### Optimistic Concurrency Control (OCC)

- **Description**: OCC is based on the assumption that multiple transactions can complete without affecting each other.
- **How it Works**:
  - **Begin Transaction**: The transaction reads the data and performs operations without acquiring locks.
  - **Validation**: Before committing, the transaction checks if other transactions have modified the data it read or wrote.
  - **Commit/Rollback**: If no conflicts are detected, the transaction commits; otherwise, it rolls back and may retry.
- **Role in Consistency**: OCC allows for high concurrency and throughput while ensuring that data inconsistencies are detected and resolved before committing.

#### Multi-Version Concurrency Control (MVCC)

- **Description**: MVCC allows multiple versions of a data item to coexist, enabling smoother concurrent operations.
- **How it Works**:
  - Each transaction sees a snapshot of the database at a point in time and operates on that snapshot.
  - Conflicts are resolved at commit time, with the possibility of a transaction being rolled back if it cannot be serialized.
- **Role in Consistency**: MVCC ensures that read operations do not block write operations and vice versa, while still ensuring that the database remains consistent.

