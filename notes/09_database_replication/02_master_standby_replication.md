# Primary–Standby Replication

Primary–standby replication is a replication topology in which one database server acts as the authoritative writer and one or more standby servers follow the primary's changes.

Older material often calls this:

```text
master–standby
master–replica
master–slave
```

Modern PostgreSQL documentation uses:

```text
primary
standby
```

so those terms will be used here.

A simple topology is:

```text
                         Applications
                              |
                 +------------+------------+
                 |                         |
              writes                    some reads
                 |                         |
                 v                         v
          +--------------+        +--------------+
          |   Primary    |        |   Standby 1  |
          | read/write   |------->|  read-only   |
          +------+-------+   WAL  +--------------+
                 |
                 | WAL
                 v
          +--------------+
          |   Standby 2  |
          |  read-only   |
          +--------------+
```

The primary accepts changes.

The standbys receive and replay those changes.

Depending on the configuration, standbys can provide:

```text
read scaling
high-availability candidates
disaster-recovery copies
backup offloading
```

But simply having a standby does not automatically guarantee:

```text
zero data loss
automatic failover
fresh reads
safe split-brain prevention
historical recovery
```

Those are separate design decisions.

## What problem does primary–standby replication solve?

Consider a database running on one machine:

```text
Application
     |
     v
+-------------+
| PostgreSQL  |
| Primary     |
+-------------+
```

If the machine fails completely:

```text
Application
     |
     X
+-------------+
| failed      |
+-------------+
```

the service cannot use the database until that server is repaired or restored elsewhere.

Now add a standby:

```text
               WAL
Primary -----------------> Standby
```

The standby continuously follows changes.

If the primary fails, the standby may already contain nearly all—or, depending on the durability configuration, all—of the required database state.

That can significantly reduce recovery time.

## Replication and failover are not the same thing

Replication means:

```text
another node is receiving database changes
```

Failover means:

```text
another node becomes the authoritative writer
```

These are separate mechanisms.

You can have perfectly functioning replication but no automatic failover.

For example:

```text
Primary ------------> Standby
   X
```

If the primary fails, somebody still has to decide:

```text
Is the primary really dead?

Is the standby sufficiently current?

May we safely promote it?

How will applications find it?

How do we stop the old primary from coming back
and accepting writes?
```

PostgreSQL provides replication and promotion primitives, but PostgreSQL itself does not supply the complete external failure-detection and automatic-failover system.

## Follow one PostgreSQL transaction

Suppose the application executes:

```sql
BEGIN;

INSERT INTO orders(order_id, customer_id, amount)
VALUES (104, 27, 89.00);

COMMIT;
```

On the primary, PostgreSQL does not replicate that SQL string to the physical standby.

Instead, the primary produces Write-Ahead Log (WAL) describing the low-level database changes needed for recovery.

Conceptually:

```text
SQL transaction
      |
      v
PostgreSQL modifies database state
      |
      v
generate WAL records
      |
      v
WAL becomes durable on primary
      |
      v
stream WAL to standby
```

On the standby:

```text
receive WAL
     |
     v
write WAL
     |
     v
flush WAL
     |
     v
replay WAL
     |
     v
standby database reflects transaction
```

This pipeline is the key to understanding PostgreSQL physical replication.

## PostgreSQL physical replication is WAL replication

PostgreSQL physical streaming replication works by transmitting WAL records from the primary to the standby.

The basic processes are conceptually:

```text
PRIMARY

transactions
    |
    v
   WAL
    |
    v
walsender
    |
    | TCP replication connection
    v
=============================
    |
    v
walreceiver
    |
    v
STANDBY WAL
    |
    v
recovery / replay
    |
    v
standby data files
```

The standby reconstructs database changes by replaying WAL.

This is why physical replication is tightly connected to PostgreSQL's storage and recovery implementation rather than simply replaying SQL statements.

PostgreSQL describes streaming replication as sending WAL incrementally from the primary to the standby.

## Receive, write, flush, and replay are different events

A crucial mental model is:

```text
PRIMARY                         STANDBY

generate WAL
    |
    +---------- send ---------->
                              receive
                                 |
                                 v
                               write
                                 |
                                 v
                               flush
                                 |
                                 v
                               replay
                                 |
                                 v
                         visible database state
```

These steps mean different things.

| Stage | Meaning |
|---|---|
| Sent | Primary transmitted the WAL |
| Written | Standby wrote WAL to its local filesystem |
| Flushed | Standby reports WAL durably flushed |
| Replayed | Standby applied the WAL to its database state |

PostgreSQL exposes these distinctions through replication positions such as `sent_lsn`, `write_lsn`, `flush_lsn`, and `replay_lsn`.

## LSN: PostgreSQL's progress coordinate

An LSN, or Log Sequence Number, identifies a position in PostgreSQL's WAL stream.

Conceptually:

```text
WAL:

... ---- A/B100 ---- A/B200 ---- A/B300 ---- A/B400 ...
```

Suppose:

```text
Primary current WAL:      A/B400

Standby written:          A/B380
Standby flushed:          A/B370
Standby replayed:         A/B350
```

Then the standby has:

```text
received more WAL than it has replayed
```

A replica can therefore be durable relatively far forward while its query-visible database state remains further behind.

That distinction becomes very important for synchronous replication.

## Asynchronous streaming replication

PostgreSQL streaming replication is asynchronous unless synchronous replication is explicitly configured.

A simplified commit timeline is:

```text
Client                 Primary                Standby
  |                       |                      |
  |---- transaction ----->|                      |
  |                       |                      |
  |                       | local commit         |
  |                       |                      |
  |<------ SUCCESS -------|                      |
  |                       |                      |
  |                       |------ WAL ---------->|
  |                       |                      |
  |                       |                 receive
  |                       |                 replay
```

The important ordering is:

```text
client receives SUCCESS

before

standby is necessarily caught up
```

This gives asynchronous replication its principal advantages:

```text
lower commit latency
less dependence on standby health
```

but creates two consequences:

```text
stale reads

possible loss of recently acknowledged writes
after certain primary failures
```

PostgreSQL explicitly documents that asynchronous log shipping creates a window in which transactions committed on the primary may not yet exist on the standby.

## Concrete stale-read example

Suppose:

```text
Primary:
orders 1 ... 104

Standby:
orders 1 ... 103
```

The application creates order `104` on the primary:

```text
POST /orders

→ primary

SUCCESS
```

Immediately afterward the frontend asks:

```text
GET /orders/104
```

but the load balancer routes the read to a standby.

The standby has not yet replayed the relevant WAL.

It returns:

```text
not found
```

The application may appear broken even though replication is functioning exactly as configured.

This is replication lag.

## Read-your-writes consistency

A user often expects:

```text
I just created the order.

Therefore I should immediately be able to read it.
```

Asynchronous replica reads do not automatically guarantee that.

Common application designs include:

### Read from the primary after a write

```text
write → primary
confirmation read → primary
later ordinary reads → replica
```

### Return the created object from the write request

Instead of:

```text
POST
then
GET
```

the write response itself contains the committed result.

### Wait until a standby reaches a known WAL position

The application or infrastructure can require a replica to catch up before serving a consistency-sensitive read.

Which design is appropriate depends on the business semantics.

## Hot standby

A PostgreSQL standby used only for failover does not necessarily have to serve ordinary application queries.

A hot standby is a standby that accepts read-only queries while recovery/replay continues.

For example:

```sql
SELECT *
FROM orders
WHERE customer_id = 27;
```

can be executed on a hot standby.

The server still cannot accept ordinary application writes while it remains a physical standby.

So:

```text
Primary:
read + write

Hot standby:
read only
```

until promotion.

PostgreSQL distinguishes warm standbys from hot standbys specifically on whether read-only client queries can be served.

## Read scaling

Suppose the workload is:

```text
10,000 writes/sec
100,000 reads/sec
```

A topology could be:

```text
                     Primary
                    writes
                   /   |   \
                  /    |    \
                 v     v     v
             Standby Standby Standby
               reads   reads   reads
```

This can distribute some read load.

But there are limits.

Adding more standbys does not automatically increase write capacity because writes still flow through the primary.

Primary–standby replication is therefore often good for:

```text
read scaling
```

but not equivalent to:

```text
write sharding
```

## Replica queries can compete with WAL replay

A hot standby has two workloads:

```text
application queries

and

WAL replay
```

Both use:

```text
CPU
memory
disk I/O
cache
```

A very expensive reporting query can therefore compete with replication.

If replay slows down:

```text
replay_lsn falls further behind
```

and stale-read lag grows.

A read replica is not unlimited free compute.

## Recovery conflicts on a hot standby

There is another complication.

Suppose the primary runs:

```text
VACUUM
```

and removes row versions that are no longer required on the primary.

Meanwhile, a long-running query on the standby still wants a snapshot involving those versions.

The standby must reconcile:

```text
continue replaying primary WAL
```

with:

```text
allow this old standby query to keep running
```

PostgreSQL can eventually cancel standby queries when necessary to allow recovery to continue.

This is why long-running analytical workloads require deliberate standby configuration rather than assuming replicas behave like independent databases.

## `hot_standby_feedback`

One option is:

```conf
hot_standby_feedback = on
```

The standby sends information upstream about snapshots that its queries still need.

That can reduce query cancellations caused by cleanup on the primary.

But there is a cost.

The primary may have to retain dead row versions for longer:

```text
standby needs old row versions
        |
feedback to primary
        |
VACUUM cannot remove them yet
        |
possible primary table bloat
```

PostgreSQL explicitly warns that `hot_standby_feedback` can reduce cleanup-conflict cancellations but can cause bloat on the primary.

So it should not be summarized as:

```text
"turn this on to stop replica queries causing bloat"
```

The trade-off is essentially the reverse.

## Synchronous replication changes the commit point

Suppose losing an acknowledged order is unacceptable.

We may require that a standby confirm the transaction before the primary returns:

```text
SUCCESS
```

Now:

```text
Client             Primary               Standby
   |                  |                     |
   |---- write ------>|                     |
   |                  |                     |
   |                  |----- WAL ---------->|
   |                  |                     |
   |                  |<---- ACK -----------|
   |                  |                     |
   |<---- SUCCESS ----|                     |
```

This is synchronous replication.

The application now pays additional commit latency in exchange for a stronger cross-node guarantee.

## PostgreSQL synchronous replication requires two concepts

A common configuration error is to change only:

```conf
synchronous_commit = remote_apply
```

and assume a standby is now synchronous.

That is incomplete.

PostgreSQL must also know which standby or standbys count as synchronous through:

```conf
synchronous_standby_names
```

For example:

```conf
synchronous_standby_names = 'standby1'
```

with:

```conf
synchronous_commit = on
```

causes transactions to wait for the selected synchronous standby's durable WAL acknowledgement.

PostgreSQL's documentation explicitly states that synchronous replication requires a non-empty `synchronous_standby_names`; `synchronous_commit` then determines the acknowledgement point.

## `synchronous_commit` levels

For a configured synchronous standby, the important levels include:

| Setting | Primary waits for |
|---|---|
| `remote_write` | Standby writes WAL to its operating system |
| `on` | Standby flushes WAL durably |
| `remote_apply` | Standby replays the transaction |
| `local` | Only local primary WAL flush; does not wait for synchronous standby |
| `off` | Even local commit acknowledgement can precede WAL flush |

The most important distinction is:

```text
on
```

versus:

```text
remote_apply
```

With `on`:

```text
standby has transaction durably in WAL
```

but a read on the standby may still not see it yet.

With `remote_apply`:

```text
standby has replayed the transaction
```

so it has become visible to queries there.

PostgreSQL documents this distinction explicitly.

## Durability and read visibility are different

Suppose:

```text
flush_lsn  = 0/5000
replay_lsn = 0/4800
```

The standby has safely persisted WAL through:

```text
0/5000
```

but queries currently reflect replay only through:

```text
0/4800
```

A transaction at:

```text
0/4900
```

may therefore already be protected against certain failures while still being invisible to standby readers.

This is why:

```text
synchronous
```

does not automatically mean:

```text
all replica reads are current
```

unless the chosen acknowledgement policy specifically waits for apply/replay.

## `remote_apply` and immediate standby reads

Consider:

```text
COMMIT order 104
```

with:

```conf
synchronous_commit = remote_apply
```

and a suitable synchronous standby configured.

The primary waits until the synchronous standby reports that the commit record has been replayed.

Now, after the commit returns:

```text
query synchronous standby
→ order 104 can be visible
```

PostgreSQL describes `remote_apply` as waiting for replay specifically so committed changes are visible to standby queries.

The cost is higher transaction latency.

## Multiple synchronous standbys

Suppose:

```text
Primary

Standby A
Standby B
Standby C
```

PostgreSQL can use priority-based synchronization.

For example:

```conf
synchronous_standby_names = 'FIRST 2 (a, b, c)'
```

meaning:

```text
wait for two highest-priority available synchronous candidates
```

Or quorum-style synchronization:

```conf
synchronous_standby_names = 'ANY 2 (a, b, c)'
```

meaning:

```text
wait for any two of those standbys
```

PostgreSQL supports both `FIRST` and `ANY` selection methods.

## Synchronous replication introduces an availability dependency

Suppose commits require one synchronous standby.

Then:

```text
Primary ----X---- Synchronous standby
```

If the standby becomes unavailable, transactions requiring its acknowledgement may stop completing until the synchronous configuration changes or another qualifying standby takes its role.

So synchronous replication trades:

```text
better durability
```

for more:

```text
coordination
latency
availability dependency
```

This is not a defect.

It is the distributed-systems trade-off being explicitly chosen.

## Geographic synchronous replication

Suppose the primary is in:

```text
Frankfurt
```

and the required synchronous standby is in:

```text
Sydney
```

A transaction now places long-distance network communication on the commit path.

Even if everything is healthy:

```text
Frankfurt
   |
   | WAL
   v
Sydney
   |
   | acknowledgement
   v
Frankfurt
```

the speed of the network contributes directly to commit latency.

This is why many architectures use:

```text
nearby synchronous standby
+
remote asynchronous disaster-recovery standby
```

rather than making every distant copy synchronous.

## Creating a standby: why a base backup is required

A standby needs a consistent starting database state.

Suppose the primary already contains:

```text
500 GB
```

of data.

The standby cannot simply begin receiving the next WAL record from an empty directory.

It first needs:

```text
consistent database copy
+
correct point in WAL history
```

A PostgreSQL base backup provides that starting point.

`pg_basebackup` is specifically designed to produce a base backup usable for streaming-replication standbys.

## Why arbitrary filesystem copies are dangerous

Suppose a PostgreSQL cluster is running while someone copies:

```text
relation file A at 12:00:00

relation file B at 12:00:10

control information at 12:00:20
```

