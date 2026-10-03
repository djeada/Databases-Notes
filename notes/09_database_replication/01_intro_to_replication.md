# Replication: Maintaining Copies of Database Changes

Replication keeps database data on more than one node by transferring changes from one database instance to another.

A common topology is:

```text
             writes
Application ---------> Primary
                         |
                         | replication stream
                         v
                      Replica 1
                         |
                         +--------> Replica 2
```

The copies are related, but this does not mean they are identical at every instant.

A replica may be:

```text
milliseconds behind
seconds behind
minutes behind
completely disconnected
```

while the primary continues accepting transactions.

This immediately creates the central question in replication:

> When the database tells the client that `COMMIT` succeeded, how much of that transaction has reached the other copies?

That question determines:

```text
durability after primary failure
replication lag
read consistency
failover data loss
write latency
```

## Why replicate a database?

A single database server creates a simple failure mode:

```text
                 ┌───────────────┐
Application ---> │ Database      │
                 │ only copy     │
                 └───────────────┘
                         X
```

If that server becomes unavailable, the application may become unavailable too.

Replication introduces additional copies:

```text
                    Primary
                   /       \
                  /         \
             Replica 1    Replica 2
```

Those copies can serve different purposes.

| Goal | How replication can help |
|---|---|
| High availability | Promote another node when the primary fails |
| Disaster recovery | Maintain a copy in another location |
| Read scaling | Send reporting/read traffic to replicas |
| Backup offloading | Run some backup work on secondary systems |
| Analytics | Feed another database or analytical system |
| Geographic reads | Place readable copies closer to users |
| Upgrade/migration | Logical replication can move data between environments |

But replication is not automatically all of these things.

For example:

```text
a reporting replica
```

and:

```text
a failover replica
```

may have very different requirements.

## A concrete example: create order 104

Suppose an application creates:

```text
order_id = 104
customer_id = 27
amount = €89
```

The application sends:

```sql
BEGIN;

INSERT INTO orders(order_id, customer_id, amount)
VALUES (104, 27, 89);

COMMIT;
```

Assume a primary and one replica.

In asynchronous replication, the timeline might be:

```text
Primary                         Replica

INSERT order 104

COMMIT
   |
   +---- durable locally

return "success"
to application

        replication data ---------->

                                receive change

                                persist/log change

                                apply change

                                order 104 becomes
                                visible to queries
```

The key observation is:

```text
client hears SUCCESS
```

before:

```text
replica can necessarily return order 104
```

That interval is replication lag.

## Replication usually transfers a change stream, not repeated full database copies

A naive replication design might sound like:

```text
database changed
→ copy entire database again
```

That would obviously be far too expensive.

Instead, database systems normally maintain a stream describing changes.

Examples include:

```text
PostgreSQL
    WAL — Write-Ahead Log

MySQL
    binary log

SQL Server Availability Groups
    transaction log records
```

Conceptually:

```text
Database state

        +
        |
        v

ordered change stream

change 101
change 102
change 103
change 104
...
```

The replica starts from some known database state and then follows that change stream.

## PostgreSQL example: WAL streaming

PostgreSQL physical streaming replication transfers WAL records.

The primary generates WAL as transactions modify the database.

A standby connects to the primary and streams WAL records as they are generated:

```text
PostgreSQL primary

database changes
       |
       v
      WAL
       |
       |  walsender
       v
================ network ================
       |
       |  walreceiver
       v
PostgreSQL standby

receive WAL
    |
write/flush WAL
    |
replay WAL
    |
updated standby database
```

PostgreSQL documents that streaming replication sends WAL records incrementally rather than waiting for a whole WAL segment to fill, and that streaming replication is asynchronous by default.

This is a good example of an important pattern:

> Replication often means shipping the database's recovery/change log to another machine and replaying it there.

## The most important replication pipeline

A useful generic model is:

```text
PRIMARY

transaction
    |
    v
commit/change log
    |
    v
SEND
    |
    |
    | network
    v

REPLICA

RECEIVE
    |
    v
PERSIST / HARDEN
    |
    v
APPLY / REPLAY
    |
    v
VISIBLE TO READERS
```

These are not interchangeable milestones.

The replica can have received a transaction without having applied it.

It can have persisted the transaction to its own log without having made the changed rows visible to queries.

That distinction explains a large fraction of replication behavior.

## Receive, persist, apply, and visibility

Consider order `104`.

### Stage 1 — Receive

The replica has obtained the replication message:

```text
Replica memory/network buffers:

"insert order 104"
```

This says little about crash durability.

The data may not yet be safely stored.

### Stage 2 — Persist / harden

The replica has recorded the change in durable or recovery storage according to the engine's durability rules.

Conceptually:

```text
Replica disk:

replication log contains order 104
```

If the replica process restarts, it may be able to recover the transaction from that log.

### Stage 3 — Apply / replay

The replica's apply mechanism has executed or replayed the change against the database state:

```text
orders table now contains order 104
```

### Stage 4 — Visible to a read

