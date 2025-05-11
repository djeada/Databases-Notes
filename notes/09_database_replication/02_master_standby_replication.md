## Master-Standby Replication

Master-Standby replication is a widely adopted database replication topology where a primary database server, known as the master, replicates data to one or more secondary servers called standbys. This setup enhances data availability, fault tolerance, and load balancing within a database system. Standby servers can handle read-only queries and, in case of a master server failure, can be promoted to become the new master, ensuring continuous operation.

### Understanding the Architecture

To visualize how Master-Standby replication works, consider the following diagram:

```
#
               +---------------------+
               |                     |
               |      Clients        |
               | (Write & Read Ops)  |
               |                     |
               +----------+----------+
                          |
           +--------------+--------------+---------------------------------+
           |                             |                                 |
 Write & Read Operations           Read Operations                   Read Operations
           |                             |                                 |
           v                             v                                 v
+----------+-----------+       +---------+----------+            +---------+----------+
|                      |       |                    |            |                    |
|    Master Server     |       |  Standby Server 1  |            |  Standby Server 2  |
|                      |       |  (Read-Only)       |            |  (Read-Only)       |
+----------+-----------+       +---------+----------+            +---------+----------+
           |                             ʌ                                 ʌ
           |                             |                                 |
           |                         Replication                       Replication
           |                             |                                 |
           +-----------------------------+---------------------------------+
```

In this architecture, the master server handles all write operations, such as inserts, updates, and deletes. The standby servers continuously receive data changes from the master to stay synchronized and can serve read-only queries, offloading read traffic from the master. This arrangement not only improves performance but also provides a failover mechanism in case the master server becomes unavailable.

### The Purpose of Master-Standby Replication

Master-Standby replication serves several essential purposes in database systems:

1. By replicating data to standby servers, the system can prevent data loss and minimize downtime during failures. If the master server fails, a standby can be promoted to take over, ensuring uninterrupted service.
2. Offloading read-heavy operations to standby servers distributes the workload more evenly, enhancing performance and scalability. This allows the master server to focus on write operations without being overwhelmed.
3. Regular maintenance tasks, such as backups or software updates, can be performed on the master or standby servers without significant downtime. Standby servers can be updated one at a time, providing continuous service to users.
4. As demand on the database grows, additional standby servers can be added to handle increased read traffic. This horizontal scaling is a cost-effective way to enhance system capacity without overhauling the existing infrastructure.

### Advantages

Implementing Master-Standby replication offers several benefits:

- With standby servers acting as backups, the risk of data loss is significantly reduced. In the event of a failure, a standby can quickly take over as the master.
- Distributing read queries to standby servers alleviates the load on the master server, resulting in faster response times for users.
- The ability to promote a standby server to master simplifies the failover process, minimizing service interruptions and ensuring business continuity.
- Continuous replication ensures that data remains consistent across all servers, maintaining data integrity throughout the system.

### Challenges

Despite its advantages, Master-Standby replication presents some challenges:

- Standby servers may not always be perfectly synchronized with the master, leading to potential stale reads. This **lag** can be problematic for applications requiring real-time data.
- Promoting a standby to master requires careful **coordination** to prevent data inconsistencies. Automated failover mechanisms need to be thoroughly tested to ensure reliability.
- Since only the master handles write operations, applications with heavy write loads may face scalability issues. The master server can become a **bottleneck** if not properly managed.
- Setting up and managing replication involves intricate configurations and ongoing monitoring. Administrators need to be skilled in replication technologies to maintain the system effectively.

### Implementing in PostgreSQL

PostgreSQL offers built-in support for streaming replication, making it a suitable choice for implementing Master-Standby replication. Below is a practical example of how to set up this replication using PostgreSQL.

