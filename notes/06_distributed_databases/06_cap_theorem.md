# The CAP Theorem

The CAP theorem describes what happens to a distributed read/write service when parts of the system can no longer communicate.

Its central result is:

> During a network partition, a distributed read/write service cannot guarantee both linearizable consistency and availability for every request reaching a non-failing node.

The important phrase is:

```text
during a network partition
```

CAP is therefore primarily a failure-time theorem.

It does not say:

```text
Every distributed database must permanently choose
exactly two properties from C, A, and P.
```

The familiar slogan:

```text
"pick any two"
```

is useful as a mnemonic but is an incomplete model of the theorem.

A much better mental model is:

```text
Network healthy:
    many designs can provide both consistency
    and availability.

Network partitioned:
    some nodes cannot exchange information.

    Now the system must decide:

        preserve linearizability
        and reject/wait on operations that cannot
        be safely coordinated

        OR

        continue processing operations
        and accept that separated copies may diverge.
```

Gilbert and Lynch's formal treatment proved that an asynchronous distributed system cannot simultaneously guarantee atomic/linearizable consistency, availability, and tolerance of arbitrary message loss.

## Start with the actual problem: information is missing

Consider two database nodes:

```text
              replication

Node A  -------------------------  Node B

price = 10                        price = 10
```

Normally they communicate.

Now the connection fails:

```text
Node A             X             Node B

price = 10                       price = 10
```

The nodes are still running.

Clients can still reach them.

Only the communication between the nodes is broken.

That is the important CAP failure.

Now Client 1 sends this to Node A:

```text
SET price = 12
```

Suppose Node A accepts the write and responds:

```text
SUCCESS
```

The situation is now:

```text
Node A             X             Node B

price = 12                       price = 10
```

Node B has received no message explaining what happened.

Client 2 now asks Node B:

```text
GET price
```

What should B return?

That simple question contains the CAP theorem.

## What does CAP consistency mean?

The `C` in CAP refers to a strong consistency model usually expressed as linearizability.

Linearizability gives the application the illusion that there is one authoritative copy of the object and that each completed operation took effect at one instant between its invocation and response.

Consider:

```text
time ─────────────────────────────────────────>

Client 1:

WRITE price = 12
|--------------|
               SUCCESS


Client 2:

                       READ price
                       |---------|
```

The read starts after the successful write has finished.

A linearizable read cannot return:

```text
10
```

It must return:

```text
12
```

or a value written even later.

This real-time requirement is important.

If the write completed before the read began, the system cannot pretend that the read occurred before the write.

## Linearizability does not require simultaneous physical updates

A common misunderstanding is:

```text
linearizable
=
every replica changes at exactly the same nanosecond
```

That is false.

Imagine three replicas:

```text
A
B
C
```

Internally they may update at slightly different times.

The implementation is free to use:

```text
leader replication
quorums
Raft
Paxos
leases
logs
other coordination
```

The requirement is about what clients are allowed to observe.

If the system reports:

```text
WRITE succeeded
```

and a later linearizable read occurs, that read must behave consistently with the completed write.

The physical implementation may be complicated while the client experiences the illusion of one copy.

## CAP consistency is not ACID consistency

The word consistency is unfortunately overloaded.

| Term | What "consistency" is about |
|---|---|
| CAP consistency | Whether distributed operations behave like one linearizable copy |
| ACID consistency | Whether transactions preserve required database/application invariants |
| Eventual consistency | Whether replicas eventually converge under suitable conditions |
| Causal consistency | Whether causally related operations are observed in causal order |
| Serializability | Whether transactions have an outcome equivalent to some serial transaction execution |
| Strict serializability | Serializability plus real-time ordering |

Suppose a database has this constraint:

```sql
CHECK (balance >= 0)
```

Maintaining that rule concerns database/application invariants.

That is closer to the `C` in ACID.

It is not what CAP's `C` means.

Likewise, a transaction system can be serializable internally while replication between two regions has weaker visibility semantics.

These properties answer different questions.

## What does CAP availability mean?

CAP availability is also stronger and more specific than everyday use of the word "available. "

Informally, the CAP requirement is:

> Every request received by a non-failing node must eventually receive a valid response.

Suppose Node B is alive but isolated.

A client asks:

```text
GET price
```

If B says:

```text
503 Service Unavailable
```

because it cannot contact the other side, the system has chosen not to provide the requested operation on that side.

In CAP reasoning, that means sacrificing availability for that operation.

Likewise:

```text
wait forever
```

does not satisfy availability.

## CAP availability is not "five nines"

This is a different meaning from operational availability metrics such as:

```text
99.9% uptime
99.99% uptime
99.999% uptime
```

Those are usually measured over time.

CAP availability is not a percentage.

A system that rejects requests from the minority side of one rare network partition may have:

```text
99.9999% practical uptime
```

and still not satisfy CAP availability during that partition.

Conversely, CAP does not give you an SLA.

A response that eventually arrives after an extremely long time can satisfy the theoretical liveness requirement even though the application experience is terrible.

So:

```text
CAP availability
≠
SLA availability
≠
latency target
```

## What does partition tolerance mean?

A network partition means some nodes cannot communicate with other nodes.

For example:

```text
            NETWORK PARTITION

A -------- B       X       C -------- D
```

Nodes A and B can communicate.

Nodes C and D can communicate.

But the two groups cannot communicate with one another.

The nodes themselves may all be perfectly healthy.

This is important because:

```text
machine crash
```

and:

```text
communication failure
```

create different uncertainty.

If A cannot communicate with C, A generally cannot immediately know whether:

```text
C crashed
```

or:

```text
network dropped the message
```

or:

```text
C is extremely slow
```

or:

```text
A can reach C but C cannot reach A
```

Distributed protocols must operate despite that uncertainty.

## Why CAP is impossible: the two-world argument

This is the heart of the theorem.

Return to:

```text
Node A             X             Node B

price = 10                       price = 10
```

B cannot communicate with A.

Now consider two possible worlds.

### World 1 — no write happened

Nothing happened at A.

The correct current value remains:

```text
10
```

Client asks B:

```text
GET price
```

A linearizable answer is:

```text
10
```

## World 2 — a successful write happened

While B was isolated, Client 1 sent to A:

```text
SET price = 12
```

A accepted it and returned:

```text
SUCCESS
```

After that success, another client asks B:

```text
GET price
```

For linearizability, the correct answer is now:

```text
12
```

## What does B know?

From B's perspective, the two executions look identical.

In both cases B has:

```text
local value = 10

no messages from A
```

B cannot distinguish:

```text
WORLD 1:
no newer write exists
```

from:

```text
WORLD 2:
price = 12 was successfully written
```

Yet the correct linearizable response differs.

World 1 requires:

```text
10
```

World 2 requires:

```text
12
```

No local algorithm can determine which world actually occurred because the information distinguishing the two worlds is on the other side of the partition.

That is the fundamental CAP problem.

It is not primarily a database implementation problem.

It is an information problem.

## Why B cannot simply guess

Suppose B guesses:

```text
12
```

Maybe that is correct in World 2.

But in World 1 there was no write.

B has just invented a value.

Suppose B returns:

```text
10
```

That works in World 1.

But in World 2 it violates linearizability because the successful write to `12` happened before the read began.

Suppose B contacts A.

It cannot:

```text
network partition
```

Suppose B waits.

If the partition can last indefinitely, the wait can last indefinitely.

Availability is lost.

Suppose B returns an error.

The operation was not served.

Again, CAP availability is lost.

There is no clever cache algorithm hiding somewhere that provides the missing information.

## Timeouts do not solve CAP

Suppose B waits:

```text
500 ms
```

for A.

No answer arrives.

B can now decide:

```text
return stale value
```

or:

```text
return error
```

But the timeout did not teach B whether:

```text
A accepted price = 12
```

It merely told B:

```text
I have not heard from A within 500 ms.
```

These are different facts.

A timeout is useful operationally because it puts an upper bound on waiting.

It does not solve the information problem.

## What a consistency-first system does

Suppose we require:

```text
Never return a result that could violate
linearizable ordering.
```

During the partition, B cannot establish whether its copy is current.

So B may refuse the operation:

```text
Node B:

GET price
    ↓
cannot reach required quorum
    ↓
ERROR / unavailable
```

The system preserves the strong consistency requirement.

But B is alive and received a request that it could not complete.

Therefore CAP availability was sacrificed for that operation.

This behavior is often loosely called:

```text
CP
```

## What an availability-first system does

Another design says:

```text
Even while partitioned,
both sides should continue serving requests.
```

Now:

```text
Node A             X             Node B

WRITE price=12                   READ price
SUCCESS                          returns 10
```

Both sides remained operational.

But the read violated linearizability.

This behavior is often loosely called:

```text
AP
```

The copies may need to reconcile after communication is restored.

## The real CAP choice during a partition

The most useful representation is therefore:

| During the partition | What happens |
|---|---|
| Preserve linearizability | Some requests must wait, fail, or be rejected |
| Preserve CAP availability | Some requests can operate without current information and may observe/diverge from globally current state |

This is more accurate than:

```text
pick C + P

or

pick A + P
```

because the actual issue is what the system does when communication needed for coordination is unavailable.

## Why "P" is not an ordinary feature toggle

The phrase:

```text
choose partition tolerance
```

is slightly misleading.

In a distributed system connected by a real network, communication failures can happen regardless of whether the application designer likes them.

The meaningful question is:

> What guarantee will the system preserve when a partition occurs?

A design can decide that a partition makes part of the system unavailable.

That is a valid design.

But it has not somehow prevented the partition from existing.

## What about "CA"?

You will often see:

```text
CA
CP
AP
```

presented as three equal categories.

That also creates confusion.

A system can provide consistency and availability while communication is healthy.

The impossibility appears when a partition exists.

So a so-called:

```text
CA system
```

essentially describes a model where partitions are excluded or treated as a failure from which the distributed service does not promise to continue operating.

That may be perfectly reasonable.

It just does not solve the partition case addressed by CAP.

## A single database server is not a CAP counterexample

Consider:

```text
Application
     |
     v
PostgreSQL server
```

The server might provide excellent transactional consistency and serve every request while healthy.

There is no replicated network partition to resolve between database copies.

If that one server fails, however:

```text
Application
     |
     X
PostgreSQL server
```

availability disappears.

That does not violate CAP and does not defeat CAP.

It is simply a different failure model.

## Quorums make the trade-off concrete

Now consider three replicas:

```text
A
B
C
```

Suppose a strongly consistent operation requires agreement from a majority:

```text
2 of 3
```

Now the network splits:

```text
A        X        B ----- C
```

The right-hand side contains:

```text
B + C = 2 nodes
```

and therefore still has a majority.

A has:

```text
1 node
```

and does not.

The system can allow:

```text
B/C side:
strong reads and writes
```

while refusing them on:

```text
A side
```

This is a common consistency-first pattern.

## Why the minority must stop accepting authoritative writes

Suppose both sides accepted authoritative writes.

A receives:

```text
price = 12
```

while B/C receive:

```text
price = 15
```

After reconnection:

```text
Which write was authoritative?
```

If both were acknowledged as part of one linearizable history, the system needs a valid ordering and coordination rule that the separated sides could not establish while isolated.

The majority rule instead ensures that two disjoint groups cannot both form majorities simultaneously.

For three nodes:

```text
majority = 2
```

Any two majorities intersect in at least one node.

That intersection is one of the key building blocks used in quorum and consensus systems.

## Quorums do not "beat CAP"

Sometimes CAP is explained badly as:

```text
CAP says you cannot have C and A,
but quorum solves that.
```

No.

A quorum is often how a system implements the trade-off.

During:

```text
A        X        B ----- C
```

the A side cannot reach two replicas.

Therefore an operation requiring quorum must fail or wait there.

That is exactly the consistency-over-availability behavior predicted by CAP.

## Concrete CP-style example: etcd

etcd is a useful concrete example because its client API exposes the distinction directly.

etcd uses Raft-based coordination and its normal key-value operations provide strict-serializable/linearizable semantics. Its documentation states that ordinary range operations are linearizable by default and that this coordination has higher cost because current cluster consensus must be established.

Suppose the cluster is:

```text
etcd A
etcd B
etcd C
```

and A becomes isolated:

```text
A        X        B ----- C
```

B and C can still establish a majority.

A cannot.

A strong operation that requires current consensus cannot simply allow isolated A to invent an authoritative current answer.

That is the CAP trade-off made concrete.

## etcd can also perform weaker local reads

etcd also supports what its API calls a:

```text
serializable
```

member-local read.

Be careful: that word is etcd API terminology and should not be confused casually with SQL transaction isolation.

A local serializable range read can be served by one member without contacting the quorum, making it cheaper and more available but permitting stale data relative to the current quorum state. etcd's documentation explicitly contrasts these with its default linearizable reads.

So even within one product:

```text
linearizable read
```

and:

```text
possibly stale member-local read
```

make different coordination choices.

That is why:

> "etcd is CP"

is much less informative than explaining the particular operation being performed.

## Per-operation behavior is more useful than product labels

A database may support:

```text
strong read

eventually consistent read

local read

quorum read

transactional write

asynchronous regional replication
```

all within the same product.

Therefore this question:

```text
Is database X CP or AP?
```

often throws away important information.

A better question is:

> For this operation, under this replication topology and consistency configuration, what happens when the required nodes cannot communicate?

## Cassandra: tunable consistency

Apache Cassandra illustrates this extremely well.

Suppose a Cassandra partition has:

```text
replication factor = 3
```

meaning there are three replicas.

Cassandra lets an operation choose consistency levels such as:

```text
ONE
QUORUM
ALL
LOCAL_ONE
LOCAL_QUORUM
```

rather than imposing one universal setting on every operation.

The current Cassandra documentation explicitly describes this as tunable consistency.

## Cassandra with `ONE`

Suppose:

```text
RF = 3
```

and a write uses:

```text
CONSISTENCY ONE
```

The coordinator only needs the required acknowledgement from one replica before satisfying the configured consistency level.

That tends to improve:

```text
latency
availability under replica failure
```

relative to waiting for every replica.

But replicas can temporarily contain different versions.

Cassandra has mechanisms for replica convergence and repair.

## Cassandra with `QUORUM`

For:

```text
RF = 3
```

a quorum is:

```text
floor(3 / 2) + 1
= 2
```

Suppose writes use:

```text
W = 2
```

and reads use:

```text
R = 2
```

Then:

```text
R + W = 4
RF    = 3

R + W > RF
```

The read and write replica sets must overlap.

For example:

```text
WRITE contacted:
A, B

READ contacted:
B, C

intersection:
B
```

Cassandra's documentation explains this quorum-intersection model and notes that `QUORUM` for both reads and writes with `RF=3` guarantees an overlapping replica, which lets subsequent reads encounter the acknowledged write under the documented model.

This is much more useful than saying simply:

```text
"Cassandra is AP."
```

## Stronger consistency reduces which failures an operation can tolerate

Suppose:

```text
RF = 3
```

and two replicas become unreachable.

With:

```text
ONE
```

an operation might still have enough reachable replicas.

With:

```text
QUORUM
```

it does not.

With:

```text
ALL
```

even losing one required replica prevents the requested consistency level from succeeding.

That is the trade-off.

The consistency level changes:

```text
how much coordination is required
```

which changes:

```text
which network failures the operation can survive
without becoming unavailable.
```

Cassandra exposes this choice on a per-operation basis.

## Quorum consistency is not a magic synonym for every strong consistency model

Be careful with statements such as:

```text
R + W > N
therefore full linearizability is guaranteed
```

The actual result also depends on:

```text
version selection rules
concurrent writes
failure handling
operation semantics
replica repair
clock/timestamp behavior
```

For example, Cassandra resolves ordinary conflicting mutations using timestamp-based last-write-wins behavior. Its current documentation explicitly describes this versioning model.

So quorum intersection is an important tool.

It is not a replacement for understanding the complete consistency protocol.

## Availability-first designs create a second problem: divergence

Return to:

```text
Node A             X             Node B
```

Suppose both sides accept writes.

A receives:

```text
shopping_cart =
    {book, headphones}
```

B independently receives:

```text
shopping_cart =
    {book, keyboard}
```

After reconnection, the system contains two legitimate histories.

Restoring the network does not answer:

```text
What should the final cart contain?
```

The communication problem has ended.

A conflict-resolution problem remains.

## Convergence needs a reconciliation rule

Some common reconciliation strategies are:

| Strategy | Basic idea | Important limitation |
|---|---|---|
| Last-write-wins | Pick one version according to an ordering rule | Another valid update can disappear |
| Causal/version metadata | Detect whether versions are causally ordered or concurrent | Detecting a conflict does not tell you the business merge |
| Application merge | Application understands the semantics and combines versions | Can require substantial application logic |
| CRDT | Structure operations/state so concurrent versions have a deterministic merge | Only works naturally for data whose semantics fit the chosen CRDT |

The network healing itself does not choose the correct business outcome.

## Last-write-wins

Suppose:

```text
A:
status = "shipped"
timestamp = 10:00:00.100

B:
status = "cancelled"
timestamp = 10:00:00.200
```

A last-write-wins system may decide:

```text
cancelled wins
```

because it has the later ordering value.

The system converges.

But convergence does not mean:

```text
both business operations survived
```

One value lost the conflict.

Clock-based LWW schemes also need carefully defined timestamp and tie-breaking behavior.

## Convergence and preservation are different properties

Suppose:

```text
Replica A = X
Replica B = Y
```

and the merge rule always chooses `Y`.

Eventually both replicas become:

```text
Replica A = Y
Replica B = Y
```

The system converged successfully.

But:

```text
X
```

has disappeared.

Therefore:

> Eventual convergence does not imply that every concurrent update survives reconciliation.

That distinction matters enormously in availability-oriented systems.

## Vector clocks detect concurrent histories

The original Amazon Dynamo system provides a classic example.

It associated versions with vector clocks containing `(node, counter)` information.

That metadata allowed Dynamo to determine whether:

```text
version B descended from version A
```

or whether:

```text
A and B evolved independently
```

and were therefore concurrent versions requiring reconciliation.

The vector clock answers:

```text
Are these versions causally related?
```

It does not automatically answer:

```text
What does the business want the merged value to be?
```

## The original Dynamo shopping-cart example

The 2007 Dynamo paper deliberately targeted services for which rejecting updates was undesirable.

Amazon's shopping-cart example treated availability as particularly important: customers should continue adding or removing items even during failures. Divergent cart versions could later be reconciled using application knowledge.

Conceptually:

```text
partition
   |
   +----------------------------+
   |                            |
Region / replica A        Region / replica B

cart: book                cart: book
+ headphones              + keyboard
   |                            |
   +-------------+--------------+
                 |
           communication
             restored
                 |
                 v
             merge
                 |
                 v
book
headphones
keyboard
```

Whether this merge is correct depends on the application's semantics.

The original Dynamo paper even notes that this strategy can allow deleted cart items to reappear in some conflict scenarios.

That is a real example of the complexity hidden behind:

```text
"eventually consistent"
```

## Dynamo used more than eventual consistency

The original Dynamo design combined several techniques.

| Problem | Dynamo technique |
|---|---|
| Partitioning | Consistent hashing |
| Replication | Multiple replica nodes |
| Causal version tracking | Vector clocks |
| Temporary replica failures | Sloppy quorum and hinted handoff |
| Permanent divergence | Anti-entropy using Merkle trees |
| Membership/failure information | Gossip |
| Concurrent business versions | Application or syntactic reconciliation |

The Dynamo paper documents these mechanisms as components of its availability-oriented architecture.

The important point is that none of them violates CAP.

They help the system operate usefully after choosing weaker consistency behavior during certain failures.

## Hinted handoff does not solve CAP

Suppose the normal replica for key `K` is unavailable.

A Dynamo-style architecture can temporarily store the update elsewhere:

```text
K should go to B

B unavailable

A temporarily stores:
"K update intended for B"
```

Later:

```text
B returns

A sends the hinted update to B
```

This improves:

```text
write availability
eventual convergence
```

But while B lacks the update, a local read from B cannot magically know that update happened.

Hinted handoff helps repair state after failures.

It does not remove CAP's missing-information problem.

## Read repair does not solve CAP either

Suppose a read contacts:

```text
A = version 7
B = version 6
C = version 7
```

The system may determine:

```text
B is stale
```

and repair B.

That is useful.

But read repair depends on the ability to communicate with replicas and compare versions.

During an actual partition:

```text
A/B       X       C
```

the unreachable side's state is still unknown.

Again:

```text
repair mechanism
≠
CAP loophole
```

## Anti-entropy

Systems can also periodically compare replica state in the background.

For example, they may exchange compact summaries of data ranges and discover:

```text
range 1: equal
range 2: equal
range 3: different
```

then synchronize only the differing data.

The Dynamo design used Merkle-tree-based anti-entropy for this purpose.

Apache Cassandra retains similar repair ideas and documents hinted handoff, read repair, and anti-entropy repair as mechanisms helping replicas converge.

Again, these mechanisms repair after or around divergence.

They do not allow an isolated node to know information it has not received.

## Eventual consistency

A useful simplified definition is:

> If new updates stop, communication succeeds, and the reconciliation/repair mechanisms continue to run, replicas eventually converge toward the system's resolved state.

Notice what this definition does not promise.

It does not necessarily mean:

```text
all replicas are fresh within 50 ms
```

It does not necessarily mean:

```text
every concurrent write survives conflict resolution
```

It does not necessarily mean:

```text
every intermediate read is monotonic
```

It does not necessarily mean:

```text
business invariants can never be temporarily violated
```

Eventual consistency is therefore a convergence statement, not a complete application semantics specification.

## MVCC does not solve CAP

MVCC solves a different problem.

Suppose one database server has concurrent transactions:

```text
T1
T2
T3
```

MVCC lets those transactions work with multiple row versions so readers and writers can avoid unnecessary blocking.

CAP instead considers distributed nodes separated by missing communication:

```text
Database A       X       Database B
```

Keeping more local row versions does not tell B:

```text
whether A accepted a new operation
```

Therefore:

```text
MVCC
```

does not remove:

```text
network-information uncertainty
```

The problems exist at different layers.

## Dynamo and DynamoDB are not the same system

This distinction is important.

Dynamo refers to the internal Amazon key-value architecture described in the 2007 SOSP paper:

```text
Dynamo: Amazon's Highly Available Key-value Store
```

That paper documents:

```text
vector clocks
sloppy quorums
hinted handoff
Merkle-tree anti-entropy
shopping-cart reconciliation
consistent hashing
```

among its mechanisms.

Amazon DynamoDB is a separate managed AWS database service.

Do not take an implementation detail from the 2007 Dynamo paper and claim:

```text
"DynamoDB internally works this way."
```

unless current DynamoDB documentation says so.

## DynamoDB itself demonstrates why product CAP labels are weak

Current DynamoDB provides several different consistency behaviors.

For ordinary DynamoDB tables and local secondary indexes, applications can request either eventually consistent or strongly consistent reads.

Global secondary indexes support eventually consistent reads only.

So even inside one regional DynamoDB table:

```text
table GetItem with ConsistentRead=true
```

and:

```text
GSI Query
```

have different consistency properties.

Calling the entire service simply:

```text
AP
```

