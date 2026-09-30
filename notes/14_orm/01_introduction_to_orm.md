# Introduction to Object-Relational Mapping

An object-relational mapper (ORM) is a library that maps application objects to relational tables and generates SQL for common database operations.

Instead of manually writing every `INSERT`, `UPDATE`, and `SELECT`, application code works with mapped classes and query APIs. The ORM translates those operations into SQL and maps returned rows back into objects.

ORMs reduce repetitive data-access code, but they do **not** remove the database. Constraints, transactions, indexes, isolation levels, query plans, and network round trips still determine correctness and performance.

## The mapping

| Application concept | Relational concept |
| --- | --- |
| Mapped class | Table |
| Object instance | Row |
| Attribute | Column |
| Relationship | Foreign key + query |
| Session / unit of work | Tracks objects and coordinates SQL |
| Query API | Generates SQL |
| Migration | Changes database schema over time |

A simplified mapping looks like:

```text
Python object                         SQL table

User(id=1, name="Alice")             users
        │                            ┌────┬────────┐
        ├── id ─────────────────────►│ id │ name   │
        └── name ───────────────────►├────┼────────┤
                                     │  1 │ Alice  │
                                     └────┴────────┘
```

## What an ORM actually does

Consider:

```python
user = User(name="Alice")
session.add(user)
session.commit()
```

Conceptually, the ORM performs work similar to:

```sql
INSERT INTO users (name)
VALUES (?);
```

Later:

```python
user = session.get(User, 1)
```

may become:

```sql
SELECT id, name
FROM users
WHERE id = ?;
```

The exact SQL depends on the ORM, database, mappings, and query.

## Typical request lifecycle

A common web-request flow is:

```text
HTTP request
    │
    ▼
application service
    │
    ▼
ORM session / unit of work
    │
    ├── SELECT / INSERT / UPDATE / DELETE
    ▼
database transaction
    │
    ├── COMMIT on success
    └── ROLLBACK on failure
```

A session is not necessarily one permanent database connection. Connection pools, transaction boundaries, and session behavior depend on the library.

## Runnable SQLAlchemy example

The repository includes a complete example:
[`scripts/orm/sqlalchemy_demo.py`](../../scripts/orm/sqlalchemy_demo.py).

It uses SQLAlchemy 2.x with SQLite so no database server is required.

### 1. Create an environment

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install sqlalchemy
```

### 2. Run the demo

```bash
python scripts/orm/sqlalchemy_demo.py
```

The demo:

1. creates `users` and `posts` tables,
2. inserts users and related posts in one transaction,
3. runs a relationship query,
4. uses eager loading to avoid an N+1 query,
5. updates a row,
6. prints the generated SQL.

Because the engine is created with SQL logging enabled, you can see statements such as:

```sql
INSERT INTO users (name) VALUES (?)
SELECT users.id, users.name FROM users ORDER BY users.id
UPDATE users SET name=? WHERE users.id = ?
```

This is useful because ORM code should never be treated as mysterious. Inspecting the generated SQL is part of using an ORM well.

## SQLAlchemy 2.x minimal example

```python
from sqlalchemy import String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))


engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)

with Session(engine) as session:
    with session.begin():
        session.add(User(name="Alice"))

    users = session.scalars(
        select(User).order_by(User.id)
    ).all()

    for user in users:
        print(user.id, user.name)
```

Expected output:

```text
1 Alice
```

## Session and unit of work

Many ORMs use a **unit of work** pattern.

The session tracks objects that were:

- loaded,
- added,
- modified,
- deleted.

It decides which SQL statements need to run before the transaction finishes.

```text
application objects
      │
      ▼
┌─────────────────┐
│ ORM session     │
│ new: User(...)  │
│ dirty: Order    │
│ deleted: Item   │
└────────┬────────┘
         │ flush
         ▼
INSERT / UPDATE / DELETE
         │
         ▼
database transaction
```

A session should usually have a clear lifetime. In web applications it is often scoped to one request or one application-level unit of work.

Long-lived sessions can accumulate stale objects and make transaction boundaries unclear.

## Flush versus commit

These terms are frequently confused.

### Flush

A **flush** sends pending SQL to the database while keeping the transaction open.

```python
session.add(User(name="Alice"))
session.flush()
```

At this point the `INSERT` may already have executed, but the transaction can still roll back.

### Commit

A **commit** makes the transaction durable according to the database's transaction guarantees.

```python
session.commit()
```

A useful mental model is:

```text
modify objects
     │
     ▼
flush ──► SQL reaches database
     │
     ▼
commit ─► transaction finishes successfully
```

## Transactions

Related writes should generally occur in one transaction.

Example: create an order and decrement inventory.

```python
with Session(engine) as session:
    with session.begin():
        session.add(order)
        inventory.quantity -= order.quantity
```

If an exception escapes the block, the transaction rolls back.

Without one transaction:

```text
1. insert order       ✓
2. application crash  ✗
3. update inventory   never happens
```

The database is left inconsistent.

With one transaction:

```text
BEGIN
  insert order
  update inventory
COMMIT
```

Either both changes commit or neither does.

## Relationships

Relational data is connected with foreign keys.

Example:

```text
users                       posts
┌────┬────────┐             ┌────┬─────────┬────────────┐
│ id │ name   │             │ id │ user_id │ title      │
├────┼────────┤             ├────┼─────────┼────────────┤
│  1 │ Alice  │◄────────────│ 10 │    1    │ ORM notes  │
└────┴────────┘             └────┴─────────┴────────────┘
```

The ORM may expose:

```python
user.posts
post.author
```

but those properties can trigger additional SQL.

That is convenient, but it can become expensive.

## The N+1 query problem

Suppose one query loads 100 orders:

```sql
SELECT * FROM orders;
```

Then application code accesses each order's customer:

```python
for order in orders:
    print(order.customer.name)
