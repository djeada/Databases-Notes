# What a Database Management System Does

A **database** is the stored collection of data. A **database management system (DBMS)** is the software that interprets requests, checks rules, manages access, and maintains storage. In everyday speech, “database” often means both; separating them helps explain how an application works.

## Follow one bookstore request

Suppose Alice opens her order history:

```text
Browser --> Application --> DBMS --> Stored data
Browser <-- Application <-- Query result
```

The browser asks the application for a page. The application sends a database query. The DBMS reads the relevant data and returns rows; the application turns those rows into a page.

A **client** is a program that sends requests to the DBMS. It could be the application, a command-line SQL shell, or an administration tool. The browser usually talks to the application, rather than connecting directly with unrestricted database credentials.

## Inside the DBMS

Consider this query:

```sql
SELECT order_id, order_date
FROM orders
WHERE customer_id = 1;
```

It assumes the `orders` table from the [introductory example](01_databases_intro.md).

The DBMS typically does several kinds of work:

1. **Parse and check:** interpret the SQL and check that the table, columns, and permissions are valid.
2. **Plan:** choose a way to find the rows, such as searching an index or scanning the table.
3. **Execute:** read the data and apply the filter.
4. **Return:** send the selected values back to the client.

A **query plan** describes the operations the engine chooses. An **index** is a separate access structure that can help it find matching rows. A **scan** examines rows or pages in a larger part of the data. Scanning is reasonable when the table is small or most rows are needed.

The application describes the desired result; it usually does not dictate every storage read. That separation lets an engine change its execution strategy as the amount of data changes.

## Check rules when data changes

If an application inserts an order for customer 99, a foreign-key rule can reject it when customer 99 does not exist. If two registrations use the same required unique email, a unique constraint can prevent the duplicate.

A **constraint** is a rule declared in the database definition. Every writer that changes the relevant data is subject to it. Checking only in one web form leaves other writers, such as an import script, able to bypass that form's validation.

The DBMS cannot infer every business rule. It does not know that an item is “available for sale” unless the design and transaction logic express what that means.

## Coordinate work that happens together

Creating an order and reducing stock are related changes. A **transaction** allows the application to group them, commit the completed work, or roll it back if the workflow fails.

Several clients can run transactions at the same time. **Concurrency control** governs their interaction. It prevents certain conflicting outcomes using locks, row versions, or conflict checks, depending on the engine and isolation level. Choosing correct transaction logic remains the application's responsibility.

## Keep useful data close to the processor

Reading persistent storage repeatedly is expensive. A DBMS commonly keeps recently used data pages in memory. A **page** is a storage unit containing records or parts of an index; a **buffer cache** holds pages already brought into memory.

This explains why the same query can be faster on its second run: the required pages may already be cached. It does not mean the first result was incorrect or that every later request avoids storage work.

## Recover after a failure

Many engines record changes in a transaction log, a sequence of recovery information. After a crash, the log helps recover the appropriate committed state. A backup supplies a separately recoverable copy for situations such as accidental deletion or loss of live storage.

Crash recovery and restoring a backup are related but different operations. The engine's guarantees depend on its configuration and storage, so recovery should be tested rather than assumed.

## Embedded software or a separate server?

| Deployment | How the application talks to it | Example |
| --- | --- | --- |
| Embedded | Calls a library inside the application process. | SQLite |
| Client-server | Uses a connection to a separately running database service. | PostgreSQL or MySQL |
| Managed service | Connects to database infrastructure operated partly by a provider. | A hosted PostgreSQL service |

A managed service still needs application-level design, permissions, and recovery decisions. An embedded engine still manages queries and transactions; it simply has no separate database server process.

## Check your understanding

1. Where does the DBMS fit between an application and stored rows?
2. Why can two executions of the same SQL use different plans?
3. Why is a database constraint useful even when a form validates input?
4. How are a buffer cache, transaction log, and backup different?

Continue with [data models](04_data_models.md) to turn a description of a business into entities, relationships, and tables.
