# Deadlocks in Database Systems

A deadlock occurs when two or more transactions are waiting for one another in a cycle and none can continue unless one of the transactions is aborted or otherwise forced to release its resources.

The simplest form is:

```text
T1 holds A and waits for B
T2 holds B and waits for A
```

Neither transaction can make progress:

```text
T1 cannot obtain B until T2 finishes.
T2 cannot obtain A until T1 finishes.

But neither can finish because both are waiting.
```

The important idea is not merely that transactions are blocked.

> A deadlock is circular blocking.

Ordinary blocking is expected in transactional databases. Deadlock is the special case where the blocking relationships form a cycle.

## Blocking is not the same thing as deadlock

Suppose T1 updates an account:

```sql
BEGIN;

UPDATE accounts
SET balance = balance - 100
WHERE account_id = 1;
```

T1 now holds whatever write-related locks the database requires for that update.

T2 executes:

```sql
UPDATE accounts
SET balance = balance + 50
WHERE account_id = 1;
```

T2 may have to wait.

The situation is:

```text
T1 holds account 1

T2
 │
 └── waits for T1
```

This is blocking, but it is not a deadlock.

T1 can continue:

```sql
COMMIT;
```

and once T1 releases its lock, T2 can proceed.

There is no circular dependency.

A deadlock requires something like:

```text
T1 waits for T2
        ↑
        │
        ↓
T2 waits for T1
```

or a longer cycle:

```text
T1 → T2 → T3 → T1
```

This distinction matters operationally because a system may have substantial lock waits without having any deadlocks.

## A concrete deadlock: two bank transfers

Consider:

```text
Account 1 = €1,000
Account 2 = €1,000
```

Two transfers occur concurrently.

Transaction T1 wants:

```text
€100 from account 1 → account 2
```

Transaction T2 wants:

```text
€50 from account 2 → account 1
```

T1 begins:

```sql
BEGIN;

UPDATE accounts
SET balance = balance - 100
WHERE account_id = 1;
```

T1 now owns a write lock associated with account `1`.

Before T1 touches account `2`, T2 runs:

```sql
BEGIN;

UPDATE accounts
SET balance = balance - 50
WHERE account_id = 2;
```

T2 obtains the lock associated with account `2`.

The state is:

| Transaction | Holds | Needs next |
|---|---|---|
| T1 | account 1 | account 2 |
| T2 | account 2 | account 1 |

T1 now executes:

```sql
UPDATE accounts
SET balance = balance + 100
WHERE account_id = 2;
```

but account `2` is locked by T2.

So:

```text
T1 waits for T2
```

T2 then executes:

```sql
UPDATE accounts
SET balance = balance + 50
WHERE account_id = 1;
```

but account `1` is locked by T1.

Now:

```text
T1 waits for T2
T2 waits for T1
```

Neither transaction can reach `COMMIT`.

That is a deadlock.

This is the same fundamental pattern used by the original notes' account example, but the important part is understanding why waiting has become impossible to resolve normally.

## The wait-for graph

A wait-for graph converts the lock situation into a graph of transaction dependencies.

Each transaction is a node.

An edge:

```text
T1 → T2
```

means:

> T1 is waiting for a resource currently preventing it from proceeding because of T2.

For the bank-transfer example:

```text
T1 → T2
T2 → T1
```

Graphically:

```text
┌────┐       waits for       ┌────┐
│ T1 │ ────────────────────→ │ T2 │
│    │ ←──────────────────── │    │
└────┘       waits for       └────┘
```

There is a cycle.

That cycle is what matters.

For three transactions:

```text
T1 waits for T2
T2 waits for T3
T3 waits for T1
```

the graph becomes:

```text
T1 → T2 → T3
↑           │
└───────────┘
```

Again, no participant can finish without another participant first making progress.

The original notes correctly identify a cycle in the wait-for graph as the essential detection idea.

## The four ingredients that make deadlock possible

The classic deadlock model describes four conditions that together make a deadlock possible.

