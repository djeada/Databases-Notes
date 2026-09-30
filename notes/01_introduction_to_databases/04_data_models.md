# Data Models: Turn a Business Description into a Structure

A **data model** describes what facts exist, how they relate, and which rules apply. Before writing SQL, make the model explicit. Otherwise, decisions such as whether an order can contain several books become accidental consequences of a table layout.

We will use the same bookstore as the introductory notes. The business says: “a customer places an order containing one or more products.”

## Name the things you need to remember

An **entity** is a kind of thing the system tracks. An **attribute** is a fact about it.

| Entity | Example | Attributes |
| --- | --- | --- |
| Customer | Alice | Customer ID, name, email |
| Product | A particular book edition | Product ID, title, current price |
| Order | Purchase 101 | Order ID, customer, order date |

Do not confuse an entity type with one instance. `Customer` describes the kind of record; Alice is one customer instance.

## Describe relationships in both directions

Ask both questions: how many orders can a customer place, and how many customers can place one order?

- One customer can place many orders.
- Each order belongs to one customer in this model.

That is **one-to-many**. The number of records permitted on each side is called the relationship's **cardinality**.

Now compare orders and products:

- One order can contain many products.
- One product can appear in many orders.

That is **many-to-many**. Quantity and the price charged are facts about a product *in a particular order*, rather than facts about the customer or the product alone.

Whether a relationship is required also matters. A customer might exist before placing an order, while an order must have a customer in this design.

## Add the missing relationship entity

Introduce an **order item**: one line in an order describing a product purchase.

```text
Customer 1 ---- many Order
Order    1 ---- many OrderItem
Product  1 ---- many OrderItem
```

The line records `quantity` and `unit_price_at_purchase`. Recording the purchase price matters because changing a product's current price should not change what an earlier order charged.

## Move from a conceptual to a logical model

A **conceptual model** explains the business without committing to SQL types. “Customers place orders” belongs here. An entity-relationship (ER) diagram draws these entities and relationships.

A **logical relational model** chooses tables, identifiers, and references:

```text
customers(customer_id, name, email)
products(product_id, title, current_price)
orders(order_id, customer_id, order_date)
order_items(order_id, line_number, product_id, quantity, unit_price_at_purchase)
```

The primary key of `order_items` is `(order_id, line_number)`: the pair identifies a line. Line number 1 can exist in several different orders. The full pair cannot repeat.

Foreign keys connect `orders.customer_id` to a customer, and each order item to its order and product. In SQL, these declarations enforce that the referenced records exist; they do not automatically fetch related records for a query.

## Inspect actual rows

| order_id | line_number | product_id | quantity | unit_price_at_purchase |
| --- | --- | --- | --- | --- |
| 101 | 1 | 10 | 2 | 15.00 |
| 101 | 2 | 20 | 1 | 25.00 |
| 102 | 1 | 10 | 1 | 15.00 |

Order 101 contains two lines and three units in total. Its amount is `2 × 15.00 + 1 × 25.00 = 55.00`. Product 10 occurs in both orders, without copying its title into every line.

Ask whether the model permits repeated products in separate lines, returns, discounts, and tax. The answers may require extra attributes or entities. A diagram is a proposal that must be checked against real workflows.

## Choose the physical design later

A **physical model** chooses engine-specific types, indexes, partitioning, and storage options. For example, an index on `orders.customer_id` may help order-history queries.

This is a different decision from “an order belongs to a customer.” Keeping the distinction allows you to improve storage access without changing the business meaning of an order.

## Other ways to represent the same domain

Tables are one logical representation. A document model might embed order lines inside an order document. A graph model might represent customers and products as nodes connected by purchase relationships.

A tree is a good model for a single-parent category hierarchy, but a product belonging to several categories does not naturally fit one strict parent path. The historical network database model used navigable record relationships; it is not simply another name for a modern graph database.

The [database-types note](02_types_of_databases.md) compares these approaches. The business rules still need to be explained whichever representation you choose.

## Check your understanding

1. Why does the bookstore need an order-items entity?
2. Why is purchase price different from current product price?
3. Can `(101, 1)` and `(102, 1)` both be valid order-item keys?
4. Which decision is conceptual, which is logical, and which is physical: an order needs a customer, the customer ID is a foreign key, and an index supports customer lookup?

Continue with [requirements analysis](../02_database_design/01_requirements_analysis.md) to discover these rules before committing to a schema. Use the [glossary](05_glossary.md) when a term is unfamiliar.
