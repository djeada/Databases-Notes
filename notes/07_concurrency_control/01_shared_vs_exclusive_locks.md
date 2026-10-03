# Shared and Exclusive Locks

Locks coordinate concurrent access to database resources.

The simplest textbook model has two lock modes:

- Shared (`S`) lock — usually associated with reading.
- Exclusive (`X`) lock — usually associated with modifying.

The basic idea is:

```text
multiple readers can coexist

but

a writer must exclude conflicting access
```

However, this is only the starting model.

A crucial practical fact is:

> Not every SQL `SELECT` acquires a shared row lock.

PostgreSQL, MySQL/InnoDB, Oracle, and row-versioned SQL Server configurations can let ordinary readers observe committed row versions without taking the kind of blocking shared row lock described by the textbook model.

So there are two questions to keep separate:

```text
1. What does S/X locking mean theoretically?

2. How does this particular database engine
   implement this particular operation?
```

## Why locks are needed

Suppose account `1` contains:

```text
balance = €500
```

Transaction T1 wants to subtract €100:

```sql
UPDATE accounts
SET balance = balance - 100
WHERE account_id = 1;
```

At almost the same time T2 wants to subtract €200.

Without concurrency control, both transactions could interfere while modifying the same logical value.

The database therefore needs some mechanism saying:

```text
T1 is currently modifying this resource.

T2 cannot perform an incompatible modification
until T1 finishes.
```

A lock is one way to express that dependency.

## Shared locks

A shared lock, traditionally written:

```text
S(A)
```

means approximately:

> The transaction is using resource `A` in a way compatible with other readers but incompatible with a conflicting writer.

Suppose T1 has:

```text
S(account 1)
```

T2 may generally also acquire:

```text
S(account 1)
```

because neither transaction is changing the resource.

Conceptually:

```text
T1: S(A)
T2: S(A)

allowed
```

This is why the lock is called shared.

Multiple transactions can share it.

## Exclusive locks

An exclusive lock, written:

```text
X(A)
```

means approximately:

> The transaction needs exclusive modification access to resource `A`.

If T1 holds:

```text
X(A)
```

then another transaction requesting:

```text
S(A)
```

or:

```text
X(A)
```

under the traditional locking model must wait or fail.

Conceptually:

```text
T1: X(A)

T2: S(A) → blocked
T3: X(A) → blocked
```

Hence the name:

```text
exclusive
```

## Basic compatibility matrix

For traditional S/X locking on the same resource:

| Existing lock | Request `S` | Request `X` |
|---|---: |---: |
| `S` | Compatible | Conflict |
| `X` | Conflict | Conflict |

The simplest rule is:

```text
S + S = allowed

S + X = conflict

X + S = conflict

X + X = conflict
```

This matrix is fundamental to lock-based concurrency control.

But it is only meaningful when we specify:

```text
same resource
same relevant granularity
same lock manager
```

An `S` lock on one row obviously does not conflict with an `X` lock on an unrelated row.

## Example: two readers

Suppose two transactions read the same customer.

In a traditional lock-based system:

```text
T1 obtains S(customer 42)
T2 obtains S(customer 42)
```

Both may proceed:

```text
             customer 42

              ┌─────┐
T1 -- S ----> │     │ <---- S -- T2
              └─────┘
```

Neither is modifying the resource.

There is therefore no reason for one reader to wait for the other.

## Example: reader versus writer

Now suppose T1 has:

```text
S(customer 42)
```

and T2 requests:

```text
X(customer 42)
```

Traditional lock compatibility says:

```text
S + X = conflict
```

so T2 waits.

```text
T1:
S(customer 42)
reading...

T2:
X(customer 42)
      │
      └── waits
```

Once T1 releases the shared lock, T2 may obtain its exclusive lock.

This model is important for understanding classical lock-based systems.

But later we will see why PostgreSQL, Oracle, and other MVCC engines do not make ordinary readers and writers behave this way.

## Example: writer versus writer

Suppose T1 executes:

```sql
UPDATE accounts
SET balance = balance - 100
WHERE account_id = 1;
```

and has not committed.

T2 executes:

```sql
UPDATE accounts
SET balance = balance + 50
WHERE account_id = 1;
```

Both want to modify the same current row.

That conflict generally must be serialized.

Conceptually:

```text
T1:
X(account 1)

T2:
X(account 1)
    │
    └── wait
```

This pattern exists even in MVCC databases.

MVCC can often eliminate reader/writer blocking.

It does not mean two transactions can freely create incompatible current versions of the same row.

## Shared/exclusive are compatibility modes, not SQL commands

It is tempting to learn:

```text
SELECT = S lock

UPDATE = X lock
```

That is too simplistic.

What is actually true is closer to:

```text
S and X describe compatibility relationships
between concurrent operations on resources.
```

Different engines then map SQL operations onto those relationships differently.

For example:

```text
SQL Server pessimistic READ COMMITTED
    ordinary read can use S locks

PostgreSQL ordinary SELECT
    reads through MVCC instead of taking
    an S row lock that blocks a writer

Oracle ordinary SELECT
    reads a consistent version

MySQL InnoDB ordinary consistent SELECT
    uses MVCC

SQLite
    coordinates access mainly through
    database/file/WAL-level mechanisms
```

This distinction is essential.

## MVCC changes the reader/writer picture

Suppose T1 is changing:

```text
salary = 50,000
```

to:

```text
salary = 55,000
```

but has not committed.

A traditional lock-based mental model says:

```text
writer has X lock
reader asks for S lock

S + X conflict

reader waits
```

An MVCC engine can instead say:

```text
writer works on the new version

reader reads an older committed version
```

Conceptually:

```text
                 old committed version
                 salary = 50,000
                        ↑
Reader ----------------┘


Writer → new version = 55,000
         not committed yet
```

Now the reader and writer do not necessarily need incompatible locks on the same visible version.

This is the foundation of Multi-Version Concurrency Control.

## PostgreSQL ordinary reads do not take blocking shared row locks

Consider PostgreSQL:

```sql
SELECT employee_id, salary
FROM employees
WHERE employee_id = 1;
```

This ordinary query uses PostgreSQL's MVCC visibility rules.

It does not acquire a `FOR SHARE`-style row lock simply because it is reading the row.

PostgreSQL explicitly states that its row-level locks do not affect ordinary data querying; they block writers and other incompatible row lockers rather than ordinary readers.

Therefore, if T1 modifies employee `1`:

```sql
BEGIN;

UPDATE employees
SET salary = salary + 100
WHERE employee_id = 1;
```

T2 can usually still execute an ordinary:

```sql
SELECT salary
FROM employees
WHERE employee_id = 1;
```

without waiting for T1's row lock.

T2 sees a version allowed by its snapshot.

## PostgreSQL locking reads are explicit

Sometimes a transaction is not merely interested in observing a value.

It wants to make a later decision based on that value.

PostgreSQL provides explicit locking clauses:

```sql
SELECT ... FOR UPDATE;
```

```sql
SELECT ... FOR NO KEY UPDATE;
```

```sql
SELECT ... FOR SHARE;
```

```sql
SELECT ... FOR KEY SHARE;
```

These are real row-locking operations, and PostgreSQL's current `SELECT` documentation identifies all four as locking clauses.

So this:

```sql
SELECT salary
FROM employees
WHERE employee_id = 1;
```

is fundamentally different from:

```sql
SELECT salary
FROM employees
WHERE employee_id = 1
FOR SHARE;
```

or:

```sql
SELECT salary
FROM employees
WHERE employee_id = 1
FOR UPDATE;
```

## PostgreSQL `FOR SHARE`

Consider two sessions.

### Session A

```sql
BEGIN;

SELECT employee_id, salary
FROM employees
WHERE employee_id = 1
FOR SHARE;
```

Session A has explicitly locked the selected row in a shared row-lock mode.

Now Session B tries:

```sql
BEGIN;

UPDATE employees
SET salary = salary + 100
WHERE employee_id = 1;
```

The update requires an incompatible lock.

Therefore Session B waits.

Conceptually:

```text
Session A
FOR SHARE
      │
      ▼
employee 1
      ▲
      │
 UPDATE requested
Session B

B waits
```

When Session A executes:

```sql
COMMIT;
```

its row lock is released.

Session B can then continue.

## Compare that with an ordinary PostgreSQL SELECT

Change Session A to:

```sql
BEGIN;

SELECT employee_id, salary
FROM employees
WHERE employee_id = 1;
```

This is merely an ordinary MVCC read.

Session B executes:

```sql
UPDATE employees
SET salary = salary + 100
WHERE employee_id = 1;
```

The ordinary reader does not create the same row-lock conflict.

This is why saying:

> "SELECT takes a shared lock. "

is wrong as a general description of PostgreSQL.

A more accurate statement is:

> PostgreSQL ordinary reads use MVCC; explicit `FOR SHARE`/`FOR UPDATE` clauses request row locks when the application needs locking semantics.

## Why would an application use `FOR UPDATE`?

Suppose we implement a withdrawal as:

```sql
SELECT balance
FROM accounts
WHERE account_id = 1;
```

The application receives:

```text
balance = 500
```

and decides:

```text
€400 withdrawal is allowed.
```

Before it writes anything, another transaction withdraws €300 and commits.

The first transaction then performs its old decision:

```sql
UPDATE accounts
SET balance = balance - 400
WHERE account_id = 1;
```

The problem was:

```text
READ
      ← concurrency gap →
DECIDE
      ← concurrency gap →
WRITE
```

The decision depended on data that another transaction could change.

A locking read can deliberately close that gap.

## PostgreSQL `FOR UPDATE` example

The transaction can instead do:

```sql
BEGIN;

SELECT balance
FROM accounts
WHERE account_id = 1
FOR UPDATE;
```

