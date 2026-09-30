# Serializable and Repeatable Read

## 1. Why transaction isolation exists

Imagine two requests hit an application at almost exactly the same time.

Both requests:

1. read the database,
2. make a decision based on what they read,
3. change the database,
4. commit.

The dangerous part is not simply that they run concurrently. Databases are specifically designed to allow concurrency.

The dangerous part is that each transaction can make a locally reasonable decision based on an incomplete view of what the other transaction is doing.

For example, suppose a hospital requires:

> At least one doctor must always remain on call.

Initially:

| Doctor | On call |
|---|---: |
| Alice | Yes |
| Bob | Yes |

Two requests execute concurrently:

| Transaction T1 | Transaction T2 |
|---|---|
| Reads: Alice + Bob are on call | Reads: Alice + Bob are on call |
| Decides Alice can leave | Decides Bob can leave |
| Sets Alice `on_call = false` | Sets Bob `on_call = false` |
| Commits | Commits |

The final state is:

| Doctor | On call |
|---|---: |
| Alice | No |
| Bob | No |

Neither transaction individually did anything irrational. Each saw another doctor available.

The problem is that the two decisions were not safe when combined.

Transaction isolation determines which of these concurrent interactions a transaction is allowed to observe and which outcomes the database must prevent.

# 2. The central distinction: Repeatable Read versus Serializable

The most useful mental model is:

> Repeatable Read asks: "Will my view remain stable? "
> Serializable asks: "Could the committed result have happened if the transactions had run one at a time? "

Those are different guarantees.

A database can give a transaction a perfectly stable snapshot while still allowing two transactions to make incompatible decisions from that snapshot.

PostgreSQL is an especially clear example. Its Repeatable Read implementation gives the transaction a stable snapshot and even prevents ordinary phantom reads, but serialization anomalies can still occur. Serializable adds additional detection specifically to prevent committed results that have no valid serial ordering.

# 3. What does "serial execution" mean?

Suppose there are two transactions, `T1` and `T2`.

A serial execution means one finishes before the other starts:

```text
T1 → COMMIT → T2 → COMMIT
```

or:

```text
T2 → COMMIT → T1 → COMMIT
```

Serializable isolation does not require the database to literally execute transactions one at a time.

The database can still execute:

```text
T1 ──────────────┐
      T2 ──────────────┐
T1 ─────── COMMIT      │
      T2 ─────── COMMIT
```

The requirement is that the final committed result must be equivalent to some legal serial order.

In the doctors example, no serial ordering produces both doctors off call.

If Alice's transaction ran first:

```text
Alice sees:
Alice = on
Bob   = on

Alice goes off call.
```

Bob's transaction would then see:

```text
Alice = off
Bob   = on
```

and should refuse to take Bob off call.

The reverse ordering has the same effect.

Therefore:

```text
Alice = off
Bob   = off
```

cannot be explained by any serial execution.

That is a serialization anomaly.

# 4. The concurrency anomalies you need to recognize

| Anomaly | What happens | Concrete example |
|---|---|---|
| Dirty read | A transaction reads another transaction's uncommitted change. | T1 changes an account balance to €0 but later rolls back. T2 temporarily reads €0. |
| Non-repeatable read | The same row returns a different value when read again. | T1 reads product price €100. T2 commits price €120. T1 reads again and gets €120. |
| Phantom read | Repeating a predicate query returns a different set of rows. | T1 queries all unpaid invoices. T2 inserts another unpaid invoice. T1 repeats the query and sees an extra row. |
| Lost update | One write effectively overwrites another concurrent decision. | Two requests read `counter = 10`, calculate 11, and both write 11 instead of reaching 12. |
| Write skew | Transactions read overlapping business-rule data but update different rows, jointly violating a rule. | Two doctors both see another doctor available and independently go off call. |
| Serialization anomaly | The final committed state cannot be explained by any serial ordering of the transactions. | The doctors example is one form of serialization anomaly. |

An important distinction is that write skew usually does not involve two transactions updating the same row.

That is why ordinary row-conflict detection is insufficient.

# 5. Why Repeatable Read sounds stronger than it actually is

Suppose a transaction starts and sees:

```text
Alice = on
Bob   = on
```

Under snapshot-based Repeatable Read, it can continue seeing exactly that snapshot throughout the transaction.

That sounds extremely safe.

But consider two transactions.

### Transaction T1

```sql
SELECT *
FROM doctors
WHERE on_call = true;
```

Result:

```text
Alice
Bob
```

