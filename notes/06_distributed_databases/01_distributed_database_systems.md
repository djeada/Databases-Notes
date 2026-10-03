# Distributed Database Systems

A distributed database system stores and processes logically related data across multiple machines, processes, availability zones, or geographic locations while trying to present an application with a coherent database abstraction.

A simple picture might be:

```text
                         Clients
                            |
                            v
                    +----------------+
                    | Router / SQL    |
                    | endpoint        |
                    +-------+--------+
                            |
              +-------------+-------------+
              |             |             |
              v             v             v
           Node A        Node B        Node C
           data          data          data
           replicas      replicas      replicas
```

But a real distributed database involves much more than:

```text
"put the database on three servers"
```

The system must answer at least five questions:

```text
1. Where does each piece of data live?

2. How many copies of it exist?

3. How does a request find the correct node?

4. How do multiple nodes agree on updates?

5. How does a transaction remain correct when it
   touches data owned by several nodes?
```

Almost every major topic in distributed databases follows from those questions.

## Why distribute a database?

A single database server has finite:

```text
CPU
RAM
storage
network bandwidth
I/O throughput
failure tolerance
geographic proximity
```

Suppose an application grows from:

```text
10 GB
```

to:

```text
10 TB
```

and from:

```text
1,000 requests/sec
```

to:

```text
500,000 requests/sec
```

At some point, continually buying a larger machine becomes difficult, expensive, or insufficient.

A distributed database can spread work across machines.

Typical goals include:

| Goal | Why distribution helps |
|---|---|
| Storage scalability | Different nodes store different pieces of data |
| Read scalability | Replicas can serve additional reads |
| Write scalability | Independent partitions can accept unrelated writes |
| Availability | Another copy can survive a machine failure |
| Geographic locality | Data can be placed closer to users |
| Fault isolation | Failure of one machine need not destroy all data |
| Parallel query processing | Several nodes can process parts of a large query |

These advantages come with a major cost:

> Communication that used to happen inside one process or one machine becomes a distributed protocol.

## The central distinction: partitioning, replication, and coordination

Three ideas are often mixed together.

### Partitioning

Different nodes contain different pieces of the data.

```text
Node A:
customers 1–1,000,000

Node B:
customers 1,000,001–2,000,000
```

This primarily addresses:

```text
capacity
write scalability
parallelism
```

### Replication

Different nodes contain copies of the same data.

```text
Node A:
customers 1–1,000,000

Node B:
customers 1–1,000,000
```

This primarily addresses:

```text
availability
durability
read scaling
```

### Coordination

Nodes run protocols to decide:

```text
which copy is authoritative?

which write wins?

has this transaction committed?

who is the current leader?
```

This addresses:

```text
correctness
consistency
failover safety
```

A serious distributed database normally uses all three ideas together.

## Sharding and replication are orthogonal

Suppose the database is split into three shards:

```text
Shard A:
users 0–999

Shard B:
users 1000–1999

Shard C:
users 2000–2999
```

Each shard might then have three replicas:

```text
Shard A:
    A1
    A2
    A3

Shard B:
    B1
    B2
    B3

Shard C:
    C1
    C2
    C3
```

So:

```text
partitioning
```

answers:

```text
"Which shard owns user 1450?"
```

while:

```text
replication
```

answers:

```text
"How many copies of that shard exist?"
```

MongoDB is a concrete example: a sharded cluster distributes collection data across shards, and each shard is normally implemented as a replica set. `mongos` provides query routing while config servers maintain cluster metadata.

## A more realistic distributed-database picture

A modern distributed database often looks conceptually like:

```text
                     Application
                          |
                          v
                  +---------------+
                  | SQL / Query   |
                  | Router        |
                  +-------+-------+
                          |
            +-------------+-------------+
            |                           |
            v                           v
       Range / Shard A             Range / Shard B
       replicas:                   replicas:

       A1  A2  A3                  B1  B2  B3
        \   |  /                    \   |  /
         quorum                      quorum
```

The important point is:

```text
database node
```

is not necessarily equivalent to:

```text
one shard
```

A physical server may contain replicas of many different shards.

## Shared-nothing architecture

In a shared-nothing system, each node has its own:

```text
CPU
memory
storage
```

and communicates with other nodes over a network.

```text
+-------------+       +-------------+       +-------------+
| Node A      |       | Node B      |       | Node C      |
| CPU         |       | CPU         |       | CPU         |
| RAM         |       | RAM         |       | RAM         |
| local disk  |       | local disk  |       | local disk  |
+------+------+       +------+------+       +------+------+
       \                     |                     /
        +---------------- network ----------------+
```

This architecture is attractive for horizontal scaling because adding a node also adds:

```text
CPU
RAM
disk capacity
network capacity
```

Apache Cassandra is a classic example of a distributed architecture where partition-key hashing assigns portions of the token space across cluster nodes. Its default `Murmur3Partitioner` determines how partition keys map into the distributed token space.

## Shared-disk architecture

A shared-disk architecture gives nodes their own compute and memory but lets several nodes access a common storage subsystem.

```text
     Node A        Node B        Node C
    CPU/RAM       CPU/RAM       CPU/RAM
       \             |             /
        +------------+------------+
                     |
                     v
              Shared storage
```

Now the problem changes.

Data does not necessarily have to be copied between local disks, but the compute nodes still need to coordinate:

```text
cache ownership
locks
metadata
writes
recovery
```

Two nodes modifying the same storage page without coordination would corrupt the database.

Shared-disk therefore removes some data-placement problems but introduces strong coordination requirements around shared storage.

## Shared-memory architecture

A shared-memory or tightly coupled multiprocessor design gives multiple CPUs access to the same physical memory.