Transactions can occur between those times.

The copied files may therefore not correspond to one recoverable database state unless the correct PostgreSQL backup protocol is being followed.

Do not bootstrap a physical standby using an arbitrary live filesystem copy.

Use:

```text
pg_basebackup
```

or another supported PostgreSQL backup mechanism.

## `pg_basebackup -R`

A convenient initialization command looks conceptually like:

```bash
pg_basebackup \
  --host=primary.example.internal \
  --username=replicator \
  --pgdata="$PGDATA" \
  --wal-method=stream \
  --write-recovery-conf \
  --progress
```

`--write-recovery-conf`, or:

```text
-R
```

creates:

```text
standby.signal
```

and writes the required connection settings into:

```text
postgresql.auto.conf
```

for the resulting standby.

This is preferable to treating `standby. signal` and `primary_conninfo` as unrelated manual steps unless manual control is actually required.

## Do not hard-code example passwords into production configuration

The source example embeds a replication password directly into:

```text
primary_conninfo
```

and uses a literal password in the notes.

That may be acceptable for a throwaway lab, but it is poor production documentation.

Prefer an appropriate secret-management mechanism, such as:

```text
a protected PostgreSQL password file
secret injection
OS credential management
platform secret manager
```

and restrict permissions appropriately.

For authentication, modern PostgreSQL supports:

```text
scram-sha-256
```

in `pg_hba. conf`. Current PostgreSQL documentation distinguishes SCRAM from the older `md5` authentication method.

## A clearer primary configuration

A minimal conceptual primary configuration might include:

```conf
wal_level = replica

max_wal_senders = 10
max_replication_slots = 10

listen_addresses = '...'
```

with replication authentication in:

```text
pg_hba.conf
```

for example conceptually:

```conf
hostssl replication replicator <standby-network> scram-sha-256
```

The actual:

```text
network
TLS policy
certificate policy
addresses
authentication
```

must match the deployment.

Do not copy example CIDRs and credentials blindly.

## `wal_keep_size` is not the same thing as `min_wal_size` or `max_wal_size`

The source suggests that newer PostgreSQL versions allow:

```text
min_wal_size / max_wal_size
```

instead of:

```text
wal_keep_size
```

That is incorrect.

They control different things.

### `wal_keep_size`

Keeps a minimum recent amount of WAL available for standbys.

### `min_wal_size` / `max_wal_size`

Primarily participate in checkpoint/WAL-recycling behavior.

PostgreSQL explicitly documents `wal_keep_size` as independent of `max_wal_size`.

So they should not be presented as substitute parameters.

## Replication slots

A physical replication slot tells PostgreSQL that a consumer may still require older WAL.

Conceptually:

```text
Current primary LSN
            |
            v
-------------------------------------->

             ^
             |
        standby still
        needs WAL from here

slot.restart_lsn
```

PostgreSQL therefore avoids automatically removing WAL that may still be required by that slot, subject to configured retention limits.

A slot is very useful for disconnected or slow standbys.

But it introduces a major operational risk.

## The replication-slot disk-fill problem

Suppose:

```text
Primary generates:
50 GB WAL/hour
```

Standby goes offline.

Its physical slot remains.

After:

```text
10 hours
```

the slot might require hundreds of gigabytes of old WAL.

Conceptually:

```text
standby stopped consuming
        |
slot cannot advance
        |
old WAL retained
        |
pg_wal grows
        |
primary disk fills
```

That can become a primary outage.

PostgreSQL explicitly warns that a slow or failed replication-slot consumer can cause WAL accumulation.

## `max_slot_wal_keep_size`

PostgreSQL provides:

```conf
max_slot_wal_keep_size
```

to place a limit on how far behind a replication slot may force WAL retention.

Without a limit, a slot can potentially retain very large amounts of WAL.

With a finite limit, the trade-off changes:

```text
protect primary disk
```

but a sufficiently stale standby may lose the WAL it needs and require rebuilding.

PostgreSQL documents the default as unlimited retention and exposes slot WAL status through `pg_replication_slots`.

## A slot does not mean "the standby has replayed everything"

This distinction matters.

A physical replication slot primarily protects WAL that the consumer may still require.

Meanwhile, PostgreSQL separately tracks:

```text
write position
flush position
replay position
```

through streaming status updates.

So do not interpret:

```text
slot advanced
```

as:

```text
every query on the standby sees all those changes.
```

Receive/durability progress and replay/visibility progress are different things.

## Monitoring on the primary

A useful starting query is:

```sql
SELECT
    application_name,
    client_addr,
    state,
    sync_state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    write_lag,
    flush_lag,
    replay_lag
FROM pg_stat_replication;
```

This gives a much richer picture than checking only:

```text
state = streaming
```

For example:

```text
sent_lsn   far ahead of write_lsn
```

suggests one category of delay.

Whereas:

```text
flush_lsn close to primary
replay_lsn much further behind
```

suggests replay/application lag.

PostgreSQL exposes separate write, flush, and replay positions and lag metrics specifically because those stages are different.

