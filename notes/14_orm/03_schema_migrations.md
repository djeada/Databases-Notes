# Schema Migrations

An ORM maps application code to a database schema, but the schema changes over time. **Schema migrations** are versioned changes that move the database from one known structure to another.

Typical changes include:

- adding or removing a column,
- creating an index,
- introducing a new table,
- renaming a field,
- splitting one table into two,
- backfilling derived data,
- tightening a constraint.

A production migration is not only "make the model class compile." It must preserve live data and remain compatible with application deployments.

## Migration mental model

Suppose version 1 has:

```text
users
┌────┬───────────────┐
│ id │ name          │
└────┴───────────────┘
```

Version 2 needs an email field:

```text
users
┌────┬───────────────┬─────────────────────┐
│ id │ name          │ email               │
└────┴───────────────┴─────────────────────┘
```

The migration history might be:

```text
001_create_users
        │
        ▼
002_add_email
        │
        ▼
003_unique_email
```

Each database instance records which revisions have already been applied.

## Why migrations are necessary

This is useful in a demo:

```python
Base.metadata.create_all(engine)
```

It creates missing objects, but it does not describe a safe history of how an existing production database should change.

For example, `create_all()` does not tell you how to:

- rename a populated column,
- backfill data before making it non-null,
- migrate one representation into another,
- build an index safely on a large table,
- coordinate two application versions during deployment.

Migrations make those changes explicit and reviewable.

## Common tools

| Ecosystem | Typical migration tool |
| --- | --- |
| SQLAlchemy | Alembic |
| Django | built-in migrations |
| Entity Framework Core | EF Core migrations |
| Rails | Active Record migrations |
| Prisma | Prisma Migrate |
| Java projects | Flyway or Liquibase are common |

The exact tooling differs, but the operational problems are similar.

## Alembic setup example

For a SQLAlchemy project:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install sqlalchemy alembic
```

Initialize migration files:

```bash
alembic init migrations
```

Typical layout:

```text
project/
├── alembic.ini
├── app/
│   └── models.py
└── migrations/
    ├── env.py
    └── versions/
```

Configure the database URL in `alembic.ini` or application configuration, then expose your SQLAlchemy metadata in `migrations/env.py`.

Conceptually:

```python
from app.models import Base

target_metadata = Base.metadata
```

## Autogenerate

After changing a mapped model:

```python
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str | None] = mapped_column(String(255))
```

Generate a candidate migration:

```bash
alembic revision --autogenerate -m "add user email"
```

Then inspect the generated file.

A typical migration contains:

```python
def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("email", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "email")
```

Alembic's documentation describes autogeneration as producing **candidate** migrations by comparing database state with application metadata. Those candidates should be reviewed and adjusted by hand.

## Applying migrations

Apply everything up to the newest revision:

```bash
alembic upgrade head
```

Show current revision:

```bash
alembic current
```

Show history:

```bash
alembic history
```

Move one revision backward:

```bash
alembic downgrade -1
```

A downgrade path can be useful in development, but production rollback is not always safe. If a migration destroys data, recreating the old schema does not restore the deleted values.

## Expand and contract

The safest production migrations often avoid changing application expectations in one step.

Suppose `users.name` should become `display_name`.

A risky deployment is:

```text
migration renames column
        │
        ▼
old application still expects "name"
        │
        ▼
requests fail
```

An **expand-and-contract** deployment separates the change.

### Step 1: expand

Add the new field while keeping the old one.

```text
users
├── name
└── display_name
```

Deploy application code that can work with both.

### Step 2: backfill

Copy old data:

```sql
UPDATE users
SET display_name = name
WHERE display_name IS NULL;
```

### Step 3: switch

Deploy code that reads and writes only `display_name`.

### Step 4: contract

After old application versions are gone, remove `name`.

```text
schema v1        expanded          new app stable      contracted
name      ───►   name            display_name  ───►   display_name
                 display_name
```

This pattern is especially useful in rolling deployments where multiple application versions coexist.

## Adding a non-null column

This innocent-looking migration can be dangerous on a populated table:

```sql
ALTER TABLE users
ADD COLUMN country VARCHAR(2) NOT NULL;
```

Existing rows have no value.

A safer sequence is often:

```text
1. add nullable column
2. deploy writers that populate it
3. backfill historical rows
4. verify no nulls remain
5. add NOT NULL constraint
```

SQL:

```sql
ALTER TABLE users
ADD COLUMN country VARCHAR(2);

UPDATE users
SET country = 'US'
WHERE country IS NULL;

ALTER TABLE users
ALTER COLUMN country SET NOT NULL;
```

The exact syntax and locking behavior depend on the database engine.

## Backfills

A **schema migration** changes structure. A **data migration** changes stored values.

Examples:

- populate a new derived field,
- normalize old enum values,
- copy data into a new table,
- calculate hashes,
- convert legacy units.

Large backfills should not automatically happen in one giant transaction.

Problem:

```text
UPDATE 500 million rows
        │
        ├── long locks
        ├── huge transaction log
        ├── replication lag
        └── difficult rollback
