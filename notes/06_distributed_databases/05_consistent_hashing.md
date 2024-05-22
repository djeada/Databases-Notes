## Consistent Hashing
- Consistent hashing is a distributed hashing technique.
- It provides even data distribution and minimal data movement during node addition/removal.

Consider a circle (or 'ring') representing the hash space, where data entries and nodes are mapped.

```
                    0/360
                     |
                     |
         270 --------+-------- 90
                     |
                     |
                    180
```

Let's assume we have 4 data entries (1, 2, 3, and 4) which will also be mapped onto the circle:

```
                    0/360 -- A
                     |
               1 --  |  -- 2
     D - 270 --------+-------- 90 - B
                     |
             4 --    |    -- 3
                  C --180
```

Each data entry is assigned to the closest node in the clockwise direction:

- **Data entry 1** is stored on **node A**.
- **Data entry 2** is stored on **node B**.
- **Data entry 3** is stored on **node C**.
- **Data entry 4** is stored on **node D**.

This way, consistent hashing distributes the data evenly and ensures that only a small number of data entries need to be remapped when a node is added or removed.
    
## Concepts

- **Hash Ring**: A conceptual circular space where both nodes and data items are placed. This ring structure allows for efficient distribution and lookup of data.
- **Hash Function**: A function that maps data items and nodes to specific positions on the hash ring. The hash function ensures that the placement is both deterministic and uniform.
- **Virtual Nodes**: Multiple positions on the hash ring that represent a single physical node. Virtual nodes help improve data distribution and handle the heterogeneity of node capacities by allowing nodes to take on multiple roles.

## Mechanism

1. Nodes and data items are assigned positions on the hash ring using the hash function. This ensures that both are distributed uniformly across the ring.
2. Each data item is allocated to the first node it encounters in the clockwise direction on the hash ring. This method ensures even distribution and efficient lookup.
3. When a new node is added, it takes over some of the data items from its neighboring nodes, ensuring a balanced load.
4. When a node is removed, its data items are redistributed to the remaining neighboring nodes, maintaining data availability and balance.

## Use Cases

- Used in systems like Memcached and Redis to ensure that cache data is evenly distributed and quickly retrievable.
- Employed to distribute requests evenly across multiple servers, preventing any single server from becoming a bottleneck.
- Applied in databases such as Apache Cassandra and DynamoDB to manage data distribution and replication efficiently.
- Used to spread file storage across multiple nodes, ensuring redundancy and quick access.

## Advantages

- Ensures that data is evenly distributed across all nodes, preventing any single node from becoming a hotspot.
- When nodes are added or removed, only a small portion of data needs to be moved, reducing the overhead on the system.
- Each node carries a fair share of the load, leading to improved overall system performance and reliability.

## Best Practices

- Select an appropriate hash function that provides optimal distribution and minimal collisions.
- Implement virtual nodes for better data distribution and to handle heterogeneity among physical nodes.
- Regularly monitor and adjust the consistent hashing scheme to ensure sustained system performance as it evolves.
