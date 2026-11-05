# Normalization: Store Each Fact in the Right Place

Normalization is a way to organize related facts so a change does not require editing many copies of the same information. Begin with the problems in a combined table, then use the normal forms to explain how to separate it safely. Each split should keep the same facts: changing the table design should not change who ordered a product, its quantity, or the price charged.

You should already understand rows, primary keys, and foreign keys from [data models](https://github.com/djeada/Databases-Notes/blob/main/notes/01_introduction_to_databases/04_data_models.md).

## Start with a table that repeats facts

Suppose every order line stores the customer's details and the product's title, along with the quantity and price charged. Prices are integer cents throughout the examples:

| order_id | line_number | customer_id | customer_name | product_id | product_title | quantity | purchase_price_cents |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 101 | 1 | 1 | Alice | 10 | Database Basics | 2 | 1500 |
| 101 | 2 | 1 | Alice | 20 | SQL Practice | 1 | 2500 |
| 102 | 1 | 1 | Alice | 10 | Database Basics | 1 | 1500 |

The row's identifier is the pair `(order_id, line_number)`. Alice's name is repeated, even though it describes a customer rather than a particular line.

If she changes her name, all three rows need an update. Missing one update leaves contradictory names for customer 1. This is an **update anomaly**: a problem caused by storing one fact in several places.

Two other anomalies follow. We cannot record a new product without inventing an order line, an **insertion anomaly**. Deleting the last line containing a product would lose its title, a **deletion anomaly**.

The update problem becomes visible if only the third row is changed:

| order_id | line_number | customer_id | customer_name |
| --- | --- | --- | --- |
| 101 | 1 | 1 | Alice |
| 101 | 2 | 1 | Alice |
| 102 | 1 | 1 | Alice Smith |

All three rows refer to the same customer, yet two different names are stored. Updating `customer_name` in a single customer row would avoid this disagreement; the order lines would refer to that row by `customer_id`.

The insertion problem is different. Suppose product 30, *Indexing Illustrated*, is available for sale but has not been ordered. The combined table requires a non-null `order_id` and `line_number`, so the following product cannot be recorded on its own:

| product_id | product_title |
| --- | --- |
| 30 | Indexing Illustrated |

In a separate `products` table it can be stored immediately, whether or not any `order_items` row refers to it. Inventing an order to hold product 30 would assert a purchase that never happened.

For the deletion problem, imagine removing order line `(101, 2)`, the only line referring to product 20. The remaining order data contains only these product details:

| order_id | line_number | product_id | product_title |
| --- | --- | --- | --- |
| 101 | 1 | 10 | Database Basics |
| 102 | 1 | 10 | Database Basics |

Product 20's title has disappeared, even though deleting one order line should not delete the catalog entry. With a separate `products` table, the row `(20, SQL Practice)` remains until someone deliberately removes that product.

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
    purchase_price_cents INTEGER NOT NULL,
    PRIMARY KEY (order_id, line_number)
);
INSERT INTO norm_raw_lines VALUES
    (101, 1, 1, 'Alice', 10, 'Database Basics', 2, 1500),
    (101, 2, 1, 'Alice', 20, 'SQL Practice', 1, 2500),
    (102, 1, 1, 'Alice', 10, 'Database Basics', 1, 1500);
UPDATE norm_raw_lines SET customer_name = 'Alice Smith' WHERE order_id = 102;

