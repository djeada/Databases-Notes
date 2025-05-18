## Two‑Phase Locking (2PL)

Two‑Phase Locking (2PL) is a **scheduling rule** built into database engines to keep concurrent transactions from stepping on each other. 2PL does **not** change *what* your application writes—it changes *when* each transaction is allowed to read or write shared data so that the overall result is the same as some serial order.

> Every transaction first grows its set of locks, hits a lock‑point, and only then starts giving locks back. Once it starts giving locks back it may never take another one.

Real‑World Analogy:

```
┌── Growing Phase ─────┐         ┌── Shrinking Phase ──┐
| Collect all library  |         | Start returning     |
| books you need.      |  ===►   | books; you cannot   |
| No returns allowed   |         | borrow more.        |
└──────────────────────┘         └─────────────────────┘
```

While you hold a book, nobody else can annotate it.  Once you drop it back, anyone may pick it up—but you may not take another.

After reading you should be able to answer…

1. What is Two‑Phase Locking (2PL) and what are its two phases?
2. How does 2PL guarantee serializability among concurrent transactions?
3. What extra rules do *Strict*, *Rigorous*, and *Conservative* 2PL add and why?
4. Which parts are handled automatically by the database engine, and which must the application developer code explicitly?
5. Show a concrete transfer‑funds example that follows 2PL.

### Overview

Before diving into lock types and variations, it helps to see **where 2-phase locking draws the line** between *taking* locks and *releasing* them.
The timeline below exaggerates every step so the **lock-point** is unmistakable.

```text
#
           ┌────────────────────────────── Growing Phase ───────────────────────────────┐               ┌──────────── Shrinking Phase ───────────┐
Timeline ► │  S(A)  │  X(B)  │  X(C)  │  S(D)  │  X(E)  │                               │  ----╂----    │  rel S(A) │  rel X(B) │  … │  rel X(E) │
           └────────┴────────┴────────┴────────┴────────┴── lock-point ─────────────────┘               └────────────────────────────────────────┘
                                        ▲
                                        └── no new locks may be taken past this point

Legend: S = shared/read lock  X = exclusive/write lock
```

Your application decides **which** rows or tables to lock and **when** the transaction starts and ends.
The **database engine** enforces the arrows: once the transaction’s first lock is released it may *only* release—never again acquire—further locks.

### Who Does What? (Engine vs Application)

The **clean hand‑off** between your code and the engine is what makes two‑phase locking practical.  Think of it like a film crew:

* Your **application** is the **director**—it decides the story: which rows/tables to touch and when the scene (transaction) starts and ends.
* The **database engine** is the **stage manager**—it controls access to the set so no actor bumps into another mid‑scene.

```
┌───────────────────────┐          BEGIN / COMMIT / ROLLBACK
│   Application Code    │ ───────────────────────────────────▶  starts & ends txn
└───────────────────────┘                                      (defines scope)
           ▲   SQL stmts / lock hints                               │
           │                                                        ▼
┌───────────────────────┐     grants / blocks        ┌──────────────────────────┐
│  DB Engine Scheduler  │◄───────────────────────────│  Lock Manager (2PL)      │
│   (2PL enforcer)      │                            └──────────────────────────┘
└───────────────────────┘              protects data while letting others run
```

| What needs to happen?      | **Handled inside the engine**                       | **What *you* still write**                                        |
| -------------------------- | --------------------------------------------------- | ----------------------------------------------------------------- |
| Get & hold the right locks | Automatic per statement and current isolation level | Optionally request extras (`SELECT … FOR UPDATE`, `LOCK TABLE …`) |
| Detect / resolve deadlocks | Wait‑for graph, timeouts, victim selection          | Decide retry/back‑off strategy; set `lock_timeout` if offered     |
| Mark txn start / finish    | —                                                   | `BEGIN`, `COMMIT`, `ROLLBACK`                                     |
| Pick isolation level rules | — (engine just applies them)                        | `SET TRANSACTION ISOLATION LEVEL …`                               |
| Choose lock granularity    | Engine picks row / page / table automatically       | Provide hints via DDL or options (`ROWLOCK`, `NOLOCK`)            |

> **Rule of thumb:** your code says *when* a transaction runs and *what* it does; the engine decides *how* to guard the data while it happens.

### The Two Phases of 2PL

During the **growing phase** the engine takes every lock the transaction asks for.  The instant the transaction releases its **first** lock it has crossed the **lock‑point** and entered the **shrinking phase**; from that moment no new locks are permitted.

```
time ►   ─┬─── acquire S(A) ── acquire X(B) ──┬─ commit ─▶
          │         (growing)                 │  (shrinking)
          │                                   │
       lock‑point ────────────────────────────┘
```

Why it works: if every transaction follows that pattern, their critical sections never overlap in a way that produces a non‑serial schedule.

### Variations of Two‑Phase Locking

