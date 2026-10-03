# Two-Phase Locking (2PL)

Two-Phase Locking, usually abbreviated 2PL, is a concurrency-control protocol for making interleaved transactions behave like some serial execution.

The central problem it solves is this:

> Two transactions may each perform individually valid reads and writes, but their operations can interleave in an order that produces a result that could never occur if the transactions had run one at a time.

2PL prevents that class of problem by controlling when a transaction may acquire and release conflicting locks.

The name has nothing to do with distributed commit.

Two-Phase Locking (2PL) controls concurrent access to data.

Two-Phase Commit (2PC) coordinates commit/rollback across multiple participants in a distributed transaction.

A distributed system can use both, but they solve completely different problems.

## The problem 2PL is trying to solve

Suppose two transactions operate on two values, `A` and `B`.

A serial execution would look like:

```text
T1 completely finishes
then T2 runs
```

or:

```text
T2 completely finishes
then T1 runs
```

Real databases want more concurrency, so they interleave operations:

```text
T1 reads A
T2 reads B
T1 writes B
T2 writes A
```

Some interleavings are harmless.

Others create contradictory ordering requirements.

For example, imagine this schedule:

```text
T1 reads A
T2 writes A

T2 reads B
T1 writes B
```

Because T1 read `A` before T2 changed it, that interaction suggests:

```text
T1 → T2
```

But because T2 read `B` before T1 changed it, the second interaction suggests:

```text
T2 → T1
```

Together:

```text
T1 → T2 → T1
```

There is a cycle.

There is therefore no way to say:

```text
T1 happened entirely before T2
```

or:

```text
T2 happened entirely before T1
```

while preserving those conflicting operations.

The schedule is not conflict serializable.

Two-Phase Locking was designed to prevent exactly these cycles.

## Locks first: Shared and Exclusive

The textbook 2PL model usually begins with two lock types.

| Lock | Meaning | Compatible with another S lock? | Compatible with an X lock? |
|---|---|---: |---: |
| Shared (`S`) | Transaction wants to read the item | Yes | No |
| Exclusive (`X`) | Transaction wants to modify the item | No | No |

For a data item `A`:

```text
T1: S(A)
```

means:

```text
T1 intends to read A.
```

Another reader can also hold:

```text
T2: S(A)
```

at the same time.

But:

```text
T1: X(A)
```

means another transaction cannot obtain a conflicting `S(A)` or `X(A)` until that lock becomes available.

Conceptually:

```text
S + S  → allowed
S + X  → conflict
X + S  → conflict
X + X  → conflict
```

Real database engines have many additional lock modes, such as update locks, intention locks, range locks, key-share locks, and metadata locks.

Those are implementation details built around the same general idea:

> operations that cannot safely occur concurrently must be made incompatible.

## The two phases

A transaction following Basic 2PL moves through two phases.

### Growing phase

The transaction may:

```text
acquire new locks
upgrade existing locks
```

but it does not release locks.

For example:

```text
S(A)
X(B)
S(C)
```

is still in the growing phase.

### Shrinking phase

The shrinking phase begins when the transaction releases its first lock.

From that point onward, it may release additional locks, but it may not acquire a new lock or upgrade an existing one.

For example:

```text
S(A)
X(B)
S(C)

release S(A)

release X(B)
release S(C)
```

is valid.

But this is not:

```text
S(A)
X(B)

release S(A)

X(C)        <-- illegal under 2PL
```

Once shrinking has started, lock acquisition is finished.

## The lock point

The lock point is the instant at which a transaction obtains its final lock.

For example:

```text
Acquire S(A)
Acquire X(B)
Acquire S(C)   <-- lock point
do work
Release S(A)   <-- shrinking begins
Release X(B)
Release S(C)
```

Notice that:

```text
lock point
```

and:

```text
first unlock
```

are not necessarily the same instant.

There can be work between them.

The important fact is simply:

> after the first unlock, the transaction can never obtain another lock.

## Why this strange rule guarantees conflict serializability

This is the part that is usually omitted from short 2PL notes.

Suppose two transactions conflict on some data item.

For example:

```text
T1 holds X(A)
T2 needs S(A)
```

T2 cannot obtain its conflicting lock until T1 releases its lock.

Because T1 follows 2PL, by the time it releases `A`, T1 has already obtained every lock it will ever need.

Its lock point has therefore already occurred.

T2 obtains its conflicting lock later.

So for this dependency:

```text
T1 → T2
```

we also know:

```text
lockPoint(T1) < lockPoint(T2)
```