SELECT customer_id, COUNT(DISTINCT customer_name) AS stored_names
FROM norm_raw_lines
GROUP BY customer_id;
```

| customer_id | stored_names |
|---|---|
| 1 | 2 |

The update succeeded because the raw table has no rule connecting the repeated names. Yet the business rule `customer_id → customer_name` has been broken. Normalization changes the representation so this fact is stored at its proper owner rather than trusting every writer to repair every copy. This experiment deliberately leaves conflicting names; the normal-form walkthrough below uses the consistent opening data so each split can be compared without also changing values.

## First normal form: represent separate facts separately

Suppose the bookstore needs to find each ordered product and record its quantity. A column such as `products = '10,20,30'` bundles several independently meaningful product references into one value. Parsing this string to find product 20 or attach quantities is a warning sign.

For this first step, focus on order 101 and leave names, titles, and prices aside. In the table below, each entry inside `products` is a `(product_id, quantity)` pair. This makes the quantities part of the input rather than introducing them during the split.

Separating the order from its individual lines gives two tables:

```text
orders(order_id, customer_id)
order_items(order_id, line_number, product_id, quantity)
```

The `orders` table records which customer placed the order. The `order_items` table records each product and its quantity on a separate line. Each line can be identified by `(order_id, line_number)` without parsing a list or relying on its position in a comma-separated string.

Each cell then carries one value *for this model*, and each row has an identifiable key. This is the practical idea behind **first normal form (1NF)**. Removing the repeating group does not, by itself, guarantee 2NF or 3NF: the opening combined table already has single values in every cell and still repeats customer and product facts. The two small tables in this focused example also happen to meet the higher forms under our stated rules; later sections return to the full combined table to show the remaining problems.

“Atomic” does not mean physically indivisible: a date can remain one value despite containing a year, month, and day. A list or JSON document can also be a legitimate opaque value for a different requirement. The problem here is that the application treats its elements as independently related products.

Before 1NF, `products` contains a repeating group:

| order_id | customer_id | products |
| --- | --- | --- |
| 101 | 1 | `(10, 2), (20, 1)` |

After removing the repeating group, `orders` (key: `order_id`):

| order_id | customer_id |
| --- | --- |
| 101 | 1 |

`order_items` (key: `(order_id, line_number)`; `order_id` references `orders`):

| order_id | line_number | product_id | quantity |
|---|---|---|---|
| 101 | 1 | 10 | 2 |
| 101 | 2 | 20 | 1 |

## Understand a dependency with a question

A **functional dependency** `X → Y` means that knowing X determines Y. Ask: “if two rows have the same X, must they have the same Y?”

In our bookstore:

```text
customer_id → customer_name
product_id → product_title
order_id → customer_id
(order_id, line_number) → product_id, quantity, purchase_price_cents
```

These are assumed business rules. A sample with no contradictions does not prove a rule. Product titles, for example, need not determine product IDs because several products can share a title.

Consider a hypothetical catalog with an additional customer and a new product that happens to share an existing title:

| customer_id | customer_name |
| --- | --- |
| 1 | Alice |
| 2 | Bob |

| product_id | product_title |
| --- | --- |
| 10 | Database Basics |
| 20 | SQL Practice |
| 31 | Database Basics |

The product title *Database Basics* identifies both products 10 and 31. Therefore, `product_title → product_id` does not hold, even though `product_id → product_title` does. A dependency has a direction: the fact that every product ID has one title does not imply that every title belongs to only one product.

The dependency `order_id → customer_id` also becomes testable with two order lines:

| order_id | line_number | customer_id |
| --- | --- | --- |
| 101 | 1 | 1 |
| 101 | 2 | 1 |
| 103 | 1 | 2 |

Both lines belonging to order 101 must have customer 1. If the second row instead had customer 2, the two rows would contradict the rule about who placed that order. However, the two rows share `order_id = 101` but have different line numbers, showing why `order_id` alone cannot identify a line; the pair `(order_id, line_number)` is needed.

These examples illustrate how to check a proposed dependency against rows. They do not prove that the rule holds for every possible future row. That requires the intended business meaning of the columns.

## Second normal form: use the whole key

Return to the full combined table from the opening example. Its candidate key is `(order_id, line_number)`. But `order_id → customer_id`: finding the customer needs only part of that key. Through `customer_id → customer_name`, the customer's name also depends on `order_id` alone.

The combined table is in 1NF but not 2NF because these customer details depend on a proper subset of the key:

```text
order_lines(order_id, line_number, customer_id, customer_name,
            product_id, product_title, quantity, purchase_price_cents)
