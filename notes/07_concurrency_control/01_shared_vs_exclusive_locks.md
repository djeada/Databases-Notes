## Shared and Exclusive Locks

Shared and exclusive locks are crucial in database systems for managing concurrent access to data. They ensure that transactions occur without conflicting with each other, maintaining the integrity and consistency of the database.

```
Illustration of Lock Types:

[Resource: Data Item X]
   |
   |-- Transaction A wants to READ --> Acquires SHARED LOCK
   |-- Transaction B wants to READ --> Acquires SHARED LOCK
   |
[Both can read simultaneously]

[Resource: Data Item Y]
   |
   |-- Transaction C wants to WRITE --> Acquires EXCLUSIVE LOCK
   |
[No other transaction can read or write until the lock is released]
```

In the diagram above, Transactions A and B both acquire shared locks on Data Item X, allowing them to read the data at the same time without interference. Transaction C, however, obtains an exclusive lock on Data Item Y to perform a write operation, preventing other transactions from accessing it until the operation is complete.

After reading the material, you should be able to answer the following questions:

1. What are shared and exclusive locks in database systems, and how do they differ in terms of access permissions for transactions?
2. How do shared and exclusive locks interact with each other, and what does the lock compatibility matrix illustrate about their behavior?
3. Can you provide examples of scenarios where shared locks are appropriate and where exclusive locks are necessary to maintain data integrity?
4. What best practices can be followed to balance concurrency and data integrity when using shared and exclusive locks in transactions?
5. How do deadlocks occur in the context of shared and exclusive locks, and what strategies can be implemented to prevent and resolve them?

### Understanding Shared Locks

Shared locks allow multiple transactions to read the same data concurrently. They are vital for operations where data needs to be read without being modified, ensuring that the data remains consistent for all reading transactions.

Imagine a library database where several users are looking up the same book information. Each user's transaction places a shared lock on the book's data, allowing everyone to read the information simultaneously without any conflicts.

### Exploring Exclusive Locks

Exclusive locks grant a single transaction the sole right to read and modify a piece of data. This lock type is necessary when a transaction needs to ensure that no other transactions can interfere with its operation, such as when updating or deleting data.

Consider an online banking system where a user is transferring money from one account to another. The transaction places an exclusive lock on both account records to prevent other transactions from reading or modifying the balances until the transfer is complete, ensuring the accuracy of the transaction.

### Interaction Between Shared and Exclusive Locks

Understanding how shared and exclusive locks interact is essential for managing database concurrency effectively.

| Lock Held \ Requested   | Shared Lock Requested | Exclusive Lock Requested |
| ----------------------- | --------------------- | ------------------------ |
| **Shared Lock Held**    | Allowed               | Not Allowed              |
| **Exclusive Lock Held** | Not Allowed           | Not Allowed              |

- When a shared lock is already held on a data item, other transactions can also acquire shared locks on it.
- If a shared lock is held, an exclusive lock request will be blocked until all shared locks are released.
- When an exclusive lock is held, all other lock requests (shared or exclusive) are blocked until the exclusive lock is released.

### Practical Examples with Commands

These examples illustrate row-level locking behavior common to most modern relational databases—**PostgreSQL**, **MySQL/InnoDB**, **MariaDB**, **SQL Server**, and **Oracle**—which support shared (S) and exclusive (X) locks at the row level. They do **not** apply to engines or table types without row-level locking (e.g., MySQL’s **MyISAM**), nor to NoSQL stores that use different concurrency controls.

#### Shared vs. Exclusive Locks: Applicability

* **Supported**: PostgreSQL, MySQL/InnoDB, MariaDB, SQL Server, Oracle.
* **Not Supported**: MySQL/MyISAM (table-level only), SQLite (uses database-level or page-level locks), many cloud-managed NoSQL databases.

Locking behavior may vary slightly by isolation level and vendor syntax; the following examples assume the default **READ COMMITTED** isolation level.

#### Example: Reading Data (Shared Lock)

In databases with row-level locking, a **shared lock** (S) permits multiple transactions to read the same rows concurrently but prevents any transaction from modifying them until all shared locks are released.

```sql
-- Applies in PostgreSQL, MySQL/InnoDB, SQL Server, Oracle
BEGIN TRANSACTION;
SELECT * FROM Employees WHERE Department = 'Sales';
-- Shared (S) lock on matching rows until COMMIT
COMMIT;
```

#### Example: Updating Data (Exclusive Lock)

An **exclusive lock** (X) is required for row modifications. If another transaction holds a shared or exclusive lock on the same row, the update waits (or may deadlock under certain patterns).