T1 decides Alice can leave:

```sql
UPDATE doctors
SET on_call = false
WHERE name = 'Alice';
```

### Transaction T2

At approximately the same time:

```sql
SELECT *
FROM doctors
WHERE on_call = true;
```

T2 also sees:

```text
Alice
Bob
```

and executes:

```sql
UPDATE doctors
SET on_call = false
WHERE name = 'Bob';
```

The writes touch different rows:

```text
T1 writes Alice
T2 writes Bob
```

A system checking only for:

```text
"Did T1 and T2 modify the same row?"
```

finds no conflict.

Both can commit.

This is the essential weakness of Snapshot Isolation / snapshot-style Repeatable Read:

> A stable snapshot protects what an individual transaction sees. It does not automatically validate the decisions that multiple transactions make from those snapshots.

PostgreSQL explicitly documents this distinction: Repeatable Read provides a stable database view but that view is not necessarily consistent with a serial execution of concurrent transactions.

# 6. A second real-world example: overselling capacity

Consider an event with ten available seats.

Instead of representing every physical seat separately, the application checks how many bookings exist:

```sql
SELECT COUNT(*)
FROM bookings
WHERE event_id = 42;
```

Suppose there are currently nine bookings.

Two customers attempt to buy the final seat.

### Transaction A

```text
COUNT = 9
9 < 10
Therefore inserting one booking is safe.
```

### Transaction B

At the same time:

```text
COUNT = 9
9 < 10
Therefore inserting one booking is safe.
```

They insert different booking rows:

```sql
INSERT INTO bookings(event_id, customer_id)
VALUES (42, 1001);
```

and:

```sql
INSERT INTO bookings(event_id, customer_id)
VALUES (42, 2002);
```

Both transactions can individually appear valid.

The result is:

```text
11 bookings
10-seat capacity
```

The business rule:

```text
COUNT(bookings) <= capacity
```

has been violated.

A stable snapshot alone does not solve the problem because both transactions legitimately saw the old count.

This pattern appears in:

| Domain | Business rule |
|---|---|
| Ticketing | Reservations must not exceed capacity |
| Warehouses | Allocated stock must not exceed available stock |
| Banking | Combined exposure must remain below a credit limit |
| Scheduling | At least one employee must cover a shift |
| Resource allocation | Allocated CPU/storage/quota must remain below a maximum |
| Approval workflows | A document must not end up with mutually incompatible approvals |
| Multiplayer / bidding systems | A unique logical resource must not be allocated twice |

# 7. Repeatable Read is not one universal behavior

This is one of the most important practical points.

The SQL isolation-level names describe guarantees, but actual database engines implement them differently.

In particular:

```text
PostgreSQL Repeatable Read
≠
MySQL InnoDB Repeatable Read
≠
SQL Server Repeatable Read
```

You therefore cannot safely read:

```text
Isolation = REPEATABLE READ
```

in application configuration and infer its exact behavior without knowing the database engine.

# 8. Technology summary

| Technology | What Repeatable Read means in practice | Ordinary phantom reads? | Can snapshot-style serialization anomalies remain? | How Serializable is implemented |
|---|---|---: |---: |---|
| PostgreSQL | One stable MVCC snapshot for the transaction; effectively Snapshot Isolation | No | Yes | Serializable Snapshot Isolation: tracks read/write dependencies and aborts transactions when necessary |
| MySQL InnoDB | Plain `SELECT` uses a stable snapshot; locking reads/writes use locking/current-read behavior | Plain snapshot reads remain stable; locking range operations use gap/next-key locking | Yes if decisions are made using ordinary snapshot reads without protecting the invariant | Stronger locking; plain `SELECT` becomes a shared locking read in normal explicit Serializable transactions |
| SQL Server | Shared locks on rows that were read are held until transaction end | Yes | Different behavior from snapshot isolation; row locking may block/deadlock competing updates | Key-range locks prevent inserts/updates into ranges previously read |
| SQL Server SNAPSHOT | Separate isolation level using row versions and a transaction-level snapshot | No | Yes; it is not equivalent to Serializable | Use `SERIALIZABLE` or explicit locking/constraints when the invariant requires it |

PostgreSQL explicitly identifies its Repeatable Read implementation as Snapshot Isolation and Serializable as Serializable Snapshot Isolation. MySQL InnoDB documents that plain Repeatable Read `SELECT`s share a snapshot, while locking reads and writes use different locking rules including gap and next-key locks. SQL Server instead defines Repeatable Read primarily through locks held on rows and Serializable through additional key-range locking.

