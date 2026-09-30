# Shared and Exclusive Locks

Locks coordinate conflicting access to a resource. A shared lock permits compatible readers; an exclusive lock excludes other conflicting lock holders. These names describe lock compatibility, not a universal rule that every SQL read acquires a shared row lock.

## Compatibility

For different transactions requesting ordinary S/X locks on the same resource:

| Held lock | Request S | Request X |
| --- | --- | --- |
| Shared (S) | Compatible | Wait or fail |
| Exclusive (X) | Wait or fail | Wait or fail |

Real engines also use other modes, including intention, update, and schema locks. Compatibility applies at a particular resource and granularity. An MVCC reader can read an older committed version despite a writer's exclusive row lock.

## Ordinary reads and locking reads

PostgreSQL and InnoDB usually use MVCC for ordinary `SELECT` statements, rather than holding shared row locks until commit. In SQL Server's lock-based Read Committed mode, read locks generally do not last until transaction end; row-versioned settings change the behavior. Oracle ordinary reads also use consistent read versions.

Use explicit locking syntax when a decision must exclude concurrent changes. Syntax and lock modes differ by engine:

| Engine | Shared locking read | Lock a row for an update decision |
| --- | --- | --- |
| PostgreSQL | `SELECT ... FOR SHARE` | `SELECT ... FOR UPDATE` |
| MySQL InnoDB | `SELECT ... FOR SHARE` | `SELECT ... FOR UPDATE` |
| SQL Server | Lock-based reads with appropriate isolation or hints | `SELECT ... WITH (UPDLOCK, HOLDLOCK)` |
| Oracle | No direct `FOR SHARE` equivalent | `SELECT ... FOR UPDATE` |

Execute locking reads inside the intended transaction. Read the engine documentation for lock lifetime and predicate protection. SQLite coordinates readers and a single writer through database-level mechanisms; it does not offer equivalent row-level `FOR UPDATE` locks.

## Two-session PostgreSQL example

Assume employee 1 exists. Keep session A open after its select:

```sql
-- Session A
BEGIN;
SELECT employee_id, salary
FROM employees
WHERE employee_id = 1
FOR SHARE;
```

Then run:

```sql
-- Session B
BEGIN;
UPDATE employees SET salary = salary + 100 WHERE employee_id = 1;
-- Waits for session A's conflicting lock to be released.
```

Commit A, then allow B to complete and commit it:

```sql
-- Session A
COMMIT;
```

```sql
-- Session B, after the UPDATE completes
COMMIT;
```

An ordinary PostgreSQL `SELECT` would not create that same shared row-lock wait. `FOR UPDATE` in A would also prevent a competing update, while an ordinary snapshot reader could still see the committed version.

## Rows are not predicates

Locking an existing row does not necessarily protect an absent row or an entire search condition. If a booking does not exist yet, selecting it `FOR UPDATE` may lock no rows. Use a unique constraint, a shared parent-row locking protocol, or an appropriate serializable design to enforce the intended rule.

## Deadlocks and lock duration

Two transactions can each hold a lock that the other needs. Acquire resources in a consistent order, keep transactions short, and retry a complete transaction after a recoverable deadlock abort. A longer timeout does not resolve a circular wait.

Inspect PostgreSQL waits with `pg_stat_activity` and `pg_locks`; use the corresponding engine diagnostics elsewhere.

## Related notes

- [Deadlocks](02_deadlocks.md)
- [Two-phase locking](03_two_phase_locking.md)
- [Double booking](04_double_booking_problem.md)
- [PostgreSQL explicit locking](https://www.postgresql.org/docs/current/explicit-locking.html)