## Monitoring on the standby

Useful functions include positions such as:

```sql
SELECT
    pg_last_wal_receive_lsn(),
    pg_last_wal_replay_lsn();
```

Conceptually:

```text
received LSN
    |
    | gap = WAL waiting to be replayed
    v
replay LSN
```

If that gap grows continuously, the standby may be unable to replay WAL as fast as the primary produces it.

Monitoring should focus on trends rather than merely whether the replication process exists.

## Functional replication tests

A simple test is useful:

On the primary:

```sql
CREATE TABLE replication_test (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    data text NOT NULL
);

INSERT INTO replication_test(data)
VALUES ('hello standby');
```

Then on the standby:

```sql
SELECT *
FROM replication_test;
```

Eventually the row should appear.

But in an asynchronous topology, documentation should not promise:

```text
"almost instantly"
```

as a correctness guarantee.

It may normally happen quickly, but lag depends on:

```text
network
WAL generation
standby storage
CPU
replay workload
query conflicts
```

## Asynchronous failover and data loss

Suppose:

```text
T1 commits on primary.

Primary tells application:
SUCCESS.

T1 has not yet reached standby.

Primary suffers unrecoverable failure.

Standby promoted.
```

The new primary may not contain T1.

This is not database corruption.

It is the durability model that asynchronous replication permits.

The amount of acknowledged data that can be lost in such a failure relates to the system's:

```text
RPO — Recovery Point Objective
```

If the business requirement is:

```text
RPO = 0
```

the replication and failover design must explicitly support that requirement.

## Failover has several steps

Safe failover is more than:

```bash
pg_ctl promote
```

A complete procedure includes something like:

```text
1. Detect that the old primary is unavailable.

2. Decide that failover is appropriate.

3. Fence the old primary.

4. Choose the best standby.

5. Promote it.

6. Redirect application connections.

7. Confirm service health.

8. Rebuild redundancy.

9. Rejoin or rebuild the old primary.
```

Each step solves a different problem.

## Promotion

Current PostgreSQL supports promotion with:

```bash
pg_ctl promote
```

or SQL:

```sql
SELECT pg_promote();
```

Promotion ends standby recovery and turns the server into a normal read/write primary.

Do not base current operational documentation on manually creating an undocumented:

```text
promote.signal
```

file.

Use the supported promotion interfaces.

## Split brain

The most dangerous failover failure is:

```text
Old primary                     New primary
still accepting writes          promoted standby
```

Applications may send:

```text
write X → old primary

write Y → new primary
```

Now there are two divergent histories.

This is split brain.

PostgreSQL's failover documentation explicitly warns that after promotion there must be a mechanism ensuring the old primary learns it is no longer primary; otherwise both systems can believe they own the primary role, leading to data loss.

## Fencing

Safe HA requires making sure the losing node can no longer process authoritative writes.

This is often called:

```text
fencing
```

or, in older cluster terminology:

```text
STONITH
```

Possible mechanisms include:

```text
power fencing
cloud-instance fencing
network isolation
storage fencing
cluster-manager leases
```

The exact mechanism depends on infrastructure.

The essential property is:

> Before the new writer is trusted, the old writer must no longer be capable of creating a competing authoritative history.

## Application redirection

Promotion does not automatically teach every application:

```text
the writer moved from Node 1 to Node 2
```

The architecture needs a routing mechanism such as:

```text
proxy
virtual IP
service discovery
DNS
HA endpoint
connection-pool integration
```

For example:

```text
Before:

db-primary.internal → Node 1

After:

db-primary.internal → Node 2
```

This routing layer is part of the HA system even though it is not PostgreSQL replication itself.

## Planned switchover versus unplanned failover

These terms are useful to separate.

### Switchover

Planned role change:

```text
old primary healthy
standby caught up
traffic controlled
roles exchanged deliberately
```

This can often be done with minimal uncertainty.

### Failover

Triggered by an unexpected primary failure:

```text
primary unreachable
its exact final state may be uncertain
```

Failover requires much stronger failure-detection and fencing logic.

A tested switchover procedure does not automatically prove that unexpected failover is safe.

## What happens to the old primary?

Suppose:

```text
Node 1 = old primary
Node 2 = promoted new primary
```

After promotion, Node 2 begins creating WAL on a new timeline.

Node 1's previous history and Node 2's new history have diverged.

The old primary cannot simply restart and resume behaving as primary.

It must be converted into a standby following Node 2.

## `pg_rewind`

A full new base backup is one option.

But PostgreSQL also provides:

```text
pg_rewind
```

for suitable failover situations.

`pg_rewind` compares the diverged cluster histories and copies the changes needed to make the old primary usable as a follower of the new primary.

PostgreSQL explicitly describes bringing an old primary back after failover as a typical `pg_rewind` use case.

So this source recommendation:

```text
wipe old primary and always take a complete new base backup
```

is unnecessarily absolute.

Sometimes a new base backup is necessary.

Sometimes `pg_rewind` is substantially faster.

## Replication timelines