Now imagine the conflict graph contained a cycle:

```text
T1 → T2
T2 → T3
T3 → T1
```

The lock-point ordering would require:

```text
lockPoint(T1) < lockPoint(T2)
lockPoint(T2) < lockPoint(T3)
lockPoint(T3) < lockPoint(T1)
```

Combining them would imply:

```text
lockPoint(T1)
<
lockPoint(T2)
<
lockPoint(T3)
<
lockPoint(T1)
```

which is impossible.

Therefore the conflict graph cannot contain a cycle.

An acyclic conflict graph means the schedule is conflict serializable.

This is the fundamental reason 2PL works.

## What goes wrong if the two-phase rule is broken

Consider this schedule:

```text
T1: acquire S(A)
T1: read A
T1: release S(A)

T2: acquire X(A)
T2: write A

T2: acquire S(B)
T2: read B

T1: acquire X(B)       <-- T1 acquires a lock after releasing one
T1: write B
```

T1 violates 2PL because it released `A` and later acquired a new lock on `B`.

Now look at the conflicts.

On `A`:

```text
T1 read A before T2 wrote A

T1 → T2
```

On `B`:

```text
T2 read B before T1 wrote B

T2 → T1
```

Therefore:

```text
T1 → T2 → T1
```

The schedule is not conflict serializable.

The rule:

> never acquire another lock after releasing your first lock

is therefore not arbitrary bookkeeping.

It prevents transactions from creating contradictory ordering relationships late in their execution.

## Basic 2PL is serializable, but recovery can still be unpleasant

Basic 2PL guarantees conflict serializability.

It does not require every lock to be held until commit.

That creates another problem.

Imagine T1 does:

```text
T1:
X(A)
write A = 500
release X(A)
```

T1 has entered its shrinking phase and will not acquire another lock, so Basic 2PL has not been violated.

Before T1 commits, T2 obtains:

```text
S(A)
```

and reads:

```text
A = 500
```

Then T1 discovers an error and rolls back.

The value T2 read never really committed.

T2 has consumed dirty data and may itself need to roll back.

If another transaction depended on T2, the rollback could cascade further.

This is the motivation for Strict 2PL.

## The main 2PL variants

| Variant | Rule | Main purpose |
|---|---|---|
| Basic 2PL | Acquire locks during growing phase; after first release, acquire no more locks | Conflict serializability |
| Strict 2PL | Basic 2PL plus hold exclusive/write locks until commit or rollback | Prevent dirty reads/writes of uncommitted changes through conflicting lock access; avoid cascading aborts |
| Rigorous 2PL | Hold both shared and exclusive locks until transaction end | Makes transaction order and recovery particularly simple |
| Conservative / Static 2PL | Obtain the complete required lock set before execution proceeds | Prevent lock deadlocks caused by gradually acquiring locks |

These variants address different problems.

They should not be thought of as four completely unrelated protocols.

For example, strictness is about how long write locks are retained, while conservative 2PL is about obtaining the required lock set before execution instead of discovering locks incrementally.

The ideas can therefore overlap.

## Strict 2PL

Under Strict Two-Phase Locking, a transaction does not release its exclusive locks until:

```text
COMMIT
```

or:

```text
ROLLBACK
```

Return to the earlier example.

T1 writes:

```text
A = 500
```

but has not committed.

Because T1 still holds:

```text
X(A)
```

T2 cannot obtain a conflicting lock allowing it to read or overwrite that value.

Conceptually:

```text
T1:
X(A)
write A = 500
...
COMMIT
release X(A)

T2:
        waits...
        S(A)
        read A
```

If T1 rolls back instead:

```text
T2 never observes the uncommitted value.
```

This makes recovery much easier.

A transaction cannot build committed work on top of another transaction's still-uncommitted write through conflicting locked access.

## Strict 2PL still has a growing and shrinking rule

A subtle point:

Strict 2PL does not simply mean:

```text
hold X locks until commit
and do whatever you want with every other lock
```

The transaction still follows Basic 2PL.

For example:

```text
Acquire S(A)
Acquire X(B)

Release S(A)

Acquire X(C)
```

is not valid Strict 2PL.

The release of `S(A)` started the shrinking phase.

Acquiring `X(C)` afterward violates 2PL.

Holding `X(B)` until commit does not repair that violation.

## Rigorous 2PL

Rigorous 2PL goes further.

Instead of holding only write locks until the transaction ends, it holds both:

```text
S locks
X locks
```

until commit or rollback.

Conceptually:

```text
BEGIN

S(A)
X(B)
S(C)

read/write work

COMMIT

release S(A)
release X(B)
release S(C)
```

There is effectively no normal shrinking phase before transaction completion.

This has a useful property:

> if T1 releases a conflicting lock before T2 obtains it, T1 must already have finished.

That makes the committed transaction order especially easy to reason about.

However, keeping read locks until transaction completion can increase blocking.

That tradeoff is one reason modern database systems often combine locking with MVCC rather than using textbook rigorous 2PL for every ordinary read.

## Conservative 2PL

Ordinary 2PL can deadlock because transactions usually discover the locks they need gradually.

For example:

```text
T1 locks A
T2 locks B

T1 requests B → waits
T2 requests A → waits
```

Neither transaction can continue.

Conservative 2PL avoids this specific problem by requiring a transaction to obtain its complete lock set before execution proceeds.

For example, T1 determines that it needs:

```text
X(A)
X(B)
S(C)
```

and asks for all of them.

If the complete set is unavailable, it does not start while holding only part of that set.

Therefore the classic pattern:

```text
hold one resource
while waiting for another
```

does not develop.

The disadvantage is obvious.

Many database transactions do not know their complete lock set in advance.

A query might first read:

```text
customer_id = 42
```

then discover from that row which invoices, accounts, jobs, or child records must be accessed.

Predeclaring everything would be difficult or impossible.

It can also reduce concurrency by acquiring resources earlier than actually needed.

## Deadlocks are not evidence that 2PL is broken

Deadlocks are a normal consequence of lock-based concurrency.

Suppose two bank transfers execute simultaneously.

Transaction T1:

```text
transfer from account 1 to account 2
```

Transaction T2:

```text
transfer from account 2 to account 1
```

If they lock their source account first:

```text
T1: X(account 1)
T2: X(account 2)
```

then:

```text
T1 asks for account 2 → waits
T2 asks for account 1 → waits
```

We now have:

```text
T1 waits for T2
T2 waits for T1
```

That is a deadlock.

The database normally detects the cycle, aborts one participant, and lets the other continue.

The application then retries the aborted transaction.

PostgreSQL automatically detects lock deadlocks and aborts one transaction; its documentation recommends acquiring multiple objects in a consistent order where possible. PostgreSQL uses SQLSTATE `40P01` for `deadlock_detected`.

MySQL/InnoDB similarly detects deadlocks. Error `1213`, `ER_LOCK_DEADLOCK`, uses SQLSTATE `40001`, and MySQL explicitly tells applications to restart the transaction.

SQL Server chooses a deadlock victim, rolls its transaction back, and returns error `1205`.

## Concrete solution: always lock accounts in the same order

A common way to reduce the bank-transfer deadlock is to define a canonical lock order.

Instead of:

```text
lock source
then lock destination
```

every transfer uses:

```text
lock lower account_id
then lock higher account_id
```

For example, in PostgreSQL:

```sql
BEGIN;

SELECT account_id, balance
FROM accounts
WHERE account_id IN (1, 2)
ORDER BY account_id
FOR UPDATE;

-- Application verifies that both accounts exist
-- and that account 1 can be debited.

UPDATE accounts
SET balance = balance - 100
WHERE account_id = 1;

UPDATE accounts
SET balance = balance + 100
WHERE account_id = 2;

COMMIT;
```

A concurrent reverse transfer should use the same account ordering.

Now both transactions attempt:

```text
account 1
then account 2
```

instead of:

```text
T1: 1 → 2
T2: 2 → 1
```

This greatly reduces the possibility of a cycle.

It does not mean an application can ignore deadlock handling entirely: databases can acquire additional internal/index locks and larger transactions can involve other resources.

Retry logic is still necessary.

## Lock ordering and 2PL solve different problems

These concepts are often mixed together.

2PL prevents non-serializable conflict schedules.

Consistent lock ordering reduces deadlocks.

A system can follow perfect 2PL and still deadlock.

For example:

```text
T1: lock A
T2: lock B

T1: request B
T2: request A
```

Neither transaction has released anything.

Both are still completely inside the growing phase.

They are obeying 2PL.

They are also deadlocked.

So:

```text
2PL ⇒ serializability
```

does not imply:

```text
2PL ⇒ no deadlocks
```

## Rows are not the only things that may need locking

Textbook explanations often talk about:

```text
lock(A)
lock(B)
```

as though every data item were one database row.

Real databases may lock or protect:

| Resource | Why it may matter |
|---|---|
| Row / tuple | Protect one existing record |
| Index entry | Protect access to indexed data |
| Key range | Prevent matching keys from appearing |
| Gap between keys | Prevent inserts into a predicate range |
| Page | Protect a larger storage unit |
| Table | Protect many rows at once |
| Metadata/schema object | Protect table definitions and other metadata |
| Logical transaction resource | Used by some modern lock implementations |

This becomes especially important for queries based on predicates.

## Row locks cannot protect a row that does not exist

Consider a reservation system with this rule:

```text
only one active reservation may exist
for resource 42 at 10:00
```

Transaction T1 executes:

```sql
SELECT *
FROM reservations
WHERE resource_id = 42
  AND start_time = '10:00'
FOR UPDATE;
```

Suppose no row exists.

What exactly did T1 row-lock?

Nothing.

There is no existing row corresponding to:

```text
resource 42 at 10:00
```

to lock.

Another transaction might also find no row and attempt to insert one.

This is the predicate / phantom problem.

The logical thing that needs protection is:

```text
"all current and future rows satisfying this condition"
```

rather than only:

```text
"these rows that currently exist"
```

Different database systems solve this in different ways.

## How SQL Server solves predicate protection

SQL Server's lock-based `SERIALIZABLE` isolation can use key-range locks.

Suppose a query reads an indexed range:

```sql
SELECT *
FROM reservations
WHERE resource_id = 42
  AND start_time >= '10:00'
  AND start_time < '11:00';
```

Protecting only currently existing rows is insufficient.

Another transaction could insert a new index key that falls into that interval.

Under locking Serializable behavior, SQL Server can protect the relevant index range so another transaction cannot insert a qualifying key until the first transaction finishes. Microsoft explicitly describes key-range locks as the mechanism used at Serializable to prevent phantom insertions.

Conceptually:

```text
Existing keys:

09:00
09:30
        [ protected range ]
11:00
```

The protected object is partly the space between keys, not only existing rows.

This is how lock-based serializable implementations extend the 2PL idea from individual rows to predicates.

## How MySQL/InnoDB solves range conflicts

InnoDB combines MVCC with record and index-range locking.

A locking query such as:

```sql
SELECT booking_id
FROM bookings
WHERE event_id = 42
FOR UPDATE;
```

can acquire locks on encountered index records.

At isolation levels and access patterns where range protection is needed, InnoDB also uses gap locks and next-key locks so that concurrent transactions cannot simply insert a new qualifying record between existing index entries.

This is how InnoDB protects situations in which:

```text
the dangerous row does not exist yet
```

or the logical resource is a range rather than one row.

MySQL's InnoDB documentation explicitly separates ordinary consistent MVCC reads from locking reads and documents next-key locking as its phantom-protection mechanism.

## PostgreSQL does something importantly different

PostgreSQL is an excellent example of why:

> "database locking" is not automatically the same thing as "the database uses textbook 2PL for everything. "

An ordinary PostgreSQL:

```sql
SELECT *
FROM accounts
WHERE account_id = 1;
```

uses MVCC.

It does not normally acquire an `S` row lock that blocks a concurrent writer.

If another transaction has modified the row but not yet committed, PostgreSQL can often read an older committed version instead.

This differs fundamentally from a pure textbook scheme where every read must acquire an `S` lock conflicting with a writer's `X` lock.

PostgreSQL row locks such as:

```sql
SELECT ...
FOR UPDATE;
```

do exist.

They block other writers and conflicting lockers until the transaction ends, but ordinary MVCC readers can continue reading suitable committed row versions. PostgreSQL explicitly documents that row-level locks do not prevent ordinary data querying.

Therefore:

```text
PostgreSQL uses locks
```

does not imply:

```text
PostgreSQL implements all transaction isolation
using classical 2PL.
```

## PostgreSQL Serializable is not lock-based 2PL

PostgreSQL's Serializable level is particularly important.

It is implemented using:

Serializable Snapshot Isolation (SSI).

PostgreSQL begins with snapshot isolation and monitors read/write dependencies between concurrent transactions.

When it detects a dependency structure that could allow a non-serializable result, it aborts one of the transactions.

Conceptually:

```text
Traditional lock-based approach:

prevent dangerous access
by blocking it with locks
```

versus PostgreSQL SSI:

```text
allow substantial concurrent snapshot execution

track dependencies

detect dangerous serialization structure

abort one transaction if necessary
```

PostgreSQL does use what its documentation calls predicate locks for SSI, represented as `SIReadLock`, but these are not ordinary blocking locks.

