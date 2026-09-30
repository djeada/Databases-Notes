# Transactions, Concurrency, and the Unit of Work

ORMs make database access convenient, but concurrent requests still operate on a shared database. Two application workers can read the same row, make different decisions, and attempt conflicting writes.

Correctness therefore depends on understanding:

- transaction boundaries,
- flush and commit behavior,
- database isolation,
- locking,
- optimistic concurrency,
- retries,
- the ORM's unit-of-work model.

## Unit of work

A **unit of work** groups related application changes that should succeed or fail together.

Example: create an order and reduce inventory.

```text
request
  │
  ▼
begin unit of work
  │
  ├── INSERT order
  ├── INSERT order_items
  └── UPDATE inventory
  │
  ▼
commit
```

If any step fails:

```text
begin
  INSERT order        ✓
  INSERT order_items  ✓
  UPDATE inventory    ✗
rollback
```

The database returns to the previous committed state.

## ORM session versus transaction

An ORM session is usually an application-side object that tracks entities and coordinates SQL.

A database transaction is a database-side atomic unit.

They are related but not identical.

```text
ORM session
   │
   ├── identity map
   ├── new objects
   ├── modified objects
   ├── deleted objects
   │
   └── uses one or more DB transactions over its lifetime
```

Do not assume "session exists" means one transaction has been open continuously.

The exact behavior depends on the ORM.

## Request-scoped pattern

A common service pattern is:

```text
HTTP request
     │
     ▼
create ORM session
     │
     ▼
begin transaction
     │
     ▼
read + modify
     │
     ▼
commit / rollback
     │
     ▼
close session
     │
     ▼
HTTP response
```

This gives each request a clear unit-of-work boundary.

Avoid keeping a transaction open while performing unrelated slow work such as calling an external API.

## Flush versus commit

A **flush** sends pending SQL to the database but leaves the transaction open.

```python
session.add(User(name="Alice"))
session.flush()
```

The row may now have a generated primary key, but another transaction may still not see it and the current transaction can still roll back.

```text
application change
      │
      ▼
flush
      │
      ├── SQL executed
      │
      └── transaction still open
      ▼
commit
      │
      └── transaction completed
```

A commit normally includes any required flush first.

## Autoflush

Many ORMs flush automatically before some queries.

Example:

```python
user = User(name="Alice")
session.add(user)

# A query may trigger an autoflush before SELECT.
count = session.scalar(select(func.count(User.id)))
```

This can surprise developers who think no SQL is sent until `commit()`.

Understand your ORM's autoflush rules, especially when:
- validation queries run after changes,
- database constraints can fail,
- generated IDs are needed.

## Lost update

The classic concurrency problem:

```text
database balance = 100

Transaction A reads 100
Transaction B reads 100

A subtracts 10 -> writes 90
B subtracts 20 -> writes 80

final balance = 80
```

The correct result for both changes should have been 70.

The second write overwrote the first because both transactions computed from stale state.

## Atomic SQL updates

One solution is to keep the calculation inside the database:

```sql
UPDATE accounts
SET balance = balance - 10
WHERE id = 1;
```

Then another transaction can independently run:

```sql
UPDATE accounts
SET balance = balance - 20
WHERE id = 1;
```

The database serializes the row updates according to its locking/MVCC rules, so each statement operates on committed/current row state rather than an old application copy.

Set-based atomic statements are often safer than read-modify-write cycles.

## Optimistic concurrency

Optimistic concurrency assumes conflicts are uncommon.

Each row contains a version:

```text
documents
┌────┬──────────────┬─────────┐
│ id │ title        │ version │
├────┼──────────────┼─────────┤
│  1 │ Draft        │    7    │
└────┴──────────────┴─────────┘
```

An update includes the expected old version:

```sql
UPDATE documents
SET title = 'New title',
    version = 8
WHERE id = 1
  AND version = 7;
```

If another transaction already changed the row to version 8, this statement updates zero rows.

```text
A loads version 7
B loads version 7

A commits -> version 8

B tries:
WHERE version = 7
       │
       ▼
0 rows updated
       │
       ▼
conflict detected
```

The application can then:
- retry,
- show a conflict message,
- merge changes,
- ask the user to reload.

## Runnable optimistic-locking example

The repository includes:

[`scripts/orm/optimistic_concurrency_demo.py`](../../scripts/orm/optimistic_concurrency_demo.py)

Run:

```bash
python -m pip install -r scripts/orm/requirements.txt
python scripts/orm/optimistic_concurrency_demo.py
```

The script opens two SQLAlchemy sessions that both load the same document version.

Session A commits first.

Session B then attempts to commit its stale object and SQLAlchemy raises `StaleDataError` because its versioned `UPDATE` matches zero rows.

