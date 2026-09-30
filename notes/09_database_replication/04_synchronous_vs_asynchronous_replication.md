# Synchronous and Asynchronous Replication

The fundamental difference between synchronous and asynchronous replication is:

> What must happen on another node before the database tells the client that the transaction succeeded?

A simplified model is:

```text id="cgayks"
SYNCHRONOUS

transaction
    |
    v
local commit work
    |
    v
required remote progress
    |
    v
SUCCESS to client
```

versus:

```text id="jsh4qs"
ASYNCHRONOUS

transaction
    |
    v
local commit work
    |
    v
SUCCESS to client
    |
    +------ remote replicas continue catching up
```

The key difference is therefore not:

```text id="tsn6u7"
"Are changes transmitted immediately?"
```

but:

```text id="z4d3ow"
"Does client-visible commit success depend on
replica progress?"
```

An asynchronous system can begin transmitting changes almost immediately.

It is still asynchronous if the client does not have to wait for replica progress before receiving success.

# 1. Start with one transaction

Suppose the application creates an order:

```sql id="oxq27b"
BEGIN;

INSERT INTO orders(order_id, customer_id, amount)
VALUES (104, 27, 89.00);

COMMIT;
```

Assume:

```text id="kdjqwz"
Primary
Replica
```

The database must decide at what point:

```text id="cjymc9"
COMMIT
```

is allowed to return:

```text id="wsr84l"
SUCCESS
```

to the application.

There are several possible milestones.

# 2. The replication pipeline

A useful generic pipeline is:

```text id="g7zvd8"
PRIMARY

transaction executes
      |
      v
change/log record created
      |
      v
local log write
      |
      v
local durable flush
      |
      v
send across network
      |
      v

REPLICA

receive
      |
      v
write
      |
      v
durably flush
      |
      v
apply / replay
      |
      v
visible to replica query
```

Not every database exposes exactly these stages, but the model is extremely useful.

The important events are different:

```text id="rzqlr9"
received
≠
durable
≠
applied
≠
visible to reads
```

# 3. Why the acknowledgment point matters

Suppose a replica says:

```text id="11apt3"
"I received transaction 104."
```

That might mean only:

```text id="6rfkk6"
the bytes reached my process
```

If that machine immediately loses power, perhaps the change disappears.

A stronger acknowledgment is:

```text id="dyvrde"
"I flushed transaction 104 to durable storage."
```

Now the transaction has survived more failure modes.

An even stronger acknowledgment might be:

```text id="djj75p"
"I replayed transaction 104
and my queries can now see it."
```

Each additional requirement generally increases:

```text id="bq5rua"
durability or visibility guarantees
```

but also increases:

```text id="qjmngk"
commit latency
```

because the primary must wait longer.

# 4. Asynchronous replication

In asynchronous replication, replica progress is not part of the client-visible commit requirement.

Timeline:

```text id="286t9h"
Client             Primary                Replica
   |                  |                      |
   |---- INSERT ----->|                      |
   |                  |                      |
   |                  | local durable commit |
   |                  |                      |
   |<---- SUCCESS ----|                      |
   |                  |                      |
   |                  |------- changes ----->|
   |                  |                      |
   |                  |                 receive
   |                  |                 persist
   |                  |                 apply
```

The client may hear:

```text id="0zo99d"
SUCCESS
```

while the replica still lacks the transaction.

This produces:

```text id="4b17eq"
lower commit latency
```

but creates a window during which:

```text id="8374rk"
primary contains newer acknowledged data
than replica
```

# 5. "Asynchronous" does not mean "send everything later"

This is an important correction to a common misconception.

An asynchronous primary might stream changes while the transaction is still progressing.

For example:

```text id="b4f3hu"
Primary                     Replica

generate log record 1 -----> receive

generate log record 2 -----> receive

generate commit record ----> receive
```

The replica may even be almost completely caught up by the time the primary commits.

The replication is still asynchronous if:

```text id="y8y1l9"
primary does not need a replica acknowledgment
before reporting success
```

So:

> Synchronous versus asynchronous describes the commit dependency, not necessarily when network transmission begins.

# 6. Failure window in asynchronous replication

Suppose the sequence is:

```text id="ydrsv6"
1. Transaction 104 commits on primary.

2. Primary returns SUCCESS.

3. Transaction 104 has not reached replica.

4. Primary suffers unrecoverable failure.

5. Replica is promoted.
```

The new primary may not contain:

```text id="x8gxx1"
transaction 104
```

even though the application previously received:

```text id="9lxg1t"
SUCCESS
```

This is the classic asynchronous replication data-loss window.

# 7. Replication lag

The distance between primary and replica progress is called replication lag.

Suppose:

```text id="qbwc42"
Primary:
transactions through 10,000

Replica:
transactions through 9,970
```

The replica is:

```text id="dxc5ti"
30 transactions behind
```

But lag can be measured in several ways:

```text id="p7u8wf"
bytes

log positions

number of transactions

estimated seconds

apply queue size
```

A single:

```text id="iq3x27"
lag = 2 seconds
```

number can hide important details.

# 8. Lag in seconds can be misleading

Consider two databases.

### Database A

```text id="fw8p3s"
2 seconds behind

primary generating 1 KB/sec
```

Outstanding replication data is tiny.

### Database B

```text id="dev7bm"
2 seconds behind

primary generating 5 GB/sec
```

Outstanding replication work is enormous.

Both display:

```text id="vtsjkt"
2 seconds lag
```

but operationally they are radically different.

That is why production monitoring should inspect:

```text id="w0xkfj"
log positions
bytes queued
apply rates
```

as well as time-based lag estimates.

# 9. Why asynchronous replicas return stale reads

