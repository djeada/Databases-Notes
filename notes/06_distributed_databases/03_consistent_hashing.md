## Consistent Hashing
- Consistent hashing is a distributed hashing technique
- Provides even data distribution and minimal data movement during node addition/removal

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

Now, we would assign each data entry to the closest node in the clockwise direction:

- Data entry 1 would be stored on node A.
- Data entry 2 would be stored on node B.
- Data entry 3 would be stored on node C.
- Data entry 4 would be stored on node D.
    
## Concepts

- **Hash Ring**: A conceptual circular space wherein nodes and data items are placed.
- **Hash Function**: Function used to map data and nodes to their positions on the hash ring.
- **Virtual Nodes**: Multiple points on the hash ring that stand for a single physical node. Useful for improving distribution and handling node heterogeneity.

## Mechanism

### Data and Node Mapping

1. Determine node and data item positions on the hash ring by applying the hash function.

### Data Allocation

1. Each data item is assigned to the first node encountered in the clockwise direction on the hash ring.

### Node Changes

1. On adding a node, it takes over some data items from its neighboring nodes.
2. On removing a node, its data items are reassigned to the remaining neighboring nodes.

## Use Cases

- Applied in distributed caching systems like Memcached and Redis.
- Used in distributed databases such as Apache Cassandra and DynamoDB.
- Employed for load balancing across multiple servers.
- Utilized in distributed file systems.

## Advantages

- **Even Data Distribution**: Data is uniformly allocated across nodes, preventing hotspots.
- **Minimal Data Reassignment**: Data reassignment is kept minimal when nodes are added or removed, reducing system overhead.
- **Load Balancing**: Nodes have balanced load, contributing to better system performance.

## Best Practices

- Select an appropriate hash function that provides optimal distribution and minimal collisions.
- Implement virtual nodes for better data distribution and to handle heterogeneity among physical nodes.
- Regularly monitor and adjust the consistent hashing scheme to ensure sustained system performance as it evolves.
