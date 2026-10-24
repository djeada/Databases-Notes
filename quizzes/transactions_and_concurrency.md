# Transactions and Concurrency Quiz

Notes: [Transaction Control](../notes/03_sql/05_transaction_control_language_tcl.md), [Transactions Introduction](../notes/04_acid_properties_and_transactions/01_transactions_intro.md), [Atomicity](../notes/04_acid_properties_and_transactions/02_atomicity.md), [Consistency](../notes/04_acid_properties_and_transactions/03_consistency.md), [Isolation](../notes/04_acid_properties_and_transactions/04_isolation.md), [Durability](../notes/04_acid_properties_and_transactions/05_durability.md), [Shared and Exclusive Locks](../notes/07_concurrency_control/01_shared_vs_exclusive_locks.md), [Deadlocks](../notes/07_concurrency_control/02_deadlocks.md), [Two-Phase Locking](../notes/07_concurrency_control/03_two_phase_locking.md), [Double Booking](../notes/07_concurrency_control/04_double_booking_problem.md), [Serializable and Repeatable Read](../notes/07_concurrency_control/05_serializable_vs_repeatable_read.md)

Reason about transaction boundaries, isolation anomalies, locks and retries. Behaviour is PostgreSQL unless a question names another engine.

#### Q. After this transaction commits, what has changed for product 10?

```sql
BEGIN;
UPDATE products SET stock = stock + 1 WHERE product_id = 10;
SAVEPOINT optional_change;
UPDATE products SET price_cents = 2000 WHERE product_id = 10;
ROLLBACK TO optional_change;
RELEASE optional_change;
COMMIT;
```

* [ ] Both the stock and the price
* [x] Only the stock
* [ ] Only the price
* [ ] Neither the stock nor the price

> **Explanation:** Rolling back to a savepoint undoes only work done after it, so the price change is discarded while the earlier stock increment stays and is committed.

#### Q. Work done before a savepoint was kept with `ROLLBACK TO`, but then the outer transaction runs `ROLLBACK`. What survives?

* [ ] The work done before the savepoint
* [ ] The work done after the savepoint
* [x] Nothing from the transaction
* [ ] Whatever was released with `RELEASE`

> **Explanation:** A savepoint is a recovery boundary inside one transaction, not an independently durable commit. Rolling back the outer transaction undoes everything in it.

#### Q. A checkout's stock update succeeds, but the following order insert fails with a duplicate-key error. What should the application do?

* [ ] Commit, since the stock update itself succeeded
* [x] Roll back the whole transaction and report or retry
* [ ] Retry only the failed insert in the same transaction
* [ ] Ignore the error, as the engine already rolled back

> **Explanation:** An error is not automatically a rollback in every engine, and committing would decrease stock without an order. The application decides the boundary and must roll back on any failure.

#### Q. `UPDATE products SET stock = stock - 1 WHERE product_id = 10 AND stock >= 1;` affects zero rows inside a checkout transaction. What does that mean for the checkout?

* [ ] The database raised an error and already rolled back
* [x] It is a business failure the code must turn into a rollback
* [ ] Stock was reserved, but no row was reported
* [ ] The statement must be retried until it affects one row

> **Explanation:** A false condition is not a database error. The code must check the affected-row count and refuse the checkout, or it will create an order without reserving stock.

#### Q. An order flow calls a payment API that can take 30 seconds. Where should that call happen?

* [ ] Inside the transaction, so a rollback can undo the payment
* [x] Outside the database transaction, keeping the transaction short
* [ ] Inside a savepoint, so it can be rolled back separately
* [ ] Inside a trigger on the orders table

> **Explanation:** A long transaction can hold locks while it waits, and `ROLLBACK` cannot undo an external charge or email. Do slow external work outside, and use an outbox for messages that must follow a commit.

#### Q. Why do the notes write an order and an `outbox` row in the same transaction instead of sending the email directly?

* [ ] So the email is sent before the order commits
* [x] So the notification commits or rolls back with it
* [ ] So `ROLLBACK` can undo an email already sent
* [ ] So the worker can never send a message twice