```

The two rows for order 101 must repeat `customer_id = 1`, although the customer is a property of the order rather than of either individual line. If the order were reassigned to another customer, both rows would need an update to avoid contradictory customer IDs within the same order.

Moving the order details to their own relation removes that partial dependency:

```text
orders(order_id, customer_id, customer_name)
order_items(order_id, line_number, product_id, product_title, quantity, purchase_price_cents)
```

The `orders` row represents each order once; line-specific quantity and charged price stay with the line. This is an *intermediate* 2NF design, **not yet 3NF**: customer names and product titles still live in tables identified by something other than their natural owner.

In the old combined line table, `order_id = 101` appears twice and each row repeats `customer_id = 1`. In the new `orders` table, order 101 appears once. This fixes the partial dependency because `customer_id` depends on `order_id`, not on the entire `(order_id, line_number)` key. By contrast, the quantity of product 10 is 2 on line `(101, 1)` and 1 on line `(102, 1)`: that value really does describe a particular line and should remain there.

Notice that 2NF does not mean all repetition has gone away. `customer_name` still appears in both orders and `product_title` still appears in two order items. Those repetitions have different causes, which 3NF addresses next. Repeated foreign-key values such as `product_id = 10` are needed to record which product each line refers to; they are not redundant copies of the product's title.

A **candidate key** is a minimal set of attributes identifying a row: removing any column stops it being a key. **2NF** requires 1NF and that no non-prime attribute depend on a proper subset of **any** candidate key. A *prime attribute* belongs to at least one candidate key; for this example, `customer_id` is not prime in the combined line table. A single-column candidate key cannot have this kind of partial dependency, but any other candidate keys must still be checked.

Before 2NF, `order_lines` (key: `(order_id, line_number)`):

| order_id | line_number | customer_id | customer_name | product_id | product_title | quantity | purchase_price_cents |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 101 | 1 | 1 | Alice | 10 | Database Basics | 2 | 1500 |
| 101 | 2 | 1 | Alice | 20 | SQL Practice | 1 | 2500 |
| 102 | 1 | 1 | Alice | 10 | Database Basics | 1 | 1500 |

After removing the partial dependencies, `orders` (key: `order_id`):

| order_id | customer_id | customer_name |
| --- | --- | --- |
| 101 | 1 | Alice |
| 102 | 1 | Alice |

`order_items` (key: `(order_id, line_number)`; `order_id` references `orders`):

| order_id | line_number | product_id | product_title | quantity | purchase_price_cents |
| --- | --- | --- | --- | --- | --- |
| 101 | 1 | 10 | Database Basics | 2 | 1500 |
| 101 | 2 | 20 | SQL Practice | 1 | 2500 |
| 102 | 1 | 10 | Database Basics | 1 | 1500 |

## Third normal form: remove the extra hop

The 2NF `orders` table still repeats Alice's name across her orders. The dependency has an extra hop:

```text
order_id → customer_id → customer_name
```

Similarly, in the 2NF line table, `(order_id, line_number) → product_id → product_title`.

The intermediate 2NF tables still store a customer name with each order and a product title with each line: `orders(order_id, customer_id, customer_name)` and `order_items(..., product_id, product_title, ...)`.

Separating customer and product details from orders and order lines produces the 3NF design:

```text
customers(customer_id, customer_name)
products(product_id, product_title)
orders(order_id, customer_id)
order_items(order_id, line_number, product_id, quantity, purchase_price_cents)
```

Now renaming Alice changes one customer row, and changing a catalog title changes one product row. Joins reconstruct the display for each order, rather than storing repeated names or titles.

The extra hop `order_id → customer_id → customer_name` is eliminated from `orders`: it has `customer_id` but no longer stores `customer_name`. The product title is also removed from each order item, because `product_id` already identifies it in `products`. A later name change from Alice to Alice Smith would affect only the customer row, without requiring edits to either order or any item. The split itself keeps the original name Alice.

The tables still need foreign keys. For example, `orders.customer_id` must refer to an existing customer and `order_items.product_id` must refer to an existing product. Merely moving columns without enforcing valid references would not give the same protection against inconsistent data.

This illustrates **3NF**: in this example, a non-key attribute must not depend transitively on the key through another non-key attribute. This is a teaching shortcut, not the full definition for overlapping candidate keys; the formal criterion appears below. Here `customer_id` does not identify an order, and `product_id` does not identify an order line, so their names and titles belong in separate tables keyed by those IDs.

Before 3NF, the two intermediate 2NF tables are `orders` (key: `order_id`):

| order_id | customer_id | customer_name |
| --- | --- | --- |
| 101 | 1 | Alice |
| 102 | 1 | Alice |

`order_items` (key: `(order_id, line_number)`):

| order_id | line_number | product_id | product_title | quantity | purchase_price_cents |
| --- | --- | --- | --- | --- | --- |
| 101 | 1 | 10 | Database Basics | 2 | 1500 |
| 101 | 2 | 20 | SQL Practice | 1 | 2500 |
| 102 | 1 | 10 | Database Basics | 1 | 1500 |

After removing the transitive dependencies, the same purchases are stored in four tables. `customers` (key: `customer_id`):

| customer_id | customer_name |
| --- | --- |
| 1 | Alice |

`products` (key: `product_id`):

| product_id | product_title |
| --- | --- |
| 10 | Database Basics |
| 20 | SQL Practice |

`orders` (key: `order_id`; `customer_id` references `customers`):

| order_id | customer_id |
| --- | --- |
| 101 | 1 |
| 102 | 1 |

`order_items` (key: `(order_id, line_number)`; `order_id` references `orders`, and `product_id` references `products`):

| order_id | line_number | product_id | quantity | purchase_price_cents |
| --- | --- | --- | --- | --- |
| 101 | 1 | 10 | 2 | 1500 |
| 101 | 2 | 20 | 1 | 2500 |
| 102 | 1 | 10 | 1 | 1500 |

## Implement the corrected design in SQLite

Run this after the raw-table experiment in the same SQLite database (with `PRAGMA foreign_keys = ON`). These four tables are the **correct** counterpart of `norm_raw_lines`. The primary and foreign keys make row identity and references explicit. Prices are integer cents.

For this implementation, resolve the conflicting raw customer names to Alice Smith and also record the current catalog prices: 1800 cents for product 10 and 2500 cents for product 20. `current_price_cents` is an additional catalog fact; it is not created by normalization or inferred from the historical purchase prices. The next section explains why both prices belong in the model.

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

The corrected name was chosen deliberately; blindly using `SELECT DISTINCT` on contradictory source records cannot decide which name is authoritative. A migration must resolve conflicts before adding keys and populating these tables. For a broader bookstore schema, see [data models](https://github.com/djeada/Databases-Notes/blob/main/notes/01_introduction_to_databases/04_data_models.md).

## Purchase price is not unnecessary duplication

A product's current price and the price charged on an order line are different facts. If product 10 now costs 18.00 but a past sale charged 15.00, storing both values is correct.

Normalization asks what a value means before deciding where it belongs. Removing purchase price and substituting a join to the current price would destroy historical information.

The distinction is visible when comparing the catalog with an earlier purchase:

`products`:

| product_id | current_price_cents |
| --- | --- |
| 10 | 1800 |

`order_items`:

| order_id | line_number | product_id | purchase_price_cents |
| --- | --- | --- | --- |
| 101 | 1 | 10 | 1500 |
| 102 | 1 | 10 | 1500 |

If the current catalog price later changes from 1800 to 2000, the `products` row changes but the two `order_items` rows stay at 1500. A report of what customers actually paid still produces 1500 for each purchase. Replacing `purchase_price_cents` with `current_price_cents` would incorrectly report 2000 for both historical orders.

The numbers are not duplicate versions of the same fact: they describe the same product at different points in the business process. A schema is not more normalized merely because it stores fewer values.

## Split tables without inventing combinations

A good decomposition must be **lossless**: joining the pieces reconstructs the original facts without adding false combinations or losing facts. Each piece is a projection of the original relation: keep selected columns and remove duplicate rows. The important question is whether joining those projections recovers exactly the original relation.

For example, split `(customer_id, customer_name, email)` into tables connected by the customer ID, rather than separating a list of names from a list of emails with no reliable link.

The difference matters if two different customers happen to have the same name:

| customer_id | customer_name | email |
| --- | --- | --- |
| 1 | Alice | alice.personal@example.test |
| 2 | Alice | alice.work@example.test |

One safe decomposition keeps the IDs in both pieces:

`customer_names`:

| customer_id | customer_name |
| --- | --- |
| 1 | Alice |
| 2 | Alice |

`customer_emails`:

| customer_id | email |
| --- | --- |
| 1 | alice.personal@example.test |
| 2 | alice.work@example.test |

Joining on `customer_id` gives exactly the original two rows. But consider discarding the ID from `customer_emails` and keeping only `(customer_name, email)`. Joining those records to `customer_names` on the name produces this result:

| customer_id | customer_name | email |
| --- | --- | --- |
| 1 | Alice | alice.personal@example.test |
| 1 | Alice | alice.work@example.test |
| 2 | Alice | alice.personal@example.test |
| 2 | Alice | alice.work@example.test |

The two cross-matched rows are invented; no original row said customer 1 had the work address or customer 2 had the personal address. The split lost the information that connected each customer to the correct email. A lossless decomposition must preserve that connection, not merely include all the original values somewhere in the pieces.

Also check **dependency preservation**: can the original rules still be enforced on the separate tables without joining them merely to check validity? Some decompositions make enforcement more complicated even when the join is lossless.

A lossless join and dependency preservation ask different questions. In the email example, the join reconstructs the data without extra rows because both tables retain the identifying customer ID. Dependency preservation concerns whether a rule, such as “a student has at most one teacher per subject,” can still be checked using keys or constraints within the resulting tables. The BCNF example below shows a lossless split where this second property is not automatic.

## More precise definitions and higher forms

Use these after the examples, rather than as the starting explanation. A **superkey** identifies a row but may contain unnecessary columns. A **prime attribute** belongs to at least one candidate key. A dependency is **nontrivial** when it determines something not already included on its left side.

For example, suppose the following `orders` rows obey the rule that every order ID is unique:

| order_id | customer_id | order_date |
| --- | --- | --- |
| 101 | 1 | 2026-10-05 |
| 102 | 1 | 2026-10-06 |
| 103 | 2 | 2026-10-06 |

Here `order_id` is a candidate key because it identifies a row without any additional column. The pair `(order_id, customer_id)` is also a superkey, but it is not a candidate key: removing `customer_id` leaves a working key. Under these rules, `order_id` is prime, while `customer_id` and `order_date` are non-prime. The dependency `order_id → order_date` is nontrivial because the date is not part of the determinant on the left. By contrast, `(order_id, customer_id) → order_id` is trivial: the right-hand attribute is already included on the left.

| Form | Rule or problem addressed |
| --- | --- |
| 3NF | For every nontrivial `X → A`, X is a superkey or A is prime. |
| BCNF | For every nontrivial functional dependency, the determinant is a superkey. This removes 3NF's exception for prime attributes. |
| 4NF | Separate independent multivalued facts, such as a person's independent lists of skills and hobbies. Formally, every nontrivial multivalued dependency has a superkey determinant. |
| 5NF | Address join dependencies not implied by candidate keys, without creating spurious combinations. |
| 6NF | No nontrivial join dependencies; useful in some temporal designs. Adding a timestamp alone does not establish 6NF. |
| DKNF | All constraints follow from domains and keys. This is an ideal target, not simply the next numbered step. |

For the DKNF distinction, imagine a small table of numbered order lines with a positive quantity:

| order_id | line_number | quantity |
| --- | --- | --- |
| 101 | 1 | 2 |
| 101 | 2 | 1 |
| 102 | 1 | 1 |

If the only business restrictions are that `order_id` and `line_number` together must be unique and `quantity` must be a positive integer, the restrictions follow from the key and the column domains. Now consider a different table with a rule that every order with `destination = DE` must have `delivery_cents = 500`:

| order_id | destination | delivery_cents |
| --- | --- | --- |
| 101 | DE | 500 |
| 102 | FR | 900 |

A row `(103, DE, 900)` has a unique order ID, a recognized destination and a nonnegative fee, yet violates the stated rule for German orders. Separate domain and key checks do not express the required relationship between `destination` and `delivery_cents`. That relationship needs an additional constraint or a different representation; it does not follow automatically from the allowed values of either column or from the key. DKNF asks whether every required constraint follows from domains and keys, not whether a table happens to look small or well-organized. Splitting tables does not automatically achieve this; see [Fagin's definition of domain-key normal form](https://s3.us.cloud-object-storage.appdomain.cloud/res-files/500-tods81.pdf).

For a BCNF example, suppose each teacher teaches one subject and each student has one teacher per subject. In `(student, subject, teacher)`, `teacher → subject`, but teacher alone does not identify a row. Splitting teacher-subject and student-teacher facts is lossless, yet enforcing one teacher per student and subject now needs a cross-table rule. BCNF can therefore trade simpler facts for harder constraint enforcement.

## BCNF: show why overlapping keys matter

Suppose each teacher teaches exactly one subject, and a student has one teacher for each subject. For `(student, subject, teacher)`, the candidate keys are `(student, subject)` and `(student, teacher)`. Every attribute is prime because it belongs to a candidate key.

For example, Lee teaches Databases to Alice and Bob, while Rao teaches Networks to Alice. `teacher → subject` holds under the business rule. Teacher alone is not a superkey because Lee has several students. The dependency satisfies 3NF because `subject` is prime, even though `teacher` is not a superkey. It violates **Boyce–Codd normal form (BCNF)**, which requires a superkey on the left of every nontrivial functional dependency, without the prime-attribute exception.

To remove the repeated teacher–subject fact, keep each teacher's subject once in `teacher_subject(teacher, subject)`, keyed by `teacher`. Record assignments in `student_teacher(student, teacher)`, keyed by `(student, teacher)`, with `teacher` referencing `teacher_subject`.

The shared `teacher` determines the subject, making the join lossless. However, the split does not automatically preserve every original rule. Assigning a new teacher Chen to Databases, then assigning Alice to Chen, would pass the individual table keys but break the rule that Alice has only one teacher for Databases. The corrected *BCNF structure* therefore still needs a cross-table constraint or transaction-safe validation for that business rule. This is why lossless decomposition and dependency preservation are distinct questions.

BCNF is useful when repeated facts remain because of overlapping keys. It is not a command to split every table further regardless of enforcement costs.

The constraint problem can be seen in actual rows. Suppose the `teacher_subject` table is extended with another Databases teacher:

| teacher | subject |
| --- | --- |
| Lee | Databases |
| Rao | Networks |
| Chen | Databases |

The `student_teacher` table can then contain both of these assignments without breaking its `(student, teacher)` key:

| student | teacher |
| --- | --- |
| Alice | Lee |
| Alice | Chen |

Joining them gives:

| student | subject | teacher |
| --- | --- | --- |
| Alice | Databases | Lee |
| Alice | Databases | Chen |

Both tables satisfy their own keys and `teacher → subject`, but the original rule that Alice has only one teacher per subject is violated. This example explains exactly what was lost from local enforcement. The decomposition is lossless, yet the `(student, subject) → teacher` rule must now be checked across the tables, for example by a safely enforced database-level mechanism. Checking once in application code without concurrency protection would not be enough.

Returning to the valid assignments, before BCNF, `student_subject_teacher` (candidate keys: `(student, subject)` and `(student, teacher)`):

| student | subject | teacher |
| --- | --- | --- |
| Alice | Databases | Lee |
| Bob | Databases | Lee |
| Alice | Networks | Rao |

After storing the teacher–subject fact in its own table, `teacher_subject` (key: `teacher`):

| teacher | subject |
| --- | --- |
| Lee | Databases |
| Rao | Networks |

`student_teacher` (key: `(student, teacher)`; `teacher` references `teacher_subject`):

| student | teacher |
| --- | --- |
| Alice | Lee |
| Bob | Lee |
| Alice | Rao |

## 4NF: independent lists create repeated combinations

Suppose a customer can have several preferred languages and several favorite categories, and these lists are independent. Alice prefers English and German and likes History and Computing. Independence means neither language restricts the categories: storing `(customer_name, language, category)` requires all four language/category pairings.

These are **multivalued dependencies**: `customer_name →→ language` and `customer_name →→ category`. For one customer, the language list is the same regardless of which category is selected, and the category list is the same regardless of language. Adding a language requires a row for every category; deleting one combination can falsely suggest that a language is associated with only one category.

Assume there are no other dependencies and the key is all three columns. The combined table has no nontrivial functional dependency with a non-superkey determinant, so it is in BCNF. It still violates **4NF**: the multivalued dependencies are nontrivial, and `customer_name` is not a superkey because a customer has several rows. BCNF alone does not remove this kind of repetition.

Represent the two independent lists in `norm_languages(customer_name, language)` and `norm_categories(customer_name, category)` instead. Each table's two columns together form its key.

Instead of four stored language-category combinations, we now store two language facts and two category facts. If Alice adds French, only `(Alice, fr)` needs to be inserted into `norm_languages`, not a row for every category. The query below produces all combinations when the application actually needs them.

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

The independence assumption matters. Suppose Alice prefers English for Computing and German for History, rather than having two independent preference lists:

| customer_name | language | category |
| --- | --- | --- |
| Alice | en | Computing |
| Alice | de | History |

If we split this table into languages and categories as above, their join also produces `(Alice, en, History)` and `(Alice, de, Computing)`. Those extra combinations would claim preferences Alice never expressed. In this situation the relationship itself is a fact, so the three-column table must retain the pairings. The 4NF split is justified by independent multivalued relationships, not by repetition alone.

For the original independent lists, before 4NF, `customer_preferences` (key: `(customer_name, language, category)`):

| customer_name | language | category |
| --- | --- | --- |
| Alice | en | History |
| Alice | en | Computing |
| Alice | de | History |
| Alice | de | Computing |

After separating the independent lists, `norm_languages` (key: `(customer_name, language)`):

| customer_name | language |
| --- | --- |
| Alice | en |
| Alice | de |

`norm_categories` (key: `(customer_name, category)`):

| customer_name | category |
| --- | --- |
| Alice | History |
| Alice | Computing |

## 5NF: three pairwise facts do not always imply a triple

A supplier–product–project relation can record which supplier is approved to supply which product to which project. Pairwise lists of supplier/product, supplier/project, and product/project are enough **only if** the business explicitly says every triple allowed by all three pairs is valid.

A supplier ID identifies a supplier, a product ID identifies a product, and a project ID identifies a project. In this example, a row means that the specific supplier is approved to deliver that specific product to that specific project. Merely having permission for each pair does not necessarily imply permission for the triple.

Consider these approved triples:

| supplier | product | project |
| --- | --- | --- |
| S1 | P1 | J1 |
| S1 | P2 | J2 |
| S2 | P1 | J2 |

Projecting them into pairs permits joining `(S1, P1)`, `(S1, J2)`, and `(P1, J2)` into `(S1, P1, J2)`, which was never approved. That is a **spurious tuple**: an invented combination. A naive three-way decomposition is lossy with respect to the intended association even if every original tuple can be recovered.

Here are the three pairwise projections formed from those original approved triples.

`supplier_product`:

| supplier | product |
| --- | --- |
| S1 | P1 |
| S1 | P2 |
| S2 | P1 |

`supplier_project`:

| supplier | project |
| --- | --- |
| S1 | J1 |
| S1 | J2 |
| S2 | J2 |

`product_project`:

| product | project |
| --- | --- |
| P1 | J1 |
| P1 | J2 |
| P2 | J2 |

Joining all three pairwise tables reconstructs the following rows:

| supplier | product | project | in original approvals? |
| --- | --- | --- | --- |
| S1 | P1 | J1 | yes |
| S1 | P1 | J2 | no |
| S1 | P2 | J2 | yes |
| S2 | P1 | J2 | yes |

The row `(S1, P1, J2)` is not a harmless duplicate. It grants an approval that did not exist in the original relation. This is why the pairwise projection is not lossless under the first business rule.

Replacing the three original triples with only their pairwise projections would admit `(S1, P1, J2)`, so it changes the meaning of the data.

In a different business, the rules may explicitly guarantee that any supplier, product and project combination is permitted whenever all three pairwise permissions hold. For that business, the pairwise relationships themselves are the facts. A **join dependency** says that the triple relation must equal the join of these three projections for every valid state of the data.

In the valid example below, `(S2, P2, J1)` does not appear because supplier S2 has no permission for project J1, even though S2 can supply product P2 and P2 is approved for J1. Conversely, `(S1, P2, J2)` appears because all three relevant pairs are present. Under this business rule, every generated triple is supposed to be present, so the decomposition is lossless. The difference from the earlier counterexample is the *meaning of the approval rule*, not the shape of the table.

Assume no pair of columns determines the third, so the candidate key of the combined table is `(supplier, product, project)`. There are also no independent lists that justify a two-table split. The table can therefore be in 4NF while still having a three-way join dependency not implied by its candidate key. **5NF** removes that remaining redundancy by storing the pairwise facts separately. Each resulting pair table has both columns as its key.

5NF is useful for genuine multiway relationship rules, but a diagram with three pairwise edges is not enough evidence to remove the triple table. The first example must keep its triple approvals; only the second example's rule justifies the split.

Before 5NF, `approved_supplies`, under the rule that all three pairwise permissions imply approval (key: `(supplier, product, project)`):

| supplier | product | project |
| --- | --- | --- |
| S1 | P1 | J1 |
| S1 | P2 | J1 |
| S1 | P2 | J2 |
| S2 | P2 | J2 |

After separating the pairwise facts, `supplier_product` (key: `(supplier, product)`):

| supplier | product |
| --- | --- |
| S1 | P1 |
| S1 | P2 |
| S2 | P2 |

`supplier_project` (key: `(supplier, project)`):

| supplier | project |
| --- | --- |
| S1 | J1 |
| S1 | J2 |
| S2 | J2 |

`product_project` (key: `(product, project)`):

| product | project |
| --- | --- |
| P1 | J1 |
| P2 | J1 |
| P2 | J2 |

## 6NF and temporal facts

Some temporal designs split independently changing facts into very small relations. A customer's address and credit limit may have different validity intervals. Keeping them in one versioned row can require copying one whenever only the other changes.

For example, separate address history `(customer_id, valid_from, valid_to, address)` and credit-limit history `(customer_id, valid_from, valid_to, limit_cents)` let each fact have its own timeline. Queries must still define interval endpoints, gaps, overlap rules, and how facts are combined at a chosen time. Timestamped tables are not automatically 6NF; the formal criterion concerns irreducible join dependencies.

Suppose both facts were originally kept in a single versioned customer table, with dates representing the first valid day and the first day after the interval. A range from `2026-01-01` to `2026-02-01` includes January but not February 1.

On February 1 only the credit limit changed, but the address had to be repeated in a new row. On March 1 only the address changed, but the credit limit had to be copied again. If these two facts genuinely vary independently, their histories can be stored separately. Adjacent intervals with the same address can be combined in the address history; adjacent intervals with the same limit can be combined in the limit history.

For a query asking about `2026-02-15`, the address row valid on that date says Berlin and the limit row says 150000. The answer is obtained by matching the customer and the overlapping intervals, not by joining on equal `valid_from` dates: the starts of the two histories need not coincide.

| as_of_date | customer_id | address | limit_cents |
| --- | --- | --- | --- |
| 2026-02-15 | 1 | Berlin | 150000 |

To reconstruct the original history, join rows for the same customer whose intervals overlap, and use the intersection as the resulting interval. The Berlin address interval overlaps both credit-limit intervals, recovering the January and February rows; the Leipzig interval recovers the March row. This is a temporal join, rather than a natural join on the two date columns.

Each history needs explicit rules about interval overlap, gaps, and inclusive or exclusive boundaries. This example shows why independently changing temporal facts may be separated; it does not establish that any table with timestamps is in 6NF. The formal requirement is that the relation have no nontrivial join dependency, assessed against the full set of business constraints. For interval data, the decomposition and join must use temporal semantics; see [Darwen's explanation of 6NF and temporal histories](https://www.dcs.warwick.ac.uk/~hugh/TTM/TemporalData.Warwick.pdf).

Most operational designs begin with 3NF or a carefully reasoned BCNF design, then inspect actual rules that motivate higher forms. PostgreSQL and other relational engines implement the resulting tables and constraints; there is no `NORMALIZE TABLE` command that discovers your business dependencies for you.

Before the temporal split discussed for 6NF, `customer_history` (key: `(customer_id, valid_from)`, with nonoverlapping intervals per customer):

| customer_id | valid_from | valid_to | address | limit_cents |
| --- | --- | --- | --- | --- |
| 1 | 2026-01-01 | 2026-02-01 | Berlin | 100000 |
| 1 | 2026-02-01 | 2026-03-01 | Berlin | 150000 |
| 1 | 2026-03-01 | 2026-04-01 | Leipzig | 150000 |

After giving each fact its own timeline, `customer_address_history` (key: `(customer_id, valid_from)`, with nonoverlapping intervals per customer):

| customer_id | valid_from | valid_to | address |
| --- | --- | --- | --- |
| 1 | 2026-01-01 | 2026-03-01 | Berlin |
| 1 | 2026-03-01 | 2026-04-01 | Leipzig |

`customer_limit_history` (key: `(customer_id, valid_from)`, with nonoverlapping intervals per customer):

| customer_id | valid_from | valid_to | limit_cents |
| --- | --- | --- | --- |
| 1 | 2026-01-01 | 2026-02-01 | 100000 |
| 1 | 2026-02-01 | 2026-04-01 | 150000 |

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

For example, even in a normalized `inventory(product_id, stock_count)` table, two transactions may both read stock 10 and each independently decide to write 9 after one item is sold:

| step | transaction A | transaction B | stored stock_count |
| --- | --- | --- | --- |
| Start |  |  | 10 |
| Read | reads 10 |  | 10 |
| Read |  | reads 10 | 10 |
| Write | writes 9 |  | 9 |
| Write |  | writes 9 | 9 |

Two items were sold, so the correct result is 8, but the final stored value is 9. That lost update cannot be repaired by moving columns into additional tables; it needs appropriate transactional update logic, locking, or other concurrency control.

## Summary

| Normal Form | Main Rule                                                                                                                    |
| ----------- | ---------------------------------------------------------------------------------------------------------------------------- |
| 1NF         | Each column contains atomic (single) values; no repeating groups or lists in a cell.                                         |
| 2NF         | Must be in 1NF + no non-prime attribute depends on a proper subset of any candidate key.                                    |
| 3NF         | Must be in 2NF + no transitive dependencies of non-key attributes on keys (in the usual simplified rule).                    |
| BCNF        | Must be in 3NF + every determinant is a superkey (for every non-trivial functional dependency X → Y, X must be a superkey).  |
| 4NF         | Must be in BCNF + no non-trivial multivalued dependencies unless the determinant is a superkey.                              |
| 5NF         | Must be in 4NF + no non-trivial join dependencies unless implied by candidate keys.                                          |
| 6NF         | No non-trivial join dependencies at all; temporal decompositions use the appropriate interval semantics.                      |
| DKNF        | Every constraint follows from domains and keys; this is a separate criterion, not the next numbered form.                     |

### Easy way to remember (1NF–BCNF)

- 1NF: One value per cell.
- 2NF: No partial dependencies.
- 3NF: No transitive dependencies (simplified).
- BCNF: Every determinant must be a superkey.

Remember: In the chain from 1NF through 6NF, with BCNF between 3NF and 4NF, each higher form satisfies the lower forms. These are increasingly strict conditions on the business dependencies, not a requirement to split every table at every step. A table that already satisfies a form needs no further decomposition for that form.

## Check your understanding

1. Which anomaly appears when Alice has different names on different order lines?
2. Why does an order's customer belong in `orders`, rather than every item row?
3. Why should purchase price remain on the order item?
4. What could go wrong if a decomposition loses the columns connecting its pieces?

Continue with [denormalization](https://github.com/djeada/Databases-Notes/blob/main/notes/02_database_design/03_denormalization.md) to learn when a measured read workload justifies deliberate duplication.
