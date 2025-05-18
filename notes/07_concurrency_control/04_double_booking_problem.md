## Handling the Double-Booking Problem in Databases

The double-booking problem is a common issue in database systems, particularly in applications like booking platforms, reservation systems, and inventory management. It occurs when multiple transactions simultaneously attempt to reserve or modify the same resource, leading to conflicts and inconsistencies. This can result in overbooked flights, double-sold tickets, or oversold inventory, causing significant problems for both businesses and customers.

After reading the material, you should be able to answer the following questions:

1. What is the double-booking problem in database systems, and in which types of applications is it commonly encountered?
2. What are the primary causes of the double-booking problem, such as race conditions and inadequate locking mechanisms?
3. How do shared and exclusive locks help prevent the double-booking problem, and what is the difference between them?
4. What concurrency control strategies can be implemented to avoid double-booking, including proper locking, setting appropriate isolation levels, and using optimistic concurrency control?
5. What are some best practices for designing transactions and managing locks to minimize the risk of double-booking in high-concurrency environments?

### Understanding the Double-Booking Problem

At its core, the double-booking problem arises due to concurrent transactions accessing and modifying shared resources without proper synchronization. When two or more transactions read the same data and proceed to update it based on the initial value, they can inadvertently overwrite each other's changes.

**Illustrative Scenario:**

Imagine two customers, Alice and Bob, trying to book the last available seat on a flight at the same time.

```
Time    Transaction by Alice            Transaction by Bob
--------------------------------------------------------------
T1      Read available seats = 1
T2                                      Read available seats = 1
T3      Book seat (available seats = 0)
T4                                      Book seat (available seats = -1)
```

In this timeline:

- At **T1**, Alice's transaction reads that there is **1 seat available**.
- At **T2**, Bob's transaction also reads **1 seat available**.
- At **T3**, Alice books the seat, updating the available seats to **0**.
- At **T4**, Bob, unaware of Alice's booking, also books the seat, reducing the available seats to **-1**.

This results in an overbooking situation where the system has allowed more bookings than available seats.

### Causes of the Double-Booking Problem

Several factors contribute to the occurrence of double-booking in databases:

- The presence of **race conditions** allows transactions to operate on the same data concurrently without proper synchronization, resulting in unpredictable and conflicting outcomes.  
- **Inadequate locking mechanisms** fail to restrict access effectively, enabling multiple transactions to simultaneously read and write to the same resource, leading to inconsistencies.  
- Utilizing **insufficient isolation levels**, such as read-uncommitted, permits undesirable phenomena like dirty reads and non-repeatable reads, increasing the likelihood of data conflicts.  
- **Delayed writes** occur when transactions read data, perform computations, and then write back changes after a delay, potentially overwriting updates made by other transactions in the interim.  

### Preventing Double-Booking

Preventing double-booking is essential for systems where concurrent users compete for limited resources. By implementing proper locking strategies and transaction controls, you can ensure data integrity and provide a reliable user experience even under high concurrency.

#### Use the Right Lock for the Situation

Locks allow you to control how multiple transactions interact with the same data. Choosing the right lock type helps balance concurrency and safety: exclusive locks prevent other operations from interfering, while shared locks permit safe reads from multiple transactions.

| Lock type             | What it does              | Works in                                       | Typical syntax                                                                                                                           | How to verify                                                                                                                                                                       |
| --------------------- | ------------------------- | ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Exclusive / Write** | One writer, no readers.   | PostgreSQL, MySQL (InnoDB), SQL Server, Oracle | `SELECT … FOR UPDATE;`  (PG/MariaDB)<br>`SELECT … LOCK IN SHARE MODE;` (MySQL 8.0+)<br>`SELECT … WITH (UPDLOCK, HOLDLOCK);` (SQL Server) | Open two sessions. In session A run the locking `SELECT`. In session B run the same statement—observe it block (PG/SQL Server) or return instantly with an error (MySQL w/ NOWAIT). |
| **Shared / Read**     | Many readers, no writers. | Same engines as above                          | `SELECT … FOR SHARE;` (PG)<br>`LOCK TABLE tbl IN SHARE MODE;` (MySQL)<br>`SELECT … WITH (HOLDLOCK);` (SQL Server)                        | Keep session A busy with `SELECT … FOR SHARE`, attempt an `UPDATE` in session B—update waits until session A commits.                                                               |