# 9. PostgreSQL: Repeatable Read

PostgreSQL's implementation is particularly important because it is stronger than the minimum SQL-standard definition of Repeatable Read.

At Repeatable Read:

```sql
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
```

the transaction essentially gets one database snapshot.

Suppose customer `1` currently has five orders.

### T1

```sql
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;

SELECT *
FROM orders
WHERE customer_id = 1;
```

Result:

```text
5 rows
```

Meanwhile T2 executes:

```sql
INSERT INTO orders(customer_id, ...)
VALUES (1, ...);

COMMIT;
```

There are now six committed rows globally.

T1 repeats:

```sql
SELECT *
FROM orders
WHERE customer_id = 1;
```

T1 still sees:

```text
5 rows
```

because it continues using its earlier snapshot.

PostgreSQL therefore prevents an ordinary phantom read at Repeatable Read even though the SQL standard does not require Repeatable Read to do so.

# 10. PostgreSQL Repeatable Read still does not mean Serializable

Return to the doctor example.

Two PostgreSQL transactions can both start at Repeatable Read:

```sql
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
```

Both execute:

```sql
SELECT COUNT(*)
FROM doctors
WHERE on_call = true;
```

Both see:

```text
2
```

T1:

```sql
UPDATE doctors
SET on_call = false
WHERE id = 1;
```

T2:

```sql
UPDATE doctors
SET on_call = false
WHERE id = 2;
```

They modified different rows.

The stable snapshots themselves do not tell PostgreSQL that:

```text
"at least one doctor must remain on call"
```

is the logical dependency connecting those writes.

This is the classic reason why Snapshot Isolation is not the same as Serializable isolation.

# 11. PostgreSQL Serializable: how the problem is solved

PostgreSQL's Serializable level is implemented using Serializable Snapshot Isolation (SSI).

```sql
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
```

The database still uses MVCC snapshots.

It does not simply put a giant lock around the database.

Instead, PostgreSQL additionally monitors dependencies between concurrent transactions.

Conceptually, PostgreSQL asks:

```text
T1 read something that T2 changed.
T2 read something that T1 changed.

Could allowing both transactions to commit produce
a result impossible under every serial ordering?
```

If PostgreSQL detects a dangerous dependency structure, one transaction is aborted.

An application may receive an error such as:

```text
ERROR:
could not serialize access due to
read/write dependencies among transactions
```

Serializable failures use SQLSTATE:

```text
40001
```

PostgreSQL's documentation explains that Serializable behaves like Repeatable Read plus monitoring for conditions that could make the execution inconsistent with every possible serial ordering. It uses predicate-lock information such as `SIReadLock` entries to track relevant dependencies; these predicate locks are used for conflict detection rather than ordinary blocking.

The important consequence is:

> PostgreSQL may deliberately abort a transaction even though the SQL statements themselves were individually valid.

That abort is the mechanism protecting correctness.

# 12. Why PostgreSQL's predicate locks are different from normal locks

The phrase predicate lock can be confusing.

Suppose the application reads:

```sql
SELECT COUNT(*)
FROM bookings
WHERE event_id = 42;
```

The logical thing being depended on is not necessarily one row.

It is effectively:

```text
"the set of rows satisfying event_id = 42"
```

A transaction that later inserts another matching booking can affect the truth of the first transaction's decision.

PostgreSQL Serializable needs to recognize this dependency.

Its SSI mechanism therefore tracks what transactions have read sufficiently to detect dangerous read/write relationships. These `SIReadLock` predicate locks do not behave like ordinary row locks that simply block another writer. PostgreSQL documents them as part of its serialization-anomaly detection system.

# 13. PostgreSQL Serializable does not mean "no concurrency"

This misconception is common:

```text
Serializable = only one transaction can run
```

That is false.

For example:

```text
T1 reads customers
T2 reads products
T3 modifies invoices
T4 modifies an unrelated account
```

can still proceed concurrently.

Serializable determines which combinations may successfully commit.

If concurrent execution is equivalent to:

```text
T2 → T1 → T4 → T3
```

then the database can allow all of them to commit.

If no possible ordering explains the result, PostgreSQL aborts one of the participating transactions.

# 14. MySQL InnoDB: Repeatable Read is a hybrid you must understand

MySQL's InnoDB engine defaults to:

```text
REPEATABLE READ
```

For ordinary non-locking `SELECT`s, a transaction uses a consistent snapshot established by its first consistent read.

For example:

```sql
START TRANSACTION;

SELECT *
FROM orders
WHERE customer_id = 1;
```

If this establishes a snapshot containing five orders, another ordinary `SELECT` later in the same transaction normally continues to see that snapshot.

MySQL documents this behavior explicitly.

However, there is a crucial complication.

These statements are locking operations:

```sql
SELECT ... FOR UPDATE;

SELECT ... FOR SHARE;

UPDATE ...;

DELETE ...;
```

They do not behave exactly like the earlier non-locking snapshot read.

MySQL explicitly warns that mixing non-locking snapshot reads with locking statements inside the same Repeatable Read transaction can expose two different notions of database state and can be difficult to reason about.

# 15. MySQL example: snapshot read versus locking read

Suppose a transaction does:

```sql
START TRANSACTION;

SELECT *
FROM products
WHERE id = 100;
```

That ordinary `SELECT` may come from the transaction's snapshot.

Another transaction changes product `100` and commits.

Your transaction then executes:

```sql
SELECT *
FROM products
WHERE id = 100
FOR UPDATE;
```

This is not simply another read of exactly the same historical snapshot.

It is a locking operation intended to find and lock the relevant current row.

That is why code such as:

```text
ordinary SELECT
business decision
SELECT FOR UPDATE
UPDATE
```

must be understood much more carefully than:

```text
"Everything is Repeatable Read, therefore every operation
must be seeing exactly the same version."
```

That inference is wrong for InnoDB.

# 16. MySQL gap locks and next-key locks

Suppose the transaction executes:

```sql
SELECT *
FROM bookings
WHERE event_id = 42
FOR UPDATE;
```

A problem remains if the database locks only the currently existing rows.

Imagine bookings with IDs:

```text
100
101
102
```

Another transaction could potentially insert:

```text
103
```

which did not exist when the first transaction acquired its row locks.

For indexed range operations, InnoDB can use gap locks and next-key locks.

These protect not just existing records but also relevant gaps in an index so that another transaction cannot freely create a new matching record inside the protected range.

MySQL's documentation describes next-key/gap locking for locking reads and range scans under Repeatable Read.

This is one reason good indexing is not merely a query-performance concern in InnoDB concurrency control: the index range scanned can affect what gets locked.

# 17. MySQL Serializable

At InnoDB Serializable isolation, behavior becomes more lock-oriented.

For explicit transactions with autocommit disabled, MySQL documents that plain:

```sql
SELECT ...
```

is effectively converted into a shared locking read:

```sql
SELECT ... FOR SHARE;
```

This prevents the application from treating ordinary reads as harmless historical observations while simultaneously making decisions that need serializable protection.

That means MySQL's implementation strategy is quite different from PostgreSQL's SSI.

A simplified comparison is:

```text
PostgreSQL Serializable
    run concurrently using snapshots
    detect dangerous dependency structures
    abort when necessary

MySQL InnoDB Serializable
    make reads more strongly locking
    make conflicting transactions wait
    possibly encounter deadlocks
```

Both aim to enforce stronger correctness, but the operational behavior can be very different.

# 18. SQL Server Repeatable Read

SQL Server uses yet another model for its traditional Repeatable Read level.

At:

```sql
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;

BEGIN TRANSACTION;
```

when the transaction reads existing rows, SQL Server keeps shared locks on those rows until the transaction finishes.

Therefore, another transaction cannot normally modify those already-read rows while the first transaction remains active.

But there is an important limitation:

> Repeatable Read protects the rows that were read, not necessarily the gaps where new matching rows could appear.

Microsoft documents that Repeatable Read does not use the range locks necessary to prevent phantom rows.

# 19. SQL Server phantom example

Suppose:

```sql
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;

BEGIN TRANSACTION;

SELECT *
FROM orders
WHERE customer_id = 1;
```

returns five rows.

SQL Server keeps appropriate shared locks on those existing rows.

But T2 may be able to insert a new order:

```sql
INSERT INTO orders(customer_id, ...)
VALUES (1, ...);

COMMIT;
```

T1 repeats:

```sql
SELECT *
FROM orders
WHERE customer_id = 1;
```

and can now see six rows.

No previously read row needed to change.

A new matching row appeared.

That is the classic phantom problem.

# 20. SQL Server Serializable: range locking

SQL Server Serializable closes this gap with key-range locks.

Suppose T1 executes:

```sql
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

BEGIN TRANSACTION;

SELECT *
FROM orders
WHERE customer_id = 1;
```

SQL Server protects the relevant key range.