Conceptually:

```text
         Shared RAM
       /    |     \
     CPU1  CPU2   CPU3
```

This is useful for scaling a database inside one machine.

It is not usually what people mean when discussing geographically distributed databases.

Communication through shared RAM is fundamentally different from communication across:

```text
TCP
datacenter networks
regions
continents
```

where failures, message delay, and partitions become important.

## Architecture summary

| Architecture | CPU | Memory | Storage | Typical scaling problem |
|---|---|---|---|---|
| Shared memory | Multiple CPUs | Shared | Often shared | Contention inside one machine |
| Shared disk | Independent | Independent | Shared | Distributed cache/lock coordination |
| Shared nothing | Independent | Independent | Independent | Network coordination and data placement |

Modern cloud databases can also use disaggregated compute and storage, so production architectures do not always fit perfectly into these textbook categories.

The categories are mental models, not universal product labels.

## Centralized versus decentralized coordination

Another independent architecture choice concerns metadata and coordination.

### Centralized coordinator

One service may know:

```text
Shard 1 → Nodes A/B/C
Shard 2 → Nodes D/E/F
Shard 3 → Nodes G/H/I
```

Clients or routers consult that service to locate data.

This simplifies reasoning but creates a component whose availability and scalability must itself be protected.

### Distributed coordination

Metadata or decisions can instead be maintained through:

```text
consensus
gossip
distributed metadata tables
peer-to-peer membership
```

The advantage is eliminating one simple central authority.

The cost is considerably more protocol complexity.

## Client routing is not always a load balancer

A normal stateless web service often uses:

```text
client
  |
load balancer
  |
any application server
```

A database request is different because data may live only on particular nodes.

Suppose:

```text
user_id = 573829
```

belongs to shard B.

Sending the request to a random shard would be useless.

The system needs data-aware routing.

MongoDB uses `mongos` as a query router. A query containing the shard key can often be routed to the relevant shard, while a query that cannot be targeted may require broader scatter/gather work across shards.

## Horizontal partitioning

Horizontal partitioning divides rows.

Suppose:

```text
USERS

user_id | name
--------+-------
10      | Alice
10020   | Bob
30050   | Carlos
```

Range partitioning might produce:

```text
Shard A:
user_id < 10,000

Shard B:
10,000 <= user_id < 20,000

Shard C:
user_id >= 20,000
```

So:

```text
Alice  → A
Bob    → B
Carlos → C
```

Each shard stores the same table structure but only some rows.

## Hash partitioning

Instead of ranges:

```text
1–999
1000–1999
...
```

the system can compute:

```text
hash(partition_key)
```

and use the result to select a partition.

Conceptually:

```text
hash(user 101) → shard C
hash(user 102) → shard A
hash(user 103) → shard B
```

Hashing tends to distribute randomly distributed keys more evenly.

The downside is that naturally adjacent keys may no longer be stored together.

This can make range scans more expensive.

## Range partitioning

Range partitioning keeps nearby key values together.

For example:

```text
A: customer_id   1 – 9999
B: customer_id 10000 – 19999
C: customer_id 20000 – 29999
```

This is excellent for queries such as:

```sql
SELECT *
FROM customers
WHERE customer_id BETWEEN 11000 AND 11500;
```

because one shard may contain the entire range.

But a poor range key can create hotspots.

## The hotspot problem

Suppose an orders table uses:

```text
order_timestamp
```

as an ascending shard/range key.

All new orders occur at the end of the key space.

Therefore:

```text
all current writes
        |
        v
     one range
        |
        v
     one leader
```

Even though the database has:

```text
100 nodes
```

one hot range can become the bottleneck.

Google Spanner explicitly warns that monotonically increasing primary keys can create hotspots and recommends schema designs that spread load more evenly where appropriate.

Distributed databases therefore force schema design to consider:

```text
data distribution
```

as well as logical relationships.

## Spanner: automatic range splitting

Spanner stores rows ordered by primary key and automatically divides growing data into splits.

A split contains a contiguous range of rows and can move independently between servers.

Conceptually:

```text
key space:

A------------------------------Z

becomes:

A--------G
         H--------P
                  Q--------Z
```

As data grows, those splits can be distributed across different servers.

This is horizontal range partitioning managed automatically by the database.

## CockroachDB: ranges

CockroachDB follows a similar broad idea.

Its SQL data is encoded into a distributed ordered key space, which is divided into chunks called ranges.

Ranges are independently replicated and distributed across nodes; each range runs a Raft consensus group.

So a SQL table that appears conceptually as:

```text
one table
```

may physically involve:

```text
hundreds or thousands of ranges
```

spread across many machines.

## Vertical partitioning

Vertical partitioning divides columns or related data.

Suppose:

```text
CUSTOMERS

customer_id
name
email
profile_photo
biography
```

A system might separate:

```text
frequently accessed:
customer_id, name, email
```

from:

```text
large infrequently used:
profile_photo, biography
```

This can improve locality.

However, reconstructing the complete entity may now require multiple storage locations.

Vertical partitioning therefore trades:

```text
locality for one workload
```

against:

```text
cross-partition reads for another.
```

## Functional partitioning

A system can also divide data by business domain:

```text
Customer service:
profiles

Order service:
orders

Payment service:
payments

Inventory service:
stock
```

This is sometimes called functional or entity-based partitioning.

It often occurs in service-oriented and microservice architectures.

But now a business operation such as:

```text
create order
charge payment
decrement inventory
```

may cross several independently owned databases.

That turns a previously local transaction into a distributed workflow.

## Partitioning summary

