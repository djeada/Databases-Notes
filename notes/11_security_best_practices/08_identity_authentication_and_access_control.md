# Identity, Authentication, and Access Control

Database security starts with answering three different questions:

1. **Who or what is connecting?** — authentication.
2. **What are they allowed to do?** — authorization.
3. **Can the action be traced back to that identity?** — accountability.

A secure design keeps those questions separate. A strong password does not compensate for excessive privileges, and least privilege is difficult to audit if every service shares one database account.

## Identity model

A common application path is:

```text
human / service / job
        │
        ▼
application identity
        │
        ▼
database login / workload identity
        │
        ▼
roles + grants
        │
        ▼
schema / table / function permissions
```

The database identity should represent a meaningful security boundary.

Examples:

- `app_api` for the public API,
- `reporting_reader` for dashboards,
- `migration_runner` for schema changes,
- `backup_operator` for backups,
- named administrator identities for humans.

Avoid one shared superuser for every workload.

## Authentication versus authorization

Authentication proves identity.

Examples:

- password,
- client certificate,
- Kerberos,
- cloud IAM token,
- managed workload identity.

Authorization decides permissions after authentication.

Examples:

```sql
GRANT SELECT ON reporting.daily_sales TO analyst;
GRANT INSERT, UPDATE ON app.orders TO app_writer;
```

An authenticated account can still be intentionally denied access to most data.

## Least privilege

**Least privilege** means granting only what a workload needs to perform its job.

Suppose an API needs to:

- read products,
- create orders,
- update order status.

It does not need:

- `DROP TABLE`,
- role creation,
- backup administration,
- access to payroll tables.

A good privilege boundary reduces the damage from:

- SQL injection,
- leaked application credentials,
- programming mistakes,
- compromised hosts.

```text
application compromised
        │
        ▼
database account permissions
        │
        ├── broad superuser -> broad damage
        └── narrow role     -> limited blast radius
```

## PostgreSQL role model

PostgreSQL roles can act as:

- login identities,
- permission groups,
- both.

A useful pattern separates login roles from group roles.

```text
login: shop_api
      │
      ├── member of app_read
      └── member of app_write
```

The group roles own permissions; the login gets membership.

## Local setup

This repository already includes a local PostgreSQL environment:

```bash
cd scripts
bash setup/start_postgres.sh
```

The development connection is:

```text
postgresql://demo:secret@127.0.0.1:5432/test
```

The credentials are intentionally simple for local learning. They are not a production credential design.

## Runnable least-privilege demo

The repository includes:

[`scripts/security/postgres_least_privilege.sql`](../../scripts/security/postgres_least_privilege.sql)

Run it inside the local PostgreSQL container:

```bash
docker exec -i postgres-local   psql -U demo -d test   < scripts/security/postgres_least_privilege.sql
```

The script creates:

- a dedicated schema,
- a sample table,
- read/write group roles,
- login roles with different memberships,
- default privilege rules for future tables.

It also prints grants so the resulting permission model is visible.

## Create group roles

A group role normally does not log in:

```sql
CREATE ROLE app_read NOLOGIN;
CREATE ROLE app_write NOLOGIN;
```

Grant object permissions:

```sql
GRANT USAGE ON SCHEMA secure_app TO app_read, app_write;

GRANT SELECT
ON ALL TABLES IN SCHEMA secure_app
TO app_read;

GRANT INSERT, UPDATE, DELETE
ON ALL TABLES IN SCHEMA secure_app
TO app_write;
```

The separation makes permission changes easier:

```text
objects -> group role -> login role
```

rather than granting every table individually to every account.

## Login roles

Create workload identities:

```sql
CREATE ROLE reporting_login
LOGIN
PASSWORD 'local-demo-only';

CREATE ROLE api_login
LOGIN
PASSWORD 'local-demo-only';
```

Assign memberships:

```sql
GRANT app_read TO reporting_login;

GRANT app_read, app_write
TO api_login;
```

The reporting account can read.

The API account can read and write.

Neither role needs superuser privileges.

## Ownership matters

The owner of an object has special rights over it.

A common production pattern is:

```text
schema owner / migration role
          │
          ├── owns tables
          │
          └── does not serve normal traffic

application role
          │
          └── receives only runtime grants
```

