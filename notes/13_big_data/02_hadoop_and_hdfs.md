# Hadoop and HDFS

Hadoop is an ecosystem for storing and processing data across many machines. Its original core components solve different problems:

- **HDFS** stores files across a cluster.
- **YARN** allocates cluster resources to applications.
- **MapReduce** provides a batch-processing programming model.
- Tools such as **Hive** and **Spark** can run on top of the same storage and cluster resources.

Hadoop is not one database and HDFS is not a relational database. HDFS is a distributed file system designed for high-throughput access to large files.

## Why HDFS exists

A single machine has finite disk capacity and eventually fails. HDFS spreads a file across many machines and keeps redundant copies of its blocks.

```text
Large file
   │
   ├── block A ──► DataNode 1
   │            └► DataNode 3
   │            └► DataNode 5
   │
   ├── block B ──► DataNode 2
   │            └► DataNode 4
   │            └► DataNode 5
   │
   └── block C ──► DataNode 1
                └► DataNode 2
                └► DataNode 4
```

The important idea is that applications can process pieces of a dataset in parallel rather than moving the entire dataset to one server.

## HDFS architecture

The main HDFS roles are:

### NameNode

The **NameNode** manages metadata:

- directory and file names,
- permissions,
- the mapping from files to blocks,
- which DataNodes hold each block.

The NameNode does not normally carry the bulk file contents for clients.

### DataNode

A **DataNode** stores block contents on local disks and serves reads and writes.

### Client

An HDFS client first asks the NameNode where blocks are located, then communicates directly with DataNodes for the data.

```text
              metadata request
Client ─────────────────────────► NameNode
  │                                 │
  │       block locations           │
  ◄─────────────────────────────────┘
  │
  │ read/write block contents
  ├────────► DataNode A
  ├────────► DataNode B
  └────────► DataNode C
```

This separation keeps metadata centralized while moving bulk data directly between clients and storage nodes.

## What happens during a write

A simplified write flow looks like this:

```text
1. client asks NameNode to create file
2. NameNode chooses DataNodes for the first block
3. client streams block to DataNode A
4. A forwards it to B
5. B forwards it to C
6. acknowledgements return through the pipeline
7. process repeats for later blocks
```

Visualized:

```text
Client ──► DataNode A ──► DataNode B ──► DataNode C
   ◄──────────── acknowledgements ────────────────
```

Replication allows the cluster to keep serving data when one storage node fails.

## Replication and failure domains

A replication factor of three means three block copies are maintained, not three whole independent databases.

Copies should be distributed across failure domains so one rack or host failure does not destroy every copy.

```text
Rack 1                  Rack 2
┌──────────────┐        ┌──────────────┐
│ DataNode A   │        │ DataNode C   │
│ block X      │        │ block X      │
└──────────────┘        └──────────────┘
┌──────────────┐
│ DataNode B   │
│ block X      │
└──────────────┘
```

Replication improves availability, but it is **not a backup**. A mistaken deletion or corrupted application write can propagate to every live copy.

## NameNode high availability

Because metadata is critical, production clusters commonly use an active and standby NameNode with shared edit information and automatic failover.

```text
             ┌────────────────┐
clients ────►│ Active NN      │
             └──────┬─────────┘
                    │ shared edits / coordination
             ┌──────▼─────────┐
             │ Standby NN     │
             └────────────────┘
```

A **Secondary NameNode** is historically used for checkpointing metadata. It should not be confused with the standby NameNode in an HA setup.

Official references:
- [HDFS architecture](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html)
- [HDFS high availability](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HDFSHighAvailabilityWithQJM.html)

## Runnable HDFS command workflow

These commands assume Hadoop is installed and configured, or that you are connected to a development cluster.

Create a local sample file:

```bash
cat > events.csv <<'EOF'
event_id,user_id,event_type
1,101,login
2,101,view_product
3,205,login
EOF
```

Create a directory in HDFS and upload the file:

```bash
hdfs dfs -mkdir -p /data/events
hdfs dfs -put -f events.csv /data/events/
```

List files:

```bash
hdfs dfs -ls /data/events
```

Read the file back:

```bash
hdfs dfs -cat /data/events/events.csv
```

Check disk usage:

```bash
hdfs dfs -du -h /data/events
```

Download it to the local filesystem:

```bash
hdfs dfs -get /data/events/events.csv downloaded-events.csv
```

Remove the test directory:

```bash
hdfs dfs -rm -r /data/events
```

The commands look similar to Unix filesystem commands, but the paths refer to the configured distributed filesystem.

## URI form

Applications can address HDFS explicitly:

```text
hdfs://namenode.example.com:8020/data/events/events.csv
```

Spark can read that path directly:

```python
df = spark.read.option("header", True).csv(
    "hdfs://namenode.example.com:8020/data/events/events.csv"
)
```

The exact host, port, authentication, and configuration come from the cluster.

## Why large files work better