The database's consistency rules allow a query to observe the applied transaction:

```sql
SELECT *
FROM orders
WHERE order_id = 104;
```

returns the row.

The important principle is:

> Persisted on a replica is not necessarily the same thing as applied on the replica.

## Why this distinction matters

Suppose:

```text
Primary transaction commits.

Replica has already persisted the change.

Replica has not applied it yet.
```

Then two different statements can simultaneously be true:

```text
The transaction is protected against loss
if the primary disappears.
```

and:

```text
A query against the replica still cannot see it.
```

This surprises people because durability and read freshness are often incorrectly treated as the same property.

They are different.

## SQL Server demonstrates this especially clearly

With SQL Server Always On Availability Groups, changes are sent from the primary to secondary replicas as transaction log records.

On the secondary:

```text
receive log records
       |
       v
harden transaction log
       |
       v
redo
       |
       v
changes visible in secondary database
```

SQL Server synchronous-commit mode waits for the synchronous secondary to harden the log before the primary completes the relevant commit protocol.

But hardening does not mean redo is finished.

Microsoft explicitly documents that a redo queue can contain log records that have already been hardened on the secondary but have not yet been applied to its database pages. Reads on that secondary can therefore still return stale data.

So:

```text
synchronous replication
```

does not automatically mean:

```text
every read on the replica immediately sees the transaction
```

## Replication lag is not one single delay

When somebody says:

```text
replica lag = 5 seconds
```

ask:

> Lag between which stages?

There can be multiple kinds of lag:

```text
primary generated
       ↓
     SEND
       ↓         ← send lag
replica received
       ↓
    PERSIST
       ↓         ← flush/harden lag
replica durable
       ↓
     APPLY
       ↓         ← replay/apply lag
replica visible
```

A replica might have excellent network throughput but slow apply performance.

Or it might apply quickly once data arrives but have a slow network.

Those are different problems.

## PostgreSQL exposes these stages directly

PostgreSQL's replication monitoring includes multiple WAL positions.

Conceptually:

```text
sent_lsn
    ↓
write_lsn
    ↓
flush_lsn
    ↓
replay_lsn
```

These correspond roughly to:

```text
sent
received/written
durably flushed
replayed
```

PostgreSQL documentation recommends comparing WAL positions to identify whether lag is primarily:

```text
primary sending slowly
network / receiver delay
or
standby replay delay
```

and notes that a large difference between received/flushed WAL and replay position means the standby is receiving WAL faster than it can replay it.

This is much more useful than treating "replica lag" as one mysterious number.

## Asynchronous replication

With asynchronous replication, the primary does not wait for the replica before acknowledging the transaction to the client.

Conceptually:

```text
Client          Primary              Replica
  |                |                    |
  |---- write ---->|                    |
  |                |                    |
  |                | COMMIT             |
  |                |                    |
  |<--- success ---|                    |
  |                |                    |
  |                |---- replicate ---->|
  |                |                    |
```

The advantage is lower commit latency.

The client does not wait for:

```text
network round trip
replica storage
replica apply
```

The cost is a failure window.

## The asynchronous data-loss window

Suppose the primary tells the client:

```text
Order 104 committed successfully.
```

but has not yet transmitted order `104` to the replica.

Then:

```text
Primary dies permanently.
```

The replica may contain only:

```text
orders 1 ... 103
```

If that replica is promoted, order `104` disappears from the surviving database state even though the application previously received success.

This is the fundamental durability tradeoff of asynchronous replication.

PostgreSQL explicitly notes that asynchronous streaming replication can lose transactions that committed on the primary but had not yet reached the standby when the primary failed.

SQL Server similarly documents possible data loss when failing over from asynchronous-commit replicas that have not caught up.

## MySQL is asynchronous by default

MySQL source-to-replica replication is asynchronous by default.

A common pipeline is:

```text
MySQL source

transaction
    |
    v
binary log
    |
    | replication connection
    v

MySQL replica

receiver / I/O thread
    |
    v
relay log
    |
    v
applier / SQL thread(s)
    |
    v
replica database
```

MySQL's documentation explicitly describes normal replication as asynchronous and supports tracking either binary-log positions or GTIDs to identify replication progress.

This pipeline again separates:

```text
received
```

from:

```text
applied
```

## Why an immediate replica read may fail

Suppose an API endpoint does:

```text
POST /orders
```

which writes order `104` to the primary.

The next browser request performs:

```text
GET /orders/104
```

but the application's load balancer sends reads to a replica.

The timing might be:

```text
Primary:
order 104 committed

Client:
POST succeeded

Replica:
still on order 103

Client:
GET /orders/104

Replica:
404 / not found
```

Nothing has necessarily malfunctioned.

The read simply arrived before replication had applied the transaction.

## This is a read-after-write consistency problem

The user expects:

```text
I just created it
therefore I should be able to read it
```

That property is commonly called read-your-writes or read-after-write consistency.

Basic asynchronous read replicas do not automatically provide it.

Several application designs are possible.

For example:

```text
write → primary
immediate confirmation read → primary
later ordinary reads → replicas
```

Another design carries a replication position/token and waits until the selected replica reaches that point.

Another design avoids the confirmation read entirely by returning the newly created object from the write operation.

The correct approach depends on how much staleness the application can tolerate.

## Different reads have different freshness requirements

Consider three queries.

### Product catalog

```text
"What products are available?"
```

Being 500 ms behind may be acceptable.

### Analytics dashboard

```text
"How many orders did we receive today?"
```

Several seconds of lag may be acceptable.

### Payment confirmation

```text
"Did my €10,000 transfer succeed?"
```

A stale read may be unacceptable.

The mistake is designing one global rule:

```text
all reads must use replicas
```

or:

```text
all reads must use primary
```

without considering the semantics of individual requests.

## Synchronous replication

Synchronous replication changes the commit rule.

Instead of:

```text
primary commits
→ tell client success
→ replicate later
```

the protocol becomes something like:

```text
primary prepares commit information
       |
       v
send to replica
       |
       v
wait for required acknowledgement
       |
       v
return success
```

The cost is latency.

The benefit is stronger durability.

But the phrase:

```text
synchronous replication
```

is incomplete unless you know:

```text
which replicas must acknowledge?

what exactly must they acknowledge?

receive?

memory write?

filesystem write?

durable flush?

application/replay?
```

## PostgreSQL makes the acknowledgement level explicit

PostgreSQL's `synchronous_commit` setting provides an excellent concrete example.

With synchronous standbys configured, PostgreSQL supports several important acknowledgement levels:

| PostgreSQL setting | Commit waits for |
|---|---|
| `remote_write` | Standby received the WAL and wrote it to its operating system |
| `on` | Standby flushed the WAL to durable storage |
| `remote_apply` | Standby replayed the transaction so it is visible to standby queries |

PostgreSQL documents those differences directly. `remote_write` is weaker than durable standby flush, `on` waits for durable storage, and `remote_apply` additionally waits for replay and visibility.

This is exactly why:

```text
receive
persist
apply
```

must be understood separately.

## PostgreSQL `remote_apply`

Suppose an application requires:

```text
COMMIT returned

therefore

a query sent to the synchronous standby
must be able to see the transaction
```

PostgreSQL can provide that stronger behavior with:

```text
synchronous_commit = remote_apply
```

The commit waits until the synchronous standby reports that the commit record has been replayed and has become visible there.

Compare that with:

```text
synchronous_commit = on
```

which waits for durable WAL on the synchronous standby but not necessarily replay.

That distinction is extremely important for applications performing synchronous replica reads.

## Synchronous replication adds network latency to commits

Consider two servers in the same datacenter:

```text
Primary ← 0.3 ms → Standby
```

The network penalty may be manageable.

Now place the synchronous standby across an ocean:

```text
Frankfurt ←────────→ Sydney
```

Every synchronous transaction may now need to incorporate a large network round trip into its commit latency.

PostgreSQL explicitly notes that synchronous replication necessarily increases response time and that the minimum extra wait includes the primary-to-standby round trip.

That produces a common architecture:

```text
nearby synchronous replica
+
distant asynchronous disaster-recovery replica
```

rather than making every geographically distant copy synchronous.

## PostgreSQL can require several replicas

Suppose:

```text
Primary
   |
   +-- Replica A
   +-- Replica B
   +-- Replica C
```

PostgreSQL can use priority-based or quorum-based synchronous replication.

For example:

```text
ANY 2 (A, B, C)
```

means the commit can wait for any two of the listed synchronous candidates rather than requiring one specific machine.

PostgreSQL's current documentation supports both `FIRST` priority-based and `ANY` quorum-style synchronous standby selection.

This illustrates another important principle:

> "Synchronous" also requires defining how many replicas constitute enough acknowledgement.

## MySQL semisynchronous replication

MySQL provides semisynchronous replication in addition to its default asynchronous replication.

Conceptually:

```text
Source
   |
   | transaction
   v
binary log
   |
   +----------> replica
                   |
                   v
                relay log
                   |
                   |
             acknowledgement
                   |
                   v
Source returns to client
```

With semisynchronous replication enabled, the source waits for the required replica acknowledgement that the transaction has been received and logged before returning according to the configured wait point.

Importantly, this is not the same as:

```text
replica has already applied the transaction
```

The replica's apply step remains separate.

## MySQL can wait for more than one replica

MySQL exposes:

```text
rpl_semi_sync_source_wait_for_replica_count
```

which controls how many replicas must acknowledge a transaction.

The default is one.

For example:

```text
wait_for_replica_count = 2
```

requires two qualifying acknowledgements while semisynchronous mode remains active.

Again, the useful question is not:

```text
"Is replication synchronous?"
```

It is:

> Which nodes participate in the commit acknowledgement rule?

## MySQL semisynchronous replication can fall back

Another operational detail matters.

MySQL's semisynchronous source has a timeout:

```text
rpl_semi_sync_source_timeout
```

