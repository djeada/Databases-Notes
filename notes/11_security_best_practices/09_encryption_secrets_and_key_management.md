# Encryption, Secrets, and Key Management

Database security depends on protecting data in several different states:

- **in transit** between clients and database servers,
- **at rest** on disks, snapshots, and backups,
- **in use** while applications and databases process it,
- **inside credentials and keys** used to access or decrypt systems.

Encryption is one control among many. It does not replace access control, auditing, backups, or secure application design.

## Threat model first

Before choosing encryption, ask what threat it is meant to reduce.

Examples:

| Threat | Useful controls |
| --- | --- |
| network eavesdropping | TLS with certificate validation |
| stolen disk or snapshot | storage/database encryption at rest |
| leaked backup | encrypted backup plus protected key |
| compromised database account | column/application encryption can reduce exposure |
| source-code leak | secret manager, no embedded credentials |
| stolen encryption key | key separation, KMS/HSM, rotation, access controls |

The control must protect against the relevant attacker.

## Layers

A database application often has several encryption boundaries:

```text
application
   │
   │ TLS
   ▼
database server
   │
   │ storage encryption
   ▼
disk / volume / snapshot

selected sensitive fields
   │
   └── application-level encryption
```

Each layer solves a different problem.

## Encryption in transit

Connections should use TLS when traffic crosses any untrusted or shared network.

A secure connection is not merely:

```text
TLS enabled
```

It should also validate that the server certificate belongs to the intended server.

Otherwise an attacker may terminate one encrypted connection and create another.

## PostgreSQL TLS modes

PostgreSQL clients support several SSL modes.

A useful progression is:

```text
disable
  │
require
  │
verify-ca
  │
verify-full
```

For production, `verify-full` is the strongest normal client mode because it verifies both:

- certificate chain,
- server hostname.

Example:

```bash
psql   "host=db.example.internal    dbname=shop    user=app    sslmode=verify-full    sslrootcert=/etc/ssl/certs/company-db-ca.pem"
```

Do not disable certificate validation merely to silence TLS errors.

Fix trust configuration instead.

## Private networks are not enough

A private VPC/VNet reduces exposure but does not make encryption unnecessary.

Traffic can still pass through:

- shared infrastructure,
- load balancers,
- proxies,
- service meshes,
- compromised hosts.

Defense in depth commonly uses both:

```text
private network
+
TLS
```

## Encryption at rest

At-rest encryption protects data if storage media, volume snapshots, or raw backup files are obtained outside normal database access.

It may be implemented by:

- operating-system full-disk encryption,
- cloud block-storage encryption,
- database transparent encryption,
- encrypted backup formats.

At-rest encryption does **not** stop a legitimate database process from reading data while it is running.

If the attacker has normal query access, the database decrypts data for them.

## Transparent encryption

Transparent data encryption protects physical database storage without requiring applications to encrypt each value manually.

Conceptually:

```text
SQL query
   │
   ▼
database engine
   │
decrypt/encrypt pages
   │
   ▼
encrypted files
```

Advantages:

- application code does not change,
- backups/snapshots may inherit encryption depending on platform,
- protects stolen storage.

Limitations:

- privileged database access still sees plaintext,
- keys must be protected,
- logs/temp files/backups must be considered too.

## Application-level field encryption

For especially sensitive values, applications can encrypt before sending them to the database.

```text
plaintext
   │
application encrypts
   ▼
ciphertext
   │
database stores ciphertext
```

This can protect against a database-only compromise when the decryption key is held elsewhere.

Trade-offs include:

- harder searching,
- harder indexing,
- key rotation complexity,
- loss of database-side functions over ciphertext.

## Deterministic versus randomized encryption

Randomized encryption of the same plaintext should normally produce different ciphertext.

That provides stronger confidentiality.

Deterministic encryption produces repeatable ciphertext for the same input, which can support equality matching but leaks equality patterns.

```text
Alice -> X91...
Alice -> X91...
Bob   -> P44...
```

An observer learns that the first two values are equal.

Use deterministic schemes only when the leakage is acceptable and the cryptographic design is well understood.

