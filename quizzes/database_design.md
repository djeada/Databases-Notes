# Database Design Quiz

Notes: [Data Models](../notes/01_introduction_to_databases/04_data_models.md), [Requirements Analysis](../notes/02_database_design/01_requirements_analysis.md), [Normalization](../notes/02_database_design/02_normalization.md), [Denormalization](../notes/02_database_design/03_denormalization.md), [Data Integrity](../notes/02_database_design/05_data_integrity.md)

Check how well you can model facts, place them in the right tables and protect them with constraints.

#### Q. A single `order_lines` table repeats `customer_name` on every line. Renaming Alice on one order leaves two different names for customer 1. Which problem is this?

* [ ] Insertion anomaly
* [x] Update anomaly
* [ ] Deletion anomaly
* [ ] Phantom read

> **Explanation:** The same fact is stored in several rows, and an update reached only some of them, breaking `customer_id → customer_name`. Normalization stores the name once with its owner.

#### Q. An `orders` table stores `products = '10,20,30'` in one column. Which redesign follows first normal form?

* [ ] Store the list as a JSON array instead of text
* [x] Add an order-items table with one row per product line
* [ ] Add `product_1`, `product_2` and `product_3` columns
* [ ] Move the list into a separate `products_text` table

> **Explanation:** 1NF represents separate facts separately, so each product reference, with its quantity, gets its own row. Numbered columns still hard-code a repeating group.

#### Q. Does a `DATE` column violate first normal form because a date contains a year, month and day?

* [ ] Yes, it must be split into three columns
* [x] No, it is used as one value in the model
* [ ] Yes, unless it is stored as text
* [ ] No, because dates are exempt from normalization

> **Explanation:** "Atomic" means atomic for the chosen model, not impossible to subdivide. The 1NF concern is bundling several independently used facts into one value.

#### Q. What does the functional dependency `product_id → product_title` assert?

* [ ] Equal titles imply equal product IDs
* [x] Equal product IDs imply equal titles
* [ ] Product IDs are derived from the titles
* [ ] A product can have several titles

> **Explanation:** `X → Y` means knowing X determines Y. The reverse need not hold: several products can share a title.

#### Q. `order_items` has key `(order_id, line_number)` and also stores `customer_id`, which depends only on `order_id`. What is the lowest normal form this table fails?

* [ ] First normal form
* [x] Second normal form
* [ ] Fourth normal form
* [ ] Fifth normal form

> **Explanation:** A non-key fact depending on a proper subset of a candidate key is a partial dependency, which 2NF forbids. Move order-level facts into `orders`.

#### Q. `orders(order_id, customer_id, customer_name)` follows `order_id → customer_id → customer_name`. What does third normal form suggest?

* [ ] Add `customer_name` to the primary key
* [x] Move `customer_name` to a `customers` table
* [ ] Duplicate `customer_name` into `order_items`
* [ ] Replace `customer_id` with `customer_name`

> **Explanation:** The name depends on the order only through the customer, a transitive dependency. Storing it with the customer means a rename changes one row; a join reconstructs it for reports.

#### Q. A product's current price is 18.00, but an order line from last year stored 15.00. What should the design do?

* [ ] Drop the line price and join to the current price
* [x] Keep both, because they are different facts
* [ ] Update the old line to 18.00 for consistency
* [ ] Store only the price that is higher

> **Explanation:** The current catalog price and the price charged on a past sale describe different times. Replacing the line price with a join would destroy historical information, so it is not redundant duplication.

#### Q. `customer_id` alone uniquely identifies a customer row. What is `(customer_id, email)`?

* [ ] A candidate key
* [x] A non-minimal superkey
* [ ] A composite foreign key
* [ ] A partial dependency

> **Explanation:** It identifies rows, so it is a superkey, but it is not minimal: removing `email` still leaves an identifier. A candidate key is a minimal identifier.

#### Q. In `enrolment(student, subject, teacher)`, each teacher teaches exactly one subject, so `teacher → subject`, but a teacher has many students. What is the lowest normal form this relation fails?

* [ ] Second normal form (2NF)
* [ ] Third normal form (3NF)
* [x] Boyce–Codd normal form
* [ ] First normal form (1NF)

> **Explanation:** Every attribute belongs to a candidate key, so 3NF's prime-attribute exception is met. BCNF requires every determinant to be a superkey, and `teacher` is not.

#### Q. The enrolment relation is split into `(teacher, subject)` and `(student, teacher)`. What is the main cost of this BCNF decomposition?