If sufficient acknowledgements do not arrive within that interval, MySQL can revert to asynchronous replication depending on configuration.

Therefore an architecture review should not stop at:

```text
"semisync is enabled"
```

It should also ask:

```text
What happens if all semisynchronous replicas disappear?

Do writes stop?

Do they continue asynchronously?

What durability guarantee does the application then have?
```

## SQL Server synchronous commit

SQL Server Always On Availability Groups have:

```text
asynchronous-commit mode
```

and:

```text
synchronous-commit mode
```

In synchronous-commit mode, the primary waits for the synchronous secondary to acknowledge that the relevant transaction log records have been hardened to disk.

This protects committed transactions against loss on primary failure when the secondary is properly synchronized.

But remember the earlier pipeline:

```text
harden
   ↓
redo
   ↓
visible
```

Synchronous commit does not collapse those into one operation.

## SQL Server synchronous commit can still have stale readable secondary data

Suppose:

```text
transaction log is already hardened
```

but the secondary's redo process is overloaded.

Then:

```text
redo queue grows
```

and the transaction may not yet be reflected in queries against a readable secondary.

Microsoft explicitly documents this scenario: log records can be safely hardened yet remain unreadable until redo applies them.

This is one of the clearest examples of:

> durability lag and query-visibility lag being different concepts.

## Technology comparison: commit acknowledgement

| Technology | Default/common asynchronous behavior | Stronger acknowledgement option | What stronger acknowledgement means |
|---|---|---|---|
| PostgreSQL streaming replication | Asynchronous by default | Synchronous replication | Can wait for remote write, durable flush, or even replay depending on `synchronous_commit` |
| MySQL source/replica | Asynchronous by default | Semisynchronous replication | Source waits for configured replica receipt/log acknowledgement; apply remains separate |
| SQL Server Availability Groups | Async-commit available | Synchronous-commit | Primary waits for synchronized secondary log hardening |
| PostgreSQL `remote_apply` | — | Stronger than normal synchronous flush | Commit can wait until transaction is replayed and query-visible |

These distinctions are documented by PostgreSQL's WAL and synchronous replication configuration, MySQL's replication and semisynchronous replication documentation, and SQL Server's Availability Group availability-mode documentation.

## Starting a new replica requires a consistent starting point

A new replica cannot normally begin from:

```text
an empty database
+
whatever replication messages happen to arrive now
```

Suppose the primary already contains:

```text
orders 1 ... 10,000,000
```

and the replica begins listening at:

```text
order 10,000,001
```

The previous data is missing.

So replication setup normally requires:

```text
1. create a consistent base copy
2. record the change-stream position corresponding to that copy
3. continue replication from that position
```

This is often called:

```text
seeding
bootstrap
base backup
initial snapshot
```

depending on the technology.

## Why copying live database files casually is unsafe

Suppose a database contains:

```text
customers.dat
orders.dat
indexes.dat
```

and you manually copy them while transactions are running.

The copy process might capture:

```text
customers.dat at 10:00:01

orders.dat at 10:00:08

indexes.dat at 10:00:15
```

Those files may represent different logical moments.

You can therefore create an inconsistent database image.

Database engines provide supported backup/snapshot procedures specifically to produce a recoverable starting state.

PostgreSQL, for example, requires a suitable base backup to bootstrap a physical standby.

MySQL likewise documents taking a source snapshot before starting replication from the corresponding position.

## Replication positions

The replica needs to answer:

> How far through the source's change history have I processed?

Systems therefore maintain replication positions.

Examples include:

```text
PostgreSQL
    LSN — Log Sequence Number

MySQL
    binary-log file + position
    or
    GTID set

SQL Server
    LSN-based transaction-log positions internally
```

Conceptually:

```text
Source stream:

100 ─ 101 ─ 102 ─ 103 ─ 104 ─ 105

Replica received through: 105
Replica persisted through: 104
Replica applied through:   102
```

That is much more informative than simply saying:

```text
replication is running
```

## MySQL GTIDs

MySQL can identify transactions using Global Transaction Identifiers (GTIDs).

Instead of saying:

```text
"continue at binary log mysql-bin.008214 byte 93482"
```

a replica can reason in terms of which transactions it has already executed.

MySQL supports GTID auto-positioning so a replica can determine which transactions it still needs from the source.

This is especially useful when topology changes make one fixed log filename/offset inconvenient.

## PostgreSQL replication slots

A different problem occurs when the replica falls behind.

Suppose the primary generates WAL quickly.

Without protection, it may eventually recycle old WAL that the disconnected replica still needs.

PostgreSQL replication slots tell the primary:

```text
this consumer has not yet passed LSN X

do not discard the WAL it still requires
```

PostgreSQL documents replication slots specifically as a mechanism to retain WAL needed by standbys.

But this creates another operational risk:

```text
replica offline
       ↓
slot cannot advance
       ↓
primary retains more WAL
       ↓
disk usage grows
```

PostgreSQL explicitly warns that replication slots can retain enough WAL to fill `pg_wal` if not managed.

