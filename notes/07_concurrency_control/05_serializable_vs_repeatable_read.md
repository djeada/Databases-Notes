## Serializable and Repeatable Read in Database Systems

Transaction isolation levels are essential for maintaining data integrity and managing concurrency in database systems. Two of the highest isolation levels are **Serializable** and **Repeatable Read**, each offering different guarantees to prevent anomalies that can occur when multiple transactions interact with the same data concurrently.

After reading the material, you should be able to answer the following questions:

1. What is the Serializable isolation level, and how does it ensure complete isolation of transactions in a database system?
2. How does the Repeatable Read isolation level differ from Serializable, and what types of data anomalies does it prevent?
3. In what scenarios would you choose to use Serializable isolation over Repeatable Read, and why?
4. What are phantom reads, and how does the Serializable isolation level prevent them compared to Repeatable Read?
5. What are the performance implications of using higher isolation levels like Serializable, and how can applications balance consistency with system performance?

### The Need for Isolation Levels

In environments where multiple transactions execute at the same time, issues like dirty reads, non-repeatable reads, and phantom reads can arise. Without proper isolation, one transaction might read data that another transaction is modifying, leading to inconsistent or incorrect results. Isolation levels define how transactions are isolated from one another to prevent these problems.

### Serializable Isolation Level

The Serializable isolation level is the strictest level, ensuring that transactions are completely isolated from each other. It guarantees that the outcome of executing transactions concurrently is the same as if they were executed sequentially in some order.

| Time | Transaction T1                                                                 | Transaction T2                                                                             |
|------|--------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------|
| T1   | **BEGIN TRANSACTION**<br>SELECT SUM(balance) FROM accounts; <br> _(Total = \$10,000)_ |                                                                                           |
| T2   |                                                                                 | **BEGIN TRANSACTION**<br>INSERT INTO accounts (id, balance) <br>VALUES (101, \$1,000);       |
| T3   |                                                                                 | _(Blocked: waiting for T1 to complete)_                                                   |
| T4   | **COMMIT**                                                                      |                                                                                           |
| T5   |                                                                                 | _(Unblocked)_ INSERT completes<br>**COMMIT**                                              |

In this scenario:

- **Transaction T1** calculates the total balance of all accounts.
- **Transaction T2** attempts to insert a new account but is blocked until T1 commits.
- T1's calculation does not include the new account from T2, ensuring a consistent view of the data.
- T2 proceeds only after T1 has finished, maintaining serializability.

### Repeatable Read Isolation Level

The Repeatable Read isolation level ensures that if a transaction reads a row, it will see the same data throughout the transaction, even if other transactions modify it. However, it doesn't prevent new rows (phantoms) from being inserted by other transactions.

| Time | Transaction T1                                                                 | Transaction T2                                                                                      |
| ---- | ------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------|
| T1   | **BEGIN TRANSACTION**<br>SELECT * FROM orders WHERE customer_id = 1;<br>_(Returns 5 rows)_ |                                                                                                     |
| T2   |                                                                                 | **BEGIN TRANSACTION**<br>INSERT INTO orders (order_id, customer_id) VALUES (101, 1);<br>**COMMIT** |
| T3   | SELECT * FROM orders WHERE customer_id = 1;<br>_(Returns 5 rows)_                |                                                                                                     |
| T4   | **COMMIT**                                                                      |                                                                                                     |


In this example:

- **Transaction T1** reads all orders for customer 1 and gets 5 rows.
- **Transaction T2** inserts a new order for customer 1 and commits.
- When T1 reads the orders again, it still sees only the original 5 rows.
- T1 is unaware of the new order inserted by T2 during its transaction.

### Comparing Serializable and Repeatable Read

Both isolation levels aim to maintain data consistency but differ in their handling of concurrent transactions and the types of anomalies they prevent.

**Serializable Isolation Level:**

- Prevents **dirty reads**, **non-repeatable reads**, and **phantom reads**.
- Ensures complete isolation by serializing transactions.
- May lead to reduced concurrency due to extensive locking.

**Repeatable Read Isolation Level:**