#### Strict 2PL (default in PostgreSQL, MySQL‑InnoDB, SQL Server)

> Keep **X** locks to the very end, release **S** locks earlier. Default in PostgreSQL, MySQL‑InnoDB, SQL Server

```
time ► ─────────────────────────────────────────────────────────────────────────────→
              growing phase                                  shrinking phase
Row A   S: ███████████▌ release
Row A   X:            ████████████████████████████████████┐
                                                          ├─ COMMIT ─► drop X locks
Row B   S:     ███████▌ release                           │
Row B   X:            ████████████████████████████████████┘
```

*Prevents* dirty reads & cascading aborts while still letting read‑only transactions slip past once they no longer conflict.

#### Rigorous 2PL

> Hold **all** locks (shared & exclusive) until end of transaction.

```
time ► ─────────────────────────────────────────────────────────────────────────────→
Row A   S: █████████████████████████████████████████████████┐
Row A   X:           ███████████████████████████████████████│
Row B   S:      ████████████████████████████████████████████│  COMMIT ─► drop every lock
Row B   X:                  ████████████████████████████████┘
```

*Simplest* to reason about and fully recoverable, but **worst concurrency**: even read locks block everybody else until the very end.

#### Conservative (Static) 2PL

> Grab **every** lock you will ever need **before** doing any work. If a lock is unavailable, wait. Deadlock‑free at the cost of longer initial waits.

```
time ► ─────────────────────────────────────────────────────────────────────────────→
try‑lock {A,B,C} ─╢ acquired ─┬────────────── work (reads/writes) ─────────────┬── COMMIT ─► release all
                            Row A X: ██████████████████████████████████████████
                            Row B X: ██████████████████████████████████████████
                            Row C S: ██████████████████████████████████████████
```

Because the transaction *first* waits until it can lock **every** object it will ever touch, no cycle of wait‑for edges can form—hence no deadlocks.  The trade‑off is potential under‑utilisation while the big lock request is waiting.

### Concrete Example – Funds Transfer

Below is **everything you write** (application layer) versus what the **engine** does silently.

```
-- application code ---------------------------------------------
BEGIN TRANSACTION;           -- start growing phase
SELECT balance               -- engine: S‑lock row A
  FROM Accounts
 WHERE id = 'A'
 FOR UPDATE;                 -- engine upgrades to X‑lock row A

SELECT balance               -- engine: S‑lock row B
  FROM Accounts
 WHERE id = 'B'
 FOR UPDATE;                 -- engine upgrades to X‑lock row B

UPDATE Accounts SET balance = balance - 100 WHERE id = 'A';
UPDATE Accounts SET balance = balance + 100 WHERE id = 'B';
COMMIT;                      -- locks released automatically (strict 2PL)
```

**Under the hood (engine):**

1. Acquires row‑level locks on `A` and `B` in exclusive mode (growing phase).
2. At `COMMIT` it flushes the log, marks the txn committed, then releases the locks (shrinking phase).

### How 2PL Ensures Serializability

Imagine two transactions T1 and T2 that both read and write the same rows.  Because each must hold a conflicting lock before proceeding, either T1 obtains the lock first (T2 waits) **or** T2 obtains the lock first (T1 waits).  The executed order is therefore serial—even though the waits happen inside one schedule.

### Challenges & Remedies

| Challenge                    | Why it happens                         | Common remedies                                                                        |
| ---------------------------- | -------------------------------------- | -------------------------------------------------------------------------------------- |
| **Deadlock**                 | T1 holds A wants B; T2 holds B wants A | ① Lock ordering, ② short transactions, ③ automatic deadlock detection + retry          |
| **Reduced concurrency**      | Locks block readers/writers            | Choose proper isolation level (e.g. Snapshot/MVCC where possible), finer‑grained locks |
| **Lock management overhead** | High‑throughput workloads              | Batch writes, keep transactions lean, use multiversion techniques                      |

Deadlock Illustration:

```
Wait‑for graph
  T1 ───► T2
  ▲       │
  └───────┘  (cycle ⇒ deadlock)
```

### Best Practices When Coding with 2PL

* Keep transactions **small and quick**.
* **Access objects in a consistent order** (e.g. alphabetical by primary key).
* Use **`SELECT … FOR UPDATE`** only when you truly need exclusive access.
* Prefer **row‑level locks** over table locks for write heavy systems.
* **Monitor** blocked/locking sessions (`pg_stat_activity`, `INFORMATION_SCHEMA.INNODB_TRX`, etc.).

### Further Reading

* **ANSI/ISO SQL Standard** – isolation levels & locking semantics
* Bernstein & Newcomer, *Principles of Transaction Processing*
* PostgreSQL docs – *Explicit Locking*, *Concurrency Control*
* Fekete et al., "Making Snapshot Isolation Serializable" (SIGMOD 2005)
