# Multi-Primary Replication

Multi-primary replication—also called multi-master or active-active replication—allows more than one database node to accept writes.

At first glance, the architecture sounds simple:

```text
                   Clients
              /       |       \
             v        v        v

          Node A    Node B    Node C
          read/write read/write read/write

             \        |        /
              +--- replication +
```

A client can write to Node A while another client writes to Node B.

But this immediately creates the central problem:

> What happens when two nodes accept changes that cannot both be part of one valid database history?

That question is what makes multi-primary replication much harder than ordinary primary–standby replication.

# 1. Compare single-primary and multi-primary

## Single-primary

```text
                writes
Clients --------------------> Primary
                                 |
                                 | replication
                                 v
                              Standby
```

There is one obvious serialization point for writes:

```text
Primary
```

Two conflicting writes ultimately meet there.

## Multi-primary

```text
Client 1 ------> Node A

Client 2 ------> Node B

Node A <------> Node B
```

Now two conflicting decisions may begin on different machines.

The replication system must decide:

```text
Can both commit?

Must one wait?

Must one abort?

Can both commit temporarily and be reconciled later?
```

Different multi-primary technologies answer those questions very differently.

# 2. "Multi-primary" describes topology, not consistency

Consider:

```text
Node A accepts writes
Node B accepts writes
```

That statement alone tells us almost nothing about correctness.

There are several possible designs.

### Asynchronous active-active

```text
A commits locally
B commits locally

changes replicated afterward
```

Conflicts may be discovered after both sides have already accepted them.

### Certification-based synchronous/virtually synchronous

```text
transaction executes locally

before final commit:
    transaction's write set participates
    in global ordering/certification

conflict
    → transaction abort
```

Galera follows this general model.

### Consensus-based distributed database

A client may submit a write to any gateway/node, but the affected partition/range is still coordinated by:

```text
a leader
or
a quorum/consensus group
```

Systems such as Spanner and CockroachDB are closer to this model.

Therefore:

> "Clients can write to any node" does not necessarily mean every node independently commits conflicting writes.

# 3. The core multi-primary conflict

Suppose:

```text
products

product_id = 42
stock = 1
```

Client A reaches Node A.

Client B reaches Node B.

Both try:

```sql
UPDATE products
SET stock = stock - 1
WHERE product_id = 42;
```

If both nodes independently commit without coordination:

```text
Node A:
stock = 0

Node B:
stock = 0
```

but logically two units may have been sold even though only one existed.

Replication later has to answer:

```text
What state is correct?

Can one write be discarded?

Was an external payment already made?

Did both clients receive SUCCESS?
```

This is much harder than merely copying rows between servers.

# 4. Another conflict: same row, different values

Initial state:

```text
customer.status = "pending"
```

During a partition or concurrent multi-writer execution:

```text
Node A:
status = "approved"

Node B:
status = "rejected"
```

Afterward the system encounters:

```text
approved
versus
rejected
```

Possible strategies include:

```text
prevent both from committing

order them and reject one

let both commit and choose one later

merge them using business logic
```

Those strategies provide very different guarantees.

# 5. Multi-primary architectures fall into different families

| Model | When conflict is resolved | Typical consequence |
|---|---|---|
| Async active-active | After independent commits | Divergence and reconciliation |
| Certification-based | Around commit/certification | One conflicting transaction aborts |
| Lock/coordinator based | Before conflicting operation completes | Waiting/blocking |
| Consensus based | Through ordered replicated decisions | Quorum/leader coordination |
| CRDT/application merge | After concurrent operations | Deterministic/domain-specific merge |

The phrase:

```text
multi-master
```

does not tell you which one is being used.

# 6. Why multi-primary can reduce geographic write latency

Suppose users are in:

```text
Berlin
Singapore
California
```

with a single writable primary in Germany.

A Singapore user must send every write across a long network path:

```text
Singapore ----------------------> Germany primary
```

A multi-primary design may allow:

```text
Singapore client → Singapore node
```

instead.

That can reduce the latency between the client and its entry point.

But there is a catch.

If the database requires global coordination before commit:

```text
Singapore node
     |
     +---- coordinate with remote nodes
```

the long-distance network latency can still appear inside the transaction commit.

Multi-primary therefore does not eliminate the speed of light.

# 7. Multi-primary does not automatically provide linear write scaling

This is one of the most important corrections to simplistic notes.

Suppose three Galera nodes exist:

```text
A
B
C
```

All three can accept writes.

But a committed write set still has to become part of the cluster-wide ordered replicated history and be applied by cluster members.

So adding:

```text
Node D
```

does not transform:

```text
10,000 writes/sec
```

into:

```text
20,000 writes/sec
```

simply because another writable endpoint exists.

In a fully replicated multi-primary cluster:

> Every replicated write ultimately creates work on every replica.

MariaDB describes Galera as multi-primary and suitable for distributing write entry points, while also noting that certification conflicts become important under high contention.

For true horizontal write scaling, partitioning/sharding may still be necessary.

# 8. Multi-primary and sharding solve different problems

Consider:

```text
3 Galera nodes
```

each containing:

```text
the entire database
```

That is replication.

Now compare:

```text
Shard A:
customers 1–1M

Shard B:
customers 1M–2M
```

That is partitioning.

With replication:

```text
same write eventually affects every copy
```

With sharding:

```text
different writes may belong to completely different subsets
```

Therefore sharding can create genuine independent write capacity in a way that adding fully replicated writable nodes may not.

# 9. Galera Cluster: the concrete model

MariaDB Galera Cluster is a useful example of certification-based, virtually synchronous multi-primary replication.

Each node can accept transactions:

```text
           MariaDB Galera Cluster

        +---------+
        | Node A  |
        | R / W   |
        +----+----+
             |
      +------+------+
      |             |
      v             v
 +---------+    +---------+
 | Node B  |    | Node C  |
 | R / W   |    | R / W   |
 +---------+    +---------+
```

But transactions do not independently become unrelated authoritative histories.

At commit time, Galera represents changes as a write set, globally orders the write set, and performs certification to determine whether it can safely commit.

MariaDB describes the process as write-set broadcasting followed by certification and application.

# 10. "Synchronous" in Galera needs qualification

Galera is commonly described as:

```text
synchronous multi-master
```

A more precise description is:

```text
virtually synchronous
```

Why?

Because these events are not literally simultaneous:

```text
transaction certified

transaction commits on origin

remote node receives write set

remote node applies write set
```

A remote node can have the write set in its receive queue before its local applier has executed it.

MariaDB explicitly notes that Galera write sets are certified at commit time but do not necessarily apply immediately on every node; they can wait in a receive queue for parallel applier threads.

Therefore:

```text
successful Galera commit
```

does not mean:

```text
every physical data page on every node changed
at exactly the same instant
```

# 11. Follow one transaction through Galera

Suppose a client connected to Node A executes:

```sql
BEGIN;

UPDATE accounts
SET balance = balance - 100
WHERE account_id = 1;

COMMIT;
```

Conceptually:

```text
1. Transaction executes locally on A.

2. Galera extracts the transaction's write set.

3. The write set enters the cluster-wide ordering protocol.

4. Certification checks whether it conflicts
   with transactions ordered before it.

5. If certification succeeds:
      transaction commits on its origin
      write set is applied on the other nodes.

6. If certification fails:
      transaction is aborted.
```

This is fundamentally different from asynchronous systems where:

```text
A commits independently

B commits independently

later:
"Oops, these disagree."
```

# 12. What is a write set?

A write set is Galera's representation of the transaction changes relevant to replication and conflict detection.

Conceptually, suppose:

```sql
UPDATE customers
SET credit_limit = 5000
WHERE customer_id = 10;
```

The write set contains information corresponding to the transaction's modifications and the keys required for certification.

Galera replicates that write set through the cluster rather than sending:

```text
"Please run this SQL text."
```

as ordinary statement-based replication would.

This is why Galera requires row-oriented replication behavior for supported clustered operation.

# 13. Certification: the heart of Galera

Suppose two concurrent transactions originate on different nodes.

### Transaction T1 on Node A

```sql
UPDATE products
SET price = 100
WHERE id = 42;
```

### Transaction T2 on Node B

```sql
UPDATE products
SET price = 120
WHERE id = 42;
```

Both may perform local work optimistically.

Around commit, their write sets enter global ordering.

Suppose ordering places T1 first:

```text
T1 → T2
```

T1's write set certifies.

When T2 is certified, Galera discovers that its relevant write set conflicts with an earlier transaction in the certification window.

The outcome can be:

```text
T1 commits

T2 aborts
```

rather than:

```text
A keeps 100
B keeps 120
and someone merges later.
```

That difference is central to Galera.

# 14. The source's "later GTID wins" model is misleading

The source currently describes conflict behavior approximately as:

```text
later GTID wins
```

with the loser rolled back.

That is not the right mental model.

Galera uses:

```text
global transaction ordering
+
write-set certification
```

to determine whether a transaction remains valid.

A transaction ordered after a conflicting transaction can fail certification.

The significant concept is not:

```text
largest GTID wins
```

like last-write-wins conflict reconciliation.

It is:

> The write set must certify against the already ordered conflicting transaction history.

MariaDB documents certification as checking incoming write sets against concurrently committed transactions; conflicts cause a transaction to be aborted rather than merged through a timestamp/GTID winner rule.

# 15. This is optimistic concurrency

Galera's model is broadly optimistic.

Transactions can execute locally without taking a distributed lock on every remote node first.

Conceptually:

```text
Node A                  Node B

execute T1              execute T2
locally                  locally
   |                        |
   +------- commit ---------+
              |
              v
        global ordering
              |
              v
         certification
```

If there was no conflict:

```text
commit
```

If the certification check discovers an incompatible concurrent transaction:

```text
abort/retry
```

This trades:

```text
less distributed locking during execution
```

for:

```text
possible transaction abort at commit time
```

# 16. Local execution means commit can still fail

This produces an important application rule.

Suppose application code does:

```text
BEGIN

UPDATE ...
UPDATE ...

COMMIT
```

All `UPDATE`s may appear to execute successfully.

Then:

```text
COMMIT
```

can fail because certification discovers a conflict.

Therefore application code must treat:

```text
COMMIT
```

as an operation that can fail due to concurrency.

MariaDB's Galera guidance explicitly advises applications to check for errors after `COMMIT`.

# 17. Why retries are necessary

Suppose Node A and Node B repeatedly update the same customer.

One transaction loses certification.

The application can:

```text
rollback
retry complete transaction
```

But it must rerun the decision from the beginning.

Not:

```text
retry only final UPDATE
```

because earlier reads may now be outdated.

The familiar safe pattern is:

```text
BEGIN

read current state
make decision
perform writes

COMMIT
```

On retry:

```text
BEGIN

read current state again
make decision again
perform writes again

COMMIT
```

# 18. Error 1213 can represent Galera conflict behavior

MariaDB exposes some Galera concurrency conflicts using familiar transactional errors, including the deadlock class.

`wsrep_retry_autocommit` exists specifically to retry autocommit statements automatically for failures including certification failure and high-priority aborts.

Application code should therefore already have a deliberate retry strategy for retryable transactional failures.

However:

```text
every error 1213
```

should not automatically be interpreted as:

```text
classic local InnoDB lock-cycle deadlock
```

In a Galera environment, the cluster's certification/concurrency mechanisms can also be involved.