| Strategy | Example key | Strength | Main danger |
|---|---|---|---|
| Range | `customer_id` intervals | Efficient range scans | Hot ranges |
| Hash | `hash(customer_id)` | Even distribution | Poor locality |
| List | country/tenant/category | Explicit placement | Uneven categories |
| Vertical | split columns | Workload locality | Reassembly cost |
| Functional | users/orders/payments | Domain isolation | Cross-service transactions |

There is no universally correct partitioning strategy.

The right question is:

> Which data is read and written together?

## Data locality matters because networks are expensive

Suppose one transaction modifies:

```text
customer
order
order_items
invoice
```

If all of those records reside in one shard:

```text
one server/range group
```

the transaction may be relatively cheap.

If they live on four different shards:

```text
Shard A → customer
Shard B → order
Shard C → items
Shard D → invoice
```

the database must coordinate several remote participants.

That adds:

```text
RPCs
consensus rounds
failure modes
transaction coordination
latency
```

Spanner's documentation explicitly notes that transactions involving data in one area of the key space are generally cheaper than transactions spread across many servers.

## Replication

Partitioning answers:

```text
where is this data?
```

Replication answers:

```text
how many copies exist?
```

Suppose shard A is stored only on node 1:

```text
Node 1
Shard A
```

If node 1 dies:

```text
Shard A unavailable
```

Replication instead keeps copies:

```text
Node 1: A1
Node 2: A2
Node 3: A3
```

Now a single machine failure does not necessarily destroy the shard.

## Asynchronous replication

With asynchronous replication:

```text
Primary
   |
   | commit
   v
SUCCESS to client
   |
   |
   +---------- replicate later ----------> Replica
```

Advantages:

```text
lower write latency
less dependence on replica response time
```

Risks:

```text
replication lag
stale replica reads
acknowledged writes may be missing after certain failovers
```

This is a good choice when some delay is acceptable.

## Synchronous replication

A synchronous write may require:

```text
write primary
      |
send to replicas
      |
wait for required acknowledgement
      |
return SUCCESS
```

This usually improves durability/consistency guarantees but increases latency.

A critical detail is:

> Synchronous does not automatically mean every replica has fully applied the transaction before the client hears success.

The exact acknowledgement point matters:

```text
received?
persisted?
applied?
visible to queries?
```

## Quorum replication

Suppose a shard has:

```text
N = 3 replicas
```

A system might require:

```text
2 replicas
```

to confirm a write.

That is a majority quorum:

```text
floor(N / 2) + 1
```

For `N = 3`:

```text
2
```

For `N = 5`:

```text
3
```

Quorums matter because two majorities must overlap.

For three replicas:

```text
Quorum 1 = {A, B}
Quorum 2 = {B, C}

intersection = B
```

That overlap is useful for consensus and strongly coordinated replicated state.

## MongoDB concrete example

A MongoDB replica set has:

```text
one primary
one or more secondaries
```

The primary accepts writes and records changes into the oplog; secondaries replicate and apply those operations. If the primary becomes unavailable, eligible members can elect another primary.

MongoDB also exposes write concern.

For example:

```javascript
{ w: "majority" }
```

requests acknowledgment from the calculated majority.

In a typical three-data-bearing-member set:

```text
Primary
Secondary
Secondary
```

a majority write generally requires acknowledgment from two members.

This demonstrates an important distributed-database concept:

> The durability/availability semantics depend not only on the product, but on the requested acknowledgement policy.

## Spanner replication

Spanner synchronously replicates database splits using Paxos-based replica groups.

A split has several replicas, and voting replicas participate in the decision for writes.

Conceptually:

```text
             Split X

              Leader
             /      \
            /        \
       Replica B   Replica C

             quorum
```

This combines:

```text
partitioning:
Split X owns a key range

replication:
several copies of Split X

consensus:
replicas agree on updates
```

Those three concepts should be kept separate even though Spanner uses them together.

## Replication and consensus are not the same thing

Replication means:

```text
make copies
```

Consensus means:

```text
make participants agree on a decision/order
despite failures
```

You can replicate data asynchronously without running a consensus algorithm for each write.

You can also run consensus specifically to establish:

```text
leader
log order
membership
configuration
```

The distinction matters.

Copying bytes is easier than deciding which conflicting state is authoritative.

## Distributed concurrency control

Now suppose transactions execute concurrently on several nodes.

Example:

```text
T1:
read account A
write account B

T2:
read account B
write account A
```

Inside one server, the database already needs concurrency control.

Across nodes, the same problem remains, but:

```text
locks
timestamps
validation
transaction state
```

may themselves need to be coordinated across machines.

Common approaches include:

```text
locking
timestamp ordering
optimistic concurrency control
MVCC
serializable validation
```

## Distributed Two-Phase Locking

With distributed locking, a transaction may acquire locks from several nodes.

Example:

```text
T1 needs:

X(account A) on Node 1
X(account B) on Node 2
```

The transaction may behave conceptually like:

```text
Node 1:
grant X(A)

Node 2:
grant X(B)

perform updates

commit

release both
```

The challenge is that waits can now cross machines.

A distributed deadlock might be:

```text
T1 on Node A waits for T2 on Node B

T2 on Node B waits for T1 on Node A
```

No individual local lock manager necessarily sees the whole cycle unless deadlock information is coordinated.

## Timestamp ordering

Another family of algorithms assigns transactions ordering metadata such as timestamps.

Conceptually:

```text
T1 timestamp = 100
T2 timestamp = 200
```

Operations are checked against that ordering.

Rather than making one transaction wait indefinitely for a conflicting lock, the system can decide:

```text
this operation violates the required timestamp order
→ abort/retry transaction
```

Distributed databases frequently combine timestamp techniques with:

```text
MVCC
locking
consensus
```

rather than using a pure textbook timestamp-ordering algorithm.

