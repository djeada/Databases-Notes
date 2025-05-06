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

#### Prerequisites

Before beginning the setup, ensure the following:

- PostgreSQL servers should be set up with at least one master server and one or more standby servers to establish a proper replication setup.  
- The network configuration must allow communication between the servers, ensuring that the required ports for PostgreSQL replication are open and accessible.  
- All servers involved in the setup should run compatible versions of PostgreSQL, ideally the same version, to maintain consistency and avoid compatibility problems.  
- The servers should have sufficient hardware resources, including CPU, memory, and disk space, to handle the expected workload and accommodate replication overhead.  

#### Configuring the Master Server

##### Editing `postgresql.conf`

Locate and edit the `postgresql.conf` file, typically found in the data directory (e.g., `/var/lib/pgsql/data/` or `/etc/postgresql/`). Modify the following parameters to enable replication:

```conf
# Enable Write-Ahead Logging (WAL) level suitable for replication
wal_level = replica

# Allow the master to send WAL data to standby servers
max_wal_senders = 3

# Set the maximum number of replication slots (optional)
max_replication_slots = 3

# Retain WAL data to assist standby synchronization
wal_keep_size = 128MB
```

##### Editing `pg_hba.conf`

Update the `pg_hba.conf` file to allow the standby servers to connect for replication. Add the following line:

```conf
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# Allow replication connections from standby servers
host    replication     replicator      standby_ip/32           md5
```

Replace `replicator` with the username of the replication role and `standby_ip/32` with the IP address of the standby server.

##### Creating a Replication User

Log into the PostgreSQL prompt on the master server and create a user for replication:

```sql
CREATE ROLE replicator WITH REPLICATION LOGIN ENCRYPTED PASSWORD 'your_password';
```

This user will be used by the standby servers to authenticate with the master.

##### Restarting PostgreSQL

Restart the PostgreSQL service on the master server to apply the configuration changes:

```bash
# For Linux systems using systemd
sudo systemctl restart postgresql
```

#### Configuring the Standby Server

##### Stopping the PostgreSQL Service

Ensure that the PostgreSQL service on the standby server is stopped before proceeding:

```bash
sudo systemctl stop postgresql
```

##### Creating a Base Backup from the Master

Use the `pg_basebackup` utility to create a base backup of the master server on the standby server:

```bash
pg_basebackup -h master_ip -D /var/lib/pgsql/data/ -U replicator -W -P --wal-method=stream
```

| Option                     | Description                                   |
|----------------------------|-----------------------------------------------|
| `-h master_ip`         | The IP address of the master server.         |
| `-D /var/lib/pgsql/data/` | The data directory on the standby server.   |
| `-U replicator`       | The replication user created earlier.        |
| `-W`                   | Prompt for the password.                     |
| `--wal-method=stream`  | Stream WAL files during the backup.          |

##### Creating the `standby.signal` File

For PostgreSQL versions 12 and above, create an empty file named `standby.signal` in the data directory to indicate that this server should start in standby mode:

```bash
touch /var/lib/pgsql/data/standby.signal
```

For versions before 12, a `recovery.conf` file is required with the necessary parameters.

##### Editing `postgresql.conf` on the Standby

Set the following parameters in the standby server's `postgresql.conf` file:

```conf
# Enable read-only queries on standby
hot_standby = on

# Configure connection information to the primary server
primary_conninfo = 'host=master_ip port=5432 user=replicator password=your_password'
```

Replace `master_ip` with the IP address of the master server and `your_password` with the password for the replication user.

##### Starting the PostgreSQL Service

Start the PostgreSQL service on the standby server:

```bash
sudo systemctl start postgresql
```

#### Verifying Replication

##### Checking Replication Status on the Master

Connect to the master server and execute the following SQL query to check the replication status:

```sql
SELECT client_addr, state
FROM pg_stat_replication;
```

This should display an entry for each standby server, indicating that they are connected and replicating.

##### Testing Data Replication

On the master server, create a test table and insert data:

```sql
-- Create a test table
CREATE TABLE replication_test (id SERIAL PRIMARY KEY, data TEXT);

-- Insert sample data
INSERT INTO replication_test (data) VALUES ('Test data');
```

On the standby server, query the test table to confirm that the data has been replicated:

```sql
-- Select data from the replicated table
SELECT * FROM replication_test;
```

If the data appears on the standby server, replication is working correctly.

#### Performing a Failover Procedure

In the event that the master server fails, you can promote a standby server to become the new master.

##### Promoting the Standby to Master

On the standby server, run the following command to promote it:

```bash
pg_ctl promote -D /var/lib/pgsql/data/
```

Alternatively, you can create a `promote.signal` file in the data directory:

```bash
touch /var/lib/pgsql/data/promote.signal
```

This action transitions the standby server to accept write operations.

##### Updating Application Connections

Redirect your application's database connections to the new master server to resume normal operations.

##### Reconfiguring the Failed Master as a Standby (Optional)

Once the original master server is operational again, you can configure it as a standby to the new master, ensuring it remains part of the replication setup.

#### Handling Replication Slots (Optional)

Replication slots prevent the master server from discarding WAL segments until they have been received by all standby servers. This helps maintain synchronization, especially when standbys are temporarily disconnected.

On the master server, create a replication slot for each standby:

```sql
SELECT * FROM pg_create_physical_replication_slot('standby_slot');
```

Modify the `primary_conninfo` on the standby server to include the slot name:

```conf
primary_slot_name = 'standby_slot'
```

