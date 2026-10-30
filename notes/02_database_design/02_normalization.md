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

Suppose the bookstore needs to find each ordered product and record its quantity. A column such as `products = '10,20,30'` bundles several independently meaningful product references into one value. Parsing this string to find product 20 or attach quantities is a warning sign.

**Incorrect for this requirement — a repeating list inside one value:**

| order_id | customer_id | products |
|---|---|---|
| 101 | 1 | `10,20` |

**Correct 1NF shape — one row for each order line:**

```text
orders(order_id, customer_id)
order_items(order_id, line_number, product_id, quantity)
```

| order_id | line_number | product_id | quantity |
|---|---|---|---|
| 101 | 1 | 10 | 2 |
| 101 | 2 | 20 | 1 |

Each cell now carries one value *for this model*, and a line has an identifiable key. This is the practical idea behind **first normal form (1NF)**. It does **not** yet establish 2NF or 3NF; the earlier combined table has single values in every cell and still repeats customer and product facts.

“Atomic” does not mean physically indivisible: a date can remain one value despite containing a year, month, and day. A list or JSON document can also be a legitimate opaque value for a different requirement. The problem here is that the application treats its elements as independently related products.

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

Our combined table has a two-column key `(order_id, line_number)`. But `order_id → customer_id`: finding the customer needs only part of that key.

**Incorrect — 1NF but not 2NF:**

```text
order_items(order_id, line_number, customer_id, product_id, quantity)
```

**Correct for 2NF — put order facts with the order:**

```text
orders(order_id, customer_id, customer_name)
order_items(order_id, line_number, product_id, product_title, quantity, purchase_price_cents)
```

The `orders` row represents each order once; line-specific quantity and charged price stay with the line. This is an *intermediate* 2NF design, **not yet 3NF**: customer names and product titles still live in tables identified by something other than their natural owner.

A **candidate key** is a minimal set of attributes identifying a row: removing any column stops it being a key. **2NF** requires 1NF and that no non-prime attribute depend on a proper subset of **any** candidate key. A *prime attribute* belongs to at least one candidate key; for this example, `customer_id` is not prime in the combined line table. A single-column candidate key cannot have this kind of partial dependency.

## Third normal form: remove the extra hop

The 2NF `orders` table still repeats Alice's name across her orders. The dependency has an extra hop:

```text
order_id → customer_id → customer_name
```

Similarly, in the 2NF line table, `(order_id, line_number) → product_id → product_title`.

**Incorrect — still duplicated in the 2NF tables:** `orders(order_id, customer_id, customer_name)` and `order_items(..., product_id, product_title, ...)`.

**Correct 3NF design — each shared fact has one owner:**

```text
customers(customer_id, customer_name)
products(product_id, product_title, current_price_cents)
orders(order_id, customer_id)
order_items(order_id, line_number, product_id, quantity, purchase_price_cents)
```

Now renaming Alice changes one customer row, and changing a catalog title changes one product row. Joins reconstruct the display for each order, rather than storing repeated names or titles.

This illustrates **3NF**: in this example, a non-key attribute must not depend transitively on the key through another non-key attribute. This is a teaching shortcut, not the full definition for overlapping candidate keys; the formal criterion appears below.

## Implement the corrected design in SQLite

Run this after the raw-table experiment in the same SQLite database (with `PRAGMA foreign_keys = ON`). These four tables are the **correct** counterpart of `norm_raw_lines`. The primary and foreign keys make row identity and references explicit. Prices are integer cents.

```sql
CREATE TABLE norm_customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name TEXT NOT NULL
);
CREATE TABLE norm_products (
    product_id INTEGER PRIMARY KEY,
    product_title TEXT NOT NULL,
    current_price_cents INTEGER NOT NULL CHECK (current_price_cents >= 0)
);
CREATE TABLE norm_orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES norm_customers(customer_id)
);
CREATE TABLE norm_order_items (
    order_id INTEGER NOT NULL REFERENCES norm_orders(order_id),
    line_number INTEGER NOT NULL,
    product_id INTEGER NOT NULL REFERENCES norm_products(product_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    purchase_price_cents INTEGER NOT NULL CHECK (purchase_price_cents >= 0),
    PRIMARY KEY (order_id, line_number)
);

INSERT INTO norm_customers VALUES (1, 'Alice Smith');
INSERT INTO norm_products VALUES
    (10, 'Database Basics', 1800),
    (20, 'SQL Practice', 2500);
INSERT INTO norm_orders VALUES (101, 1), (102, 1);
INSERT INTO norm_order_items VALUES
    (101, 1, 10, 2, 1500),
    (101, 2, 20, 1, 2500),
    (102, 1, 10, 1, 1500);

SELECT o.order_id, i.line_number, c.customer_name,
       p.product_title, i.quantity, i.purchase_price_cents
FROM norm_orders AS o
JOIN norm_customers AS c ON c.customer_id = o.customer_id
JOIN norm_order_items AS i ON i.order_id = o.order_id
JOIN norm_products AS p ON p.product_id = i.product_id
ORDER BY o.order_id, i.line_number;
```

