# Auditing, Compliance, and Data Governance

A secure database should answer:

- who accessed data,
- what changed,
- when it happened,
- which application/request initiated the action,
- whether the action was permitted,
- how long the evidence is retained.

Auditing is not the same as application logging, and compliance is not the same as security. Good systems use both technical controls and governance processes.

## Audit goals

Audit data commonly supports:

- incident investigation,
- privileged-access review,
- change accountability,
- fraud detection,
- compliance evidence,
- debugging critical data changes.

An audit trail should be designed from explicit questions.

Example:

> Who changed this customer's payout account from value A to value B, and from which application request?

That requires more context than a generic "UPDATE succeeded" log.

## Audit layers

Database activity can be observed at several levels:

```text
end user
   │
application audit event
   │
database session/query log
   │
row-change audit record
   │
cloud / infrastructure audit log
```

Each layer sees different information.

A connection pool may know only the shared database account, while the application knows the real end user.

## Application audit events

Applications understand business meaning.

Example event:

```json
{
  "event": "customer_email_changed",
  "actor_user_id": 42,
  "customer_id": 1007,
  "request_id": "req-abc",
  "timestamp": "2026-10-01T12:00:00Z"
}
```

This is more meaningful than only logging:

```text
UPDATE customers SET email = $1 WHERE id = $2
```

But application logs can be bypassed by direct database administration, so database-level auditing may still be required.

## Database audit logs

Database logs can record:

- authentication attempts,
- session start/end,
- DDL,
- role/permission changes,
- queries,
- errors,
- checkpoints or operational events.

Logging every statement can generate enormous volume and may expose sensitive values.

Choose audit scope deliberately.

## Row-change audit tables

For selected critical tables, a trigger can store old/new values.

The repository includes:

[`scripts/security/postgres_audit_trigger_demo.sql`](../../scripts/security/postgres_audit_trigger_demo.sql)

Run:

```bash
docker exec -i postgres-local   psql -U demo -d test   < scripts/security/postgres_audit_trigger_demo.sql
```

The demo:

1. creates a sample customer table,
2. creates an append-only-style audit table,
3. adds a trigger for update/delete events,
4. changes a row,
5. prints the audit history.

## Example audit schema

```sql
CREATE TABLE audit.customer_history (
    audit_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    changed_at timestamptz NOT NULL DEFAULT now(),
    db_user text NOT NULL DEFAULT current_user,
    action text NOT NULL,
    customer_id bigint NOT NULL,
    old_row jsonb,
    new_row jsonb
);
```

The audit record stores both context and row state.

## Trigger example

Conceptually:

```text
UPDATE customers
       │
       ▼
audit trigger
       │
       ├── old row
       ├── new row
       ├── current user
       └── timestamp
       │
       ▼
audit history
```

A trigger can capture changes made outside the main application.

## Audit table limitations

A normal table in the same database is not tamper-proof.

A sufficiently privileged user may be able to:

- modify audit rows,
- disable triggers,
- truncate the audit table,
- alter timestamps.

For stronger assurance, send audit events to a separate security boundary:

```text
production database
      │
      ▼
central audit pipeline
      │
      ▼
restricted immutable/retained storage
```

## Append-only design

Audit systems often aim for append-only behavior.

Controls may include:

- separate owner,
- no UPDATE/DELETE grants to normal operators,
- external log export,
- write-once retention storage,
- cryptographic integrity mechanisms.

"Append-only" should describe an enforced control, not only developer intention.

## Correlation IDs

A request ID helps connect layers.

```text
HTTP request: req-123
      │
      ├── application logs
      ├── audit event
      └── database session metadata
```

Then an incident can reconstruct one transaction across systems.

## End-user identity through a connection pool

A pool may use one login:

```text
Alice ─┐
Bob   ─┼──► app_db
Carol ─┘
```

The database alone sees `app_db`.

Possible approaches include:

- application audit records,
- setting a safe session-local request/user identifier,
- stored procedures accepting actor context,
- structured transaction metadata.

Never trust arbitrary client-supplied actor IDs without authentication.

## Privileged activity

Prioritize auditing:

- superuser logins,
- role grants/revokes,
- schema changes,
- security configuration changes,
- backup restore actions,
- bulk exports,
- disabling audit controls.

These events have high impact even if they are rare.

## Authentication events

Monitor:

- failed login count,
- successful privileged login,
- source IP/network,
- unexpected geographic or network source where meaningful,
- disabled account use.

Be careful with noisy alerts. Broken deployments can generate thousands of failed logins.

## Data classification

Governance starts by understanding what the database stores.

A simple classification might be:

```text
public
internal
confidential
restricted
```

Examples:

| Data | Possible classification |
| --- | --- |
| product catalog | public/internal |
| customer email | confidential |
| authentication secrets | restricted |
| payment-card data | restricted |

Classification should drive:

- access,
- encryption,
- logging,
- retention,
- export controls.

## Data inventory

You cannot protect data you do not know exists.

Maintain an inventory of:

- databases,
- schemas,
- sensitive columns,
- owners,
- retention requirements,
- data flows,
- replicas,
- backups,
- analytics copies.

Shadow exports and abandoned databases are common security risks.

## Data minimization

Store only data with a justified purpose.

Bad pattern:

```text
"we may need this someday"
```

creates:

- larger breach impact,
- more compliance obligations,
- more backup copies,
- harder deletion.

