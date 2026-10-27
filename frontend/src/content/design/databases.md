## Why it matters

The database is usually the hardest part to scale and the slowest to change later. Interviewers want to hear you choose storage from the **access patterns**, not from habit.

## Key ideas

**Families of databases**

| Type | Examples | Strong at |
|---|---|---|
| Relational (SQL) | PostgreSQL, MySQL | Transactions, joins, constraints, flexible queries |
| Key-value | DynamoDB, Redis, RocksDB | Lookups by key at huge scale |
| Wide-column | Cassandra, HBase, Bigtable | Very high write rates, time-ordered data per partition |
| Document | MongoDB, Couchbase | Nested, evolving JSON-like records |
| Graph | Neo4j | Multi-hop relationship queries |
| Time-series | Prometheus, InfluxDB, TimescaleDB | Metrics, compression, time-range queries |
| Search | Elasticsearch, OpenSearch | Full-text search, faceting |
| Analytical (OLAP) | ClickHouse, Druid, BigQuery, Snowflake | Aggregations over billions of rows |

**Start with relational** unless you have a reason not to: scale beyond one primary, a simple key-based access pattern at huge volume, or a data shape that doesn't fit tables.

**Indexes** speed up reads and slow down writes.

- **B-tree** (most SQL databases): good for reads and range queries, updates in place.
- **LSM tree** (Cassandra, RocksDB): writes go to an in-memory memtable and a write-ahead log, then flush to sorted SSTable files that are compacted in the background. Very fast writes; reads may check several files (Bloom filters help).
- Composite indexes follow the leftmost-prefix rule; a covering index answers a query without touching the table.

**Transactions and isolation**

- ACID: atomic, consistent, isolated, durable.
- Isolation levels: read committed → repeatable read / snapshot → serializable. Know one anomaly each prevents (dirty read, non-repeatable read, lost update, write skew).
- Avoid lost updates with `SELECT … FOR UPDATE`, atomic updates (`SET stock = stock - 1 WHERE stock > 0`) or optimistic concurrency (a `version` column checked on update).

**Data modelling for NoSQL**: design the table for the query. In Cassandra/DynamoDB pick a **partition key** that spreads load evenly and a **sort/clustering key** that orders rows within it, for example `(chat_id) → message_id`.

**Normalisation vs denormalisation**: normalise for correctness, denormalise (duplicate data) to avoid expensive joins on hot read paths, accepting extra work on writes.

**IDs**: auto-increment needs a single writer; UUIDs are random (bad index locality); **Snowflake-style IDs** (timestamp + machine id + sequence) are unique, roughly time-sortable and generated without coordination.

## Trade-offs to talk through

- SQL gives you joins and transactions but sharding it is manual work; NoSQL scales horizontally but pushes consistency and joins into the application.
- Every secondary index is another write and more storage.

## Use it in an interview

- Name the main tables or collections with their primary key and the 2–3 queries they serve.
- Justify the choice in one sentence tied to a requirement.

## Check yourself

1. Why do LSM-tree stores handle write-heavy workloads better than B-trees?
2. Two users buy the last item at the same time. Show two different ways to stop overselling.
3. Design the Cassandra table for "the latest 50 messages of a chat".
