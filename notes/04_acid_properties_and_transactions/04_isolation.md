## Isolation

Isolation is one of the ACID properties of database transactions, ensuring that the intermediate results of a transaction are not visible to other concurrently executing transactions.

## Importance of Isolation

### Concurrency Control
Isolation is crucial for managing concurrent access to the database, preventing conflicts and data inconsistencies that may arise when multiple transactions attempt to read or modify the same data simultaneously.
    
### Data Integrity
By ensuring isolation, the database can maintain data integrity and consistency even in highly concurrent environments.

## Examples

### Preventing Dirty Reads

- **Scenario**: A transaction T1 in a banking application transfers $100 from account A to B, involving two steps: (a) withdraw $100 from A, and (b) deposit $100 into B.
- **Without Isolation**: A concurrent transaction T2 may read A's balance after step (a) but before (b), leading to an inaccurate balance reading.
- **With Isolation**: T2 only accesses the final results of T1, ensuring accuracy in the balance reading.

### Avoiding Non-Repeatable Reads

- **Scenario**: In an inventory system, transaction T1 reads a product's stock level, computes the new level based on a sales order, and updates it.
- **Without Isolation**: A concurrent transaction T2 may modify the stock level, causing T1 to read different stock levels in the same transaction.
- **With Isolation**: T1 sees a consistent stock level, ensuring accurate calculations.

## Transaction Isolation Levels

Transaction isolation levels balance the trade-off between isolation and performance. Higher isolation levels provide greater consistency but may result in decreased concurrency and increased contention.

| Isolation Level   | Definition                                                   | Pros                                   | Cons                                         | Example                                                                                   |
|-------------------|--------------------------------------------------------------|----------------------------------------|----------------------------------------------|-------------------------------------------------------------------------------------------|
| Read Uncommitted  | Can read data modified by uncommitted transactions.          | High concurrency.                      | May lead to dirty reads.                     | Reading an intermediate state during a money transfer can lead to incorrect balances.     |
| Read Committed    | Can only read data committed before the start of transaction.| Avoids dirty reads, Good concurrency.  | May lead to non-repeatable reads.            | Reading a bank account's balance may show different values within the same transaction.  |
| Repeatable Read   | Same value is returned for multiple reads within a transaction.| Avoids non-repeatable reads.          | May lead to phantom reads, Lower concurrency.| Reading a list of bank accounts may miss new accounts added by another transaction.      |
| Serializable      | Complete isolation from other transactions.                  | Avoids phantom reads, Strong consistency. | Lowest concurrency, can lead to contention. | Calculating total balance across all accounts ensures no modifications until complete.   |

## Concurrency Control Mechanisms

### Locking Mechanisms

- **Description**: Locking prevents concurrent access to data by restricting data access to one transaction at a time.
- **Types**:
  - **Row-level Locking**: Locks are applied to specific rows.
  - **Table-level Locking**: Locks are applied to entire tables.
- **Role in Isolation**: Locking mechanisms prevent data inconsistencies by serializing access to data.

### Optimistic Concurrency Control

- **Description**: This approach permits transactions to execute without locks, validating data at commit time to ensure no conflicts.
- **How it Works**: Transactions read data, perform operations, and then check for conflicts at commit time. If conflicts are found, the transaction may be rolled back.
- **Role in Isolation**: By detecting and resolving conflicts at commit time, optimistic concurrency control ensures isolation without the overhead of locking.