Suppose:

```text id="uwb5l6"
Primary:
order 104 exists

Replica:
order 104 has not been applied
```

A user creates order `104`:

```text id="k7yywv"
POST /orders

→ Primary
→ SUCCESS
```

Then immediately:

```text id="7f7g52"
GET /orders/104
```

is routed to the replica.

The replica returns:

```text id="5oxt0v"
not found
```

The database has not necessarily malfunctioned.

The read simply arrived before replication caught up.

# 10. Read-your-writes consistency

Users often expect:

```text id="n18pgo"
I wrote X.

Then I read X.

Therefore I should see X.
```

That property is often called:

```text id="758v7m"
read-your-writes consistency
```

Plain asynchronous replicas do not automatically provide it.

Possible application strategies include:

```text id="m1o1k0"
write to primary
then temporarily read from primary
```

or:

```text id="xeo8bq"
return the newly created object
directly from the write response
```

or:

```text id="jrjeww"
record the write's replication position
and wait until the chosen replica reaches it
```

The correct solution depends on the application.

# 11. Synchronous replication

Synchronous replication changes when the client receives success.

Conceptually:

```text id="t8cdrb"
Client             Primary                Replica
   |                  |                      |
   |---- write ------>|                      |
   |                  |                      |
   |                  |------ change ------->|
   |                  |                      |
   |                  |                 required
   |                  |                 progress
   |                  |                      |
   |                  |<------- ACK ---------|
   |                  |                      |
   |<---- SUCCESS ----|                      |
```

The primary's commit is now dependent on a particular remote event.

But:

```text id="3cmnfk"
remote event
```

must be defined.

# 12. "Synchronous" is incomplete without the acknowledgment level

Consider these possible requirements:

```text id="yu9v83"
A. Replica received the data.

B. Replica wrote it to its operating-system buffers.

C. Replica durably flushed it to storage.

D. Replica applied/replayed it.

E. Replica made it visible to user queries.
```

Each one is stronger than a simple:

```text id="05er6y"
"some network packet arrived"
```

Different database engines expose different choices.

Therefore:

> Never document a system merely as "synchronous. " Document what acknowledgment is required.

# 13. Receive versus durable persistence

Suppose the replica receives:

```text id="aal5vf"
transaction 104
```

into RAM.

It acknowledges.

Then:

```text id="qfk98e"
replica power fails
```

If the change had not reached durable storage, it may disappear.

So:

```text id="kg50n9"
receive acknowledgment
```

and:

```text id="t1op91"
durability acknowledgment
```

provide different guarantees.

# 14. Durable versus applied

Now suppose the replica has safely written transaction `104` to its recovery log.

Its state is:

```text id="p42xqt"
log contains transaction 104

database pages/read state
still reflect transaction 103
```

If the replica crashes and restarts, it can replay the durable log.

So the transaction is protected.

But an immediate query may still not see it.

Therefore:

```text id="uh1fb8"
durability
```

and:

```text id="vjx79p"
read freshness
```

are separate properties.

# 15. The most important replication distinction

Remember:

```text id="ajqn8d"
DURABLE ON REPLICA

does not necessarily mean

VISIBLE ON REPLICA
```

That one distinction explains a surprising amount of behavior in:

```text id="v819m9"
PostgreSQL
SQL Server
MySQL
other log-based replication systems
```

# 16. PostgreSQL: the clearest example

Current PostgreSQL exposes several commit levels through:

```text id="b37569"
synchronous_commit
```

Relevant values include:

```text id="1a9l55"
remote_apply
on
remote_write
local
off
```

When synchronous standbys have actually been configured, those values determine how much standby progress the transaction waits for. PostgreSQL documents `remote_write`, `on`, and `remote_apply` as distinct remote acknowledgment levels.

# 17. PostgreSQL requires a synchronous standby configuration too

A subtle but important point:

```conf id="nyywqd"
synchronous_commit = remote_apply
```

alone does not magically create a synchronous replica.

The primary also needs:

```conf id="00oc6z"
synchronous_standby_names = '...'
```

to identify which connected standbys participate in synchronous replication.

PostgreSQL's current documentation states that `synchronous_standby_names` must be non-empty before streaming replication becomes synchronous.

So there are two distinct questions:

```text id="mawgpi"
Which replicas count?

What progress must they report?
```

# 18. PostgreSQL `remote_write`

With:

```conf id="5jk0f6"
synchronous_commit = remote_write
```

the primary waits until the selected synchronous standby reports that the commit record has been received and written to the standby operating system.

It does not require that the WAL be durably flushed to persistent storage there.

PostgreSQL therefore documents `remote_write` as weaker than normal synchronous `on`, but potentially lower latency.

Conceptually:

```text id="rlkrup"
Primary durable

Standby received
Standby OS write completed

→ client SUCCESS
```

# 19. PostgreSQL `synchronous_commit = on`

With a synchronous standby selected and:

```conf id="85ssgn"
synchronous_commit = on
```

the primary waits for the synchronous standby to report that the commit WAL has been flushed to durable storage.

Conceptually:

```text id="62hmhd"
Primary durable

Standby received
Standby durable

→ SUCCESS
```

PostgreSQL describes this as the normal durable synchronous-replication level.

But the standby might still not have replayed the transaction.

# 20. PostgreSQL `remote_apply`

With:

```conf id="3k9bxz"
synchronous_commit = remote_apply
```

the primary waits until the synchronous standby reports that it has:

```text id="y4mlyw"
received
flushed
and replayed
```

the transaction.

PostgreSQL specifically says that at this point the transaction has become visible to queries on that standby.

Timeline:

```text id="1quv73"
Primary commit
      |
      v
send WAL
      |
      v
standby receive
      |
      v
standby durable flush
      |
      v
standby replay
      |
      v
ACK
      |
      v
SUCCESS
```

This provides a stronger read-after-commit property at the cost of higher latency.

# 21. PostgreSQL summary

| `synchronous_commit` | Client success waits for |
|---|---|
| `remote_write` | Remote filesystem write |
| `on` | Remote durable WAL flush |
| `remote_apply` | Remote replay / read visibility |
| `local` | Local durable WAL only |
| `off` | Does not wait for local WAL flush before reporting success |

For the remote modes to have their remote meaning, `synchronous_standby_names` must select synchronous standbys. PostgreSQL otherwise treats the non-`off` options as local durable commit behavior.

# 22. PostgreSQL can choose which standbys count

Suppose:

```text id="xuzpgv"
Primary

A
B
C
```

A priority configuration might say:

```conf id="bn7ht8"
synchronous_standby_names =
    'FIRST 1 (a, b, c)'
```

meaning:

```text id="ydhoif"
wait for one synchronous standby,
preferring A, then B, then C
```

A quorum configuration might say:

```conf id="8rvhn6"
synchronous_standby_names =
    'ANY 2 (a, b, c)'
```

meaning:

```text id="0im5qs"
wait for acknowledgments
from any two candidates
```

PostgreSQL supports both priority-based and quorum synchronous replication.

# 23. Why synchronous replication increases commit latency

Suppose local storage commit takes:

```text id="8q3jvi"
1 ms
```

but the required replica is:

```text id="dc7olp"
40 ms network round trip away
```

The commit must now include enough remote communication to obtain the acknowledgment.

Conceptually:

```text id="19rcnm"
local work       1 ms
network/storage 40+ ms
----------------------
commit latency   much higher
```

Actual latency is pipeline-dependent, so these numbers should not simply be added mechanically.

The important point is:

> Remote coordination is now on the transaction's critical path.

# 24. Geography therefore matters

A synchronous replica in the same availability zone or nearby datacenter may have low round-trip latency.

A required synchronous replica on another continent can dramatically increase write latency.

This often produces architectures such as:

```text id="n86xvo"
Primary
  |
  +-- nearby synchronous standby
  |
  +-- remote asynchronous disaster-recovery standby
```

Different copies have different purposes.

# 25. MySQL uses different terminology: semisynchronous replication

Traditional MySQL source-to-replica replication is asynchronous.

MySQL 8. 4 also supports:

```text id="51f68w"
semisynchronous replication
```

The source waits for acknowledgment from one or more configured semisynchronous replicas before returning to the committing session.

The name is intentional:

```text id="b2gv86"
semisynchronous
```

rather than simply:

```text id="otjo4r"
fully synchronous apply
```

because replica application remains separate.

# 26. What does a MySQL semisynchronous replica acknowledge?

MySQL documents that the replica acknowledges a transaction after its events have been written to the replica's relay log and flushed to disk.

Conceptually:

```text id="xphw76"
SOURCE

transaction
   |
binary log
   |
   +-------------------->
                        REPLICA
                          |
                       relay log
                          |
                     durable flush
                          |
                         ACK
   <----------------------+
   |
client may continue
```

The replica does not have to finish applying the transaction before sending that semisynchronous acknowledgment.

# 27. MySQL semisynchronous durability is not replica read freshness

Immediately after the acknowledgment:

```text id="hvh6ab"
Replica relay log:
contains transaction 104
```

but:

```text id="ksnbat"
Replica SQL/applier:
may not have applied 104 yet
```

Therefore:

```sql id="hdd8fn"
SELECT *
FROM orders
WHERE id = 104;
```

on the replica may still lag behind.

Again:

```text id="ik5330"
durable replication progress
≠
query-visible application
```

# 28. MySQL `AFTER_SYNC`

MySQL's default semisynchronous source wait point is:

```text id="xf1qft"
AFTER_SYNC
```

At a high level:

```text id="cprj66"
source writes transaction to binary log

source sends it toward replicas

source syncs binary log

source waits for required replica acknowledgment

source commits to storage engine

source returns result
```

MySQL documents `AFTER_SYNC` as the default semisynchronous wait point.

This ordering is specifically chosen to improve consistency of what clients can observe on the source during failover scenarios.

# 29. MySQL `AFTER_COMMIT`

The alternative is:

```text id="y36fd3"
AFTER_COMMIT
```

Conceptually:

```text id="8mcs6d"
source writes/syncs binary log

source commits locally

source waits for replica acknowledgment

source returns SUCCESS
```

So the remote acknowledgment still affects when the client hears success, but it occurs after local storage-engine commit.

MySQL documents both `AFTER_SYNC` and `AFTER_COMMIT` as supported semisynchronous wait points.

# 30. MySQL semisynchronous can fall back to asynchronous

This is an extremely important operational detail.

Suppose the source requires a replica acknowledgment but no qualifying replica responds.

MySQL waits up to:

```text id="6xosjk"
rpl_semi_sync_source_timeout
```

The default documented value is:

```text id="t490r8"
10,000 ms
```

After that timeout, MySQL can revert to ordinary asynchronous replication.

So:

```text id="8qp5qe"
semisynchronous enabled
```

does not necessarily mean:

```text id="608mex"
the source will refuse all future writes
until a replica acknowledges.
```

The configured fallback behavior matters.

# 31. This changes the durability guarantee

Suppose semisynchronous replication is healthy:

```text id="dsa1ay"
Source
  |
  +----> Replica
           ACK
```

Now the replica disappears.

After the timeout:

```text id="u82d08"
source falls back to asynchronous mode
```

The application may continue receiving successful commits.

