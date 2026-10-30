# Eventual Consistency

**Eventual consistency** is a convergence guarantee: if updates stop and replicas can communicate and repair their states, they eventually agree on the value selected by the system's reconciliation policy. It does not promise a maximum delay, a read-your-writes experience, or preservation of every concurrent update. Propagation and conflict resolution are part of the contract, not details to assume away.

```
Initial State:
+-----------+   +-----------+   +-----------+
| v1        |   | v1        |   | v1        |
| Node A    |   | Node B    |   | Node C    |
+-----------+   +-----------+   +-----------+

After Update on Node A:
+-----------+   +-----------+   +-----------+
| v2        |   | v1        |   | v1        |
| Node A    |   | Node B    |   | Node C    |
+-----------+   +-----------+   +-----------+

Time T1:
+-----------+   +-----------+   +-----------+
| v2        |   | v1        |   | v1        |
| Node A    |   | Node B    |   | Node C    |
+-----------+   +-----------+   +-----------+

Time T2:
+-----------+   +-----------+   +-----------+
| v2        |   | v2        |   | v1        |
| Node A    |   | Node B    |   | Node C    |
+-----------+   +-----------+   +-----------+

Time T3:
+-----------+   +-----------+   +-----------+
| v2        |   | v2        |   | v2        |
| Node A    |   | Node B    |   | Node C    |
+-----------+   +-----------+   +-----------+
```

In this scenario, Node A receives an update changing the data from Version 1 to Version 2. Initially, only Node A has the latest version. Over time, the update propagates to Node B and eventually to Node C. By Time T3, all nodes have synchronized to Data Version 2, achieving eventual consistency.

## Characteristics of Eventual Consistency

Eventual consistency is considered a **weak consistency model** compared to strong consistency models like linearizability. It allows systems to remain highly available and responsive by permitting temporary inconsistencies.

### High Availability and Performance

By not requiring immediate synchronization across all nodes, systems can sometimes avoid waiting for remote coordination; storage work and network delays still remain. This approach reduces latency because nodes do not need to wait for confirmation from other nodes before responding to a request.

### Scalability

Eventual consistency supports scalability in distributed systems. Nodes can handle requests and updates locally without constant coordination with other nodes, allowing the system to accommodate a growing number of nodes and handle increased loads efficiently.

## How Update Propagation Works

Updates in an eventually consistent system propagate to other nodes asynchronously. The time it takes for updates to reach all nodes depends on factors like network latency, replication mechanisms, and system load.

### Example of Update Propagation:

1. A user updates their profile picture on a social media platform.
2. The update is saved on one server (Node A).
3. Node A asynchronously replicates the change to other servers (Nodes B and C).
4. Friends accessing the user's profile through different nodes might see the old picture until the update reaches those nodes.
5. Eventually, all nodes reflect the new profile picture.

## Trade-offs of Eventual Consistency

While eventual consistency offers advantages in availability and performance, it introduces certain trade-offs that need to be managed carefully.

### Temporary Inconsistencies

During the propagation delay, different nodes may hold different versions of the data. This can lead to clients reading stale or outdated information. Applications need to handle these inconsistencies appropriately, perhaps by:

- Providing mechanisms for conflict resolution.
- Informing users about the potential for stale data.
- Designing operations that can tolerate inconsistencies.

### Conflict Resolution

When multiple nodes update the same data simultaneously, conflicts can arise. The system must have strategies in place to resolve these conflicts and ensure that all nodes eventually agree on the final state of the data.

#### Common Conflict Resolution Strategies:

- **Last Write Wins** selects the winning update using timestamps and a tie-breaker. Clock skew can change the winner, and concurrent updates may be lost.
- **Version vectors** track causal relationships across replicas and detect concurrent versions; a separate rule resolves those versions.
- **Merge functions** employ application-specific logic to combine or reconcile conflicting updates.
- **CRDTs (Conflict-Free Replicated Data Types)** leverage specialized data structures to handle concurrent updates without introducing conflicts.

## Where delayed propagation can be acceptable

Consider three **generic** workloads, rather than assuming the internals of a particular product:

| Workload | What readers might observe | Design question |
|---|---|---|
| Social feed projection | A new post appears to some viewers before others | Is delayed visibility acceptable, and can the feed catch up after replay? |
| Replicated collaborative state | Two edits arrive in different orders | What merge semantics preserve intended user changes? |
| Edge content cache | An old asset remains until refresh or invalidation | What maximum staleness, purge, and versioning contract is offered? |

Some collaborative editors use stronger coordination, operational transformation, or CRDTs for particular features; **eventual consistency alone does not explain their conflict behavior**. Likewise, a CDN cache is not automatically an eventually consistent database with the same API guarantees.

## Benefits of Eventual Consistency

Eventual consistency can support these goals **when the replication and failure model permits them**:

- **Throughput and latency:** acknowledging writes before all replicas coordinate may reduce write latency, at the cost of stale reads and reconciliation work.
- **Availability during failures:** some requests can continue at reachable replicas, but this depends on routing, write durability, conflict handling, and how the system behaves when capacity is lost.
- **User experience:** eventual consistency fits workflows that tolerate delayed visibility; it is not appropriate by default for decisions requiring a current authoritative value, such as unique seat allocation.

## Considerations When Using Eventual Consistency

Applications relying on eventual consistency need to account for its characteristics in their design.

### Designing for Inconsistency

Applications should handle cases where data may be outdated. For example:

- Displaying messages indicating that data is being updated.
- Allowing users to refresh or manually sync data.
- Implementing retries for failed operations.

### Understanding Consistency Requirements

Not all applications can tolerate temporary inconsistencies. Systems handling financial transactions or inventory management may require stronger consistency models to prevent errors. It's important to assess consistency requirements based on the application's domain.

## Implementing Eventual Consistency

Implementing eventual consistency involves designing systems that can handle delayed updates and resolve conflicts effectively.

### Update Propagation Mechanisms

Updates can be propagated using various methods:

- **Gossip protocols** enable nodes to randomly share information with peers, gradually disseminating updates across the network.
- **Asynchronous replication** can acknowledge a local write before other replicas receive it. This lowers coordination but risks lag or loss of a recent write if the acknowledged copy fails before durable propagation, depending on failure and durability policy.
- **Publish-subscribe systems** distribute change events to subscribers, but delivery, replay, duplicate handling, and durable consumer progress must be implemented; subscription alone does not guarantee eventual convergence.

### Handling Conflicts with Version Vectors

Version vectors summarize observed causal history. They can distinguish “this version followed that one” from “these updates were concurrent,” but **they do not select a winner or merge values**. Resolution is a separate application or storage-policy decision.

#### Example of Version Vectors:

- **Node A** updates the data, creating a version vector `[A:1, B:0, C:0]`, indicating its update.
- **Node B** simultaneously updates the same data, resulting in a version vector `[A:0, B:1, C:0]`.
- During synchronization, the vectors reveal that neither version causally dominates the other. A defined merge function, retained sibling versions, or a deliberate last-writer-wins rule must then resolve the concurrent values.

## Review questions

1. What is eventual consistency in distributed database systems, and how does it differ from strong consistency models?
2. How does update propagation work in an eventually consistent system, and what factors influence the time it takes for all nodes to synchronize?
3. What are the main trade-offs of using eventual consistency, particularly regarding temporary inconsistencies and conflict resolution?
4. What are some common conflict resolution strategies used in eventually consistent systems, such as Last Write Wins, version vectors, and CRDTs?
5. In what real-world scenarios is eventual consistency particularly beneficial, and how do applications like social media platforms and content delivery networks leverage this consistency model?