# 19. Hot rows are especially expensive in multi-primary Galera

Suppose every checkout performs:

```sql
UPDATE global_counter
SET value = value + 1
WHERE id = 1;
```

Clients send traffic across:

```text
Node A
Node B
Node C
```

All transactions update the same row.

The cluster continually encounters transactions whose write sets conflict.

Result:

```text
high certification failure rate
+
retries
+
lower throughput
```

The fact that there are three writable nodes does not help if all writers contend on one logical record.

This is why workload shape matters more than the phrase:

```text
multi-master
```

# 20. Good multi-primary workloads

Galera tends to behave much better when concurrent transactions modify largely independent data.

For example:

```text
Node A clients:
customers 1–1000

Node B clients:
customers 1001–2000
```

even though both nodes technically accept all writes.

Low contention means fewer overlapping write sets.

A difficult workload is:

```text
every node repeatedly updates
the same inventory row
the same counter
the same account
```

because certification conflicts become common.

# 21. Primary keys matter

Efficient row identification is especially important for certification-based replication.

A good table design includes a stable primary key:

```sql
CREATE TABLE orders (
    order_id BIGINT PRIMARY KEY,
    ...
);
```

rather than relying on rows without useful unique identity.

Current Galera configuration even provides a `REQUIRED_PRIMARY_KEY` strict mode option for deployments that want to enforce stronger table discipline.

Primary keys are not merely an ORM convention here.

They help the distributed system identify conflicting row changes efficiently.

# 22. AUTO_INCREMENT becomes interesting in multi-primary systems

Suppose Node A and Node B both execute:

```sql
INSERT INTO orders(...)
VALUES (...);
```

and both independently generate:

```text
order_id = 100
```

That would create a key conflict.

Galera provides:

```text
wsrep_auto_increment_control
```

which dynamically adjusts:

```text
auto_increment_increment
auto_increment_offset
```

according to cluster membership.

For three nodes, values might conceptually be interleaved:

```text
Node A:
1, 4, 7, 10, ...

Node B:
2, 5, 8, 11, ...

Node C:
3, 6, 9, 12, ...
```

MariaDB documents this automatic adjustment and enables it by default.

# 23. Do not expect contiguous AUTO_INCREMENT values

The consequence is:

```text
AUTO_INCREMENT
```

should be interpreted as:

```text
generate a convenient unique identifier
```

not:

```text
generate an uninterrupted sequence
```

A Galera cluster can produce:

```text
1
4
7
...
```

from one node because IDs are being coordinated to avoid clashes with values generated elsewhere.

MariaDB explicitly warns that Galera auto-increment sequences can contain gaps.

If business logic depends on:

```text
invoice 100
invoice 101
invoice 102
```

with no gaps, ordinary `AUTO_INCREMENT` is the wrong business-sequencing mechanism.

# 24. UUIDs do not solve transaction conflicts

Using:

```text
UUID
```

for identifiers can eliminate certain key-generation collisions.

It does not solve:

```text
two transactions modify customer 42
```

or:

```text
two transactions reserve the same seat
```

Those are business-data conflicts, not identifier-generation conflicts.

So:

```text
UUID
```

can solve:

```text
PK allocation
```

without solving:

```text
distributed write contention.
```

# 25. Quorum is what prevents split brain in Galera

Suppose a three-node cluster is:

```text
A ----- B ----- C
```

The cluster relies on quorum.

Now the network partitions:

```text
A       X       B ----- C
```

The B/C side has:

```text
2 of 3 votes
```

and forms the majority Primary Component.

A has:

```text
1 of 3
```

and does not.

The minority side cannot simply continue independently as another writable cluster.

MariaDB documents quorum as requiring more than half of the relevant voting membership; nodes outside the Primary Component stop ordinary query/transaction processing to prevent split brain.

# 26. "Primary Component" does not mean primary database node

Terminology is confusing here.

Galera is:

```text
multi-primary
```

meaning multiple nodes can accept writes.

But it also has a:

```text
Primary Component
```

The Primary Component is the connected quorum group that is authorized to process normal cluster operations.

It is not:

```text
the one primary writer
```

A healthy three-node Primary Component can contain:

```text
A
B
C
```

and all three can remain writable.

# 27. A three-node quorum example

Initial cluster:

```text
A ----- B ----- C

wsrep_cluster_size = 3
wsrep_cluster_status = Primary
```

Node C crashes:

```text
A ----- B      C X
```

A/B still have:

```text
2 / 3
```

and retain quorum.

Writes can continue.

Now B also disappears:

```text
A       B X    C X
```

A has:

```text
1 / 3
```

and cannot safely form the previous cluster's majority by itself.

The correct behavior is to stop ordinary cluster writes rather than invent an independent authoritative history.

# 28. Why two-node clusters are awkward

Suppose the cluster contains only:

```text
A
B
```

They lose communication:

```text
A       X       B
```

Each sees:

```text
1 of 2
```

Neither has a majority.

Allowing both to continue would create split brain.

Therefore odd-sized voting groups such as:

```text
3
5
```

are often easier to make fault tolerant.

This does not mean:

```text
every deployment needs five database servers
```

but quorum math must be considered deliberately.

# 29. Quorum solves split-brain authority, not conflict hot spots

Quorum answers:

```text
Which connected component is allowed to operate?
```

Certification answers:

```text
Can this particular transaction coexist
with concurrently ordered transactions?
```

These are different problems.

You can have:

```text
healthy quorum
```

and still experience:

```text
many certification conflicts
```

because applications repeatedly update the same rows.

# 30. Node failure in Galera is not ordinary "promotion"

With primary–standby:

```text
Primary fails
→ promote standby
```

With healthy Galera:

```text
Node A fails

Node B and C already accept writes
```