or:

```text
CP
```

hides that distinction.

## Current DynamoDB global tables make the distinction even clearer

As of the current AWS documentation, DynamoDB Global Tables support two multi-Region consistency modes:

```text
MREC
Multi-Region Eventual Consistency

MRSC
Multi-Region Strong Consistency
```

MREC is the default and asynchronously propagates item changes across Regions.

MRSC synchronously replicates item changes to another Region before the write returns successfully, and strongly consistent reads on MRSC replicas return the latest version.

This is a particularly good modern example of why:

> classify the configuration and operation, not the product logo.

## DynamoDB MREC: availability-oriented regional behavior

With MREC:

```text
Region A             Region B

write X
   |
SUCCESS
   |
   | asynchronous replication
   +---------------------------->
```

Region B can temporarily have an older value.

AWS documents that MREC changes propagate asynchronously and that concurrent updates can be resolved using last-writer-wins behavior.

This architecture favors lower cross-Region coordination latency.

The consequence is weaker immediate cross-Region consistency.

## DynamoDB MRSC: stronger coordination

MRSC changes the design.

Conceptually:

```text
Region A
    |
write
    |
    +----------> Region B / witness path
                      |
                required coordination
                      |
                      v
                 acknowledgement
    |
    v
SUCCESS
```

AWS documents that MRSC synchronously replicates a change to at least one other Region before the write returns and provides strongly consistent reads across MRSC replicas.

That coordination has a latency cost because cross-Region communication is now on the critical path.

AWS explicitly notes that MRSC write and strongly consistent read latency depends on the participating Regions and their network round-trip latency.

That leads directly into PACELC.

## MRSC also makes the availability trade-off visible

AWS's MRSC documentation says the local Region can continue servicing read/write operations while it can establish the required coordination with another replica or witness.

If it cannot establish that quorum, strongly consistent operations cannot simply continue as though nothing happened; eventually consistent reads remain a different option.

That is CAP-style behavior made concrete:

```text
strong guarantee
requires coordination

coordination unavailable
→ strong operation may become unavailable
```

## PACELC: CAP describes failures, but systems make trade-offs when healthy too

CAP concentrates on the partition case.

But distributed databases spend most of their time without a severe partition.

There is still an important design trade-off during normal operation:

```text
coordination
versus
latency
```

This motivated PACELC.

Daniel Abadi's formulation asks:

```text
IF Partition:

    Availability
        versus
    Consistency

ELSE:

    Latency
        versus
    Consistency
```

Abadi introduced PACELC specifically to emphasize that CAP does not describe the important latency/consistency trade-offs that continue during normal operation.

## PACELC with two regions

Suppose:

```text
Frankfurt <-------- network --------> Sydney
```

A user writes in Frankfurt.

A strong global design may require coordination with Sydney before returning success:

```text
Frankfurt
    |
    | request
    v
Sydney
    |
    | acknowledgement
    v
Frankfurt
    |
SUCCESS
```

Even when nothing is broken, speed-of-light/network latency exists.

The transaction waits for that coordination.

A weaker asynchronous design can respond locally:

```text
Frankfurt

write
  |
local commit
  |
SUCCESS
  |
  +---------- replicate later ----------> Sydney
```

The second design has lower write latency.

But Sydney may temporarily be stale.

That is the `ELC` part of PACELC:

```text
Else no partition:
Latency versus Consistency.
```

## CAP and PACELC together

A good mental model is:

| Situation | Main question |
|---|---|
| Network partition exists | Must this operation sacrifice availability or strong consistency? |
| Network healthy | How much latency/coordination are we willing to pay for stronger consistency? |

This explains why distributed database design does not suddenly become trivial when there is no outage.

Global coordination always has a cost.

## Not every operation needs the same consistency

Consider an e-commerce application.

| Operation | Possible requirement |
|---|---|
| Product description | Slightly stale read may be acceptable |
| Product-review count | Eventual consistency may be acceptable |
| Shopping-cart contents | Application-specific merge may be possible |
| Payment idempotency record | Stale result may be dangerous |
| Inventory allocation | Strong coordination may be required |
| Feature flag used for ordinary UI | Some staleness may be acceptable |
| Distributed lock / leader election | Linearizable semantics are usually important |

The application should choose consistency based on the invariant being protected.

There is no reason every piece of data must necessarily use the same distributed consistency model.

## Why some data merges easily and some does not

Suppose two regions independently modify a set of tags.

Region A:

```text
{database, distributed-systems}
```

Region B:

```text
{database, replication}
```

A merge rule might produce:

```text
{database, distributed-systems, replication}
```

That may be completely acceptable.

Now consider a hotel room:

```text
Region A:
room 101 booked by Alice

Region B:
room 101 booked by Bob
```

A merge:

```text
Alice + Bob
```

