# Database Hardening and Patch Management

Hardening reduces the number of ways a database can be attacked or accidentally misused.

The goal is not to enable every security feature. It is to remove unnecessary exposure, enforce secure defaults, and keep the supported configuration continuously maintained.

## Defense in depth

A production database is protected by several layers:

```text
internet
   │
firewall / private network
   │
database listener
   │
TLS + authentication
   │
roles + privileges
   │
schema / data controls
   │
host / container / storage
```

No single layer should be assumed perfect.

## Reduce network exposure

A database generally should not be directly reachable from the public internet unless the architecture explicitly requires it.

Preferred topology:

```text
internet
   │
load balancer / API
   │
application network
   │
database private network
```

The application talks to the database over a controlled private path.

## Bind addresses intentionally

Development examples in this repository usually bind database ports to:

```text
127.0.0.1
```

rather than every host interface.

Production should use:

- private subnets,
- security groups/firewalls,
- explicit allowed sources,
- no accidental `0.0.0.0/0` exposure.

## Firewall policy

Prefer allowlists.

Example policy:

```text
app subnet -> database port ALLOW
admin VPN  -> database port ALLOW
everything else        DENY
```

Do not rely on database passwords as the only boundary.

## Administrative access

Administration should enter through controlled paths:

- VPN,
- bastion,
- privileged workstation,
- identity-aware proxy,
- managed cloud console.

Avoid exposing admin listeners broadly.

## Disable unused services

Every enabled component adds attack surface.

Review:

- unused database listeners,
- optional extensions,
- web admin consoles,
- remote management ports,
- legacy protocols,
- sample databases,
- default users.

If a feature has no owner or use case, consider removing it.

## Default accounts

Immediately review vendor/default accounts.

Actions may include:

- disable,
- remove,
- change credentials,
- restrict login,
- rename where appropriate.

Never leave installation defaults in production.

## Principle of least functionality

A database host should do database work.

Avoid mixing unrelated workloads on the same host:

```text
database
+
web server
+
build agent
+
file share
```

A compromise in any one service increases risk to the others.

## Operating-system hardening

Relevant controls include:

- supported OS release,
- regular security patches,
- minimal installed packages,
- restricted SSH access,
- host firewall,
- time synchronization,
- disk encryption,
- file permissions,
- endpoint monitoring where appropriate.

Database security depends on the host underneath it.

## Container hardening

If databases run in containers:

- pin images intentionally,
- avoid `:latest` for reproducible production,
- run supported images,
- scan images,
- use non-root execution where supported,
- restrict Linux capabilities,
- use read-only filesystems where compatible,
- mount persistent data deliberately,
- protect Docker/Kubernetes control-plane access.

A container is not a security boundary by itself.

## Image pinning

Development:

```yaml
image: postgres:latest
```

is convenient.

Production:

```yaml
image: postgres:17.6
```

or an immutable digest gives a reproducible artifact.

Pinning does not eliminate patching. It makes change explicit.

## Patch management

Security updates should follow a managed lifecycle:

```text
vendor advisory
     │
     ▼
risk assessment
     │
     ▼
staging validation
     │
     ▼
backup / rollback readiness
     │
     ▼
production rollout
     │
     ▼
verification
```

The correct speed depends on severity and exposure.

## Version inventory

Maintain an inventory of:

- database engine version,
- operating-system version,
- extension versions,
- driver versions,
- proxy/pooler versions,
- backup tools,
- monitoring agents.

You cannot patch unknown software.

## End of life

Unsupported versions stop receiving normal security updates.

Track vendor support dates before they become emergencies.

Upgrade planning should account for:

- application compatibility,
- extension support,
- replication,
- backups,
- rollback,
- performance changes.

## Extensions

Database extensions run with meaningful privileges and may execute native code.

Treat them like dependencies.

Ask:

1. Who maintains the extension?
2. Is the version supported?
3. Does the application actually need it?
4. What privileges does installation require?
5. How will it be patched?

Do not allow arbitrary extension installation by normal application roles.

## Drivers

A secure database server can still be exposed by vulnerable client drivers.

Keep:

- JDBC,
- psycopg,
- mysqlclient,
- ODBC,
- ORM dependencies

under normal dependency-management and vulnerability-scanning processes.

## Authentication configuration

For PostgreSQL, `pg_hba.conf` controls client authentication rules.

Review:

- source network,
- database,
- user,
- authentication mechanism,
- rule order.

Broad rule:

```text
host all all 0.0.0.0/0 ...
```

may be far wider than intended.

Prefer narrowly scoped rules.

## Avoid trust authentication in production

A `trust` rule means matching clients can connect without supplying a password.

That can be convenient for isolated local development.

It is usually inappropriate across a production network.

## Strong password authentication

When passwords are used, prefer modern challenge-response/password mechanisms supported by the engine.

For PostgreSQL, SCRAM-SHA-256 is the modern password mechanism.

Migration must account for:

- stored password verifier format,
- client-driver support,
- authentication rules.

## TLS

Require encrypted connections where appropriate.

Also verify certificates.

Hardening checklist:

- disable obsolete TLS versions,
- use maintained cipher suites,
- protect private keys,
- rotate certificates,
- monitor expiry.

## Database configuration

Security-relevant configuration includes:

- authentication,
- TLS,
- logging,
- extension loading,
- file access,
- statement timeouts,
- connection limits,
- replication,
- backup destinations.

Keep configuration under version-controlled infrastructure/configuration management where practical.

## Prevent dangerous resource exhaustion

Availability is part of security.

A user who can run an unlimited query may exhaust:

- CPU,
- memory,
- temporary disk,
- connection pool,
- I/O.

Controls can include:

- statement timeouts,
- connection limits,
- workload queues,
- memory limits,
- resource groups.

Do not use resource limits as a substitute for query tuning, but use them to contain failures.

## Connection limits

If the database supports 500 connections but the application opens 5,000, service can collapse before CPU is saturated.

Use:

- bounded pools,
- pool timeouts,
- role/database connection limits,
- proxies/poolers where appropriate.

Capacity limits are security/reliability boundaries too.

## Filesystem permissions

Database files should be accessible only to the operating-system account that needs them.

Protect:

- data directory,
- WAL/log files,
- TLS private keys,
- configuration files,
- backup credentials.

World-readable database files defeat database authorization.

## Backup hardening

Backups need their own boundary.

Protect against an attacker who compromises production and then deletes every backup.

Useful controls:

- separate account/project,
- immutable retention,
- restricted deletion,
- offline/cross-account copies,
- independent credentials.

## Monitoring changes

Alert on security-sensitive configuration changes such as:

- new superuser,
- new login role,
- disabled TLS,
- audit logging disabled,
- firewall broadened,
- backup retention reduced.

Configuration drift is an incident signal.

## Infrastructure as code

Representing configuration as code can improve review:

```text
pull request
   │
   ▼
review
   │
   ▼
automated deployment
   │
   ▼
drift detection
```

But IaC repositories must not contain plaintext secrets.

## Vulnerability scanning

Scan:

- operating-system packages,
- container images,
- application dependencies,
- exposed services.

A scanner result is a signal, not a complete risk assessment.

Prioritize with context:

- exploitability,
- internet exposure,
- privilege required,
- data sensitivity,
- compensating controls.

## Database-specific advisories

Subscribe to security announcements from the database vendor/community.

General OS scanning may not understand:

- database extensions,
- engine patch levels,
- managed-service notices.

## Managed services

Cloud-managed databases reduce some patching responsibility.

The provider may handle:

- host OS,
- database binaries,
- failover infrastructure.

The customer still owns:

- account permissions,
- network exposure,
- schema,
- query security,
- backup policy,
- application credentials,
- supported configuration choices.

"Managed" does not mean "secure by default for our application."

## Patch windows

Planned maintenance can use:

- rolling upgrades,
- replicas,
- blue/green environments,
- maintenance windows.

Test application behavior during failover/reconnect.

An upgrade is not complete if the database is healthy but every client crashes on connection reset.

## Emergency patching

For actively exploited vulnerabilities:

1. assess exposure,
2. apply compensating controls if needed,
3. patch faster than normal cadence,
4. verify,
5. monitor for prior compromise.

Do not skip backups/rollback preparation blindly, but balance recovery risk against exploitation risk.

## Configuration baselines

Define an expected baseline:

```text
public listener: disabled
TLS: required
application superuser: no
backup retention: 30 days
audit export: enabled
statement timeout: configured
```

Automated checks can detect drift.

## Security benchmark frameworks

Organizations may use:

- CIS Benchmarks,
- vendor hardening guides,
- cloud security baselines.

Use the benchmark matching the exact product/version.

Do not enable controls mechanically when they conflict with required functionality; document exceptions.

## Common mistakes

### Database exposed publicly because "the password is strong"

Network isolation should also reduce exposure.

### Patching only the server

Drivers and extensions remain vulnerable.

### Running unsupported versions

Known vulnerabilities accumulate.

### Installing extensions ad hoc in production

Change control disappears.

### Production uses `:latest`

Deployments become non-reproducible.

### Same account controls production and backups

Ransomware/credential compromise can destroy both.

### No resource limits

One accidental query becomes an availability incident.

## Hardening checklist

1. Is the database private by default?
2. Are firewall rules minimal?
3. Are default accounts removed/restricted?
4. Is the host/container supported and patched?
5. Are images/versions pinned intentionally?
6. Are unused extensions/services disabled?
7. Is modern authentication configured?
8. Is TLS required and validated?
9. Are filesystem permissions restrictive?
10. Are connections/query resources bounded?
11. Are backups protected by a separate boundary?
12. Are security advisories monitored?
13. Is configuration drift detected?
14. Is emergency patching rehearsed?

## Related notes

- [Database security overview](02_database_security.md)
- [Identity and access control](08_identity_authentication_and_access_control.md)
- [Encryption, secrets, and key management](09_encryption_secrets_and_key_management.md)
- [Performance monitoring and tuning](05_performance_monitoring_and_tuning.md)
- [Incident response and disaster recovery drills](12_incident_response_and_disaster_recovery_drills.md)