There is no database-role promotion equivalent to turning a read-only standby into a writer.

What still has to happen is:

```text
remove failed endpoint from client routing
```

or have a proxy notice automatically.

For this reason, HA deployments commonly put:

```text
MariaDB MaxScale
HAProxy
ProxySQL
or another routing layer
```

in front of the database nodes.

MariaDB specifically positions MaxScale alongside Galera for connection routing and HA.

# 31. Client routing still matters

Suppose clients connect directly to:

```text
db1.example.com
```

and Node 1 crashes.

The fact that Nodes 2 and 3 are healthy does not magically rewrite the application's connection string.

A production architecture needs:

```text
load balancer
proxy
service discovery
DNS endpoint
or application-aware node selection
```

For example:

```text
Application
     |
     v
+----------+
| MaxScale |
+-----+----+
      |
 +----+----+
 |         |
 v         v
Node B    Node C
```

Multi-primary storage does not remove the need for connection routing.

# 32. Read consistency is subtler than "all nodes are synchronous"

Suppose a transaction commits through Node A.

Node B already knows the ordered write set but its local applier has not yet applied it.

A query arrives at B immediately.

Without an explicit causal synchronization requirement, the read can encounter a node that is briefly behind in local apply.

Galera therefore provides:

```text
wsrep_sync_wait
```

for operations requiring a causality check.

MariaDB documents that `wsrep_sync_wait` waits until the local node catches up with cluster updates before executing selected operation types, at the cost of additional read latency.

# 33. Concrete read-after-write example

Client writes through A:

```sql
INSERT INTO orders(id, ...)
VALUES (104, ...);

COMMIT;
```

Then immediately connects to B:

```sql
SELECT *
FROM orders
WHERE id = 104;
```

For a critical causal read, the session can use:

```sql
SET SESSION wsrep_sync_wait = 1;

SELECT *
FROM orders
WHERE id = 104;
```

The read waits for the local node to be synchronized sufficiently before execution.

This is another reason:

> "synchronous cluster" does not mean application code can ignore read-consistency semantics.

# 34. Why Galera can still have an apply queue

Suppose transactions arrive faster than one node can apply them.

That node develops:

```text
receive queue

write set 101
write set 102
write set 103
write set 104
...
```

The transactions already belong to the global cluster history.

The problem is local application speed.

Galera uses parallel applier threads to process write sets that can safely be applied concurrently. MariaDB exposes this through Galera applier-thread configuration and receive-queue monitoring.

# 35. Flow Control: the slowest node can affect the cluster

Suppose:

```text
Node A:
fast

Node B:
fast

Node C:
slow disk
```

C's receive queue grows:

```text
C queue:

101
102
103
104
105
106
...
```

Galera cannot let that queue grow without bound.

When it crosses configured limits, C can trigger Flow Control.

Conceptually:

```text
C:
"I'm falling behind."

        |
        v

cluster pauses/throttles new replication work

        |
        v

C catches up

        |
        v

cluster resumes
```

MariaDB documents Flow Control as an automatic cluster-wide throttling mechanism triggered when a node's receive queue grows too large.

# 36. One slow node can therefore reduce cluster write throughput

This is a crucial performance property.

Suppose:

```text
A can apply 10k writes/sec
B can apply 10k writes/sec
C can apply 2k writes/sec
```

If the cluster has to prevent C from falling indefinitely behind, C can become a limiting factor.

Therefore:

```text
add a cheap slow third node
```

can actually hurt cluster performance.

This is very different from simplistic reasoning:

```text
more nodes
=
more throughput
```

In replicated systems, the slowest required participant can matter greatly.

# 37. Monitor Flow Control

Important Galera metrics include:

```text
wsrep_local_recv_queue
wsrep_local_recv_queue_avg
wsrep_flow_control_paused
wsrep_flow_control_sent
wsrep_flow_control_recv
```

A persistently increasing:

```text
wsrep_local_recv_queue_avg
```

suggests the node cannot apply write sets as fast as they arrive.

A high:

```text
wsrep_flow_control_paused
```

means the cluster is spending substantial time throttled by Flow Control.

MariaDB explicitly recommends these metrics for identifying cluster bottlenecks.

# 38. State transfer: how does a node catch up?

Suppose Node C has been offline.

During that time:

```text
cluster executes transactions
1000 through 5000
```

C returns having applied only through:

```text
1000
```

It must catch up before becoming a normal synchronized member.

Galera has two important mechanisms:

```text
IST
Incremental State Transfer

SST
State Snapshot Transfer
```

# 39. IST: Incremental State Transfer

If a donor still has the missing write sets in its GCache, it can send only the missing history.

Conceptually:

```text
C has through:
1000

Donor GCache contains:
1001 ... 5000

        |
        v

send 1001 ... 5000
```

C applies them and catches up.

MariaDB describes IST as the preferred, faster mechanism when the donor's GCache contains the write sets required by the returning node.

# 40. GCache

Galera's GCache retains recent write sets primarily so nodes that briefly disconnect can catch up through IST.

Conceptually:

```text
current seqno
      |
      v
----------------------------------->
      ^
      |
   GCache keeps
   recent history
```

A larger useful GCache increases the outage window from which a returning node may recover through IST instead of requiring a full snapshot.

But:

```text
GCache
```

is not:

```text
a permanent historical backup.
```

It is recovery/catch-up state.

# 41. SST: State Snapshot Transfer

If the required history is no longer available:

```text
C needs transaction 1001

donor GCache begins at 3000
```

IST is impossible.

The node needs a complete state transfer:

```text
SST
```

Conceptually:

```text
Donor
  |
  | complete database state
  v
Joiner
```

After receiving the state, the joiner then processes newer write sets and eventually becomes synchronized.

MariaDB documents SST as a full dataset copy used when incremental catch-up is not sufficient.