```

Better:

```text
batch 1 -> commit
batch 2 -> commit
batch 3 -> commit
...
```

Use checkpoints so the backfill can resume.

## Index creation

Adding an index can be expensive.

```sql
CREATE INDEX idx_orders_created_at
ON orders(created_at);
```

On a large production table, database-specific online or concurrent index creation features may be preferable.

For example, PostgreSQL supports:

```sql
CREATE INDEX CONCURRENTLY ...
```

That has its own restrictions and transaction behavior, so migration tools sometimes require special handling.

Always understand the target database rather than assuming all DDL behaves the same way.

## Migrations and transactions

Different databases treat DDL differently.

PostgreSQL supports transactional behavior for many DDL operations.

MySQL has operations that can implicitly commit or use online DDL mechanisms depending on operation and version.

SQLite may need a move-and-copy strategy for some table alterations. Alembic includes a batch migration mode designed for this class of operation.

The migration framework cannot erase engine-specific behavior.

## Generated migrations need review

Autogeneration can detect many structural differences, but it cannot reliably understand intent.

Suppose the model changes:

```text
old: first_name
new: given_name
```

A tool may interpret this as:

```text
DROP first_name
ADD given_name
```

But the intended operation is:

```text
RENAME first_name TO given_name
```

Those operations have very different data-loss consequences.

Review every generated migration.

## Migration dependencies

A migration must match the application version that expects it.

A safe deployment plan might be:

```text
migration A: add optional column
        │
        ▼
deploy app version 2
        │
        ▼
backfill data
        │
        ▼
migration B: enforce constraint
```

Do not assume deployment is atomic across every server.

## Forward compatibility

During a rolling deploy:

```text
server 1 -> app v1
server 2 -> app v1
server 3 -> app v2
server 4 -> app v2
```

The database schema must temporarily support both versions.

This is why destructive migrations usually happen after new code has fully replaced old code.

## Migration locks

DDL can block other database work.

Possible effects:

- table locks,
- blocked writes,
- lock queues,
- transaction timeouts,
- replication delay.

Before running a migration on a large table, investigate:

1. lock level,
2. expected duration,
3. table size,
4. write rate,
5. replica behavior,
6. rollback/recovery plan.

## Reversible does not mean safe

A migration can define a `downgrade()` but still lose information.

Example:

```text
upgrade:
DROP COLUMN legacy_code

downgrade:
ADD COLUMN legacy_code
```

The column structure comes back, but its values do not.

For destructive changes, recovery may require backups or a forward repair migration.

## Database migrations in CI/CD

A common workflow is:

```text
pull request
    │
    ▼
migration generated
    │
    ▼
review SQL / operations
    │
    ▼
run against temporary database
    │
    ▼
application tests
    │
    ▼
deploy
```

Useful automated checks include:

- migration chain has one expected head,
- empty database can migrate from zero,
- production-like schema can upgrade,
- migration does not accidentally drop important objects,
- application starts after migration.

## Offline SQL review

Some tools can render migration SQL without applying it.

Alembic supports SQL-generation workflows for migrations where teams want to inspect statements before execution.

This is useful in organizations where:

- DBAs review DDL,
- production access is restricted,
- migration SQL is executed through a separate deployment system.

## Production migration checklist

Before applying a migration:

1. What exact SQL or database operations will run?
2. Does it lock a hot table?
3. How much data will be touched?
4. Can old application versions keep running?
5. Does a backfill need batching?
6. What happens on replicas?
7. Is the migration idempotent or restartable?
8. What happens if it fails halfway?
9. Is rollback actually possible?
10. Is a backup or restore point needed?

## Common mistakes

### Editing old migration files after deployment

Applied migration history should be treated as immutable. Add a new migration instead.

### Combining huge backfills with schema DDL

Separate operationally risky steps.

### Dropping columns immediately

Wait until old application versions no longer need them.

### Trusting autogenerate blindly

A tool sees structural differences, not business intent.

### Running migrations automatically on every application instance

Multiple replicas may race to modify the schema. Production systems usually centralize migration execution.

### Ignoring database-specific DDL

ORM portability does not imply migration portability.

## Related notes

- [Introduction to ORM](01_introduction_to_orm.md)
- [ORM tools and their trade-offs](02_popular_orm_tools.md)
- [Relationship loading and query performance](04_relationship_loading_and_query_performance.md)
- [Transactions, concurrency, and unit of work](05_transactions_concurrency_and_unit_of_work.md)
- [Transactions and ACID](../04_acid_properties_and_transactions/)