Promotion creates a new PostgreSQL timeline.

Conceptually:

```text
Timeline 1:

-----------------------------X
                              \
                               \
Timeline 2:                     +----------------->
                                 new primary
```

The timeline records that the database history forked.

This is essential because after failover there may be WAL from:

```text
old primary history
```

and:

```text
new primary history
```

and PostgreSQL must distinguish them.

For HA standbys, PostgreSQL recommends following the latest recovery timeline so downstream standbys can follow a promoted server.

## Cascading replication

Standbys do not always have to connect directly to the primary.

You can have:

```text
Primary
   |
   v
Standby A
   |
   +------> Standby B
   |
   +------> Standby C
```

This is cascading replication.

Potential benefit:

```text
reduce primary network fan-out
```

Potential cost:

```text
B and C depend on A
```

and gain an additional replication hop.

Also note that PostgreSQL's synchronous-standby selection on a primary concerns directly connected standbys rather than arbitrary downstream cascading standbys.

## Replication is not backup

Suppose the application accidentally executes:

```sql
DELETE FROM orders;
```

The primary generates WAL describing the deletions.

The standbys faithfully replay that WAL.

Soon:

```text
Primary:
orders gone

Standby 1:
orders gone

Standby 2:
orders gone
```

Replication worked correctly.

It did not protect the historical data.

You still need:

```text
base backups
WAL archiving
point-in-time recovery
restore testing
```

for historical recovery.

## WAL archiving and streaming replication solve different problems

Streaming replication sends WAL to currently connected standbys.

WAL archiving retains WAL in an archive for recovery purposes.

A robust system can use both:

```text
Primary
   |
   +------ streaming ------> HA standby
   |
   +------ WAL archive ----> durable archive storage
```

The standby supports:

```text
fast failover
```

The archive supports:

```text
point-in-time recovery
recovery from older backup
additional disaster-recovery workflows
```

These mechanisms complement rather than replace each other.

## `archive_mode` is not merely a replication performance tweak

Settings such as:

```conf
archive_mode = on
```

and:

```conf
archive_command = ...
```

belong to a deliberate continuous-archiving/PITR design.

They should not be presented simply as:

```text
extra hardening for replicas
```

The archive must be:

```text
durable
monitored
restorable
capacity-managed
```

and its retention must align with base-backup strategy.

PostgreSQL recommends an archive accessible independently of the primary when using WAL archives for standby/recovery purposes.

## Clock synchronization

Accurate clocks are strongly recommended in distributed infrastructure for:

```text
logs
metrics
certificate validity
monitoring
incident reconstruction
time-based features
```

But this source statement:

```text
"replication breaks if clocks drift"
```

is too strong.

Basic WAL streaming is based on WAL positions, not on synchronized wall clocks.

Some time-sensitive PostgreSQL features do depend on clocks.

For example, `recovery_min_apply_delay` compares primary commit timestamps with standby time, and PostgreSQL notes that unsynchronized clocks can affect that delay calculation.

So the accurate guidance is:

> Synchronize clocks operationally, but do not teach clock synchronization as a fundamental prerequisite for basic physical streaming replication.

## Avoid generic Linux tuning prescriptions

Advice such as:

```text
vm.swappiness = 1

kernel.shmmax >= shared_buffers
```

should not be presented as universal prerequisites for PostgreSQL replication.

Kernel and memory tuning depends on:

```text
Linux distribution
PostgreSQL version
memory size
workload
storage
containerization
huge pages
deployment platform
```

Replication works because the PostgreSQL replication configuration is correct—not because a generic sysctl recipe was copied.

Tune only from measured workload requirements and current platform documentation.

## `checkpoint_timeout` is not a standby catch-up setting

The source recommends:

```conf
checkpoint_timeout = 15min
```

with an explanation implying this helps replicas catch up.

That is misleading.

`checkpoint_timeout` controls checkpoint timing.

Checkpoint configuration affects:

```text
WAL volume
I/O behavior
crash-recovery work
checkpoint frequency
```

It is not a direct:

```text
"make replica catch up"
```

parameter.

Replica catch-up depends on:

```text
WAL generation
network throughput
standby WAL write/flush throughput
replay speed
standby workload
```

Do not tune checkpoint behavior primarily from a replication slogan.

## `backup_label` is not a tuning parameter

Likewise:

```text
backup_label
```

should not appear in a table of configuration settings beside:

```text
checkpoint_timeout
archive_mode
hot_standby_feedback
```

`backup_label` is part of PostgreSQL backup/recovery machinery, not a setting you normally "enable" for replication hardening.

Point-in-time recovery uses:

```text
base backup
WAL archive
recovery target configuration
```

as a complete recovery design.

## Corrected PostgreSQL lab topology

For a teaching environment:

```text
Primary:
db1.example.internal

Standby 1:
db2.example.internal

Standby 2:
db3.example.internal
```

Avoid hard-coding production documentation around:

```text
10.0.0.10
10.0.0.11
10.0.0.12
```

unless those addresses actually belong to the lab.

