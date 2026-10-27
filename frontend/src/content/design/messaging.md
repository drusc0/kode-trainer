## Why it matters

Queues and logs decouple services in time: the producer doesn't wait for the consumer, bursts are absorbed, slow work happens in the background and one failing consumer doesn't break the producer. Almost every large design has at least one.

## Key ideas

**Message queue vs log**

| | Queue (SQS, RabbitMQ) | Log (Kafka, Kinesis, Pulsar) |
|---|---|---|
| After consumption | Message is deleted | Message stays until retention expires |
| Consumers | Compete for messages | Each consumer group reads independently, can replay |
| Ordering | Usually best effort (FIFO queues exist) | Strict order within a partition |
| Best for | Task distribution, jobs | Event streams, fan-out to many systems, reprocessing |

**Kafka in one paragraph**: a topic is split into **partitions**, each an append-only log on disk replicated to several brokers (one leader, followers in the in-sync replica set). Producers choose the partition by key hash, so all events for one key stay in order. A **consumer group** splits partitions among its members; each partition is read by one member, which commits its **offset**. Parallelism is capped by the partition count. Throughput comes from sequential disk IO, batching and zero-copy reads.

**Delivery semantics**

- **At most once**: commit before processing. May lose messages.
- **At least once**: process, then commit. May duplicate. The usual choice, combined with idempotent consumers.
- **Exactly once**: idempotent producers + transactions inside Kafka, or at-least-once plus deduplication in the sink.

**Patterns**

- **Work queue**: many workers pull jobs (transcoding, emails).
- **Pub/sub fan-out**: one event, many independent subscribers (search indexer, analytics, notifications).
- **Event sourcing**: the log of events is the source of truth; state is derived by replaying it.
- **Change data capture (CDC)**: stream DB changes (Debezium) to caches, search indexes and warehouses.
- **Delay / scheduled delivery**: delay queues, or a scheduler polling a time-indexed table.

**Handling failure**

- Retries with **exponential backoff and jitter**, a max attempt count, then a **dead-letter queue (DLQ)** for poison messages, with alerts.
- **Visibility timeout** (SQS): a message reappears if the worker dies before deleting it.
- **Back-pressure**: when consumers fall behind, lag grows. Monitor consumer lag, autoscale consumers, shed or degrade low-priority work.

## Trade-offs to talk through

- Async processing makes the user-facing path fast but the result eventually consistent; the UI must cope ("processing…").
- Ordering only holds per partition. A global order means one partition, which means one consumer.
- More partitions mean more parallelism, and more open files, slower leader elections and costlier rebalancing.

## Use it in an interview

- Add a queue wherever work is slow, bursty, retried or consumed by several systems.
- Say the partition key and why ordering matters (or doesn't) for that key.
- Say the delivery semantics and how consumers stay idempotent.

## Check yourself

1. You need all events for a given order processed in order, but high throughput overall. How do you partition?
2. A consumer crashes after writing to the DB but before committing its offset. What happens, and how do you make it safe?
3. When is a simple SQS queue a better choice than Kafka?
