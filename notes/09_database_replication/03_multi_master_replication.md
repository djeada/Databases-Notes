## Multi-Master Replication

Multi-master replication is a database replication model where multiple database nodes, referred to as masters, can perform read and write operations concurrently. Each master node propagates its data changes to every other master node, ensuring consistency across the entire system. This approach enhances scalability, availability, and performance but introduces complexities like conflict resolution and increased configuration overhead.

### Understanding the Architecture

To visualize how multi-master replication works, consider the following ASCII diagram:

```
#
               +---------------------+
               |                     |
               |      Clients        |
               | (Write & Read Ops)  |
               |                     |
               +----------+----------+
                          |
           +--------------+---------------------+----------------------------------+
           |                                    |                                  |
 Write & Read Operations                 Write & Read Operations           Write & Read Operations  
           |                                    |                                  |
           v                                    v                                  v
+----------+-----------+              +---------+----------+             +---------+----------+
|                      | Replication  |                    | Replication |                    |
|    Master Server     | ---------->  |   Master Server    | ----------> |   Master Server    |
|                      | <----------  |                    | <---------- |                    |
+----------+-----------+              +---------+----------+             +---------+----------+
```

In this setup, each master node is connected to every other master node through replication links. Data changes made on any node are replicated to all other nodes, and clients can connect to any master node for both read and write operations. This interconnected architecture allows for a highly available and scalable system.

#### Characteristics

Multi-master replication has several defining features:

- All master nodes can accept write operations simultaneously.
- Changes made on one master are replicated to others to maintain data consistency.
- The system remains operational even if one or more master nodes fail, providing high availability.
- Mechanisms are required to handle conflicting updates due to concurrent writes, which adds complexity to the system.

#### Purpose of Multi-Master Replication

The primary goals of multi-master replication include:

1. By distributing the write load across multiple nodes, the system can handle higher transaction volumes without a single point becoming a bottleneck.
2. With multiple masters, the system continues to operate even if one master fails, offering redundancy and resilience.
3. In geographically dispersed systems, allowing writes to the nearest master reduces latency and improves performance for users in different locations.
4. Balancing both read and write operations across multiple nodes optimizes resource utilization and prevents any single node from becoming overwhelmed.

### Advantages

Implementing multi-master replication offers several benefits:

- Supports higher write throughput by allowing multiple nodes to handle write operations concurrently.
- Eliminates single points of failure, enhancing the system's resilience since other masters can take over if one fails.
- Localized writes reduce the delay associated with remote database access, providing faster response times for users.
- Distributes workloads across multiple nodes, preventing bottlenecks and optimizing performance.

### Challenges

Despite its advantages, multi-master replication introduces several challenges:

- Concurrent writes to the same data can cause conflicts. Mechanisms must be in place to detect and resolve these conflicts appropriately.
- Ensuring strong consistency across nodes can be complex and may impact performance, especially in systems with high latency between nodes.
- Configuring, managing, and monitoring a multi-master setup is more complicated than single-master configurations.
- Replicating data across multiple nodes increases network traffic, which can affect performance if not managed properly.

### Conflict Resolution Strategies

Handling conflicts is a critical aspect of multi-master replication. Various strategies can be employed:

- **Synchronous replication** ensures data consistency by using **locking mechanisms** that allow only one node to modify a specific piece of data at any given time. This approach can result in reduced performance due to increased latency caused by waiting for acknowledgments from other nodes.  
- **Asynchronous replication** with **conflict detection** improves performance by allowing changes to proceed without waiting for all nodes to acknowledge. However, it introduces the risk of **temporary inconsistencies**, which are resolved later through conflict detection and resolution mechanisms.  
- **Timestamp ordering** resolves conflicts by prioritizing **transactions** based on their timestamps, where the **latest transaction** overrides previous ones. This method simplifies resolution but may discard earlier valid changes.  
- **Application-level handling** uses **custom logic** defined within the application to resolve conflicts. This approach provides **flexibility**, enabling conflict resolution tailored to the specific needs and business logic of the application.

### Implementing Multi-Master Replication with MySQL / MariaDB + Galera Cluster

Galera Cluster is a synchronous multi-master replication plugin for MySQL and MariaDB databases. It ensures that transactions are committed on all nodes simultaneously, providing strong data consistency across the cluster.

```text
#
                 ┌────────────────────────────┐
                 │  Galera  Quorum  Network   │
                 └────────────┬───────────────┘
                              │ (TCP 4567)
        ┌─────────────────────┴─────────────────────┐
        │                                           │
┌───────▼────────┐                         ┌────────▼────────┐
│  Node-1        │                         │  Node-2         │
│  10.0.0.20     │ ←───◀──────────────►───→│  10.0.0.21      │
│  (Master*)     │    │  synchronous   │   │  (Master*)      │
└───────┬────────┘    │  replication   │   └────────┬────────┘
       │              │  (4567/4568/   │            │
       │              │   4444)        │            │
       │              ▼─────────────►──┘            │
┌───────▼────────┐                         ┌────────▼────────┐
│  Node-3        │─────────────────────────► 10.0.0.22       │
│  10.0.0.22     │         (Full Mesh)     │  (Master*)      │
│  (Master*)     │                         │                 │
└────────────────┘                         └─────────────────┘
```

> **Legend** – All three nodes act as *masters* (“writer-writers”).
> Traffic flows in a full-mesh using the Galera ports **4567 (replication)**, **4568 (incremental SST/IST)** and **4444 (state snapshot transfer)**.
> When you see `10.0.0.20/21/22` or **Node-1/2/3** below, they refer to the diagram.

#### Prerequisites