Do not make the application login the owner of every table if it does not need DDL rights.

## Default privileges

Grants on existing tables do not automatically cover every future table.

PostgreSQL supports default privileges:

```sql
ALTER DEFAULT PRIVILEGES
IN SCHEMA secure_app
GRANT SELECT ON TABLES TO app_read;
```

This matters when migrations continuously create new objects.

Without a default-grant strategy, a new table may be:

- accidentally inaccessible,
- accidentally exposed through an overly broad owner account.

## Public privileges

Review the implicit `PUBLIC` role.

`PUBLIC` means every database role.

For sensitive schemas, explicitly design whether general users should have:

- database `CONNECT`,
- schema `USAGE`,
- function execution.

Do not assume defaults match the application's security model.

## Schema isolation

Schemas can provide administrative separation:

```text
database
├── app
├── reporting
├── internal
└── audit
```

A reporting user may have access only to:

```text
reporting.*
```

Schema permissions do not replace table permissions, but they add another boundary.

## Read-only is more than SELECT

A "read-only" role should be reviewed for:

- table writes,
- sequence changes,
- function execution,
- temporary object creation,
- access to sensitive system functions.

Functions can execute with the caller's rights or, in some systems, with definer rights.

A role that cannot directly update a table might still call a powerful function.

## Security definer functions

PostgreSQL supports `SECURITY DEFINER` functions.

They execute with the function owner's privileges.

This can be useful for narrowly controlled operations:

```text
low-privilege caller
      │
      ▼
approved function
      │
      ▼
specific privileged action
```

But a poorly written definer function becomes a privilege-escalation path.

Important defenses include:

- fixed/controlled `search_path`,
- parameterized SQL,
- minimal owner privileges,
- narrow `EXECUTE` grants,
- code review.

## Row-level security

Sometimes table-level grants are not enough.

Suppose all tenants share one table:

```text
orders
├── tenant_id
├── order_id
└── total
```

The application should only see rows for its tenant.

PostgreSQL Row-Level Security (RLS) can enforce row policies inside the database.

Conceptually:

```text
SELECT * FROM orders
       │
       ▼
RLS policy
       │
       ├── tenant matches -> row visible
       └── tenant differs -> hidden
```

RLS can provide defense in depth for multi-tenant systems.

It also increases complexity. Policies must be tested for:

- reads,
- inserts,
- updates,
- deletes,
- privileged/bypass roles.

## Views as security boundaries

A view can expose only selected columns.

Base table:

```text
customers
├── id
├── name
├── email
├── password_hash
└── internal_risk_score
```

Reporting view:

```sql
CREATE VIEW reporting.customers AS
SELECT id, name
FROM app.customers;
```

The reporting account receives access to the view, not the base table.

This is useful for minimizing sensitive-data exposure.

## Column privileges

Some databases support column-level grants.

PostgreSQL can grant access to specific columns:

```sql
GRANT SELECT (customer_id, display_name)
ON app.customers
TO analyst;
```

Column permissions can help, but views are often clearer when the exposed interface has business meaning.

## Human administrators

Human administration should be attributable.

Prefer:

```text
alice_admin
bob_admin
carol_admin
```

over:

```text
shared_dba
```

Named identities improve:

- auditability,
- revocation,
- incident investigation,
- privilege reviews.

Emergency "break-glass" access should be exceptional, monitored, and tested.

## Service accounts

Each application or service should generally have its own database identity.

Bad:

```text
website ─┐
worker  ─┼──► db_user
billing ─┘
```

Better:

```text
website -> website_db
worker  -> worker_db
billing -> billing_db
```

If one credential leaks, only that service's privileges need to be considered.

## Password authentication

When passwords are used:

- use long randomly generated service passwords,
- store them in a secret manager,
- rotate them,
- do not commit them,
- do not share human accounts.

Do not force arbitrary periodic rotation of human passwords without a threat-driven reason if the policy encourages weak predictable changes. Follow the organization's identity provider and current security guidance.

## Workload identity

Cloud platforms increasingly support short-lived identity tokens or managed workload identities.

Conceptually:

```text
application workload
      │
      ▼
cloud identity service
      │
      ▼
short-lived database token
      │
      ▼
database
```

