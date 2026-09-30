# The CAP Theorem

During a network partition, a distributed read/write service cannot guarantee both **linearizable consistency** and **availability for every request to a non-failing node**. CAP explains a failure-time trade-off; “pick any two” is an incomplete description.

## What the properties mean

| Property | Meaning in CAP |
| --- | --- |
| Consistency (C) | Operations behave like operations on one copy, respecting real-time order. A read begun after a successful write must reflect that write or a later one. |
| Availability (A) | Every request received by a non-failing node eventually completes with a valid result. An error or indefinite wait does not satisfy this requirement. |
| Partition tolerance (P) | The model allows communication between groups of nodes to be lost or delayed indefinitely. |

CAP availability does not specify a latency bound or an uptime percentage. CAP consistency is not ACID consistency, which concerns application invariants. Linearizability also does not require every physical replica to update at exactly the same instant.

## A two-node example

Both nodes initially store `price = 10`. Their network connection fails.

```text
Client 1 --> Node A     X     Node B <-- Client 2
             price=10         price=10
```

Client 1 writes `price = 12` to A. Client 2 then reads from B. B cannot determine whether A accepted a newer write.

- If A accepts the write and B returns its old value, the service has sacrificed linearizability.
- If the service rejects or waits on operations that cannot be safely completed, it has sacrificed CAP availability for those operations.

No cache, timeout, or concurrency-control algorithm gives B the missing information. A timeout can bound waiting, but an error still does not meet CAP availability.

## CP, AP, and the limits of labels

**CP** describes behavior that preserves consistency by withholding operations when communication is insufficient, often outside a reachable quorum. **AP** describes behavior that continues serving operations on separated nodes, allowing divergent state that must later be reconciled.

“CA” is useful only when partitions are excluded from the model. A single-server database does not demonstrate a solution to the distributed partition problem, and can still become unavailable if that server fails.

Classify an operation and configuration rather than treating a product label as a universal guarantee. A database can offer different read consistency levels, quorum settings, or regional replication modes. A quorum configuration can also make requests unavailable when too few replicas are reachable.

## Convergence and conflict resolution

If writes are accepted on both sides of a partition, reconnection alone does not specify the correct result. The system needs a reconciliation rule.

- **Last-write-wins:** select by a timestamp and a tie-breaker. Clock skew can affect the outcome, and one update can be lost.
- **Version vectors:** track causal relationships and identify concurrent versions; the application may still need to merge them.
- **Application merge or CRDT:** combine changes according to explicit rules suited to the data model.

Eventual consistency means replicas converge when writes stop and communication and reconciliation can complete. It does not guarantee that every update survives a merge or that convergence has a fixed deadline.

MVCC manages versions for concurrent transactions. It does not remove CAP's communication constraint. Read repair, hinted handoff, and anti-entropy help replicas reconcile after failures; they do not make unavailable information immediately knowable.

## Dynamo and DynamoDB are different

Amazon's **Dynamo** paper describes an availability-oriented key-value system and shopping-cart conflict resolution. It discusses techniques including consistent hashing and versioning. Those implementation details should not be presented as documented internals of the separate managed service **DynamoDB**. See the [original Dynamo paper](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf).

DynamoDB offers different consistency options depending on the operation and resource. For example, table and local secondary index reads can request strong consistency, while global secondary index reads are eventually consistent. Regional replication modes also matter. Consult [DynamoDB read consistency](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.ReadConsistency.html) rather than assigning the whole service one CAP label.

## PACELC: the trade-off during normal operation

PACELC asks: **if there is a partition, how does the service trade availability against consistency; otherwise, how does it trade latency against consistency?**

Even with a healthy network, waiting for remote coordination can increase latency. Whether that coordination is necessary depends on the consistency guarantee and the operation.

## Review questions

1. Why can an isolated replica not guarantee a fresh read after a write elsewhere?
2. How does CAP availability differ from an uptime target?
3. Why are ACID consistency and CAP consistency different?
4. What determines whether concurrent writes can be merged safely?
5. Why should CAP labels include the operation and configuration?