```

If the relationship is lazy-loaded, the ORM may run:

```text
1 query for orders
100 queries for customers
-------------------------
101 total queries
```

This is the **N+1 problem**.

Visualized:

```text
load orders ─────────────► 1 query
   │
   ├─ order 1 customer ─► 1 query
   ├─ order 2 customer ─► 1 query
   ├─ order 3 customer ─► 1 query
   └─ ...
```

The solution is not "always join everything". Instead choose a loading strategy that matches the query.

For SQLAlchemy, `selectinload()` often loads related collections with a second query:

```text
1 query for users
1 query for all matching posts
------------------------------
2 total queries
```

Joined eager loading is another option, but a large join can duplicate parent rows and transfer too much data.

Measure the actual SQL.

## Object identity and stale data

Many ORMs keep one in-memory object per database identity within a session.

If the same row is requested repeatedly, the session may return the same Python object.

This is useful, but it means an object can become stale if another transaction changes the row.

The database remains the source of truth. Refreshing objects, ending the transaction, or starting a new unit of work may be necessary depending on isolation and application requirements.

## Database constraints still matter

Application validation is useful for user feedback, but correctness rules should also live in the database when possible.

For example, this application check is not sufficient:

```python
if not email_exists(email):
    create_user(email)
```

Two requests can race:

```text
Request A: email absent
Request B: email absent
Request A: insert
Request B: insert
```

A database `UNIQUE` constraint closes the race.

Use database constraints for:
- primary keys,
- foreign keys,
- uniqueness,
- required fields,
- check constraints where appropriate.

The ORM should map those rules, not replace them.

## Schema creation versus migrations

This is convenient for demos:

```python
Base.metadata.create_all(engine)
```

It creates missing tables, but it is not a complete production schema-migration strategy.

Production systems need versioned migrations for changes such as:

- renaming columns,
- adding non-null columns,
- backfilling data,
- changing indexes,
- splitting tables,
- removing old fields.

Common migration tools include:

| Ecosystem | Migration tool |
| --- | --- |
| SQLAlchemy | Alembic |
| Django | built-in Django migrations |
| Entity Framework Core | EF Core migrations |
| Rails | Active Record migrations |
| Prisma | Prisma Migrate |
| Java/JPA projects | often Flyway or Liquibase |

Generated migrations should be reviewed before deployment.

## Connection pooling

Opening a new database connection for every query is expensive. Applications typically use a connection pool.

```text
Application workers
   │   │   │
   ▼   ▼   ▼
┌─────────────────┐
│ connection pool │
│ conn 1          │
│ conn 2          │
│ conn 3          │
└───────┬─────────┘
        ▼
     database
```

The ORM or underlying database library often manages the pool.

Important settings include:
- maximum pool size,
- connection timeout,
- idle connection lifetime,
- stale connection detection.

More connections are not always better. The database has finite CPU, memory, locks, and worker capacity.

## Concurrency and lost updates

An ORM does not automatically solve concurrent writes.

Two transactions can both load the same balance:

```text
T1 reads 100
T2 reads 100
T1 writes 90
T2 writes 80
```

The final value may overwrite one update.

Solutions depend on the business rule:
- stronger transaction isolation,
- row locks,
- atomic SQL updates,
- optimistic version columns,
- serialization at the application level.

For example, an atomic update:

```sql
UPDATE accounts
SET balance = balance - 10
WHERE id = 1;
```

can be safer than reading a value into application memory and writing a computed replacement.

## Raw SQL is not a failure

ORMs are useful abstractions, but not every query should be expressed through an ORM.

Raw SQL may be clearer for:
- complex analytical queries,
- recursive CTEs,
- engine-specific features,
- carefully optimized reports,
- bulk data manipulation.

Use parameter binding:

```python
session.execute(
    text("SELECT * FROM users WHERE email = :email"),
    {"email": email},
)
```

Do not concatenate untrusted values into SQL strings.

## Performance principles

The expensive part of ORM code is often not object creation. It is the generated database workload.

Measure:
- number of SQL statements,
- rows transferred,
- query latency,
- lock time,
- transaction duration,
- connection-pool waits.

A slow-looking loop in Python may actually be an N+1 query problem. A compact ORM expression may generate a huge join.

Always inspect both the application code and the SQL.

## When an ORM is a good fit

ORMs are particularly useful when:
- the application is CRUD-heavy,
- domain objects map reasonably well to relational tables,
- the team wants migrations and relationship handling,
- portability and consistent data-access patterns matter.

An ORM may be less attractive when:
- most work is analytical SQL,
- queries are highly database-specific,
- the application is mostly bulk data processing,
- the schema is intentionally hidden behind stored procedures or a strict database API.

Many systems mix ORM queries with SQL for specialized cases.

## Practical checklist

Before merging ORM code, ask:

1. What SQL will this generate?
2. How many database round trips occur?
3. Is the transaction boundary explicit?
4. Are important rules enforced by database constraints?
5. Could relationship loading cause N+1 queries?
6. Is pagination deterministic?
7. Is a migration required?
8. Could two concurrent requests overwrite each other?
9. Is raw SQL parameterized?
10. Can the query be inspected in the database execution plan?

## Related notes

- [ORM tools and their trade-offs](02_popular_orm_tools.md)
- [Accessing a database in code](../08_database_performance/05_accessing_database_in_code.md)
- [Transactions and ACID](../04_acid_properties_and_transactions/)
- [SQL injection](../11_security_best_practices/06_sql_injection.md)