* [ ] The join can invent false teacher–subject pairs
* [x] One-teacher-per-subject needs a cross-table rule
* [ ] Each student's name must now be stored twice
* [ ] The split loses each student's teacher assignment

> **Explanation:** The split is lossless, but the simple keys no longer stop Alice having two Databases teachers. This is why dependency preservation matters alongside losslessness.

#### Q. A customer's preferred languages and favourite categories are independent lists stored together as `(customer, language, category)`. Which design follows fourth normal form?

* [ ] Keep one table but make `category` nullable
* [x] Store languages and categories in two separate tables
* [ ] Concatenate languages into one column per customer
* [ ] Add a surrogate key to the combined table

> **Explanation:** Independent multivalued facts force a row for every language/category pairing. Separating them removes those repeated combinations. If the lists were not independent, the split would invent preferences.

#### Q. Approved triples are `(S1, P1, J1)`, `(S1, P2, J2)` and `(S2, P1, J2)`. If you store only the three pairwise projections and join them back, which unapproved triple appears?

* [ ] `(S2, P2, J1)`
* [x] `(S1, P1, J2)`
* [ ] `(S2, P1, J1)`
* [ ] `(S1, P2, J1)`

> **Explanation:** The pairs `(S1, P1)`, `(S1, J2)` and `(P1, J2)` all exist, so the join creates a spurious tuple. 5NF analysis checks whether a multiway relationship really decomposes.

#### Q. What makes a decomposition lossless?

* [ ] Every table keeps the original primary key
* [x] Rejoining yields exactly the original facts
* [ ] No column appears in more than one piece
* [ ] Every piece has the same number of rows

> **Explanation:** A lossless split loses no facts and adds no false combinations when rejoined. Splitting names and emails into tables with no reliable link would fail this test.

#### Q. A sample table shows every book with exactly one author. What can you conclude about the dependency `book_id → author_id`?

* [ ] It holds, because the sample has no counterexample
* [x] Nothing yet: dependencies come from business rules
* [ ] It holds only after you add a unique index
* [ ] It never holds for many-to-many data

> **Explanation:** A sample without contradictions does not prove a rule. Ask the business whether co-authored books are forbidden before designing around it.

#### Q. To speed up order pages, you add a stored `total_cents` column to `orders`. What new responsibility does this create?

* [ ] Every read must recompute the total to verify it
* [x] Every write to order lines must also update the total
* [ ] The `order_items` table can now be dropped
* [ ] The total must be indexed to be correct

> **Explanation:** A stored aggregate is a second representation of a calculation. Every path that changes line items must maintain it, or a drift-detection and rebuild process must exist.

#### Q. A denormalized summary is maintained by a periodic background job instead of in the writing transaction. What must readers accept?

* [ ] Writes to the source table are blocked during refresh
* [x] They may see values older than the source data
* [ ] The summary can never drift from the source
* [ ] The source table must become read-only

> **Explanation:** Background refresh trades freshness for cheaper writes. Record refresh progress and agree on how much staleness is acceptable.

#### Q. A report joining orders and lines is slow. What do the notes recommend before adding a denormalized copy?

* [ ] Convert the whole schema to a document store
* [x] Inspect the plan, indexes and rows actually read
* [ ] Duplicate the line columns into `orders`
* [ ] Add an application cache in front of every query

> **Explanation:** A suitable index or a smaller result can remove the bottleneck without duplicating data. Denormalization should be justified by measurement and documented with its authoritative source.

#### Q. With SQLite foreign keys enabled, what happens to staff rows when their department is deleted?

```sql
CREATE TABLE staff (
    staff_id INTEGER PRIMARY KEY,
    department_id INTEGER REFERENCES departments(department_id)
        ON DELETE SET NULL,
    name TEXT NOT NULL
);
```

* [ ] They are deleted along with the department
* [x] They stay, with `department_id` set to `NULL`
* [ ] The department delete is rejected with an error
* [ ] They keep the old ID, which now dangles

> **Explanation:** `SET NULL` retains the employee but removes the reference, which requires the column to be nullable. `CASCADE` would delete the staff rows; `RESTRICT` would reject the delete.

#### Q. Why might `ON DELETE CASCADE` from `customers` to `orders` be the wrong choice?

* [ ] Cascades are not supported on foreign keys
* [x] It could erase order history needed for accounting
* [ ] It makes every customer insert much slower
* [ ] It prevents any customer from ever being deleted