> **Tip for PostgreSQL:** Inspect current locks with
>
> ```sql
> SELECT pid, locktype, relation::regclass, mode, granted
> FROM pg_locks l JOIN pg_stat_activity a USING(pid);
> ```

#### Pick an Isolation Level You Can Live With

Isolation levels define how visible changes in one transaction are to others. Stricter levels prevent more anomalies but can reduce performance by increasing locking and blocking. Choose the level that meets your consistency needs without unnecessarily hindering throughput.

| Level               | Guarantees                                                                                                                   | Supported by                                                                         | Set with                                           | Quick test                                                                                                                                                                                       |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ | -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **SERIALIZABLE**    | No dirty, non-repeatable or phantom reads. Behaves as if transactions ran one-after-another.                                 | PostgreSQL, SQL Server, Oracle, MySQL 8.0 (but uses extra locks → lower concurrency) | `SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;`    | In two sessions insert into the same over-booked seat; one will roll back with `SQLSTATE 40001` (PG) or `ERROR 1213 (MySQL)`.                                                                    |
| **REPEATABLE READ** | Same row value every time you read it; phantoms still possible (unless engine adds gap locks, e.g. MySQL). Default in MySQL. | PostgreSQL, MySQL (InnoDB), MariaDB, SQL Server (`SNAPSHOT`)                         | `SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;` | Read seat count twice in one Tx while another session inserts a new seat. In MySQL you won’t see new rows (gap locks); in PostgreSQL you will—so use explicit `SELECT … FOR KEY SHARE` to block. |

*Verification script for MySQL*

```sql
-- Session A
SET SESSION TRANSACTION ISOLATION LEVEL SERIALIZABLE;
START TRANSACTION;
SELECT * FROM seats WHERE seat_id = 42 FOR UPDATE;

-- Session B (should block or fail)
START TRANSACTION;
UPDATE seats SET user_id = 99 WHERE seat_id = 42;
```

#### Optimistic Concurrency Control (OCC)

When conflicts are rare, OCC lets you avoid heavy locking by using a version or timestamp column to detect concurrent updates. If a conflict is detected at commit time, the transaction retries, yielding higher throughput under low contention.

```sql
-- Works in: PostgreSQL, SQL Server (rowversion/timestamp), MySQL (generated col), Oracle
BEGIN;
SELECT quantity, version
FROM inventory
WHERE product_id = 101;

-- business logic here …

UPDATE inventory
SET quantity = :new_qty,
    version  = version + 1
WHERE product_id = 101
  AND version   = :old_version;      -- fails (0 rows) if someone changed it
COMMIT;
```

*Verify it*:

1. Run above block in two psql sessions simultaneously.
2. One commit succeeds, the other sees `UPDATE 0`, signaling a retry.

#### Pessimistic Lock First, Work Later

Sometimes you need to lock resources immediately to prevent any concurrent modifications. This approach acquires an exclusive lock up front, ensuring that no one else can read or write the locked rows until you commit.

```sql
-- SQL Server style
BEGIN TRAN;
SELECT * FROM seats
    WITH (UPDLOCK, HOLDLOCK)        -- upgrade immediately
    WHERE seat_id = 101;
/* proceed with booking */
COMMIT;
```

* **Where this shines:** hotel room or flight-seat tables during a flash sale.
* **Where it hurts:** large report queries (locks too many rows & slows everyone).
* **Verification:** Watch `sys.dm_tran_locks`; you’ll see an `X` lock on that row.