They exist to record read dependencies.

PostgreSQL explicitly states that its Serializable predicate locks do not themselves block other transactions and therefore do not participate in lock deadlocks.

That is very different from SQL Server Serializable key-range locks.

## "Predicate lock" means different things operationally

The terminology can therefore be confusing.

SQL Server Serializable:

```text
range protection
→ conflicting insert can be blocked
```

PostgreSQL Serializable SSI:

```text
predicate/read tracking
→ conflicting work can continue
→ dangerous dependency can later cause serialization failure
```

Both protect serializability.

They do not protect it in the same way.

This is exactly why database isolation should be understood in terms of guarantees and mechanisms rather than assuming that every engine implements one textbook algorithm.

## InnoDB is also not "just 2PL"

InnoDB is a hybrid.

Ordinary consistent reads use MVCC.

For example, a normal:

```sql
SELECT *
FROM products
WHERE id = 100;
```

can read a historical committed row version rather than waiting on a current writer.

But a locking read:

```sql
SELECT *
FROM products
WHERE id = 100
FOR UPDATE;
```

behaves differently.

It acquires locks on relevant records/index entries.

Those locks remain until commit or rollback.

MySQL documents that `FOR SHARE` and `FOR UPDATE` locks are released when the transaction commits or rolls back.

So InnoDB combines:

```text
MVCC snapshot reading
+
pessimistic locking
+
record locks
+
gap / next-key locks
+
deadlock detection
```

It should not be reduced to:

```text
"MySQL uses 2PL."
```

without explaining which operations and isolation mode are being discussed.

## SQL Server is the closest of the three to the textbook locking model

Traditional SQL Server isolation is easier to map onto lock-based theory.

Under pessimistic locking:

```text
READ COMMITTED
```

normally releases read locks after the statement.

Under:

```text
REPEATABLE READ
```

read locks are held longer so rows already read cannot be changed by another transaction before the current transaction ends.

Under:

```text
SERIALIZABLE
```

SQL Server additionally protects key ranges so new qualifying rows cannot appear.

Microsoft's locking documentation describes Repeatable Read as retaining read/write locks and Serializable as adding range locks to prevent phantom reads.

That behavior resembles the textbook progression from row-level locking toward a strict/range-aware locking protocol.

However, modern SQL Server adds an important complication.

## Modern SQL Server and optimized locking

Recent SQL Server versions and Azure SQL can use optimized locking.

Instead of necessarily retaining every physical row/page `X` lock until transaction completion, SQL Server can release many row/page locks earlier and retain a transaction-ID (`TID`) lock representing the uncommitted transaction.

Microsoft describes, for example, an update of many rows where individual row `X` locks may be released after modification while one transaction-level `X` lock remains until the transaction ends.

This means statements such as:

> "SQL Server implements rigorous 2PL by holding every S and X row lock until commit. "

are too simplistic for modern SQL Server.

The observable isolation guarantee matters more than whether each internal physical lock exactly matches the textbook protocol.

This is an important general lesson:

> Textbook 2PL is a model for reasoning about concurrency. Production engines may implement equivalent guarantees using MVCC, dependency tracking, transaction-ID locks, range locks, or combinations of these mechanisms.

## Technology summary

| Technology | Ordinary read mechanism | Explicit locking | Predicate/range protection | Serializable strategy |
|---|---|---|---|---|
| PostgreSQL | MVCC snapshot/read committed versions | `FOR UPDATE`, `FOR NO KEY UPDATE`, `FOR SHARE`, `FOR KEY SHARE` | SSI predicate-read tracking rather than ordinary blocking range locks | Serializable Snapshot Isolation; dangerous dependency can abort a transaction |
| MySQL InnoDB | MVCC consistent reads | `FOR UPDATE`, `FOR SHARE` | Record, gap, and next-key locks depending on operation/isolation | Stronger locking behavior combined with InnoDB MVCC |
| SQL Server | Locking or row versioning depending on configuration | S/U/X locks and locking hints | Key-range locks at locking Serializable | Primarily lock/range-lock based; newer versions can use optimized TID locking |
| Textbook 2PL | Reads acquire S locks | Writes acquire X locks | Requires locking the appropriate logical data item/range | Serializability follows from the growing/shrinking rule |

PostgreSQL's current documentation explicitly identifies its Serializable implementation as SSI rather than traditional blocking serializable locking. MySQL documents its combination of consistent MVCC reads and explicit locking reads. SQL Server documents both its traditional lock-based isolation behavior and its newer optimized-locking mechanism.