| Condition | Meaning in a database |
|---|---|
| Mutual exclusion | Some resource cannot simultaneously be held in conflicting modes by multiple transactions. |
| Hold and wait | A transaction holds one resource while requesting another. |
| No forced preemption | The database does not simply take a lock away from a transaction in the middle of its work. |
| Circular wait | T1 waits for T2, T2 waits for T3, .. ., and eventually another transaction waits for T1. |

Consider the bank example.

T1 holds account `1` while asking for account `2`:

```text
hold and wait
```

T2 holds account `2` while asking for account `1`:

```text
hold and wait
```

Their incompatible write locks provide:

```text
mutual exclusion
```

and the database cannot simply remove T1's lock while keeping T1's uncommitted transaction intact:

```text
no preemption
```

Finally:

```text
T1 → T2 → T1
```

provides circular wait.

The DBMS therefore has to break the situation by aborting a transaction.

## Why the database cannot simply "let both continue"

Suppose T1 currently has an uncommitted modification to account `1`.

Allowing T2 to ignore T1's lock and modify the same version would destroy the database's concurrency-control guarantees.

Likewise, removing T1's lock while leaving T1's transaction alive would leave unclear ownership of the uncommitted state.

So the normal solution is not:

```text
ignore the locks
```

but:

```text
choose one transaction
roll it back
release its locks
allow the others to continue
```

The rolled-back transaction is commonly called the deadlock victim.

## Deadlocks occur because transactions acquire resources incrementally

Most transactions do not acquire every resource they need at the beginning.

They do something like:

```text
lock A
do work

discover that B is needed
lock B

discover that C is needed
lock C
```

That behavior is useful because locking everything up front would reduce concurrency and may not even be possible when later resources depend on earlier query results.

But incremental acquisition creates an opportunity for:

```text
T1: A → waiting for B
T2: B → waiting for A
```

This is also why Two-Phase Locking can guarantee conflict serializability and still permit deadlocks.

Two transactions can both be obeying the growing phase of 2PL while each waits for another lock.

## Deadlocks are not limited to explicit `LOCK` statements

A common misconception is:

> "We never manually lock tables, therefore we cannot deadlock. "

Normal SQL statements acquire locks automatically.

For example:

```sql
UPDATE accounts
SET balance = balance - 100
WHERE account_id = 1;
```

can acquire row-related locks even though the application never wrote:

```sql
LOCK ...
```

PostgreSQL explicitly documents that deadlocks can arise from ordinary row-level locks and gives essentially the same two-account example: one transaction updates one account, a second transaction updates another, and each subsequently requests the other's row. PostgreSQL automatically detects the resulting deadlock and aborts one transaction.

InnoDB likewise states that deadlocks can occur through ordinary statements such as `UPDATE` and `SELECT. .. FOR UPDATE`, including conflicts involving ranges of index records and gaps.

## The locked resource may not simply be "a row"

Real databases can deadlock on more than two obvious table rows.

Depending on the engine and operation, resources involved can include:

| Resource | Example |
|---|---|
| Row / tuple | Two transactions update customer rows in opposite order |
| Index key | Two writes need incompatible locks on index entries |
| Key range / gap | Concurrent range operations or inserts |
| Table | DDL and DML require incompatible table lock modes |
| Transaction ID | One PostgreSQL transaction waits for another transaction's outcome |
| Metadata/schema resource | DDL competes with queries or other schema operations |
| Application/advisory lock | Application-defined logical resources are acquired in inconsistent order |
| Internal SQL Server resource | Deadlock graphs can involve keys, pages, parallel query resources, and other engine-managed resources |

This explains a common debugging surprise:

```text
"We only updated one logical row each.
How did these transactions deadlock?"
```

The executed statement may have touched several indexes or additional internal resources.

InnoDB explicitly warns that even inserts or deletes involving a single row can deadlock because the operation can lock multiple index records internally.

## Indexes are therefore part of deadlock behavior

Consider:

```sql
UPDATE orders
SET status = 'processing'
WHERE customer_id = 42
  AND status = 'new';
```