```text
Topology:
                           ┌──────────────────────────┐
                           │  ┌────────────────────┐  │
                           │  │  Master / Primary  │  │
                           │  │  Node-1 10.0.0.10  │  │
                           │  └─────────┬──────────┘  │
                           │            │             │
                           │   (async or synchronous) │
                           │            │             │
   ┌───────────────────────▼────────────┴─────────────▼────────────────────┐
   │                                                                       │
   │  ┌────────────────────┐                       ┌────────────────────┐  │
   │  │  Replica-1         │                       │  Replica-2         │  │
   │  │  Node-2 10.0.0.11  │      Streaming        │  Node-3 10.0.0.12  │  │
   │  │  (Hot-Standby)     │ <--- Replication ---> │  (Hot-Standby)     │  │
   │  └────────────────────┘                       └────────────────────┘  │
   └───────────────────────────────────────────────────────────────────────┘
```

> **Legend** – We will call the nodes **Node-1 (master)**, **Node-2 (replica-1)** and **Node-3 (replica-2)** throughout.
> Keep the diagram handy: configuration snippets below reference the IPs exactly as shown.

#### Prerequisites

- **Three PostgreSQL instances installed** (same major version) on *10.0.0.10*, *10.0.0.11*, *10.0.0.12*.
- **Network reachability** – TCP 5432 open bidirectionally (replicas must also talk *back* to the master for `pg_basebackup`).
- **Time synchronisation** – enable `chrony`/`ntpd`; replication breaks if clocks drift.
- **Adequate resources** – WAL can spike; leave at least 30 % free disk on the master.
- **Linux tuning (recommended)** – increase `vm.swappiness = 1`, set `kernel.shmmax` ≥ shared\_buffers, etc.

#### Configuring Node-1 (Master)

Before setting up physical replication, you need to prepare the primary server (Node-1) by adjusting its configuration to enable write-ahead logging (WAL) streaming and accept connections from standby servers. This section walks you through the required changes to PostgreSQL's configuration files and the creation of a replication role.

I. Config file

As the master, Node-1 must generate and retain sufficient WAL segments for standby servers to consume. Update `postgresql.conf` with appropriate settings.

```conf
# Enable WAL suitable for physical replication
wal_level               = replica          # 'logical' if you also need logical slots
# Allow enough WAL sender processes for your standby servers
max_wal_senders         = 10               # >= number of stand-bys + maintenance head-room
# Maintain replication slots to prevent WAL removal too early
max_replication_slots   = 10               # same logic as above
# Keep enough WAL files to let standbys catch up without recycling
wal_keep_size           = 512MB            # prevents WAL recycling before stand-bys catch up
# Listen only on the master’s address (or '*' to trust all)
listen_addresses        = '10.0.0.10'      # or '*' if all IPs are trusted
# Choose commit behavior: local yields speed; remote_apply ensures sync
synchronous_commit      = local            # change to 'remote_apply' for synchronous sets
```

> **Tip** – From v15 onward you can use `min_wal_size`/`max_wal_size` instead of a fixed `wal_keep_size` to auto-scale WAL retention.

II. `pg_hba.conf`

Standby servers must be allowed to connect for replication. Add entries to `pg_hba.conf` specifying the replication database, user, and host addresses.

```conf
# TYPE  DATABASE        USER        ADDRESS            METHOD
host    replication     replicator  10.0.0.11/32       md5
host    replication     replicator  10.0.0.12/32       md5
```

III. Create the replication role

A dedicated role with replication privileges is required for streaming WAL to standbys. Execute the following SQL on the master:

```sql
CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'S3cUr3P@ss!';
```

IV. Reload / restart Node-1

After updating configuration files and creating the role, reload or restart PostgreSQL to apply changes.

```bash
sudo systemctl restart postgresql
```

#### Configuring Node-2 and Node-3 (Replicas)

Once the master is prepared, each standby (Node-2 and Node-3) needs to be bootstrapped from a base backup and configured to stream WAL. You will perform the same steps on both replicas, adjusting only the connection details as needed.

I. Stop PostgreSQL

Ensure PostgreSQL is not running on the replica before taking the base backup or restoring data.

```bash
sudo systemctl stop postgresql
```

II. Take a base-backup from the master

Use `pg_basebackup` to clone the primary’s data directory, stream WAL, and automatically write recovery settings.

```bash
sudo -u postgres pg_basebackup \
  -h 10.0.0.10 \
  -D /var/lib/pgsql/15/data \
  -U replicator \
  -W -P --wal-method=stream --write-recovery-conf
```