A concurrent transaction trying to insert another row whose key falls inside that protected range may have to wait.

Microsoft describes Serializable as preventing another transaction from inserting key values that fall inside ranges previously read by the current transaction, with those range locks held until the transaction completes.

The strategy is therefore approximately:

```text
PostgreSQL:
detect dangerous dependency → abort one transaction

SQL Server:
protect key range → make conflicting transaction wait
```

Both can produce serializable behavior while using very different mechanisms.

# 21. Do not confuse SQL Server SNAPSHOT with SQL Server REPEATABLE READ

SQL Server additionally provides:

```text
SNAPSHOT
```

as a separate isolation level.

This is important because discussions about database isolation often casually use:

```text
Repeatable Read
Snapshot Isolation
```

as though they were synonyms.

They are not synonyms in SQL Server.

Traditional SQL Server Repeatable Read is primarily lock-based.

SQL Server SNAPSHOT uses row versioning so that a transaction observes a transactionally consistent historical view.

Microsoft's documentation explicitly treats `SNAPSHOT` as a separate level from `REPEATABLE READ` and `SERIALIZABLE`.

A stable SNAPSHOT still should not automatically be interpreted as:

```text
"every cross-row business invariant is serializable"
```

because snapshot isolation and serializable isolation solve different problems.

# 22. Same SQL isolation name, three different implementations

Consider:

```sql
SELECT *
FROM orders
WHERE customer_id = 1;
```

followed by a concurrent insert.

## PostgreSQL Repeatable Read

T1:

```text
5 rows
```

T2 inserts row 6 and commits.

T1 repeats:

```text
5 rows
```

because T1 keeps using its transaction snapshot.

## MySQL InnoDB Repeatable Read, ordinary SELECT

The basic outcome is similar:

```text
5 rows
```

because ordinary consistent reads use the transaction snapshot.

But locking reads and writes introduce different current/locking semantics that must be understood separately.

## SQL Server Repeatable Read

T1 can observe:

```text
6 rows
```

because locks protect the rows already read but Repeatable Read does not generally protect the entire search range from inserts.

This is why statements such as:

> "Repeatable Read prevents phantom reads. "

or:

> "Repeatable Read allows phantom reads. "

are incomplete unless the database engine is specified.

# 23. Summary: phantom behavior

| Isolation / technology | Repeating `WHERE customer_id = 1` after another transaction inserts a matching row |
|---|---|
| PostgreSQL `READ COMMITTED` | New row can appear |
| PostgreSQL `REPEATABLE READ` | New row does not appear in ordinary snapshot read |
| PostgreSQL `SERIALIZABLE` | Serializable semantics; incompatible patterns may cause transaction abort |
| MySQL InnoDB `READ COMMITTED` | Each consistent read gets a fresh snapshot; new row can appear |
| MySQL InnoDB `REPEATABLE READ`, ordinary SELECT | Stable snapshot; new row normally does not appear |
| MySQL locking range read | Relevant next-key/gap locking can block matching inserts |
| SQL Server `REPEATABLE READ` | New matching rows can appear |
| SQL Server `SNAPSHOT` | Historical transaction snapshot remains stable |
| SQL Server `SERIALIZABLE` | Key-range locking prevents conflicting inserts into the read range |

MySQL documents that Repeatable Read consistent reads share a snapshot, while `READ COMMITTED` creates a fresh snapshot per consistent read and locking range operations can use gap/next-key locks. SQL Server documents the distinction between Repeatable Read and Serializable specifically in terms of whether key ranges are protected.

# 24. The most important application question: what invariant are you protecting?

Choosing an isolation level should start from the business rule, not from the name of the isolation level.

Examples:

```text
balance >= 0
```

```text
COUNT(bookings) <= capacity
```

```text
at least one doctor is on call
```

```text
total_credit_exposure <= customer_limit
```

```text
only one active subscription of this type exists
```

```text
stock_reserved <= stock_available
```

Then ask:

```text
Can two transactions each independently verify this condition
and modify different rows in a way that jointly breaks it?
```

If yes, a stable snapshot alone may not be sufficient.

# 25. Sometimes the right solution is a database constraint, not Serializable

Do not solve every concurrency problem by switching the entire application to Serializable.

Suppose the rule is:

```text
username must be unique
```

Do not implement:

```sql
SELECT COUNT(*)
FROM users
WHERE username = 'alice';
```

followed by:

```text
if count == 0:
    INSERT ...
```

and depend on transaction isolation.

Instead create:

```sql
CREATE UNIQUE INDEX users_username_uq
ON users(username);
```

Now the database directly represents the invariant.

Likewise:

```text
quantity >= 0
```

may be expressible with a `CHECK` constraint.

Foreign-key relationships should normally use:

```sql
FOREIGN KEY
```

rather than an application doing:

```text
SELECT parent
then later INSERT child
```

without database enforcement.

A useful principle is:

> If the invariant can be expressed directly as a database constraint, prefer the constraint.

Serializable isolation becomes especially valuable for multi-row or predicate-based invariants that cannot easily be represented by a simple uniqueness, foreign-key, or check constraint.

# 26. Another solution: atomic conditional UPDATE

Consider inventory.

Naive implementation:

```sql
SELECT available_stock
FROM products
WHERE id = 42;
```

Application:

```text
if stock >= 1:
    stock = stock - 1
```

Then:

```sql
UPDATE products
SET available_stock = ?
WHERE id = 42;
```

That separates:

```text
check
```

from:

```text
write
```

and creates room for concurrency bugs.

A safer design can combine them:

```sql
UPDATE products
SET available_stock = available_stock - 1
WHERE id = 42
  AND available_stock >= 1;
```

Then inspect:

```text
rows affected
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

there was no available stock.

This often gives a much simpler correctness argument than:

```text
read → decide → write
```

because the condition and modification are handled atomically against the same row.

# 27. Another solution: explicit row locking

Suppose an operation must read an account before deciding how to modify it.

Instead of:

```sql
SELECT *
FROM accounts
WHERE id = 100;
```

use:

```sql
SELECT *
FROM accounts
WHERE id = 100
FOR UPDATE;
```

The intention is:

```text
I am not merely looking at this row.
I am reading it because I am about to make a decision
whose correctness depends on nobody changing it underneath me.
```

This technique is useful for well-defined row-level resources.

But it becomes harder when the invariant depends on:

```text
all rows satisfying a predicate
```

or:

```text
several tables
```

or:

```text
rows that do not exist yet
```

At that point you need to understand range/predicate locking or use Serializable isolation.

# 28. Fixing the doctors example with explicit locking

Instead of:

```sql
SELECT *
FROM doctors
WHERE on_call = true;
```

the transaction could deliberately lock the relevant rows:

```sql
SELECT *
FROM doctors
WHERE on_call = true
FOR UPDATE;
```

Then decide whether the selected doctor may leave.

Because competing transactions follow the same locking protocol, one transaction must wait for the other instead of independently making its decision from the same old state.

However, this is only safe if:

```text
every piece of code modifying this invariant follows the protocol
```

If one service uses `FOR UPDATE` but another service simply executes:

```sql
UPDATE doctors
SET on_call = false
...
```

without respecting the same design, the application's correctness argument can collapse.

Serializable isolation can sometimes simplify this because the database validates interactions between participating Serializable transactions rather than requiring application code to manually predict every conflicting access pattern.

# 29. Serializable transactions require retry logic

Serializable does not mean:

```text
BEGIN
do stuff
COMMIT
always succeeds
```

The database may intentionally reject the transaction because allowing it to commit would violate serializable execution.

For PostgreSQL this commonly appears as:

```text
SQLSTATE 40001
```

The correct algorithm is conceptually:

```text
for limited number of attempts:

    begin transaction

    perform ALL reads
    make decision
    perform writes

    try commit

    if serialization failure:
        rollback
        retry entire transaction
    else:
        success
```

The important phrase is:

> retry the entire transaction

PostgreSQL's documentation specifically instructs applications encountering these concurrency failures to restart the transaction from the beginning so that its reads and decisions are recomputed from an appropriate state.

# 30. Why retrying only the UPDATE is wrong

Suppose the transaction originally did:

```text
READ:
2 doctors are on call

DECISION:
Alice may leave

WRITE:
Alice = off
```

If PostgreSQL aborts because the decision was no longer serializable, this is wrong:

```text
retry only:
UPDATE Alice = off
```

The decision:

```text
Alice may leave
```

came from the old transaction.

The retry must perform:

```text
READ AGAIN
DECIDE AGAIN
WRITE AGAIN
```

because the database state may now be:

```text
Alice = on
Bob   = off
```

and the correct decision is therefore different.

# 31. Be careful with external side effects during retries

Suppose a Serializable transaction does:

```text
1. read database
2. send confirmation email
3. update database
4. COMMIT
```

and step 4 fails with a serialization error.

The application retries.

Now it may send the email again.

The database rollback cannot undo:

```text
HTTP API request
email
payment-provider call
Kafka publication already acknowledged externally
SMS
```

because those effects occurred outside the database transaction.

A common architecture is an outbox pattern.

Instead of:

```text
database transaction
    update order
    call email service