# 42. IST versus SST

| Property | IST | SST |
|---|---|---|
| Transfers | Missing write sets | Full database state |
| Usually faster | Yes | No |
| Requires relevant GCache history | Yes | No |
| Data volume | Incremental | Potentially entire dataset |
| Typical use | Short outage | New node / long outage |
| Donor impact | Usually small | Depends heavily on SST method |

This distinction is much more important operationally than merely saying:

```text
"joining nodes replicate automatically."
```

# 43. SST method matters

The source config uses:

```ini
wsrep_sst_method = rsync
```

and describes:

```text
mariabackup is faster for TB-scale
```

but that hides a more important operational distinction.

Different SST methods have different:

```text
donor blocking behavior
performance
security characteristics
tooling requirements
```

MariaDB documents SST methods as separate provisioning mechanisms and notes that donor blocking depends on the chosen method.

For current production systems, choose an SST method from current MariaDB documentation rather than treating `rsync` as a default recommendation.

# 44. The source's `wsrep_sst_auth` example is also misleading for `rsync`

The source combines:

```ini
wsrep_sst_method = rsync
wsrep_sst_auth = sstuser:...
```

and then creates an SST account.

Current MariaDB documentation says `wsrep_sst_auth` is unused when the SST method is `rsync`; authentication requirements depend on the SST mechanism.

So the correct documentation pattern is:

> Pick the SST mechanism first, then follow that mechanism's current authentication and TLS requirements.

Do not teach one generic SST user recipe as universal.

# 45. Quorum loss and full-cluster recovery

Suppose all three nodes shut down.

There is no surviving Primary Component.

You must not simply start random nodes with:

```text
--wsrep-new-cluster
```

until one works.

You first need to determine which node contains the most advanced safe cluster state.

MariaDB's recovery procedure explicitly requires identifying the most advanced node and bootstrapping the new Primary Component from the appropriate state.

Bootstrapping is a cluster-authority operation, not merely a startup convenience.

# 46. Why careless bootstrapping is dangerous

Imagine:

```text
Node A applied through seqno 10,000

Node B applied through seqno 9,950
```

After a full outage, an operator incorrectly bootstraps B as a brand-new authoritative cluster.

The cluster may now start from an older state and effectively discard transactions that existed on A.

The safe question is:

```text
Which node contains the latest recoverable cluster state?
```

not:

```text
Which server boots fastest?
```

# 47. Monitoring cluster health

A basic health check should include:

```sql
SHOW GLOBAL STATUS LIKE 'wsrep_cluster_size';
SHOW GLOBAL STATUS LIKE 'wsrep_cluster_status';
SHOW GLOBAL STATUS LIKE 'wsrep_local_state_comment';
SHOW GLOBAL STATUS LIKE 'wsrep_ready';
```

Healthy values commonly include:

```text
wsrep_cluster_status = Primary

wsrep_local_state_comment = Synced

wsrep_ready = ON
```

The expected:

```text
wsrep_cluster_size
```

depends on how many nodes should currently be members.

MariaDB documents these status variables as central quorum and node-health indicators.

# 48. Do not monitor only cluster size

Suppose:

```text
wsrep_cluster_size = 3
```

That tells you three nodes are present in the component.

It does not alone tell you:

```text
Are they Synced?

Is Flow Control constantly active?

Are receive queues growing?

Are certification conflicts exploding?

Is one node repeatedly transferring state?
```

A healthy cluster needs several categories of metrics.

# 49. Practical monitoring table

| Question | Useful signal |
|---|---|
| Do we have quorum? | `wsrep_cluster_status` |
| How many nodes are members? | `wsrep_cluster_size` |
| Is this node synchronized? | `wsrep_local_state_comment` |
| Can the node accept normal application work? | `wsrep_ready` |
| Is apply falling behind? | `wsrep_local_recv_queue_avg` |
| Is network sending backlogged? | `wsrep_local_send_queue_avg` |
| Is Flow Control throttling us? | `wsrep_flow_control_paused` |
| Is this node causing pauses? | `wsrep_flow_control_sent` |
| How much parallel apply may be possible? | `wsrep_cert_deps_distance` |
| Are application conflicts occurring? | certification/BF-abort metrics and logs |

MariaDB's monitoring documentation specifically recommends receive/send queues, Flow Control metrics, and certification-dependency information for cluster diagnosis.

# 50. A corrected minimal MariaDB Galera configuration

For a lab, a basic configuration may look conceptually like:

```ini
[mariadb]

bind-address = 0.0.0.0

default_storage_engine = InnoDB
binlog_format = ROW
innodb_autoinc_lock_mode = 2

wsrep_on = ON
wsrep_provider = /path/to/libgalera_smm.so

wsrep_cluster_name = example_cluster
wsrep_cluster_address = gcomm://db1,db2,db3

wsrep_node_name = db1
wsrep_node_address = 10.0.0.20
```

The node-specific values change on every host.

MariaDB's current Galera deployment documentation continues to identify `ROW`, InnoDB, `wsrep_on`, provider configuration, and cluster/node addressing as core configuration.

Do not blindly copy provider paths: they differ across distributions and package layouts.

# 51. Current product naming matters

The source describes:

```text
MySQL / MariaDB + Galera
```

as though this were one interchangeable current deployment.

That should now be qualified.

In 2025 MariaDB acquired Codership/Galera, and in September 2026 MariaDB announced the end of the separately distributed MySQL Galera Cluster line while continuing Galera integration in MariaDB.

So for current notes:

> Use MariaDB Galera Cluster as the concrete Galera implementation unless you are deliberately documenting another supported Galera-based product such as a vendor-specific distribution.

Configuration commands should come from the documentation for that exact product/version.

