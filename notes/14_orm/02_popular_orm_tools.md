# ORM Tools and Their Trade-offs

ORMs differ in how they map objects, track changes, load relationships, and expose SQL. Start with the application's language and database requirements, then inspect how a tool handles your actual queries.

## Common options

| Tool | Ecosystem | Main approach |
| --- | --- | --- |
| SQLAlchemy ORM | Python | Explicit mappings and sessions; integrates with SQLAlchemy Core expressions. |
| Django ORM | Python / Django | Models, query sets, and migrations integrated into the web framework. |
| Hibernate ORM | Java | Entity mappings, persistence contexts, and relationship loading; implements Jakarta Persistence. |
| Entity Framework Core | .NET | Entity mappings, LINQ queries, change tracking, and migrations. |
| Active Record | Ruby / Rails | Model objects combine persisted data with data-access behavior. |

These are examples of different approaches rather than a performance ranking. Database support and feature coverage depend on the tool version and provider.

## Questions to answer before choosing

1. Does the provider support the database features you need, including types, constraints, and concurrency behavior?
2. Can you inspect generated SQL and execution plans?
3. How are transactions, retries, and connection pooling handled?
4. Can you control relationship loading and avoid N+1 queries?
5. How are schema migrations reviewed, deployed, and recovered from?
6. Can you use parameterized raw SQL for operations the ORM does not express well?

Test a representative workflow containing a relationship query, pagination, a batch write, and a concurrent update. Measure database round trips and transferred rows as well as application execution time.

## Shared pitfalls

A model-level validation can race with another writer; enforce the corresponding database constraint too. Bulk operations may bypass normal object tracking or hooks. Lazy relationships may fail after their session closes. Migration generation produces a proposal that needs review, especially for renames, backfills, and destructive changes.

## Official documentation

- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/orm/)
- [Django database models](https://docs.djangoproject.com/en/stable/topics/db/models/)
- [Hibernate ORM](https://hibernate.org/orm/documentation/)
- [Entity Framework Core](https://learn.microsoft.com/en-us/ef/core/)
- [Rails Active Record](https://guides.rubyonrails.org/active_record_basics.html)
