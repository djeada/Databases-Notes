# Normalization: Store Each Fact in the Right Place

Normalization is a way to organize related facts so a change does not require editing many copies of the same information. Begin with the problems in a combined table, then use the normal forms to explain how to separate it safely.

You should already understand rows, primary keys, and foreign keys from [data models](../01_introduction_to_databases/04_data_models.md).

## Start with a table that repeats facts

Suppose every order line stores the customer's details and the product's title:

| order_id | line_number | customer_id | customer_name | product_id | product_title | quantity |
| --- | --- | --- | --- | --- | --- | --- |
| 101 | 1 | 1 | Alice | 10 | Database Basics | 2 |
| 101 | 2 | 1 | Alice | 20 | SQL Practice | 1 |
| 102 | 1 | 1 | Alice | 10 | Database Basics | 1 |

The row's identifier is the pair `(order_id, line_number)`. Alice's name is repeated, even though it describes a customer rather than a particular line.

If she changes her name, all three rows need an update. Missing one update leaves contradictory names for customer 1. This is an **update anomaly**: a problem caused by storing one fact in several places.

Two other anomalies follow. We cannot record a new product without inventing an order line, an **insertion anomaly**. Deleting the last line containing a product would lose its title, a **deletion anomaly**.

## Make the anomalies visible in SQL

Run this separate SQLite experiment in a fresh database. It records the intentionally repeated customer name from the opening example:

```sql
PRAGMA foreign_keys = ON;

CREATE TABLE norm_raw_lines (
    order_id INTEGER NOT NULL,
    line_number INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    customer_name TEXT NOT NULL,
    product_id INTEGER NOT NULL,
    product_title TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    PRIMARY KEY (order_id, line_number)
);
INSERT INTO norm_raw_lines VALUES
    (101, 1, 1, 'Alice', 10, 'Database Basics', 2),
    (101, 2, 1, 'Alice', 20, 'SQL Practice', 1),
    (102, 1, 1, 'Alice', 10, 'Database Basics', 1);
UPDATE norm_raw_lines SET customer_name = 'Alice Smith' WHERE order_id = 102;

SELECT customer_id, COUNT(DISTINCT customer_name) AS stored_names
FROM norm_raw_lines
GROUP BY customer_id;
```

| customer_id | stored_names |
|---|---|
| 1 | 2 |

The update succeeded because the raw table has no rule connecting the repeated names. Yet the business rule `customer_id → customer_name` has been broken. Normalization changes the representation so this fact is stored at its proper owner rather than trusting every writer to repair every copy.

## First normal form: represent separate facts separately

A column such as `products = '10,20,30'` bundles several independently meaningful product references into one value. To find one product or attach a quantity, the application must parse that string.

Use an order-items table with one row per line instead. This removes the repeating list and gives each value a clear role. That is the practical idea behind **first normal form**, or **1NF**.

“Atomic” values are values used as one value in the chosen model. A date is not invalid because it contains a year, month, and day. The issue is how a fact is represented and used, not whether it can ever be subdivided.

## Understand a dependency with a question

A **functional dependency** `X → Y` means that knowing X determines Y. Ask: “if two rows have the same X, must they have the same Y?”

In our bookstore:

```text
customer_id → customer_name
product_id → product_title
order_id → customer_id
(order_id, line_number) → product_id, quantity, purchase_price
```

These are assumed business rules. A sample with no contradictions does not prove a rule. Product titles, for example, need not determine product IDs because several products can share a title.

## Second normal form: use the whole key

Our combined table has a two-column key. But the customer for an order depends on `order_id` alone, without needing `line_number`.

Move order-level facts into `orders`. Keep line-level facts in `order_items`:

```text
orders(order_id, customer_id, customer_name)
order_items(order_id, line_number, product_id, product_title, quantity, purchase_price)
```

This removes a **partial dependency**: a non-key fact depending on only part of a candidate key. **2NF** requires 1NF and no such dependency on a proper subset of any candidate key.

A **candidate key** is a minimal identifier: removing any of its columns would stop it identifying the row. Consider all candidate keys, not only the one chosen as primary.

## Third normal form: remove the extra hop

The new `orders` table still repeats Alice's name. The dependency is indirect:

```text
order_id → customer_id → customer_name
```

The name belongs with the customer. Move it there. Likewise, keep product titles in `products`:

```text
customers(customer_id, customer_name)
products(product_id, product_title, current_price)
orders(order_id, customer_id)
order_items(order_id, line_number, product_id, quantity, purchase_price)
```

Now renaming Alice changes one row. Orders still identify her by `customer_id`. A join reconstructs the customer name when a report needs it.

This illustrates **3NF**: in this simple design, non-key facts should not depend on another non-key fact rather than directly on the relevant identifier. Designs with several overlapping candidate keys need the more precise definition below.

## Create the separated customer and order facts

```sql
CREATE TABLE norm_customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name TEXT NOT NULL
);
CREATE TABLE norm_orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES norm_customers(customer_id)
);
INSERT INTO norm_customers VALUES (1, 'Alice Smith');
INSERT INTO norm_orders VALUES (101, 1), (102, 1);

SELECT o.order_id, c.customer_name
FROM norm_orders AS o
JOIN norm_customers AS c ON c.customer_id = o.customer_id
ORDER BY o.order_id;
```

| order_id | customer_name |
|---|---|
| 101 | Alice Smith |
| 102 | Alice Smith |

The corrected name was chosen deliberately; blindly using `SELECT DISTINCT` on conflicting source records would not decide which name was authoritative. A migration needs conflict resolution before it can safely add keys and populate the new tables. The complete customer/product/order/item implementation is in [data models](../01_introduction_to_databases/04_data_models.md).

## Purchase price is not unnecessary duplication

A product's current price and the price charged on an order line are different facts. If product 10 now costs 18.00 but a past sale charged 15.00, storing both values is correct.

Normalization asks what a value means before deciding where it belongs. Removing purchase price and substituting a join to the current price would destroy historical information.

## Split tables without inventing combinations

A good decomposition must be **lossless**: joining the pieces reconstructs the original facts without adding false combinations or losing facts.

For example, split `(customer_id, customer_name, email)` into tables connected by the customer ID, rather than separating a list of names from a list of emails with no reliable link.

Also check **dependency preservation**: can the original rules still be enforced on the separate tables without joining them merely to check validity? Some decompositions make enforcement more complicated even when the join is lossless.

## More precise definitions and higher forms

Use these after the examples, rather than as the starting explanation. A **superkey** identifies a row but may contain unnecessary columns. A **prime attribute** belongs to at least one candidate key. A dependency is **nontrivial** when it determines something not already included on its left side.

| Form | Rule or problem addressed |
| --- | --- |
| 3NF | For every nontrivial `X → A`, X is a superkey or A is prime. |
| BCNF | For every nontrivial functional dependency, the determinant is a superkey. This removes 3NF's exception for prime attributes. |
| 4NF | Separate independent multivalued facts, such as a person's independent lists of skills and hobbies. Formally, every nontrivial multivalued dependency has a superkey determinant. |
| 5NF | Address join dependencies not implied by candidate keys, without creating spurious combinations. |
| 6NF | No nontrivial join dependencies; useful in some temporal designs. Adding a timestamp alone does not establish 6NF. |
| DKNF | All constraints follow from domains and keys. This is an ideal target, not simply the next numbered step. |

For a BCNF example, suppose each teacher teaches one subject and each student has one teacher per subject. In `(student, subject, teacher)`, `teacher → subject`, but teacher alone does not identify a row. Splitting teacher-subject and student-teacher facts is lossless, yet enforcing one teacher per student and subject now needs a cross-table rule. BCNF can therefore trade simpler facts for harder constraint enforcement.

## BCNF: show why overlapping keys matter

Suppose each teacher teaches exactly one subject, and a student has one teacher for each subject. For `(student, subject, teacher)`, the candidate keys are `(student, subject)` and `(student, teacher)`. Every attribute is prime because it belongs to a candidate key.

| student | subject | teacher |
|---|---|---|
| Alice | Databases | Lee |
| Bob | Databases | Lee |
| Alice | Networks | Rao |

`teacher → subject` holds under the business rule. Teacher alone is not a superkey because Lee has several students. Thus the relation can meet 3NF's prime-attribute exception while violating **Boyce–Codd normal form (BCNF)**.

Decompose it into `(teacher, subject)` and `(student, teacher)`. Their shared teacher determines the teacher/subject part, so joining reconstructs the associations without inventing extra subjects for a teacher. However, nothing in those two tables' simple keys prevents Alice from being assigned two teachers who both teach Databases. Enforcing one teacher per student and subject now needs an additional cross-table rule. This is a concrete reason dependency preservation matters alongside losslessness.