With a useful index such as:

```text
(customer_id, status)
```

the engine may find the relevant records through a relatively narrow access path.

Without a suitable index, it may need to inspect a much larger portion of the table or index.

That can mean:

```text
more rows visited
more records/ranges locked
locks held for longer
more overlap with concurrent transactions
```

which increases opportunities for contention and deadlock.

MySQL specifically recommends indexes on columns used by locking reads and updates when trying to reduce InnoDB deadlocks.

So indexing is not only:

```text
query performance
```

It can also affect:

```text
concurrency behavior
```

## The most effective prevention technique: consistent lock ordering

Return to the two transfers.

The bad ordering is:

```text
T1:
account 1
account 2

T2:
account 2
account 1
```

A cycle can form.

Instead, define a global rule:

> Whenever a transaction needs several accounts, lock them in increasing `account_id` order.

Now both transactions use:

```text
account 1
account 2
```

even if the logical transfer direction is reversed.

T1:

```text
lock account 1
lock account 2
```

T2:

```text
request account 1
```

but T1 already has it, so T2 waits before acquiring account 2.

The state becomes:

```text
T1 holds 1 and 2

T2 waits for 1
```

There is no:

```text
T1 waits for T2
```

edge.

Therefore there is no cycle.

PostgreSQL explicitly recommends acquiring locks on multiple objects in a consistent order as its primary deadlock defense. MySQL gives the same recommendation for transactions that update multiple rows or tables.

## PostgreSQL implementation of ordered account locking

A PostgreSQL transfer can deliberately acquire both row locks first:

```sql
BEGIN;

SELECT account_id, balance
FROM accounts
WHERE account_id IN (1, 2)
ORDER BY account_id
FOR UPDATE;

-- Verify both rows exist.
-- Verify the debit is permitted.

UPDATE accounts
SET balance = balance - 100
WHERE account_id = 1;

UPDATE accounts
SET balance = balance + 100
WHERE account_id = 2;

COMMIT;
```

All transfer code should follow the same ordering rule:

```text
lowest account_id first
highest account_id second
```

A transfer:

```text
2 → 1
```

must not decide:

```text
"2 is the source, therefore lock 2 first."
```

It should still lock:

```text
1 → 2
```

The business direction and the lock acquisition order are separate concepts.

## Lock conversion can also contribute to deadlock

Deadlock does not always look like:

```text
T1 owns A
T2 owns B
```

Consider two transactions that first acquire compatible shared locks:

```text
T1: S(A)
T2: S(A)
```

Both can coexist.

Later both decide they need to modify `A` and request stronger locks.

Conceptually:

```text
T1 owns S(A), wants X(A)
T2 owns S(A), wants X(A)
```

Each transaction's existing shared lock interferes with the other's upgrade.

The precise behavior depends on the engine and lock modes, but the general lesson is:

> Acquiring a weak lock and later upgrading it can create different deadlock patterns from requesting the necessary restrictive mode earlier.

PostgreSQL therefore advises that, where practical, the first lock acquired on an object should be the most restrictive mode the transaction will need.

## Keeping transactions short reduces the window for cycles

Consider:

```text
BEGIN
update row A

call payment API
wait 3 seconds

update row B
COMMIT
```

For those three seconds, the transaction may continue holding locks.

Another transaction has much more time to obtain `B` and then request `A`.

Now compare:

```text
call payment API

BEGIN
update A
update B
COMMIT
```

The lock-holding interval is far shorter.

Long transactions increase the period during which another transaction can form a conflicting dependency.

The original notes correctly identify long transaction duration as a deadlock risk. PostgreSQL explicitly warns against leaving transactions open while waiting for user interaction, and MySQL recommends keeping transactions small and committing related changes promptly.

## PostgreSQL: what happens when a deadlock occurs

PostgreSQL automatically detects deadlocks.

Suppose:

```text
T1 holds A → waits for B
T2 holds B → waits for A
```

PostgreSQL eventually recognizes that waiting cannot resolve normally.