So solving:

```text
replica missed required history
```

can create:

```text
primary disk exhaustion
```

if monitoring is absent.

## Physical replication

Physical replication works at a level closely tied to the storage/recovery format of the database engine.

PostgreSQL physical streaming replication is the clearest example:

```text
primary WAL
    |
    v
standby WAL replay
```

The standby reconstructs the physical database state by replaying WAL.

Advantages include:

```text
very complete copy of the database cluster state
efficient failover-style replication
close integration with crash recovery
```

The tradeoff is tighter engine/version/platform coupling.

PostgreSQL notes that physical log shipping is tied closely enough to server storage formats that major PostgreSQL versions generally cannot be mixed in a normal physical primary/standby configuration.

## Logical replication

Logical replication works with logical data changes rather than reproducing the source's physical storage layout.

Conceptually:

```text
INSERT customer 7
UPDATE order 104
DELETE item 8
```

rather than:

```text
modify physical page X at byte offsets Y...
```

PostgreSQL logical replication uses a publication/subscription model and tracks rows through a replication identity, usually a primary key.

This allows much more selective replication.

For example:

```text
Database A

customers
orders
internal_audit
temporary_processing
```

might publish only:

```text
customers
orders
```

to another system.

## PostgreSQL logical replication

A PostgreSQL logical replication topology might look like:

```text
Publisher

customers
orders
payments
internal_logs

     |
     | publication:
     | customers, orders
     v

Subscriber

customers
orders
```

PostgreSQL can perform an initial table synchronization and then continually send changes made after that snapshot.

Logical replication can support scenarios such as:

```text
replicating only selected data
replicating between PostgreSQL major versions
replicating between different platforms
feeding analytical databases
```

which PostgreSQL explicitly lists among its logical-replication use cases.

## Physical versus logical replication

| Property | Physical | Logical |
|---|---|---|
| Replicates | Storage/recovery-level changes | Logical row/data changes |
| Typical use | HA standby | Selective replication, migrations, integrations |
| Scope | Usually broad database/cluster copy | Can often choose tables/rows/columns |
| Engine coupling | High | Usually lower |
| Cross-version flexibility | Limited | Often better |
| Schema handling | Physical copy naturally follows storage state | Schema compatibility must be considered |
| Example | PostgreSQL WAL streaming | PostgreSQL publications/subscriptions |

Neither is universally better.

They solve different problems.

## Logical replication does not mean "everything is copied"

Suppose the publisher adds:

```sql
ALTER TABLE customers
ADD COLUMN loyalty_level integer;
```

Do not assume every logical replication technology automatically reproduces every schema operation.

Logical replication frequently requires the target schema to be compatible with the replicated data.

Likewise:

```text
sequences
large objects
DDL
permissions
extensions
triggers
```

may have technology-specific behavior.

Therefore:

> "The tables are logically replicated"

does not imply:

> "Every database object and every schema operation is automatically synchronized. "

## Replication lag can come from several places

A replica can fall behind because:

```text
primary generates changes faster than network can send them

network is slow or congested

replica disk cannot persist logs fast enough

replica CPU cannot apply changes fast enough

long queries interfere with apply/redo

replication process is paused

replica is disconnected
```

These produce different diagnostic signatures.

For example, SQL Server explicitly distinguishes log hardening from redo: a secondary can receive and harden changes faster than redo can apply them, creating a recovery/redo queue.

PostgreSQL similarly exposes separate received/flushed/replayed WAL positions, making it possible to distinguish network/receive delay from replay delay.

## Read replicas can make themselves slower

Suppose a replica is intended for large reporting queries:

```sql
SELECT ...
FROM orders
JOIN ...
GROUP BY ...
```

Those queries consume:

```text
CPU
memory
I/O bandwidth
```

But the same replica also needs CPU and I/O to apply incoming replication changes.

So:

```text
more reporting work
        ↓
less resource available to replication apply
        ↓
replica falls further behind
        ↓
reports become even more stale
```

SQL Server explicitly documents that heavy reporting workloads on readable secondary replicas can compete with redo and increase replication latency.

This is why:

```text
"we'll move reads to replicas"
```

is not automatically free scalability.

## Failover

Failover changes which node accepts primary/write responsibility.

Before:

```text
                 Primary A
                    |
                    v
                 Replica B
```

A fails.

After failover:

```text
                 X Primary A

                 Primary B
```

This sounds simple, but several things must happen correctly:

```text
select a suitable replacement

ensure it has an acceptable data position

promote it

route application traffic to it

prevent the old primary from continuing to accept writes
```

Replication by itself does not perform all of those steps safely.

## Promotion

A replica normally behaves differently from a primary.

For example, a PostgreSQL physical standby continuously replays WAL.

Promotion tells it:

```text
stop behaving as a recovery standby

become a normal read/write primary
```

PostgreSQL supports promotion through `pg_ctl promote` or `pg_promote()`.

After promotion, applications must also know where to connect.

That may require:

```text
load balancer
proxy
VIP
DNS
cluster manager
service discovery
connection-string listener
```

