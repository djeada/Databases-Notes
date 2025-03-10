## Distributed Database System

A **distributed database system (DDS)** is a collection of logically interrelated databases distributed across multiple physical locations, connected by a network. The data in these systems might be replicated and/or partitioned among different sites, but the system should ideally appear to the user as a single integrated database.

```
      Internet/Clients
             |
             v
      +---------------+
      | Load Balancer |
      +-------^-------+
              |
       +-------+---------+-----------------+
       |                 |                 |
       v                 v                 v
+-------------+   +-------------+   +-------------+
|   Node 1    |   |   Node 2    |   |   Node 3    |
|  (Shard/Rep)|   | (Shard/Rep) |   | (Shard/Rep) |
+------^------+   +------^------+   +------^------+
       |                |                 |
       +----------Network-----------------+
```

- A load balancer distributes client requests among different nodes.
- Each node may hold a shard (partition) or a replica.

### Motivation

- The design supports expanding data volumes by incorporating additional nodes, with *Scalability* being a key attribute that enables the system to grow with demand.
- By strategically locating data closer to users and balancing loads, the architecture improves query speeds through targeted *Performance* enhancements.
- Redundant copies are implemented so that even when a node or site encounters issues, the service remains active, showcasing the system’s inherent *Reliability*.
- The network is organized to allow data access and storage in multiple regions, a setup that embraces *Geographical Distribution* to help reduce latency.

### Challenges

- Effective management of data replication across sites presents a challenge in achieving optimal *Data distribution* throughout the network.
- Handling simultaneous transactions across different nodes requires mechanisms that address *Concurrency control* to preserve data consistency.
- Coordinating updates across nodes to maintain ACID properties is complex, highlighting issues related to *Distributed transactions*.
- Robust recovery strategies are needed to manage potential node or network failures, which emphasizes the importance of *Fault tolerance* in system design.
- Integrating a variety of hardware, operating systems, and DBMS software into one environment necessitates resolving challenges associated with *Heterogeneity*.

### Distributed Database Architectures

#### Shared-Nothing, Shared-Disk, and Shared-Memory

I. **Shared-Nothing Architecture**  

- Each node has its own memory and disk storage.  
- Nodes communicate via a network.  
- Scales out by adding more nodes with local CPU, memory, and disk.  
- Widely used in large-scale systems (e.g., Google’s Bigtable, Cassandra, MongoDB clusters).

```
    +---------+         +---------+         +---------+
    | Node 1  |         | Node 2  |         | Node 3  |
    | CPU/Mem |         | CPU/Mem |         | CPU/Mem |
    | Disk    |         | Disk    |         | Disk    |
    +----^----+         +----^----+         +----^----+
         |                    |                   |
         |                    |                   |
         +--------- Network---+-------------------+
```

II. **Shared-Disk Architecture**  

- Each node has its own CPU and memory, but all share a common disk subsystem.  
- Often carried out via Storage Area Networks (SAN).  
- Coordination mechanisms (like distributed locking) are needed to avoid conflicts on the shared disk.

```
    +---------+   +---------+   +---------+
    | Node 1  |   | Node 2  |   | Node 3  |
    | CPU/Mem |   | CPU/Mem |   | CPU/Mem |
    +----^----+   +----^----+   +----^----+
         |           |            |
         +----+------+------+-----+
              |      |      |
              |    Shared   |
              |     Disk    |
              +-------------+
```

III. **Shared-Memory Architecture**  

- All nodes share the same memory and possibly the same disk.  
- Rarely used for large-scale, highly distributed systems due to scalability and contention.

```
      +------------------------+
      |      Shared RAM       |
      +---------+------+------+ 
                |      |
  +-------------v------v-------------+
  |   CPU 1   |   CPU 2   |  CPU 3   |
  | (Node 1)  | (Node 2)  | (Node 3) |
  +----------------------------------+
  |                                  |
  +----------- Shared Disk ----------+
```

#### Centralized vs. Decentralized Coordination