## Searchable encryption trade-offs

Databases are useful because they can:

- compare,
- sort,
- index,
- aggregate.

Strong application-side encryption hides those properties.

Possible approaches include:

- tokenize values,
- store a keyed hash for equality lookup,
- maintain a separate search index,
- decrypt in a trusted service.

Every workaround leaks some structure or adds operational complexity.

Do not invent cryptography casually.

## Passwords are not encrypted

User passwords should normally be **hashed**, not reversibly encrypted.

The application needs to verify a password, not recover it.

Conceptually:

```text
password
   │
slow password hash + salt
   ▼
stored verifier
```

Use a password hashing algorithm designed for passwords, such as:

- Argon2id,
- scrypt,
- bcrypt,
- PBKDF2 where appropriate.

Do not store:

- plaintext passwords,
- SHA-256(password),
- encrypted passwords intended for later decryption.

Follow the language/framework's maintained password API.

## Salts

A salt is a unique random value used for each password.

It prevents identical passwords from producing identical stored hashes and makes precomputed rainbow tables less useful.

Modern password-hashing libraries normally handle salts automatically.

The salt is not secret.

## Peppers

A **pepper** is an additional secret stored outside the password database.

It can reduce impact from a database-only leak, but it creates another secret-management dependency.

If used:

- store it in a secret manager/HSM,
- plan rotation,
- do not hard-code it.

## Secret types

Database systems use many secrets:

- service passwords,
- API keys,
- TLS private keys,
- client certificates,
- encryption keys,
- backup keys,
- replication credentials,
- cloud access credentials.

Treat each as an asset with:

- owner,
- location,
- allowed consumers,
- rotation policy,
- revocation procedure.

## Never commit secrets

Bad:

```python
DATABASE_URL = "postgresql://app:prod-password@db/prod"
```

A Git history can preserve removed secrets indefinitely.

If a secret enters version control:

1. revoke/rotate it,
2. remove it from current code,
3. consider history cleanup if required,
4. investigate where it was exposed.

Deleting the line is not enough.

## Environment variables

Environment variables are better than hard-coded secrets, but they are not a complete secret-management system.

They can leak through:

- process inspection,
- debug dumps,
- CI logs,
- crash reports,
- accidental printing.

Use them carefully.

A managed secret store is usually better for production.

## Runnable secret-injection demo

The repository includes:

[`scripts/security/connect_with_env.py`](../../scripts/security/connect_with_env.py)

Run against the local PostgreSQL demo:

```bash
export DATABASE_URL='postgresql://demo:secret@127.0.0.1:5432/test'
python scripts/security/connect_with_env.py
```

The script:

- refuses to run without `DATABASE_URL`,
- connects using the supplied value,
- prints only safe connection metadata,
- does not echo the password.

The local credential is intentionally trivial. The point is keeping connection data outside source code.

## Secret managers

Production systems commonly use:

- AWS Secrets Manager,
- Azure Key Vault,
- Google Secret Manager,
- HashiCorp Vault,
- Kubernetes-integrated secret mechanisms,
- platform workload identities.

A secret manager can provide:

- central access control,
- audit logging,
- rotation,
- short-lived credentials,
- versioning.

## Static credentials versus short-lived credentials

Static:

```text
password valid for months
```

Short-lived:

```text
workload identity
      │
      ▼
token valid for minutes
```

Short-lived credentials reduce the useful lifetime of a stolen secret.

They require:

- reliable token issuance,
- client refresh logic,
- clear fallback behavior.

## Key management systems

A KMS protects encryption keys and exposes controlled cryptographic operations.

Instead of storing the master key beside encrypted data:

```text
database backup
+
master key
```

store the master key in a separate KMS/HSM boundary.

## Envelope encryption

A common pattern:

```text
KMS master key
      │
      ▼
encrypts data-encryption key
      │
      ▼
encrypted DEK stored with ciphertext
      │
      ▼
DEK encrypts actual data
```

The master key does not encrypt every database row directly.

Benefits:

- scalable cryptographic operations,
- easier key rotation,
- separation between master and data keys.