Minimization reduces attack surface.

## Purpose limitation

A dataset collected for one purpose should not automatically be reused for another.

Technical controls can support this through:

- separate schemas,
- restricted roles,
- approved views,
- separate analytics copies,
- access review.

Governance decisions belong to the organization, not only the database administrator.

## Retention

Every sensitive dataset should have a lifecycle:

```text
created
  │
actively used
  │
archived
  │
expired
  │
deleted
```

Retention policies should address:

- primary data,
- replicas,
- caches,
- search indexes,
- exports,
- backups,
- audit logs.

Deleting one primary row may not immediately remove every historical copy.

## Legal hold

Sometimes normal deletion must pause because data is required for litigation, investigation, or regulation.

A mature retention process distinguishes:

```text
normal expiry
vs
legal hold
```

This usually requires coordination between legal/compliance and technical teams.

## Data deletion

Deletion requirements can be difficult in distributed systems.

Copies may exist in:

- replicas,
- backups,
- object storage,
- CDC streams,
- warehouses,
- search indexes.

Document how deletion propagates.

Do not promise immediate physical erasure from immutable backup media if the platform does not support it.

## Masking

Data masking reduces exposure in lower-trust contexts.

Example:

```text
alice@example.com
       │
       ▼
a***@example.com
```

Uses include:

- support dashboards,
- development copies,
- screenshots,
- logs.

Masking is not encryption.

If the original data still exists elsewhere, masking only reduces exposure in that representation.

## Tokenization

Tokenization replaces sensitive values with opaque tokens.

```text
card number
    │
    ▼
token vault
    │
    ├── original protected
    └── token returned
```

Applications use the token instead of repeatedly storing the original value.

This can reduce sensitive-data scope.

## Development/test data

Do not clone production databases into development without controls.

Safer options:

- synthetic data,
- masked copies,
- subset datasets,
- generated fixtures.

A laptop with a production dump can bypass many server-side controls.

## Compliance frameworks

Organizations may need to meet requirements from frameworks or regulations such as:

- GDPR,
- HIPAA,
- PCI DSS,
- SOX,
- ISO 27001,
- SOC 2.

Requirements depend on:

- jurisdiction,
- industry,
- contractual obligations,
- exact data handled.

This note is technical guidance, not legal advice.

Use current authoritative requirements for compliance decisions.

## Evidence

Compliance audits often ask for evidence such as:

- access reviews,
- configuration records,
- backup restore tests,
- patch history,
- privileged activity logs,
- incident-response exercises,
- retention settings.

Automate evidence collection where possible.

Screenshots taken once a year are weak operational evidence.

## Audit retention

Audit logs need a retention policy too.

Keeping them forever can:

- increase privacy risk,
- raise storage costs,
- make searches slower.

Keeping them for too little time can undermine investigations.

Set retention from:

- incident-detection window,
- legal requirements,
- operational needs.

## Log integrity

Protect logs from the systems/users they are intended to audit.

A common architecture:

```text
database host
   │
   ▼
log collector
   │
   ▼
central security storage
   │
   ├── restricted writes
   └── retention policy
```

If an attacker compromises the database server, local logs may be deleted.

Remote collection improves resilience.

## Sensitive values in logs

Avoid recording:

- passwords,
- access tokens,
- full payment data,
- encryption keys,
- secrets in SQL literals.

Parameterized queries also reduce accidental secret exposure in SQL text.

Log enough context to investigate without turning logging into another sensitive database.

## Database activity monitoring

Larger environments may use dedicated Database Activity Monitoring (DAM) or security products.

These can analyze:

- privileged access,
- unusual query volume,
- sensitive-table reads,
- suspicious authentication,
- policy violations.

They complement native database logs rather than automatically replacing them.

## Anomaly detection

Useful anomalies can include:

- service account suddenly exporting millions of rows,
- administrator login from an unusual source,
- schema changes outside deployment windows,
- new role grants,
- high failed-login rate.

Alerts should include enough context for triage.

## Audit review

Collecting logs without reviewing them provides limited value.

Define:

- which alerts are real-time,
- which reports are weekly/monthly,
- who owns review,
- what escalation path exists.

## Common mistakes

### Logging everything without a purpose

Costs rise and sensitive values accumulate.

### Audit table writable by application owner

A compromised application can alter its own evidence.

### No end-user correlation

Every action appears to come from one pooled service account.

### Production data copied freely into test

Security boundary disappears.

### Retention applies only to primary tables

Backups and derived systems are forgotten.

### Compliance treated as an annual paperwork task

Controls should run continuously.

## Governance checklist

1. Is sensitive data classified?
2. Is there an owner for each important dataset?
3. Can privileged changes be attributed?
4. Are critical row changes audited where required?
5. Are logs exported away from the database host?
6. Are audit logs protected from modification?
7. Are secrets excluded from logs?
8. Are application user/request IDs correlated?
9. Is retention defined for primary and derived data?
10. Are development datasets synthetic or masked?
11. Are access reviews performed?
12. Is evidence collected continuously?

## Related notes

- [Identity and access control](08_identity_authentication_and_access_control.md)
- [Encryption, secrets, and key management](09_encryption_secrets_and_key_management.md)
- [Database hardening and patch management](11_database_hardening_and_patch_management.md)
- [Incident response and disaster recovery drills](12_incident_response_and_disaster_recovery_drills.md)
