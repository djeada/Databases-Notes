# Streaming, Kafka, and Change Data Capture

Batch systems process bounded data: "all orders from yesterday." Streaming systems process data that continues arriving: clicks, payments, sensor readings, database changes, and application events.

The key design change is that there is no final row.

```text
batch:
[file of records] ──► process once ──► result

stream:
event ─► event ─► event ─► event ─► ...
                 │
                 ▼
          continuous processing
```

## Where streaming is used

Common use cases include:

- fraud detection,
- operational monitoring,
- clickstream analytics,
- near-real-time dashboards,
- log pipelines,
- notification systems,
- event-driven microservices,
- database change capture,
- feeding search indexes and caches.

Not every problem needs streaming. A five-minute batch job is often simpler and completely adequate.

## Kafka mental model

Apache Kafka is a distributed event log.

Applications **produce** records to topics. Topics are split into **partitions**. Consumers read records in partition order.

```text
producers
   │
   ├──────────────┐
   ▼              ▼
┌────────────────────────────┐
│ topic: orders              │
│                            │
│ partition 0: 0 1 2 3 4 ...│
│ partition 1: 0 1 2 3 4 ...│
│ partition 2: 0 1 2 3 4 ...│
└─────────────┬──────────────┘
              │
              ▼
          consumers
```

An offset identifies a record's position inside one partition.

## Why partitions matter

Partitions provide parallelism.

If a topic has four partitions, a consumer group can process several partitions concurrently.

```text
topic partitions        consumer group

P0 ───────────────────► consumer A
P1 ───────────────────► consumer A
P2 ───────────────────► consumer B
P3 ───────────────────► consumer B
```

Within one consumer group, one partition is assigned to at most one consumer at a time. Adding consumers beyond the partition count does not increase parallel consumption of that topic.

## Ordering

Kafka preserves record order **within a partition**, not across the whole topic.

If events for one account must stay ordered, use a stable key such as `account_id`.

```text
key = account-42
        │
        ▼
partition(key)
        │
        ▼
all account-42 events -> same partition -> ordered
```

The trade-off is that a very hot key can create partition skew.

## Local Kafka setup

The repository includes a single-node development configuration:

[`scripts/big_data/kafka/docker-compose.yml`](../../scripts/big_data/kafka/docker-compose.yml)

It uses Apache Kafka in KRaft mode. It is for learning, not production.

Start it:

```bash
cd scripts/big_data/kafka
docker compose up -d
docker compose ps
```

The broker is available to the host at `localhost:9092`.

Create a topic:

```bash
docker exec kafka-notes   /opt/kafka/bin/kafka-topics.sh   --bootstrap-server localhost:9092   --create   --topic orders   --partitions 3   --replication-factor 1
```

List topics:

```bash
docker exec kafka-notes   /opt/kafka/bin/kafka-topics.sh   --bootstrap-server localhost:9092   --list
```

## Produce events

Start a console producer:

```bash
docker exec -it kafka-notes   /opt/kafka/bin/kafka-console-producer.sh   --bootstrap-server localhost:9092   --topic orders
```

Enter records:

```text
{"order_id":1001,"customer_id":42,"amount":19.95}
{"order_id":1002,"customer_id":51,"amount":39.00}
{"order_id":1003,"customer_id":42,"amount":12.50}
```

Each line becomes one Kafka record.

## Consume events

In another terminal:

```bash
docker exec -it kafka-notes   /opt/kafka/bin/kafka-console-consumer.sh   --bootstrap-server localhost:9092   --topic orders   --from-beginning
```

You should see the JSON records produced above.

Stop the development broker:

```bash
docker compose down
```

## Consumer groups

A consumer group represents one logical subscriber.

Suppose both billing and analytics need every order:

```text
             ┌──► group: billing
orders topic ┤
             └──► group: analytics
```

Each group gets its own logical progress through the topic.

Inside one group, instances share work:

```text
group: analytics
├── analytics-1 -> partitions 0,2
└── analytics-2 -> partition 1
```

This is how Kafka supports both fan-out between applications and horizontal scaling within one application.

## At-most-once, at-least-once, and exactly-once

Delivery semantics depend on when progress is committed relative to processing.

### At-most-once

Commit first, process second.

```text
commit offset
     │
     ▼
process event
     │
 crash here -> event may be lost
```

### At-least-once

Process first, commit second.

```text
process event
     │
 crash before offset commit
     │
     ▼
event is read again
```

Duplicates are possible, so consumers should often be idempotent.

### Exactly-once

Exactly-once processing is a system property, not a magic checkbox. Kafka supports transactional mechanisms within compatible Kafka workflows, but external databases and APIs still need coordinated or idempotent handling.

A practical design is often:

```text
event has stable event_id
        │
        ▼
consumer writes result
        │
        ├── event_id already processed? -> ignore
        └── new event_id -> apply once
```

## Idempotency

An operation is idempotent when repeating it has the same intended result.

Dangerous retry:

```sql
UPDATE accounts
SET balance = balance + 100
WHERE id = 7;
```

Running this twice credits twice.

A safer event-processing design may record a unique transfer ID in the same transaction:

```text
BEGIN
  INSERT processed_events(event_id)
  -- fails if duplicate
  UPDATE account balance
COMMIT
```

Database constraints are useful tools for making stream consumers safe to retry.

## Event time versus processing time

**Event time** is when the event actually happened.

**Processing time** is when the streaming system handled it.

```text
event occurred:   10:00:03
network delay:       00:12
processed:        10:00:15
```

Late events make streaming aggregation more difficult.