## A concrete application example: bank transfer

Consider:

```text
account 1 = €500
account 2 = €300
```

We want to transfer:

```text
€100 from account 1 to account 2
```

The business operation is:

```text
read/check source
debit source
credit destination
```

Both account changes must belong to one transaction.

A PostgreSQL implementation might be:

```sql
BEGIN;

SELECT account_id, balance
FROM accounts
WHERE account_id IN (1, 2)
ORDER BY account_id
FOR UPDATE;

-- Verify:
-- account 1 exists
-- account 2 exists
-- account 1 has at least 100

UPDATE accounts
SET balance = balance - 100
WHERE account_id = 1;

UPDATE accounts
SET balance = balance + 100
WHERE account_id = 2;

COMMIT;
```

The important design decisions are not merely:

```text
"we used FOR UPDATE"
```

but:

```text
both rows are locked before the decision is completed

all transfer code uses the same lock ordering

the debit and credit occur in one transaction

the transaction remains short
```

A useful database constraint may also be appropriate:

```sql
CHECK (balance >= 0)
```

if negative balances are never legal.

Constraints and locks solve different layers of the problem:

```text
locking coordinates concurrent decisions

constraints reject impossible final states
```

Using both can be valuable.

## Why an ordinary PostgreSQL reader can still see the account

Suppose T1 holds:

```text
FOR UPDATE
```

on account `1`.

Another transaction executes:

```sql
SELECT balance
FROM accounts
WHERE account_id = 1;
```

That ordinary PostgreSQL reader is not automatically blocked by the row lock.

Because PostgreSQL uses MVCC, it can read an appropriate committed version.

What is blocked are operations requiring a conflicting row lock or modification.

PostgreSQL documents exactly this distinction: row-level locks block writers and lockers of the same row, but do not prevent ordinary querying.

Therefore the intuition:

```text
X lock exists
→ nobody can even read the row
```

is a textbook-locking intuition that does not directly describe MVCC engines.

## Another concrete example: reserving a seat

Suppose an application stores seats individually:

```text
seat 1
seat 2
seat 3
...
```

To reserve seat 42:

```sql
SELECT *
FROM seats
WHERE seat_id = 42
FOR UPDATE;
```

Then:

```sql
UPDATE seats
SET reserved_by = 1001
WHERE seat_id = 42;
```

This maps naturally to row locking because the logical resource already exists as one row.

The lockable object:

```text
seat 42
```

is explicit.

Now compare a different data model:

```text
event capacity = 100

bookings are separate rows
```

The rule is:

```text
COUNT(bookings WHERE event_id = 5) <= 100
```

There is no single booking row representing:

```text
"the last remaining unit of capacity"
```

Two transactions can both count 99 and insert booking number 100 independently.

The invariant is now predicate-based.

Possible designs include:

```text
lock one event/capacity row and update a counter atomically

use database Serializable isolation

use suitable range locking where the engine supports it

redesign the invariant as a directly lockable or constrained resource
```

This shows why concurrency design depends heavily on the schema.

## A useful design trick: create a row that represents the logical resource

Predicate locking can be complicated.

Sometimes the easiest solution is to transform an abstract invariant into a concrete lockable row.

Instead of repeatedly checking:

```sql
SELECT COUNT(*)
FROM bookings
WHERE event_id = 42;
```

the `events` table might contain:

```text
event_id
capacity
reserved_count
```

Then reservation can use one atomic statement:

```sql
UPDATE events
SET reserved_count = reserved_count + 1
WHERE event_id = 42
  AND reserved_count < capacity;
```

If:

```text
rows affected = 1
```

capacity was successfully reserved.

If:

```text
rows affected = 0
```

the event was already full.

This may be simpler than protecting:

```text
all current and future booking rows
```

with a complex locking protocol.

The broader lesson is:

> Good schema and statement design can remove the need for complicated locking.

## `FOR UPDATE` is not a universal magic phrase

Adding:

```sql
FOR UPDATE
```

does not automatically make every business rule safe.

Consider:

```sql
SELECT *
FROM users
WHERE email = 'alice@example.com'
FOR UPDATE;
```

If no user exists, there may be no existing row to lock.

Two transactions may both conclude:

```text
email is available
```

and both attempt the insert.

The correct solution for uniqueness is normally:

```sql
UNIQUE(email)
```

not relying on a pre-check plus row locking.

Likewise, use:

```text
FOREIGN KEY
```

for referential integrity where appropriate rather than manually reproducing all parent/child locking behavior in application code.

