# Isolation in Database Transactions

Isolation defines how concurrent transactions interact. The strongest common level, Serializable, makes their committed outcome equivalent to some serial execution. Lower levels permit certain anomalies to reduce coordination costs; simply wrapping statements in `BEGIN` and `COMMIT` does not make all races safe.

## Picture two checkouts running together

**Concurrent** transactions overlap in time. Suppose the bookstore has one copy left. Alice and Bob each read that value before either finishes buying. Their earlier reads do not reserve the book. The system needs a write that checks and reserves stock together, or another coordination mechanism that preserves the rule.

An **anomaly** is an interaction that breaks the workflow's expected behavior. A **snapshot** is the set of row versions a read is allowed to see. Depending on the engine and isolation level, a new statement can get a new snapshot or reuse one established for the transaction. Reading a snapshot is not the same thing as locking every row against changes.

Read [Transactions](01_transactions_intro.md) first. The table below names common anomalies; the isolation levels then describe protections against them.

## Recognizing anomalies

| Anomaly | Example |
| --- | --- |
| Dirty read | Read a new balance before the writer commits; the writer later rolls back. |
| Non-repeatable read | Read a balance twice and see a concurrent committed update on the second read. |
| Phantom read | Repeat a query for open orders and see a changed matching set after another transaction commits. |
| Lost update | Two clients read 10, each writes 11, and one increment is lost. |
| Write skew | Two doctors each see another doctor on call, update different rows, and both go off call. |

An anomaly is a property of the whole read-and-write workflow. An individual `UPDATE` taking a row lock does not protect a decision made by an earlier unprotected read.

## Isolation levels

The SQL standard specifies minimum protections. Actual engines can be stronger.

| Level | Required protection | Remaining concerns |
| --- | --- | --- |
| Read Uncommitted | Does not require protection from dirty reads. | Dirty reads and other anomalies; some engines implement it as Read Committed. |
| Read Committed | Prevents dirty reads. | Separate statements can see different committed states. |
| Repeatable Read | Also prevents non-repeatable reads. | The standard permits phantoms and serialization anomalies; implementations differ. |
| Serializable | Committed transactions must be equivalent to a serial order. | Blocking or transaction aborts can require retries. |

PostgreSQL Repeatable Read uses a transaction snapshot and prevents phantoms, but can permit write skew. InnoDB ordinary Repeatable Read reads also use a stable snapshot; locking reads and writes have additional rules. SQL Server Repeatable Read uses locks on existing read rows and can permit phantoms. See [Serializable and Repeatable Read](../07_concurrency_control/05_serializable_vs_repeatable_read.md) for the detailed comparison.

## How engines enforce isolation

**Locking** coordinates conflicting accesses. Shared and exclusive locks have compatibility rules; range locks can protect predicates against inserts. Locks can cause waits and deadlocks.

**MVCC** keeps row versions so an ordinary read can use a committed snapshot while a writer changes the current version. The snapshot can be per statement or per transaction. Readers and writers can still conflict through explicit locks, schema changes, or competing updates. MVCC alone does not establish serializability.

**Optimistic checks** detect conflicting changes using versions or dependency validation. An application can condition an update on a previously read version and check the affected-row count. The update still uses the engine's normal write coordination; “optimistic” does not mean that no locks exist anywhere.

## Example: reserve the last unit safely

This PostgreSQL conditional update performs the test and decrement in one statement:

```sql
BEGIN;
UPDATE inventory
SET stock = stock - 1
WHERE product_id = 101 AND stock > 0
RETURNING product_id, stock;
-- Application: create the reservation only if exactly one row was returned.
-- If no row was returned, report unavailable; do not create a reservation.
COMMIT;
```

Place the reservation insert in the same transaction as the successful decrement. Add `CHECK (stock >= 0)` and use an idempotency key if the request can be retried. For individually assigned seats, a unique constraint on the relevant flight and seat provides an additional rule.

This is safer than reading stock, calculating a value in application code, and later writing that stale value. At stronger isolation levels, conflicts can abort the transaction; retry the complete operation when appropriate.

## Choosing and validating isolation

Choose a level against the invariants the workflow must preserve. Test concurrent operations with separate sessions, rather than assuming a successful single-session run proves correctness. Track blocking, deadlocks, serialization failures, and end-to-end latency.

For PostgreSQL:

```sql
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
-- Read rule-related data and perform related writes.
COMMIT;
```

Other engines use different transaction-start and isolation-setting syntax. Use the dialect's documented order of operations.

## References

- [PostgreSQL transaction isolation](https://www.postgresql.org/docs/current/transaction-iso.html)
- [Double booking](../07_concurrency_control/04_double_booking_problem.md)
- [Two-phase locking](../07_concurrency_control/03_two_phase_locking.md)