## Optimistic Concurrency Control

Optimistic concurrency control (OCC) assumes conflicts are relatively uncommon.

Conceptually:

```text
Phase 1:
read and compute without blocking competitors

Phase 2:
validate that relevant data did not change

Phase 3:
commit if validation succeeds
```

If validation fails:

```text
abort
retry
```

This is attractive under low contention because transactions do not need to hold extensive locks during normal execution.

Under heavy contention, however:

```text
many transactions
→ same hot records
→ many validation failures
→ repeated retries
```

can become expensive.

## Spanner provides a concrete modern example

Current Spanner supports both pessimistic and optimistic concurrency modes.

For its default serializable isolation, pessimistic concurrency is the default: transactions acquire relevant locks and Spanner uses wound-wait logic to resolve conflicting transactions.

For repeatable-read isolation, optimistic concurrency is the default: reads use a snapshot and conflicts are validated later.

This is useful because it demonstrates that:

```text
database product
```

does not necessarily imply:

```text
one concurrency-control algorithm.
```

The isolation level and transaction mode can change the mechanism.

## What is a distributed transaction?

Suppose a transfer moves:

```text
€100
```

from account `A` to account `B`.

If both accounts live on one shard:

```text
Shard 1:

A
B
```

the transaction is local.

Now suppose:

```text
Shard 1:
A

Shard 2:
B
```

The transaction becomes distributed.

We require:

```text
A -= 100
B += 100
```

to behave atomically.

The unacceptable outcomes are:

```text
A debited
B not credited
```

or:

```text
B credited
A not debited
```

Several nodes must therefore agree on one transaction outcome.

## Why cross-shard transactions cost more

A single-shard transaction can often be decided by one replica group.

A cross-shard transaction may require:

```text
find every participant
coordinate concurrency
prepare each participant
replicate each participant's state
agree on global outcome
publish commit/abort
```

That adds both latency and failure cases.

MongoDB explicitly notes that transactions touching multiple shards have greater performance cost than single-shard transactions.

Spanner likewise documents additional coordination for transactions spanning multiple splits.

## Two-Phase Commit (2PC)

Two-Phase Commit solves atomic commitment across participants.

It is unrelated to Two-Phase Locking.

Assume:

```text
Coordinator

Participant A
Participant B
```

The goal is:

```text
both commit
```

or:

```text
both abort
```

never:

```text
A commits
B aborts
```

## Phase 1: prepare

Coordinator asks:

```text
Can you commit transaction T?
```

Participant A checks:

```text
locks/resources available?
constraints valid?
changes durable enough to survive?
```

If yes:

```text
A → PREPARED / YES
```

Participant B does the same:

```text
B → PREPARED / YES
```

A prepared participant promises:

> If the coordinator later says COMMIT, I am capable of committing.

## Phase 2: decision

If every required participant prepared:

```text
Coordinator → COMMIT
```

Otherwise:

```text
Coordinator → ABORT
```

Conceptually:

```text
               Coordinator
                   |
          +--------+--------+
          |                 |
       PREPARE           PREPARE
          |                 |
          v                 v
     Participant A     Participant B
          |                 |
         YES               YES
          |                 |
          +--------+--------+
                   |
                 COMMIT
```

The protocol ensures one global atomic outcome.

## What happens if the coordinator disappears?

Suppose both participants have replied:

```text
PREPARED
```

Then the coordinator disappears before they learn whether the final decision is:

```text
COMMIT
```

or:

```text
ABORT
```

A participant cannot safely guess.

If it guesses commit:

```text
other participants might abort
```

If it guesses abort:

```text
coordinator might already have committed elsewhere
```

The classical 2PC problem is therefore that a prepared participant may have to retain transaction state/resources while the global decision is recovered.

Modern systems mitigate this with durable logs, replicated coordinators, recovery mechanisms, consensus groups, and implementation-specific optimizations.

But the basic uncertainty is the reason classical 2PC is described as a blocking commit protocol.

## PostgreSQL exposes prepared transactions directly

PostgreSQL supports:

```sql
PREPARE TRANSACTION 'transfer-123';
```

followed later by either:

```sql
COMMIT PREPARED 'transfer-123';
```

or:

```sql
ROLLBACK PREPARED 'transfer-123';
```

Once prepared, the transaction state is durably retained so an external transaction manager can later finish the distributed decision. PostgreSQL explicitly documents this interface for external two-phase transaction managers.

This makes textbook 2PC unusually visible.

## Spanner: 2PC plus consensus

Spanner provides an excellent example of why 2PC and consensus solve different problems.

Within each split:

```text
Paxos
```

replicates that split's state.

When one transaction spans several splits:

```text
2PC
```

coordinates the atomic transaction across those participant splits.

Spanner's documented multi-split write flow explicitly uses standard two-phase commit across splits, while each split's transaction state and decisions are themselves replicated through its Paxos group.

Conceptually:

```text
                 Transaction Coordinator
                   /              \
                  /                \
              Split A             Split B
            Paxos group         Paxos group
```

So:

```text
Paxos:
replicate/agree inside a shard

2PC:
commit atomically across shards
```

They are complementary.

## 2PC is not consensus

This distinction is fundamental.

Consensus answers something like:

> Can a group agree on a value/order despite failures?

Atomic commit answers:

> Should this distributed transaction commit or abort everywhere?

2PC assumes a coordinator-driven commit decision across participants.

Raft/Paxos establish replicated agreement despite failures.

A robust distributed database may layer them together.

Do not write:

```text
"Raft replaces 2PC"
```

or:

```text
"2PC is a consensus protocol"
```

without much more qualification.

## Three-Phase Commit

