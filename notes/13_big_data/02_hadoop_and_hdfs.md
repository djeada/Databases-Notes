# Hadoop and HDFS

Hadoop is a collection of tools for distributed storage and processing. HDFS supplies file storage, YARN manages cluster resources, and MapReduce provides a batch-processing model. These components have different jobs.

## HDFS architecture

The **NameNode** manages the namespace and block metadata. **DataNodes** store blocks and serve file contents directly to clients. Files are split into large blocks distributed across machines.

```text
Client --> NameNode: locate file blocks
Client --> DataNodes: read or write block contents
```

Blocks can be replicated to survive storage-node failures. Replication costs extra capacity, and placement across failure domains matters. Metadata also needs protection; a NameNode high-availability deployment uses active and standby roles. A Secondary NameNode performs checkpointing and is not simply a failover standby. See the [HDFS architecture](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html).

## Example workflow

With a configured Hadoop cluster and a local `events.csv` file:

```bash
hdfs dfs -mkdir -p /data/events
hdfs dfs -put events.csv /data/events/
hdfs dfs -ls /data/events
hdfs dfs -cat /data/events/events.csv
```

The path belongs to the configured distributed filesystem. Applications such as Spark can read it using an HDFS URI.

## What HDFS is suited to

HDFS favors large files, streaming reads, and batch throughput. It is a poor substitute for a database that needs frequent small random updates or low-latency row lookups. A large number of tiny files also creates metadata overhead.

A processing engine can divide work among workers near the blocks. MapReduce expresses a job as mapping records followed by grouping and reducing results. Spark supports a broader execution model and can use HDFS without using MapReduce.

## Operational considerations

Replication does not replace backups: deletions and bad application writes can affect all live copies. Monitor storage capacity, missing or under-replicated blocks, metadata health, and recovery procedures. Authentication, authorization, and encryption must be configured for the deployment.

## Related notes

- [Data warehousing](01_data_warehousing.md)
- [Spark SQL](03_spark_sql.md)
- [HDFS high availability](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HDFSHighAvailabilityWithQJM.html)
