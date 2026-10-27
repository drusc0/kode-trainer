## Why it matters

As soon as data lives on more than one machine, machines disagree for a while. Interviewers probe whether you know which guarantee your feature actually needs, and what it costs. "Can a seat be sold twice?" and "can a like count be off by one for a second?" have very different answers.

## Key ideas

**CAP**: when a network **p**artition happens, a system must choose between **c**onsistency (refuse or block some requests) and **a**vailability (answer, possibly with stale data). **PACELC** adds: **e**lse, when there's no partition, you trade **l**atency against **c**onsistency.

**Consistency models**, strongest to weakest:

- **Linearizable**: behaves like a single copy; every read sees the latest write. Needed for locks, leader election, unique usernames, inventory.
- **Sequential / causal**: everyone sees causally related events in order (a reply after the message it answers).
- **Read-your-writes, monotonic reads**: per-user guarantees that fix most "my change disappeared" bugs cheaply.
- **Eventual**: replicas converge if writes stop. Fine for feeds, counts, recommendations.

**Quorums**: with N replicas, write to W and read from R. If **R + W > N** the read and write sets overlap, so a read sees the latest acknowledged write (with caveats around failures). N=3, W=2, R=2 is common.

**Consensus** (Raft, Paxos, ZAB): a majority of nodes agrees on an ordered log, surviving minority failures. Used by etcd, ZooKeeper, Consul, Kafka KRaft and Spanner for leader election, configuration and metadata. Writes cost a majority round trip; a 5-node group survives 2 failures.

**Distributed locks and leases**: a lock with a TTL (Redis `SET key value NX PX 30000`, ZooKeeper ephemeral nodes). A paused process can still believe it holds an expired lock, so protect the resource with a **fencing token** (a number that increases with each lock grant, checked by the storage).

**Distributed transactions**

- **Two-phase commit (2PC)**: coordinator asks all to prepare, then commit. Atomic, but blocks if the coordinator dies.
- **Sagas**: a sequence of local transactions, each with a compensating action (refund, release seat). Orchestrated by a coordinator or choreographed through events.
- **Transactional outbox**: write the business row and an event row in the **same** local transaction; a relay publishes the outbox to the message broker. Avoids the "DB committed but the event was lost" dual-write bug.

**Idempotency**: an operation that gives the same result when repeated. Retries are inevitable, so writes that move money or send messages carry an idempotency key, stored with the result and checked before doing the work again.

**Clocks and ordering**: wall clocks drift, so don't order events across machines by timestamp alone. Use a single sequencer per partition, Lamport clocks (total order) or vector clocks (detect concurrent updates). Spanner uses TrueTime with bounded uncertainty.

**Concurrent edits to the same data**: last-write-wins loses data; **CRDTs** (counters, sets, sequences) merge automatically; **operational transformation** rewrites concurrent operations against each other via a central server (Google Docs).

## Trade-offs to talk through

- Strong consistency costs latency and availability, especially across regions. Use it only where a violation would be a real bug (money, inventory, uniqueness) and use weaker models elsewhere.
- Exactly-once delivery doesn't exist across a network; **exactly-once effects** come from at-least-once delivery plus idempotent processing.

## Use it in an interview

- For each data type, say the consistency it needs and why.
- When you add a retry, add an idempotency key in the same breath.

## Check yourself

1. N = 5. Which values of R and W give overlapping quorums, and what does W = 5 cost you?
2. Why does a distributed lock with a TTL need a fencing token?
3. An order service writes to its DB and then publishes `OrderCreated` to Kafka. What can go wrong, and how does an outbox fix it?