**Centralized Coordinator**

- One node acts as the coordinator for metadata (e.g., who owns which partition) and handles global tasks (e.g., transaction routing).  
- Simplifies coordination at the cost of potential bottlenecks and single-point-of-failure issues.

**Decentralized / Peer-to-Peer**  

- All nodes are peers, and they coordinate using distributed consensus or other mechanisms (e.g., gossip protocols).  
- Improves fault tolerance and eliminates single points of failure but is more complicated to carry out.

### Data Distribution Strategies

#### Replication

Replicating data means storing identical copies of data on different nodes. This can improve read performance and fault tolerance but complicates writes (since updates must be propagated).

I. **Synchronous Replication**  

- All replicas must be updated (or acknowledged) before a transaction is considered committed.  
- Makes sure strong consistency but may increase latency and reduce availability under network partitions.

II. **Asynchronous Replication**  

- The primary node commits a transaction first, and replicas are updated later.  
- Faster commit times, higher availability, but risk of “stale reads” (eventual consistency).

III. **Quorum-Based Replication**  

- A transaction commits if it reaches a certain subset of replicas (write quorum), and read operations read from a certain subset (read quorum).  
- Ties in with the CAP theorem and helps strike a balance among consistency, availability, and partition tolerance.

Example:

```
          +----------------+
          | Master (Node1) |
          +--------^-------+
                   |
           Synchronous/Async
                   |
        +----------v----------+
        |   Replica (Node2)   |
        +----------^----------+
                   |
           Synchronous/Async
                   |
        +----------v----------+
        |   Replica (Node3)   |
        +---------------------+
```

- **Master-Replica** setup: Node1 is the primary for writes, Node2 and Node3 receive replicated data.
- Could be synchronous (strong consistency) or asynchronous (eventual consistency).

#### Partitioning / Sharding

Partitioning distributes subsets (partitions or shards) of the data across multiple nodes.

I. **Horizontal Partitioning**  

- Rows of a table are split among nodes (by key range, hashing, or list partitioning).  
- Common in large-scale transactional systems.

II. **Vertical Partitioning**  

- Columns of a table are distributed among nodes.  
- Can be used to separate frequently accessed columns for performance.

III. **Functional / Entity-Based Partitioning**  

- Different tables or entities are distributed according to their usage patterns or business logic.  
- For example, user profiles on one node, transaction history on another.

Example:

```
 Table: USERS
 -----------------------------------------------------
 | user_id | name     | email             | ...
 -----------------------------------------------------

  Partition by user_id range:
     Shard A    Shard B    Shard C

  Shard A (Node 1): user_id < 10000
  Shard B (Node 2): 10000 <= user_id < 20000
  Shard C (Node 3): user_id >= 20000

 +----------+     +----------+     +----------+
 | Shard A  |     | Shard B  |     | Shard C  |
 | (Node 1) |     | (Node 2) |     | (Node 3) |
 +----^-----+     +----^-----+     +----^-----+
      |                |                |
      +--------- Network--------------->+
```

- Rows (by user_id range in this example) are placed on different nodes.  
- Each node stores only a portion of the table.

### Distributed Concurrency Control

Concurrency control makes sure correct, consistent results when multiple transactions execute simultaneously on different nodes.

#### Two-Phase Locking (2PL)

- **Phase 1 (Growing Phase)**: Transaction acquires the locks it needs (read or write locks).  
- **Phase 2 (Shrinking Phase)**: Once the first lock is released, no new locks can be acquired.  
- In a distributed context, each node manages its own lock manager. Deadlock detection or avoidance is more complicated because deadlocks can involve multiple nodes.

#### Timestamp Ordering

- Each transaction is given a global timestamp.  
- Operations are ordered based on timestamps.  
- Makes sure serializability by comparing the timestamps of transactions against the read/write timestamps of objects.

#### Optimistic Concurrency Control (OCC)