Then:

```text
if balance >= 400:
    perform withdrawal
```

and:

```sql
UPDATE accounts
SET balance = balance - 400
WHERE account_id = 1;

COMMIT;
```

A competing transaction requiring an incompatible lock on that account must wait.

The application is saying:

> "I am reading this row specifically because I intend to make a decision that depends on its current state. "

That is fundamentally different from ordinary reporting:

```sql
SELECT balance
FROM accounts
WHERE account_id = 1;
```

## MySQL/InnoDB makes the same ordinary-versus-locking distinction

InnoDB also uses MVCC for ordinary consistent reads.

At its default `REPEATABLE READ` level, plain non-locking `SELECT`s in a transaction use the transaction's consistent snapshot.

For example:

```sql
SELECT balance
FROM accounts
WHERE account_id = 1;
```

is normally a consistent non-locking read.

If the application needs explicit protection, InnoDB supports:

```sql
SELECT ...
FOR SHARE;
```

and:

```sql
SELECT ...
FOR UPDATE;
```

MySQL states that `FOR SHARE` sets shared-mode locks on selected rows, while `FOR UPDATE` locks selected records similarly to an update.

## MySQL `FOR SHARE`

Suppose T1 executes:

```sql
START TRANSACTION;

SELECT *
FROM products
WHERE product_id = 100
FOR SHARE;
```

Another transaction may perform a compatible locking read.

But a transaction attempting to modify the protected record may need to wait.

Conceptually:

```text
T1:
S(product 100)

T2:
S(product 100) → compatible

T3:
UPDATE product 100 → conflict
```

MySQL documents `FOR SHARE` specifically for cases where related data will subsequently be inserted or updated and an ordinary `SELECT` does not provide sufficient protection.

## MySQL `FOR UPDATE`

If the transaction intends to modify the row, use:

```sql
START TRANSACTION;

SELECT stock
FROM products
WHERE product_id = 100
FOR UPDATE;
```

Then:

```sql
UPDATE products
SET stock = stock - 1
WHERE product_id = 100;

COMMIT;
```

The locking read protects the relevant current record/index entry from competing locking operations.

An ordinary InnoDB consistent reader can still behave differently because MVCC reads can use versions in their read view rather than conflicting with the locking read.

## InnoDB locks index records, not an abstract SQL row

This becomes important in real systems.

When InnoDB executes a locking query such as:

```sql
SELECT *
FROM orders
WHERE customer_id = 42
FOR UPDATE;
```

the lock behavior depends on the access path.

InnoDB locks index records and ranges that the statement scans.

For a unique-index equality search:

```sql
WHERE order_id = 100
```

it can lock the matching index record.

For range or non-unique searches:

```sql
WHERE customer_id = 42
```

it may protect a broader index range using record, gap, or next-key locking depending on the isolation level and operation. MySQL explicitly documents that locking reads, updates, and deletes are tied to index records/ranges scanned rather than a remembered abstract SQL predicate.

That is why indexes affect concurrency behavior as well as performance.

## SQL Server maps much more directly onto textbook S/X terminology

SQL Server exposes the S/X model very explicitly.

Its lock manager includes:

```text
Shared (S)
Update (U)
Exclusive (X)
Intent locks
Schema locks
Key-range locks
...
```

Under pessimistic locking, SQL Server documents `S` as a read lock and `X` as the lock used for modification. It also documents the familiar compatibility rule: multiple shared locks may coexist, while an exclusive lock conflicts with other locks on the same resource.

This makes SQL Server particularly useful when learning classical locking theory.

## SQL Server READ COMMITTED does not necessarily hold S locks until commit

Even in a lock-based SQL Server configuration, this is too simplistic:

```text
SELECT takes S lock
S lock remains until COMMIT
```

At ordinary pessimistic `READ COMMITTED`, shared row/page locks are generally released after the data has been read rather than held until transaction end.

SQL Server documents that `READ COMMITTED` normally uses short-duration shared locks when row versioning is not being used.

So:

```sql
BEGIN TRANSACTION;

SELECT *
FROM accounts
WHERE account_id = 1;

-- do something for 20 seconds

COMMIT;
```

does not automatically mean that the ordinary `READ COMMITTED` shared lock on that row is retained for those entire 20 seconds.

The isolation level determines the required read-lock lifetime.

## SQL Server can use row versions instead of read locks

SQL Server can also implement `READ COMMITTED` using row versioning through:

```text
READ_COMMITTED_SNAPSHOT
```

When `READ_COMMITTED_SNAPSHOT` is enabled, SQL Server can read row versions instead of acquiring ordinary shared data locks for `READ COMMITTED` reads. Microsoft documents this distinction directly.

Therefore even this statement:

> "SQL Server SELECT takes an S lock. "

requires qualification.

It depends on:

```text
isolation level
database configuration
query hints
optimized locking features
```

## SQL Server update locks (`U`)

