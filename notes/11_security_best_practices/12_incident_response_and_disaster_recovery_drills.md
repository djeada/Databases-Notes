# Incident Response and Disaster Recovery Drills

A security or reliability incident is the wrong time to discover that:

- the backup cannot restore,
- no one knows the database owner,
- the emergency credential expired,
- failover changes connection strings,
- the team cannot identify what data was exposed.

Incident response and disaster recovery should be practiced before they are needed.

## Incident response versus disaster recovery

They overlap but answer different questions.

**Incident response** focuses on:

- what happened,
- how to contain it,
- what was affected,
- how to eradicate the cause,
- what evidence must be preserved.

**Disaster recovery** focuses on:

- how to restore service,
- how much data loss is acceptable,
- how quickly systems must recover.

```text
security incident
     │
     ├── investigate + contain
     │
     └── restore/rebuild safely
```

## Incident lifecycle

A useful lifecycle:

```text
prepare
  │
detect
  │
triage
  │
contain
  │
eradicate
  │
recover
  │
learn
```

Real incidents may loop between stages.

## Preparation

Before an incident, maintain:

- architecture diagrams,
- asset inventory,
- database owners,
- escalation contacts,
- credential-rotation procedure,
- backup/restore runbooks,
- clean rebuild procedure,
- log locations,
- retention periods,
- emergency communication channel.

Documentation should be usable when normal systems are unavailable.

## Detection

Signals can include:

- unusual authentication,
- mass data export,
- unexpected schema changes,
- backup deletion,
- high error rates,
- replication lag,
- corrupted pages,
- ransomware notes,
- abnormal query volume.

Detection should lead to actionable context, not only an alarm.

## Triage

Initial questions:

1. Which database/service is affected?
2. Is the incident ongoing?
3. Is confidentiality, integrity, availability, or all three affected?
4. Which credentials may be compromised?
5. Is replication spreading damage?
6. Are backups safe?
7. What evidence must be preserved?
8. Does the incident require legal/compliance escalation?

## Preserve evidence

Do not destroy useful evidence in a rush to clean up.

Potential evidence:

- authentication logs,
- query/audit logs,
- cloud control-plane logs,
- host telemetry,
- database WAL/binlog,
- snapshots,
- process/network data.

Coordinate with the organization's incident process.

## Containment

Containment depends on the event.

Possible actions:

- revoke credential,
- block source network,
- disable compromised service account,
- isolate application host,
- stop a malicious job,
- remove public exposure,
- freeze administrative changes.

Containment should minimize further damage without unnecessarily destroying evidence.

## Credential compromise

If a database credential is stolen:

```text
revoke/rotate credential
      │
      ▼
identify where it was used
      │
      ▼
review actions during exposure window
      │
      ▼
fix source of leak
      │
      ▼
issue new credential
```

Do not rotate only the password and declare the incident closed.

The attacker may have:

- created another user,
- changed data,
- copied data,
- installed persistence elsewhere.

## Ransomware scenario

A dangerous architecture:

```text
production admin
       │
       ├── can delete production
       └── can delete every backup
```

A stronger design:

```text
production boundary
      │
      ▼
backup copy
      │
      ▼
separate account / immutable retention
```

Recovery plans should assume production credentials may be compromised.

## Integrity incident

Not every incident is an outage.

Example:

```text
application bug updates 2 million prices incorrectly
```

Service may still be online.

Recovery may require:

- stop further bad writes,
- identify affected interval,
- determine correct source,
- restore to side database,
- compare,
- repair selected rows.

This is why point-in-time recovery and audit history matter.

## Availability incident

Example:

```text
primary database unavailable
```

Questions:

- can a replica fail over?
- what data lag exists?
- how do clients reconnect?
- what happens to in-flight transactions?
- who authorizes failover?

A failover that takes 20 seconds but requires 45 minutes of manual DNS changes is not a 20-second recovery.