#### Enforce Invariants with Constraints & Indexes

Constraints and indexes enforce business rules at the database level, preventing invalid or conflicting data regardless of application logic. They serve as a final safety net against double-booking and other anomalies.

| Technique                                                       | Engines                                      | Sample SQL                                                                                | How to test                                                                              |
| --------------------------------------------------------------- | -------------------------------------------- | ----------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| **Unique constraint** on `(seat_number, flight_id)`             | All relational DBs; MongoDB via unique index | `ALTER TABLE bookings ADD CONSTRAINT u_flight_seat UNIQUE(seat_number, flight_id);`       | Insert same seat twice ⇒ expect `ERROR: duplicate key value violates unique constraint`. |
| **Check constraint** to keep counters ≥ 0                       | PostgreSQL, SQL Server, Oracle, MySQL 8.0+   | `ALTER TABLE flights ADD CONSTRAINT chk_available_seats CHECK (available_seats >= 0);`    | Try manual `UPDATE flights SET available_seats = -1` ⇒ fails.                            |
| **Partial / filtered unique index** to ignore cancelled tickets | PostgreSQL, SQL Server                       | `CREATE UNIQUE INDEX u_active_seat ON bookings(seat,flight_id) WHERE status='CONFIRMED';` | Insert two rows with `status='CONFIRMED'` ⇒ second insert fails.                         |

#### Consistent Lock Ordering to Avoid Deadlocks

Deadlocks occur when transactions lock resources in different orders. By enforcing a global lock acquisition order in all your transactions, you eliminate the circular dependencies that lead to deadlocks.

1. Decide on a global order (e.g., always lock `flights` before `seats`).
2. Code every transaction to follow that order.
3. **Verify:** turn on deadlock logging (`log_lock_waits=on` in PostgreSQL) and run parallel stress tests; no deadlocks should appear.

### Monitor & Tune Locking in Production

*Proactive, continuous monitoring is the cheapest insurance you can buy against “everything-is-stuck” incidents.  The goal is to notice lock contention **while it is still a warning sign**—long before users start calling, background jobs fall behind, or an outage page lights up.*

#### Why you watch

| What you’re looking for               | Why it matters                                                                                  | Typical symptom in the app                     |
| ------------------------------------- | ----------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| **Long-running transactions**         | They hold locks far beyond the “polite” window, slowing everyone else.                          | Pages hang, batch jobs back up.                |
| **Lock-wait time & blocked sessions** | Indicates immediate pain and the exact sessions involved.                                       | Sudden latency spikes.                         |
| **Deadlocks**                         | Proof the workload has crossed a concurrency threshold where simple waiting will never resolve. | Intermittent 400/500 errors, rolled-back work. |
| **Changing hotspot objects**          | Which tables/rows/indexes get hotter over time?                                                 | Emerging scalability bottlenecks.              |

#### Instant health-check queries  (engine specifics)