commit
```

do:

```text
database transaction
    update order

    INSERT INTO outbox(
        event_type,
        payload
    )

commit
```

A separate worker later processes the committed outbox row.

Now a serialization retry rolls back both:

```text
order change
outbox event
```

together.

Idempotency keys can provide additional protection when talking to payment providers and other external APIs.

# 32. PostgreSQL syntax

## Stable snapshot

```sql
BEGIN TRANSACTION
ISOLATION LEVEL REPEATABLE READ;

SELECT *
FROM orders
WHERE customer_id = 1;

-- Other transactions may commit here.

SELECT *
FROM orders
WHERE customer_id = 1;

COMMIT;
```

The ordinary reads continue to use the transaction snapshot.

## Serializable

```sql
BEGIN TRANSACTION
ISOLATION LEVEL SERIALIZABLE;

SELECT COUNT(*)
FROM doctors
WHERE on_call = true;

UPDATE doctors
SET on_call = false
WHERE id = 1;

COMMIT;
```

The application must be prepared for the commit or one of the statements to fail with a serialization error and retry the transaction.

# 33. MySQL InnoDB syntax

## Repeatable Read

```sql
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;

START TRANSACTION;

SELECT *
FROM orders
WHERE customer_id = 1;

SELECT *
FROM orders
WHERE customer_id = 1;

COMMIT;
```

InnoDB's default isolation level is Repeatable Read, and ordinary consistent reads within the transaction use the transaction's snapshot.

## Lock rows that drive a decision

```sql
START TRANSACTION;

SELECT *
FROM doctors
WHERE on_call = true
FOR UPDATE;

UPDATE doctors
SET on_call = false
WHERE id = 1;

COMMIT;
```

## Serializable

```sql
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

START TRANSACTION;

SELECT *
FROM doctors
WHERE on_call = true;

UPDATE doctors
SET on_call = false
WHERE id = 1;

COMMIT;
```

For an explicit Serializable transaction, InnoDB makes ordinary reads more strongly locking rather than treating every `SELECT` as an ordinary historical snapshot read.

# 34. SQL Server syntax

## Repeatable Read

```sql
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;

BEGIN TRANSACTION;

SELECT *
FROM orders
WHERE customer_id = 1;

COMMIT TRANSACTION;
```

Existing rows read by the transaction remain protected by shared locks, but new matching rows are not generally excluded because Repeatable Read does not use the key-range protection of Serializable.

## Serializable

```sql
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

BEGIN TRANSACTION;

SELECT *
FROM orders
WHERE customer_id = 1;

COMMIT TRANSACTION;
```

Here SQL Server can acquire key-range locks so that another transaction cannot freely insert rows into the range protected by the query until the first transaction finishes.

# 35. What happens under contention?

Stronger isolation does not make conflicts disappear.

It changes how conflicts are handled.

| Mechanism | Typical consequence |
|---|---|
| Ordinary row locking | One transaction waits |
| Range / gap locking | Inserts or updates in a protected range wait |
| Deadlock detection | Database chooses a transaction to abort |
| PostgreSQL SSI | Dangerous dependency causes serialization failure |
| Optimistic concurrency control | Version/check failure forces application retry |
| Unique/check constraint | Invalid write is rejected |

So when somebody says:

> "Serializable is slower. "

that is too vague to be useful.

The real questions are:

```text
How often do transactions conflict?
How long are transactions open?
How many rows/ranges do they touch?
Do they block or abort?
What is the retry rate?
Are indexes allowing narrow access paths?
Is the application doing network calls while holding a transaction open?
```

A workload with short, mostly independent transactions can behave very differently from one where hundreds of requests compete for the same logical resource.

# 36. A practical decision table

| Situation | Usually consider |
|---|---|
| Simple reporting requiring a stable point-in-time view | Snapshot / Repeatable Read depending on database |
| Prevent one known row from changing during a decision | `SELECT. .. FOR UPDATE` or an atomic conditional update |
| Unique username/email/order number | `UNIQUE` constraint |
| Parent-child integrity | `FOREIGN KEY` |
| Simple value invariant on one row | `CHECK` constraint or atomic update |
| Capacity/inventory represented by one counter row | Atomic conditional `UPDATE` can often be simplest |
| Invariant spans several rows | Explicit locking protocol or Serializable |
| Invariant depends on a query/predicate | Serializable is often easier to reason about |
| Several independent services can modify the same invariant | Prefer database-enforced rules or Serializable over informal application conventions |
| Long-running analytical read | Snapshot-style reading may be preferable to extensive locks |

This is a design table, not a universal prescription. The exact solution depends on how the invariant is represented and how every writer interacts with it.

# 37. The easiest way to reason about isolation problems

For every concurrency-sensitive operation, write down four things.

### 1. What did the transaction read?

Example:

```sql
SELECT *
FROM doctors
WHERE on_call = true;
```

### 2. What decision did it derive?

```text
There are at least two doctors,
therefore one may leave.
```

### 3. What did it write?

```sql
UPDATE doctors
SET on_call = false
WHERE id = ?;
```

### 4. Could another transaction make the same decision concurrently while writing somewhere else?

If yes, you may have:

```text
write skew
predicate conflict
serialization anomaly
```

even if neither transaction modifies the same row.

This method is usually more useful than trying to memorize isolation-level definitions.

# 38. The main conceptual trap

The following reasoning is wrong:

```text
I use Repeatable Read.