For a "sales per five-minute window" report, the system must decide how long to wait for late data before considering a window complete.

## Windows

Streaming queries often aggregate into windows.

```text
10:00 ├──────────────┤ 10:05
      events: 17
10:05 ├──────────────┤ 10:10
      events: 24
```

Common window types:

- tumbling: non-overlapping fixed windows,
- sliding: overlapping windows,
- session: activity grouped until an inactivity gap.

Frameworks such as Spark Structured Streaming and Apache Flink provide event-time windows and watermarking.

## Change Data Capture

**Change Data Capture (CDC)** turns database changes into a stream.

Instead of polling:

```sql
SELECT *
FROM orders
WHERE updated_at > last_seen;
```

a CDC system reads the database's change log.

```text
PostgreSQL WAL / MySQL binlog
            │
            ▼
         Debezium
            │
            ▼
          Kafka
            │
    ┌───────┼────────┐
    ▼       ▼        ▼
warehouse  search   services
```

CDC is useful because it can capture inserts, updates, and deletes with lower source-database overhead than repeated full scans.

## Debezium

Debezium is commonly used to stream changes from databases such as PostgreSQL and MySQL into Kafka-compatible pipelines.

Typical uses:

- replicate OLTP changes into analytics,
- update search indexes,
- populate caches,
- synchronize services,
- construct audit/event streams.

CDC events often contain:

- source metadata,
- operation type,
- before image,
- after image,
- log position or transaction metadata.

Consumers must understand deletes, schema changes, and replay behavior.

## The outbox pattern

Publishing a Kafka event after committing a database transaction can fail in between:

```text
1. commit order to database      ✓
2. process crashes               ✗
3. publish OrderCreated          never happens
```

The outbox pattern writes both business data and an outgoing event record in one database transaction.

```text
BEGIN
  INSERT INTO orders ...
  INSERT INTO outbox ...
COMMIT
```

A CDC process then publishes the outbox row.

```text
application transaction
       │
       ▼
database + outbox
       │
       ▼
CDC / Debezium
       │
       ▼
Kafka
```

This avoids a distributed transaction between the application database and message broker.

## Kafka versus a queue

Kafka is log-oriented. Consumers track positions and records can remain available after consumption.

Traditional queues often emphasize handing a message to a worker and then removing or hiding it.

Kafka is especially useful when:

- several independent consumers need the same events,
- replay is valuable,
- ordered partition logs are useful,
- throughput is high,
- event history should be retained.

A simpler task queue may be preferable for background jobs where replayable event history is not needed.

## Kafka versus database tables

Do not use Kafka as a replacement for all persistent data.

A database is better for:

- current entity state,
- indexed point lookups,
- relational constraints,
- transactional queries.

Kafka is better for:

- event propagation,
- replayable logs,
- decoupled consumers,
- ordered streams.

Many architectures use both:

```text
API -> PostgreSQL
        │
        ▼ CDC
       Kafka
      /  |   \
     /   |    \
search cache warehouse
```

## Production concerns

A production Kafka deployment needs decisions around:

- broker count,
- replication factor,
- partition count,
- retention,
- disk capacity,
- authentication and authorization,
- TLS,
- schema compatibility,
- consumer lag monitoring,
- rebalance behavior,
- disaster recovery.

A single-node Docker broker demonstrates semantics but none of the resilience expected in production.

## Schemas

Raw JSON is easy to start with but weakly governed.

Larger organizations often use:

- Avro,
- Protobuf,
- JSON Schema,
- a schema registry.

The goal is to prevent a producer change from silently breaking consumers.

A compatibility policy may allow:

```text
v1: order_id, amount
v2: order_id, amount, currency
```

while preventing incompatible type changes without a coordinated migration.

## Consumer lag

Consumer lag measures how far a consumer group is behind the latest records.

```text
latest offset:    1,000,000
consumer offset:    970,000
lag:                 30,000
```

Lag can increase because:

- traffic spikes,
- consumers are too slow,
- downstream databases throttle,
- one partition is skewed,
- a consumer is repeatedly crashing.

Lag is one of the most important Kafka operational metrics.

## Technologies used in practice

| Responsibility | Common technologies | Why |
| --- | --- | --- |
| durable event log | Apache Kafka, managed Kafka services | scalable retained event streams |
| CDC | Debezium, cloud CDC services | reads database change logs |
| stream processing | Flink, Kafka Streams, Spark Structured Streaming | stateful transforms and windows |
| schemas | Avro, Protobuf, schema registries | compatibility and typed events |
| delivery to systems | Kafka Connect | standardized source/sink connectors |
| monitoring | Prometheus/Grafana, platform tooling | lag, broker health, throughput |

Managed Kafka offerings reduce broker operations but do not eliminate partitioning, schema, or consumer design decisions.

## Common mistakes

### Too many partitions immediately

Partitions add parallelism but also metadata, files, and operational overhead.

### No event key strategy

Related events can land in different partitions and lose ordering guarantees.

### Non-idempotent consumers

At-least-once processing can duplicate effects.

### Treating consumer lag as only a Kafka problem

The real bottleneck may be a downstream database or external API.

### Infinite retention without a reason

Retention consumes storage and affects recovery planning.

### Putting huge payloads in events

Store large blobs in object storage and put references/metadata in Kafka when appropriate.

## Related notes

- [Data lakes and lakehouses](04_data_lakes_and_lakehouses.md)
- [Pipelines, orchestration, and data quality](06_data_pipelines_orchestration_and_quality.md)
- [Spark SQL](03_spark_sql.md)
- [Transactions](../04_acid_properties_and_transactions/)