Locking is most useful when the business decision itself cannot be represented directly by a database constraint or atomic statement.

## 2PL versus MVCC

The cleanest contrast is:

| Traditional 2PL intuition | MVCC intuition |
|---|---|
| Reader takes an S lock | Reader often reads a version |
| Writer takes X lock | Writer creates/changes a newer version and uses write-related locks |
| Reader and writer may block each other | Reader may continue from an older committed version |
| Serializability comes from lock ordering | Serializability may come from locks, validation, dependency tracking, or a hybrid |

Neither technique is inherently "better. "

They make different tradeoffs.

Locking tends to discover some conflicts by:

```text
waiting before proceeding
```

Optimistic/MVCC techniques may instead allow more concurrency and discover problems through:

```text
validation
serialization failure
transaction retry
```

Modern databases frequently combine both approaches.

## Blocking versus aborting

Consider two transactions that cannot both safely complete.

A pessimistic lock-based system may behave as:

```text
T1 obtains resource

T2 requests resource
T2 waits

T1 commits

T2 continues
```

An optimistic/SSI-style system can behave more like:

```text
T1 proceeds

T2 proceeds concurrently

database detects incompatible dependency pattern

one transaction aborts

application retries it
```

The application experiences very different operational behavior:

```text
locking → latency from waiting

optimistic detection → retry cost
```

Yet both approaches can provide serializable outcomes.

## Deadlock versus serialization failure

These are also different concepts.

A deadlock means transactions are waiting in a cycle:

```text
T1 waits for T2
T2 waits for T1
```

The database must break the cycle.

A serialization failure means allowing all participating transactions to commit could violate serializable ordering.

There does not have to be a lock-wait cycle.

PostgreSQL Serializable SSI is the clearest example: its dependency tracking can abort a transaction with SQLSTATE `40001` even though its predicate locks themselves do not block.

Therefore:

```text
deadlock retry
```

and:

```text
serialization-failure retry
```

belong to the same broad application pattern but arise for different reasons.

## Retry the complete transaction

When the database aborts a transaction because of a deadlock or serialization conflict, the application should normally retry the transaction from the beginning.

Not:

```text
retry only the UPDATE that failed
```

but:

```text
BEGIN

repeat the reads

repeat the business decision

repeat the writes

COMMIT
```

The earlier reads may no longer be valid.

For example:

```text
read balance = 500
decide €400 debit is safe
```

followed by an aborted transaction cannot safely become:

```text
retry only debit €400
```

because another transaction may have changed the balance before the retry.

PostgreSQL's documentation explicitly recommends retrying the whole transaction for serialization failures and identifies `40P01` deadlock failures as another case applications may retry.

MySQL likewise tells applications encountering InnoDB deadlock error `1213` to run all operations in the transaction again.

## Keep locked transactions short

Locks are held resources.

A dangerous pattern is:

```text
BEGIN

lock customer row

call external HTTP service

wait 5 seconds

ask user for confirmation

perform more queries

COMMIT
```

During the network call or user wait, other transactions may be blocked.

Long lock durations increase:

```text
contention
deadlock probability
tail latency
lock memory consumption
transaction timeout risk
```

PostgreSQL explicitly advises against leaving transactions holding locks while waiting for external/user interaction.

A better design is generally:

```text
perform slow external work outside the database transaction

BEGIN
perform short concurrency-sensitive work
COMMIT
```

When external side effects must be coordinated with database state, patterns such as an outbox or idempotency mechanism are often more appropriate than keeping a database transaction open during the external operation.

## Indexes affect locking behavior

Indexes are not only performance structures.

They can also determine:

```text
which records are scanned

which index keys are touched

which gaps or ranges need protection

how many locks are acquired
```

InnoDB explicitly recommends good indexes as one method of reducing the number of index records scanned and therefore the amount of locking and deadlock exposure.

SQL Server's documented key-range locking also depends on index-based range protection.

Therefore a query changing from:

```text
targeted index lookup
```

to:

```text
large scan
```

can alter not only query cost but also concurrency behavior.

This is one reason concurrency testing must use realistic schema, indexes, and execution plans.

## 2PL and 2PC are completely different

The similar names cause constant confusion.

| Two-Phase Locking | Two-Phase Commit |
|---|---|
| Concurrency-control protocol | Distributed atomic-commit protocol |
| Concerned with acquiring/releasing locks | Concerned with prepare/commit decisions |
| Prevents non-serializable conflicting schedules | Ensures distributed participants agree to commit or abort |
| Phases: growing → shrinking | Phases: prepare → commit/abort |
| Can deadlock | Can suffer coordinator/participant availability problems |
| Usually discussed inside database concurrency control | Usually discussed across multiple resource managers/nodes |