| Engine             | Handy views / commands                                                                                                    | What to keep on the big screen                                                             | Sample “grab-it-now” query                                                                                                                                                                             |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **PostgreSQL**     | `pg_stat_activity`, `pg_locks`, `pg_blocking_pids()`                                                                      | • Active vs idle in txn<br>• `wait_event = lock` count<br>• Blocking tree                  | `SELECT pid, state, now() - xact_start AS age, wait_event_type, wait_event, query FROM pg_stat_activity WHERE state = 'active' AND now() - xact_start > interval '30s';`                               |
| **SQL Server**     | `sys.dm_exec_sessions`, `sys.dm_exec_requests`, `sys.dm_tran_locks`, `sys.dm_os_waiting_tasks`                            | • `waiting_tasks_count` on **LCK\_**\* waits<br>• Top blockers from `sys.dm_exec_sessions` | `SELECT TOP 10 blocking_session_id, wait_time_ms, wait_type, [text] FROM sys.dm_exec_requests CROSS APPLY sys.dm_exec_sql_text(sql_handle) WHERE blocking_session_id <> 0 ORDER BY wait_time_ms DESC;` |
| **MySQL / InnoDB** | `SHOW ENGINE INNODB STATUS\G`, `information_schema.innodb_trx` / `innodb_locks` / `innodb_lock_waits`, Performance Schema | • “LATEST DETECTED DEADLOCK” section<br>• `trx_wait_started` age                           | `SELECT waiting_trx_id, waiting_pid, blocking_pid, waiting_query FROM information_schema.innodb_lock_waits;`                                                                                           |
| **Oracle**         | `V$LOCK`, `V$SESSION`, `DBA_BLOCKERS`, `DBA_WAITERS`, `V$ASH`                                                             | • `BLOCKING_SESSION_STATUS = 'VALID'` count<br>• Session trees from `DBA_BLOCKERS`         | `SELECT s.sid, s.serial#, l.id1 AS resource1, l.id2 AS resource2, s.seconds_in_wait FROM v$session s JOIN v$lock l ON s.sid = l.sid WHERE l.block = 1;`                                                |
> **Tip** Save each snippet in a “first-aid” script kit (one per engine) so on-call staff can paste-and-go.

#### Alert thresholds that catch trouble early  (*tune for your SLA*)

| Symptom                           | OLTP starting point | Analytic/ETL starting point | How to alert                                    |
| --------------------------------- | ------------------- | --------------------------- | ----------------------------------------------- |
| **Transaction age**               | 30 s                | 5 min                       | gauge, page on P95>threshold for 10 min         |
| **Lock wait**                     | 2 s                 | 30 s                        | histogram + alert on >N waits > threshold / min |
| **Deadlocks**                     | 1/min               | 5/min                       | count(\*) from deadlock view over 5 min window  |
| **% time spent waiting on locks** | 5 %                 | 15 %                        | ratio of lock-wait time to total session time   |

A good rule of thumb: **alert on a trend, not a single incident**—except for deadlocks, which deserve immediate attention because they roll back user work.

#### When an alert fires—triage playbook

I. **Grab blocker details** (queries above) and write them to an incident doc.

II. **Decide: kill vs wait**

* OLTP?  Kill or nudge the blocker; user impact is measured in seconds.
* Batch/ETL?  Often OK to wait unless the blocker exceeds a soft limit (e.g., 10 min).

III. **Collect forensic artefacts**

* PostgreSQL — enable `log_lock_waits`, `deadlock_timeout = 500ms` temporarily.
* SQL Server — run an Extended Events session with `xml_deadlock_report`.
* MySQL — dump `SHOW ENGINE INNODB STATUS` every 30 s until clear.
* Oracle — generate an AWR or ASH report over the incident window.

IV. **Mitigate**

* Shorten transaction scopes (commit early, avoid open cursors).
* Add or refine indexes so readers don’t escalate to page/extent locks.
* Re-order statements to access tables in a consistent order.
* Consider optimistic isolation (PostgreSQL `READ COMMITTED` + `statement_timeout`, SQL Server `READ_COMMITTED_SNAPSHOT`, Oracle `FOR UPDATE SKIP LOCKED`).

#### Automating the watch

| Layer                   | Tooling ideas                                                                                                                           | Notes & nice-to-haves                                                                                                                                         |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **DB native**           | PostgreSQL `pg_stat_statements`, `pgwatch2`; SQL Server Agent alerts + Query Store; MySQL Performance Schema; Oracle Enterprise Manager | Fire alerts directly from the database when possible—latency-free and resilient to network loss.                                                              |
| **Metrics/time-series** | Prometheus + Grafana, Datadog DBM, New Relic, AWS CloudWatch RDS metrics                                                                | Export `lock_wait_time`, `deadlocks_total`, `xact_age_seconds` as counters/gauges.  Grafana’s state-timeline panel is perfect for showing blockers over time. |
| **Notification**        | PagerDuty, Opsgenie, Slack/Teams webhook                                                                                                | Include the SQL text & locks held so the first responder can act without shell access.                                                                        |