Those newer commits do not have the same remote durability guarantee.

Therefore monitoring should distinguish:

```text id="55p5cm"
semisynchronous configured
```

from:

```text id="qpu234"
semisynchronous currently operational
```

MySQL exposes status variables specifically for that purpose.

# 32. MySQL can require several acknowledgments

The setting:

```text id="q5g6m4"
rpl_semi_sync_source_wait_for_replica_count
```

controls how many replica acknowledgments are required.

Its documented default is:

```text id="v1lm6u"
1
```

For example:

```text id="061539"
source
 |
 +--> replica A
 +--> replica B
 +--> replica C
```

with:

```text id="svua8c"
wait_for_replica_count = 2
```

the source waits for two replica acknowledgments before satisfying the semisynchronous requirement.

# 33. Waiting for application is separate in MySQL too

MySQL provides synchronization functions that can wait until a replica has applied changes through a specified source binary-log position.

For example, current MySQL provides:

```text id="w2xaqu"
SOURCE_POS_WAIT()
```

which waits until a replica has read and applied updates through a requested position.

This is a different operation from semisynchronous commit acknowledgment.

Semisynchronous acknowledgment answers:

```text id="e966me"
has enough remote durability been achieved?
```

whereas position waiting can answer:

```text id="xq702c"
has this replica applied through
the position I need to read?
```

# 34. SQL Server Availability Groups

SQL Server Always On Availability Groups provide:

```text id="hotd83"
asynchronous-commit mode
```

and:

```text id="fqzmfk"
synchronous-commit mode
```

For an asynchronous secondary, the primary does not wait for that secondary to harden its transaction log before committing. Microsoft documents that this minimizes transaction latency but permits lag and possible data loss if failover uses a secondary that has not caught up.

# 35. SQL Server synchronous commit

For a healthy synchronous-commit secondary:

```text id="ocqvpq"
Primary
   |
send transaction log records
   |
   v
Secondary
   |
harden log
   |
ACK
   |
   v
Primary completes commit
```

Microsoft explicitly describes the acknowledgment as the secondary confirming that it has hardened the log.

That is a durability milestone.

It is not yet necessarily a read-visibility milestone.

# 36. SQL Server redo is separate

After the secondary hardens its transaction log:

```text id="tn6odb"
transaction is durable in secondary log
```

SQL Server still runs redo to apply those log records to the secondary's database files.

Conceptually:

```text id="x5qllq"
receive
   |
   v
harden transaction log
   |
   v
redo
   |
   v
query-visible database state
```

If redo cannot keep up, a:

```text id="vgv91l"
redo queue
```

develops. Microsoft documents this explicitly.

# 37. SQL Server synchronous secondary reads can therefore be stale

Suppose:

```text id="r5ja48"
log hardened through LSN 500

redo applied through LSN 450
```

A transaction at:

```text id="6v1q9q"
LSN 480
```

is durably present on the secondary.

But a read-only workload there may still not see its effects until redo catches up.

Microsoft specifically warns that readable secondaries can return stale data when hardened log records are waiting in the redo queue.

So:

```text id="td512s"
SQL Server synchronous commit
```

does not mean:

```text id="9cq3mv"
every readable secondary is caught up for queries.
```

# 38. SQL Server has an important failure nuance

A simplistic table often says:

```text id="bcew57"
synchronous replica disappears
→ primary blocks forever
```

That is not universally correct for SQL Server Availability Groups.

If a synchronous secondary stops responding long enough, SQL Server can mark it:

```text id="7kgidf"
NOT SYNCHRONIZING
```

and the primary can proceed rather than waiting for it under the normal/default behavior.

This means the data-protection state can change when the secondary becomes unhealthy.

# 39. `REQUIRED_SYNCHRONIZED_SECONDARIES_TO_COMMIT`

SQL Server 2017 and later provide:

```text id="4e9543"
REQUIRED_SYNCHRONIZED_SECONDARIES_TO_COMMIT
```

This lets administrators specify a minimum number of synchronized secondaries that must be available for primary commits.

For example:

```text id="fwajx6"
required = 1
```

can cause the primary to stop accepting normal commits if it cannot maintain the required synchronized-secondary condition.

Microsoft explicitly describes this as trading primary availability for stronger data protection.

This is an excellent example of why:

```text id="3r15kg"
"synchronous mode"
```

by itself is not the complete configuration.

# 40. Technology comparison

| Technology | Async mode | Stronger mode | What remote acknowledgment means |
|---|---|---|---|
| PostgreSQL | Streaming replication normally async | Synchronous standby | `remote_write`, durable flush with `on`, or replay with `remote_apply` |
| MySQL | Traditional source/replica async | Semisynchronous replication | Required replica has durably logged transaction events in relay log |
| SQL Server AG | Asynchronous commit | Synchronous commit | Secondary hardened transaction log |
| SQL Server with required synchronized secondaries | — | Stronger availability/data-protection rule | Minimum configured number must remain synchronized for commit availability |

The important differences are documented by PostgreSQL's synchronous-replication settings, MySQL's semisynchronous replication protocol, and SQL Server Availability Group modes.

# 41. Do not confuse replication mode with local durability

There are actually two separate questions:

```text id="oxzv4o"
1. Has the transaction become durable
   on the local primary?

2. Has it reached the required state
   on another replica?
```

For example, PostgreSQL:

```conf id="7t4i2i"
synchronous_commit = off
```

can report a transaction success before its WAL has been durably flushed locally.

That is a local durability choice, not simply:

```text id="w63ehh"
asynchronous replication
```

PostgreSQL documents `off` separately from the remote synchronous modes.

Similarly, SQL Server supports delayed transaction durability independently of Availability Group replication.

