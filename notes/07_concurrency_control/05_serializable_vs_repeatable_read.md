# Serializable and Repeatable Read

Isolation controls which effects of concurrent transactions a transaction can observe. **Repeatable Read** protects repeated reads; **Serializable** additionally guarantees that committed transactions have an outcome equivalent to some serial execution. Neither requires transactions to run one at a time.

## The anomalies to distinguish

| Anomaly | What happens |
| --- | --- |
| Dirty read | A transaction reads another transaction's uncommitted change. |
| Non-repeatable read | Re-reading a row returns a value changed by a concurrent commit. |
| Phantom read | Repeating a predicate query returns a different set of matching rows because of a concurrent commit. |
| Write skew | Transactions read the same rule-related data, update different rows, and jointly violate a rule. |

## Repeatable Read depends on the engine

The SQL standard permits phantom reads at Repeatable Read. An engine can provide stronger guarantees.

- **PostgreSQL:** ordinary reads use a stable transaction snapshot, so concurrent inserts do not appear as phantoms. Write skew can still occur.
- **MySQL InnoDB:** ordinary consistent reads share a snapshot. Locking reads and writes use different rules; range locking can block inserts. Do not mix snapshot reads and locking reads as though they observe the same state.
- **SQL Server:** Repeatable Read holds read locks on existing rows but does not generally protect the gaps between them. A repeated query can see new matching rows. `SNAPSHOT` is a separate isolation level.

### Example: a concurrent insert

Suppose customer 1 initially has five orders. T1 starts at Repeatable Read and executes an ordinary `SELECT`.

| Step | T1 | T2 |
| --- | --- | --- |
| 1 | Read orders for customer 1: five rows. | |
| 2 | | Insert a sixth order and commit. |
| 3 | Repeat the query. | |

At step 3, PostgreSQL and InnoDB snapshot reads still return five rows. SQL Server Repeatable Read can return six. T1's own writes remain visible to T1 in these models.

## Why a stable snapshot is not enough

Suppose two doctors are on call and at least one must remain available.

1. T1 and T2 each read a snapshot showing two doctors on call.
2. T1 marks doctor A off call; T2 marks doctor B off call.
3. They update different rows, so a simple same-row conflict check need not stop either transaction.
4. If both commit, no doctor remains on call.

Each transaction saw stable data, but the combined outcome violates the rule. This is write skew. A valid serial execution would make the second doctor see only one doctor remaining and stay on call.

## What Serializable adds

A serializable implementation prevents such an outcome from committing. Lock-based implementations can block conflicting operations; PostgreSQL uses Serializable Snapshot Isolation to detect dangerous dependencies and abort a transaction when necessary.

Applications must retry the **whole transaction**, including its reads, after a serialization failure. Retrying only the final write can reuse an invalid decision. Keep retries bounded and avoid repeating external side effects such as sending a payment or email; use idempotency or an outbox where needed.

### PostgreSQL syntax

```sql
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
-- Read the rule-related rows, make a decision, and perform the writes.
COMMIT;
```

For a stable snapshot without full serializability:

```sql
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT * FROM orders WHERE customer_id = 1;
-- A later ordinary SELECT uses the same transaction snapshot.
COMMIT;
```

## Choosing a level

Use Repeatable Read for work that needs a stable view and whose correctness does not depend on unprotected cross-row rules. Use Serializable when concurrent decisions must behave like a serial execution. Constraints, conditional updates, and explicit locking can also protect specific rules, provided every relevant writer follows the protocol.

Measure throughput, lock waits, and retry rates under a realistic workload. The isolation level alone does not determine performance.

## References

- [PostgreSQL transaction isolation](https://www.postgresql.org/docs/current/transaction-iso.html)
- [InnoDB consistent reads](https://dev.mysql.com/doc/refman/8.4/en/innodb-consistent-read.html)
- [SQL Server isolation levels](https://learn.microsoft.com/en-us/sql/t-sql/statements/set-transaction-isolation-level-transact-sql)
