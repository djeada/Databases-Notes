## What is a transaction?

A database transaction consists of a series of operations, such as inserting, updating, or deleting data, which are executed as a single unit of work. Transactions play a crucial role in preserving database consistency and integrity while managing concurrent access.

```
1. Initial State:
+------------------+          +------------------+
| Account A: $100  |          | Account B: $50   |
+------------------+          +------------------+

2. Transaction Start:
+------------------+            +------------------+
| Account A: $100 |    --$20->  | Account B: $50   |
+------------------+            +------------------+

3. Transaction End:
+------------------+          +------------------+
| Account A: $80   |          | Account B: $70   |
+------------------+          +------------------+
```

If any failure occurs during the transaction, the system should be able to rollback to the initial state.

## ACID Properties

Transactions are defined by their ACID properties, ensuring database consistency even when multiple transactions are executed simultaneously.

### Atomicity
A transaction is atomic, meaning it either fully completes or does not occur at all. If any part of the transaction fails, the entire transaction is rolled back, and the database reverts to its state before the transaction began.

```
+----------------+      +----------------+
| Transaction 1  |      | Transaction 1  |
| - Step 1       |      | - Step 1       |
| - Step 2       |  ->  | - Step 2       |
| - Step 3       |      | - Step 3       |
+----------------+      +----------------+
   All or Nothing           Fully Applied
```
    
### Consistency
A transaction guarantees that the database transitions from one consistent state to another. Consistency rules, such as primary key and foreign key constraints, must be upheld throughout the transaction.
  
```
+----------------+      +----------------+
| Before         |      | After          |
| - State A      |      | - State B      |
| - Valid        |  ->  | - Valid        |
+----------------+      +----------------+
   Consistent State        Consistent State
```
  
### Isolation
Transactions are isolated from each other, ensuring that the intermediate results of one transaction remain invisible to other transactions. This prevents conflicts and creates the illusion that each transaction is executed sequentially, despite potential concurrency.
    
```
+----------------+      +----------------+
| Transaction 1  |      | Transaction 2  |
| - Step 1       |      | - Step 1       |
| - Step 2       |  --  | - Step 2       |
+----------------+      +----------------+
   Independent             Independent
```

### Durability
Once a transaction is committed, its changes to the database become permanent. The system must safeguard committed data against loss due to crashes or system failures.

```
+----------------+      +----------------+
| Committed      |      | System         |
| Transaction    |  ->  | Restart        |
| - Preserved    |      | - Preserved    |
+----------------+      +----------------+
   Permanent Change       Change Survives
```

## Analogy of a post office

Once upon a time in a quaint little village, there was a diligent postman named Tom. Tom had the responsibility of ensuring that all letters sent from the village's post office reached their rightful recipients.

One day, Tom received a special request. A villager, Alice, wanted to send two letters: one to her friend Bob and another to her cousin Charlie. Tom knew that both letters were part of a surprise birthday plan and thus, both had to be delivered together or not at all.

Tom carefully prepared both letters, ensuring that if one letter couldn't be delivered (perhaps due to an incorrect address), neither would be sent out. This way, Alice's surprise would remain a secret until both friends could be told at the same time (ATOMICITY).

The post office had strict guidelines for sending letters. Each letter had to be stamped, sealed, and the address had to be correctly formatted. Tom meticulously checked Alice's letters to ensure they met all the criteria. If a letter was not properly stamped or sealed, it would not be sent.

Tom found that one of the letters didn't have a stamp. He knew he couldn't send them until they were both properly prepared, ensuring consistency in the process (CONSISTENCY).

Meanwhile, other villagers were also sending and receiving letters. Tom was juggling multiple deliveries and pickups, but he was careful to treat each task independently. Even if he was in the middle of preparing Alice's letters, when he switched to handle another villager's letters, he ensured that the tasks did not interfere with each other.

For instance, while preparing Alice's letters, he was also packaging a parcel for another villager, Dave. Even though Tom switched between tasks, Dave's parcel and Alice's letters were handled as if they were the only tasks in the world, unaffected by each other (ISOLATION).

Finally, after ensuring that both of Alice's letters were stamped, sealed, and addressed correctly, Tom sent them out for delivery. Once the letters were on their way, Tom knew that the task was irreversible and permanent. Even if a storm came or his bicycle broke down, the post office guaranteed that the letters would reach Bob and Charlie. The commitment was durable and reliable (DURABILITY).
    
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