#### Continuous improvement loop

1. **Review weekly** the “top ten longest blockers” list.
2. **Refactor** high-contended code paths (break up batch jobs, swap row for key-value store where feasible).
3. **Tune thresholds** as usage grows—successful apps outgrow yesterday’s idea of “long”.
4. **Educate developers**: share post-mortems, highlight how small design choices (e.g., “always write parent then child”) prevent deadlocks entirely.

> *“A lock issue once a quarter is a blameless learning opportunity.  The same lock issue every week is a monitoring failure.”*

### Real-World Example: Ticket Booking System

Below is a self-contained, “copy-paste-ready” walk-through you can run on your laptop to **see the double-booking bug happen, then fix it, and finally prove the fix works**.

####  Stack & prerequisites

| Layer                       | Why we pick it                                                                    | Other options                                                                                                   |
| --------------------------- | --------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| **PostgreSQL ≥ 10**         | Mature row-level locks (`SELECT … FOR UPDATE`) and full ACID isolation levels.    | MySQL (InnoDB), SQL Server (`WITH (UPDLOCK)`), Oracle (`SELECT … FOR UPDATE`), MariaDB, CockroachDB, YugabyteDB |
| **Python 3.9+**             | Quick to script concurrent threads; `psycopg2-binary` client is ubiquitous.       | Node.js + pg, Java + JDBC, Go + pgx                                                                             |
| **psycopg2-binary**         | PostgreSQL driver.                                                                | pg-8000, asyncpg                                                                                                |
| **Threading** (not asyncio) | Easiest to show true race with two parallel transactions in separate connections. | multiprocessing, separate psql shells                                                                           |

> **Install once**
>
> ```bash
> pip install psycopg2-binary
> # PostgreSQL: brew install postgresql or apt install postgresql
> ```

The same SQL works, almost verbatim, on the other databases listed above (the locking keywords differ slightly—see § 5).

#### Build a miniature ticket system

```sql
-- file: setup.sql
DROP TABLE IF EXISTS concerts CASCADE;
CREATE TABLE concerts (
    id          SERIAL PRIMARY KEY,
    title       TEXT NOT NULL,
    tickets_left INTEGER NOT NULL CHECK (tickets_left >= 0)
);

INSERT INTO concerts (title, tickets_left) VALUES ('RockFest 2025', 1);
```

```bash
psql -U postgres -f setup.sql
```

We start with **exactly one ticket** left, which is the classic “last-seat” problem.

#### Reproduce the double-booking bug

Create `race_demo.py`:

```python
import psycopg2, threading, time, random

DSN = "dbname=postgres user=postgres host=localhost"

def buy_ticket(name):
    conn = psycopg2.connect(DSN)
    conn.set_session(isolation_level='READ COMMITTED', autocommit=False)
    cur = conn.cursor()

    try:
        cur.execute("BEGIN;")                         # open txn
        cur.execute("SELECT tickets_left FROM concerts WHERE id = 1;")
        tickets = cur.fetchone()[0]
        print(f"{name}: saw {tickets} ticket(s) left")

        if tickets > 0:
            # simulate user thinking
            time.sleep(random.uniform(0.5, 1.5))
            cur.execute("UPDATE concerts SET tickets_left = tickets_left - 1 WHERE id = 1;")
            print(f"{name}: bought the ticket!")
        else:
            print(f"{name}: no tickets left")

        conn.commit()
    except Exception as e:
        print(f"{name}: ERROR {e}")
        conn.rollback()
    finally:
        conn.close()

threads = [threading.Thread(target=buy_ticket, args=(f"User{i}",)) for i in (1, 2)]
for t in threads: t.start()
for t in threads: t.join()

with psycopg2.connect(DSN) as check_conn:
    with check_conn.cursor() as cur:
        cur.execute("SELECT tickets_left FROM concerts WHERE id = 1;")
        print("After race, tickets_left =", cur.fetchone()[0])
```

