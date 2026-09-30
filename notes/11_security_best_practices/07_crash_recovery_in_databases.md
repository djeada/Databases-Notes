# Understanding Crash Recovery in Databases

Crash recovery is an important component of database systems that ensures data consistency and durability despite unexpected events like power outages, hardware failures, or software crashes. By design, databases must be capable of returning to a reliable state after a failure occurs. This is largely accomplished through mechanisms like the Write-Ahead Log (WAL), which records changes before they are committed to the actual data files on disk.

## The Basics of Crash Recovery

Databases typically cache data in memory (often called the buffer pool) for speed. When a change is made, such as adding a row or updating an existing row, it is applied first in memory. Only later is this modified data flushed to disk. If a crash or power loss happens mid-write, data could end up corrupted or partially written. Crash recovery techniques help the database detect and correct any inconsistencies by replaying or discarding in-flight changes.

## The Role of the Write-Ahead Log (WAL)

The WAL, sometimes called the redo log, keeps track of all modifications. Changes generate log records, initially possibly buffered in memory. The corresponding log must be durably flushed before changed data pages are written to persistent storage. Durable commits also require the relevant commit log records to be flushed before acknowledgment.

- The WAL is appended in a strictly sequential manner, which is efficient for most disk types and reduces write overhead.
- Because each modification is recorded in the log, the WAL acts as the authoritative record of what changed in the database.
- If the system crashes, the database can use the WAL to replay needed changes and determine which transactions committed. Some recovery algorithms also undo uncommitted work; PostgreSQL instead uses transaction status to keep uncommitted row versions invisible.

```
WAL:
                           +----------------+
                           |  Application   |
                           |  Transaction   |
                           +--------+-------+
                                    |
                                    | 1. Emit transaction
                                    v
                           +--------+-------+
                           |  Write-Ahead   |
                           |   Log (WAL)    |
                           +--------+-------+
                                    |
    +-------------------------------+-------------------------------+
    |                                                               |
    | 2a. Append record to WAL buffer                               |
    |                                                               |
    |      +----------------+                   +----------------+  |
    |      | WAL In-Memory  | --(write)-->      | WAL On-Disk    |  |
    |      |   Buffer       |                   | (log file)     |  |
    |      +----------------+                   +----------------+  |
    |               |                                     |         |
    |               | 2b. Fsync (sync to durable storage) |         |
    |               +------------------------------------>+         |
    |                                                               |
    +---------------------------------------------------------------+
                                    |
                                    | 3. Apply logged changes
                                    v
                           +--------+-------+
                           |   Data Store   |
                           |   (Main DB)    |
                           +----------------+
```

## WAL and Transaction States

Databases use transaction recovery to enforce atomicity (all or nothing). The WAL is directly tied to these transaction guarantees:

- With durable commit settings, the required WAL, including commit information, reaches stable storage before success is acknowledged. Even if a crash occurs immediately afterward, the committed changes can be replayed from the WAL upon restart.
- If the system crashes before these transactions commit, the database treats them as rolled back. Uncommitted changes must not become visible as committed data. Recovery may still replay their physical log records; engine-specific undo or visibility rules handle their transaction status.

## Checkpointing

A checkpoint establishes a recovery position and coordinates flushing relevant dirty pages. It does not universally copy every in-memory page or create a transaction-consistent snapshot. This makes the on-disk data more up-to-date and reduces the amount of log replay needed if a crash occurs.

- Frequent checkpoints mean there is less WAL data to replay during restart.
- Writing all in-memory data pages to disk can be expensive, especially for large or very active databases.
- Administrators tune checkpoint frequency to balance acceptable recovery time with acceptable performance during normal operations.

## Crash Recovery Steps

When a database restarts after a crash, it uses engine-specific recovery steps to restore a consistent state:

1. Locate the recovery start position using checkpoint and control metadata.
2. Replay the required log records, which can include physical work from transactions that never committed.
3. Apply the engine’s undo or transaction-visibility rules so incomplete transactions do not appear as committed changes.
4. The database finishes replaying WAL records and transitions back to handling regular queries.

## Flushing the WAL

Some databases offer configuration options for controlling how often the WAL is physically written and synchronized to disk:

- Ensures the operating system flushes the WAL to stable storage, guaranteeing durability.
- Group commit can share a flush among transactions while still waiting for durability before acknowledging each one. Asynchronous commit is different: it acknowledges before the required durable flush and can lose recent acknowledged changes.
- Stricter flushing maintains stronger guarantees but can lower throughput for write-heavy workloads.

```
+===========================+
|       Database System     |
+===========================+
             |
             | Initiate Transaction
             v
+---------------------------+
|        Client/System      |
+---------------------------+
             |
             | Generate Log Record
             v
+---------------------------+
|      WAL Buffer (RAM)     |
|  -----------------------  |
|  | Log Record 1        |  |
|  | Log Record 2        |  |
|  | Log Record 3        |  |
|  | ...                 |  |
|  -----------------------  |
+---------------------------+
             |
             | Sequential Write (Flush)
             v
+---------------------------+
|     Stable Storage (Disk) |
|  -----------------------  |
|  | Log Record 1        |  |
|  | Log Record 2        |  |
|  | Log Record 3        |  |
|  | ...                 |  |
|  -----------------------  |
+---------------------------+
             |
             | Apply Changes to Database
             v
+---------------------------+
|       Database Files      |
|  -----------------------  |
|  | Data Page A         |  |
|  | Data Page B         |  |
|  | ...                 |  |
|  -----------------------  |
+---------------------------+
```

## Benefits of WAL-Based Recovery

- Committed transactions survive power loss or crashes, thanks to the WAL.
- WAL records are appended sequentially, which matches well with disk I/O patterns.
- WAL entries can be streamed to secondary systems for real-time or near-real-time replication.
- The WAL can be archived and replayed on top of a previous full backup to reach a desired point in time.

## Drawbacks and Trade-Offs

- WAL files occupy extra disk space that administrators must monitor and manage.
- Every change is written at least twice—once to the WAL, then later to the actual data file.
- Frequent checkpoints can spike I/O usage and temporarily slow other operations.
- Adjusting checkpoint intervals, flush frequencies, and other parameters requires careful tuning to find the right balance between performance and reliability.

## Practical Example

Consider an `orders` table:

| OrderID | CustomerID | Status    |
|---------|-----------|-----------|
| 1       | 1001      | Pending   |
| 2       | 1002      | Shipped   |
| 3       | 1003      | Delivered |

Suppose a user updates `OrderID = 1` from `Pending` to `Shipped`.

I. The database modifies the in-memory page representing `OrderID = 1`.

II. A corresponding record showing the old and new values (`Pending` -> `Shipped`) is appended to the WAL on disk.

III. The data file containing the `orders` table may not be updated immediately.

IV. If the database crashes at this point, the WAL can be replayed to recover the change.

V. After restart, the database replays the WAL entries for all committed transactions, ensuring `OrderID = 1` is set to `Shipped` in the data file.

## Visualizing Crash Recovery

```
#
               +-----------------+
Changes in --> |    Memory       |
the database   | (Buffer Pool)   |
               +--------+--------+
                        |
                WAL Record Written
                        |
                        v
               +-----------------+
               | Write-Ahead Log |
               |   (Redo Log)    |
               +--------+--------+
                        |
  Checkpoint ---------->+
     (Flush data pages) .
                        .
                        .
                        v
               +------------------+
               |  Data Files on   |
               |       Disk       |
               +------------------+
```

- The buffer pool stores active data pages in memory.
- All changes are recorded in the WAL on disk before data files are updated.
- A checkpoint flushes the current in-memory state of data to disk and records this action in the WAL.
- After a crash, the database replays committed transactions from the WAL and ignores uncommitted changes.

## Best Practices

I. Find the right interval to minimize both I/O spikes and recovery time.

II. Make sure adequate storage capacity and regularly archive or clean old WAL files.

III. Configure fsync to make sure that WAL data truly resides on stable media.

IV. Combine periodic full backups with continuous WAL archiving for point-in-time recovery.

V. Validate recovery settings in staging environments to confirm that the database can recover from abrupt failures.

## Review questions

- What is crash recovery in database systems, and why is it important?
- How does the Write-Ahead Log (WAL) facilitate crash recovery?
- What is the role of checkpointing in the crash recovery process?
- What are the main steps a database follows during crash recovery after a system restart?
- What are the benefits and trade-offs associated with WAL-based recovery mechanisms?