Expected shape:

```text
Both sessions loaded version 1
Session A committed version 2
Session B was rejected because its version was stale.
Final row: title='Edited by session A', version=2
```

SQL logging is enabled so the version check is visible.

## Pessimistic locking

Pessimistic locking assumes conflicts are likely enough that access should be serialized.

A common SQL pattern is:

```sql
SELECT id, balance
FROM accounts
WHERE id = 1
FOR UPDATE;
```

The transaction locks the selected row for conflicting writes until commit or rollback.

```text
Transaction A
SELECT ... FOR UPDATE
        │
        ├── owns row lock
        │
Transaction B
SELECT ... FOR UPDATE
        │
        └── waits
```

After A commits, B can continue.

Use this when:
- a short critical section must be serialized,
- retrying optimistic conflicts would be expensive,
- business logic needs a stable locked row.

Risks:
- lock waits,
- reduced concurrency,
- deadlocks,
- long transactions causing queues.

## ORM locking example

SQLAlchemy:

```python
account = session.scalar(
    select(Account)
    .where(Account.id == account_id)
    .with_for_update()
)
```

The target database must support the requested locking semantics.

SQLite, PostgreSQL, MySQL, and SQL Server have different locking models, so do not assume identical behavior.

## Deadlocks

A deadlock can occur when two transactions acquire resources in different orders.

```text
Transaction A          Transaction B

lock account 1         lock account 2
      │                      │
      ▼                      ▼
want account 2         want account 1
      │                      │
      └────── wait cycle ────┘
```

The database detects the cycle and aborts one transaction.

Applications should be prepared to retry transactions that fail with deadlock/serialization errors.

A useful prevention rule is to acquire resources in a consistent order.

Example:

```text
always lock lower account ID first
```

## Retry the transaction, not one statement

If a transaction is aborted because of a serialization conflict or deadlock, retry the whole business unit of work.

Bad:

```text
BEGIN
read A
read B
UPDATE A  -> deadlock
retry only UPDATE A
```

Earlier reads may no longer be valid.

Better:

```text
attempt 1:
  BEGIN
  read A
  read B
  update
  COMMIT
  -> conflict

attempt 2:
  BEGIN
  repeat entire decision
  COMMIT
```

Retries should be bounded and usually use backoff.

## Isolation levels

Isolation determines which concurrent effects transactions can observe.

Common names include:

- READ UNCOMMITTED,
- READ COMMITTED,
- REPEATABLE READ,
- SERIALIZABLE.

The exact guarantees differ by database engine.

Do not infer behavior only from the isolation-level name.

For example, PostgreSQL and MySQL both expose REPEATABLE READ but implement concurrency differently.

See the repository's transaction/isolation notes for engine-level detail.

## Read committed

At READ COMMITTED, separate statements in one transaction may see newer committed data.

Conceptually:

```text
T1: SELECT status -> 'pending'

T2: UPDATE status='paid'
T2: COMMIT

T1: SELECT status -> may now see 'paid'
```

This is often a reasonable default for request-driven applications, but multi-step decisions can still need locks or version checks.

## Repeatable read / snapshot behavior

A transaction may keep seeing one snapshot:

```text
T1 begins
T1 reads value 10

T2 changes value to 20
T2 commits

T1 reads again
T1 still sees 10
```

This provides a stable view but does not automatically prevent every application-level anomaly.

## Serializable

Serializable aims to make concurrent transactions behave as though they ran one at a time.

A database may achieve this through locking, validation, or serializable snapshot techniques.

Applications may receive serialization failures and need to retry.

Stronger isolation can simplify reasoning but may reduce throughput or increase retries under contention.

## Check-then-act races

Application validation can race.

```python
if not user_exists(email):
    create_user(email)
```

Two workers:

```text
A: email absent
B: email absent
A: INSERT
B: INSERT
```

The correct defense is a database uniqueness constraint:

```sql
ALTER TABLE users
ADD CONSTRAINT uq_users_email UNIQUE (email);
```

The application can catch the constraint violation and return an appropriate result.

Use application checks for friendly feedback, database constraints for correctness.

## Get-or-create

"Get or create" is a common race-prone operation.

Unsafe:

```text
SELECT key
if missing:
    INSERT key
```

Better approaches:
- database-native upsert,
- unique constraint plus retry,
- ORM helper that is documented to handle the race appropriately.

PostgreSQL example:

```sql
INSERT INTO tags(name)
VALUES ('database')
ON CONFLICT (name)
DO NOTHING;
```

Then fetch the existing/current row.

## Upserts

Upserts combine insert/update decisions atomically in the database.

PostgreSQL:

```sql
INSERT INTO counters(key, value)
VALUES ('orders', 1)
ON CONFLICT (key)
DO UPDATE
SET value = counters.value + 1;
```

MySQL and SQLite have their own upsert syntax.

Use the ORM's database-specific support or parameterized SQL when this expresses the operation more safely than a read-modify-write cycle.

## Long transactions

Long transactions are harmful because they can:

- retain locks,
- keep old MVCC versions alive,
- increase deadlock opportunities,
- block schema changes,
- consume connections,
- cause replica/storage cleanup pressure.

Bad pattern:

```text
BEGIN
read rows
call external payment API for 8 seconds
update rows
COMMIT
```

Prefer:

```text
short DB transaction
      │
      ▼
external call
      │
      ▼
new short transaction
```

When the external action and database state must coordinate, use patterns such as:
- outbox,
- explicit state machine,
- idempotency keys,
- compensating actions.

Do not keep a database lock open across a slow remote network call unless the trade-off is deliberate.

## Connection pools and transactions

A checked-out connection is a finite resource.

```text
request A ──► connection 1
request B ──► connection 2
request C ──► connection 3
request D ──► waits
```

Long transactions keep connections occupied longer.

Symptoms of pool pressure:
- request latency grows,
- timeouts waiting for a connection,
- database appears underutilized because the application is queueing before it.

Track both pool wait time and database query time.

## Session state after an error

After a database error, an ORM session/transaction may require rollback before it can be reused.

Typical pattern:

```python
try:
    session.commit()
except Exception:
    session.rollback()
    raise
```

Framework helpers may automate this, but the concept remains important.

Do not continue issuing arbitrary operations on a failed transaction.

## Nested work and savepoints

A savepoint allows partial rollback inside one transaction.

```sql
BEGIN;

INSERT INTO orders ...;

SAVEPOINT before_optional_step;

-- optional operation fails
ROLLBACK TO SAVEPOINT before_optional_step;

-- main order transaction continues

COMMIT;
```

ORMs often expose nested transaction/savepoint APIs.

Use savepoints carefully: they do not create an independent durable transaction.

## Idempotency keys

For APIs that may be retried, a stable request ID can prevent duplicate effects.

Example payment request:

```text
Idempotency-Key: payment-8f193
```

Store it under a unique constraint:

```text
payments
├── id
├── idempotency_key UNIQUE
├── amount
└── status
```

If the client retries the same request, the service can return the already-created result rather than charge twice.

## Transaction boundaries and events

A common problem:

```text
BEGIN
INSERT order
COMMIT

publish event to Kafka
   │
   └── application crashes before publish
```

The database contains the order but no event exists.

The transactional outbox pattern writes an event row in the same database transaction:

```text
BEGIN
INSERT order
INSERT outbox_event
COMMIT
```

A separate publisher/CDC process delivers the outbox event later.

This connects ORM transaction design with streaming architecture.

## Choosing a concurrency strategy

```text
Can operation be one atomic SQL statement?
        │
        ├── yes -> prefer atomic SQL
        │
        └── no
             │
             ▼
Are conflicts uncommon?
        │
        ├── yes -> optimistic version check
        │
        └── no
             │
             ▼
Must one worker hold exclusive access briefly?
        │
        ├── yes -> pessimistic row lock
        │
        └── no -> reconsider transaction/data model
```

Isolation level and constraints still apply around all three choices.

## Practical checklist

For each write path, ask:

1. What begins and ends the transaction?
2. Which ORM actions trigger a flush?
3. What happens if two requests update the same row?
4. Can the operation be expressed atomically in SQL?
5. Is a version column appropriate?
6. Is a row lock required?
7. Which errors should retry the whole transaction?
8. Are uniqueness/check/foreign-key rules enforced in the database?
9. Does the transaction perform network calls?
10. How long can it hold a connection or lock?

## Common mistakes

### One session for the entire application

This creates stale state and unclear transaction boundaries.

### Calling commit after every individual row

This destroys atomicity and adds overhead.

### Assuming ORM objects remain current forever

Other transactions can change the database.

### Catching a conflict but not rolling back

The transaction may remain unusable.

### Retrying only the failed SQL statement

Retry the whole business decision when isolation/deadlock semantics require it.

### Using locks without consistent ordering

Deadlocks become more likely.

### Treating optimistic locking as database locking

It detects stale writes; it does not block another transaction from editing.

## Related notes

- [Introduction to ORM](01_introduction_to_orm.md)
- [Schema migrations](03_schema_migrations.md)
- [Relationship loading and query performance](04_relationship_loading_and_query_performance.md)
- [ACID properties and transactions](../04_acid_properties_and_transactions/)
- [Concurrency control](../07_concurrency_control/)
