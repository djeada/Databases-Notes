## Database replication
Database replication is a technique used to maintain multiple copies of data across different database instances or locations. This note focuses on the concept of database replication, its purpose, types, and implementation considerations.

## Purpose of Database Replication

### High Availability

1. Replication helps ensure high availability by providing redundant copies of data, allowing database systems to continue functioning even if one instance or location becomes unavailable.
2. High availability helps minimize downtime and ensures data can be accessed at all times.

### Load Balancing

1. By distributing data across multiple instances or locations, replication can help balance the workload among multiple database servers.
2. Load balancing can improve database performance by reducing the load on individual servers and preventing bottlenecks.

### Backup and Disaster Recovery

1. Replication can be used as a backup strategy to maintain up-to-date copies of data in separate locations.
2. In the event of a disaster or data loss, the replicated data can be used to restore the affected database system.

### Distributed Data Processing

1. Replication can facilitate distributed data processing by allowing data to be stored closer to the users or applications that access it.
2. This can help improve performance and reduce latency for users and applications.

## Types of Database Replication

### Synchronous Replication

1. In synchronous replication, data is written to the primary database and all replica databases simultaneously before the transaction is considered complete.
2. This ensures strong consistency among replicas but can introduce latency in write operations due to the need to wait for all replicas to acknowledge the write.

### Asynchronous Replication

1. In asynchronous replication, data is written to the primary database first, and changes are propagated to the replica databases at a later time.
2. This allows for faster write operations and reduced latency, but can result in temporary inconsistencies between the primary and replica databases.

### Snapshot Replication

1. Snapshot replication involves periodically capturing a snapshot of the data in the primary database and applying it to the replica databases.
2. This method is suitable for scenarios where data does not change frequently or where consistency between replicas is not a critical requirement.

## Implementation Considerations

### Replication Topology

1. The replication topology determines the relationships between the primary and replica databases.
2. Common replication topologies include master-slave, multi-master, and peer-to-peer.

### Conflict Resolution

1. In scenarios where multiple replicas can be updated independently, conflicts may arise when changes are propagated.
2. Conflict resolution strategies include timestamp-based resolution, user-defined conflict resolution, and manual intervention.

### Monitoring and Failover

1. Monitoring the health and performance of the replicated databases is essential to ensure data consistency and availability.
2. Automated failover mechanisms can be used to switch to a replica database in case the primary database becomes unavailable.