## RPO

**Recovery Point Objective (RPO)** is the acceptable data-loss window.

Example:

```text
RPO = 5 minutes
```

The recovery design should allow restoration to within roughly five minutes of the incident, under the defined assumptions.

RPO is a business requirement, not a backup schedule by itself.

## RTO

**Recovery Time Objective (RTO)** is the target time to restore the service.

Example:

```text
RTO = 30 minutes
```

RTO includes more than database startup:

- detection,
- decision making,
- restore/failover,
- application reconnect,
- validation.

## RPO/RTO diagram

```text
last recoverable point         incident               service restored
        │                         │                          │
        └──── data-loss window ───┘                          │
                  RPO                                       │
                                  └──── downtime ────────────┘
                                             RTO
```

## Failover versus restore

Failover:

```text
primary unavailable
      │
      ▼
promote replica
```

Restore:

```text
data damaged/lost
      │
      ▼
recover from backup/WAL
```

Replication helps availability.

Backups help recover historical state.

They solve different failure classes.

## Replication can copy mistakes

If an administrator runs:

```sql
DELETE FROM customers;
```

replication may faithfully copy the delete.

That means:

```text
replica != backup
```

A recovery design needs historical copies or point-in-time recovery.

## Restore drills

A backup should be tested by restoring it.

The repository includes:

[`scripts/security/postgres_restore_drill.sh`](../../scripts/security/postgres_restore_drill.sh)

It uses the local `postgres-local` container and a disposable database named:

```text
security_restore_drill
```

The script:

1. creates known data,
2. takes a `pg_dump`,
3. drops the disposable database,
4. recreates it,
5. restores the dump,
6. verifies expected rows,
7. cleans up.

Run:

```bash
bash scripts/security/postgres_restore_drill.sh
```

It never touches the repository's normal `test` database.

## What a restore drill should verify

Do not stop at "restore command returned zero."

Verify:

- row counts,
- critical constraints,
- important queries,
- application connection,
- permissions,
- extensions,
- sequences/identities,
- point-in-time target,
- recovery duration.

## Recovery validation

A restored database can be syntactically healthy but logically wrong.

Example:

```text
database accepts connections
but
last 6 hours of orders missing
```

Validation should compare against expected recovery point.

## Restore to a separate environment

For investigation, restore into isolation:

```text
backup
  │
  ▼
forensic/recovery environment
```

Benefits:

- no accidental overwrite of production,
- compare current versus recovered state,
- validate before cutover.

## Point-in-time recovery

PITR combines:

- base backup,
- continuous transaction log/WAL archive.

Conceptually:

```text
base backup
   │
WAL 1
WAL 2
WAL 3
   │
restore until chosen timestamp
```

Useful for recovering to just before:

- accidental delete,
- bad migration,
- corrupt import.

## Recovery timeline

Document the event sequence.

Example:

```text
10:02 bad migration starts
10:04 alerts fire
10:07 writes disabled
10:10 restore begins
10:27 restored to 10:01:59
10:34 validation passes
10:38 traffic restored
```

Timelines support both operations and post-incident learning.

## Disaster recovery topology

A regional design may include:

```text
region A
 primary + replicas
      │
      └──── backups / replication ───► region B
                                         │
                                         ▼
                                  recovery capacity
```

Questions:

- is region B warm or cold?
- are credentials/configuration available?
- is DNS/failover automated?
- how current is data?
- can applications run there?

## Cold, warm, and hot recovery

### Cold

Infrastructure is created after disaster.

Cheaper, slower recovery.

### Warm

Some infrastructure/data is ready.

Moderate cost and recovery time.

### Hot

Secondary environment is continuously ready.

Higher cost, faster potential recovery.

Choose based on RTO/RPO, not preference.

## Dependency recovery

The database may depend on:

- DNS,
- identity provider,
- secret manager,
- network routing,
- object storage,
- KMS.

