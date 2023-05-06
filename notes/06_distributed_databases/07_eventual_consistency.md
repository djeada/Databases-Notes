## Eventual consistency 
Eventual consistency is a consistency model used in distributed databases, where updates to the data may not be immediately visible to all nodes in the system, but will eventually propagate to all nodes and become consistent. This note focuses on the concept of eventual consistency, its advantages and trade-offs, and its implications for distributed database systems.

## Characteristics

### Weak Consistency Model
1. Eventual consistency is a weak consistency model compared to strong consistency models, such as linearizability or strict serializability.
2. In eventual consistency, the system does not guarantee that all updates are immediately visible to all nodes, allowing for temporary inconsistencies.

### Update Propagation
1. Updates to the data will eventually propagate to all nodes, ensuring that the system becomes consistent over time.
2. The time it takes for updates to propagate depends on factors such as network latency, replication mechanisms, and system load.

## Advantages

### High Availability
1. Eventual consistency allows for high availability, as nodes can continue to operate even when some replicas are not up-to-date.
2. In the case of network partitions or node failures, the system can still provide read and write access to the data, ensuring continued operation.

### Improved Performance
By allowing for temporary inconsistencies, eventual consistency can lead to improved performance, as updates can be applied locally without waiting for global synchronization.

### Scalability
Eventual consistency enables better scalability in distributed systems, as nodes can operate independently without requiring constant coordination.

## Trade-offs

### Temporary Inconsistencies
1. Eventual consistency allows for temporary inconsistencies, which may lead to stale reads or outdated data being returned to clients.
2. Applications must be designed to handle these inconsistencies and ensure correct operation even when dealing with stale or outdated data.

### Conflict Resolution
1. In eventual consistency, conflicts can arise when multiple nodes update the same data simultaneously. Conflict resolution mechanisms, such as version vectors or conflict-free replicated data types (CRDTs), must be employed to ensure eventual consistency.

## Use Cases

1. Eventual consistency is well-suited for applications where high availability, performance, and scalability are more important than immediate consistency.
2. Examples include large-scale distributed systems, such as social media platforms, collaborative editing tools, or content delivery networks (CDNs).