SQL Server introduces an additional mode that explains an important real-world problem:

```text
Update lock (U)
```

Suppose two transactions both do:

```text
read row
then maybe update row
```

If both first acquire `S` locks:

```text
T1: S(A)
T2: S(A)
```

they are compatible.

Later both want:

```text
X(A)
```

Now each transaction's shared lock interferes with the other's upgrade.

Conceptually:

```text
T1: S(A) → wants X(A)
T2: S(A) → wants X(A)
```

This can create an upgrade deadlock.

SQL Server's `U` lock is designed partly to address this pattern: many transactions may hold `S`, but only one transaction can normally hold the update lock for a particular resource. Microsoft explicitly describes this use case.

## SQL Server `UPDLOCK`

An application that reads something because it expects to modify it can use:

```sql
SELECT balance
FROM accounts WITH (UPDLOCK)
WHERE account_id = 1;
```

`UPDLOCK` tells SQL Server to take update locks for the read and retain them until the transaction completes.

Conceptually:

```text
ordinary SELECT:
"I am reading."

UPDLOCK:
"I am reading this because I may modify it;
reserve the update path."
```

This is not exactly identical to PostgreSQL `FOR UPDATE` internally, but it often serves a similar application-level purpose.

## What does `HOLDLOCK` mean in SQL Server?

SQL Server's:

```sql
WITH (HOLDLOCK)
```

is equivalent to using `SERIALIZABLE` semantics for that table reference.

Thus:

```sql
SELECT ...
FROM reservations WITH (UPDLOCK, HOLDLOCK)
WHERE resource_id = 42;
```

is asking for both:

```text
update-oriented locking

and

serializable-range protection
```

for the referenced table.

That is much stronger than merely:

```text
"lock this one existing row."
```

This distinction becomes important for missing rows and predicates.

## Modern SQL Server makes simple lock slogans even less reliable

Current SQL Server versions can use optimized locking.

With optimized locking enabled, SQL Server can release many physical row/page locks associated with modifications earlier and retain a transaction-ID lock representing the uncommitted transaction instead.

Microsoft also recommends row-versioned `READ COMMITTED` where appropriate to maximize optimized-locking benefits.

Therefore statements such as:

```text
"Every UPDATE keeps an X row lock
until COMMIT."
```

are no longer universally accurate descriptions of SQL Server internals.

The isolation guarantee matters more than memorizing one physical lock implementation.

## Oracle is strongly version-oriented for ordinary reads

Oracle provides another useful counterexample to:

```text
SELECT = shared row lock
```

For ordinary querying:

```sql
SELECT *
FROM accounts
WHERE account_id = 1;
```

Oracle uses consistent-read mechanisms.

Its documented concurrency model is essentially:

```text
reader does not block writer

writer does not block reader

writer does block another writer
of the same row
```

Oracle uses undo information to provide readers with the appropriate consistent row version while another transaction modifies the current row.

So ordinary Oracle readers do not need a PostgreSQL-style `FOR SHARE` equivalent.

## Oracle `SELECT. .. FOR UPDATE`

When an Oracle application needs to read rows specifically in preparation for a modification, it can use:

```sql
SELECT balance
FROM accounts
WHERE account_id = 1
FOR UPDATE;
```

Oracle describes this operation as selecting and locking the rows so another user cannot change those row values before the current transaction performs its update.

The locks remain until transaction completion. Oracle's current locking documentation states that locks acquired through explicit transactional locking are released by commit or rollback.

So Oracle follows the same broad application distinction:

```text
ordinary SELECT
    observe consistent data

SELECT FOR UPDATE
    observe data and reserve it
    for a subsequent decision/update
```

## Technology summary: ordinary reads

| Database | Ordinary `SELECT` behavior |
|---|---|
| PostgreSQL | MVCC read; no blocking shared row lock like `FOR SHARE` |
| MySQL/InnoDB | Usually consistent MVCC read |
| SQL Server pessimistic READ COMMITTED | Generally takes short-duration shared locks |
| SQL Server with RCSI | Uses row versions for READ COMMITTED reads |
| Oracle | Consistent-version read; ordinary readers do not block writers |
| SQLite WAL mode | Readers observe snapshots while one writer can append changes |

PostgreSQL separates ordinary MVCC queries from explicit row-locking clauses. InnoDB similarly distinguishes consistent reads from `FOR SHARE`/`FOR UPDATE`. SQL Server can use either shared locks or row versions depending on configuration. Oracle explicitly documents nonblocking ordinary readers and writers.

## Technology summary: explicit locking reads

| Engine | Read because data will be used for a decision |
|---|---|
| PostgreSQL | `SELECT. .. FOR UPDATE`, `FOR NO KEY UPDATE`, `FOR SHARE`, `FOR KEY SHARE` |
| MySQL/InnoDB | `SELECT. .. FOR UPDATE`, `SELECT. .. FOR SHARE` |
| SQL Server | Locking isolation or hints such as `UPDLOCK`; `HOLDLOCK` when serializable range protection is needed |
| Oracle | `SELECT. .. FOR UPDATE` |
| SQLite | No equivalent row-level `SELECT. .. FOR UPDATE` model |