# 42. A useful two-axis model

Think of:

```text id="h8cgx7"
LOCAL DURABILITY
```

and:

```text id="7gf5dv"
REMOTE REPLICATION
```

as separate dimensions.

For example:

| Local primary | Replica | Meaning |
|---|---|---|
| Durable | No acknowledgment required | Traditional async replication |
| Durable | Replica receives/logs | Semisynchronous-style guarantee |
| Durable | Replica durably flushes | Strong synchronous durability |
| Durable | Replica applies | Strong synchronous visibility |
| Not yet durable | No remote requirement | Delayed local durability; weakest crash guarantee |

This prevents terminology such as:

```text id="1v2a92"
sync / async
```

from hiding several independent choices.

# 43. What if the replica fails?

With asynchronous replication:

```text id="le6r68"
Primary --------X-------> Replica
```

the primary normally continues committing.

The replica simply falls further behind.

This favors:

```text id="3zd7k5"
write availability
```

but reduces:

```text id="bqr0e2"
redundant durability
```

until replication recovers.

# 44. What if a required synchronous replica fails?

Now suppose the primary truly requires a remote acknowledgment.

The system must choose one of several policies:

```text id="1gk5ph"
wait indefinitely

wait for another eligible synchronous replica

fail the write

stop write availability

temporarily degrade to asynchronous behavior
```

Different products/configurations choose differently.

PostgreSQL synchronous transactions can remain waiting when the required synchronous-standby condition cannot be satisfied. PostgreSQL recommends configuring enough candidate synchronous standbys to maintain HA.

MySQL semisynchronous replication, by contrast, can time out and fall back to asynchronous operation.

SQL Server's behavior depends additionally on synchronization health and `REQUIRED_SYNCHRONIZED_SECONDARIES_TO_COMMIT`.

# 45. So "synchronous is less available" needs qualification

A common statement is:

```text id="fswfws"
synchronous replication
=
replica failure blocks writes
```

That can be true.

But the accurate version is:

> A strict remote acknowledgment requirement creates an availability dependency on the replicas needed to satisfy that requirement.

If a technology automatically degrades to asynchronous operation:

```text id="4zsezm"
writes may remain available
```

but:

```text id="84rol6"
the durability guarantee has weakened.
```

So always ask:

```text id="k0ou7e"
What does the database do
when the required replica disappears?
```

# 46. Durability versus availability during a partition

Imagine:

```text id="l877lb"
Primary       X       synchronous replica
```

The network is broken.

The primary can choose:

### Preserve remote durability guarantee

```text id="marg4v"
do not acknowledge new writes
```

Availability suffers.

### Preserve write availability

```text id="2lovge"
continue local commits
```

Remote durability guarantee is weakened.

This is another concrete manifestation of distributed-systems trade-offs.

# 47. Failover requires more than synchronous replication

Suppose:

```text id="c6bh0k"
Primary fails.

Replica has every acknowledged transaction.
```

Excellent.

But the system still has to:

```text id="h24mps"
detect the failure

choose the new writer

promote/elect it

prevent the old primary from accepting writes

redirect clients
```

Synchronous replication solved:

```text id="qeriy0"
where the transaction existed
```

not:

```text id="5add41"
who should now own write authority.
```

Therefore synchronous replication and failover are separate concerns.

# 48. Synchronous replication does not automatically prevent split brain

Suppose the old primary becomes isolated.

A standby is promoted.

Then the old primary reconnects only to clients and still believes it is writable.

Now:

```text id="vsfdvn"
Old primary:
accepts X

New primary:
accepts Y
```

There are two write histories.

This is split brain.

Preventing it requires:

```text id="t8e09e"
quorum
fencing
leases
cluster coordination
or another ownership mechanism
```

depending on the technology.

Replication acknowledgment alone is not enough.

# 49. Which replica should be promoted?

Suppose three async replicas exist:

```text id="xfhjg0"
A applied through 1000

B applied through 995

C applied through 970
```

Primary fails.

Choosing C merely because:

```text id="7i60fa"
C responded first
```

could lose more data than promoting A.

A failover manager therefore needs to understand:

```text id="vu90x6"
replication position

durability state

health

topology

authority
```

Promotion policy is part of the consistency/durability architecture.

# 50. RPO: Recovery Point Objective

RPO answers:

> How much committed business data may be lost after a disaster?

Examples:

```text id="m7um9h"
RPO = 0
```

means:

```text id="td97bm"
no acknowledged transactions may be lost
for the failures included in the design.
```

An RPO of:

```text id="lgiijw"
5 minutes
```

means the business accepts recovery potentially losing up to approximately five minutes of recent data under the specified disaster scenario.

Replication design should follow the RPO requirement.

Not the reverse.

# 51. RPO is not simply "replication lag"

Suppose normal lag is:

```text id="02hd6v"
200 ms
```

That does not automatically mean:

```text id="ty9fef"
RPO = 200 ms
```

RPO is a business/recovery objective.

Actual potential loss depends on:

```text id="v46lhu"
replication mode
failure type
which replicas survive
which replica is promoted
whether remote data is durable
```

Monitoring lag helps determine whether the implementation is meeting the intended RPO.

# 52. RTO: Recovery Time Objective

RTO answers:

> How long can the service remain unavailable after failure?

Suppose:

```text id="pvs777"
primary fails at 12:00:00
```

and:

```text id="b584tn"
service accepts writes again at 12:00:25
```

recovery took:

```text id="6icqbk"
25 seconds
```

RTO therefore concerns:

```text id="8futs3"
failure detection
election/promotion
recovery
routing
application reconnection
```

not merely replication.

# 53. Apply lag can hurt RTO too

