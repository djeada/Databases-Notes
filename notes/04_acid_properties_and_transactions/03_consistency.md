# Consistency: Preserve the Rules That Make Data Valid

In ACID, **consistency** means that correct transactions take the database from a valid state to another valid state. A valid state satisfies the system's required rules. The database enforces declared constraints; the application must correctly implement rules that are not fully expressed by those constraints.

This use of “consistency” concerns valid data. [Eventual consistency](../06_distributed_databases/07_eventual_consistency.md) concerns when separate copies agree. The same word describes different questions.

## Name the rules before choosing a mechanism

For the bookstore, “the data should be correct” is too vague. These rules are specific enough to test:

| Rule | Possible enforcement |
|---|---|
| Every customer has a distinct email | `UNIQUE` and `NOT NULL` |
| Each order references an existing customer | `FOREIGN KEY` and `NOT NULL` |
| Stock cannot be negative | `CHECK (stock >= 0)` and `NOT NULL` |
| A purchased quantity is positive | `CHECK (quantity > 0)` and `NOT NULL` |
| A successful checkout records both its stock change and its items | Correct transaction logic |

A **constraint** is a rule declared in the schema that the database checks when data changes. An **invariant** is any condition that must remain true as the system operates. An invariant may be implemented by a constraint, transaction logic, or both.

## Test a declared rule

Use the fresh [bookstore setup](../03_sql/01_intro_to_sql.md). Product 10 starts with stock 5 and has a nonnegative-stock constraint.

```sql
UPDATE products SET stock = -1 WHERE product_id = 10;
```

This statement is deliberately invalid. SQLite rejects it with a check-constraint failure; it does not store stock -1. Run it on its own, rather than including it in a script expected to complete successfully.

```sql
SELECT stock FROM products WHERE product_id = 10;
```

The value is still 5. The constraint protects this rule even if an application sends a bad update.

`CHECK (stock >= 0)` alone does not reject `NULL` in SQL: a check generally rejects a false result, while an unknown result is allowed. `NOT NULL` supplies the separate requirement that a value be present. Likewise, foreign-key enforcement must actually be enabled; the SQLite setup uses `PRAGMA foreign_keys = ON` for each connection.

## A valid row can still belong to an invalid workflow

Consider decreasing stock by one and committing without creating an order. Every remaining row may satisfy its keys and checks. Nevertheless, the checkout's business rule has been violated.

The engine cannot infer that every stock reduction must correspond to a sale: stock might also decrease because a damaged book was removed. The application needs a clearly defined operation, the right transaction boundary, and suitable concurrency control.

**Atomicity** makes changes an all-or-nothing unit. **Consistency** asks whether that unit performs a valid change. A transaction can atomically deduct the wrong quantity.

## A check followed by a write can race

Suppose one copy remains. Two transactions each read stock 1 and independently decide that a sale is allowed. Their decisions were based on data that can change before they write.

For a simple stock reservation, combine the condition and modification:

```sql
UPDATE products
SET stock = stock - 1
WHERE product_id = 10 AND stock >= 1;
```

Continue only if one row changed. Handle any concurrency failure according to the engine and retry policy. Keep the order inserts in the same transaction. This avoids relying on an earlier, separate availability check.

More complex invariants can span multiple rows. For example, limiting a customer's total unpaid orders cannot generally be enforced by an ordinary row-level `CHECK`. The design may require a different schema, explicit locking, or serializable isolation with retries. See [Isolation](04_isolation.md) and the [double booking problem](../07_concurrency_control/04_double_booking_problem.md).

## Check your understanding

1. Why are `CHECK` and `NOT NULL` separate requirements?
2. Can a database satisfy every declared constraint while a checkout is still wrong?
3. What changes when the stock test becomes part of the update?
4. How does ACID consistency differ from replicas eventually agreeing?

Next: [Isolation](04_isolation.md) explains what concurrent transactions can observe.