The syntax is superficially similar between some engines, but the exact lock modes, ranges, lifetimes, and MVCC interaction differ.

## A locking read protects existing resources—not necessarily a business rule

This is one of the most important limitations.

Suppose an application prevents duplicate bookings with:

```sql
SELECT *
FROM reservations
WHERE room_id = 7
  AND reservation_date = DATE '2026-10-15'
FOR UPDATE;
```

The query returns:

```text
0 rows
```

The application concludes:

```text
The room is available.
```

Another transaction executes the same query.

It also returns:

```text
0 rows
```

What row did either transaction lock?

Possibly none.

The dangerous resource is:

```text
"a reservation that does not exist yet"
```

There is no existing row to row-lock.

## Concrete double-booking example

Initial state:

```text
reservations table:

(no reservation for room 7 on Oct 15)
```

T1:

```sql
SELECT *
FROM reservations
WHERE room_id = 7
  AND reservation_date = '2026-10-15'
FOR UPDATE;
```

Result:

```text
0 rows
```

T2 executes the same query.

Result:

```text
0 rows
```

T1 inserts:

```sql
INSERT INTO reservations(room_id, reservation_date, customer_id)
VALUES (7, '2026-10-15', 100);
```

T2 inserts:

```sql
INSERT INTO reservations(room_id, reservation_date, customer_id)
VALUES (7, '2026-10-15', 200);
```

If nothing else protects the invariant:

```text
room 7 is double booked
```

The mistake was assuming:

```text
FOR UPDATE on zero rows
```

somehow locks:

```text
"the absence of a row."
```

That is not generally a safe assumption.

## The best solution for uniqueness is usually a constraint

If the business rule is:

```text
one reservation per room per date
```

represent it directly:

```sql
CREATE UNIQUE INDEX reservation_room_date_uq
ON reservations(room_id, reservation_date);
```

Now both transactions may attempt the insert, but the database cannot commit two rows with the same unique key.

This is generally much better than:

```text
SELECT to see whether value exists

then

INSERT if not found
```

because the invariant is enforced where the race actually matters.

A useful principle is:

> If a business invariant can be expressed directly as a database constraint, prefer the constraint over trying to reproduce it with application locking.

## Rows and predicates are different things

Suppose the rule is more complex:

```text
no more than 10 active reservations
for event 42
```

The transaction executes:

```sql
SELECT COUNT(*)
FROM reservations
WHERE event_id = 42
  AND status = 'active';
```

and obtains:

```text
9
```

The logical dependency is not one particular row.

It is:

```text
the entire set of rows satisfying:

event_id = 42
AND status = 'active'
```

A concurrent transaction can insert a new matching row.

So a row-locking solution must somehow protect not only existing rows but the relevant predicate/range.

This is where:

```text
key-range locks
gap locks
next-key locks
Serializable isolation
predicate/dependency tracking
```

become important.

## How InnoDB protects ranges

For many locking range queries under InnoDB, the engine can use:

```text
record locks
+
gap locks
=
next-key locks
```

Suppose an index contains:

```text
10
20
30
```

and the transaction needs to protect:

```text
10 < key < 30
```

Locking only existing key:

```text
20
```

would not stop another transaction inserting:

```text
25
```

So the engine may also protect the relevant gaps.

MySQL documents this behavior for non-unique/range locking searches, where the index range scanned can be protected to block inserts into relevant gaps.

This is why InnoDB locking behavior depends strongly on indexes and isolation level.

## How SQL Server protects ranges

At `SERIALIZABLE` isolation, SQL Server can use key-range locks.

Suppose T1 executes:

```sql
SELECT *
FROM reservations
WHERE room_id = 7
  AND reservation_date BETWEEN '2026-10-01'
                           AND '2026-10-31';
```

Protecting only existing rows would not prevent a new October reservation.

Serializable range locking protects the relevant key interval.

Microsoft describes key-range locks specifically as the mechanism preventing another transaction from inserting rows that would qualify for a serializable transaction's query.

So the lock is conceptually on:

```text
existing keys
+
relevant space between those keys
```

rather than only existing rows.

## PostgreSQL Serializable solves this differently

PostgreSQL does not implement Serializable merely by turning every predicate into a traditional blocking range lock.

Its Serializable level uses Serializable Snapshot Isolation (SSI).

The database can allow transactions to execute concurrently using snapshots while tracking dependencies between their reads and concurrent writes.

If allowing every transaction to commit would create a non-serializable result, PostgreSQL aborts one of them.

Therefore the solution can look like:

```text
SQL Server:
    block conflicting range operation

InnoDB:
    record/gap/next-key locking

PostgreSQL Serializable:
    track dependency
    detect dangerous structure
    abort/retry
```

