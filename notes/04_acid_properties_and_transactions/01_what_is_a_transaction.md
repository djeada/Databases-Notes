## What is a transaction?

A database transaction consists of a series of operations, such as inserting, updating, or deleting data, which are executed as a single unit of work. Transactions play a crucial role in preserving database consistency and integrity while managing concurrent access.

## ACID Properties

Transactions are defined by their ACID properties, ensuring database consistency even when multiple transactions are executed simultaneously.

### Atomicity
A transaction is atomic, meaning it either fully completes or does not occur at all. If any part of the transaction fails, the entire transaction is rolled back, and the database reverts to its state before the transaction began.
    
### Consistency
A transaction guarantees that the database transitions from one consistent state to another. Consistency rules, such as primary key and foreign key constraints, must be upheld throughout the transaction.
    
### Isolation
Transactions are isolated from each other, ensuring that the intermediate results of one transaction remain invisible to other transactions. This prevents conflicts and creates the illusion that each transaction is executed sequentially, despite potential concurrency.
    
### Durability
Once a transaction is committed, its changes to the database become permanent. The system must safeguard committed data against loss due to crashes or system failures.
    
## Transaction Management

Transaction management involves coordinating and controlling transactions to maintain their ACID properties.

### Begin Transaction
A transaction starts with the "begin transaction" operation, which establishes the starting point for the series of operations.

### Commit
When all the operations within a transaction execute successfully, the transaction is committed, and the changes are permanently stored in the database.

### Rollback
If an operation within the transaction fails, or the user decides to cancel the transaction, a rollback is initiated, undoing all changes made by the transaction.

### Concurrency Control
Concurrency control mechanisms, such as locking and optimistic concurrency, manage simultaneous access to the database and prevent conflicts between transactions.

## Transaction Isolation Levels

Transaction isolation levels balance the trade-off between isolation and performance. Higher isolation levels provide greater consistency but may result in decreased concurrency and increased contention.

1. Read Uncommitted
2. Read Committed
3. Repeatable Read
4. Serializable