It aborts one transaction.

The other can then continue because the victim's locks are released.

PostgreSQL explicitly warns that applications should not depend on which transaction gets chosen as the victim.

The error is classified as:

```text
SQLSTATE 40P01
deadlock_detected
```

PostgreSQL's current documentation specifically identifies `40P01` as a deadlock failure that applications may retry.

## PostgreSQL does not continuously run expensive deadlock detection

PostgreSQL has a setting called:

```text
deadlock_timeout
```

This is not:

```text
"abort any query that waits longer than this"
```

Instead, it controls roughly how long a process waits on a lock before PostgreSQL performs its deadlock check.

The current default is:

```text
1 second
```

PostgreSQL explains that deadlock detection has a cost, so it does not immediately run the detector every time a transaction encounters a conflicting lock.

This creates an important distinction:

```text
deadlock_timeout
≠
general query timeout
≠
lock timeout
```

A perfectly legitimate lock wait may last longer than usual if no timeout terminates it.

## Debugging PostgreSQL lock contention

PostgreSQL exposes:

```sql
pg_locks
```

which contains outstanding lock information.

A simple first inspection is:

```sql
SELECT *
FROM pg_locks
WHERE NOT granted;
```

This shows lock requests that are currently waiting.

However, manually joining `pg_locks` to determine the blocker can be difficult.

PostgreSQL provides:

```sql
pg_blocking_pids(pid)
```

which returns the PID or PIDs blocking a backend from acquiring a lock.

A useful diagnostic query is therefore:

```sql
SELECT
    a.pid,
    a.query,
    a.wait_event_type,
    a.wait_event,
    pg_blocking_pids(a.pid) AS blocking_pids
FROM pg_stat_activity AS a
WHERE cardinality(pg_blocking_pids(a.pid)) > 0;
```

This helps answer:

```text
Who is waiting?

What SQL is it running?

Who is blocking it?
```

For a deadlock that has already been resolved, the server log/error information is generally more useful because one participant has already been aborted and the cycle no longer exists.

## MySQL/InnoDB: automatic deadlock detection

InnoDB also automatically detects transaction deadlocks by default.

When it finds one, it rolls back a victim transaction so that the other transaction can continue.

The familiar application error is:

```text
ERROR 1213 (40001):
Deadlock found when trying to get lock;
try restarting transaction
```

The key parts are:

```text
MySQL error number: 1213
SQLSTATE: 40001
```

MySQL's own error documentation explicitly tells the application to rerun all operations in the transaction after this error.

## How InnoDB chooses a victim

When deadlock detection is enabled, InnoDB attempts to choose a relatively small transaction to roll back.

Its documentation describes transaction size for this purpose in terms of the number of rows inserted, updated, or deleted.

Conceptually, if the choice is between:

```text
T1:
changed 2 rows

T2:
changed 100,000 rows
```

rolling back T1 may waste much less work.

This is an engine policy rather than an application guarantee.

Application correctness must never depend on:

```text
"our transaction will never be chosen."
```

## Debugging InnoDB deadlocks

One of the most useful MySQL commands is:

```sql
SHOW ENGINE INNODB STATUS\G
```

Its output includes:

```text
LATEST DETECTED DEADLOCK
```

when a recent InnoDB deadlock exists.

That section can show:

```text
which transactions participated

which statements they were running

which locks they held

which locks they requested

which transaction InnoDB rolled back
```

MySQL documents this information explicitly.

For recurring problems, InnoDB provides:

```text
innodb_print_all_deadlocks
```

When enabled, all InnoDB user-transaction deadlocks are written to the MySQL error log instead of retaining only the latest deadlock information available through InnoDB status.

That makes it much easier to diagnose intermittent production deadlocks.

## MySQL deadlock versus lock-wait timeout

These are different errors.

A deadlock means InnoDB has identified a dependency cycle.

InnoDB rolls back the whole victim transaction.

A lock wait timeout means a statement has waited longer than the configured waiting threshold.

