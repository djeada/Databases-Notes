# Consistency, Replication, Transactions, and Conflict Handling

Choosing a NoSQL data model does not automatically choose a consistency model. Document, key-value, wide-column, and graph describe how data is represented. Replication, transaction scope, and read/write guarantees are separate design choices.

```text
data model
    |
    +-- document / key-value / wide-column / graph

distribution
    |
    +-- leader / multi-leader / leaderless / sharded

guarantees
    |
    +-- atomicity / isolation / session consistency / eventual consistency
```

A document database can support multi-document transactions. A key-value store can provide linearizable operations for selected keys. A relational database can use asynchronous replicas. Avoid treating SQL and NoSQL as shorthand for guarantees they do not necessarily imply.

## Start with the business invariant

Write the rule before choosing the mechanism.

Examples:

- inventory must not become negative,
- a username must be unique,
- an order total must match its line items,
- a user should see their own recent profile update,
- recommendation results may be a few minutes stale.

The first three are correctness constraints. The last two are visibility and freshness requirements.

## Atomic over what boundary?

Atomicity means all-or-nothing within a defined scope.

A store may guarantee:

```text
one key update is atomic
```

without guaranteeing:

```text
updates to 100 independent keys are atomic
```

A document database may make one-document changes atomic and offer an optional broader transaction API.

Always ask: **atomic over which keys, documents, partitions, or shards?**

## Single-record atomicity

If one aggregate is stored together, atomic updates are simpler.

Example inventory document:

```json
{
  "sku": "DB-101",
  "available": 7,
  "reserved": 3
}
```

A conditional update can move units between fields without exposing a half-finished state. This is one reason aggregate boundaries matter in NoSQL modeling.

## Cross-partition transactions

When a transaction spans partitions or shards, more coordination is required.

```text
single partition
      |
      v
local coordination

many partitions
      |
      v
distributed coordination
      |
      v
more latency and failure cases
```

Use broad transactions when the business invariant requires them, not merely because the API exists.

## Lost updates

Two clients read version 7.

Client A writes version 8.

Client B still holds version 7 and tries to write.

Without concurrency control, B may overwrite A.

Use optimistic concurrency:

```text
update only if version = 7
```

If zero records match, another writer won and the stale operation must reload/retry.

## Compare-and-set

Conditional writes are a common NoSQL primitive:

```text
if current value == expected:
    write new value
else:
    fail
```

Useful for:

- versioned updates,
- claiming work,
- leases,
- uniqueness coordination.

## Replication

Replication creates copies:

```text
client
  |
  v
replica/leader A
  |------> replica B
  `------> replica C
```

Replication can improve availability and read capacity, but introduces questions about acknowledgement, lag, failover, and conflict handling.

## Synchronous replication

A write waits for enough replicas before success.

Advantages:

- stronger durability under defined failures,
- fresher failover state.

Trade-offs:

- higher write latency,
- reduced availability if enough replicas cannot respond.

## Asynchronous replication

The primary may acknowledge before replicas apply the write.

```text
client -> primary -> success
              |
              `---- later ----> replica
```

Advantages:

- lower write latency.

Trade-offs:

- replicas can be stale,
- recent acknowledged data can be at risk under some failover designs.

## Read-after-write

A user updates a profile and immediately reloads it.

If the read goes to a lagging replica, the old value can reappear.

Possible strategies:

- read from the writer/leader after a write,
- use session consistency,
- sticky routing,
- wait for a replica to catch up,
- choose a stronger read consistency setting.

## Eventual consistency

Eventual consistency means replicas are expected to converge if updates stop and communication recovers.

It does **not** define:

- how long convergence takes,
- what a client sees during lag,
- how concurrent conflicts are resolved,
- whether acknowledged writes can be lost.

State a concrete staleness budget instead of saying only "eventual is fine."

Example:

```text
recommendations may lag by 5 minutes
inventory reservations may not be stale
```

## Leader-based replication

```text
writers
  |
  v
leader
  |----> follower
  `----> follower