Therefore my transaction always sees consistent data.

Therefore decisions based on that data are safe.

Therefore two concurrent transactions cannot violate
a business invariant.
```

The first part may be true for a snapshot-based database.

The conclusion does not follow.

Correct reasoning is:

```text
Repeatable Read may give each transaction
an internally stable view.

But two different transactions can have
compatible-looking individual snapshots
while making mutually incompatible decisions.

Serializable additionally constrains
the combined committed execution.
```

# 39. Database implementations compared

| Database | Core technique | Repeatable Read | Serializable |
|---|---|---|---|
| PostgreSQL | MVCC | Snapshot Isolation; stable snapshot, no ordinary phantoms, but serialization anomalies remain possible | SSI: MVCC + dependency/predicate tracking + transaction aborts |
| MySQL InnoDB | MVCC + row/index locking | Stable ordinary consistent reads; locking reads/writes use record, gap, and next-key locking | Stronger locking semantics; explicit transactions make ordinary reads shared locking reads |
| SQL Server | Locks plus optional row versioning | Shared locks on rows retained until transaction end; phantoms remain possible | Shared/exclusive locking plus key-range locks |
| SQL Server SNAPSHOT | Row versioning | Separate isolation mode rather than SQL Server's Repeatable Read | Still distinct from lock-based Serializable |

PostgreSQL documents that Serializable builds on Snapshot Isolation by adding serialization-anomaly detection. MySQL documents its combination of transaction snapshots with record/gap/next-key locking and its stronger behavior under Serializable. Microsoft documents SQL Server's transition from row protection at Repeatable Read to range protection at Serializable.

# 40. Final mental model

Do not memorize:

```text
Repeatable Read = good
Serializable = better
```

Memorize this instead:

```text
READ COMMITTED
    "What is committed when this statement runs?"

REPEATABLE READ / SNAPSHOT-STYLE READING
    "Give this transaction a stable view."

SERIALIZABLE
    "Only allow committed results that can be explained
     as some one-at-a-time execution."
```

Then remember that the implementation differs:

```text
PostgreSQL:
    stable MVCC snapshot
    +
    dependency detection
    +
    abort/retry

MySQL InnoDB:
    MVCC snapshots
    +
    record/gap/next-key locking
    +
    stronger locking at Serializable

SQL Server:
    row locking at Repeatable Read
    +
    key-range locking at Serializable

SQL Server SNAPSHOT:
    separate row-versioned isolation mode
```

The practical lesson is:

> A transaction seeing an internally consistent snapshot does not imply that several transactions can safely make concurrent decisions from those snapshots.

That is the gap Serializable isolation is intended to close.

# References

PostgreSQL's current transaction-isolation documentation describes its stronger-than-standard Repeatable Read behavior, Snapshot Isolation implementation, Serializable Snapshot Isolation, predicate locks, serialization failures, and SQLSTATE `40001`.

The MySQL InnoDB documentation describes Repeatable Read as the default, transaction-level consistent reads, the distinction between ordinary and locking reads, gap/next-key locking, and the stronger locking behavior of Serializable transactions.

Microsoft's SQL Server documentation describes Repeatable Read as retaining locks on already-read data without protecting key ranges, while Serializable adds key-range locking; it also documents SNAPSHOT as a separate isolation model.