does not solve the business problem.

The data type and business invariant determine whether concurrent updates are safely mergeable.

## CRDTs help only when the semantics fit

A Conflict-Free Replicated Data Type (CRDT) is designed so independently produced states or operations can converge deterministically according to mathematically defined rules.

For suitable data structures this can be extremely useful.

For example:

```text
distributed counters
sets
some maps/registers
collaborative structures
```

can have well-defined merge semantics.

But CRDT does not mean:

```text
all business conflicts disappear
```

A CRDT cannot decide whether:

```text
Alice or Bob should receive
the last available concert ticket
```

unless the application's semantics have been deliberately modeled to resolve that problem.

## Conflict resolution is a business decision too

Suppose two disconnected regions update:

```text
credit_limit = €10,000
```

Region A:

```text
new limit = €8,000
```

Region B:

```text
new limit = €20,000
```

Possible rules include:

```text
latest timestamp wins

lowest value wins

highest value wins

manual reconciliation

prevent concurrent changes through coordination
```

All are technically possible.

They have completely different business consequences.

Distributed-system design cannot choose the correct business semantics automatically.

## CAP does not say weak consistency is bad

An availability-oriented choice may be exactly correct.

For example, if a social network temporarily shows:

```text
1,002 likes
```

instead of:

```text
1,003 likes
```

that may be harmless.

Rejecting the entire page because a distant replica cannot be contacted could be much worse.

Conversely, an availability-oriented stale decision may be unacceptable for:

```text
withdraw the last €500
sell the last seat
elect one cluster leader
assign a globally unique scarce resource
```

CAP does not tell you which business trade-off to choose.

It tells you the distributed-system constraint you must design around.

## CAP does not say strong consistency is always better

Strong consistency has costs:

```text
coordination
network round trips
reduced availability under some failures
higher tail latency
```

Those costs may be worthwhile.

Or they may not.

The correct choice depends on what can happen if data is stale or conflicting.

A product catalog and a distributed lock service are not the same problem.

## CAP does not say eventual consistency means "random"

Eventually consistent systems are not necessarily chaotic.

They may implement very specific guarantees around:

```text
causal ordering
monotonic reads
read-your-writes
session consistency
quorum intersection
conflict resolution
repair
```

The phrase:

```text
eventually consistent
```

alone does not specify all of those properties.

You need to know the actual consistency model.

## CAP does not classify an entire architecture forever

Suppose an application uses:

```text
etcd
```

for leader election and:

```text
Cassandra
```

for an activity feed and:

```text
PostgreSQL
```

for financial transactions and:

```text
DynamoDB GSI
```

for an eventually consistent lookup.

What is the application's CAP category?

There is no particularly useful single answer.

Different operations intentionally make different trade-offs.

Even one datastore can provide several choices.

## Technology summary

| Technology / operation | Concrete consistency behavior relevant to this discussion |
|---|---|
| etcd default KV/range operations | Linearizable/strict-serializable semantics involving current cluster consensus |
| etcd member-local serializable read | Avoids quorum coordination and may return stale data |
| Cassandra `ONE` / `LOCAL_ONE` | Fewer required replica responses; prioritizes lower latency/greater request survivability at the cost of weaker immediate consistency |
| Cassandra `QUORUM` | Requires a majority; read/write quorum intersection can provide stronger visibility guarantees |
| Cassandra `ALL` | Requires all replicas, giving up more availability when a replica is unreachable |
| Original Amazon Dynamo | Designed for very high write availability; supported divergent versions and later reconciliation |
| DynamoDB table/LSI strong read | Application can request strongly consistent reads |
| DynamoDB GSI read | Eventually consistent only |
| DynamoDB Global Tables MREC | Asynchronous multi-Region propagation with eventual cross-Region consistency |
| DynamoDB Global Tables MRSC | Cross-Region coordination supporting strong multi-Region consistency, with corresponding coordination/latency/availability implications |

etcd documents the difference between its default linearizable reads and lower-cost potentially stale member-local reads. Cassandra documents per-operation tunable consistency and quorum behavior. The original Dynamo paper documents its availability-oriented design and reconciliation mechanisms. Current DynamoDB documentation describes table/index read consistency and separate MREC/MRSC global-table modes.

## Common CAP mistakes

