# Requirements Analysis: Decide What the Database Must Remember

Before choosing tables, find out what the application must do. A requirement is a statement about a needed behavior or rule. “Use PostgreSQL” is a technology choice; “an order must retain the price originally charged” is a requirement that the design must support.

We will use a bookstore so that the requirements connect to the [data-modeling example](../01_introduction_to_databases/04_data_models.md).

## Begin with a real workflow

Ask the person operating the store to describe a purchase from start to finish:

1. A customer chooses products and quantities.
2. The application checks whether enough stock exists.
3. It records the order and its items.
4. It reduces the available stock.
5. Staff later find the order for packing or cancellation.

Each step raises questions. Does an unpaid order reserve stock? Can a customer cancel part of an order? What happens if a product's price changes during checkout? Write the answers down rather than letting each programmer make a different assumption.

A **stakeholder** is someone affected by the system: customers, store staff, accountants, support staff, or operators. They often need different views of the same records.

## Separate behaviors, rules, and service targets

| Kind of requirement | Bookstore example | What it influences |
| --- | --- | --- |
| Behavior | Show a customer's order history. | Which data and queries are needed. |
| Data rule | Every order belongs to an existing customer. | A required reference and foreign key. |
| Historical rule | Keep the price charged on each order line. | A purchase-price attribute rather than only a current price. |
| Performance target | Order history should meet an agreed latency target at expected traffic. | Workload testing and access paths. |
| Recovery target | Define acceptable data loss and time to restore service. | Backup, replication, and recovery procedures. |
| Access rule | A customer can see only their own orders. | Authentication and authorization checks. |

A performance target should be measurable, including traffic, data size, and which proportion of requests must meet it. “Fast” leaves the design impossible to evaluate.

## Identify facts and their owners

An **entity** is a kind of record, such as a customer or product. An **attribute** describes it. For each fact, ask which record it belongs to:

- A customer's email belongs to the customer.
- A product's current price belongs to the product.
- The quantity and price charged belong to an order item.
- The cancellation time belongs to the order or canceled line, depending on the workflow.

This prevents storing a fact in a convenient but misleading place. If an order has several products, a single `product_id` column on the order cannot represent the whole purchase.

## State the relationships and optional cases

“One customer can place many orders” is incomplete until you ask whether a customer can have zero orders and whether an order can have no customer.

For our initial model:

- A customer can exist without an order.
- An order requires one customer.
- An order can contain several items.
- Each item identifies one product and a positive quantity.

The requirement that a completed order has at least one item is not enforced merely by adding a foreign key to the item table. It needs appropriate workflow validation and transaction logic. Identify such rules explicitly.

## List the questions the database must answer

Write representative queries in ordinary language before SQL:

- Find customer 1's orders, newest first.
- List the items in order 101 with their quantities and purchase prices.
- Find products with fewer than five units in stock.
- Calculate completed sales by day, including the policy for returns.

These are **access patterns**: the reads and writes the application repeats. They guide index choices and help compare possible data models.

## Test the requirements with awkward examples

Try a duplicate customer name, a product with zero stock, a price change, a repeated checkout request, and two buyers requesting the last unit.

For each case, write the expected outcome. For a repeated request, should the application create another order or return the existing one? A stable request identifier can make the intended “once” behavior enforceable.

A sample record is not a business rule. Seeing that every product currently has one author does not prove that co-authored books are forbidden.

## What to produce before implementation

Produce a small entity-relationship diagram, a list of facts and rules, the important access patterns, and testable acceptance examples. Mark unresolved assumptions so they do not disappear into the schema.

Then convert the agreed model into tables and constraints. Revisit the requirements when workflows change; adding a table is not a substitute for deciding what the new behavior means.

## Make the requirements testable before choosing a product

“Fast,” “scalable,” and “secure” do not specify a design. Replace them with operations and conditions that can be observed. For example, an order-history page might return 20 orders at a time and have a measured latency target under an agreed concurrent load. A stock reservation might require that two requests cannot both claim the final copy. A daily report might allow yesterday's data rather than requiring every sale immediately.

Record the target, the representative data size and distribution, and how it will be measured. **Latency** is time per request; **throughput** is completed requests per unit time. An average can hide a slow tail, so record a percentile when that describes the requirement better. The illustrative targets here are decisions to agree with stakeholders, not universal database benchmarks.

Capacity planning should distinguish storage growth, query CPU, connection count, and write contention. Adding read replicas can help suitable reads, but does not automatically divide one primary's write workload. Choosing a shard key before understanding the queries can make ordinary cross-customer reports expensive. The requirements should explain which bottleneck the chosen architecture is meant to address.

## A second worked domain: university enrollment

A university example shows why a model must follow the rules rather than merely name tables. A registrar manages enrollment, lecturers need rosters, students need schedules, and administrators need historical reports. Those stakeholders can disagree about what should be retained, who can change it, and when it is considered final.

Start with these agreed rules:

| Statement from a stakeholder | Modeling consequence |
|---|---|
| A student may attend several courses | Student–course membership is many-to-many |
| A course may have many students | Introduce an enrollment relationship |
| A professor teaches several courses | Professor identifier is referenced by courses |
| An enrolled student may not yet have a grade | Grade is optional rather than replaced with zero |
| A student cannot enroll twice in the same course in this exercise | Pair of student and course identifiers must be unique |
| Old enrollments must survive a student name correction | Refer to stable identifiers rather than copy the current name |

This deliberately small model treats a course as one offered class. A real university normally separates the catalog course from an offering in a term, and can have several lecturers per offering. Discover that distinction before enforcing a rule such as “one professor per course.” Otherwise a convenient tutorial assumption becomes a production limitation.

### Create the proposed model and ask a stakeholder's question

Run this standalone SQLite example in a fresh database. The `uni_` prefix distinguishes these tables from the bookstore:

```sql
PRAGMA foreign_keys = ON;
CREATE TABLE uni_students (
    student_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE uni_professors (
    professor_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);
CREATE TABLE uni_courses (
    course_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    professor_id INTEGER NOT NULL REFERENCES uni_professors(professor_id)
);
CREATE TABLE uni_enrollments (
    student_id INTEGER NOT NULL REFERENCES uni_students(student_id),
    course_id INTEGER NOT NULL REFERENCES uni_courses(course_id),
    grade INTEGER CHECK (grade BETWEEN 0 AND 100),
    PRIMARY KEY (student_id, course_id)
);
INSERT INTO uni_students VALUES (1, 'Alice'), (2, 'Bob'), (3, 'Carol');
INSERT INTO uni_professors VALUES (10, 'Dr Lee'), (20, 'Dr Rao');
INSERT INTO uni_courses VALUES (101, 'Databases', 10), (102, 'Networks', 20);
INSERT INTO uni_enrollments VALUES (1, 101, 88), (2, 101, NULL), (1, 102, 91);

SELECT s.name, e.grade
FROM uni_enrollments AS e
JOIN uni_students AS s ON s.student_id = e.student_id
WHERE e.course_id = 101
ORDER BY s.student_id;
```

| name | grade |
|---|---|
| Alice | 88 |
| Bob | NULL |

The roster returns Bob despite his missing grade. Interpreting null as zero would incorrectly turn “not graded yet” into a failing result. The pair key prevents duplicate enrollment under the stated rule, while foreign keys prevent missing students and courses.

Ask the professor how they would use this roster. Do they need withdrawn students, a preferred name, or a section number? Each answer can change the required schema or filter. A working query is a way to validate a requirement, not proof that the entire domain has been understood.

### Validate a report that keeps courses with no students

```sql
SELECT c.title, COUNT(e.student_id) AS enrolled_students
FROM uni_courses AS c
LEFT JOIN uni_enrollments AS e ON e.course_id = c.course_id
GROUP BY c.course_id, c.title
ORDER BY c.course_id;
```

| title | enrolled_students |
|---|---|
| Databases | 2 |
| Networks | 1 |

A left join lets an empty course remain in the report. Counting the non-null enrollment identifier would give it zero; `COUNT(*)` would count its unmatched result row instead. That distinction should be established before a report is used for staffing or capacity decisions.

## Resolve priorities and disagreements explicitly

Separate required correctness from optional convenience. A useful initial scope might require a valid roster and duplicate-enrollment protection, while postponing automatic recommendations. Do not postpone a rule that prevents lost money or invalid records simply because it has no visible user-interface element.

Keep a decision log: the rule, its owner, the selected interpretation, and an example that demonstrates it. Walk through rejected cases as well as successful ones. If one stakeholder wants permanent history and another wants to remove a record, determine what must be deleted, anonymized, archived, or retained under the organization's policy. Do not make that choice silently in `ON DELETE CASCADE`.

## Security and integration produce schema requirements too

List operations by actor: lecturers might read rosters and enter grades for their classes; a registrar might manage enrollment; students might read their own results. Authentication establishes identity. Authorization determines which records and actions that identity may access. A shared application database account does not by itself implement those per-user rules.

Integrations need stable identifiers, ownership, and a conflict policy. If an identity system supplies a student identifier, decide whether it is also the database key and what happens to mergers or corrections. Define import validation, duplicate detection, failure reporting, and whether a partially loaded batch may be accepted. An API response or CSV column is an interface contract, not automatically the database's internal schema.

Deliver a conceptual diagram, a logical schema, representative data, a query list, an access matrix, capacity assumptions, and acceptance cases. Then test the assumptions with a small implementation before committing to storage and indexes. The university example's roster is one such acceptance case; the bookstore's stock reservation is another.

## Check your understanding

1. Why must a purchase price be recorded separately from a current product price?
2. What extra questions follow from “customers place orders”?
3. Why does “every item references an order” not ensure every order contains an item?
4. Write an expected outcome for two customers buying the last copy.

Continue with [normalization](02_normalization.md), which organizes these facts without unnecessary duplication.