> **Explanation:** The outbox makes "send this message" part of the atomic business change. A worker sends after commit, but it can still resend after a crash, so recipients need duplicate tolerance.

#### Q. Which anomaly occurs when a transaction reads a balance that another transaction has written but later rolls back?

* [x] Dirty read
* [ ] Non-repeatable read
* [ ] Phantom read
* [ ] Write skew

> **Explanation:** A dirty read observes uncommitted data that may never become real. Read Committed and stronger levels prevent it.

#### Q. Under Read Committed, a transaction reads a balance twice and sees a different committed value the second time. Which anomaly is this?

* [ ] Uncommitted (dirty) read
* [x] Non-repeatable read
* [ ] Lost update
* [ ] Phantom read

> **Explanation:** Each Read Committed statement can see a newer committed state. Repeatable Read prevents re-reading the same row with a different result; phantoms concern a changing set of matching rows.

#### Q. Two clients each read `stock = 10`, compute 11 in the application and write it back. The final value is 11. Which fix removes this lost update most simply?

* [ ] Run both reads at Read Uncommitted isolation
* [x] Use `SET stock = stock + 1` in one `UPDATE`
* [ ] Add an index on the `stock` column first
* [ ] Read the value twice before writing it

> **Explanation:** An atomic relative update lets the database apply both increments to the current row value. The stale calculation came from an unprotected read used for a later write.

#### Q. In PostgreSQL at Repeatable Read, two doctors each count two doctors on call, and each sets only their own row to off call. Both commit. What is this anomaly?

* [ ] Dirty read
* [ ] Lost update
* [x] Write skew
* [ ] Phantom read

> **Explanation:** Each transaction read a consistent snapshot and updated a different row, so neither overwrote the other, yet together they broke "at least one on call". Snapshot isolation permits this.

#### Q. The same doctors schedule runs at PostgreSQL Serializable. What should the application expect?

* [ ] Both transactions commit, leaving nobody on call
* [x] One transaction fails with a serialization error to retry
* [ ] The second `SELECT` blocks until the first commits
* [ ] Both transactions are rolled back automatically and silently

> **Explanation:** PostgreSQL's Serializable Snapshot Isolation detects the dangerous dependency and aborts one transaction with SQLSTATE `40001`. Do not depend on which session is chosen as the victim.

#### Q. A serializable transaction fails with SQLSTATE `40001`. What should the retry do?

* [ ] Re-run only the final `UPDATE` statement
* [x] Restart the whole transaction from its reads
* [ ] Re-run it at Read Committed to avoid the error
* [ ] Commit the work that succeeded before the error

> **Explanation:** The decision came from reads that are no longer valid. Retrying only the write reuses an obsolete decision; a fresh transaction must read, decide and write again.

#### Q. In PostgreSQL Repeatable Read, transaction A runs `SELECT ... WHERE customer_id = 1` twice. Between the two reads, B inserts and commits a matching row. What does A's second read show?

* [ ] The new row, because it is committed
* [x] The same rows as the first read
* [ ] An error, because the snapshot is stale
* [ ] Only the new row

> **Explanation:** PostgreSQL Repeatable Read reads from one transaction snapshot, so ordinary phantoms do not appear. It can still allow write skew.

#### Q. In SQL Server at Repeatable Read, the same sequence runs: a range read, a committed insert of a matching row, then a second range read. What can the second read return?

* [ ] Exactly the same rows, as in PostgreSQL
* [x] The newly inserted matching row, a phantom
* [ ] An error, as the range is locked
* [ ] Only rows that were updated in between

> **Explanation:** SQL Server Repeatable Read holds shared locks on the rows it read, but not on the key range, so new rows can appear. Serializable adds key-range locks to block them.

#### Q. An editor submits `UPDATE catalog SET price_cents = 1700, version = version + 1 WHERE product_id = 10 AND version = 1;` after another editor already saved version 2. What happens?

* [ ] The price becomes 1700 and the version becomes 3
* [x] Zero rows are updated, signalling a conflict
* [ ] The statement waits until version 1 returns
* [ ] The database raises a constraint violation

> **Explanation:** The version condition no longer matches, so the update affects nothing. This is optimistic concurrency control; the application must check the row count and report the conflict.