| Claim | Better explanation |
|---|---|
| "CAP means pick any two forever. " | CAP constrains guarantees during partitions. |
| "Partition tolerance is optional if we choose CA. " | You can exclude partitions from your guarantee/model, but real distributed networks can still partition. |
| "Returning an error preserves CAP availability. " | Rejecting an operation because coordination is unavailable means that operation is unavailable in the CAP sense. |
| "Timeouts solve partitions. " | A timeout bounds waiting; it does not provide missing information. |
| "Quorum beats CAP. " | Quorum is commonly how consistency-first systems decide which side can continue authoritative operations. |
| "Eventual consistency means all writes survive. " | Convergence can discard a conflicting version depending on reconciliation rules. |
| "MVCC solves CAP. " | MVCC handles concurrent versions locally; it cannot communicate across a broken network. |
| "Every database is either CP or AP. " | Operations, replication modes, read levels, and configurations can make different choices. |
| "Dynamo and DynamoDB are the same implementation. " | Dynamo is the 2007 architecture/paper; DynamoDB is a separate managed service with its own documented features. |
| "CAP consistency means ACID consistency. " | CAP uses a distributed visibility/order guarantee; ACID consistency concerns transaction invariants. |

## How to analyze a real system

Instead of asking:

```text
Is this database CP or AP?
```

ask:

```text
What exact operation are we discussing?

What consistency guarantee does that operation request?

How many replicas exist?

Which replicas must participate?

What happens when some replicas cannot communicate?

Does the operation wait?

Does it return an error?

Does it use a local possibly stale value?

Can writes happen on both separated sides?

If they can, how are conflicts detected?

How are conflicts resolved?

What guarantee exists after communication returns?

What latency does normal coordination add?
```

Those questions reveal the real distributed-system design.

## A complete three-node example

Suppose:

```text
RF = 3

A
B
C
```

All store:

```text
price = 10
```

Network partition:

```text
A        X        B ----- C
```

Now Client 1 sends to A:

```text
SET price = 12
```

Client 2 sends to B:

```text
GET price
```

### Consistency-first configuration

The system requires:

```text
2 of 3
```

for authoritative operations.

A has only:

```text
1
```

reachable replica.

Therefore:

```text
write on A → rejected/waits
```

B and C have:

```text
2
```

and can continue.

The service preserved the strong consistency protocol but sacrificed availability for strong operations on A's side.

### Availability-first configuration

A is allowed to write locally:

```text
A = 12
```

B continues serving:

```text
B = 10
```

Both sides remain operational.

But they no longer present one linearizable copy.

After reconnection:

```text
12
```

and:

```text
10
```

must be reconciled according to the system's version/conflict rules.

That is CAP in one example.

## The deepest CAP insight

CAP is often taught as a triangle:

```text
        C
       / \
      /   \
     A --- P
```

That picture is memorable but hides the actual reasoning.

The more useful picture is:

```text
             NETWORK PARTITION

Node A                            Node B

local information                local information
      |                                |
      |                                |
      X---------- no messages ----------X


Question:

Can both nodes continue answering
while guaranteeing that their answers
respect a single real-time global history?
```

If operations on one side can change the correct answer on the other side, and communication is impossible, then the other side lacks the information needed to guarantee both.

That information gap is the core of CAP.

## Final mental model

Remember CAP like this:

```text
NORMAL OPERATION

A <-----------> B

Communication works.

The system may coordinate to provide
strong consistency and availability.
```

Now:

```text
PARTITION

A       X       B
```

A successful operation can occur on one side.

The other side cannot learn about it.

If the other side must remain fully available:

```text
it may operate on incomplete information
→ linearizability may be lost
```

If linearizability must be preserved:

```text
it must avoid operations whose correctness
depends on unavailable information
→ availability is lost for those operations
```

Then add PACELC:

```text
PARTITION:
    Availability ↔ Consistency

ELSE:
    Latency ↔ Consistency
```

Finally, do not classify databases by slogans.

Ask:

> For this particular operation, replica topology, consistency setting, and network failure, which nodes must communicate before the operation succeeds—and what happens when they cannot?

That question turns CAP from an interview slogan into a practical distributed-systems design tool.

## References

Gilbert and Lynch formally proved Brewer's conjecture for an asynchronous distributed model, establishing the impossibility of simultaneously guaranteeing atomic/linearizable consistency, availability, and partition tolerance.

Daniel Abadi's PACELC discussion explains why CAP primarily constrains systems during partitions while distributed databases also face a normal-operation trade-off between latency and consistency.

The original Amazon Dynamo paper documents an availability-oriented key-value architecture using consistent hashing, object versioning, vector clocks, quorum-like techniques, hinted handoff, anti-entropy, and application-assisted conflict resolution.

Apache Cassandra's current architecture documentation describes its Dynamo-influenced design, last-write-wins versioning, replica repair mechanisms, and per-operation tunable consistency including `ONE`, `QUORUM`, `LOCAL_QUORUM`, and `ALL`.

etcd documents default linearizable key-value reads and an optional member-local `serializable` read mode that trades current quorum visibility for lower coordination cost and possible staleness.

Current AWS documentation describes DynamoDB's eventually and strongly consistent read options, eventually consistent GSIs, and the separate MREC and MRSC consistency modes now available for Global Tables.