# 52. Do not use "rule of thumb = threads equal CPU cores" blindly

The source suggests:

```ini
wsrep_slave_threads = 4
```

with a CPU-based rule.

Parallel apply capacity depends on:

```text
workload dependency structure
CPU
I/O
locking
write-set parallelism
```

MariaDB exposes:

```text
wsrep_cert_deps_distance
```

specifically as an indicator of potential parallel application.

So tune applier threads from:

```text
observed receive queues
Flow Control
CPU
wsrep_cert_deps_distance
```

rather than a universal core-count formula.

# 53. `wsrep_slave_threads` versus `wsrep_applier_threads`

Terminology differs across product lines and versions.

MariaDB's current Galera documentation still exposes:

```text
wsrep_slave_threads
```

as the variable controlling parallel write-set appliers.

The MySQL-wsrep branch renamed several legacy `slave` names, including:

```text
wsrep_slave_threads
→
wsrep_applier_threads
```

in its own newer releases.

Therefore:

> Always use the variable documented by the exact MariaDB/MySQL-wsrep/Percona version being operated.

Do not copy Galera settings between products merely because all of them use Galera technology.

# 54. `innodb_autoinc_lock_mode = 2`

Current MariaDB Galera deployment documentation still includes:

```ini
innodb_autoinc_lock_mode = 2
```

alongside row binary logging and InnoDB.

But it solves a specific database-engine behavior.

It does not replace:

```text
wsrep_auto_increment_control
```

which addresses cross-node auto-increment allocation.

These settings live at different layers.

# 55. Large transactions are costly

Consider:

```sql
UPDATE events
SET archived = 1
WHERE event_date < '2020-01-01';
```

that modifies:

```text
10 million rows
```

A huge transaction creates a huge distributed write set and long apply/certification consequences.

Effects may include:

```text
large memory/network usage
slow apply
Flow Control
long conflict windows
large rollback cost
```

MariaDB's Flow Control documentation recommends breaking large write operations into smaller batches when they cause write-set/applier pressure.

# 56. DDL is also distributed coordination

Suppose:

```sql
ALTER TABLE customers
ADD COLUMN preferred_language VARCHAR(10);
```

A schema change cannot safely appear on one node while the others continue processing incompatible write sets indefinitely.

Galera therefore has schema-upgrade mechanisms such as:

```text
TOI — Total Order Isolation

RSU — Rolling Schema Upgrade
```

MariaDB documents TOI as the default mode, ordering DDL consistently with cluster transactions; RSU instead performs the DDL locally while the node is desynchronized and requires careful compatibility handling.

DDL therefore deserves its own deployment plan.

# 57. Multi-primary does not mean "no failover planning"

Galera avoids the classic:

```text
promote read-only standby
```

step while quorum remains healthy.

But applications still need:

```text
health detection
routing
quorum awareness
full-cluster recovery
node rejoin procedures
```

and operators still need plans for:

```text
one node failure

majority loss

entire cluster shutdown

network partition

state transfer

data-center failure
```

The failure model changes.

It does not disappear.

# 58. Three-node failure table

| Event | A | B | C | Expected cluster behavior |
|---|---|---|---|---|
| Normal | up | up | up | 3-node Primary Component |
| C fails | up | up | down | A/B retain majority |
| B and C fail | up | down | down | A loses quorum |
| A isolated, B↔C connected | isolated | up | up | B/C Primary Component |
| A/B isolated from C | up | up | isolated | A/B Primary Component |
| All stop | down | down | down | Manual recovery/bootstrap required |

The critical question is not:

```text
"Is one node still alive?"
```

It is:

```text
"Does the surviving component have authoritative quorum?"
```

# 59. Geographically distributed Galera needs caution

A tempting topology is:

```text
Berlin
Singapore
Virginia
```

all in one Galera cluster.

This gives:

```text
local writable endpoints
```

but cluster coordination must still travel across the WAN.

Effects include:

```text
higher certification/commit latency

higher probability of Flow Control interaction

greater sensitivity to network jitter

more complex quorum placement
```

MariaDB documentation notes WAN-specific provider considerations, and current Enterprise materials position geographic Galera deployment carefully rather than treating WAN latency as free.

For some applications, another architecture—regional clusters plus asynchronous inter-region replication, for example—may fit better.

# 60. Compare Galera with asynchronous active-active replication

Imagine two asynchronous writable sites:

```text
Site A                    Site B

write X                   write Y
commit                     commit

       replicate later
```

A conflict can exist after both applications already received success.

That requires:

```text
conflict reconciliation
```

Galera instead tries to maintain a single cluster-wide ordered history:

```text
T1
T2
T3
...
```

and rejects transactions that fail certification.

So Galera conflict management is closer to:

```text
prevent incompatible committed histories
```

than:

```text
allow divergent histories
then merge them.
```

# 61. Compare Galera with last-write-wins

Last-write-wins might do:

```text
A: status = approved, timestamp 100

B: status = rejected, timestamp 101

result:
rejected
```

Both writes may already have happened.

One simply wins reconciliation.

Galera's certification model instead resembles:

```text
T1 ordered first
T1 certifies

T2 conflicts with T1
T2 aborts
```

The losing application sees a transaction failure and has an opportunity to retry under the new state.

These are fundamentally different semantics.

# 62. Compare Galera with consensus-based distributed SQL

Now consider a system such as CockroachDB or Spanner.

A client may send SQL to multiple entry nodes.

But for each replicated range:

```text
writes are ordered through
a Raft/Paxos replica group
```

The system may still use distributed transaction coordination across several ranges.

That architecture is not normally described as:

```text
every replica independently acts as master
```

even though clients can write through many database endpoints.

This is why:

```text
multi-primary endpoint
```

and:

```text
independent master
```

should not be treated as synonyms.

