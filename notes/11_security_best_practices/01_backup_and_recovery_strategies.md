# Backup and Recovery Strategies

Backup and recovery strategies are crucial components of any database management plan, ensuring data durability, availability, and business continuity. One of the primary challenges in designing these strategies is performing backups without stopping or slowing down production read/write operations. This note provides an in-depth exploration of backup types, methods to minimize production impact, recovery strategies, best practices, and tools, with illustrative diagrams to enhance understanding.

**Key Objectives:**

- **Data Durability**: Ensure that data is not lost due to hardware failures, software bugs, or human errors.
- **Data Availability**: Minimize downtime and maintain continuous access to data.
- **Performance Preservation**: Conduct backups without impacting the performance of production read/write operations.

## Challenges in Non-Disruptive Backups

- **Resource Contention**: Backup processes can consume significant I/O, CPU, and network resources, competing with production workloads.
- **Data Consistency**: Ensuring the backup captures a consistent state of the database without locking tables or halting transactions.
- **Scalability**: Handling large volumes of data efficiently during backup without affecting application performance.

---

## Types of Backups

Understanding the different types of backups is essential for designing an effective backup strategy.

### Full Backup

- **Definition**: A complete copy of the entire database at a specific point in time.
- **Characteristics**:
  - **Pros**:
    - Simplifies recovery since all data is in a single backup.
    - Easier to manage and restore.
  - **Cons**:
    - Time-consuming to create, especially for large databases.
    - Requires significant storage space.
    - Can impact production if not managed properly.

### Incremental Backup

- **Definition**: Backs up only the data that has changed since the last backup (full or incremental).
- **Characteristics**:
  - **Pros**:
    - Faster and requires less storage than full backups.
    - Reduces backup window and resource utilization.
  - **Cons**:
    - Recovery is more complex, requiring all incremental backups since the last full backup.
    - Potentially longer recovery time.

### Differential Backup

- **Definition**: Backs up data that has changed since the last full backup.
- **Characteristics**:
  - **Pros**:
    - Faster than full backups.
    - Simpler recovery process than incremental backups (only need the last full and differential backup).
  - **Cons**:
    - As time passes, differential backups can become nearly as large as full backups.

### Logical vs. Physical Backups

- **Logical Backups**:
  - **Definition**: Export database objects like schemas and data using database utilities (e.g., `mysqldump`, `pg_dump`).
  - **Pros**:
    - Portable across different database versions and platforms.
    - Allows for selective restores.
  - **Cons**:
    - Slower and can impact performance due to table scans.
    - May not capture certain database-specific features.

- **Physical Backups**:
  - **Definition**: Copy the physical files that store the database data (e.g., data files, logs).
  - **Pros**:
    - Faster backup and restore times.
    - Less impact on performance if managed correctly.
  - **Cons**:
    - Usually platform-specific.
    - Requires consistency measures (e.g., snapshots).

---

## Backup Methods Minimizing Production Impact

To avoid disrupting production operations, consider backup methods designed to minimize resource contention and maintain data consistency without halting read/write activities.

### Online (Hot) Backups

- **Definition**: Backups taken while the database is running and accessible to users.
- **Mechanism**:
  - Utilize database features that allow for consistent backups without locking tables.
  - Often involve reading data files while tracking changes (e.g., through write-ahead logs).
- **Considerations**:
  - Ensure the backup tool supports online backups.
  - Monitor resource utilization to prevent performance degradation.

**Example with PostgreSQL:**

```bash
# Using pg_basebackup for online backup
pg_basebackup -h localhost -D /backup/data -U replicator -Fp -Xs -P
```

### Snapshot-Based Backups

- **Definition**: Leverage filesystem or storage-level snapshots to capture the state of the database at a point in time.
- **Mechanism**:
  - **Filesystem Snapshots**: Use features like LVM, ZFS, or Btrfs snapshots.
  - **Storage Snapshots**: Use SAN or NAS capabilities to create instant snapshots.
- **Advantages**:
  - Snapshots are nearly instantaneous, minimizing impact.
  - Can be used in conjunction with database mechanisms to ensure consistency.

**Illustrative Diagram:**

```
+------------------------+
|   Production Database  |
|       (Running)        |
+-----------+------------+
            |
       Initiate Snapshot
            |
            v
+------------------------+
|   Snapshot Created     |
|   (Point-in-Time Copy) |
+------------------------+

- The production database continues to run without interruption.
- The snapshot can be backed up or moved without affecting the production load.
```

**Example with LVM Snapshots:**

```bash
# Create LVM snapshot
lvcreate --size 10G --snapshot --name db_snapshot /dev/vg0/db_volume

# Mount snapshot and perform backup
mount /dev/vg0/db_snapshot /mnt/db_snapshot
tar -czf db_backup.tar.gz /mnt/db_snapshot

# Remove snapshot after backup
umount /mnt/db_snapshot
lvremove /dev/vg0/db_snapshot
```

### Replication-Based Backups

- **Definition**: Use a replica (standby) server to perform backups, thereby offloading the backup load from the primary server.
- **Mechanism**:
  - Set up replication to a standby server.
  - Perform backups on the standby without impacting the primary.
- **Advantages**:
  - Eliminates backup load on the primary server.
  - Standby can be used for other purposes like read scaling.

**Illustrative Diagram:**

