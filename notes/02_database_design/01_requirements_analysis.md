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

## Check your understanding

1. Why must a purchase price be recorded separately from a current product price?
2. What extra questions follow from “customers place orders”?
3. Why does “every item references an order” not ensure every order contains an item?
4. Write an expected outcome for two customers buying the last copy.

Continue with [normalization](02_normalization.md), which organizes these facts without unnecessary duplication.