All three are trying to protect the same logical property through different mechanisms.

## Locks exist at different granularities

A resource does not necessarily mean:

```text
one row
```

Databases can lock or otherwise protect:

| Granularity | Example |
|---|---|
| Row / tuple | One customer |
| Index key | One indexed value |
| Key range / gap | Values between existing index entries |
| Page | A group of records |
| Table | Entire table |
| Schema / metadata | Table definition |
| Transaction ID | Another transaction's unresolved state |
| File/database | SQLite concurrency coordination |

So when someone says:

> "Transaction T1 has an exclusive lock. "

the next question should be:

> Exclusive lock on what?

Granularity determines how much unrelated work can proceed concurrently.

## Why intention locks exist

Suppose a database supports both:

```text
row locks
```

and:

```text
table locks
```

T1 holds:

```text
X(row 100)
```

T2 now requests:

```text
X(entire table)
```

The lock manager needs an efficient way to notice that some lower-level resource inside the table is already protected.

Scanning millions of row locks every time somebody requests a table lock would be expensive.

This is the purpose of intention locks.

Conceptually:

```text
IX(table)
    │
    └── X(row 100)
```

The table-level `IX` does not mean:

```text
the whole table is exclusively locked
```

It means approximately:

> "This transaction has or intends to acquire exclusive locks on resources below this point in the hierarchy. "

SQL Server explicitly exposes modes such as `IS`, `IX`, and `SIX` for this lock hierarchy.

InnoDB similarly uses intention locks as part of row/table lock coordination.

## SQL Server compatibility is therefore richer than S/X

The simple matrix:

| Held | `S` | `X` |
|---|---: |---: |
| `S` | Yes | No |
| `X` | No | No |

is useful for learning.

Real SQL Server locking has a substantially larger matrix including:

```text
IS
IX
S
U
SIX
X
range locks
schema locks
...
```

For example:

```text
S + U = compatible

U + U = conflict
```

This is intentional.

It lets many normal readers coexist while reserving only one transaction as the likely updater.

Microsoft publishes the full compatibility matrix for these modes.

## Lock upgrades can produce deadlocks

Suppose:

```text
T1 obtains S(A)
T2 obtains S(A)
```

That is fine.

Then both decide to update `A`.

T1 requests:

```text
X(A)
```

but T2 still owns:

```text
S(A)
```

so T1 waits.

T2 requests:

```text
X(A)
```

but T1 still owns:

```text
S(A)
```

so T2 waits.

Now:

```text
T1 waits for T2
T2 waits for T1
```

Deadlock.

This is one reason that if an application already knows:

```text
"I will probably update this row"
```

using an update-oriented locking mode from the beginning can be safer than first obtaining a general read lock and attempting to upgrade it later.

SQL Server's `UPDLOCK` exists partly for this exact pattern.

## Lock duration matters as much as lock type

Suppose T1 obtains an exclusive lock for:

```text
2 milliseconds
```

Contention may be insignificant.

The same lock held for:

```text
30 seconds
```

can create a queue of waiting transactions.

Therefore these questions belong together:

```text
What lock?

On what resource?

At what granularity?

For how long?
```

A transaction such as:

```text
BEGIN

lock rows

call external HTTP API

wait 5 seconds

perform more SQL

COMMIT
```

keeps concurrency-sensitive resources occupied while no useful database work is occurring.

Keep transactional sections short.

## `NOWAIT` changes waiting behavior, not compatibility

Suppose a row is already locked.

Normally:

```sql
SELECT ...
FOR UPDATE;
```

may wait.

PostgreSQL can instead use:

```sql
SELECT ...
FOR UPDATE NOWAIT;
```

If the row cannot immediately be locked, the statement returns an error rather than waiting. PostgreSQL documents `NOWAIT` as exactly this alternative to waiting for a conflicting row lock.

The important point is:

```text
NOWAIT does not make incompatible locks compatible.
```

It changes:

```text
what happens when a conflict is encountered
```

from:

```text
wait
```

to:

```text
fail immediately
```

## `SKIP LOCKED`

PostgreSQL and MySQL also support patterns such as:

```sql
SELECT ...
FOR UPDATE SKIP LOCKED;
```

Instead of waiting for already-locked rows, the query skips them.

This can be very useful for work queues.

Suppose:

```text
job 1
job 2
job 3
job 4
```

Worker A locks:

```text
job 1
```

Worker B executes:

```text
FOR UPDATE SKIP LOCKED
```

and can select:

```text
job 2
```

instead of waiting behind Worker A.

PostgreSQL explicitly warns that `SKIP LOCKED` gives an intentionally inconsistent view and is suitable for queue-like workloads rather than general-purpose transactional reads.

## Queue example

A PostgreSQL worker might use:

```sql
BEGIN;

SELECT job_id
FROM jobs
WHERE status = 'pending'
ORDER BY job_id
FOR UPDATE SKIP LOCKED
LIMIT 1;
```

