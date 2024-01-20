## Durability
Durability is one of the ACID properties of database transactions, ensuring that once a transaction is committed, its effects are permanent and can survive system failures.

```
+----------------+      +----------------+
| Committed      |      | System         |
| Transaction    |  ->  | Restart        |
| - Preserved    |      | - Preserved    |
+----------------+      +----------------+
   Permanent Change       Change Survives
```

## Importance of Durability

### Data Persistence
Durability makes sure that committed transactions are not lost even during system failures, which guarantees data preservation and reliability.
    
### System Recovery
With durability in place, the database system can bounce back from failures by replaying committed transactions and restoring the database to a consistent state.
    
## Examples

### E-commerce Order Persistence

- **Scenario**: A transaction creates a new order record and modifies inventory levels in an e-commerce platform.
- **Durability in Action**: Even if a system crash occurs immediately after the transaction is committed, durability ensures that the order and inventory updates are permanently stored.
- **Post-Recovery**: The system, upon recovery, retains the committed order and inventory changes, maintaining data integrity.

### Financial Transaction Safeguard

- **Scenario**: A financial transaction transfers funds between two accounts.
- **Durability in Action**: Durability ensures that the debiting and crediting actions are permanent and immune to system failures.
- **Post-Recovery**: The database, upon recovery, reflects the committed changes accurately, ensuring no loss or inconsistency in financial data.

## Techniques for Ensuring Durability

### Write-Ahead Logging (WAL)

- **Description**: WAL ensures durability by persistently logging transactions before executing data changes.
- **Working Principle**: Before changes are written to the database, the transaction logs are saved to persistent storage. In case of a failure, these logs can be replayed to recover the state.
- **Applicability**: WAL is a common technique used in database systems like PostgreSQL and SQLite.

### Checkpoints

- **Description**: Checkpoints involve periodically saving data from memory to disk.
- **Working Principle**: By regularly storing committed transactions on disk, checkpoints minimize data recovery time post-failure.
- **Applicability**: Checkpoints are a standard feature in many database systems.

### Replication

- **Description**: Replication enhances durability by maintaining multiple copies of data across different nodes or storage systems.
- **Working Principle**: By keeping redundant copies, the system ensures data availability and durability even when one node fails.
- **Applicability**: Replication is commonly used in distributed databases like Cassandra and MongoDB.

    