With InnoDB's default behavior, a lock wait timeout normally rolls back the waiting statement rather than necessarily the entire transaction; the behavior can be changed with `innodb_rollback_on_timeout`.

Therefore application code should not blindly treat:

```text
deadlock
```

and:

```text
lock wait timeout
```

as identical failure modes.

## SQL Server: deadlock victim error 1205

SQL Server also detects deadlock cycles and selects a victim.

The victim's transaction is rolled back, releasing its resources so the other participants can continue.

The client receives:

```text
error 1205
```

Microsoft documents this behavior directly.

Conceptually:

```text
T1 ←──── deadlock ────→ T2
                        ↓
                  victim selected
                        ↓
                     rollback
                        ↓
                  locks released
                        ↓
                other T continues
```

The application should be prepared to retry the operation represented by the victim transaction.

## SQL Server allows deadlock priorities

SQL Server provides:

```sql
SET DEADLOCK_PRIORITY LOW;
```

or:

```sql
SET DEADLOCK_PRIORITY NORMAL;
```

or:

```sql
SET DEADLOCK_PRIORITY HIGH;
```

Numeric values from:

```text
-10 ... 10
```

are also supported.

If two sessions have different priorities, the one with the lower deadlock priority is preferred as the victim.

If priorities are equal, SQL Server generally chooses the transaction it estimates is less expensive to roll back, based on rollback cost.

This feature does not prevent deadlocks.

It influences:

```text
which transaction loses when one occurs
```

That is very different from lock ordering, which attempts to eliminate the cycle in the first place.

## SQL Server deadlock graphs

SQL Server provides particularly rich deadlock diagnostics.

The recommended mechanism is the Extended Events event:

```text
xml_deadlock_report
```

The built-in:

```text
system_health
```

Extended Events session captures detected deadlocks, including their deadlock graphs, by default.

A deadlock graph typically includes:

```text
victim-list

process-list

resource-list
```

which lets you reconstruct:

```text
who was involved

what each process was doing

what resource each held

what resource each needed

which process became the victim
```

Microsoft recommends `xml_deadlock_report` rather than relying on the older SQL Trace/Profiler deadlock event mechanisms.

This is a major practical advantage when diagnosing production incidents: you want the cycle, not merely the SQL statement that happened to receive error `1205`.

## Technology comparison

| Area | PostgreSQL | MySQL/InnoDB | SQL Server |
|---|---|---|---|
| Automatic detection | Yes | Yes by default | Yes |
| Typical victim error | SQLSTATE `40P01` | Error `1213`, SQLSTATE `40001` | Error `1205` |
| Victim selection | Engine chooses; application should not rely on which one | Attempts to choose a smaller transaction | Priority first; if equal, rollback cost is considered |
| Main diagnostic mechanism | Logs, `pg_locks`, `pg_stat_activity`, `pg_blocking_pids()` | `SHOW ENGINE INNODB STATUS`, `innodb_print_all_deadlocks` | Extended Events `xml_deadlock_report`, `system_health` |
| Important prevention technique | Consistent resource order | Consistent resource/order access | Consistent resource order |
| Application response | Retry complete transaction when appropriate | Retry complete transaction | Retry victim transaction |
| Can ordinary SQL create deadlocks? | Yes | Yes | Yes |
| Are explicit locks required? | No | No | No |

PostgreSQL documents automatic deadlock detection and consistent ordering as the primary defense. InnoDB documents automatic detection, victim rollback, and transaction retry. SQL Server documents automatic victim selection, error `1205`, and deadlock graph diagnostics through Extended Events.

## Prevention, detection, and timeout are three different strategies

These terms should not be mixed.

| Strategy | What it does | Example |
|---|---|---|
| Prevention | Designs transactions so a cycle is unlikely or impossible | Always lock account IDs ascending |
| Detection | Allows waits to form, discovers an actual cycle, aborts a victim | PostgreSQL/InnoDB/SQL Server deadlock detector |
| Timeout | Stops waiting after a threshold even without proving a cycle | Lock wait timeout |

Consider:

```text
T1 holds A for 20 seconds
T2 waits for A
```

There is no cycle.

A detector should not call this a deadlock.

But a configured lock timeout might still abort T2 because it waited too long.

Conversely:

```text
T1 waits for T2
T2 waits for T1
```

is a genuine deadlock even if it formed only milliseconds ago.

A real deadlock detector can resolve it without waiting for a long general timeout.

## Timeouts do not fix deadlock design

Suppose transactions consistently do:

```text
T1: A → B
T2: B → A
```

Setting:

```text
lock timeout = 2 seconds
```

does not remove the structural problem.

It merely guarantees that someone eventually stops waiting.

The better fix is usually:

```text
T1: A → B
T2: A → B
```

and then retain timeout/retry mechanisms as operational protection.

This is why timeouts should generally be treated as:

```text
failure containment
```

rather than:

```text
the primary concurrency-control design
```

## Isolation level and deadlocks: avoid simplistic rules

The statement:

> "Higher isolation means more deadlocks. "

is too broad.

Higher isolation levels can cause some engines or workloads to retain more protection, touch ranges differently, or create additional blocking opportunities.

But deadlock behavior depends on much more:

```text
database engine

MVCC versus locking behavior

query plan

indexes

lock types

transaction length

number of rows touched

order of access

locking reads

range locks

application concurrency
```

For example, PostgreSQL ordinary MVCC reads behave differently from SQL Server's traditional locking reads.

MySQL/InnoDB explicitly states that deadlocks can occur regardless of isolation level and that normal writes themselves are sufficient to produce them.

Therefore a useful diagnosis is:

> "Which resources do these particular statements lock, in which order, and for how long? "

rather than simply:

> "Which isolation level are we using? "

## Deadlock versus serialization failure

These are easy to confuse because both can cause a database to abort a transaction.

A deadlock is:

```text
T1 is waiting for T2
T2 is waiting for T1
```

A serialization failure is broader:

```text
allowing all these transactions to commit
would violate the required serializable outcome
```

There does not have to be a lock-wait cycle.

PostgreSQL makes the distinction particularly visible:

```text
40P01 = deadlock_detected

40001 = serialization_failure
```

PostgreSQL recommends considering retries for both classes of failure.

The retry pattern can look similar, but the reason for the abort is different.

## Deadlock versus livelock

A deadlock means:

```text
nothing moves
```

because participants wait for one another.

A livelock means:

```text
participants are doing things
but no useful progress occurs
```

For example:

```text
T1 loses conflict → immediately retries
T2 loses conflict → immediately retries
T1 loses conflict → immediately retries
T2 loses conflict → immediately retries
...
```

The system is active, but the workload does not converge.

This is one reason retry logic often uses:

```text
bounded attempts
+
backoff
+
jitter
```

rather than immediate infinite retry loops.

The original notes correctly separate deadlock from livelock and connect aggressive retries with the latter.

## Retry the whole transaction

Suppose a transaction does:

```text
1. read account balance
2. decide transfer is allowed
3. update account A
4. update account B
```

and is chosen as a deadlock victim at step 4.

Do not retry only:

```text
step 4
```

The transaction was rolled back.

More importantly, the state used for:

```text
step 1
step 2
```

may now be stale.

The safe pattern is:

```text
attempt 1:

BEGIN
    READ
    DECIDE
    WRITE
COMMIT

deadlock

attempt 2:

BEGIN
    READ AGAIN
    DECIDE AGAIN
    WRITE AGAIN
COMMIT
```

MySQL explicitly says that a deadlock rolls back the entire InnoDB transaction and instructs applications to rerun the complete transaction. PostgreSQL likewise identifies deadlock failures as appropriate candidates for transaction retry.

## Example retry logic

Conceptually:

```text
MAX_ATTEMPTS = 4

for attempt in 1..MAX_ATTEMPTS:

    try:
        BEGIN

        perform all reads
        validate business rules
        perform all writes

        COMMIT
        return success

    catch deadlock:
        ROLLBACK

        if attempt == MAX_ATTEMPTS:
            fail

        sleep(backoff + random_jitter)
```