Suppose Worker 1 obtains:

```text
job 100
```

Worker 2 runs the same statement and skips job `100` because it is locked.

It obtains:

```text
job 101
```

Now two workers can process different jobs concurrently.

This is a good example of deliberately using locking semantics to partition work among consumers.

It is very different from using locking to obtain a consistent report.

## SQLite uses a different concurrency model

SQLite should not be forced into the row-lock model used by client/server databases.

Its concurrency control is built around the database file, journaling mode, and pager/WAL locking.

SQLite explicitly states that there can normally be only one writer at a time to a database, although multiple connections can exist and multiple readers can operate concurrently.

Therefore there is no ordinary equivalent of:

```sql
SELECT ...
FOR UPDATE;
```

that gives application-controlled row-level locking comparable to PostgreSQL or InnoDB.

## SQLite rollback mode versus WAL

In traditional rollback-journal mode, SQLite coordinates access to the database file through states such as:

```text
SHARED
RESERVED
PENDING
EXCLUSIVE
```

Its locking documentation describes `SHARED` as permitting multiple readers and `EXCLUSIVE` as providing exclusive access needed for writing the database file.

WAL mode changes the concurrency picture.

Readers can continue to access their snapshot while a writer appends to the write-ahead log.

SQLite documents:

```text
readers do not block the writer

writer does not block existing readers

but only one writer can append at a time
```

in ordinary WAL operation.

This is conceptually much closer to MVCC/snapshot thinking than to row-level `S/X` locking.

## Technology comparison

| Technology | Ordinary reader | Same-row writer conflict | Explicit locking read | Predicate/range strategy |
|---|---|---|---|---|
| PostgreSQL | MVCC | Writers/lockers can block | `FOR UPDATE`, `FOR SHARE`, etc. | Serializable SSI dependency tracking rather than traditional blocking range locks |
| MySQL/InnoDB | MVCC consistent read | Writers conflict through record/index locks | `FOR UPDATE`, `FOR SHARE` | Gap/next-key locking for relevant locking ranges |
| SQL Server pessimistic | Shared locks | Exclusive/update locking | `UPDLOCK`, isolation/hints | Key-range locks at Serializable |
| SQL Server RCSI | Row versions | Writes still require modification coordination | Lock hints can explicitly request pessimistic locks | Serializable/locking hints when required |
| Oracle | Consistent versions | Same-row writers block | `FOR UPDATE` | Serializable/versioning and application/schema design |
| SQLite | File/WAL snapshot mechanisms | One normal writer at a time | No comparable row-level `FOR UPDATE` mechanism | Database/WAL-level concurrency model |

## Do not use locks where an atomic statement is simpler

Suppose inventory contains:

```text
stock = 1
```

A naive application does:

```sql
SELECT stock
FROM products
WHERE product_id = 42;
```

Then in application code:

```text
if stock > 0:
    stock = stock - 1
```

Then:

```sql
UPDATE products
SET stock = ?
WHERE product_id = 42;
```

This creates a read/decision/write race.

You might solve it with a locking read.

But an even simpler solution can be:

```sql
UPDATE products
SET stock = stock - 1
WHERE product_id = 42
  AND stock > 0;
```

Then inspect:

```text
affected rows
```

If:

```text
1
```

the reservation succeeded.

If:

```text
0
```

there was no stock to reserve.

Atomic SQL can sometimes eliminate the need for explicit application-managed locking.

## Locks and constraints solve different problems

Suppose the invariant is:

```text
email must be unique
```

Use:

```sql
UNIQUE(email)
```

Suppose the invariant is:

```text
balance must never be negative
```

where the business model permits direct enforcement:

```sql
CHECK (balance >= 0)
```

Suppose the operation requires:

```text
read several existing rows
make a business decision
update them consistently
```

Then explicit locking or Serializable isolation may be appropriate.

A useful hierarchy is:

```text
Can a constraint enforce it?

        ↓ no

Can one atomic SQL statement enforce it?

        ↓ no

Can a simple well-defined row locking protocol enforce it?

        ↓ no

Do we need predicate/range protection
or Serializable isolation?
```

This tends to produce simpler systems than reflexively adding `FOR UPDATE` everywhere.

## Shared and exclusive locks do not themselves guarantee serializability

Another common mistake is:

```text
we use S and X locks

therefore

our execution must be serializable
```

Not necessarily.

The protocol governing when locks are acquired and released matters.

For example, if a transaction:

```text
lock A
read A
unlock A

later:

lock B
write B
```

another transaction may interleave conflicting operations in a way that creates a non-serializable cycle.

This is exactly why Two-Phase Locking (2PL) adds the rule:

```text
once a transaction begins releasing locks,
it may not acquire new ones
```

Lock modes answer:

> "Which operations conflict? "

2PL answers:

> "In what acquisition/release pattern must those locks be used to guarantee conflict serializability? "

These are separate concepts.

## Shared/exclusive locking and deadlocks