```

This gives a clear write-ordering point but requires leader failover and can make follower reads stale.

## Multi-leader replication

Several sites accept writes.

```text
EU leader <---- replication/conflicts ----> US leader
```

This may reduce local write latency but concurrent writes can conflict.

## Leaderless and quorum-style replication

A coordinator may write/read several replicas.

With three replicas, a quorum is two.

The intuition is that overlapping read and write sets can improve freshness, but exact guarantees depend on the product, topology, failure modes, and conflict-resolution rules.

Cassandra is a concrete example with tunable consistency levels.

## CAP theorem

CAP concerns behavior **during a network partition**. A distributed system cannot provide both complete availability and linearizable consistency across separated sides of the partition.

"Pick two of three" is an oversimplification because real distributed deployments cannot simply opt out of partitions.

Use CAP to reason about partition-time behavior, not as a product scorecard.

## Conflict handling

Suppose two regions concurrently update the same profile:

```text
EU: display_name = "Alice Smith"
US: display_name = "A. Smith"
```

After reconnection, the system needs a rule.

Possible strategies:

- last-write-wins,
- explicit conflicting versions,
- application merge,
- CRDT-specific merge,
- single-writer ownership.

## Last-write-wins

LWW is simple but can silently discard valid concurrent work.

If two users update different fields of the same object and the whole object is resolved by one timestamp, one change can vanish.

Use it only when that loss policy matches business semantics.

## Application merge

Some data can be merged naturally.

Two offline shopping-list edits:

```text
region A adds milk
region B adds bread
```

can become:

```text
milk + bread
```

A bank balance cannot safely use an arbitrary merge rule.

Conflict resolution is data-type specific.

## CRDT idea

Conflict-free Replicated Data Types define mergeable state/operations for specific semantics, such as counters or sets.

They are powerful but not a universal answer. Arbitrary business objects do not become safely mergeable just by calling them CRDTs.

## Clock problems

Physical clocks can drift or jump. A later wall-clock timestamp is not always a causally later operation.

Distributed systems may use logical clocks, vector clocks, hybrid logical clocks, or engine-specific version metadata.

## Transactions across services

Checkout may involve:

```text
reserve inventory
charge payment
create order
publish event
```

One database transaction usually cannot roll back an external payment or message broker.

Use workflow patterns such as sagas and compensating actions when work spans systems.

## Outbox pattern

A transaction can write both:

```text
business state
+
outbox event
```

Then a separate publisher reliably forwards the outbox event.

This avoids the gap where the database commits but event publication fails.

## Idempotency

Retries are normal because clients may not know whether a timed-out request committed.

Use stable request IDs:

```text
idempotency_key = checkout-6f...
```

A repeated request can return the previous result instead of creating a duplicate order.

## Timeout ambiguity

A client timeout means:

```text
response was not observed
```

not necessarily:

```text
server rolled back
```

The server may have committed.

This is why idempotency and post-timeout verification matter.

## At-least-once delivery

Message systems frequently deliver an event more than once.

Consumers should handle duplicates:

```text
event ID
  |
  v
already processed?
  |-- yes -> return prior result
  `-- no  -> process and record
```

End-to-end "exactly once" cannot be inferred from a single component label.

## Retry the whole logical operation

On a serialization/concurrency conflict:

```text
read
validate
compute
conditional write
   |
 conflict?
   |-- yes -> reload and retry
   `-- no  -> success
```

Retry the whole operation because earlier reads may no longer be valid.

Bound retries and use backoff.

## Multi-region latency

Strong synchronous coordination across distant regions costs network time.

```text
EU request ---- round trip ----> US replica
```

Place data and write leadership near the workload when possible, while meeting durability and residency requirements.

"Globally distributed" does not make geography free.

## Choose guarantees per operation

A single system can need several levels:

| Operation | Requirement |
| --- | --- |
| product recommendations | minutes of staleness may be acceptable |
| profile read after update | read-your-writes/session consistency |
| inventory reservation | conditional or transactional correctness |
| unique username claim | compare-and-set or transaction |
| analytics projection | eventual consistency |

Do not use the strongest option everywhere without need. Do not weaken correctness-critical operations merely for benchmark speed.

## Failure testing

Test the hard cases:

- replica unavailable,
- leader failover,
- network delay,
- duplicate request,
- timeout after commit,
- stale replica read,
- concurrent writers.

Guarantees matter most during failures.

## Design checklist

For each operation:

1. What invariant must hold?
2. What is the atomicity boundary?
3. Can concurrent writers conflict?
4. How stale may reads be?
5. Must the writer read its own write?
6. What happens during a partition?
7. What acknowledgement is required?
8. How are conflicts resolved?
9. Can retries be made idempotent?
10. What happens after timeout ambiguity?
11. Does the workflow cross services?
12. Has failure behavior been tested?

## Common mistakes

### "NoSQL means eventual consistency"

False as a category statement.

### "Transactions make modeling irrelevant"

Distributed transaction cost still matters.

### "Replica means backup"

Replication can copy bad changes.

### "Timeout means failure"

The operation may have committed.

### "Last write wins is harmless"

Valid concurrent work can disappear.

### Strongest consistency everywhere

May add latency with no product benefit.

### Weak consistency for money/inventory invariants

Can violate correctness.

## Related notes

- [NoSQL introduction](01_nosql_databases_intro.md)
- [Document modeling](05_document_modeling.md)
- [Key-value modeling](06_key_value_modeling.md)
- [Wide-column modeling](07_wide_column_modeling.md)
- [Graph modeling](08_graph_modeling.md)
- [CAP theorem](../06_distributed_databases/06_cap_theorem.md)
- [Eventual consistency](../06_distributed_databases/07_eventual_consistency.md)
- [Transactions](../04_acid_properties_and_transactions/01_transactions_intro.md)