depending on the platform.

## SQL Server Availability Group listener

SQL Server Availability Groups provide the concept of an availability group listener.

Applications connect to the listener rather than hard-coding the current primary machine.

After failover, the listener allows client connections to be routed toward the replica currently holding the primary role. SQL Server can also use read-only routing for appropriate read-intent connections.

This solves an important layer beyond merely copying data:

```text
"Which server should my application connect to now?"
```

## RPO: how much data can we lose?

The Recovery Point Objective (RPO) describes the tolerated data-loss window.

Suppose asynchronous replication normally lags by:

```text
2 seconds
```

If the primary dies permanently, the surviving replica may be approximately two seconds behind.

The business might therefore lose recently acknowledged transactions.

A system requirement might say:

```text
RPO = 0
```

meaning acknowledged committed transactions must not be lost under the failures covered by the design.

Another system may accept:

```text
RPO ≤ 60 seconds
```

for a low-value reporting database.

The replication architecture should follow the business requirement, not the reverse.

## RTO: how long can the system remain unavailable?

The Recovery Time Objective (RTO) concerns time rather than data:

```text
failure
   |
   v
detect failure

choose new primary

promote/recover

redirect clients

application becomes usable
   |
   v

elapsed time = recovery time
```

A company might require:

```text
RTO < 30 seconds
```

while another system might tolerate:

```text
RTO = 4 hours
```

Those lead to very different architectures.

Replication improves the potential RTO because a mostly up-to-date database already exists.

But automatic detection, promotion, routing, replay backlog, and application reconnection all affect actual recovery time.

## Replica apply lag can hurt RTO too

Suppose a failover replica has safely received large amounts of transaction log but has not replayed all of it.

The data may be durable:

```text
good RPO
```

but recovery may still need to process the backlog before the database becomes fully useful:

```text
worse RTO
```

SQL Server specifically documents that a large redo queue on a secondary can extend failover time even when those log records have already been hardened there.

Again:

```text
durability
```

and:

```text
readiness
```

are different properties.

## Split brain

One of the most dangerous failover failures is split brain.

Suppose network communication between two sites fails:

```text
Site A                 Site B

Primary A      X       Replica B
```

A can no longer see B.

B can no longer see A.

If both sides independently decide:

```text
"The other side is dead.
I should be primary."
```

you can get:

```text
Primary A             Primary B

accepts write X       accepts write Y
```

Now the system has two conflicting histories.

That is much more difficult than ordinary replica lag.

## Fencing

Safe failover therefore requires more than promotion.

The old primary must be prevented from continuing to process writes if it is no longer authoritative.

That exclusion is commonly called fencing.

Conceptually:

```text
1. Decide B will become primary.

2. Ensure A cannot continue writing.

3. Promote B.

4. Route clients to B.
```

Possible fencing mechanisms depend on the environment and can involve:

```text
cluster quorum
storage fencing
node power control
leases
STONITH-style mechanisms
cloud control planes
consensus-based ownership
```

The architectural principle is:

> Never rely solely on "we think the old primary is dead. "

You need a mechanism ensuring only the authorized writer remains active.

## SQL Server shows why quorum matters

SQL Server synchronous Availability Group automatic failover is not based only on:

```text
secondary can no longer ping primary
```

Microsoft documents additional requirements including synchronous state, configured automatic failover, WSFC quorum, and failover-policy conditions.

This is an example of a general distributed-systems principle:

> Failure detection alone is not enough to safely assign write ownership.

You also need coordination about who has authority.

## Asynchronous failover can lose acknowledged writes

Suppose:

```text
T1 committed on Primary A

Primary A told application:
SUCCESS

T1 had not reached Replica B

Primary A permanently fails

Replica B promoted
```

The new primary never contained T1.

This is why forced failover from an unsynchronized asynchronous SQL Server secondary explicitly permits data loss.

The same fundamental risk exists in asynchronous PostgreSQL and MySQL replication.

Asynchrony trades some durability guarantee for lower commit latency and increased geographic flexibility.

## Synchronous replication changes the failure tradeoff

Suppose the commit rule instead requires:

```text
Primary local durable write

AND

Replica durable write

before

SUCCESS
```

Then loss of only the primary does not lose the acknowledged transaction.

But now consider:

```text
replica unavailable
```

What should happen?

Possibilities include:

```text
stop accepting commits

wait indefinitely

wait for another synchronous replica

fall back to asynchronous operation
```

Different systems/configurations choose differently.

That is why synchronous replication also creates an availability tradeoff.

## Durability versus availability during network partitions

Consider:

```text
Primary A --------X-------- Synchronous replica B
```

The network link fails.

A now has to choose between two desirable properties:

```text
keep accepting writes
```

and:

```text
guarantee every acknowledged write exists on B
```

It cannot do both using B while communication is impossible.

A strict design may stop commits.

A looser design may continue asynchronously.

The important point is:

> Replication configuration is partly a business decision about what to sacrifice during failures: latency, availability, or risk of data loss.