```sql
-- Applies in PostgreSQL, MySQL/InnoDB, SQL Server, Oracle
BEGIN TRANSACTION;
UPDATE Employees SET Salary = Salary * 1.05 WHERE Department = 'Sales';
-- Request X lock: waits until no other S or X locks exist on those rows
COMMIT;
```

#### Lock Interaction Timeline

| Step | Transaction  | Action                            | Lock Held                | Outcome                                          |
| ---- | ------------ | --------------------------------- | ------------------------ | ------------------------------------------------ |
| 1    | T1 (Reader)  | `SELECT ... FOR SHARE` (implicit) | S on Sales rows          | Allows other S locks; blocks X locks             |
| 2    | T2 (Updater) | `UPDATE ...`                      | Requests X on Sales rows | Waits until T1 commits and releases its S lock   |
| 3    | T1           | `COMMIT`                          | Releases S               | T2 acquires X lock, performs update, then COMMIT |

> **Note**: Some databases (e.g., Oracle) require explicit `SELECT ... FOR UPDATE` to acquire row locks for reads; others implicitly lock on `UPDATE`.

#### Considerations and Variations

* Under **SERIALIZABLE**, readers may acquire additional locks or trigger predicate locks. Under **READ UNCOMMITTED**, shared locks may be skipped (dirty reads).
* MyISAM uses table-level locks, so the above does not apply. SQLite uses page or database locks.
* If two transactions request locks in opposite order, a deadlock may occur. Most RDBMS detect and kill the victim.

### Balancing Concurrency and Integrity

Efficient database systems strive to balance the need for high concurrency with the necessity of maintaining data integrity. Locks play a pivotal role in achieving this balance. Here are the key concepts:

- Shared locks enable multiple transactions to **read the same data simultaneously**, enhancing concurrency and system throughput.  
- Exclusive locks restrict access to a resource for modifications, ensuring **data integrity** by preventing conflicts and data corruption during concurrent updates.  
- Locking mechanisms must be carefully managed to avoid **deadlocks**, where two or more transactions wait indefinitely for each other to release locks.  
- Transaction isolation levels, such as **serializable** and **read committed**, provide a framework for managing concurrency while maintaining data consistency.

### Best Practices for Using Locks

To optimize database performance while ensuring data integrity, the following practices are recommended:

- Transactions should be designed to **minimize the duration of locks** by keeping operations concise, reducing contention and blocking of other processes.  
- Lock granularity should be chosen carefully, with **row-level locks** preferred over table-level locks for fine-grained control, promoting greater concurrency.  
- Avoiding unnecessary locks helps reduce overhead; for instance, adopting a **read-uncommitted isolation level** can be beneficial in scenarios where occasional dirty reads are acceptable.  
- Deadlock detection and resolution mechanisms should be implemented to **automatically identify and address circular locking scenarios**, ensuring system stability.  
- Prioritize using **optimistic concurrency control** techniques, such as timestamp-based validation, in read-heavy systems to reduce locking frequency.  
- Regularly monitor and analyze transaction logs to **identify bottlenecks and locking conflicts**, enabling proactive adjustments to database configuration or schema.  
- Employ **indexing strategies** to limit the range of locks required, as properly indexed queries reduce the amount of data scanned and locked.  

### Deadlocks and How to Handle Them

Deadlocks occur when two or more transactions are waiting indefinitely for each other to release locks.

```
Deadlock Scenario:

Transaction 1:
   LOCK Resource A
   WAIT for Resource B

Transaction 2:
   LOCK Resource B
   WAIT for Resource A
```

In this situation, Transaction 1 holds a lock on Resource A and waits for Resource B, while Transaction 2 holds a lock on Resource B and waits for Resource A. Neither can proceed, resulting in a deadlock.

**Strategies to Prevent Deadlocks:**

- Establishing **resource ordering** ensures that locks are acquired in a consistent sequence, which prevents circular wait conditions from arising.  
- Setting a **lock timeout** allows transactions to fail gracefully by limiting the maximum time a lock request can wait, avoiding indefinite blocking.  
- Implementing **deadlock detection** systems enables the identification of deadlock situations, allowing resolution by aborting one of the conflicting transactions.  
- Using a **wait-die or wound-wait algorithm** enforces a structured priority-based approach to manage transactions and prevent deadlocks.  
- Designing transactions to **lock resources in bulk** at the beginning reduces the chances of mid-transaction lock conflicts, which can trigger deadlocks.  
- Minimizing **long-running transactions** reduces the risk of lock contention, as shorter transactions are less likely to encounter deadlock situations.  
- Optimizing **index usage** and query design decreases the number of locks required, reducing the probability of lock-related conflicts.  
- Regularly reviewing and analyzing **deadlock logs** aids in understanding the root causes and refining locking strategies accordingly.  