Suppose a synchronous replica has every transaction durably recorded.

Excellent RPO.

But it has:

```text id="z3zx3e"
200 GB
```

of unapplied recovery/redo work.

Failover may still require additional recovery work before the new database becomes fully usable.

Microsoft explicitly documents that a large SQL Server redo queue can extend failover time even when the log has already been hardened on the secondary.

Thus:

```text id="rbt5kj"
good RPO
```

does not automatically imply:

```text id="53sumo"
good RTO.
```

# 54. RPO and RTO are independent dimensions

Imagine two systems.

### System A

```text id="890v8k"
RPO = 0
RTO = 2 hours
```

No committed data is lost, but recovery is slow.

### System B

```text id="o80f6t"
RPO = 5 minutes
RTO = 15 seconds
```

It comes back quickly but may lose several minutes of work.

Neither is inherently better.

The correct design depends on business requirements.

# 55. Synchronous replication is not backup

Suppose the application executes:

```sql id="jov6ak"
DELETE FROM orders;
```

Synchronous replication can ensure that the deletion is durably copied to another server before the primary reports success.

Now both contain:

```text id="q60fvk"
orders deleted
```

The replication system worked perfectly.

It did not preserve the old data.

# 56. The same is true for logical corruption

Examples:

```text id="0xm8uy"
bad deployment updates wrong rows

administrator drops table

application writes corrupted values

attacker with valid DB permissions deletes data
```

A replica faithfully copying current database state may reproduce every one of those changes.

You still need:

```text id="j1t4i3"
backups
WAL/binlog/log retention
point-in-time recovery
restore testing
```

for historical recovery.

# 57. Monitoring must distinguish the pipeline stages

A good monitoring model asks:

```text id="1scbpd"
How far has the primary generated?

How far has the primary sent?

How far has the replica received?

How far has it durably persisted?

How far has it applied?

How far behind is the query-visible state?
```

Different stages imply different operational failures.

# 58. Example monitoring diagnosis

Suppose:

```text id="jb5a5w"
Primary position:          10000

Replica received:          9998

Replica durable:           9998

Replica applied:           8000
```

Network transport is healthy.

Durability is nearly current.

But application/replay is badly behind.

Likely investigation area:

```text id="541r3w"
replica CPU

disk I/O

long-running queries

apply-thread capacity

redo/replay blocking
```

Adding network bandwidth would probably not solve that problem.

# 59. Another diagnosis

Now suppose:

```text id="hn38y2"
Primary position:         10000

Replica received:          7000

Replica durable:           7000

Replica applied:           6999
```

Apply is keeping pace with what arrives.

The big gap is before receipt.

Investigate:

```text id="s8uut5"
network

sender throughput

receiver throughput

replication connection

bandwidth
```

Same high-level symptom:

```text id="hxczl1"
replica behind
```

different cause.

# 60. PostgreSQL monitoring example

PostgreSQL exposes:

```sql id="y6ot0u"
SELECT
    application_name,
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

The positions correspond to increasingly advanced stages of standby progress.

This is far more informative than a single:

```text id="9xwgsn"
replica connected = yes
```

flag.

# 61. SQL Server monitoring example

SQL Server Availability Group monitoring includes concepts such as:

```text id="i7ceeb"
log send queue

redo queue

redo rate

synchronization state
```

If:

```text id="38tuzm"
log send queue large
```

the secondary has not yet received/hardened all the primary's log.

If:

```text id="hcc0pg"
redo queue large
```

the log may already be safely on the secondary but has not yet been applied to query-visible data. Microsoft explicitly distinguishes these states in its Availability Group diagnostics.

# 62. MySQL monitoring also needs two stages

For traditional MySQL replication, distinguish:

```text id="wlj07m"
receiver progress
```

from:

```text id="qq7x41"
applier progress
```

The replica may have received transactions into its relay log while the SQL/applier side remains behind.

GTID sets or binary-log positions provide more useful progress information than a simple:

```text id="3mfhuw"
replica process running
```

status.

# 63. Synchronous replication and throughput

Synchronous replication does not necessarily reduce raw transaction throughput by exactly:

```text id="0nccu4"
1 / network latency
```

because databases pipeline:

```text id="1jjfvl"
WAL writes

network transmission

group commit

replica acknowledgments
```

across concurrent transactions.

A system can still process many synchronous commits concurrently.

However, individual transaction latency must include enough remote progress to satisfy the synchronization rule.

So the practical impact depends on:

```text id="g3k5bt"
network RTT
storage latency
group commit
transaction rate
replica performance
number of required acknowledgments
```

# 64. Group commit helps

Suppose 100 transactions become ready to commit at nearly the same time.

A database may avoid doing:

```text id="rm5c64"
100 independent disk syncs
```

and instead combine durability work.

Conceptually:

```text id="u5vxll"
T1
T2
T3
...
T100
   \
    +---- one batch WAL/log flush
```

Similar batching can help replication.

Therefore synchronous replication can still provide substantial throughput even while adding remote commit latency.

# 65. Synchronous replication and tail latency

Average latency is not the only concern.

Suppose:

```text id="hotgha"
replica normally acknowledges in 2 ms
```

but occasionally stalls for:

```text id="f1enl1"
200 ms
```

If that replica is required for commit, user transaction latency may suddenly spike.

This produces high:

```text id="1od2wk"
p95
p99
p99.9
```

latency even if average performance looks acceptable.

For user-facing workloads, monitor latency distributions rather than averages only.

# 66. One slow synchronous participant can matter greatly

Suppose the primary waits for:

```text id="6gw5gg"
ALL 3 replicas
```

and their response times are:

```text id="4omqph"
A = 2 ms
B = 3 ms
C = 100 ms
```

The slow replica may dominate the acknowledgment.

If the policy instead requires:

```text id="hi5xma"
ANY 2
```

the transaction can potentially proceed after A and B respond.

This is why quorum/standby-selection policy has major performance consequences.

# 67. More synchronous copies are not free

Suppose the durability goal changes from:

```text id="mre1j7"
wait for one remote durable copy
```

to:

```text id="vyc353"
wait for three remote durable copies
```

The system may gain resilience against more simultaneous failures.

But it may also increase exposure to:

```text id="qwfzys"
slow replicas
network jitter
storage stalls
partial outages
```

Replication count should follow the failure model and business requirement.

# 68. A practical architecture example

Suppose an online payment company deploys:

```text id="iax7ys"
Frankfurt Primary

