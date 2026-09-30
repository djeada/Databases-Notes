# Two-Phase Locking (2PL)

Two-phase locking is a concurrency-control protocol that guarantees conflict serializability when all conflicting accesses are covered by appropriate locks. Its two phases concern acquiring and releasing locks; it is different from two-phase commit, a distributed commit protocol.

## The two phases

1. **Growing:** a transaction may acquire locks or upgrade them, but releases none.
2. **Shrinking:** once it releases a lock, it may release or downgrade others, but cannot acquire or upgrade another lock.

The **lock point** is the instant the transaction acquires its last lock. The first release starts the shrinking phase; these events need not be simultaneous.

```text
Acquire S(A) --> Acquire X(B) --> Work --> Release S(A) --> Release X(B)
                 lock point               shrinking starts
|-------------- growing ----------------|------ shrinking ------------|
```

Shared (S) locks allow compatible readers; exclusive (X) locks exclude conflicting lock holders. In MVCC engines, an ordinary snapshot read can read an older committed version despite a writer's row lock.

For predicate queries, row locks alone do not protect rows that have not yet been inserted. A lock-based serializable implementation also needs suitable range or predicate protection.

## Variants

| Variant | Additional rule | Consequence |
| --- | --- | --- |
| Basic 2PL | Follow growing and shrinking phases. | Conflict serializable, but deadlocks and cascading aborts are possible. |
| Strict 2PL | Hold exclusive locks until commit or rollback; retain the basic 2PL rule for other locks. | Prevents another transaction from observing or overwriting uncommitted writes through conflicting accesses. |
| Rigorous 2PL | Hold both shared and exclusive locks until transaction end. | Simplifies recovery and lock release. |
| Conservative 2PL | Obtain the full required lock set before execution; do not hold a partial set while waiting for the rest. | Avoids lock deadlocks, but requires knowing the set in advance and can reduce concurrency. |

Strict 2PL permits an earlier shared-lock release only if no later lock acquisition occurs. Releasing a shared lock and then acquiring an exclusive lock on another item violates basic 2PL.

## Engines do not all use 2PL for reads

PostgreSQL, InnoDB, and SQL Server combine locking with other techniques depending on their settings. PostgreSQL ordinary reads use MVCC, and its serializable level uses dependency detection. Holding write locks until commit does not by itself prove that every transaction follows 2PL or is serializable.

The application chooses transaction boundaries and any explicit locking strategy. The engine manages its lock compatibility rules, waiting, and deadlock handling. SQL Server's `NOLOCK` changes read isolation; it is not a way to request finer lock granularity.

## Example: lock before making a decision

This PostgreSQL example assumes both accounts exist. The application must check the debit balance and roll back if it is insufficient.

```sql
BEGIN;
-- All transfers acquire account locks in the same order.
SELECT account_id, balance
FROM accounts
WHERE account_id IN (1, 2)
ORDER BY account_id
FOR UPDATE;

-- Proceed only after validating account 1's balance and both rows' existence.
UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;
UPDATE accounts SET balance = balance + 100 WHERE account_id = 2;
COMMIT;
```

Both row locks are held until transaction end. An ordinary MVCC reader can still read committed versions. Keep the debit and credit in the same transaction, and enforce useful constraints such as `CHECK (balance >= 0)` where the business permits it.

## Deadlocks and retries

2PL can deadlock: T1 holds A and requests B while T2 holds B and requests A. A consistent acquisition order reduces this risk. Engines typically resolve a detected deadlock by aborting a participant; applications must retry the complete transaction with bounded backoff.

Keep transactions short, avoid network calls while holding locks, and inspect lock waits before increasing lock timeouts.

## Related notes

- [Shared and exclusive locks](01_shared_vs_exclusive_locks.md)
- [Deadlocks](02_deadlocks.md)
- [Serializable and Repeatable Read](05_serializable_vs_repeatable_read.md)
- [PostgreSQL concurrency control](https://www.postgresql.org/docs/current/mvcc.html)