The retry should be:

```text
bounded
```

because persistent deadlocks may indicate a design problem.

Backoff avoids immediately recreating exactly the same scheduling conflict.

Random jitter helps prevent many failed transactions from waking simultaneously and colliding again.

## External side effects make retries dangerous

Consider:

```text
BEGIN

update order

send email

update inventory

COMMIT
```

Suppose the transaction becomes a deadlock victim after the email was sent.

The database rolls back:

```text
order changes
inventory changes
```

but it cannot roll back:

```text
the email
```

The application retries.

Now the customer receives two emails.

The same problem applies to:

```text
payment API calls
SMS
HTTP requests
message publication
shipping requests
```

This is why retryable database transactions should avoid irreversible external side effects inside the transaction boundary.

Patterns such as an outbox let the database transaction record:

```text
order change
+
message to be sent
```

atomically, while another component performs the external effect after commit.

## Do not solve frequent deadlocks only by adding more retries

An occasional deadlock in a highly concurrent transactional system is not automatically a database defect.

InnoDB's documentation explicitly notes that deadlocks are a normal transactional phenomenon and applications should be prepared to retry them.

But if deadlocks occur continuously, blindly increasing:

```text
retry count
```

can make things worse:

```text
more retries
→ more concurrent work
→ more contention
→ more deadlocks
→ still more retries
```

Frequent deadlocks should trigger analysis of:

```text
lock order
transaction length
indexes
query plans
rows/ranges touched
lock upgrades
application access patterns
```

Retry is a resilience mechanism.

It is not a substitute for fixing a deterministic circular acquisition pattern.

## How to analyze a production deadlock

When a deadlock report is available, reconstruct the cycle.

Suppose the diagnostics tell you:

```text
T1:
owns X lock on orders/100
waits for customers/42

T2:
owns X lock on customers/42
waits for orders/100
```

Do not start by asking:

```text
"Which SQL statement is bad?"
```

Ask:

```text
Why does transaction T1 access Order → Customer?

Why does transaction T2 access Customer → Order?
```

The structural problem is often the inconsistent order:

```text
T1: Order → Customer
T2: Customer → Order
```

A durable fix might be:

```text
all code paths:
Customer → Order
```

The specific victim query is often merely where the cycle happened to become visible.

## A deadlock can involve different application services

Imagine:

```text
Payment Service
    locks invoice
    then updates customer

Customer Service
    locks customer
    then updates invoice
```

Each service looks sensible in isolation.

But together:

```text
Payment:
Invoice → Customer

Customer:
Customer → Invoice
```

creates opposite resource ordering.

This is why lock-order rules need to be shared across:

```text
repositories
background workers
microservices
stored procedures
batch jobs
administrative scripts
```

if they operate against the same transactional resources.

A local convention inside one method is insufficient if another code path accesses the resources in reverse order.

## Application-level locks can deadlock too

PostgreSQL supports advisory locks, allowing the application to define logical resources that do not correspond directly to rows.

For example:

```sql
SELECT pg_advisory_xact_lock(100);
```

could represent:

```text
logical customer 100
```

If one transaction obtains:

```text
customer 100
then customer 200
```

and another obtains:

```text
customer 200
then customer 100
```

the same deadlock reasoning applies.

PostgreSQL's advisory locks participate in normal blocking behavior and are visible through `pg_locks`.

The database does not care that the identifier is application-defined.

The cycle is still:

```text
T1 → T2 → T1
```

## Deadlocks outside databases

The same structure appears in multithreaded applications.

Thread A:

```text
lock mutex M1
request mutex M2
```

Thread B:

```text
lock mutex M2
request mutex M1
```

Result:

```text
Thread A waits for B
Thread B waits for A
```

The database version is not a fundamentally different phenomenon.

The resources are simply:

```text
rows
keys
ranges
tables
transaction resources
```

instead of:

```text
mutexes
```

This connection is also present in the original notes' thread example.