```
          +-------------------+
          |   Primary Server  |
          |   (Production)    |
          +---------+---------+
                    |
               Replication
                    |
                    v
          +-------------------+
          |   Standby Server  |
          |   (Read-Only)     |
          +---------+---------+
                    |
               Backup Process
                    |
                    v
          +-------------------+
          |   Backup Storage  |
          +-------------------+

- Replication keeps the standby synchronized with the primary.
- Backups are performed on the standby, avoiding impact on the primary.
```

**Considerations:**

- Ensure replication lag is minimal to have up-to-date backups.
- Standby server should have sufficient resources to handle backup operations.

---

## Recovery Strategies

An effective recovery strategy is essential to restore operations quickly after data loss.

### Point-in-Time Recovery (PITR)

- **Definition**: Restoring the database to a specific moment using backups and transaction logs.
- **Mechanism**:
  - Restore the latest full backup.
  - Apply incremental backups (if any).
  - Replay transaction logs up to the desired point in time.
- **Requirements**:
  - Regular backups (full, incremental, or differential).
  - Continuous archiving of transaction logs (WAL files in PostgreSQL, binary logs in MySQL).

**Example with PostgreSQL:**

1. **Configure Continuous Archiving**:

   ```conf
   # postgresql.conf
   archive_mode = on
   archive_command = 'cp %p /archive_location/%f'
   ```

2. **Perform Recovery**:

   - Restore the base backup.
   - Create `recovery.conf` specifying the target time.

   ```conf
   # recovery.conf
   restore_command = 'cp /archive_location/%f %p'
   recovery_target_time = '2023-09-14 12:34:56'
   ```

### Continuous Data Protection (CDP)

- **Definition**: Capturing and storing all changes in real-time or near-real-time to enable quick recovery with minimal data loss.
- **Mechanism**:
  - Log every write operation.
  - Allows recovery to any point in time.
- **Considerations**:
  - Requires significant storage for logs.
  - May impact performance due to continuous logging.

### Standby Databases

- **Definition**: Maintain one or more standby databases synchronized with the primary via replication.
- **Usage**:
  - **Failover**: Promote a standby to primary in case of primary failure.
  - **Load Balancing**: Use standbys for read queries.
  - **Backup Source**: Perform backups from standby to offload primary.

**Failover Process Illustration:**

```
[Normal Operation]
+-------------------+       Replication       +-------------------+
|   Primary Server  | ----------------------> |   Standby Server  |
|   (Active)        |                         |   (Passive)       |
+-------------------+                         +-------------------+

[After Primary Failure]
+-------------------+                          +-------------------+
|   Primary Server  |      Promote Standby     |   Standby Server  |
|   (Failed)        | -----------------------> |   (Now Primary)   |
+-------------------+                          +-------------------+

- Standby server becomes the new primary.
- Clients are redirected to the new primary.
```

---

## Best Practices

1. **Regular Backup Schedule**:
   - Align with Recovery Point Objective (RPO) and Recovery Time Objective (RTO).
   - Automate backups to reduce human error.

2. **Backup Testing**:
   - Regularly test restore procedures.
   - Verify backup integrity to ensure data can be recovered.

3. **Offsite and Redundant Storage**:
   - Store backups in multiple locations.
   - Use cloud storage for additional redundancy.

4. **Monitoring and Alerts**:
   - Implement monitoring for backup processes.
   - Set up alerts for failures or performance issues.

5. **Documentation and Procedures**:
   - Maintain up-to-date documentation of backup and recovery processes.
   - Train staff on recovery procedures.

6. **Security Measures**:
   - Encrypt backups to protect sensitive data.
   - Restrict access to backup storage.

7. **Resource Management**:
   - Schedule backups during off-peak hours if possible.
   - Throttle backup processes to limit resource usage.

8. **Compliance and Retention Policies**:
   - Adhere to legal requirements for data retention.
   - Implement policies for backup retention and disposal.

---

## Tools and Technologies

Various tools and technologies can facilitate efficient backups without impacting production.

### Database-Specific Tools

- **MySQL/MariaDB**:
  - **Percona XtraBackup**: Open-source tool for hot physical backups.
    - Supports non-blocking backups of InnoDB databases.
    - Incremental backups and compression options.
  - **MySQL Enterprise Backup**: Provides hot backup capabilities.

- **PostgreSQL**:
  - **pg_basebackup**: Built-in tool for streaming physical backups.
  - **Barman** and **pgBackRest**: Advanced backup and recovery tools supporting incremental backups, compression, and PITR.

- **Oracle**:
  - **RMAN (Recovery Manager)**: Comprehensive backup and recovery tool integrated with Oracle databases.

### Filesystem and Storage Solutions

- **LVM Snapshots**: Logical Volume Manager allows for point-in-time snapshots of volumes.
- **ZFS Snapshots**: ZFS filesystem supports efficient snapshots and replication.
- **Cloud Provider Snapshots**:
  - **AWS EBS Snapshots**: Provides incremental snapshots of EBS volumes.
  - **Azure Managed Disks**: Supports snapshots and incremental backups.
  - **Google Cloud Persistent Disk Snapshots**: Allows for point-in-time copies.

### Backup and Recovery Software

- **Bacula**: Enterprise-level open-source backup solution.
- **Amanda**: Open-source backup software compatible with various operating systems.
- **Veeam Backup & Replication**: Offers data protection for virtual, physical, and cloud environments.
- **Commvault**: Comprehensive data management solution with backup and recovery capabilities.

### Continuous Data Protection Tools

- **DRBD (Distributed Replicated Block Device)**: Mirrors block devices between servers.
- **MongoDB Ops Manager**: Provides continuous backup for MongoDB databases.
- **SQL Server Always On Availability Groups**: Supports real-time data replication.