The NameNode must track metadata for every file and block. Millions of tiny files create large metadata overhead and inefficient processing.

Compare:

```text
Good:
1,000 files × 1 GB

Problematic:
10,000,000 files × 100 KB
```

Both may contain similar total data, but the tiny-file layout creates far more metadata and scheduling work.

Compaction into larger Parquet or ORC files is a common remedy.

## MapReduce mental model

MapReduce splits a batch job into map and reduce stages.

For a word-count example:

```text
Input blocks
   │
   ├── mapper 1 ──► (cat, 1) (dog, 1)
   ├── mapper 2 ──► (cat, 1) (cat, 1)
   └── mapper 3 ──► (dog, 1)
                    │
                    ▼ shuffle/group
              cat -> [1,1,1]
              dog -> [1,1]
                    │
                    ▼ reduce
              cat -> 3
              dog -> 2
```

The shuffle is expensive because data may move across the network. Spark also performs shuffles for joins and aggregations, although its execution model is more flexible than classic MapReduce.

## HDFS, YARN, MapReduce, Hive, and Spark

A common source of confusion is treating these as alternatives when they solve different layers.

```text
┌───────────────────────────────────────┐
│ SQL / processing                     │
│ Hive, Spark, MapReduce applications   │
├───────────────────────────────────────┤
│ Resource management                  │
│ YARN                                  │
├───────────────────────────────────────┤
│ Distributed storage                  │
│ HDFS                                  │
├───────────────────────────────────────┤
│ Commodity / virtual machines         │
└───────────────────────────────────────┘
```

Spark can use HDFS without using the MapReduce execution engine.

## Where Hadoop is used in practice

Classic Hadoop clusters are still important in existing on-premises and large enterprise platforms, especially where organizations have invested heavily in HDFS, YARN, Hive, and related tooling.

For many new cloud systems, object storage often replaces HDFS as the long-term storage layer.

Typical modern cloud pattern:

```text
S3 / GCS / ADLS
       │
       ├── Spark
       ├── Trino
       ├── Athena / serverless SQL
       └── lakehouse table format
```

Why object storage is attractive:

- storage is decoupled from compute,
- it is durable and managed,
- multiple engines can access the same files,
- compute clusters can be created and removed independently.

Why HDFS can still be attractive:

- high-throughput local cluster storage,
- data locality for on-premises workloads,
- mature integration with existing Hadoop platforms,
- predictable control over hardware and network topology.

## HDFS versus object storage

| Characteristic | HDFS | Cloud object storage |
| --- | --- | --- |
| Storage ownership | cluster manages disks | cloud provider manages storage |
| Compute coupling | usually close to compute nodes | decoupled from compute |
| Namespace | filesystem-like | object/key namespace |
| Typical new cloud use | less common | very common |
| On-premises big-data use | common in existing platforms | depends on object-storage product |
| Data locality | explicit concept | usually remote service access |

The choice is architectural rather than purely about speed.

## Security

A production Hadoop installation should not rely on an open development configuration.

Important controls include:

- Kerberos authentication,
- HDFS permissions and ACLs,
- encryption in transit,
- encryption at rest,
- service authorization,
- network segmentation,
- audit logging,
- secrets management.

Authorization should be tested from the identity that actually runs jobs, not only from an administrator account.

## Operations and monitoring

Useful HDFS signals include:

- storage utilization,
- under-replicated blocks,
- missing or corrupt blocks,
- DataNode health,
- NameNode heap pressure,
- metadata checkpoint health,
- request latency,
- failed disks,
- decommissioning progress.

A cluster running out of storage can become unstable even before disks are literally 100% full, so capacity planning matters.

## Common mistakes

### Treating HDFS as a database

HDFS is not designed for frequent small row updates or low-latency indexed lookups.

Use a database when the workload needs:

- primary-key lookups,
- transactions,
- constraints,
- secondary indexes,
- frequent record-level updates.

### Storing huge numbers of tiny files

Small files create excessive metadata and task scheduling overhead.

### Assuming replication is backup

Replication protects against hardware failure, not accidental deletion, bad writes, ransomware, or operator error.

### Ignoring data format

Raw CSV works for simple exchange, but analytical jobs usually benefit from typed columnar formats such as Parquet or ORC.

### Assuming locality always dominates

In modern cloud systems, compute and storage are frequently separated. Network bandwidth, caching, file layout, and column pruning can matter more than classic HDFS data locality.

## When HDFS is a good fit

HDFS is most appropriate when:

- datasets are very large,
- files are read or appended in large sequential operations,
- workloads are batch-oriented,
- the organization operates a Hadoop cluster,
- data needs to be spread across many machines.

It is usually a poor fit for:

- millions of tiny mutable records,
- low-latency request/response APIs,
- frequent random updates,
- workloads already well served by a managed relational database.

## Related notes

- [Data warehousing](01_data_warehousing.md)
- [Spark SQL](03_spark_sql.md)
- [Distributed databases](../06_distributed_databases/)
