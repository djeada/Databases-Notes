# Master-Standby Replication

Master-Standby replication is a common database replication topology where a primary database server (the **master**) replicates data to one or more secondary servers (the **standbys**). This setup enhances data availability, fault tolerance, and load balancing. Standby servers can serve read-only queries and can be promoted to become the master in case of failure.

This note provides a comprehensive overview of Master-Standby replication, including its purpose, characteristics, advantages, challenges, and a practical example using PostgreSQL.

## Overview of Master-Standby Replication

### Architectural Diagram

```
                    +------------------+
                    |                  |
                    |   Master Server  |
                    |                  |
                    +--------+---------+
                             |
                     Write Operations
                             |
                             v
                    +--------+---------+
                    |                  |
                    |   Standby Server |
                    |      (Read-Only) |
                    +--------+---------+
                             |
                         Replication
                             |
                             v
                    +--------+---------+
                    |                  |
                    |   Standby Server |
                    |      (Read-Only) |
                    +------------------+
```

**Legend:**

- **Master Server**: The primary database server where all write operations occur.
- **Standby Servers**: Secondary servers that replicate data from the master and serve read-only queries.
- **Replication Arrows**: Indicate the flow of data from the master to the standbys.

### Key Characteristics

- **Write Operations**: Only the master server handles write operations (INSERT, UPDATE, DELETE).
- **Read Operations**: Standby servers can serve read-only queries, offloading read traffic from the master.
- **Data Replication**: Standbys continuously receive data changes from the master to stay synchronized.
- **Failover Capability**: Standby servers can be promoted to master in case of master failure, ensuring high availability.

## Purpose of Master-Standby Replication

1. **High Availability and Disaster Recovery**: Provides redundancy to prevent data loss and minimize downtime in case of failures.
2. **Load Balancing**: Offloads read-heavy operations to standby servers, improving performance and scalability.
3. **Maintenance Flexibility**: Allows maintenance on the master or standbys without significant downtime.
4. **Scalability**: Facilitates horizontal scaling by adding more standby servers as needed.

## Advantages

1. **Enhanced Fault Tolerance**: Standby servers act as backups, reducing the risk of data loss.
2. **Improved Read Performance**: Distributing read queries to standbys alleviates load on the master.
3. **Simplified Failover Process**: Standbys can quickly take over as the master, minimizing service interruption.
4. **Data Integrity**: Ensures data consistency across servers through continuous replication.

## Challenges

1. **Replication Lag**: Standbys may not always be perfectly synchronized with the master, leading to potential stale reads.
2. **Failover Complexity**: Promoting a standby to master requires careful coordination to prevent data inconsistencies.
3. **Write Scalability Limitations**: Since only the master handles writes, write-heavy applications may face scalability issues.
4. **Configuration Complexity**: Setting up and managing replication requires careful configuration and monitoring.

## Example: Implementing Master-Standby Replication in PostgreSQL

PostgreSQL supports streaming replication out-of-the-box, making it a suitable choice for implementing Master-Standby replication.

### Prerequisites

- **Two or more PostgreSQL servers**: One master and one or more standby servers.
- **Network Connectivity**: All servers must communicate over the network.
- **PostgreSQL Version**: Ensure all servers run compatible PostgreSQL versions (preferably the same version).

### Configuring the Master Server

#### 1. Edit `postgresql.conf`

Locate and edit the `postgresql.conf` file, typically found in the data directory (`/var/lib/pgsql/data/` or `/etc/postgresql/`).

Add or modify the following parameters:

```conf
# Enable WAL (Write-Ahead Logging) level suitable for replication
wal_level = replica

# Allow the master to send WAL data to standbys
max_wal_senders = 3

# Set the maximum number of replication slots (optional)
max_replication_slots = 3

# Set the amount of WAL data to retain (helps with standby synchronization)
wal_keep_size = 128MB
```

#### 2. Edit `pg_hba.conf`

Update `pg_hba.conf` to allow the standby servers to connect for replication:

```conf
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# Allow replication connections from standby servers
host    replication     replicator      standby_ip/32           md5
```

- **`replicator`**: The replication user.
- **`standby_ip/32`**: IP address of the standby server.

#### 3. Create a Replication User

Log into the PostgreSQL prompt and create a user for replication:

```sql
CREATE ROLE replicator WITH REPLICATION LOGIN ENCRYPTED PASSWORD 'your_password';
```

#### 4. Restart PostgreSQL

Restart the PostgreSQL service to apply changes:

```bash
# For Linux systems using systemd
sudo systemctl restart postgresql
```

### Configuring the Standby Server

#### 1. Stop PostgreSQL Service

Ensure the PostgreSQL service on the standby server is stopped:

```bash
sudo systemctl stop postgresql
```

#### 2. Create a Base Backup from the Master

Use `pg_basebackup` to create a base backup of the master on the standby server:

```bash
pg_basebackup -h master_ip -D /var/lib/pgsql/data/ -U replicator -W -P --wal-method=stream
```

- **`-h master_ip`**: IP address of the master server.
- **`-D /var/lib/pgsql/data/`**: Data directory on the standby server.
- **`-U replicator`**: Replication user.
- **`-W`**: Prompt for password.
- **`--wal-method=stream`**: Stream WAL files during backup.

#### 3. Create `standby.signal` File

For PostgreSQL versions 12 and above, create an empty file named `standby.signal` in the data directory:

```bash
touch /var/lib/pgsql/data/standby.signal
```

For versions before 12, create a `recovery.conf` file with the necessary parameters.

#### 4. Edit `postgresql.conf` on Standby

Set the following parameters in `postgresql.conf`:

```conf
# Enable read-only queries on standby
hot_standby = on

# Configure primary connection info
primary_conninfo = 'host=master_ip port=5432 user=replicator password=your_password'
```

#### 5. Start PostgreSQL Service

Start the PostgreSQL service on the standby server:

```bash
sudo systemctl start postgresql
```

### Verifying Replication

#### 1. Check Replication Status on Master

Connect to the master server and run:

```sql
SELECT client_addr, state
FROM pg_stat_replication;
```

You should see an entry for each standby server, indicating that they are connected.

#### 2. Test Data Replication

On the master server:

```sql
-- Create a test table
CREATE TABLE replication_test (id SERIAL PRIMARY KEY, data TEXT);

-- Insert data
INSERT INTO replication_test (data) VALUES ('Test data');
```

On the standby server, attempt to query the table:

```sql
-- Select data from the replicated table
SELECT * FROM replication_test;
```

You should see the inserted data, confirming that replication is working.

### Failover Procedure

In case the master server fails, you can promote a standby server to become the new master.

#### 1. Promote Standby to Master

On the standby server, run:

```bash
pg_ctl promote -D /var/lib/pgsql/data/
```

Alternatively, create a `promote.signal` file in the data directory:

```bash
touch /var/lib/pgsql/data/promote.signal
```

#### 2. Update Application Connections

Redirect your applications to connect to the new master server.

#### 3. Reconfigure the Failed Master as Standby (Optional)

Once the original master is back online, you can set it up as a standby to the new master.

### Handling Replication Slots (Optional)

Replication slots prevent the master from discarding WAL segments until they have been received by all standbys.

On the master server, create a replication slot for each standby:

```sql
SELECT * FROM pg_create_physical_replication_slot('standby_slot');
```

Modify the `primary_conninfo` on the standby to include the slot:

```conf
primary_slot_name = 'standby_slot'
```