> **Explanation:** Cascade should be chosen because dependent rows are meant to disappear, not to silence a foreign-key error. Historical orders often need retention or anonymization instead.

#### Q. In SQLite, a child row's foreign key is declared `DEFERRABLE INITIALLY DEFERRED`. Inside one transaction you insert the child, then its parent, then commit. What happens?

* [ ] The child insert fails immediately
* [x] The commit succeeds because the reference is valid at commit
* [ ] The commit succeeds even if the parent is never inserted
* [ ] SQLite ignores the deferral and rejects the commit

> **Explanation:** Deferral moves the check to commit time. Without the parent insert, the commit itself would fail.

#### Q. A cinema has `UNIQUE (screening_id, seat_number)`. Which booking is rejected after `(100, 'A1')` is stored?

* [ ] `(101, 'A1')`
* [ ] `(100, 'A2')`
* [x] `(100, 'A1')`
* [ ] `(102, 'B7')`

> **Explanation:** The pair must be unique, not each column on its own. Seat A1 can be booked for other screenings.

#### Q. An application checks "is this seat free?" and then inserts a booking. Why does the notes' design still rely on a unique constraint?

* [ ] Constraints always run faster than any `SELECT`
* [x] Two clients can both pass the check before either inserts
* [ ] The check cannot read uncommitted rows of its own
* [ ] Unique constraints also lock the whole bookings table

> **Explanation:** A check followed by a write races with concurrent writers. The database rule is evaluated for every insert, so only one booking for the pair can succeed.

#### Q. Which kind of integrity does `CHECK (price_cents >= 0)` protect?

* [ ] Entity integrity
* [ ] Referential integrity
* [x] Domain integrity
* [ ] Business integrity

> **Explanation:** Domain integrity limits an attribute's allowed values. Entity integrity concerns unambiguous identifiers, referential integrity valid relationships, and business integrity larger multi-row invariants.

#### Q. In an ordinary (non-`STRICT`) SQLite table, what happens when you insert `'abc'` into an `INTEGER` column?

* [ ] It is rejected with a datatype mismatch
* [x] It is stored as text due to type affinity
* [ ] It is silently converted to the integer 0
* [ ] It is stored as `NULL` instead

> **Explanation:** Ordinary SQLite tables use type affinity rather than strict enforcement. A `STRICT` table (SQLite 3.37+) rejects the value; PostgreSQL also rejects it.

#### Q. In the conceptual, logical and physical design levels, which one does "index `orders.customer_id`" belong to?

* [ ] Conceptual
* [ ] Logical
* [x] Physical
* [ ] Requirements

> **Explanation:** An index is an access-path decision for a particular engine. "An order has a customer" is conceptual, and "store `customer_id` as a foreign key" is logical.

#### Q. A `customer_preferences` table uses `customer_id` as both its primary key and a foreign key to `customers`. What relationship does this implement?

* [ ] One-to-many
* [x] One-to-zero-or-one
* [ ] Many-to-many
* [ ] Exactly one-to-one

> **Explanation:** The primary key prevents a second preference row for a customer, and the foreign key requires the customer to exist. Nothing forces every customer to have a preference row.

#### Q. Orders can contain many products, and products appear in many orders. How is this represented relationally?

* [ ] A `product_ids` array column on `orders`
* [x] A junction table like `order_items`
* [ ] A foreign key from `products` to `orders`
* [ ] A self-join on the `orders` table

> **Explanation:** A junction table records each order–product association as its own row, here with quantity and purchase price. Its composite key `(order_id, line_number)` identifies each line.

#### Q. Which rule can a foreign key from `order_items` to `orders` not enforce on its own?

* [ ] Each item refers to an existing order
* [x] Every completed order has at least one item
* [ ] An item cannot point to a missing order ID
* [ ] Deleting an order affects its items

> **Explanation:** A foreign key checks that referenced rows exist. "At least one item" involves several rows and the checkout workflow, so it needs a deliberate implementation.

#### Q. Which performance requirement is testable enough to guide design?

* [ ] "Order history pages should always feel fast to customers."
* [x] "95% of order-history requests finish in 200 ms at 500 req/s."
* [ ] "The database should scale well as the business grows."
* [ ] "Queries should use indexes wherever that is possible."

> **Explanation:** A useful target names the latency, the proportion of requests and the expected traffic. "Fast" or "scales well" cannot be evaluated or tested.