Three-Phase Commit adds another protocol stage to reduce the blocking conditions of basic 2PC under stronger timing/failure assumptions.

Textbooks typically present:

```text
canCommit?
preCommit
doCommit
```

The additional state can make certain decisions recoverable without indefinite blocking.

However, 3PC relies on assumptions that are difficult to guarantee in arbitrary asynchronous networks with partitions.

In practice, modern distributed databases much more commonly combine:

```text
replicated logs
consensus
2PC variants
transaction recovery
```

than deploy classic textbook 3PC.

So 3PC is important academically, but it should not be presented as the standard modern replacement for 2PC.

## Consensus: the problem it solves

Suppose three replicas contain the same shard:

```text
A
B
C
```

A write arrives.

The replicas need to establish one authoritative ordering:

```text
entry 51: x = 10
entry 52: x = 12
entry 53: y = 8
```

even when:

```text
messages are delayed
one machine crashes
leadership changes
```

Consensus algorithms such as:

```text
Paxos
Raft
```

solve this class of agreement problem.

## Raft mental model

Raft typically organizes nodes into:

```text
leader
followers
```

The leader proposes log entries.

For a three-replica group:

```text
       Leader A
       /      \
      /        \
Follower B   Follower C
```

A majority is:

```text
2 of 3
```

The system can continue committing entries as long as a quorum of the voting group remains mutually reachable.

If A is isolated:

```text
A       X       B ----- C
```

B and C can potentially elect a new leader because together they form a majority.

A alone cannot safely create an independent committed log.

## etcd: a concrete Raft system

etcd is a distributed key-value store built around Raft.

Its API responses expose both:

```text
revision
raft_term
```

which let clients identify the logical store revision and the Raft election term associated with a response.

Loss of quorum prevents the cluster from making ordinary new consensus progress; etcd's operational metrics explicitly identify loss of quorum as one cause of prolonged proposal failures.

This is a concrete example of consensus affecting availability.

## Replica learners

Adding a new voting replica immediately can be dangerous if the new node is far behind.

etcd therefore supports a learner state.

A learner:

```text
receives data
does not vote
does not count toward quorum
```

until it has caught up sufficiently to be promoted.

This addresses a subtle distributed-systems issue:

> Membership changes themselves can reduce fault tolerance if performed carelessly.

## Consensus does not make networks free

Suppose a three-region consensus group is:

```text
Frankfurt
Virginia
Singapore
```

A write cannot be fully coordinated faster than the network required to reach the necessary quorum.

Strongly coordinated replication therefore introduces physical latency.

That is one reason database placement matters.

Consensus solves correctness under failure.

It does not eliminate:

```text
speed of light
network congestion
disk latency
```

## Failure types

Distributed systems face more failure modes than a local database.

| Failure | Example |
|---|---|
| Process failure | DB process crashes |
| Machine failure | VM/server disappears |
| Disk failure | Local storage fails |
| Network partition | Nodes remain alive but cannot communicate |
| Packet loss | Some messages disappear |
| High latency | Messages arrive too slowly |
| Region failure | Entire datacenter becomes unreachable |
| Partial failure | Some components work while others do not |

The difficult case is often:

```text
partial failure
```

because one node cannot immediately distinguish:

```text
peer crashed
```

from:

```text
peer slow
```

from:

```text
network partitioned.
```

## Failure detection uses suspicion, not omniscience

Distributed systems often use:

```text
heartbeats
timeouts
leases
failure detectors
```

If A has not heard from B for ten seconds, A can conclude:

```text
B is probably unavailable
```

but not mathematically prove:

```text
B has ceased to exist.
```

This matters during leader election and failover.

If both sides of a network partition independently decide:

```text
"The other side is dead"
```

and both begin accepting conflicting writes, the system can produce split brain.

Consensus/quorum mechanisms are designed in part to prevent isolated minorities from making authoritative decisions.

## Logging and checkpointing

Durable distributed systems still rely on familiar local recovery techniques.

A write-ahead log records changes before the corresponding data pages need to be fully written.

Conceptually:

```text
transaction changes
       |
       v
durable log
       |
       v
data pages later
```

After a crash, the database can use the log to reconstruct committed state.

A checkpoint records that earlier portions of the log have already been reflected sufficiently in database state, reducing how much recovery work must be replayed.

In distributed databases, these local recovery mechanisms are combined with replication and consensus.

## Replication is not backup

Suppose a user executes:

```sql
DELETE FROM customers;
```

Replication can faithfully copy that deletion everywhere.

After replication:

```text
Replica 1:
deleted

Replica 2:
deleted

Replica 3:
deleted
```

Replication protects against some infrastructure failures.

It does not preserve historical states automatically.

Backups, snapshots, retained logs, and point-in-time recovery solve different problems.

## CAP enters because communication can fail

Suppose two replicas lose connectivity:

```text
Node A       X       Node B
```

A client writes:

```text
x = 10
```

to A.

Another client asks B:

```text
What is x?
```

B cannot know whether A accepted a newer write because the relevant information cannot cross the partition.

The system therefore faces the CAP trade-off:

```text
preserve strong consistency
→ some requests cannot complete

or

continue serving both sides
→ some responses may not belong to one
  linearizable global history
```

CAP is therefore about behavior during network partitions, not a permanent "pick two" product taxonomy.

## Quorum and CAP

Return to three replicas:

```text
A
B
C
```

Suppose operations require a majority.

Partition:

```text
A       X       B ----- C
```

The B/C side has:

```text
2 of 3
```

and can continue quorum-based authoritative operations.

A has:

```text
1 of 3
```

and cannot.

This preserves the quorum protocol by sacrificing availability on the minority side.

Quorum does not defeat CAP.

