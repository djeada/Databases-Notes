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

## Check your understanding

1. Which anomaly appears when Alice has different names on different order lines?
2. Why does an order's customer belong in `orders`, rather than every item row?
3. Why should purchase price remain on the order item?
4. What could go wrong if a decomposition loses the columns connecting its pieces?

Continue with [denormalization](03_denormalization.md) to learn when a measured read workload justifies deliberate duplication.
