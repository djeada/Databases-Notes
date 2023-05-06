## Multi-Master replication
Multi-Master replication is a replication topology where multiple databases act as masters, allowing write operations on each master. This note focuses on the concept of Multi-Master replication, its purpose, advantages, and challenges.

## Multi-Master Replication Overview

### Purpose

1. Improve write performance by distributing write operations across multiple masters.
2. Enhance high availability and fault tolerance by allowing applications to continue operating even if one master fails.
3. Facilitate load balancing for both read and write operations.

### Advantages

1. Increased write scalability compared to single-master setups.
2. Improved fault tolerance due to the presence of multiple writable masters.
3. Reduced latency for write operations, especially in geographically distributed setups, as clients can write to the nearest master.

### Challenges

1. Conflict resolution: When multiple masters receive conflicting updates, a conflict resolution mechanism is required to ensure data consistency.
2. Increased complexity: Multi-master replication is more complex to set up, manage, and monitor compared to single-master replication.
3. Potential for reduced consistency: Depending on the conflict resolution strategy, data consistency across masters may be affected.

## Example: MySQL with Galera Cluster

### Introduction

Galera Cluster is a synchronous multi-master replication solution for MySQL and MariaDB databases. It provides a transparent, synchronous replication mechanism that allows write operations on any node in the cluster.

### Setup

1. Install Galera Cluster software on each master node.
2. Configure MySQL or MariaDB on each master node.
3. Configure the Galera Cluster settings in the MySQL or MariaDB configuration file (e.g., `my.cnf`) on each master node.
4. Start the Galera Cluster by bootstrapping the first node and joining the other nodes to the cluster.

### Conflict Resolution

1. Galera Cluster uses a certification-based approach to handle conflicts.
2. Each write transaction is assigned a global transaction ID (GTID).
3. Before committing, the transaction is checked against other concurrent transactions. If no conflicts are detected, the transaction is certified and applied to all nodes.
4. If a conflict is detected, the transaction with the lower GTID is aborted, and the client receives a deadlock error
