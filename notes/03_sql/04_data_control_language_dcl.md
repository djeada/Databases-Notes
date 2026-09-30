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

## Try permissions on a complete PostgreSQL practice object

SQLite does not implement this role system. Run the following in a disposable **PostgreSQL** database as an administrator or a role allowed to create schemas and roles. The role names must not already exist:

```sql
-- PostgreSQL
CREATE SCHEMA dcl_practice;
CREATE TABLE dcl_practice.order_summary (
    order_id INTEGER PRIMARY KEY,
    total_cents BIGINT NOT NULL
);
INSERT INTO dcl_practice.order_summary VALUES (101, 5500), (103, 5000);
CREATE ROLE dcl_practice_reader NOLOGIN;
GRANT USAGE ON SCHEMA dcl_practice TO dcl_practice_reader;
GRANT SELECT ON dcl_practice.order_summary TO dcl_practice_reader;

SET ROLE dcl_practice_reader;
SELECT order_id, total_cents
FROM dcl_practice.order_summary
ORDER BY order_id;
RESET ROLE;
```

The reader sees two rows. `SET ROLE` changes the active role for the session; it does not create a network login or change the underlying session's login identity. The administrator can switch to this practice role for the test. An ordinary application login needs an authorized membership before it can use another role.

`USAGE` lets the role resolve objects in this schema. `SELECT` lets it read this table. Neither grant lets it insert orders. To observe a denied operation, switch roles again and run this statement **separately**, outside a transaction block:

```sql
-- PostgreSQL; expected permission error
SET ROLE dcl_practice_reader;
INSERT INTO dcl_practice.order_summary VALUES (104, 1500);
```

The insert should fail with a permission error. Run `RESET ROLE;` afterward. If a client automatically wraps the test in a transaction, roll back the failed transaction before resetting the role. A read-only job should fail visibly when it accidentally attempts a write, rather than obtaining broad privileges to conceal the mistake.

## Separate login identity from a job's privileges

A role can represent a collection of permissions without having login rights. A login can then receive that role. This supports changing a job's access in one place instead of granting every table separately to every person:

```sql
-- PostgreSQL; creates a role, not a configured connection
CREATE ROLE dcl_practice_job LOGIN;
GRANT dcl_practice_reader TO dcl_practice_job;
```

The role has no password configured here. PostgreSQL authentication is governed by server configuration; `LOGIN` alone does not guarantee a connection is possible. Provision credentials through the system's secret-handling process. In an interactive `psql` session, `\password dcl_practice_job` prompts for a password without putting a literal secret in a saved SQL file.

A service account should represent a service rather than a shared human identity. Human access, deployment access, reporting access, and normal application access have different needs. For example, a migration role may need to alter tables while a web application's role only needs selected reads and writes. If a query endpoint is compromised, the application's restricted database role reduces the actions available through that connection.

Role inheritance and the permission to switch roles have configurable behavior, including membership options in recent PostgreSQL versions. Verify the actual login using the intended connection path; an administrator successfully reading a table is not evidence that a reporting login has the right grants.

## Existing tables and future tables are different scopes

A grant on existing objects does not automatically cover tables created next week. PostgreSQL can set defaults for objects a specific owner creates:

```sql
-- PostgreSQL; run as the role that will create the tables
ALTER DEFAULT PRIVILEGES IN SCHEMA dcl_practice
GRANT SELECT ON TABLES TO dcl_practice_reader;

CREATE TABLE dcl_practice.daily_totals (
    report_date DATE PRIMARY KEY,
    total_cents BIGINT NOT NULL
);
INSERT INTO dcl_practice.daily_totals VALUES ('2025-01-12', 6500);

SET ROLE dcl_practice_reader;
SELECT report_date, total_cents FROM dcl_practice.daily_totals;
RESET ROLE;
```

The reader can select the newly created table. These defaults belong to the creating role and affect future objects. They do not retroactively change every existing table, and they do not automatically apply to tables created by a different owner. If a deployment pipeline creates tables under another role, configure that owner's defaults deliberately.

An insert using a generated sequence can require sequence permissions in addition to table permissions. Grant the specific capabilities a writer needs; adding `ALL` merely because one sequence call failed is a much wider change.

## Trace effective access before revoking it

Permissions can arrive through direct grants, role memberships, ownership, or `PUBLIC`. In PostgreSQL, `PUBLIC` represents all roles, including future roles. Revoking a grant from one role does not remove a permission it still inherits through another path.

```sql
-- PostgreSQL
SELECT has_table_privilege(
    'dcl_practice_reader', 'dcl_practice.order_summary', 'SELECT'
) AS may_read;

REVOKE SELECT ON dcl_practice.order_summary FROM dcl_practice_reader;

SELECT has_table_privilege(
    'dcl_practice_reader', 'dcl_practice.order_summary', 'SELECT'
) AS may_read;
```

In this isolated setup, the answers are true then false. On a live database, inspect other paths if the answer remains true. Object owners normally retain powers that an ordinary grantee lacks, and superusers are unsuitable for testing a restricted account.

`WITH GRANT OPTION` permits a grantee to grant a privilege onward. Use it only when delegation is intended. Revoking delegated privileges can involve dependencies and cascading revocation. Keep the ownership and grant chain understandable instead of treating every role as an independent list of permissions.

## Clean up the practice roles

Reset the role before cleanup. Remove the defaults and membership that would otherwise retain dependencies:

```sql
-- PostgreSQL; use the same creating administrator as above
RESET ROLE;
ALTER DEFAULT PRIVILEGES IN SCHEMA dcl_practice
REVOKE SELECT ON TABLES FROM dcl_practice_reader;
REVOKE dcl_practice_reader FROM dcl_practice_job;
DROP TABLE dcl_practice.daily_totals;
DROP TABLE dcl_practice.order_summary;
DROP SCHEMA dcl_practice;
DROP ROLE dcl_practice_job;
DROP ROLE dcl_practice_reader;
```

The explicit cleanup is preferable for this exercise to an indiscriminate `DROP OWNED` against a real account. That command can affect objects the role owns as well as its grants.

MySQL accounts include a user and host component, so `'reporter'@'localhost'` and `'reporter'@'%'` describe different connection scopes. SQL Server distinguishes server logins from database users. These systems solve related access problems, but PostgreSQL role commands cannot be assumed to configure either one.

References: [PostgreSQL privileges](https://www.postgresql.org/docs/current/ddl-priv.html), [default privileges](https://www.postgresql.org/docs/current/sql-alterdefaultprivileges.html), and [role membership](https://www.postgresql.org/docs/current/role-membership.html).

## Check your understanding

1. How are authentication and authorization different?
2. Why does reading a PostgreSQL table involve more than a `SELECT` grant alone?
3. Why might revoking one role's grant leave a user's access intact?
4. Why does a shared application connection still need a customer-level access policy?

Continue with [transaction control](05_transaction_control_language_tcl.md) to decide which authorized changes must succeed together.