Run it twice:

```bash
python race_demo.py
```

**Expected output without locks (typical run)**

```
User1: saw 1 ticket(s) left
User2: saw 1 ticket(s) left
User1: bought the ticket!
User2: bought the ticket!
After race, tickets_left = -1        <-- Over-sale!
```

Both threads decremented the same row because they **read before each other updated**, demonstrating a real-world overbooking.

#### Prevent it (pessimistic locking)

Patch the critical section with `SELECT … FOR UPDATE`:

```python
# ---------- only the changed part ----------
cur.execute("SELECT tickets_left FROM concerts WHERE id = 1 FOR UPDATE;")
```

(Full fixed file: `race_demo_fixed.py` in the repo below.)

Reset stock then test again:

```bash
psql -U postgres -c "UPDATE concerts SET tickets_left = 1 WHERE id = 1;"
python race_demo_fixed.py
```

**Expected output with lock**

```
User1: saw 1 ticket(s) left
User1: bought the ticket!
User2: waiting for row lock...
User2: saw 0 ticket(s) left
User2: no tickets left
After race, tickets_left = 0         <-- Correct
```

> In practice you’d intercept “no tickets left” on the application layer and return an *HTTP 409 – Sold Out*.

Why it works:

* `FOR UPDATE` grabs an **exclusive row-level lock**.
* While User 1 holds it, User 2 blocks until the lock is released.
* Once User 2 enters, the row value is **already updated**, so it sees `0` and aborts its purchase path.

#### At a glance: equivalents in other engines

| Engine         | Pessimistic lock syntax                                              | Notes                                                               |
| -------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------- |
| PostgreSQL     | `SELECT … FOR UPDATE`                                                | Recommended. Use `FOR NO KEY UPDATE` if only updating non-key cols. |
| MySQL (InnoDB) | `SELECT … FOR UPDATE`                                                | Works only in a transaction; default isolation `REPEATABLE READ`.   |
| SQL Server     | `SELECT … WITH (UPDLOCK, ROWLOCK)`                                   | Or table hint in `UPDATE …`.                                        |
| Oracle         | `SELECT … FOR UPDATE`                                                | Same behavior as Postgres.                                          |
| MongoDB        | Use a **transaction** plus an `$inc` with `$cond` or `findAndModify` | Replica sets/sharded clusters only.                                 |
| Redis          | `EVAL` Lua script implementing `GET tickets; DECR ticket` atomically | Single-threaded nature keeps atomicity.                             |

#### Alternative: optimistic locking

If you dislike blocking, add a **version column**:

```sql
ALTER TABLE concerts ADD COLUMN version INTEGER NOT NULL DEFAULT 0;
```

Application flow:

I. `SELECT tickets_left, version FROM concerts WHERE id = 1;`

II. If tickets\_left > 0, run

```sql
UPDATE concerts
   SET tickets_left = tickets_left - 1,
       version = version + 1
 WHERE id = 1
   AND version = :previous_version;
```

III. Check `cursor.rowcount`:

* `1` → success
* `0` → someone modified the row first ⇒ retry or inform user.

Works everywhere a single `UPDATE` can match on the old version.

#### Quick checklist for your project

I. **Pick your strategy**

* Low traffic → pessimistic lock is simplest.
* High traffic / micro-services → optimistic retries scale better.

II. **Keep the critical section tiny** – read, validate, update, commit.

III. **Always wrap in a transaction**; otherwise `FOR UPDATE` does nothing.

IV. Add **monitoring**: alert if `tickets_left` ever < 0 or if conflicts exceed a threshold.

V. Unit-test with **concurrency harness** (exactly like `race_demo.py`) in CI.