| order_id | line_number | customer_name | product_title | quantity | purchase_price_cents |
|---|---|---|---|---|---|
| 101 | 1 | Alice Smith | Database Basics | 2 | 1500 |
| 101 | 2 | Alice Smith | SQL Practice | 1 | 2500 |
| 102 | 1 | Alice Smith | Database Basics | 1 | 1500 |

The *join output* repeats names and titles to display each purchase, but the **stored data** has only one customer name and one title per product. `norm_order_items` owns each line's historical price, while `norm_products` owns the current catalog price.

The corrected name was chosen deliberately; blindly using `SELECT DISTINCT` on contradictory source records cannot decide which name is authoritative. A migration must resolve conflicts before adding keys and populating these tables. For a broader bookstore schema, see [data models](../01_introduction_to_databases/04_data_models.md).

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

**Correct BCNF decomposition for `teacher → subject`:** keep each teacher's subject once and record student–teacher assignments separately.

`teacher_subject` (key: `teacher`):

| teacher | subject |
|---|---|
| Lee | Databases |
| Rao | Networks |

`student_teacher` (key: `(student, teacher)`):

| student | teacher |
|---|---|
| Alice | Lee |
| Bob | Lee |
| Alice | Rao |

The shared `teacher` determines the subject, making the join lossless. **But this does not automatically preserve every original rule:** assigning a new teacher Chen to Databases, then assigning Alice to Chen, would pass the individual table keys but break the rule that Alice has only one teacher for Databases. The corrected *BCNF structure* therefore still needs a cross-table constraint or transaction-safe validation for that business rule. This is why lossless decomposition and dependency preservation are distinct questions.

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

**Incorrect 4NF design:** the combined table above stores four rows for just two independent lists.

**Correct 4NF design:** represent each list once, using two tables:

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

**Incorrect decomposition:** replacing the three original triples with only their pairwise projections would admit `(S1, P1, J2)`, so it changes the meaning of the data.

**Correct decomposition in a *different* business situation:** suppose the rules explicitly guarantee that every supplier/product/project triple permitted by all three pairs is approved. For pairwise rows `supplier_product = {(S1, P1)}`, `supplier_project = {(S1, J1), (S1, J2)}`, and `product_project = {(P1, J1), (P1, J2)}`, the only valid triples are `(S1, P1, J1)` and `(S1, P1, J2)`. Joining the pairwise tables reconstructs exactly those two facts, so the split is lossless **under that rule**.

**5NF** addresses join dependencies: when can projections be joined without changing the facts? It is useful for genuine multiway relationship rules, but a diagram with three pairwise edges is not enough evidence to remove the triple table.

## 6NF and temporal facts

Some temporal designs split independently changing facts into very small relations. A customer's address and credit limit may have different validity intervals. Keeping them in one versioned row can require copying one whenever only the other changes.

For example, separate address history `(customer_id, valid_from, address)` and credit-limit history `(customer_id, valid_from, limit_cents)` let each fact have its own timeline. Queries must still define interval endpoints, gaps, overlap rules, and how facts are combined at a chosen time. Timestamped tables are not automatically 6NF; the formal criterion concerns irreducible join dependencies.

Most operational designs begin with 3NF or a carefully reasoned BCNF design, then inspect actual rules that motivate higher forms. PostgreSQL and other relational engines implement the resulting tables and constraints; there is no `NORMALIZE TABLE` command that discovers your business dependencies for you.

## A design review procedure

Use a small **incorrect-versus-correct** checklist before declaring a schema normalized:

| Check | Incorrect or unproven | Correct approach |
|---|---|---|
| Business dependencies | Infer `title → product_id` from a few rows | Confirm rules with the domain; several products may share a title |
| Keys | Inspect only the chosen primary key | Identify all candidate keys and test partial and transitive dependencies |
| Lossless joins | Split a triple into pairs because each pair looks valid | Join projections and check for missing or spurious tuples |
| Constraints | Assume a lossless split preserves every rule | List which rules remain local and which require cross-table enforcement |
| Historical facts | Replace past charged price with current catalog price | Keep distinct facts with their actual owner and time meaning |
| Performance | Duplicate customer names to avoid an unmeasured join | Measure first; plan maintenance if redundancy is justified |

Check insertion, update, and deletion anomalies using counterexamples, not only happy-path data. Finally compare any proposed decomposition against the application's real business rules.

Normalization protects representation; concurrency control protects overlapping changes. A normalized schema can still suffer a lost update if the application uses unsafe read-and-write logic.

## Check your understanding

1. Which anomaly appears when Alice has different names on different order lines?
2. Why does an order's customer belong in `orders`, rather than every item row?
3. Why should purchase price remain on the order item?
4. What could go wrong if a decomposition loses the columns connecting its pieces?

Continue with [denormalization](03_denormalization.md) to learn when a measured read workload justifies deliberate duplication.