Frankfurt Standby A

Berlin Standby B

Virginia Standby C
```

One possible policy:

```text id="251g05"
Standby A:
required synchronous durable copy

Standby B:
synchronous candidate/failover

Standby C:
asynchronous disaster-recovery copy
```

Why?

```text id="00k70d"
A/B:
low enough latency for synchronous commits

C:
far away; synchronous waiting would add too much latency
```

The topology balances:

```text id="h3c3tv"
RPO
latency
regional resilience
```

rather than treating every replica identically.

# 69. Another architecture: analytics replica

Suppose:

```text id="som09q"
Primary:
OLTP

Replica A:
HA

Replica B:
analytics
```

Replica B runs:

```text id="4hu32t"
large joins
hour-long reports
full scans
```

It may deliberately be asynchronous because analytics freshness requirements allow lag.

Replica A, meanwhile, may use stricter synchronous behavior because it is a failover candidate.

This illustrates an important principle:

> Different replicas can have different jobs and therefore different replication guarantees.

# 70. Comparison table

| Concern | Synchronous | Asynchronous |
|---|---|---|
| Client commit | Waits for configured remote progress | Does not wait for replica progress |
| Typical latency | Higher | Lower |
| Dependency on remote replica | Stronger | Weaker |
| Replica lag | Can still exist after the acknowledged stage | Expected |
| Read freshness | Depends on whether apply/replay is included | Usually may be stale |
| Primary failure | Required durable copies can protect acknowledged commits | Recent acknowledged commits may be missing |
| Network partition | Strict requirement may stop commits | Primary may continue alone |
| Geographic deployment | WAN latency can affect commit | Remote copies can lag without delaying commit |
| Failover | Still requires promotion/election and fencing | Same, plus potential-loss decision |
| Historical recovery | Still needs backup/PITR | Still needs backup/PITR |

The table is a starting point, not a substitute for knowing a product's exact acknowledgment and fallback rules.

# 71. Technology-specific summary

| Engine | Mode | Commit dependency |
|---|---|---|
| PostgreSQL | Async streaming | No standby required |
| PostgreSQL | `remote_write` | Required standby has written WAL to OS |
| PostgreSQL | `on` with sync standby | Required standby durably flushed WAL |
| PostgreSQL | `remote_apply` | Required standby replayed commit |
| MySQL | Async replication | No replica required |
| MySQL | Semisynchronous | Configured replica count durably logged events before client proceeds |
| SQL Server AG | Async commit | No secondary harden acknowledgment required |
| SQL Server AG | Sync commit | Healthy synchronous secondary hardens transaction log |
| SQL Server AG | Required synchronized secondaries | Configured minimum synchronization requirement can gate primary commit availability |

This demonstrates why:

```text id="6ums28"
sync
```

and:

```text id="36fn8a"
async
```

are families of behavior, not complete specifications.

# 72. Common misconceptions

| Claim | Better explanation |
|---|---|
| "Async sends changes only after commit. " | Transmission can overlap; the client simply does not wait for replica progress |
| "Sync means every replica is identical at commit. " | Only the required replicas/stage must meet the configured acknowledgment condition |
| "Replica received it, so it is safe. " | Receipt may differ from durable persistence |
| "Replica flushed it, so queries can see it. " | Apply/replay may still lag |
| "Sync replication guarantees fresh reads everywhere. " | Read freshness depends on which replica and acknowledgment/apply policy |
| "Sync replication guarantees zero data loss. " | Only for the covered failure model and correct failover target |
| "Async always loses data on failure. " | It *can* lose recent acknowledged changes; whether loss actually occurs depends on timing |
| "Synchronous secondary failure always blocks the primary. " | Product/fallback policy matters |
| "Semisync MySQL means replica applied the transaction. " | The acknowledgment concerns durable relay-log receipt, not completed application |
| "Replication gives us backup. " | Bad changes replicate too |

# 73. Questions to ask when someone says "we use synchronous replication"

Ask:

```text id="4r46se"
Which replicas participate?

How many acknowledgments are required?

What does acknowledgment mean?

Received?

Written?

Durably flushed?

Applied?

Visible?

What happens if one required replica disappears?

Do writes block?

Fail?

Choose another replica?

Fall back to asynchronous?

Which node can be promoted?

How is split brain prevented?

Can reads come from a replica?

How stale may they be?
```

Until those questions are answered:

```text id="yh3uiv"
"We use synchronous replication"
```

does not fully describe the guarantee.

# 74. Questions to ask for asynchronous replication

Likewise:

```text id="mk93nq"
How far may replicas lag?

How do we measure lag?

Which reads can use replicas?

How do we provide read-your-writes?

Which replica is selected for failover?

What acknowledged data might it be missing?

What RPO does the business permit?

How long can a replica remain behind
before it must be rebuilt?