## Practical strategy table

| Problem observed | First thing to investigate |
|---|---|
| Same two tables repeatedly deadlock | Check whether code paths access them in opposite orders |
| Account-transfer deadlocks | Lock account IDs in deterministic order |
| Deadlocks increased after query change | Compare execution plans, indexes, rows/ranges touched |
| Deadlocks during `SELECT. .. FOR UPDATE` | Check range size, indexes, and lock order |
| InnoDB deadlock | Inspect `LATEST DETECTED DEADLOCK` |
| PostgreSQL sessions waiting | Inspect `pg_stat_activity`, `pg_locks`, `pg_blocking_pids()` |
| SQL Server error 1205 | Inspect `xml_deadlock_report` / deadlock graph |
| Many transactions retry simultaneously | Add bounded backoff and jitter; investigate root contention |
| Long transactions | Remove network/user waits and commit sooner |
| Same resource upgraded from weak to strong lock | Consider acquiring the required mode earlier |
| Deadlocks after adding Serializable/range locking | Inspect range access and execution plans rather than assuming row-level conflicts |
| Rare unavoidable deadlock | Correctly retry the full transaction |

## What each database gives you

| Database | Error/application signal | Main production diagnostic |
|---|---|---|
| PostgreSQL | `40P01 deadlock_detected` | Server logs plus `pg_locks`, `pg_stat_activity`, `pg_blocking_pids()` |
| MySQL/InnoDB | `1213`, SQLSTATE `40001` | `SHOW ENGINE INNODB STATUS`; optionally `innodb_print_all_deadlocks` |
| SQL Server | Error `1205` | `xml_deadlock_report` Extended Event; default `system_health` session |

PostgreSQL exposes outstanding locks through `pg_locks` and blocker relationships through `pg_blocking_pids()`.

InnoDB records detailed information about its latest detected deadlock and can log all deadlocks when `innodb_print_all_deadlocks` is enabled.

SQL Server's default `system_health` Extended Events session captures deadlock graphs, and Microsoft recommends the `xml_deadlock_report` event for deadlock analysis.

## Final mental model

Do not memorize deadlock as merely:

```text
"two transactions lock each other"
```

Use this model instead:

```text
NORMAL BLOCKING

T1 holds A
T2 waits for T1

T1 eventually commits
T2 continues

No cycle.
```

versus:

```text
DEADLOCK

T1 holds A and waits for B
T2 holds B and waits for A

T1 → T2
T2 → T1

Cycle.
Nobody can resolve it by normal waiting.
```

The DBMS therefore does:

```text
detect cycle
→ choose victim
→ rollback victim
→ release victim's resources
→ allow remaining transaction(s) to continue
```

The application should do:

```text
retry the complete victim transaction
```

while the system design should reduce recurrence through:

```text
consistent resource ordering
short transactions
appropriate indexes
small lock scope
predictable locking modes
careful transaction boundaries
```

The most useful production question is not:

```text
"How do I disable deadlocks?"
```

It is:

> Which resources did each transaction acquire, in what order, what did each transaction request next, and where did that ordering form a cycle?

Once the cycle is reconstructed, the fix is usually much easier to see.

## References

The source notes provide the original wait-for-graph, lock-ordering, timeout, rollback, bank-transfer, and deadlock-versus-livelock structure.

PostgreSQL's current explicit-locking documentation describes row/table locking, automatic deadlock detection, consistent lock ordering, victim aborts, and lock inspection.

PostgreSQL's lock-management documentation explains `deadlock_timeout`, while its monitoring interfaces provide `pg_locks` and `pg_blocking_pids()`.

MySQL's InnoDB documentation describes automatic deadlock detection, victim selection, error handling, `SHOW ENGINE INNODB STATUS`, `innodb_print_all_deadlocks`, and complete-transaction retry requirements.

Microsoft's SQL Server documentation describes deadlock victim selection, error `1205`, `DEADLOCK_PRIORITY`, and Extended Events deadlock graphs captured by `system_health`.