*The `--write-recovery-conf` switch auto-creates `standby.signal` and fills in `primary_conninfo`.*

III. (If you skipped `--write-recovery-conf`) edit `postgresql.conf`

Manually enable hot standby mode and configure connection to the master, specifying the replication slot unique to each standby.

```conf
hot_standby          = on
primary_conninfo     = 'host=10.0.0.10 port=5432 user=replicator password=S3cUr3P@ss!'
primary_slot_name    = 'node2_slot'     # unique per standby (see slots below)
```

If needed, create the standby signal file to trigger recovery mode (PostgreSQL v12+):

```bash
touch /var/lib/pgsql/15/data/standby.signal
```

IV. Start the replica

With configuration in place, start PostgreSQL on the standby to begin streaming WAL from the master.

```bash
sudo systemctl start postgresql
```

#### Verifying Replication

After configuring both master and standbys, you should verify that WAL streaming is active and data changes propagate as expected. This section covers querying replication status and performing a simple functional test.

I. On **Node-1**

Check the replication status view on the master to confirm standbys are connected and streaming.

```sql
SELECT client_addr, state, sync_state
FROM   pg_stat_replication;
```

You should see rows for **10.0.0.11** and **10.0.0.12** with `state = streaming`. If you configured synchronous replication (`synchronous_standby_names`, `synchronous_commit = remote_apply`) the `sync_state` column will be `sync` for the chosen stand-bys.

II. Functional test

Perform a simple create-and-read test to confirm that changes on the master appear on the replica almost immediately.

```sql
-- Master (10.0.0.10)
CREATE TABLE replication_test (id SERIAL PRIMARY KEY, data TEXT);
INSERT INTO replication_test (data) VALUES ('Hello replicas');

-- Replica (10.0.0.11 or .12)
SELECT * FROM replication_test;  -- should return 1 row almost instantly
```

#### Performing a Fail-over

In a production environment, you need a plan for promoting a standby to master when the primary fails. This section outlines a manual fail-over process, though automation tools can streamline detection and promotion.

I. **Detect failure** of Node-1 (often automated with Patroni, pg\_auto\_failover, etc.).

II. **Promote** Node-2 (example)

```bash
sudo -u postgres pg_ctl promote -D /var/lib/pgsql/15/data
```

or

```bash
touch /var/lib/pgsql/15/data/promote.signal
```

III. **Redirect applications** to the new master (10.0.0.11).

IV. **Re-configure the old master** (once repaired) as a replica: wipe its data dir, repeat the “Replica” steps, giving it a new slot (`node1_as_replica_slot`).

#### Optional: Replication Slots (Highly Recommended)

Replication slots ensure that WAL segments needed by a standby are retained on the master until they have been safely replayed. This prevents standbys from falling too far behind and losing data.

On **Node-1**:

```sql
SELECT pg_create_physical_replication_slot('node2_slot');
SELECT pg_create_physical_replication_slot('node3_slot');
```

Then, on each replica’s `postgresql.conf`, match the slot:

```conf
primary_slot_name = 'node2_slot'   # or node3_slot accordingly
```

Slots guarantee that WAL remains available until every replica has replayed it—preventing the dreaded “requested WAL segment has already been removed”.

#### Extra Hardening & Performance Tweaks

Beyond basic replication, additional configuration can improve resilience, disaster recovery capabilities, and performance. Consider these settings as part of a hardened, high-availability setup:

| Setting                                 | Why it matters (refer to ASCII diagram for scope)                    |
| --------------------------------------- | -------------------------------------------------------------------- |
| `checkpoint_timeout = 15min`            | Longer intervals reduce I/O on Node-1; ensure replicas can catch up. |
| `archive_mode = on` + `archive_command` | Off-site WAL shipping for disaster recovery beyond Node-2 & Node-3.  |
| `hot_standby_feedback = on`             | Stops long-running queries on replicas from causing bloat on master. |
| `backup_label` & `recovery_target`      | For point-in-time restores (PITR) if required.                       |