- Prevents **dirty reads** and **non-repeatable reads**.
- Does not prevent **phantom reads** (new rows inserted by other transactions may be visible).
- Allows higher concurrency compared to Serializable.

### Practical Examples and Commands

To set the isolation level to Serializable:

```sql
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
BEGIN TRANSACTION;
-- Transaction operations here
COMMIT;
```

To set the isolation level to Repeatable Read:

```sql
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
BEGIN TRANSACTION;
-- Transaction operations here
COMMIT;
```

- **Serializable** ensures that the transaction operates as if it's the only one interacting with the database, providing the highest level of isolation.
- **Repeatable Read** maintains consistency for the data read during the transaction but allows for other transactions to insert new rows that could affect subsequent queries.

### When to Use Each Isolation Level

Choosing between Serializable and Repeatable Read depends on the specific needs of your application.

- **Use Serializable** when it's critical that transactions are completely isolated to prevent all types of anomalies. This is suitable for financial systems where accurate and consistent data is paramount.
- **Use Repeatable Read** when you need to prevent dirty reads and non-repeatable reads but can tolerate phantom reads. This level offers a balance between data consistency and system performance, making it appropriate for many general-purpose applications.

### Balancing Performance and Consistency

Higher isolation levels like Serializable provide greater data integrity but can impact performance due to increased locking and decreased concurrency. Lower isolation levels improve performance but may expose the application to data anomalies.

- It is important to assess application requirements by determining the acceptable level of data **anomalies** based on the application's functionality and user expectations.
- Testing under load involves evaluating how different isolation levels affect **performance** in a simulated production environment.
- Considering optimistic concurrency control can improve concurrency without sacrificing data **integrity** by using techniques that detect conflicts at commit time.

### Understanding Phantom Reads

Here’s a revised section that fixes the table layout and adds an explicit **Database State** column, plus a clear narrative of what each transaction is trying to achieve and what actually happens:

### Understanding Phantom Reads

*Phantom reads* happen when Transaction T1 re-executes a query and sees **new** rows inserted by another transaction (T2), despite using Repeatable Read.

| Time | Transaction T1 (T1’s view)                                                        | Transaction T2                                                                                                | Database State (Electronics)   |
| :--: | :-------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------ | :----------------------------- |
|  T1  | **BEGIN TRANSACTION**<br>– Reads count of Electronics products:<br>  `COUNT = 10` |                                                                                                               | 10 rows (*IDs: 101–110*)       |
|  T2  |                                                                                   | **BEGIN TRANSACTION**<br>– Inserts a new Electronics product:<br>  `INSERT (201,'Electronics')`<br>**COMMIT** | 11 rows (*IDs: 101–110, 201*)  |
|  T3  | Re-reads same query:<br>  `SELECT COUNT(*) ... = 11`<br>**(Phantom row!)**        |                                                                                                               | 11 rows (*IDs: 101–110, 201*)  |
|  T4  | **COMMIT**                                                                        |                                                                                                               | Final state preserved: 11 rows |

**What T1 intended:**
T1 began under Repeatable Read to get a stable snapshot of “all Electronics” and expected any re-reads to still return 10. Its purpose might be to calculate inventory before placing a bulk order or generating a report.

**What actually happened:**
Because T2 committed an insert of a new Electronics product before T1 re-ran its `SELECT`, T1’s second read sees 11 rows. That extra “phantom” row wasn’t visible on the first read, breaking T1’s expectation of repeatability.

* *Repeatable Read* prevents non-repeatable reads of **existing** rows (you can’t see updates twice), but it does **not** stop other transactions from inserting new rows that match your `WHERE` clause. Those new rows show up as phantoms.
* To guard against phantoms, you must use **Serializable** isolation, which effectively locks the range of possible rows or aborts conflicting transactions.

### Strategies to Prevent Phantom Reads

If phantom reads pose a problem, consider using the Serializable isolation level or implementing additional locking mechanisms.

**Using Serializable Isolation Level:**

```sql
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
BEGIN TRANSACTION;
-- Transaction operations
COMMIT;
```

Under Serializable, T1 would not see the new product inserted by T2 during its transaction.