The logical topology is what matters:

```text
                     db1
                  PRIMARY
                  /      \
                 /        \
              WAL          WAL
               v            v
             db2            db3
          HOT STANDBY    HOT STANDBY
```

## Step 1 — create a replication role

On the primary:

```sql
CREATE ROLE replicator
WITH LOGIN REPLICATION
PASSWORD '<managed-secret>';
```

For a real deployment, store and deliver the secret securely rather than publishing a reusable password in documentation.

## Step 2 — permit replication connections

Example conceptually:

```conf
# pg_hba.conf

hostssl replication replicator <standby-1-address>/32 scram-sha-256
hostssl replication replicator <standby-2-address>/32 scram-sha-256
```

The exact authentication policy should follow the environment's security model.

After changing `pg_hba. conf`, reload PostgreSQL as appropriate.

## Step 3 — primary replication parameters

For example:

```conf
wal_level = replica

max_wal_senders = 10

max_replication_slots = 10
```

If physical slots will be used, create one per standby:

```sql
SELECT pg_create_physical_replication_slot('standby1');
SELECT pg_create_physical_replication_slot('standby2');
```

Then monitor them.

A slot is not a "set it and forget it" feature.

## Step 4 — initialize each standby

Stop PostgreSQL on the target standby and ensure its target data directory is suitable for replacement.

Then run `pg_basebackup`, for example:

```bash
pg_basebackup \
  --host=db1.example.internal \
  --username=replicator \
  --pgdata="$PGDATA" \
  --wal-method=stream \
  --write-recovery-conf \
  --progress
```

If you want `pg_basebackup` itself to use a named slot, configure the relevant slot option as appropriate for the deployment.

`-R`/`--write-recovery-conf` creates `standby. signal` and writes connection settings into `postgresql. auto. conf`.

## Step 5 — configure slot identity if used

For Standby 1:

```conf
primary_slot_name = 'standby1'
```

For Standby 2:

```conf
primary_slot_name = 'standby2'
```

Each independent physical standby should normally have its own slot if slots are being used.

Otherwise multiple consumers would not independently preserve their own required WAL positions.

## Step 6 — start the standby

Start PostgreSQL.

The standby:

```text
recognizes standby.signal

connects using primary_conninfo

starts WAL recovery

starts streaming when possible
```

The primary should then show a corresponding connection in:

```sql
SELECT *
FROM pg_stat_replication;
```

## Step 7 — verify the pipeline, not only connectivity

Check:

```sql
SELECT
    application_name,
    client_addr,
    state,
    sync_state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn
FROM pg_stat_replication;
```

You want to understand:

```text
Is WAL being sent?

Is the standby writing it?

Is it flushing it?

Is it replaying it?
```

A connection marked:

```text
streaming
```

is good, but it is only one part of replication health.

## Configuring synchronous replication correctly

Suppose `standby1` uses:

```text
application_name=standby1
```

in its connection information.

The primary could use:

```conf
synchronous_standby_names = 'FIRST 1 (standby1, standby2)'
```

and:

```conf
synchronous_commit = on
```

Now commits requiring the default synchronous behavior wait for durable acknowledgement from the chosen synchronous standby.

If the application specifically requires standby read visibility before commit returns:

```conf
synchronous_commit = remote_apply
```

may be appropriate.

The important point is that:

```text
synchronous_standby_names
```

selects the participating standby set, while:

```text
synchronous_commit
```

controls the wait level.

## Monitoring table

| Question | PostgreSQL signal |
|---|---|
| Is standby connected? | `pg_stat_replication. state` |
| Is it synchronous? | `sync_state` |
| How far has primary sent? | `sent_lsn` |
| How far has standby written? | `write_lsn` |
| How far has standby flushed? | `flush_lsn` |
| How far has standby applied? | `replay_lsn` |
| How much WAL does a slot retain? | `pg_replication_slots. restart_lsn`, `wal_status`, `safe_wal_size` |
| Are standby queries being canceled? | `pg_stat_database_conflicts` on standby |
| Is receiver active? | `pg_stat_wal_receiver` on standby |

This is far more useful operationally than a single:

```text
replication = yes/no
```

indicator.

## Failover procedure summary

A manual emergency sequence is conceptually:

```text
1. Confirm old primary is not allowed to keep serving writes.

2. Choose the intended standby.

3. Check its replication/recovery state.

4. Promote:
      pg_ctl promote
   or:
      SELECT pg_promote();

5. Confirm it accepts writes.

6. Redirect applications.

7. Re-establish remaining standbys.

8. Rewind or rebuild the old primary.

9. Restore HA redundancy.
```

The exact automation belongs to an HA manager rather than ad hoc shell commands.

## What PostgreSQL alone does and does not provide

PostgreSQL provides:

```text
WAL generation
streaming replication
hot standby
replication slots
synchronous replication
promotion
timelines
pg_rewind
monitoring views
```

PostgreSQL by itself does not provide the complete external system for:

```text
failure detection
quorum-based primary ownership
fencing
virtual-IP movement
application endpoint failover
cluster orchestration
```

