# Introduction to Object-Relational Mapping

An object-relational mapper (ORM) maps application objects to relational tables and generates SQL for common operations. It reduces repetitive data-access code while leaving database constraints, transactions, and query costs in place.

## The mapping

| Application concept | Database concept |
| --- | --- |
| Mapped class | Table |
| Object instance | Row |
| Mapped attribute | Column |
| Object relationship | Association backed by keys and queries |
| Session or unit of work | Tracks changes and coordinates database operations |

A session is not necessarily one connection or one transaction for its whole lifetime. Its exact behavior depends on the ORM.

## Example with SQLAlchemy 2.x

Install SQLAlchemy in your Python environment. This example uses an in-memory SQLite database, so each run starts empty.

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

    names = session.scalars(select(User.name).order_by(User.id)).all()
    print(names)  # ['Alice']
```

The transaction context commits on successful exit and rolls back on an exception. A **flush** sends pending SQL to the database; it does not by itself commit the transaction. Schema creation here is a learning convenience; use reviewed migrations to evolve an existing database. See the [SQLAlchemy ORM quick start](https://docs.sqlalchemy.org/en/20/orm/quickstart.html).

## Relationships and the N+1 problem

Loading 100 orders and then lazily loading each order's customer can cause one order query plus up to 100 customer queries. This is the N+1 problem. Select an appropriate eager-loading strategy or query the needed fields directly, and inspect the generated SQL.

A large joined eager load can duplicate rows and transfer too much data. Eager loading is a choice to measure, not a universal improvement.

## Correctness still belongs in the design

Use database constraints for uniqueness and references. Keep related writes in one transaction. Choose isolation or explicit concurrency checks for competing updates. Parameter binding protects values, but raw SQL built from untrusted strings remains vulnerable, even inside an ORM.

Use raw SQL when it makes a complex or engine-specific operation clearer. The useful boundary is whether the query is correct, understandable, and measurable.

## Related notes

- [Popular ORM tools](02_popular_orm_tools.md)
- [Accessing a database in code](../08_database_performance/05_accessing_database_in_code.md)
- [SQL injection](../11_security_best_practices/06_sql_injection.md)