#### Q. What must happen before PostgreSQL acknowledges a durable commit under default settings?

* [ ] Every changed data page is written to disk
* [x] The commit's WAL records are flushed to durable storage
* [ ] A checkpoint completes for the database
* [ ] All replicas confirm that they have applied the change

> **Explanation:** Write-ahead logging requires durable log records before acknowledgement; data pages can be written later and replayed from the log after a crash.

#### Q. What is the risk of setting PostgreSQL `synchronous_commit = off`?

* [ ] The database files can become corrupted after a crash
* [x] Recently acknowledged commits can be lost after a crash
* [ ] Transactions are no longer atomic
* [ ] Constraints are checked only at checkpoints

> **Explanation:** It acknowledges commits before their WAL is flushed, so a crash can lose the latest ones while the database stays consistent. Disabling `fsync` is far more dangerous and can corrupt the database.

#### Q. The connection drops while a payment transaction is committing, and the client never gets a reply. What is the safe follow-up?

* [ ] Resubmit the payment under a new request ID
* [x] Look up the outcome by its stable request ID
* [ ] Assume the transaction was rolled back
* [ ] Assume the transaction was committed

> **Explanation:** The server may have committed even though the reply was lost. A unique request identifier enforced by a constraint lets the client find the outcome and avoid a duplicate.

#### Q. In two-phase commit, a participant has prepared and then loses contact with the coordinator. What can it do?

* [ ] Commit, because it already voted yes
* [ ] Roll back once a short timeout expires
* [x] Wait in doubt, holding locks, for the decision
* [ ] Ask another participant to pick the outcome

> **Explanation:** A prepared participant cannot guess the global decision without risking inconsistency. In-doubt transactions can hold locks until recovery resolves them, which is a major operational cost.

#### Q. How do two-phase commit (2PC) and two-phase locking (2PL) relate?

* [ ] 2PL is the commit step inside 2PC
* [x] 2PC agrees on commit; 2PL controls access
* [ ] They are two names for one protocol
* [ ] 2PC replaces 2PL on single-node databases

> **Explanation:** 2PC makes several participants agree to commit or abort. 2PL is a locking discipline for serializable schedules. The similar names do not make them the same mechanism.

#### Q. Under traditional shared/exclusive locking, which request on the same row is granted immediately?

* [x] A shared lock while another shared lock is held
* [ ] An exclusive lock while a shared lock is held
* [ ] A shared lock while an exclusive lock is held
* [ ] An exclusive lock while an exclusive lock is held

> **Explanation:** Shared locks are compatible with each other, so readers can share. Any combination involving an exclusive lock on the same resource conflicts.

#### Q. In PostgreSQL, session A has updated a row but not committed. Session B runs an ordinary `SELECT` of that row at Read Committed. What happens?

* [ ] B blocks until A commits or rolls back
* [x] B reads the last committed version at once
* [ ] B sees A's uncommitted change immediately
* [ ] B fails with a lock-timeout error

> **Explanation:** MVCC lets ordinary reads use a committed snapshot instead of taking blocking shared row locks. A locking read such as `FOR SHARE` or `FOR UPDATE` would wait.

#### Q. What does `SELECT ... FOR UPDATE NOWAIT` change when the row is already locked?

* [ ] It makes the two locks compatible
* [x] It raises an error instead of waiting
* [ ] It skips the locked row and returns others
* [ ] It reads the row without any lock

> **Explanation:** `NOWAIT` changes only the waiting behaviour: fail immediately rather than block. It does not make incompatible locks compatible; skipping rows is what `SKIP LOCKED` does.

#### Q. Several workers claim jobs with this query while job 100 is locked by another worker. What does a worker get?

```sql
SELECT job_id FROM jobs
WHERE status = 'pending'
ORDER BY job_id
FOR UPDATE SKIP LOCKED
LIMIT 1;
```

* [ ] It waits for the lock on job 100 to be released
* [x] The next unlocked pending job, such as 101
* [ ] An error because job 100 is locked
* [ ] Job 100, read without a lock

