## Why it matters

One machine eventually runs out of disk, memory or write throughput, and it will eventually fail. **Replication** copies data for availability and read scaling; **partitioning (sharding)** splits data so each machine holds a part. Real systems use both.

## Key ideas

**Replication**

- **Single leader (primary–replica)**: all writes go to the leader, which streams changes to followers. Reads can go to followers but may be stale (replication lag). Failover promotes a follower; risk of lost writes and split brain.
- **Synchronous vs asynchronous**: sync waits for followers (durable, slower, blocked if a follower dies); async is fast but can lose the last writes on leader failure. Semi-sync: wait for one follower.
- **Multi-leader**: leaders in several regions accept writes; conflicts must be resolved (last-write-wins, merge, CRDTs).
- **Leaderless (Dynamo style)**: clients write to N replicas and wait for W acks, read from R. Repairs happen via read repair and anti-entropy.

**Read-after-write problems from lag** and their fixes: read your own writes from the leader for a short time, monotonic reads by pinning a user to one replica.

**Partitioning strategies**

| Strategy | Good | Bad |
|---|---|---|
| Range (by key ranges) | Range scans | Hot spots on sequential keys (timestamps) |
| Hash of key | Even spread | No range queries across shards |
| Directory / lookup service | Flexible moves | Extra lookup, another component |
| Geographic / tenant | Data locality, compliance | Uneven sizes |

**Consistent hashing** places nodes and keys on a ring; each key belongs to the next node clockwise. Adding or removing a node moves only ~1/N of the keys instead of nearly all of them with `hash(key) % N`. **Virtual nodes** (many points per server) even out the load and let bigger machines take more.

**Choosing a shard key**

- High cardinality and even access, so no shard gets all the traffic.
- Matches the main query, so most requests touch one shard (`user_id` for user data, `chat_id` for messages).
- Celebrity / hot partitions need special handling: split the key, add a random suffix, or cache.

**Rebalancing**: fixed number of many small partitions moved between nodes (Elasticsearch, Kafka, Redis Cluster), or splitting partitions when they grow (Bigtable, HBase).

## Trade-offs to talk through

- Cross-shard queries and transactions are slow and complex: scatter-gather reads, two-phase commit or sagas for writes.
- Async replication trades durability on failover for write latency.
- More replicas mean better availability and read capacity, and more write cost and storage.

## Use it in an interview

- State the shard key and why. Mention the hot-key risk and your mitigation.
- Say whether replication is sync or async and what happens on leader failure.

## Check yourself

1. You add a fifth server to a cluster using `hash(key) % 4`. Roughly what fraction of keys move? And with consistent hashing?
2. Why is a timestamp a poor range-partition key for a write-heavy log?
3. A user updates their profile and the next page load shows the old one. Why, and how do you fix it?
