## Durability
Durability is one of the ACID properties of database transactions, ensuring that once a transaction is committed, its effects are permanent and can survive system failures.

## Importance of Durability

### Data Persistence
Durability makes sure that committed transactions are not lost even during system failures, which guarantees data preservation and reliability.
    
### System Recovery
With durability in place, the database system can bounce back from failures by replaying committed transactions and restoring the database to a consistent state.
    
## Examples

### E-commerce Order Example

1. In an online shopping scenario, a transaction may involve creating a new order record and updating inventory levels for the items purchased.

2. As soon as the transaction is committed, durability ensures that the order record and inventory updates are permanently stored in the database, even if the system crashes right after the commit.

3. When the system recovers, the committed order and inventory updates remain in the database, preserving data integrity and consistency.

### Financial Transaction Example

1. In a financial system, a transaction might involve transferring funds between two accounts by debiting one account and crediting the other.

2. Durability ensures that once the transaction is committed, the changes made to both accounts are permanent and won't be lost, even in the event of a system failure.

3. When the system recovers, the results of the committed transaction are still present in the database, guaranteeing that no funds are lost or inaccurately accounted for.

## Techniques for Ensuring Durability

### Write-Ahead Logging (WAL)
WAL is a method that guarantees durability by recording transaction logs to persistent storage before the actual data changes are written to the database. In the event of a system failure, the transaction logs can be replayed to recover the committed transactions.
    
### Checkpoints
Checkpoints consist of periodically transferring modified data from memory to disk, making sure that committed transactions are stored durably and minimizing the amount of data that needs to be recovered in case of a failure.
    
### Replication
Replication entails keeping multiple copies of data across various nodes or storage systems, which enhances durability and fault tolerance in case of a failure.
    