> **Explanation:** `SKIP LOCKED` ignores rows other transactions have locked, which suits queues. It deliberately gives an inconsistent view, so it is not for general transactional reads.

#### Q. T1 locks account A then requests B, while T2 locks B then requests A. Which design change prevents this deadlock?

* [ ] Raising the lock timeout for both transactions
* [x] Always locking accounts in the same order, such as by ID
* [ ] Using `NOLOCK` hints on the updates
* [ ] Retrying each failed statement until it eventually succeeds

> **Explanation:** A deadlock needs a cycle of waits. Acquiring locks in a consistent global order makes the cycle impossible; timeouts and retries only react after it happens.

#### Q. What does PostgreSQL's `deadlock_timeout` setting (default 1 second) control?

* [ ] The maximum runtime allowed for any query
* [ ] How long a transaction may hold any lock
* [x] How long a lock wait lasts before deadlock checks
* [ ] How long a deadlock victim waits before it is retried

> **Explanation:** Deadlock detection has a cost, so PostgreSQL runs it only after a lock wait lasts this long. It is not a general query or lock timeout.

#### Q. PostgreSQL aborts a transaction with SQLSTATE `40P01`. What happened?

* [ ] A serialization failure with no lock cycle
* [x] A deadlock was detected; it was the victim
* [ ] A lock-wait timeout expired for a statement
* [ ] A unique constraint was violated on insert

> **Explanation:** `40P01` is `deadlock_detected`; `40001` is a serialization failure, which needs no wait cycle. Both are retriable by rerunning the whole transaction.

#### Q. What rule defines two-phase locking?

* [ ] Locks are acquired in two batches of equal size
* [x] Once a transaction releases any lock, it acquires no new locks
* [ ] Every lock is held for exactly two statements
* [ ] Shared locks are always taken first, then exclusive locks

> **Explanation:** A growing phase that only acquires is followed by a shrinking phase that only releases. This guarantees conflict serializability but not freedom from deadlock.

#### Q. What does strict 2PL add to basic two-phase locking?

* [ ] All locks are acquired before the transaction starts
* [x] Exclusive locks are held until commit or abort
* [ ] Shared locks are never released
* [ ] Deadlocks become impossible

> **Explanation:** Holding write locks to the end stops other transactions reading uncommitted data, avoiding cascading aborts. Conservative 2PL, not strict 2PL, pre-acquires all locks.

#### Q. T1 waits for a row lock held by T2, and T2 is busy with a long update that waits on nothing T1 holds. What is this situation?

* [ ] A deadlock that the database must break
* [x] Blocking that ends when T2 commits or rolls back
* [ ] A livelock between the two transactions
* [ ] A serialization failure that is awaiting a retry

> **Explanation:** Blocking is a one-way wait that resolves when the holder finishes. A deadlock needs a cycle, such as T2 also waiting for T1, so that no transaction can ever proceed.

#### Q. Why can `SELECT ... FOR UPDATE` on existing booking rows fail to prevent a double booking?

* [ ] `FOR UPDATE` only locks rows for reading
* [x] It cannot lock a row that does not exist yet
* [ ] It releases its locks after each statement
* [ ] It is ignored at Read Committed

> **Explanation:** Row locks protect existing rows, not the absence of a matching row. Use a constraint, a range or predicate mechanism, Serializable, or lock a row that represents the resource itself.

#### Q. What does SQL Server's `WITH (NOLOCK)` hint actually do?

* [ ] Uses finer-grained row locks for the query
* [x] Reads with roughly Read Uncommitted semantics
* [ ] Releases other transactions' locks on the table
* [ ] Makes the query fully serializable

> **Explanation:** `NOLOCK` is an isolation choice, not a lock-size tuning switch. It can return dirty, missing or duplicated rows.

#### Q. An application runs `BEGIN` on one pooled connection and its next `UPDATE` on a different connection. What is true?

* [ ] Both statements share the same transaction
* [x] The `UPDATE` is not part of the first connection's transaction
* [ ] The pool merges the two connections into one session automatically
* [ ] The `UPDATE` waits until the first connection commits

> **Explanation:** Transaction state belongs to a connection. Returning an unfinished transaction to the pool can also surprise the next borrower.
