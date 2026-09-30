# DCL: Decide Who May Access the Data

**Data Control Language (DCL)** manages database privileges through statements such as `GRANT` and `REVOKE`. A **privilege** is permission to perform a particular operation on a particular resource.

The bookstore might need an application that creates orders and a reporting job that only reads them. They should not necessarily have the same permissions.

## Identity is different from permission

**Authentication** answers “who is connecting?” **Authorization** answers “what may this identity do?” Successfully logging in does not mean that every table or operation should be available.

A **role** is a named database identity or collection of privileges, depending on the engine. Assigning privileges to a role can avoid repeating the same grants for every reporting user.

The commands in this note use **PostgreSQL**, where roles can have login ability or serve as privilege groups. SQLite has no equivalent built-in `GRANT`/`REVOKE` user system; its access is managed by the application and operating-system file permissions.

## Grant a narrowly defined reading role

Assume a PostgreSQL database named `bookstore`, a schema named `public`, and a `public.orders` table. A **schema** here is a namespace grouping objects inside the database. Run administrative commands only through an account permitted to issue these grants.

```sql
CREATE ROLE report_reader;
GRANT CONNECT ON DATABASE bookstore TO report_reader;
GRANT USAGE ON SCHEMA public TO report_reader;
GRANT SELECT ON TABLE public.orders TO report_reader;
```

The separate privileges have separate purposes: connect to this database, refer to objects in this schema, and read this table. The example role is a group without login ability; an existing reporting login must be granted membership to use it.

```sql
-- Assume reporting_login is an existing login role.
GRANT report_reader TO reporting_login;
```

No insert, update, or delete privilege is granted by these statements. However, the login may obtain additional privileges through other roles, ownership, or privileges granted to `PUBLIC`. PostgreSQL `PUBLIC` means all roles; it is different from the `public` schema.

## Revoke a grant and understand the remaining paths

```sql
REVOKE SELECT ON TABLE public.orders FROM report_reader;
```

This removes that grant from that role. It is not an absolute ban: another applicable grant or ownership may still permit reading. To audit access, inspect all relevant roles and privilege sources.

Grants on existing tables also do not automatically establish the policy for every future table. Default privileges are a separate engine-specific mechanism controlled by the role creating those objects.

## Database privileges are not the whole application policy

The database connection may be shared by many bookstore customers through one application identity. Giving that identity access to orders does not mean every customer should see every order.

The application must check whose order is being requested, or use a suitable database row-level policy. A **row-level policy** governs which rows may be accessed, rather than only whether the table as a whole can be queried. Its design must account for how authenticated customer identity reaches the database.

## Use least privilege

**Least privilege** means granting only the access needed for a job. A reporting process usually does not need schema modification. A checkout application generally should not use the database administrator's identity.

Separate migration credentials from routine application credentials. A migration changes tables; normal checkout uses the already defined tables. Keeping those jobs separate reduces the authority available to an unintended query or compromised application.

## Check your understanding

1. How are authentication and authorization different?
2. Why does reading a PostgreSQL table involve more than a `SELECT` grant alone?
3. Why might revoking one role's grant leave a user's access intact?
4. Why does a shared application connection still need a customer-level access policy?

Continue with [transaction control](05_transaction_control_language_tcl.md) to decide which authorized changes must succeed together.