1. **Three Linux hosts** (Ubuntu 22.04 LTS, Debian 12, RHEL 9, etc.) with static IPs `10.0.0.20-22`.
2. **MariaDB 10.6+** *or* **Percona XtraDB / MySQL-wsrep** build that ships Galera 4.
3. **Open firewall**: TCP 3306 (MySQL client), TCP 4567 (replication), TCP 4568 (incremental state), TCP 4444 (full SST)
4. **Time sync** via `chronyd` or `systemd-timesyncd`.
5. At least **2 CPU / 4 GiB RAM / 30 GiB SSD** per node (Galera buffers and gcache like RAM + IO).

#### Install Server & Galera

**Ubuntu / Debian**

```bash
sudo apt update
sudo apt install mariadb-server galera-4 rsync
```

**RHEL / CentOS**

```bash
sudo dnf install mariadb-server galera-4 rsync
```

*(Replace `mariadb-…` with Percona packages if you need MySQL-8 compatibility.)*

#### Core Configuration

The foundation of a stable Galera cluster is consistent configuration across all nodes. This section outlines the essential parameters you must set in the Galera configuration file to enable multi-master replication, ensure data consistency, and tune basic performance settings.

`/etc/mysql/conf.d/60-galera.cnf` or `/etc/my.cnf.d/galera.cnf`

```ini
[mysqld]
# ==== Basic ====
bind-address            = 0.0.0.0
default_storage_engine  = InnoDB
binlog_format           = ROW              # mandatory
innodb_autoinc_lock_mode= 2                # mandatory for multi-master

# ==== Galera ====
wsrep_on                = ON
wsrep_provider          = /usr/lib/galera/libgalera_smm.so

wsrep_cluster_name      = my_galera_cluster
wsrep_cluster_address   = gcomm://10.0.0.20,10.0.0.21,10.0.0.22

# ---- Node-specific (edit on every host) ----
wsrep_node_name         = node1            # node2 / node3 respectively
wsrep_node_address      = 10.0.0.20        # 10.0.0.21 / 10.0.0.22

# State Snapshot Transfer (full clone)
wsrep_sst_method        = rsync            # mariabackup is faster for TB-scale
wsrep_sst_auth          = sstuser:s3cr3t!  # will create below

# Performance / flow-control
innodb_buffer_pool_size = 2G               # ≥40 % RAM (adjust)
wsrep_slave_threads     = 4                # = CPU cores (rule of thumb)
```

#### Creating the SST User

To securely transfer the initial dataset from the primary node to joining nodes, Galera uses a State Snapshot Transfer (SST) user. Create and grant the necessary privileges once on any cluster node.

```bash
mysql -u root <<'SQL'
CREATE USER 'sstuser'@'%' IDENTIFIED BY 's3cr3t!';
GRANT RELOAD, LOCK TABLES, PROCESS, REPLICATION CLIENT ON *.* TO 'sstuser'@'%';
FLUSH PRIVILEGES;
SQL
```

#### Securing the Server

Before bringing up the cluster, tighten the default MariaDB security posture. Run the secure installation script to set a strong root password, remove unused accounts, and disable remote root access.

```bash
sudo mysql_secure_installation   # set root pwd, remove test DB, disallow remote root
```

#### Bootstrapping the Cluster (Node-1)

The first node must be started in bootstrap mode to initialize the cluster state. This step only runs once and sets up the initial primary component.

```bash
sudo systemctl stop mariadb
sudo galera_new_cluster           # or: mysqld --wsrep-new-cluster &
```

Verify that the cluster is running and contains only the bootstrap node:

```bash
mysql -e "SHOW GLOBAL STATUS LIKE 'wsrep_cluster_size';"
# Expect Value = 1
```

#### Joining Remaining Nodes (Node-2 & Node-3)

Subsequent nodes join the existing cluster by starting their MariaDB service. They will perform an SST from the primary node to synchronize state before becoming active members.

```bash
sudo systemctl start mariadb
```

Monitor the SST process in real time with:

```bash
journalctl -u mariadb -f
```

Once complete, verify every node sees the full cluster:

```bash
mysql -e "SHOW GLOBAL STATUS LIKE 'wsrep_cluster_size';"
# Expect Value = 3 on every node
```

#### Conflict Resolution & Certification

Galera uses optimistic concurrency control and write-set certification to resolve conflicts in a synchronous multi-master setup. At commit time, write-sets are broadcast and validated against each node's transaction history.

1. **Optimistic execution** – transactions execute locally on the origin node.
2. **Write-set creation** – at commit, row changes are packaged into a write-set.
3. **Synchronous certification** – write-set is sent to all nodes; each node checks version vectors.
* **No conflict** → write-set applied, client receives COMMIT.
* **Conflict** → later GTID wins, losing node rolls back and returns WSREP\_CONFLICT error.

##### Application Strategies

Proper application design can minimize and handle conflicts:

* **Automatic retries** – catch SQL errno 1213 (deadlock) and retry critical transactions.
* **Hot-spot mitigation** – avoid sequential key updates; shard counters across nodes.
* **Deterministic primary keys** – use UUIDs or configure `auto_increment_offset` and `auto_increment_increment` to prevent PK clashes.

#### Testing the Cluster

Validate cluster behavior under different scenarios to ensure reliability. The table below outlines core tests and expected outcomes.

| Test            | Procedure (refer to Node IPs)                                             | Expected result                                      |
| --------------- | ------------------------------------------------------------------------- | ---------------------------------------------------- |
| **Consistency** | `INSERT` on Node-1 → `SELECT` on Node-2/3                                 | Rows visible in < 1 s                                |
| **Conflict**    | Begin two sessions, `UPDATE` the same row concurrently on Node-2 & Node-3 | One session commits, other gets errno 1213           |
| **Failover**    | `systemctl stop mariadb` on Node-1                                        | Cluster size drops to 2, writes continue on Node-2/3 |