# 63. Conflict avoidance can be better than conflict retry

Suppose customers are geographically assigned:

```text
European customer records
→ normally written through Node A

US customer records
→ normally written through Node B
```

Both nodes remain capable of writing everything.

But normal routing reduces the probability that two nodes concurrently update the same logical record.

This strategy is sometimes called:

```text
writer affinity
```

or:

```text
home-region ownership
```

depending on the architecture.

Multi-primary capability can exist while application routing deliberately reduces multi-writer contention.

# 64. External side effects and Galera retries

Suppose:

```text
BEGIN

update order

send payment API request

update inventory

COMMIT
```

Certification fails at `COMMIT`.

Database state rolls back.

The payment API does not.

A retry can charge again.

This is why distributed transaction retry safety still requires:

```text
idempotency
outbox patterns
careful side-effect boundaries
```

Galera's ability to abort a transaction at commit makes this especially important.

# 65. Do not confuse replication conflict with business invariant safety

Suppose two transactions modify different rows:

```text
T1:
doctor A off call

T2:
doctor B off call
```

Business rule:

```text
at least one doctor must remain on call
```

The write sets may touch different rows.

Simple row-level write-set conflict detection does not automatically mean:

```text
cross-row business invariant is safe
```

You still need appropriate:

```text
constraints
locking
transaction isolation
application protocol
```

for such invariants.

Multi-primary replication does not replace transaction-isolation reasoning.

# 66. Multi-primary and CAP

Suppose a three-node Galera cluster partitions:

```text
A       X       B ----- C
```

Could both sides stay writable?

If yes:

```text
A could commit one history

B/C could commit another
```

and split brain would result.

Galera instead allows the majority Primary Component to continue while the minority cannot perform normal clustered work.

That is a consistency-first response to the partition.

It illustrates CAP concretely:

```text
preserve one authoritative cluster history
→ sacrifice write availability on minority side
```

# 67. Multi-primary therefore does not mean "available everywhere"

This misconception is especially common:

```text
every node is writable
therefore
every node can always keep accepting writes
```

No.

A healthy multi-primary node that has lost quorum may be intentionally prevented from accepting normal writes.

That is a safety feature.

Availability must always be discussed together with:

```text
network partition
quorum
membership
consistency guarantee
```

# 68. Practical architecture comparison

| Architecture | Writers | Conflict point | Partition behavior | Typical strength |
|---|---|---|---|---|
| PostgreSQL primary/standby | One primary | Primary | Failover required | Simple authoritative write path |
| Async active-active replication | Several | Reconciliation after commit | Both sides may continue | Geographic write availability |
| MariaDB Galera | Several entry writers | Global order + certification | Majority Primary Component continues | Active-active HA with conflict aborts |
| MySQL/InnoDB Cluster | Client may use topology-aware endpoints | Group Replication / majority coordination | Majority requirements | MySQL HA/consensus-style group replication |
| CockroachDB | Many SQL gateways | Raft + transaction layer | Quorum per range | Distributed serializable SQL |
| Spanner | Many entry points | Paxos + distributed transactions | Quorum/replica configuration | Global distributed SQL |

Do not choose among these using only:

```text
"supports multi-master: yes/no"
```

The mechanisms and guarantees differ substantially.

# 69. What multi-primary replication is good at

It can be a strong fit when you need:

```text
multiple writable connection endpoints

fast failover without promoting a read-only replica

high availability inside a low-latency cluster

maintenance while other writable nodes remain online

geographic/localized write entry where coordination latency is acceptable
```

and the workload has manageable write contention.

# 70. When it becomes difficult

Warning signs include:

```text
very high write contention on the same rows

large transactions

high-latency WAN between cluster nodes

nodes with very different performance

requirements to remain writable on both sides
of a network partition

applications that cannot safely retry transactions

huge state transfers

poor primary-key design
```

Those are architectural issues, not merely tuning problems.

# 71. Common misconceptions

| Claim | Better explanation |
|---|---|
| "Every master commits independently. " | Not in Galera; writes participate in cluster ordering/certification |
| "Synchronous means applied simultaneously. " | Remote application can lag behind certification/order |
| "More writable nodes means linear write scaling. " | Fully replicated writes still create work across the cluster |
| "Galera uses last-write-wins. " | It normally aborts transactions that fail certification |
| "A larger GTID wins a conflict. " | Certification is based on globally ordered conflicting write sets |
| "Three writers mean no failover problem. " | Client routing and quorum still matter |
| "One surviving node can always continue. " | Not if it lacks quorum |
| "SST and IST are equivalent. " | SST copies full state; IST transfers missing write sets |
| "`rsync` needs the generic SST user shown in every example. " | SST authentication requirements depend on the method |
| "A synchronous cluster cannot return a stale local read. " | Local apply can lag; use causal synchronization when required |
| "UUIDs prevent multi-primary conflicts. " | They prevent some ID collisions, not business-data conflicts |
| "Multi-primary replaces sharding. " | Replication and partitioning solve different problems |

# 72. Recommended Galera test plan

Do not validate a cluster only with:

```text
INSERT on A
SELECT on B
```

Test actual failure and conflict behavior.

| Test | What to verify |
|---|---|
| Write on each node | Every intended endpoint is writable |
| Cross-node read | Normal replication works |
| Immediate critical read | Behavior with/without `wsrep_sync_wait` |
| Same-row concurrent update | One transaction fails/retries as expected |
| Node failure | Remaining majority keeps operating |
| Network isolation of one node | Minority leaves normal Primary operation |
| Two-node loss in 3-node cluster | Remaining minority stops safely |
| Node rejoin shortly afterward | IST occurs when GCache permits |
| Node rejoin after long outage | SST occurs correctly |
| Slow one node deliberately | Flow Control behavior is visible |
| Full cluster stop | Recovery procedure identifies correct bootstrap node |
| Proxy failure | Client routing layer itself is redundant |
| Large transaction | Observe write-set and Flow Control impact |

