# Consistent Hashing

Imagine you're organizing books in a vast library with shelves arranged in a circle. Each book’s position is chosen by the first letter of its title, looping back to the beginning after **Z**. When you install a new shelf or remove one, you’d prefer not to reshuffle every book—only a small, predictable subset should move. **Consistent hashing** gives distributed computer systems that same flexibility: data can be spread across servers, yet when servers come or go only a fraction of keys are remapped.

## The Hash Ring Concept

Consistent hashing imagines the entire hash space as a circle.
For illustration, consider a 32-bit hash (0 → $2^{32} - 1$); after the last value the count “wraps” back to 0, so the ends meet like the edges of a clock dial.

* The ring abstraction lets us reason in angles, but it really represents a modulo - $2^{32}$ number line.
* **Data movement is proportional to the arc length** affected—so scaling out (or shrinking) causes only *$O(k / n)$* re-shuffles instead of moving everything.
* The same mechanism underpins virtual nodes (VNodes): each physical server advertises many points on the circle, smoothing load without changing the fundamental rules.

### Hash-ring overview

```
Hash Ring:
                         0°   (hash 0; maximum wraps to 0)
                         ●
                         │
                         │
   270° (¾·2³²)     ●────┼────●  90° (¼·2³²)
                         │
                         │
                         ●
                       180° (½·2³²)
```

* Every point on the circumference corresponds to a possible hash value.
* Moving clockwise always increases the hash (mod $2^{32}$) and eventually loops back to 0 (0°).
* A node owns the arc from the preceding node (exclusive) to its own position (inclusive). A key maps to the first node clockwise at or after its hash.

## Mapping Nodes and Data onto the Ring

Assume three servers —**Node A**, **Node B** and **Node C**.

### Placing nodes