- Transactions execute without acquiring locks.  
- During **validation phase**, the system checks if conflicts exist.  
- If a conflict is detected, the transaction is aborted and re-executed.  
- Reduces locking overhead but can lead to high abort rates under contention.

### Distributed Transaction Management

#### ACID Properties

- The property of *Atomicity* ensures that each transaction is executed completely or not at all.
- Transactions adhere to *Consistency* by transitioning data between valid states without error.
- Concurrency is managed through *Isolation*, which prevents overlapping transactions from causing discrepancies.
- The feature of *Durability* guarantees that once transactions commit, their changes remain permanent even after system failures.

#### Two-Phase Commit (2PC)

- In the initial stage known as the *Prepare Phase*, the coordinator asks all nodes to get ready for a commit, with each node writing to stable storage and replying with a ready or no decision.
- During the subsequent stage called the *Commit Phase*, the coordinator issues a commit message if every participant is prepared, or initiates a rollback if any participant is not.
- Although this protocol is straightforward, it can lead to indefinite waiting if the coordinator fails, which calls for additional failure handling protocols.

```
           +------------------+
           |  Coordinator     |
           +------------------+
                  |     ^
Phase 1 (Prepare) |     | Phase 2 (Commit / Abort)
                  v     |
        +---------------------+
        | Participant (NodeA) |
        +---------------------+
                 |     ^
                 |     |
        +---------------------+
        | Participant (NodeB)|
        +---------------------+
```

I. **Phase 1 (Prepare)**:  

- Coordinator asks each participant if it can commit.  
- Participants reply “ready” or “no.”

II. **Phase 2 (Commit/Abort)**:  

- If *all* participants are ready, coordinator sends “commit.”  
- Otherwise, coordinator sends “abort.”

#### Three-Phase Commit (3PC)

- This protocol introduces an extra stage, referred to as *3PC*, which helps to mitigate the blocking issues that can occur in the two-phase commit process.
- While it is more complex than the two-phase method, the approach incorporates additional logs and timeout mechanisms to offer non-blocking guarantees under certain failure scenarios.

#### Distributed Consensus Protocols (Paxos, Raft)

- The protocol known as *Paxos* provides a method for achieving distributed consensus and is typically used in systems that operate replicated state machines.
- A more accessible alternative, *Raft*, separates the tasks of leader election from log replication, and it is frequently used in systems that require strong consistency guarantees.

### Fault Tolerance & Recovery

#### Failures in Distributed Systems

- Distributed systems may experience a *Site Failure* when a node crashes or becomes unreachable, impacting overall operations.
- Network issues can lead to a *Network Failure* that results in partitions or partial message loss across the system.
- Communication disruptions may occur due to *Communication Failures* where messages are delayed or corrupted during transmission.

#### Strategies for Fault Tolerance

- The system incorporates *Replication* by maintaining multiple data copies so that the failure of one node does not cause data loss.
- Extra hardware or software components are deployed to provide *Redundancy*, enabling a smooth takeover if one component fails.
- Heartbeat mechanisms are used for *Failure Detection* to promptly identify nodes that have crashed or become partitioned.
- Upon detecting faults, the system initiates *Reconfiguration* by electing new leaders, redirecting queries, or re-syncing data to restore normal operations.

#### Logging & Checkpointing

- A write-ahead log is maintained for *Log-based Recovery*, allowing the system to roll back or re-apply partial transactions if needed.
- The practice of *Checkpointing* involves periodically saving the database state to stable storage, which helps reduce recovery time.

### The CAP Theorem

#### Statement

In a distributed system, it is impossible to simultaneously guarantee:

- Every node displays identical data concurrently, a guarantee achieved through the principle of *Consistency* in the system.  
- The design ensures that every request gets a response, reflecting a commitment to *Availability* even when the data may not be the absolute latest.  
- Despite disruptions from network failures, the system continues to function smoothly due to its inherent *Partition tolerance*, which keeps operations running amid isolated segments.