## Key hierarchy

Example:

```text
root / master key
       │
       ├── backup-key-encryption key
       ├── application-field key
       └── analytics-export key
```

Different purposes should not automatically share one key.

Separation limits blast radius and simplifies rotation.

## Key rotation

Rotation can mean different things:

1. issue a new key for new data,
2. rewrap data-encryption keys under a new master key,
3. decrypt and re-encrypt all historical data.

These have very different costs.

Design key versioning from the beginning:

```text
ciphertext
├── key_version = 7
└── encrypted_value = ...
```

Then old records can still be decrypted during gradual migration.

## Key revocation

Revocation is powerful.

If a key is destroyed, encrypted data may become unrecoverable.

That can be:

- a feature for cryptographic deletion,
- a disaster if done accidentally.

Protect destructive key-management operations with:

- stronger authorization,
- change review,
- audit logging,
- backup/recovery planning.

## Backups

Backups should be encrypted when confidentiality requires it.

Ask:

1. Is the backup file encrypted?
2. Is transport to backup storage encrypted?
3. Who can decrypt it?
4. Is the key stored separately?
5. Does key rotation break old backups?
6. Can a restore actually access the required key?

An unreadable encrypted backup is still a failed backup.

## Replication credentials

Replication users often need powerful access.

Protect them separately from application credentials.

Use:

- dedicated role,
- restricted network,
- TLS,
- minimal replication privileges,
- rotation.

Do not reuse the public API's database login for replication.

## Logging and secrets

Never log:

- passwords,
- bearer tokens,
- private keys,
- full connection strings with credentials,
- raw encryption keys.

Redact structured logs before they leave the application.

Bad:

```text
database connection failed:
postgresql://app:SuperSecret123@db/prod
```

Better:

```text
database connection failed
host=db
database=prod
user=app
error=certificate verify failed
```

## TLS certificate lifecycle

Certificates expire.

Monitor:

- expiration date,
- issuing CA lifetime,
- hostname/SAN correctness,
- revocation where used.

A system that fails when the certificate expires at midnight has a key-management problem even if encryption was configured correctly.

## Rotation without downtime

Credential rotation can use overlapping validity:

```text
phase 1: old credential valid
phase 2: old + new valid
phase 3: applications use new
phase 4: old revoked
```

This avoids an all-at-once outage.

The exact mechanism depends on the database and identity provider.

## Separation of keys and data

Avoid:

```text
backup.tar
backup-key.txt
```

stored in the same bucket.

If one compromise retrieves both, encryption provides little additional protection.

Store keys under a separate access boundary.

## Development environments

Do not copy production secrets into developer laptops.

Use:

- separate development databases,
- synthetic or masked data,
- development-only credentials,
- separate encryption keys.

Environment isolation is part of secret management.

## Common mistakes

### TLS without hostname validation

Traffic is encrypted but the peer may not be trustworthy.

### Hard-coded connection strings

Source code becomes a credential store.

### One encryption key for everything

Rotation and incident containment become harder.

### Encrypting passwords

Passwords should be verified with password hashing.

### Storing decryption keys beside ciphertext

A single breach exposes both.

### Logging connection strings

Secrets leak into observability systems.

### Rotation policy with no tested procedure

A policy document does not prove applications can survive rotation.

## Encryption design checklist

Before production:

1. Which threat does each encryption layer address?
2. Is TLS certificate validation enabled?
3. Is storage encryption enabled where required?
4. Are backups encrypted?
5. Are field-level encryption needs identified?
6. Are user passwords hashed with a password-specific algorithm?
7. Are secrets absent from source code?
8. Is a secret manager used in production?
9. Are keys separated from encrypted data?
10. Is key versioning supported?
11. Is credential/key rotation tested?
12. Are logs checked for secret leakage?

## Related notes

- [Identity and access control](08_identity_authentication_and_access_control.md)
- [Auditing, compliance, and data governance](10_auditing_compliance_and_data_governance.md)
- [Backup and recovery](01_backup_and_recovery_strategies.md)
- [Database security overview](02_database_security.md)