![ring\_nodes](https://github.com/user-attachments/assets/41d53327-71e1-4014-9a5c-531ee7a5548a)

| Node   | Hash angle | Covers hash interval\* |
| ------ | ---------- | ---------------------- |
| Node A | 0°         | (240° → 0°]            |
| Node B | 120°       | (0° → 120°]            |
| Node C | 240°       | (120° → 240°]          |

Interval is *open* at the start and *closed* at the end, so each key maps to exactly one node.

### Placing data keys

| Key | Hash angle | Stored on…                    |
| --- | ---------- | ----------------------------- |
| K1  | 100°       | Node B                        |
| K2  | 200°       | Node C                        |
| K3  | 330°       | Node A (0°) – wraps past 360° |

![ring\_nodes\_data](https://github.com/user-attachments/assets/313d5a15-1e6d-4a01-a869-ad77e40931a6)

- Rule of thumb → “First node clockwise.”
- Each key walks clockwise until it hits a node marker; that node stores the key.

## Adding and Removing Nodes

A major advantage of consistent hashing is that **only the keys that lie in the affected arc move** when the node set changes.

### Adding **Node D** at 80°

![ring\_add\_node\_d](https://github.com/user-attachments/assets/f8800739-a2d1-496b-90b9-318c9d530c4e)

* Node D splits Node B’s old interval. Only keys in the slice (0° → 80°] are affected.
* None of K1 (100°), K2 (200°), or K3 (330°) lies in (0° → 80°], so all three keep their assignments. A key at 50° would move from Node B to Node D.

### Removing **Node B**

![ring\_remove\_node\_b](https://github.com/user-attachments/assets/8b2319cd-e67a-49c9-8d2a-96e9e630ac5c)

* When a node departs, its entire arc is reassigned to the next clockwise node. Here Node C inherits Node B’s range.
* Removing B from either ring moves K1 (100°) to C; the other example keys remain assigned as before.

## Practical Example: Distributed Caching with Consistent Hashing

Consider a web application using a distributed cache to store session data. Let's see how consistent hashing helps in this scenario.

### Without Consistent Hashing

- Servers are selected using a simple modulo operation: `server = hash(key) % number_of_servers`.
- Adding or removing a server changes `number_of_servers`, causing most keys to remap to different servers.
- This results in cache misses and increased load on the database.

### With Consistent Hashing

- Servers and keys are placed on the hash ring.
- Only keys that would map to the affected servers need to be remapped.
- The majority of keys continue to map to the same servers, preserving cache hits.

## Virtual Nodes (VNodes)

To enhance data distribution and fault tolerance, consistent hashing often uses virtual nodes.

### What Are Virtual Nodes?

- Each physical node is represented multiple times on the hash ring at different positions.
- For example, Node A might be placed at positions 5°, 120°, and 250°.

### Benefits of Virtual Nodes

- **Improved load balancing** is achieved as increasing the number of points on the hash ring leads to a more even distribution of data among nodes.
- **Easier scaling** is possible because adding or removing a physical node only requires redistributing its associated virtual nodes, minimizing disruption.
- Supporting heterogeneous nodes allows nodes with greater capacity to have more virtual nodes, enabling them to handle a proportionally larger share of data and requests.

## Implement a deterministic lookup

A practical ring needs a stable hash function, a stable key encoding, virtual-node membership, and an efficient successor lookup. This runnable Python example uses SHA-1 **only for placement**, not to authenticate data, and binary search to avoid walking all 300 virtual nodes for every key.

```python
from bisect import bisect_left
from hashlib import sha1

def position(value: str) -> int:
    return int.from_bytes(sha1(value.encode("utf-8")).digest(), "big")

def build_ring(nodes: list[str], replicas: int = 100):
    if not nodes or replicas < 1 or len(nodes) != len(set(nodes)):
        raise ValueError("provide distinct nodes and at least one virtual node")
    entries = sorted(
        (position(f"{node}:{i}"), node)
        for node in nodes for i in range(replicas)
    )
    positions = [hash_value for hash_value, _ in entries]
    return entries, positions

def owner(key: str, entries, positions) -> str:
    index = bisect_left(positions, position(key)) % len(entries)
    return entries[index][1]

ring, positions = build_ring(["NodeA", "NodeB", "NodeC"])
print(owner("my_data_key", ring, positions))
```

Building the ring sorts `N × replicas` virtual nodes; lookup uses binary search over the sorted positions. The output is deterministic for a given membership list, hash, and encoding, but the assigned node is not important to memorize. Real implementations must also resolve the astronomically unlikely hash collision and coordinate **membership changes**: different clients using different ring versions can disagree about ownership. The ring does not provide replication or durable rebalancing by itself.

## Real‑World Uses & Challenges

| System                         | Why uses consistent hashing                                       | Notable wrinkles                                          |
| ------------------------------ | ----------------------------------------------------------------- | --------------------------------------------------------- |
| **Amazon Dynamo**   | On‑line shopping carts must survive node loss during Black Friday | Requires anti‑entropy sync to handle “sloppy” quorums     |
| **Apache Cassandra**           | Ring topology underpins token ranges for partitions               | Hot partitions can appear if token assignment is careless |
| **Memcached client libraries** | Keeps cache‑hit rate high during live scaling                     | Need client‑side agreement on hash function               |
| **CDNs (e.g., Akamai)**        | Predictable client → edge‑server mapping                          | Must integrate geo‑routing and health‑checks              |

Implementation challenges include choosing a non‑biased hash function, deciding how many VNodes per server, and coordinating ring state changes across clients.

## What consistent hashing solves—and what it does not

| Mechanism | Benefit | Remaining responsibility |
|---|---|---|
| Ring lookup | Deterministic mapping from key to a current owner | Agree on hash encoding and membership version |
| Virtual nodes | Better expected balance and smoother movement when capacity changes | One exceptionally hot key can still dominate its owner |
| Adding or removing nodes | Only a fraction of keys normally change primary ownership | Move or re-fetch data without losing writes during transition |
| Replication around the ring | Can place copies on distinct owners when deliberately implemented | Failure domains, quorum rules, repair, and anti-entropy are separate designs |

Monitor actual key skew, traffic, and migration progress; the number of virtual nodes is a capacity/metadata trade-off, not a universal constant. Unlike consistent hashing, naïve modulo hashing such as `hash(key) % number_of_nodes` commonly remaps most keys when the modulus changes.

## Review questions

1. What is consistent hashing, and how does it differ from traditional hashing?
2. How does the hash‑ring abstraction work, and how are nodes and data mapped onto it?
3. Why does adding or removing a node trigger only limited data movement?
4. How do virtual nodes (VNodes) improve load‑balancing and scalability?
5. Where is consistent hashing used in the real world, and what pitfalls can appear in practice?