It implements a particular response to the partition.

## PACELC adds the healthy-network question

CAP asks what happens:

```text
if the network partitions.
```

PACELC also asks what happens:

```text
when the network is healthy.
```

The shorthand is:

```text
If Partition:
    Availability vs Consistency

Else:
    Latency vs Consistency
```

A strongly coordinated multi-region write might require:

```text
Frankfurt → Virginia → acknowledgement
```

before completing.

Even with no failure, that remote coordination increases latency.

Distributed-database design therefore involves trade-offs even during normal operation.

## Distributed query processing

Distribution affects reads too.

Suppose:

```sql
SELECT *
FROM users
WHERE user_id = 100;
```

and `user_id` is the partition key.

The router can likely target one shard.

But:

```sql
SELECT COUNT(*)
FROM users;
```

may require every shard.

Conceptually:

```text
Coordinator
   |
   +--> Shard A: partial count
   |
   +--> Shard B: partial count
   |
   +--> Shard C: partial count
   |
   v
combine results
```

This is a distributed query plan.

## Scatter/gather

A scatter/gather query sends work to many partitions and collects the answers.

Example:

```sql
SELECT COUNT(*)
FROM orders;
```

with:

```text
Shard A → 1,000,000
Shard B → 2,000,000
Shard C →   500,000
```

Coordinator calculates:

```text
3,500,000
```

This parallelism can be powerful.

But total query latency often depends heavily on the slowest participating shard.

## Distributed joins

Suppose:

```text
CUSTOMERS
```

is partitioned differently from:

```text
ORDERS.
```

A query:

```sql
SELECT c.name, o.total
FROM customers c
JOIN orders o
  ON c.customer_id = o.customer_id;
```

may require moving data between nodes.

Common approaches include:

```text
broadcast join
shuffle/repartition join
co-located join
```

## Broadcast join

Suppose:

```text
countries table = 200 rows

orders table = 10 billion rows
```

Instead of moving the huge orders table, send the small countries table to every worker:

```text
countries
   ├──> Node A
   ├──> Node B
   └──> Node C
```

Each node joins locally.

This is a broadcast join.

## Shuffle join

If both join inputs are large, rows may need to be redistributed by the join key.

```text
Customers partitioned by region
Orders partitioned by order_id
```

To join on:

```text
customer_id
```

the engine may hash both sides on `customer_id` and send corresponding rows to the same workers.

That network exchange is often called a:

```text
shuffle
```

Large distributed joins can therefore be network-intensive.

## Push computation to the data

A central principle in distributed query processing is:

> Move as little data as possible.

Instead of transferring:

```text
10 TB of raw rows
```

to one coordinator, workers should ideally perform:

```text
filters
partial aggregates
local joins
projections
```

near where the data resides.

Google Spanner's query engine, for example, can send subplans to remote servers and combine their results at a root server; it includes distributed union/apply and broadcast-hash-join operators.

## MongoDB sharding makes targeted queries important

MongoDB's `mongos` router can target a subset of shards when the query contains sufficient shard-key information.

Without suitable shard-key information, the query may need to be sent more broadly across the cluster.

This demonstrates why choosing the shard key affects not only:

```text
data distribution
```

but also:

```text
query routing
network traffic
latency.
```

## Homogeneous distributed databases

A homogeneous distributed database generally uses the same DBMS technology and compatible internal data model across the participating cluster.

Examples include a normal cluster of:

```text
Cassandra nodes

MongoDB replica/shard members

CockroachDB nodes
```

This makes internal protocols and schemas easier to coordinate.

Homogeneity does not mean every machine must have identical hardware or workload.

## Heterogeneous distributed data systems

A heterogeneous architecture may combine:

```text
PostgreSQL
Kafka
Elasticsearch
object storage
analytical warehouse
```

with data flowing between them.

Now the system must handle:

```text
schema conversion
different transaction models
different data types
different consistency semantics
different query languages
```

This is often better described as data integration/federation than as one tightly integrated distributed DBMS.

The distinction matters because one ACID transaction may not span those systems automatically.

## Relational, NoSQL, and distributed SQL

The source divides systems into:

```text
relational
NoSQL
NewSQL
```

This is useful historically, but modern products blur the categories.

A clearer classification is based on properties.

| System style | Typical characteristics |
|---|---|
| Distributed relational / SQL | SQL, schemas, transactions, joins |
| Wide-column / key-value | Partition-key-oriented access, horizontal scale |
| Document | JSON-like records, document-centric operations |
| Graph | Relationship traversal |
| Distributed SQL | Relational/SQL interface plus automated partitioning/replication across nodes |

"NewSQL" is still encountered, but distributed SQL is often the clearer modern term.

## Spanner as distributed SQL

Google describes Spanner as a distributed database providing transactional consistency, synchronous replication, relational schema, SQL, and ACID transactions.

Its design combines:

```text
automatic splitting
synchronous Paxos replication
distributed transactions
SQL query processing
strong transactional guarantees
```

It is a useful example because many theoretical topics appear in one production system.

## CockroachDB as distributed SQL

CockroachDB similarly exposes a SQL layer over a distributed transactional key-value layer.

Its data is divided into ranges, ranges are replicated across nodes, and each range uses Raft coordination.

Its SQL transaction layer then coordinates operations that can span multiple ranges.

This again demonstrates the architecture:

```text
SQL
  |
distributed transactions
  |
partitioned key-value ranges
  |
Raft-replicated copies
```

## Cassandra as a different design point

Cassandra is much more partition-key oriented.

A partitioner maps partition keys into the cluster token space. Replication determines which nodes store copies, and clients can select consistency levels appropriate to operations.