## Replication is not backup

Suppose an administrator accidentally runs:

```sql
DELETE FROM customers;
```

Replication faithfully copies the change.

Soon:

```text
Primary:
customers deleted

Replica A:
customers deleted

Replica B:
customers deleted
```

Replication succeeded perfectly.

Yet the data is gone everywhere.

That is why:

```text
multiple current copies
```

is not the same as:

```text
historical recoverability
```

## Corruption and bad application writes can replicate too

Other examples:

```text
UPDATE accounts
SET balance = 0;
```

without a `WHERE` clause.

Or an application bug writes:

```text
customer_email = NULL
```

for millions of customers.

Or malicious credentials delete records.

Replication may propagate those changes to every healthy replica.

A replica protects against some infrastructure failures.

It does not automatically protect against:

```text
logical corruption
operator mistakes
application bugs
malicious valid writes
```

## Backup solves a different problem

A backup preserves an earlier recoverable state.

For example:

```text
Monday backup
Tuesday backup
Wednesday backup

+
transaction/WAL/binlog archive
```

may allow restoration to:

```text
Wednesday 14:37:12
```

before an accidental deletion at:

```text
14:37:15
```

This is point-in-time recovery.

Replication provides:

```text
another current copy
```

while backups and retained logs provide:

```text
historical recovery points
```

A resilient system often needs both.

## Replica, backup, and failover are different concepts

| Mechanism | Main question |
|---|---|
| Replica | Do I have another copy receiving current changes? |
| Backup | Can I restore an earlier state? |
| Failover | Can another node safely become the writer? |
| Point-in-time recovery | Can I restore to a chosen moment? |
| Read replica | Can I offload some read workload? |

Having one does not prove that the others are properly implemented.

For example:

```text
three replicas
```

does not answer:

```text
Can I recover data deleted last Tuesday?
```

## Replication is not sharding

These concepts are also frequently confused.

### Replication

```text
Node A:
customers 1-1,000,000

Node B:
customers 1-1,000,000
```

The nodes contain overlapping copies.

### Sharding

```text
Shard A:
customers 1-500,000

Shard B:
customers 500,001-1,000,000
```

Different nodes own different subsets.

Replication solves:

```text
copying / availability / read scaling
```

Sharding solves:

```text
partitioning data or write load
```

They can be combined:

```text
Shard 1
   primary
   replica

Shard 2
   primary
   replica

Shard 3
   primary
   replica
```

## Read scaling does not scale writes

Suppose:

```text
Primary
   |
   +--- Replica A
   +--- Replica B
   +--- Replica C
```

You can distribute:

```text
SELECT
```

traffic across several replicas.

But if all writes still go through one primary:

```text
INSERT
UPDATE
DELETE
```

write throughput is still constrained by the single-writer path.

Adding read replicas does not magically partition write load.

That is one reason multi-primary systems and sharding exist—but they introduce much harder conflict and coordination problems.

## Cascading replication

Replicas do not always connect directly to the primary.

A topology can be:

```text
Primary
   |
   v
Replica A
   |
   +------> Replica B
   |
   +------> Replica C
```

This is cascading replication.

It can reduce:

```text
connections to primary
cross-site bandwidth
```

but adds another dependency.

If A falls behind, B and C cannot be more current than the data they receive through A.

PostgreSQL supports cascading physical streaming replication, where one standby can stream WAL to downstream standbys. PostgreSQL currently documents that cascading replication itself is asynchronous.

## Monitoring replication

A production replication system should answer at least:

| Question | Why it matters |
|---|---|
| Is the replica connected? | Disconnected replicas stop advancing |
| What position has the source produced? | Defines the latest available state |
| What position has the replica received? | Measures transport lag |
| What has the replica persisted? | Measures durability progress |
| What has the replica applied/replayed? | Measures query freshness |
| Is lag growing or shrinking? | Distinguishes transient delay from overload |
| How much log is retained for the replica? | Prevents source disk exhaustion |
| Is the replica eligible for failover? | Avoids promoting a bad candidate |
| How large is the redo/apply queue? | Affects freshness and potentially RTO |

Monitoring only:

```text
"replication process = running"
```

is not enough.

## Concrete monitoring concepts by engine

| PostgreSQL | MySQL | SQL Server |
|---|---|---|
| `pg_stat_replication` | Replication connection/status metadata | Availability Group dashboard / DMVs |
| WAL LSN positions | GTID / binary-log positions | received/hardened/redone LSNs |
| receive/flush/replay progress | receiver vs applier progress | send queue / redo queue |
| replication slot state | relay logs | synchronization state |
| `pg_stat_wal_receiver` | replica I/O/applier state | `sys. dm_hadr_database_replica_states` |

PostgreSQL documents WAL-position monitoring and replication sender/receiver views. MySQL tracks source and relay-log/applier positions and supports GTID-based progress tracking. SQL Server exposes redo and synchronization information through Availability Group monitoring and `sys. dm_hadr_database_replica_states`.

## Technology summary

