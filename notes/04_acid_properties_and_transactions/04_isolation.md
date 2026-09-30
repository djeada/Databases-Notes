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

## Reproduce a changed read with two PostgreSQL sessions

Use two terminals connected to the **same PostgreSQL database**. Run setup once, outside the scheduled transactions:

```sql
-- PostgreSQL; setup once
CREATE TABLE isolation_inventory (
    product_id INTEGER PRIMARY KEY,
    stock INTEGER NOT NULL CHECK (stock >= 0)
);
INSERT INTO isolation_inventory VALUES (10, 5);
```

Run these steps in the listed order, alternating terminals. Each table cell is one command sequence for the named session:

| Step | Session A | Session B |
| --- | --- | --- |
| 1 | `BEGIN ISOLATION LEVEL READ COMMITTED;` | |
| 2 | `SELECT stock FROM isolation_inventory WHERE product_id = 10;` → 5 | |
| 3 | | `BEGIN; UPDATE isolation_inventory SET stock = 4 WHERE product_id = 10; COMMIT;` |
| 4 | `SELECT stock FROM isolation_inventory WHERE product_id = 10;` → 4 | |
| 5 | `COMMIT;` | |

The second read sees B's committed update. This is a non-repeatable read, permitted at Read Committed. If A reads while B's update is still uncommitted, A's ordinary select sees the older committed version instead; PostgreSQL does not expose a dirty read.

Reset stock to 5 in a session with no active transaction. Repeat the schedule with A starting `BEGIN ISOLATION LEVEL REPEATABLE READ;`. Its reads return 5 and 5 even though B commits 4. After A commits, a fresh query sees 4. A's old snapshot does not roll back B or prevent B from changing that row.

## A phantom concerns a matching set

Use another independent PostgreSQL setup:

```sql
-- PostgreSQL; setup once
CREATE TABLE isolation_open_orders (
    order_id INTEGER PRIMARY KEY,
    status TEXT NOT NULL
);
INSERT INTO isolation_open_orders VALUES (101, 'open');
```

At Read Committed, A begins and queries `SELECT order_id FROM isolation_open_orders WHERE status = 'open' ORDER BY order_id;`, obtaining 101. B inserts `(102, 'open')` and commits. A repeats the same query and obtains 101 and 102. The changed matching set is a phantom.

In PostgreSQL Repeatable Read, A's stable snapshot prevents this particular phantom. The SQL standard's minimum Repeatable Read definition is weaker, so this observation must not be generalized to every database's implementation. SQL Server Repeatable Read and Serializable differ in their protection of ranges where new rows could appear.

## Watch a stale calculation lose a decrement

Reset `isolation_inventory.stock` to 5. At Read Committed, both clients can read 5 and independently calculate 4. A writes the literal value 4 and commits; B subsequently writes its already calculated literal value 4 and commits. The final stock is 4 even though the clients intended two sales. The writes can be individually locked while the overall workflow still loses one change.

For this single-row rule, keep arithmetic and availability inside the write:

```sql
-- PostgreSQL; each checkout uses its own connection
BEGIN;
UPDATE isolation_inventory
SET stock = stock - 1
WHERE product_id = 10 AND stock > 0
RETURNING stock;
-- Application checks that one row was returned before inserting its order.
COMMIT;
```

At PostgreSQL Read Committed, a competing updater waits when necessary and rechecks the condition on the updated row. Two successful decrements from 5 produce 3, rather than both storing a stale 4. From stock 1, one checkout can obtain the unit and the other gets no qualifying row after the first commits. At stronger isolation levels, the competing operation can instead fail and need a complete retry.

The statement protects this stock rule. It does not reserve a credit-card charge or validate a separate predicate over several products. Use a rule-specific test rather than assuming one conditional update proves the whole checkout correct.

## Write skew changes different rows and breaks one shared rule

Two doctors provide a useful cross-row example. The invariant is “at least one doctor remains on call.” Run this PostgreSQL setup once:

```sql
-- PostgreSQL
CREATE TABLE isolation_on_call (
    doctor_id INTEGER PRIMARY KEY,
    on_call BOOLEAN NOT NULL
);
INSERT INTO isolation_on_call VALUES (1, TRUE), (2, TRUE);
```

At Repeatable Read, follow this schedule:

| Step | Session A | Session B |
| --- | --- | --- |
| 1 | `BEGIN ISOLATION LEVEL REPEATABLE READ;` | `BEGIN ISOLATION LEVEL REPEATABLE READ;` |
| 2 | `SELECT COUNT(*) FROM isolation_on_call WHERE on_call;` → 2 | |
| 3 | | `SELECT COUNT(*) FROM isolation_on_call WHERE on_call;` → 2 |
| 4 | `UPDATE isolation_on_call SET on_call = FALSE WHERE doctor_id = 1;` | |
| 5 | | `UPDATE isolation_on_call SET on_call = FALSE WHERE doctor_id = 2;` |
| 6 | `COMMIT;` | |
| 7 | | `COMMIT;` |

Both transactions saw another doctor available. They updated different rows, so neither needed to overwrite the other's row. Both can commit, leaving zero doctors on call. Stable reads have preserved each transaction's snapshot while allowing a combined result that no correct serial execution of this rule would produce.

To repeat at Serializable, first reset both rows to true outside any active transaction. Use the same schedule with both transactions started at Serializable. PostgreSQL detects the dangerous dependency pattern and aborts a transaction; failure may be reported during a write or commit. Roll back a failed transaction before reusing its connection. Do not depend on a particular session always being the victim.

Retry the entire failed operation. On a fresh state after the other transaction commits, the count is one, so the doctor's application must refuse to go off call. Serializable does not rewrite incorrect application logic: if the application ignores that count, a serial execution can still violate the rule.

## Protect the shared decision, not just each doctor's row

Another design locks one shared coordination row for the duty roster before reading and changing its doctors. All writers must acquire that same lock, then validate the invariant under the appropriate snapshot rules. Locking only the current doctor's row would not coordinate decisions made about the other doctor.

Serializable avoids making the application manually identify every such dependency, but introduces retry requirements and can add overhead. A uniqueness constraint is often simpler for “one booking per seat,” while a conditional update fits “reserve one unit from this row.” Choose the narrow mechanism that actually expresses and protects the workflow's invariant.

## SQLite has its own concurrency model

SQLite normally isolates separate connections and serializes writes. WAL mode permits readers to retain a snapshot while another connection writes. A reader trying to upgrade an obsolete WAL snapshot into a writer can get `SQLITE_BUSY_SNAPSHOT`; it should finish the old transaction and retry against current state. A busy timeout helps some lock waits, but does not make an obsolete snapshot valid.

Shared-cache connections with `read_uncommitted` enabled are a special case; do not use that exception to describe ordinary SQLite reads. PostgreSQL, InnoDB, and SQL Server have different snapshot and locking rules. Record the engine, level, session schedule, and final invariant when testing concurrency.

References: [PostgreSQL transaction isolation](https://www.postgresql.org/docs/current/transaction-iso.html), [PostgreSQL explicit locking](https://www.postgresql.org/docs/current/explicit-locking.html), and [SQLite isolation](https://www.sqlite.org/isolation.html).

## References

- [PostgreSQL transaction isolation](https://www.postgresql.org/docs/current/transaction-iso.html)
- [Double booking](../07_concurrency_control/04_double_booking_problem.md)
- [Two-phase locking](../07_concurrency_control/03_two_phase_locking.md)