PostgreSQL's own failover documentation explicitly says external system software is required for primary failure detection and notification.

Tools and platforms can provide that orchestration layer.

## Primary–standby across technologies

The same architecture appears under different names.

| Technology | Writer role | Follower role | Change mechanism | Stronger acknowledgement |
|---|---|---|---|---|
| PostgreSQL physical replication | Primary | Standby | WAL streaming/replay | Synchronous standby |
| MySQL | Source/primary | Replica | Binary log / relay log | Semisynchronous replication |
| SQL Server Availability Groups | Primary replica | Secondary replica | Transaction-log transport/redo | Synchronous commit |
| MongoDB replica set | Primary | Secondary | Oplog replication | Configurable write concern |

The concepts recur:

```text
one current writer

replicated change stream

followers apply it

optional stronger acknowledgement

promotion/election after failure
```

but the exact correctness and failover semantics differ by engine.

## Advantages and limitations

| Benefit | Important qualification |
|---|---|
| High availability | Requires safe failover orchestration and fencing |
| Lower RTO | Only if standby is healthy and sufficiently caught up |
| Read scaling | Reads may be stale and can compete with replay |
| Better durability | Depends on asynchronous vs synchronous acknowledgement |
| Maintenance flexibility | Depends on topology and failover procedure |
| Geographic copy | Network latency and replication lag matter |
| Simple write ownership | Primary can become a write bottleneck |

The source correctly identifies read offloading, failover, and write-primary bottlenecks as central characteristics of the topology.

## Common misconceptions

| Claim | Correct interpretation |
|---|---|
| "We have a standby, therefore no data can be lost. " | Async replication can leave an acknowledged-write loss window |
| "Synchronous means the standby query sees the write. " | Only if acknowledgement waits through replay, such as `remote_apply` |
| "A replication slot means the standby is current. " | It manages WAL retention; replay position is separate |
| "`wal_keep_size` is replaced by `max_wal_size`. " | They control different things |
| "Clock drift breaks basic streaming replication. " | WAL positions drive basic streaming; clocks matter for specific time-based behavior and operations |
| "`hot_standby_feedback` prevents primary bloat. " | It can prevent standby cleanup conflicts by allowing more primary bloat |
| "Promotion solves failover. " | Promotion is only one step; fencing and routing are also required |
| "Old primary must always be wiped. " | A new base backup may be needed, but `pg_rewind` can often rejoin a diverged former primary |
| "Replication is backup. " | Logical mistakes replicate too |
| "More standbys increase write throughput. " | They mainly add redundancy/read capacity in a single-primary design |

## Final mental model

Do not memorize primary–standby replication as:

```text
Primary copies database to standby.
```

Use this model:

```text
APPLICATION WRITE
       |
       v
     PRIMARY
       |
       v
generate WAL
       |
       v
local durability
       |
       +-----------------------------+
       |                             |
       | streaming                   |
       v                             |
    STANDBY                          |
       |                             |
     receive                         |
       |                             |
      write                          |
       |                             |
      flush                          |
       |                             |
     replay                          |
       |                             |
       v                             |
read-visible state                   |
                                     |
          <--- commit policy decides
               where SUCCESS occurs
```

Then ask five questions.

### Where does `COMMIT SUCCESS` occur?

```text
after primary only?

after standby write?

after standby flush?

after standby replay?
```

### Where are reads served?

```text
primary?

standby?

both?
```

### How stale may standby reads be?

```text
milliseconds?

seconds?

not stale at all?
```

### What happens when the primary disappears?

```text
who detects it?

who chooses the new primary?

who fences the old one?

who redirects clients?
```

### How do we recover historical data?

```text
standby?
No.

backup + WAL archive + PITR.
```

If those questions have clear answers, the replication architecture is understandable.

If the only documentation says:

```text
"we have two replicas"
```

you still know very little about its actual availability and durability guarantees.

## References

The source notes provide the original primary/standby architecture, PostgreSQL streaming-replication example, base-backup setup, replication-status check, manual promotion, replication-slot discussion, and HA tuning suggestions.

Current PostgreSQL high-availability documentation describes physical WAL streaming, hot standbys, synchronous replication, cascading replication, standby setup, and the distinction between synchronous write/flush/apply acknowledgement.

Current `pg_basebackup` documentation describes base backups for standby initialization and `-R`/`--write-recovery-conf`, which creates `standby. signal` and writes connection information to `postgresql. auto. conf`.

Current PostgreSQL monitoring documentation distinguishes `sent_lsn`, `write_lsn`, `flush_lsn`, and `replay_lsn`, allowing receive/durability lag to be distinguished from replay lag.

PostgreSQL's replication-slot documentation describes `restart_lsn` as the oldest WAL still potentially required by the consumer and documents the risk/limits associated with retained WAL.

PostgreSQL's failover and `pg_rewind` documentation describes the need to prevent the old primary from continuing as a writer and explains how a diverged former primary can often be rewound and reused as a standby after failover.