| Feature | PostgreSQL physical streaming | MySQL source/replica | SQL Server Availability Groups |
|---|---|---|---|
| Change source | WAL | Binary log | Transaction log |
| Replica transport | `walsender` → `walreceiver` | Source → replica receiver | Primary → secondary |
| Apply mechanism | WAL replay | Replica applier thread(s) | Redo |
| Default/basic mode | Asynchronous streaming | Asynchronous | Async or sync configured per replica |
| Stronger durability mode | Synchronous standbys | Semisynchronous plugin | Synchronous commit |
| Can acknowledgement precede apply? | Yes, except `remote_apply` | Yes | Yes |
| Readable replica | Hot standby | Replica can serve reads | Readable secondary |
| Progress identifier | LSN | Binlog position / GTID | Log/LSN state |
| Typical HA use | Physical standby + external orchestration | Source/replica + HA tooling | Built-in Availability Group roles/failover integration |
| Selective logical replication | Built in publication/subscription | Binlog replication can filter; separate group/topology features exist | SQL Server has separate replication technologies besides AGs |

PostgreSQL's current documentation describes asynchronous physical streaming, synchronous standbys, WAL positions, hot standbys, and logical publication/subscription replication. MySQL documents source-to-replica asynchronous replication, semisynchronous replication, relay logs, and GTID positioning. SQL Server documents asynchronous/synchronous Availability Group replicas, readable secondaries, log hardening, and failover modes.

## Choosing what each replica is for

A replica should have an explicit job.

For example:

```text
Replica A
    synchronous
    same datacenter
    failover candidate

Replica B
    asynchronous
    another geographic region
    disaster recovery

Replica C
    asynchronous
    large machine
    analytical/reporting reads
```

Trying to make every replica satisfy every goal can create bad tradeoffs.

A reporting replica may tolerate lag but need substantial CPU.

A failover replica may prioritize:

```text
low lag
durable replication
fast promotion
strict monitoring
```

over analytical workloads.

## A useful design exercise

For each replica, answer:

```text
What is this replica for?

May applications read from it?

How stale may those reads be?

Can it be promoted?

How much acknowledged data may it be missing?

What acknowledgement does the primary wait for?

Does the acknowledgement mean receive, persist, or apply?

How do we know the replica is healthy?

Who decides failover?

How is the old primary fenced?

How do clients discover the new primary?

Where are the historical backups?
```

If those questions do not have clear answers, merely knowing:

```text
"we have replication"
```

does not tell you much about the system's actual reliability.

## Final mental model

Do not memorize replication as:

```text
Primary copies data to replica.
```

Use this model:

```text
WRITE ON PRIMARY
      |
      v
PRIMARY CHANGE LOG
      |
      v
SEND
      |
      v
RECEIVE ON REPLICA
      |
      v
PERSIST / HARDEN
      |
      v
APPLY / REPLAY
      |
      v
VISIBLE TO REPLICA READS
```

Then ask where `COMMIT SUCCESS` occurs.

### Asynchronous

```text
PRIMARY COMMIT
      |
SUCCESS TO CLIENT
      |
      v
SEND → RECEIVE → PERSIST → APPLY
```

Fast commits, but a primary failure can lose acknowledged transactions that have not reached the surviving replica.

### Synchronous durability

```text
PRIMARY
   |
SEND
   |
REPLICA PERSIST
   |
ACK
   |
SUCCESS TO CLIENT
```

Stronger protection, but higher latency.

### Synchronous visibility

Some technologies can go further:

```text
PRIMARY
   |
SEND
   |
REPLICA PERSIST
   |
REPLICA APPLY
   |
ACK
   |
SUCCESS TO CLIENT
```

PostgreSQL `remote_apply` is a concrete example.

Finally, keep these four concepts separate:

```text
REPLICATION
    another current copy

FAILOVER
    make another copy authoritative

BACKUP
    retain recoverable historical state

SHARDING
    divide different data among nodes
```

The central replication question is therefore not:

> "Do we have a replica? "

It is:

> "When we tell the application that a transaction succeeded, where else does that transaction exist, how durable is it there, has it been applied there, and what happens if the current primary disappears at that exact moment? "

That question connects replication lag, synchronous versus asynchronous replication, read consistency, RPO, RTO, and failover into one coherent model.

## References

PostgreSQL's current high-availability documentation describes physical WAL streaming, asynchronous and synchronous standbys, hot standby reads, replication slots, cascading replication, promotion, WAL positions, and the different synchronous acknowledgement levels.

PostgreSQL's logical replication documentation describes publications/subscriptions, initial synchronization, logical replication identities, selective replication, and cross-version/platform use cases.

MySQL's current replication documentation describes asynchronous source-to-replica replication, binary/relay logs, GTID positioning, replica initialization, and semisynchronous acknowledgement behavior.

Microsoft's SQL Server Availability Group documentation describes asynchronous and synchronous commit, secondary log hardening, readable secondaries, redo lag, failover modes, listeners, and RPO/RTO-related monitoring.