How is WAL/binlog/log history retained?
```

Asynchronous replication is not:

```text id="k805fw"
"bad replication"
```

It is a deliberate latency/availability trade-off.

# 75. Choosing based on the business operation

Consider several workloads.

### Social-media like counter

A small amount of temporary replica staleness may be harmless.

Asynchronous replication can be a good fit.

### Financial transfer ledger

Losing an acknowledged transaction may be unacceptable.

Stronger synchronous durability may be appropriate.

### Analytics

Freshness within:

```text id="o9qxnc"
30 seconds
```

may be perfectly adequate.

An asynchronous analytical replica may make sense.

### User creates profile, then immediately loads it

General replica lag may be acceptable, but this specific interaction requires:

```text id="83cz3s"
read-your-writes
```

So the application might temporarily route the user's reads to the primary.

Different operations in the same application may need different guarantees.

# 76. PostgreSQL can choose durability per transaction

PostgreSQL's `synchronous_commit` can be changed at transaction/session level.

That means one application could choose:

```text id="kao36n"
payment transaction:
remote_apply / on
```

while another less critical transaction uses:

```text id="bw9xnn"
local
or
off
```

under an appropriate architecture.

PostgreSQL explicitly supports per-transaction synchronous-commit choices.

This can avoid imposing the highest durability cost on every piece of data.

# 77. Measure the workload, not only the configuration

Before changing replication mode, measure:

```text id="4jmr5m"
commit latency p50/p95/p99

network RTT

WAL/binlog/log generation rate

replica receive rate

flush rate

replay/apply rate

replica queue size

replica read staleness

failure/failover time

storage latency
```

A configuration that looks safe on paper can perform poorly if:

```text id="cy26jv"
one standby disk is overloaded
```

or:

```text id="zad5qy"
network latency is unstable.
```

# 78. Test failures rather than only normal replication

A meaningful replication test plan should include:

| Test | Question answered |
|---|---|
| Normal write | Does replication work? |
| Immediate replica read | How stale can reads be? |
| Slow replica disk | How does commit/apply latency react? |
| Replica disconnect | Does primary block, fail, or degrade? |
| Network partition | What happens to write availability? |
| Primary crash just after commit | Which acknowledged transactions survive? |
| Failover while replica behind | What data is lost? |
| Large apply queue | What happens to RTO? |
| Old primary returns | Is split brain prevented? |
| Accidental delete | Can backup/PITR restore the previous state? |

Replication is a failure-handling mechanism.

It should therefore be tested under failure.

# 79. RPO/RTO decision matrix

| Requirement | Likely architectural pressure |
|---|---|
| RPO approximately zero for covered primary failure | Require durable remote acknowledgment |
| Very low write latency | Prefer local/asynchronous path |
| Cross-continent replica | Async often easier for latency |
| Immediate read from secondary | Need apply-aware synchronization |
| Maximum write availability if replicas fail | Async or degradable policy |
| Must stop rather than weaken durability | Strict synchronous requirement |
| Fast failover | Keep candidate caught up and monitor replay/redo |
| Historical recovery | Separate backups/PITR |

The correct mode follows the recovery objective.

Not a universal rule such as:

```text id="1epb0g"
"synchronous is always better."
```

# 80. Final mental model

Do not memorize:

```text id="nxjhst"
synchronous = same data everywhere

asynchronous = delayed copy
```

Instead memorize this pipeline:

```text id="qb4iux"
PRIMARY

execute transaction
       |
       v
local log
       |
       v
local durable
       |
       v
SEND
       |
       v
---------------- NETWORK ----------------
       |
       v
REPLICA RECEIVE
       |
       v
REPLICA WRITE
       |
       v
REPLICA DURABLE FLUSH
       |
       v
REPLICA APPLY / REPLAY
       |
       v
VISIBLE TO READERS
```

Then place:

```text id="n05o0q"
CLIENT SUCCESS
```

somewhere on that timeline.

### Asynchronous

```text id="qwwkhd"
local durability
      |
SUCCESS
      |
remote replication continues
```

### Remote-write synchronous

```text id="jgoc2s"
replica receives/writes
      |
SUCCESS
```

### Durable synchronous

```text id="70c7bo"
replica durable
      |
SUCCESS
```

### Apply-aware synchronous

```text id="vpu73l"
replica replayed
      |
SUCCESS
```

Then ask:

```text id="xsr5hs"
How many replicas have to reach that point?

What happens if they cannot?
```

Those two questions define most of the practical replication guarantee.

# 81. Final principle

The most useful question is not:

> "Is our replication synchronous or asynchronous? "

It is:

> "When the application receives a successful commit, exactly which nodes possess that transaction, how durable is it on each of them, has it been applied there, and what will the system do if those nodes stop communicating at that exact moment? "

Once that question can be answered precisely, the trade-offs between:

```text id="z2ym2m"
latency
durability
availability
read freshness
RPO
RTO
failover safety
```

become much easier to reason about.

# References

PostgreSQL's current documentation distinguishes `remote_write`, `on`, and `remote_apply`; explains the role of `synchronous_standby_names`; and documents both priority-based and quorum synchronous replication.

MySQL 8. 4 documents asynchronous source/replica replication and semisynchronous replication, including durable relay-log acknowledgment, configurable acknowledgment counts, `AFTER_SYNC`/`AFTER_COMMIT`, and timeout-based fallback to asynchronous replication.

Microsoft's current SQL Server Availability Group documentation distinguishes asynchronous and synchronous commit, defines synchronous acknowledgment as secondary log hardening, and documents `REQUIRED_SYNCHRONIZED_SECONDARIES_TO_COMMIT` for stronger availability/data-protection control.

Microsoft separately documents redo queuing, in which log records can already be hardened on a secondary while remaining unapplied and therefore not yet visible to readable-secondary queries.