Locks solve one concurrency problem but create another possibility:

```text
waiting cycles
```

Suppose:

```text
T1 holds X(A)
T2 holds X(B)
```

Then:

```text
T1 requests X(B)
T2 requests X(A)
```

Now:

```text
T1 → T2
T2 → T1
```

Deadlock.

The fact that the locks behaved correctly did not malfunction.

The locks successfully prevented conflicting operations.

The deadlock occurred because the transactions acquired resources in opposite orders.

Use a deterministic acquisition order where practical and retry deadlock victims.

## Locks, waits, and timeouts are different concepts

If T1 holds:

```text
X(A)
```

and T2 requests:

```text
X(A)
```

T2 may wait.

That is ordinary lock contention.

If:

```text
T1 waits for T2
T2 waits for T1
```

there is a deadlock.

If T2 has merely waited longer than the configured limit:

```text
lock timeout
```

may occur even without a deadlock.

So distinguish:

```text
lock conflict
    ↓
wait

circular wait
    ↓
deadlock

wait exceeds policy
    ↓
timeout
```

Those are three different states.

## What to inspect in production

When investigating locking, ask:

```text
What resource is locked?

What lock mode exists?

What mode is being requested?

Which session owns it?

Which session is waiting?

How long has the transaction been open?

What SQL acquired the lock?

What indexes/ranges did the query scan?

Is this an ordinary MVCC read
or an explicit locking read?
```

For PostgreSQL, relevant tools include:

```text
pg_stat_activity
pg_locks
pg_blocking_pids()
```

For InnoDB:

```text
Performance Schema lock tables
SHOW ENGINE INNODB STATUS
```

For SQL Server:

```text
dynamic management views
Extended Events
deadlock graphs
```

The underlying question is always:

> Which incompatible dependencies exist, and why did these statements request them?

## Practical decision table

| Situation | Good first mechanism to consider |
|---|---|
| Reporting/read-only query | Ordinary MVCC/versioned read |
| Read row and immediately update it | `FOR UPDATE` / `UPDLOCK` / equivalent |
| Several readers must coexist but writers must wait | Shared locking read where appropriate |
| Unique value | `UNIQUE` constraint |
| Reserve inventory counter | Atomic conditional `UPDATE` |
| Existing row represents the logical resource | Row locking can work well |
| Logical resource does not yet exist | Constraint, range protection, parent-row lock, or Serializable design |
| Predicate covers possible future rows | Range/gap locking or Serializable isolation |
| Worker queue | `FOR UPDATE SKIP LOCKED` where supported |
| Long read should not block writers | MVCC / row-versioning |
| Multiple resources need locks | Deterministic lock order |
| Cross-row business invariant | Explicit protocol or Serializable isolation |

## Final mental model

Do not memorize:

```text
SELECT = S
UPDATE = X
```

Memorize the abstract rule first:

```text
Shared:
    multiple compatible users may coexist.

Exclusive:
    conflicting access must be excluded.
```

Then ask how the engine implements ordinary reads:

```text
PostgreSQL
    MVCC

MySQL/InnoDB
    MVCC consistent reads

SQL Server
    S locks or row versions,
    depending on configuration

Oracle
    consistent versions

SQLite
    database/WAL-level concurrency
```

Then distinguish an ordinary observation from a locking decision:

```text
ordinary SELECT:
    "show me data I am allowed to see"

locking SELECT:
    "I am basing a transactional decision
     on this resource, so protect it"
```

Finally, remember that:

```text
row lock
≠
predicate lock
≠
unique constraint
≠
Serializable isolation
```

A row lock protects a particular lockable resource.

A business rule may instead depend on:

```text
a row that does not yet exist

an index range

several rows

a count

several tables

an aggregate condition
```

and those require different mechanisms.

The most useful question in production is therefore not:

> "Does this query take an S lock or an X lock? "

It is:

> What logical invariant is this transaction relying on, which physical or logical resources protect that invariant, and how does this database engine handle concurrent readers and writers of those resources?

That connects the simple S/X compatibility matrix to real database design.

## References

PostgreSQL's current locking documentation describes its row-level lock modes, their conflicts, transaction lifetime, and the important fact that row locks do not block ordinary data querying.

MySQL's current InnoDB documentation distinguishes ordinary MVCC consistent reads from `FOR SHARE` and `FOR UPDATE` locking reads and explains record, range, gap, and next-key locking.

Microsoft's SQL Server documentation describes shared, update, exclusive, intention, schema, and key-range locks; row-versioned alternatives; `UPDLOCK`; `HOLDLOCK`; and modern optimized locking.

Oracle's concurrency documentation describes its consistent-read model, same-row writer conflicts, nonblocking ordinary readers/writers, and explicit `SELECT. .. FOR UPDATE` behavior.

SQLite's concurrency documentation explains its database/file locking model, single-writer behavior, and WAL snapshot concurrency rather than row-level `FOR UPDATE` locking.