A distributed transaction may use:

```text
2PL for isolation
+
2PC for distributed atomic commit
```

so the presence of one tells you nothing about whether the other is being used.

## What applications control and what databases control

The application typically controls:

```text
where a transaction begins and ends

which statements execute inside it

which explicit locking clauses are requested

which isolation level is chosen

the order in which logical resources are accessed

how deadlocks/serialization failures are retried
```

The database engine typically controls:

```text
the concrete lock manager

lock compatibility

physical row/page/index/range locks

MVCC version visibility

wait queues

deadlock detection

lock escalation or optimized locking

which transaction becomes a deadlock victim
```

The division matters.

An application saying:

```sql
SELECT ... FOR UPDATE;
```

expresses a locking requirement.

It does not generally dictate every internal lock object or storage-level mechanism the engine will use.

## `NOLOCK` is not "use smaller locks"

SQL Server's:

```sql
WITH (NOLOCK)
```

is often badly named in informal explanations.

It does not mean:

```text
please use more lightweight row locks
```

It changes the read semantics approximately to `READ UNCOMMITTED` for the referenced data.

That can allow dirty/inconsistent reads.

It is therefore an isolation choice, not a lock-granularity tuning switch.

Microsoft's own locking documentation shows that using `NOLOCK` can bypass the key-range locks that would otherwise be needed for Serializable behavior, meaning serializability is no longer guaranteed for that access.

## Practical comparison of concurrency strategies

| Problem | Common mechanism |
|---|---|
| Two transactions update exactly the same row | Exclusive/write lock or optimistic version check |
| Read a row, then make a decision before updating it | Locking read such as `FOR UPDATE`, or atomic conditional update |
| Prevent duplicate logical value | `UNIQUE` constraint |
| Prevent negative quantity | `CHECK`, atomic conditional update, or appropriate locking |
| Protect a range against new matching rows | Range/gap/next-key locks or Serializable predicate protection |
| Multi-row business invariant | Explicit locking protocol or Serializable isolation |
| Deadlock | Database aborts a victim; application retries |
| Serializable dependency conflict | Database rejects an execution; application retries |
| Long reader should not block writers | MVCC / row-versioning approach |
| Need deterministic resource acquisition | Canonical lock ordering |

## The most useful mental model

Do not memorize 2PL as:

```text
phase 1 = lock
phase 2 = unlock
```

That is technically correct but not very useful.

Remember:

```text
A transaction is allowed to expand
the set of resources it depends on.

Once it begins giving resources back,
it may never expand that dependency set again.
```

Why?

Because that creates a single ordering point for the transaction.

Conflicting transactions can then be ordered by their lock points.

That prevents dependency cycles.

Then remember the variants:

```text
Basic 2PL
    solves conflict serializability

Strict 2PL
    additionally keeps uncommitted writes protected

Rigorous 2PL
    holds all read/write locks until transaction end

Conservative 2PL
    obtains the required lock set up front
    to avoid incremental lock deadlocks
```

Finally, remember that real systems are hybrids:

```text
PostgreSQL
    MVCC ordinary reads
    explicit row locks when requested
    SSI for Serializable

MySQL InnoDB
    MVCC consistent reads
    row/index locking
    gap and next-key locking

SQL Server
    traditional pessimistic locking
    key-range locking at Serializable
    row versioning options
    modern optimized TID locking
```

The important question is therefore not:

```text
"Does this database use 2PL?"
```

but:

> For this operation and isolation level, what is being protected, how is it protected, when is that protection released, and what happens when two transactions conflict?

That question transfers directly from textbook theory to production systems.

## References

PostgreSQL's explicit-locking documentation describes its table and row lock modes, `FOR UPDATE` behavior, transaction-end lock release, and automatic deadlock detection.

PostgreSQL's transaction-isolation documentation explains that Serializable uses Serializable Snapshot Isolation, including nonblocking predicate locks used to detect dangerous dependencies rather than traditional blocking range locking.

MySQL's InnoDB locking documentation describes its combination of MVCC, record locks, gap/next-key locking, locking reads, and deadlock handling.

Microsoft's SQL Server locking documentation describes shared/exclusive locking, Repeatable Read behavior, Serializable key-range protection, deadlock handling, and modern optimized TID locking.