BCNF is useful when repeated facts remain because of overlapping keys. It is not a command to split every table further regardless of enforcement costs.

## 4NF: independent lists create repeated combinations

Suppose a customer can have several preferred languages and several favorite categories, and these lists are independent. Storing `(customer, language, category)` requires every language/category pairing:

| customer | language | category |
|---|---|---|
| Alice | en | History |
| Alice | en | Computing |
| Alice | de | History |
| Alice | de | Computing |

These are **multivalued dependencies**: `customer →→ language` and `customer →→ category`. Adding a language requires a row for every category; deleting one combination can falsely suggest that a language is associated with only one category.

Create two independent tables instead:

```sql
CREATE TABLE norm_languages (
    customer_name TEXT NOT NULL,
    language TEXT NOT NULL,
    PRIMARY KEY (customer_name, language)
);
CREATE TABLE norm_categories (
    customer_name TEXT NOT NULL,
    category TEXT NOT NULL,
    PRIMARY KEY (customer_name, category)
);
INSERT INTO norm_languages VALUES ('Alice', 'en'), ('Alice', 'de');
INSERT INTO norm_categories VALUES ('Alice', 'History'), ('Alice', 'Computing');

SELECT l.language, c.category
FROM norm_languages AS l
JOIN norm_categories AS c ON c.customer_name = l.customer_name
ORDER BY l.language, c.category;
```

| language | category |
|---|---|
| de | Computing |
| de | History |
| en | Computing |
| en | History |

The join reconstructs all combinations because independence is the stated rule. If Alice prefers German only for History, that rule is false, and separating the lists would invent preferences. The decomposition is justified by meaning, not by seeing repeated strings in a sample.

The text name is a short teaching identifier here; a production schema would normally reference a stable customer key.

## 5NF: three pairwise facts do not always imply a triple

A supplier–product–project relation can record which supplier is approved to supply which product to which project. Pairwise lists of supplier/product, supplier/project, and product/project are enough **only if** the business explicitly says every triple allowed by all three pairs is valid.

Consider these approved triples:

```text
(S1, P1, J1)
(S1, P2, J2)
(S2, P1, J2)
```

Projecting them into pairs permits joining `(S1, P1)`, `(S1, J2)`, and `(P1, J2)` into `(S1, P1, J2)`, which was never approved. That is a **spurious tuple**: an invented combination. A naive three-way decomposition is lossy with respect to the intended association even if every original tuple can be recovered.

**5NF** addresses join dependencies: when can projections be joined without changing the facts? It is useful for genuine multiway relationship rules, but a diagram with three pairwise edges is not enough evidence to remove the triple table.

## 6NF and temporal facts

Some temporal designs split independently changing facts into very small relations. A customer's address and credit limit may have different validity intervals. Keeping them in one versioned row can require copying one whenever only the other changes.

For example, separate address history `(customer_id, valid_from, address)` and credit-limit history `(customer_id, valid_from, limit_cents)` let each fact have its own timeline. Queries must still define interval endpoints, gaps, overlap rules, and how facts are combined at a chosen time. Timestamped tables are not automatically 6NF; the formal criterion concerns irreducible join dependencies.

Most operational designs begin with 3NF or a carefully reasoned BCNF design, then inspect actual rules that motivate higher forms. PostgreSQL and other relational engines implement the resulting tables and constraints; there is no `NORMALIZE TABLE` command that discovers your business dependencies for you.

## A design review procedure

List candidate keys and dependencies from requirements, check insertion/update/deletion anomalies, choose decompositions, and verify joins against awkward cases. Identify constraints that remain local and rules that become cross-table checks. Keep historical facts distinct from current facts. Only then discuss deliberate redundancy for a measured read workload.

Normalization protects representation; concurrency control protects overlapping changes. A normalized schema can still suffer a lost update if the application uses unsafe read-and-write logic.

## Check your understanding

1. Which anomaly appears when Alice has different names on different order lines?
2. Why does an order's customer belong in `orders`, rather than every item row?
3. Why should purchase price remain on the order item?
4. What could go wrong if a decomposition loses the columns connecting its pieces?

Continue with [denormalization](03_denormalization.md) to learn when a measured read workload justifies deliberate duplication.