```
         Consistency (C)
               /\
              /  \
             /    \
            /      \
Partition /         \ Availability
  Tolerance (P)       (A)
```

#### Implications

- Distributed systems must sacrifice one of Consistency or Availability in the presence of network partitions (which are inevitable).  
- This tradeoff leads to different design philosophies (e.g., CP systems emphasize consistency over availability; AP systems emphasize availability over consistency).

#### Brewer’s CAP vs. PACELC

- **PACELC** extends CAP by adding that “Else Latency or Consistency,” highlighting tradeoffs even when no partition exists.  
- It clarifies that systems choose how to balance latency and consistency during normal operation.

### Types of Distributed Databases

#### Homogeneous vs. Heterogeneous

I. **Homogeneous Distributed Database**  

- All nodes run the same DBMS software and schema.  
- Simpler to manage, but less flexible for integrating diverse systems.

II. **Heterogeneous Distributed Database**  

- Different nodes may run different DBMS software, possibly with different schemas or data models.  
- Integration requires data transformation or middleware layers.

#### Relational vs. NoSQL vs. NewSQL

I. **Relational Distributed Databases**  

- Traditional SQL-based systems extended for distributed operation (e.g., VoltDB, CockroachDB).  
- Typically aim for ACID compliance and can use 2PC or consensus protocols.

II. **NoSQL (Key-Value, Document, Column-Family, Graph)**  

- Focus on scalability and availability with relaxed consistency.  
- Examples: Cassandra (AP-oriented), MongoDB (eventual/strong consistency modes), HBase/Bigtable (column-store), Neo4j (graph).

III. **NewSQL**  

- Combines the scalability of NoSQL with the ACID guarantees of relational systems.  
- Examples: Spanner (global transactions, strong consistency), CockroachDB (ACID over a distributed cluster).

### Practical Design Considerations

#### Query Processing & Optimization

- The system uses *cost-based distributed query optimizers* that evaluate the expense of transferring data among nodes to choose an efficient execution plan.
- Computation is shifted closer to where data resides through the technique of *data localization*, which minimizes the need for extensive data movement.
- Various join methods, such as broadcast join, shuffle join, or partitioned join, are employed based on the underlying patterns of *data distribution*.

#### Caching Strategies

- Frequently accessed information is stored via *client-side caching*, which helps reduce network overhead while requiring proper invalidation or expiration policies.
- Servers maintain a local store of popular data using *server-side caching*, which can improve response times and lower the load on the system.
- A coordinated approach is adopted in *global caching*, where distributed cache layers like Redis clusters ensure consistency across different nodes.

#### Security

- The system ensures that only trusted sources issue distributed queries through robust *authentication and authorization* processes.
- Secure communication is maintained by using industry-standard protocols for *encryption*, protecting both data in transit and data at rest.
- Privacy compliance is supported by applying *data masking* techniques or tokenization to protect sensitive information in distributed environments.

#### Monitoring & Observability

- Tracking queries across multiple nodes is made possible with *distributed tracing* tools, such as OpenTracing or OpenTelemetry, which help reveal performance bottlenecks.
- System health is continuously assessed by collecting a variety of metrics through *metrics and logging*, which monitor resources like CPU, memory, throughput, latency, and error rates.

### Summary of Tradeoffs and Principles

- Distributed systems must balance the trade-off between *Consistency*—where all nodes display identical data simultaneously—and high availability, which may sometimes compromise the immediacy of data updates.
- In replication strategies, the system's design is influenced by *Latency*, as favoring faster responses can lead to less immediate durability compared to approaches that emphasize strict synchronization.
- Architects often evaluate *Simplicity* against scalability, choosing between a centralized system that is easier to manage and a decentralized approach that supports growth.
- Certain applications demand *Strong Consistency* to ensure precise data correctness, even if this choice may impact read and write performance compared to eventual consistency models.
- When designing the overall architecture, the decision to implement a *Homogeneous* environment is weighed against integrating diverse systems, with each option offering distinct operational benefits.