Advantages can include:

- fewer long-lived static passwords,
- centralized revocation,
- identity-based audit trails.

The exact mechanism depends on the database and platform.

## Client certificates

Mutual TLS can authenticate clients with certificates.

```text
client certificate
      │
      ▼
TLS handshake
      │
      ▼
database validates issuer / identity
```

Certificates still need:

- issuance,
- rotation,
- revocation,
- private-key protection.

They move credential management; they do not eliminate it.

## Connection pooling

A connection pool often uses one database identity for many application users.

```text
Alice ─┐
Bob   ─┼──► web app ─► pool ─► app_db_role
Carol ─┘
```

The database may not directly know which end user initiated each request.

If user-level accountability matters, propagate application identity into:

- structured audit events,
- transaction/session metadata where safe,
- request IDs.

Do not create thousands of database logins merely to imitate application users unless the architecture genuinely requires that model.

## Privilege review

Privileges accumulate.

A quarterly or release-based review should answer:

1. Which login roles still exist?
2. Which services still use them?
3. Which group roles are they members of?
4. Which schemas/tables/functions can they access?
5. Are there unused elevated roles?
6. Are former employees or retired workloads removed?
7. Do default privileges still match policy?

## PostgreSQL inspection queries

List login-capable roles:

```sql
SELECT
    rolname,
    rolsuper,
    rolcreatedb,
    rolcreaterole,
    rolcanlogin
FROM pg_roles
WHERE rolcanlogin
ORDER BY rolname;
```

List role memberships:

```sql
SELECT
    member_role.rolname AS member,
    granted_role.rolname AS granted_role
FROM pg_auth_members m
JOIN pg_roles granted_role
  ON granted_role.oid = m.roleid
JOIN pg_roles member_role
  ON member_role.oid = m.member
ORDER BY member, granted_role;
```

Review these queries from an appropriately privileged administrative account.

## Separation of duties

A mature environment may separate:

- deployment/migration access,
- application runtime access,
- backup administration,
- security audit review,
- infrastructure administration.

The objective is to avoid one credential being able to:

1. change data,
2. erase the evidence,
3. alter backups,
4. grant itself more access.

Separation of duties reduces insider and credential-compromise risk.

## Temporary elevation

Sometimes a service needs temporary elevated access.

Prefer:

```text
normal low privilege
      │
approved elevation
      │
short lifetime
      │
automatic expiry
```

over permanently granting powerful privileges "just in case."

Cloud IAM systems and privileged-access-management tools can support this workflow.

## Failed authentication

Monitor failed logins, but interpret them carefully.

A spike can mean:

- attack attempts,
- expired credentials,
- broken deployment configuration,
- a retired service still retrying.

Useful event context includes:

- database user,
- source network,
- timestamp,
- authentication mechanism,
- application name.

Avoid logging plaintext passwords or authentication secrets.

## Common mistakes

### Application runs as superuser

A single SQL injection bug becomes catastrophic.

### Shared DBA password

Actions cannot be reliably attributed.

### Grants only ever increase

Old permissions remain after responsibilities change.

### New tables are created with accidental defaults

Use migration and default-privilege policies.

### Role names describe people rather than responsibilities

Prefer reusable permission roles such as `reporting_read`.

### Security exists only in application code

Database permissions provide an independent layer.

## Practical access-control checklist

Before production:

1. Does every workload have a distinct identity?
2. Does the application avoid superuser/owner access?
3. Are permissions grouped into clear roles?
4. Are default privileges defined?
5. Is `PUBLIC` access understood?
6. Are sensitive columns hidden from reporting users?
7. Does multi-tenancy need row-level security?
8. Are powerful functions reviewed?
9. Are human administrators individually identifiable?
10. Can credentials be revoked quickly?
11. Are role memberships periodically reviewed?
12. Are failed authentication events monitored?

## Related notes

- [Database security overview](02_database_security.md)
- [Encryption, secrets, and key management](09_encryption_secrets_and_key_management.md)
- [Auditing, compliance, and data governance](10_auditing_compliance_and_data_governance.md)
- [Database hardening and patch management](11_database_hardening_and_patch_management.md)
- [SQL injection](06_sql_injection.md)
