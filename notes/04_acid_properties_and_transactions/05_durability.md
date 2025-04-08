## Durability in Database Transactions

Durability is a fundamental principle in database systems that ensures once a transaction has been committed, its effects are permanent and will survive any subsequent system failures. This means that the data changes made by a transaction are safely stored and can be recovered even if the system crashes or experiences a power loss immediately afterward.

Imagine that every time you save a file on your computer, you expect it to be there the next time you turn it on—even if there was an unexpected shutdown. Similarly, durability guarantees that committed transactions in a database are preserved, providing reliability and trust in the system.

Once a transaction is committed, its changes are permanently recorded, even in the event of a system failure or crash:

```
             +--------------------------+
             | Transaction Successfully |
             |      Committed           |
             |  (Changes Finalized)     |
             +------------+-------------+
                          |
                          v
             +--------------------------+
             |  Write-Ahead Log (WAL)   |
             | (Persistent Log Entry)   |
             +------------+-------------+
                          |
                          v
             +--------------------------+
             |   Persistent Storage     |
             |     (Disk / SSD)         |
             | (Data Remains Intact)    |
             +--------------------------+
```

- Once a transaction is successfully committed, its changes are considered final and should be immune to failures.
- Before changes are applied to the primary data storage, they are first recorded in a durable log. This ensures that if a system crash occurs, the database can recover by replaying the WAL.
- The changes are then written to durable storage (e.g., disk or SSD), guaranteeing that the transaction's effects remain, even if power is lost or the system crashes.

After reading the material, you should be able to answer the following questions:

1. What is durability in database transactions, and how does it ensure that committed transactions remain permanent even in the event of system failures?
2. Why is durability important for maintaining data integrity and reliability in database systems?
3. What are the key techniques used to ensure durability, such as Write-Ahead Logging (WAL), checkpointing, and data replication, and how do they work?
4. How does the Two-Phase Commit Protocol (2PC) contribute to durability in distributed database environments?
5. Can you provide real-world examples of scenarios where durability is essential, and explain how durability mechanisms protect data in those cases?

### The Importance of Durability

Durability plays a crucial role in maintaining the integrity and reliability of a database. By ensuring that committed transactions are not lost, it provides confidence that the data remains consistent and accurate over time.

#### Ensuring Data Persistence

Once a transaction is committed, durability guarantees that its changes are permanently recorded. This means that even in the face of hardware failures or system crashes, the data modifications are not lost and can be retrieved upon system recovery.

#### Facilitating System Recovery

In the event of a system failure, durability allows the database to recover to a consistent state by reapplying or confirming the committed transactions. This ensures that the database does not revert to an earlier state, preventing data loss and maintaining continuity.

### Real-World Examples

To better understand how durability impacts everyday applications, let's explore some scenarios where this property is essential.

#### Processing Online Orders

Consider an e-commerce platform where customers place orders and the system updates inventory levels accordingly.

- A customer completes a purchase, and the system commits the transaction that records the order details and adjusts the stock quantity.
- If a power outage occurs immediately after the transaction commits, the order information and updated inventory levels are preserved.
- When the system restarts, the customer's order is still recorded, and the inventory reflects the correct stock levels, ensuring accurate order fulfillment and inventory management.

#### Handling Bank Transactions

Imagine a banking system where funds are transferred between accounts.

- A transaction debits $1,000 from Account A and credits $1,000 to Account B.
- Once the transaction is committed, both accounts reflect the updated balances.
- If the system crashes right after the commit, upon recovery, the database still shows the debited and credited amounts, preserving the integrity of the financial records.

### Techniques for Ensuring Durability

Databases implement several mechanisms to guarantee that committed transactions remain durable, even in the face of unexpected failures.

#### Write-Ahead Logging (WAL)

Write-Ahead Logging is a method where changes are first recorded in a log before being applied to the database itself.

- Before any modifications are made to the database, the changes are written to a persistent log file. If a system failure occurs, the database can use this log to redo the transactions upon restart.
- This ensures that no committed transactions are lost, as the log provides a reliable record that can be used to restore the database to its correct state.

#### Checkpointing

Checkpointing involves periodically saving the current state of the database to stable storage.

- At certain intervals, the database writes all in-memory changes to disk, creating a consistent snapshot. This reduces recovery time because only transactions after the last checkpoint need to be reapplied.
- By minimizing the amount of data that needs to be recovered, checkpoints help the system return to normal operations more quickly after a failure.

#### Data Replication

Replication involves maintaining copies of the database on multiple servers or storage systems.

- Committed transactions are synchronized across different nodes or locations. If one server fails, another can take over, ensuring that the data remains accessible.
- Replication enhances durability by providing redundancy. Even in the event of hardware failure or data corruption on one server, the data remains safe and available on others.

Alright, here’s the upgraded and clarified version of **“Visualizing Durability Mechanisms”**, with added detail, clearer structure, real-world analogies, and concrete SQL/logging output. Tone stays direct and to-the-point, like a friend walking you through what’s actually happening under the hood.

### Visualizing Durability Mechanisms

**Durability** guarantees that once a transaction is committed, its results are permanent—even if the system crashes seconds later. If the database says, “Done,” it better mean it.

Let’s look at how that works behind the scenes:

```
[Start Transaction]
        |
[Write Changes to Log]
        |
[Apply Changes to Database]
        |
[Commit Transaction]
        |
[Durability Ensured]
```

Each step exists to protect your data from disappearing into the void. Here's how it plays out:

I. **Start Transaction**

At this point, nothing’s permanent. You’re just signaling that some changes are about to happen.

```sql
BEGIN;
```

II. **Write-Ahead Logging (WAL)**

Before the actual data is changed, all actions are recorded in a transaction log. This is critical. The log is stored on disk immediately.

```plaintext
LOG: UPDATE accounts SET balance = balance - 100 WHERE id = 1
LOG: UPDATE accounts SET balance = balance + 100 WHERE id = 2
```

If the system crashes *after* this point but *before* applying changes to the actual data, the recovery system will use the log to **redo** the transaction.

📝 **Why this matters:** Logging comes *before* any changes are made. That’s why it’s called *Write-Ahead Logging* (WAL).

III. **Apply Changes to the Database**

Now the actual tables are updated.

```sql
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
```

These changes happen in memory first. They’ll be flushed to disk shortly, but not necessarily immediately.

IV. **Commit Transaction**

This is the point of no return.

```sql
COMMIT;
```

The system writes a special *commit record* to the log. If that commit log entry exists, then the transaction is considered **durable**.

#### What Happens If There’s a Crash?

Imagine the system crashes **right after** the commit. What happens on recovery?

- The system reads the log.
- Sees the commit record.
- Replays all the changes (if necessary) to make sure the database reflects them.

Even if the data changes weren’t fully flushed to disk, the **log was**, and that’s enough to recover.

#### Analogy: Save Before You Close

Think of this like editing a document:
- You make changes.
- You hit **Ctrl+S** (which writes to the disk).
- Then you close the app.

Even if your laptop dies after closing, that save ensures your edits aren't lost. That’s durability.