Testing the happy path alone does not validate HA.

# 73. A safer basic deployment sequence

For a fresh three-node MariaDB Galera lab:

```text
1. Install the same supported MariaDB/Galera version
   on all nodes.

2. Configure:
      InnoDB
      ROW binlog format
      wsrep provider
      cluster name
      cluster member addresses
      node identity

3. Configure network/TLS/firewall rules.

4. Bootstrap exactly one initial cluster node.

5. Verify:
      wsrep_cluster_status = Primary
      wsrep_cluster_size = 1

6. Start Node 2 normally.

7. Let it complete IST/SST as required.

8. Start Node 3 normally.

9. Verify:
      cluster size
      Synced states
      wsrep_ready
      queues and Flow Control

10. Add an HA-aware client routing layer.

11. Test failures before calling the system production-ready.
```

The current MariaDB quick-start documentation follows this overall bootstrap-one-then-join-others model.

# 74. Do not bootstrap ordinary joining nodes

This command:

```bash
galera_new_cluster
```

means:

```text
create a new Primary Component
```

not:

```text
start MariaDB in Galera mode.
```

Use it for the deliberate initial bootstrap or appropriate full-cluster recovery case.

Normal joining nodes should start normally and connect to the existing Primary Component.

Careless repeated use can create precisely the split histories quorum is designed to prevent.

# 75. Security considerations

A production cluster should secure:

```text
client traffic
cluster replication traffic
IST transfers
SST transfers
administrative access
```

The source lists ports such as:

```text
3306
4567
4568
4444
```

which correspond to typical client/Galera/state-transfer purposes, but exact bindings and security rules must follow the deployment.

Current MariaDB Galera documentation also supports encrypted cluster and state-transfer traffic; current 2026 maintenance releases tightened behavior so misconfigured SST encryption fails instead of silently falling back to plaintext in affected methods.

Do not simply expose Galera ports broadly.

# 76. Technology summary: what actually happens to a write

| System | Entry point | How one authoritative outcome is reached |
|---|---|---|
| PostgreSQL primary/standby | Primary | Primary commits; WAL replicated outward |
| MariaDB Galera | Any synced Primary-Component node | Write-set global ordering + certification |
| Async active-active DB | Multiple nodes | Independent commits + later conflict resolution |
| CockroachDB | Any SQL gateway | Transaction layer + Raft ranges |
| Spanner | Frontend/server | Distributed transaction + Paxos-replicated splits |
| Cassandra normal mutation | Coordinator | Replica consistency level + timestamp/version rules |
| etcd | Cluster member/client endpoint | Raft leader/quorum replicated log |

The user-visible statement:

```text
"I can send a write to any node"
```

can therefore hide radically different distributed protocols.

# 77. Final mental model

Do not memorize multi-primary replication as:

```text
many masters
+
copy every write everywhere
```

Use this sequence instead:

```text
CLIENT SENDS WRITE TO ANY WRITABLE NODE
               |
               v
       TRANSACTION EXECUTES
               |
               v
          WRITE SET
               |
               v
       GLOBAL ORDERING
               |
               v
        CERTIFICATION
          /       \
         /         \
   conflict       safe
      |             |
      v             v
   ABORT          COMMIT
                     |
                     v
             REMOTE APPLY QUEUES
                     |
                     v
              OTHER NODES APPLY
```

Alongside that is a separate membership path:

```text
CLUSTER MEMBERSHIP
       |
       v
     QUORUM
       |
       v
PRIMARY COMPONENT
       |
       +---- majority side may operate
       |
       +---- minority side stops
```

And a separate recovery path:

```text
NODE REJOINS
    |
    +--> required history in GCache?
            |
       +----+----+
       |         |
      YES       NO
       |         |
      IST       SST
```

Those three flows explain most of Galera:

```text
transaction correctness
cluster safety
node recovery
```

# 78. The question to ask in any multi-primary system

Do not ask only:

> "Can every node accept writes? "

Ask:

> "If two nodes receive conflicting writes at the same time, exactly when is the conflict discovered, which operation is allowed to succeed, what does the losing client observe, and what happens if those nodes cannot communicate? "

For Galera, the answer is approximately:

```text
transactions execute optimistically on writable nodes

write sets enter one cluster-wide ordered history

conflicting transactions can fail certification

a majority Primary Component preserves authority
during partitions

lagging/rejoining nodes recover through IST or SST

slow apply can throttle the whole cluster through Flow Control
```

Once those mechanisms are understood, "multi-master" stops being a marketing label and becomes a concrete concurrency and availability architecture.

# References

The source notes provide the original multi-master topology, motivations, conflict-resolution discussion, Galera configuration, SST setup, bootstrapping process, and certification example.

MariaDB's current Galera documentation describes multi-primary write-set replication, global ordering/certification, and the fact that write sets can be queued and applied after certification rather than physically applied simultaneously.

MariaDB's quorum documentation describes the Primary Component, majority requirement, minority-side protection against split brain, and the need to bootstrap from the most advanced state after full quorum loss.

MariaDB's state-transfer documentation distinguishes Incremental State Transfer using retained GCache history from full State Snapshot Transfer when the required history is unavailable.

MariaDB's Flow Control documentation describes cluster throttling when a node's receive queue grows, and its monitoring documentation identifies receive/send queues, Flow Control, and certification dependency metrics as important performance signals.

Current MariaDB system-variable documentation covers `wsrep_auto_increment_control`, `wsrep_retry_autocommit`, `wsrep_sync_wait`, `wsrep_slave_threads`, SST authentication behavior, and Galera schema-upgrade modes.