For specialized compare-and-set-style operations, Cassandra also implements Lightweight Transactions using Paxos variants. Current Cassandra configuration even exposes different Paxos implementations for LWT behavior.

So:

```text
"Cassandra is eventually consistent"
```

is far too vague to describe every operation it supports.

## MongoDB combines replica sets and sharding

A MongoDB distributed deployment may combine:

```text
mongos routers

config-server replica set

multiple data shards

each shard = replica set
```

This gives two independent scaling dimensions:

```text
add shards
→ more data/write capacity

add/adjust replicas
→ redundancy/read options
```

MongoDB also supports multi-document transactions that span sharded clusters, though cross-shard transactions have additional performance cost.

## Technology summary

| Technology | Partitioning | Replication / agreement | Transactions | Useful example of |
|---|---|---|---|---|
| Google Spanner | Automatic key-range splits | Synchronous Paxos replication | Distributed ACID transactions; 2PC across splits when needed | Distributed SQL + global coordination |
| CockroachDB | Distributed key ranges | Raft per range | Serializable distributed SQL transactions | Range-based distributed SQL |
| MongoDB | Shards selected by shard key | Replica sets, elections, write concern | Multi-document and cross-shard transactions | Explicit sharding + replication |
| Cassandra | Hash/token partitioning | Configurable replication and per-operation consistency | Normal partition operations plus Paxos-based LWT | Tunable distributed consistency |
| etcd | Not a general SQL/sharded DB model | Raft replicated log | Small transactional KV operations | Consensus and cluster metadata |

Spanner's current documentation describes splits, Paxos-based synchronous replication, and multi-split 2PC. MongoDB documents replica-set-backed shards and `mongos` routing. CockroachDB documents replicated ranges coordinated through Raft.

## A complete example: placing an order

Consider an online shop with:

```text
Customer
Inventory
Order
Payment
```

A customer places an order.

In a centralized database:

```text
BEGIN

check inventory
decrement stock
insert order
record payment

COMMIT
```

may all happen locally.

Now distribute the data:

```text
Customer shard A

Inventory shard B

Order shard C

Payment shard D
```

The same business operation can require:

```text
routing
remote reads
concurrency control
several replica quorums
distributed transaction coordination
retries
failure recovery
```

The business operation did not become logically more complicated.

The architecture made its implementation more complicated.

## Why distribution is not automatically faster

Suppose a query previously took:

```text
10 ms
```

on one machine.

After sharding, it touches ten nodes.

Now it may involve:

```text
10 RPCs
remote queues
network serialization
partial aggregation
coordinator work
```

and its latency can become dominated by the slowest participant.

Distribution improves performance when it enables useful:

```text
parallelism
locality
independent scaling
```

It can degrade performance when every operation becomes a cross-node coordination problem.

## The "single-node fast path"

Many distributed databases therefore optimize for operations contained within one partition/range.

Spanner explicitly avoids distributed 2PC when a transaction is contained in one split; multi-split transactions pay extra coordination cost.

This illustrates an important architecture rule:

> Distributed capability does not mean every transaction should be distributed.

Data modeling should try to keep frequent transactional work local when practical.

## Secondary indexes can unexpectedly make transactions distributed

Suppose one row lives in:

```text
Range A
```

but a global secondary-index entry for that row lives in:

```text
Range B.
```

Now one logical SQL insert modifies:

```text
base row
+
index row
```

across two ranges.

Spanner explicitly documents that global secondary indexes can cause a write to become a cross-split distributed transaction, adding 2PC-related latency and CPU cost.

This is a useful reminder:

> Distribution can be hidden beneath ordinary SQL.

## Security gets harder too

A distributed database may communicate across:

```text
hosts
availability zones
regions
cloud networks
```

Security therefore includes:

```text
node authentication
client authentication
authorization
TLS between components
encryption at rest
key management
network isolation
audit logs
```

It may also require controlling where particular data is legally allowed to reside.

Data placement can therefore become a compliance property, not only a performance decision.

## Observability must follow one request across nodes

Suppose one SQL query involves:

```text
router
shard A
shard B
transaction coordinator
replication leader
storage engine
```

A local log from only one machine may not explain a 5-second request.

Distributed tracing attaches a request/trace identity and follows the execution through multiple components.

Useful telemetry includes:

```text
request latency

cross-node RPC latency

replica lag

quorum failures

transaction retries

lock waits

hot shards

range movement

network errors

leader elections

query fan-out
```

Observability becomes part of database correctness engineering because partial failures can otherwise be extremely difficult to reconstruct.

## Common design mistakes

| Mistake | Why it fails |
|---|---|
| "We have three nodes, therefore we are highly available. " | Availability depends on quorum, placement, failure domains, routing, and failover |
| "Replication means backup. " | Bad writes/deletes can replicate |
| "Sharding means redundancy. " | A shard can still have only one copy |
| "Replication means write scaling. " | Single-leader replication may still serialize writes through one leader |
| "Consensus replaces transactions. " | Consensus and atomic transactions solve different problems |
| "2PC and 2PL are the same. " | One is atomic commitment; the other is concurrency control |
| "More nodes means lower latency. " | Cross-node coordination can increase latency |
| "A load balancer can route any DB request anywhere. " | Data-aware routing is usually required |
| "All distributed operations have the same consistency. " | Many systems expose operation-specific consistency/acknowledgement settings |
| "A network timeout means the write failed. " | The outcome may be unknown; the server may have committed before the response disappeared |

## The unknown-outcome problem

Suppose the client sends:

```text
INSERT order 104
```

The database commits successfully.

Then the network breaks before the client receives:

```text
SUCCESS
```

The client sees:

```text
timeout
```

What happened?

Possibilities include:

```text
transaction never reached server

transaction reached server but aborted

transaction committed but response was lost
```

The client cannot infer the outcome from the timeout alone.

This is why distributed applications often need:

```text
idempotency keys
transaction identifiers
status queries
safe retries
```

A timeout is not equivalent to rollback.

## Idempotency

Suppose a payment request contains:

```text
idempotency_key = order-104-payment
```

If the client retries after an unknown network outcome, the server can recognize:

```text
I already processed this logical operation.
```

instead of charging twice.

Idempotency is not a database consensus algorithm.

It is an application technique for making retries safer in systems where responses can disappear after work has completed.

## Choosing architecture from requirements

Start with requirements rather than technologies.

Ask:

```text
How much data?

How many reads/sec?

How many writes/sec?

Where are users?

Can reads be stale?

What data loss is acceptable?

How long may failover take?

Do transactions span entities?

Can entities be partitioned cleanly?

Which operations require linearizable behavior?

Can conflicts be merged?

How much cross-region latency is acceptable?
```

Only then choose:

```text
partitioning
replication
quorum
isolation
transaction model
database product
```

## Decision table

| Requirement | Architecture pressure |
|---|---|
| Dataset exceeds one machine | Partition/shard |
| Very high independent write throughput | Partition by write key |
| Read scaling | Add readable replicas |
| Survive machine failure | Replicate across failure domains |
| Survive region failure | Geographic replication |
| RPO near zero | Stronger synchronous acknowledgement |
| Very low write latency across regions | Avoid unnecessary global coordination |
| Strong cross-row transactions | Distributed transactional DB / careful locality |
| Cheap local transactions | Co-locate related data |
| High availability under partitions | Decide which operations may weaken consistency |
| Strong leader/metadata correctness | Consensus/quorum |
| Historical recovery | Backups/PITR, not only replication |

## The full mental model

The easiest way to understand a distributed database is as several layers.

```text
APPLICATION
    |
    v
QUERY / SQL LAYER
    |
    v
ROUTING
"where is the data?"
    |
    v
PARTITIONING
"which shard owns this key?"
    |
    v
TRANSACTION / CONCURRENCY CONTROL
"can these operations execute together?"
    |
    v
CONSENSUS / REPLICATION
"which replicated state is authoritative?"
    |
    v
STORAGE + WAL
"how is committed state persisted?"
```

A single request may pass through all of these.

## Final technology-oriented mental model

Think of several real systems:

```text
MongoDB

mongos
   ↓
shard selection
   ↓
replica set
   ↓
primary + secondaries
```

```text
Cassandra

partition key
   ↓
token range
   ↓
replicas
   ↓
chosen consistency level
```

```text
Spanner

SQL
   ↓
key range / split
   ↓
split leader
   ↓
Paxos replicas
   ↓
2PC if several splits participate
```

```text
CockroachDB

SQL
   ↓
distributed KV keys
   ↓
ranges
   ↓
Raft replicas
   ↓
distributed transaction layer
```

```text
etcd

KV request
   ↓
Raft leader
   ↓
replicated log quorum
```

These systems differ substantially, but the same questions keep appearing:

```text
Where is the data?

How is it replicated?

How does a request reach it?

How is one update ordered?

How are concurrent updates controlled?

How does a cross-partition transaction commit?

What happens when communication fails?
```

If you can answer those questions for a product, you understand much more than simply knowing whether it is called:

```text
SQL
NoSQL
NewSQL
CP
AP
shared-nothing
```

## Final summary

A distributed database is not one algorithm.

It combines several independent mechanisms:

| Problem | Typical mechanism |
|---|---|
| Data too large for one machine | Partitioning / sharding |
| Need redundant copies | Replication |
| Find the right partition | Routing / metadata |
| Copies must agree | Consensus or another replication protocol |
| Concurrent transactions conflict | Locks, MVCC, OCC, timestamps |
| Transaction touches multiple partitions | Distributed transaction coordination / 2PC variants |
| Node fails | Replication + leader election + recovery |
| Network partitions | Quorum/CAP behavior |
| Query spans nodes | Distributed query planning/execution |
| Bad data must be recovered historically | Backup + log retention / PITR |
| Operations may be retried | Idempotency + transaction retry logic |

The deepest practical lesson is:

> Distribution turns local assumptions into network protocols.

On one machine, a function call can read memory.

Across machines, that call becomes:

```text
send message
wait
possibly time out
possibly retry
possibly reach the wrong leader
possibly discover a newer configuration
possibly coordinate a quorum
```

That is why distributed databases can provide extraordinary scalability and availability, but also why their guarantees must always be understood in terms of data placement, replication, coordination, transaction scope, and failure behavior.

## References

The source notes establish the original framework of shared-nothing/shared-disk/shared-memory architecture, centralized versus decentralized coordination, replication and sharding, distributed concurrency control, 2PC/3PC, consensus, fault tolerance, CAP/PACELC, database categories, and distributed query/observability concerns.

Google Cloud's current Spanner documentation describes automatic key-range splits, synchronous Paxos-based replication, distributed query execution, pessimistic and optimistic concurrency control, serializable/repeatable-read transactions, and standard 2PC for transactions spanning multiple splits.

MongoDB's documentation describes sharded clusters built from replica-set shards, `mongos` query routing, configurable write concern, elections, and distributed transactions across sharded deployments.

CockroachDB's current architecture material describes SQL over a distributed key-value layer, key ranges replicated across nodes, and Raft-based agreement per range.

Apache Cassandra's current documentation describes partition-key/token distribution and Paxos variants for Lightweight Transactions.

etcd's current documentation exposes Raft terms and revisions in its API and documents quorum-aware membership, learners, and operational consequences of lost quorum.
