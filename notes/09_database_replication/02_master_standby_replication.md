## Master-Standby replication
Master-Standby replication is a common replication topology where a primary (master) database is replicated to one or more secondary (standby) databases. This note focuses on the concept of Master-Standby replication and provides an example using PostgreSQL as the database management system.

## Master-Standby Replication Overview

### Purpose

1. Maintain a redundant copy of the master database for high availability and disaster recovery.
2. Offload read queries to the standby databases for load balancing.

### Characteristics

1. Write operations are only performed on the master database.
2. Standby databases are read-only and can be used for read operations or reporting.
3. Standby databases can be promoted to master in case of master failure.

## PostgreSQL Master-Standby Replication Example

### Prerequisites

1. Two PostgreSQL instances: one for the master and one for the standby.
2. PostgreSQL configuration files: `postgresql.conf` and `pg_hba.conf`.
3. An archive directory for storing WAL (Write-Ahead Log) files.

### Configure the Master Database

1. Edit the `postgresql.conf` file on the master instance:

```shell
wal_level = replica
archive_mode = on
archive_command = 'scp %p user@standby:/path/to/archive/%f'
max_wal_senders = 3
```

2. Edit the `pg_hba.conf` file on the master instance to allow connections from the standby server:

host replication <standby_user> <standby_ip>/32 trust

3. Restart the master PostgreSQL instance to apply the configuration changes.

### Create a Base Backup

1. On the standby server, create a backup directory: `mkdir /path/to/backup`.
2. On the standby server, use `pg_basebackup` to create a base backup from the master database:

```
pg_basebackup-D /path/to/backup -Fp -Xs -P -R -h <master_ip> -U <standby_user> -v
```

### Configure the Standby Database

1. Move the backup data to the standby PostgreSQL data directory:

```
mv /path/to/backup/* /path/to/standby/data/directory/
```

2. Edit the `postgresql.conf` file on the standby instance:

hot_standby = on

3. Create a `recovery.conf` file in the standby PostgreSQL data directory with the following content:

```
standby_mode = 'on'
primary_conninfo = 'host=<master_ip> port=5432 user=<standby_user>'
restore_command = 'scp user@master:/path/to/archive/%f %p'
trigger_file = '/path/to/trigger_file'
```

4. Start the standby PostgreSQL instance.

### Verify Replication

1. On the master database, create a test table and insert some data:

```
CREATE TABLE test (id SERIAL PRIMARY KEY, name VARCHAR(255));
INSERT INTO test (name) VALUES ('Example');
```

2. On the standby database, query the test table to verify that the data has been replicated:

```
SELECT * FROM test;
```

### Failover (Optional)

1. To promote the standby database to master, create the trigger file specified in the `recovery.conf`:

```
touch /path/to/trigger_file
```

2. The standby database will now become the new master, and clients can be redirected to the new master database.