A DR plan that restores PostgreSQL but cannot retrieve its TLS key or application secret is incomplete.

## Configuration backups

Back up more than data.

Include:

- schema,
- roles/grants,
- extensions,
- configuration,
- infrastructure definitions,
- monitoring rules,
- runbooks.

Data alone may not recreate a usable service.

## Key recovery

Encrypted backups require encryption keys.

Test that disaster recovery can access:

- KMS,
- HSM,
- certificate authority,
- secret manager.

Do not discover during an outage that the only key administrator account was in the failed environment.

## Tabletop exercise

A tabletop is a discussion-based simulation.

Example scenario:

> At 09:00, the API database's application credential appears in a public repository. Logs show successful connections from an unknown network source for 40 minutes.

Ask the team:

1. Who leads the incident?
2. How is credential revoked?
3. Which logs are preserved?
4. How is data access scope determined?
5. Are backups isolated?
6. What applications break after rotation?
7. When is service safe to resume?

Tabletops expose missing procedures cheaply.

## Technical game day

A game day performs real controlled failure.

Examples:

- terminate a replica,
- expire a development certificate,
- restore a backup,
- revoke a test service credential,
- simulate disk-full in staging.

Do not run destructive experiments against production without an approved safe design.

## Chaos and failure injection

Failure injection can validate assumptions.

But the objective should be explicit:

```text
hypothesis:
"application reconnects within 30 seconds after primary failover"
```

Measure the result.

Avoid random breakage without learning goals.

## Incident communication

Define channels before incidents.

Audiences may include:

- engineering,
- security,
- leadership,
- customer support,
- legal/compliance,
- customers.

Keep factual separation between:

- confirmed facts,
- current hypothesis,
- next action.

## Post-incident review

A useful review asks:

- what happened?
- why did controls not prevent it?
- what detected it?
- what slowed recovery?
- what worked?
- what changes reduce recurrence?

Focus on systems/process, not blame.

## Action items

Good action items are:

- specific,
- owned,
- prioritized,
- tracked to completion.

Bad:

```text
"be more careful"
```

Good:

```text
"block database public ingress in Terraform policy by 2026-11-01"
```

## Recovery metrics

Track real results:

- backup success rate,
- restore success rate,
- restore duration,
- failover duration,
- observed replica lag,
- incident detection time,
- credential rotation time.

Then compare to RTO/RPO.

## Common mistakes

### Backups never restored

Backup success proves only that a file was produced.

### Runbook requires the failed system

Documentation or credentials disappear with the outage.

### Replica treated as historical recovery

Replication copies mistakes.

### Incident cleanup destroys evidence

Investigation becomes harder.

### Credential rotated but persistence not checked

Attacker-created access remains.

### RTO excludes decision/validation time

Real outage lasts much longer than the metric suggests.

## Drill cadence

Cadence depends on risk, but mature systems commonly schedule:

- regular restore tests,
- periodic failover tests,
- annual or more frequent incident exercises,
- extra drills after architecture changes.

The key is continuous evidence, not a specific calendar rule.

## Practical incident-readiness checklist

1. Are database owners and contacts known?
2. Can credentials be revoked quickly?
3. Are logs retained outside the database host?
4. Are backups isolated from production credentials?
5. Has a restore succeeded recently?
6. Is restore duration measured?
7. Are RPO and RTO explicit?
8. Can the application reconnect after failover?
9. Are KMS/secrets available during regional failure?
10. Is evidence-preservation guidance documented?
11. Has the team run a tabletop?
12. Are post-incident actions tracked?

## Related notes

- [Backup and recovery](01_backup_and_recovery_strategies.md)
- [Crash recovery](07_crash_recovery_in_databases.md)
- [Auditing and data governance](10_auditing_compliance_and_data_governance.md)
- [Database hardening](11_database_hardening_and_patch_management.md)
- [Database security overview](02_database_security.md)
