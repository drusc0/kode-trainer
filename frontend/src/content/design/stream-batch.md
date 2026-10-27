## Why it matters

Analytics, counters, recommendations, search indexes and billing all turn raw events into aggregates. You process them either in **batches** over stored data (high throughput, hours of delay) or as a **stream** (seconds of delay, trickier correctness). Ad clicks, metrics and autocomplete questions hinge on this.

## Key ideas

**Batch processing** (MapReduce, Spark, warehouse SQL): read a big immutable dataset (files in S3/HDFS, Parquet), compute, write results. Easy to rerun when there's a bug, since the input doesn't change. Good for daily reports, model training and rebuilding indexes.

**Stream processing** (Flink, Kafka Streams, Spark Structured Streaming): continuously consume events from a log, keep state (counts, joins) in local stores that are checkpointed, and emit results.

**Time in streams**

- **Event time** (when it happened) vs **processing time** (when you saw it). Billing and analytics need event time.
- **Windows**: tumbling (fixed, non-overlapping: clicks per minute), sliding (last 5 minutes every minute), session (activity separated by gaps).
- **Watermarks** say "I've probably seen all events up to time T", so a window can close. Events later than the watermark are dropped, sent to a side output, or used to update an already-emitted result.

**Exactly-once in streams**: Flink takes consistent snapshots (checkpoints) of operator state and input offsets; on failure it rewinds both. Output stays correct if the sink is transactional or the writes are idempotent (upsert by window key).

**Architectures**

- **Lambda**: a fast stream path for fresh approximate results plus a batch path that recomputes exact results later. Two codebases.
- **Kappa**: stream only; to fix a bug, replay the log through a new version of the job.

**Approximate algorithms** when exact is too expensive:

- **HyperLogLog**: count distinct users in ~12 KB with ~1% error.
- **Count-Min Sketch**: approximate frequency counts for heavy hitters / top-k.
- **Bloom filter**: "definitely not seen" or "probably seen", for dedup.

**Serving the results**: write aggregates to an OLAP store (ClickHouse, Druid, Pinot) or a key-value store keyed by `(entity, time bucket)` for fast dashboard queries. Pre-aggregate into rollups (minute → hour → day).

## Trade-offs to talk through

- Freshness vs cost and correctness: streaming is harder to operate and reason about.
- Hot keys in streaming (one viral ad) overload a single task: pre-aggregate locally, or salt the key and merge.
- Keeping raw events in cheap object storage lets you recompute anything later.

## Use it in an interview

- Draw the pipeline: producers → Kafka → stream job → OLAP/KV store → query API, with a raw-event sink to object storage.
- Say the window, the time semantics, how late data is handled and how duplicates are removed.

## Check yourself

1. Why do billing pipelines aggregate by event time rather than processing time?
2. Your stream job crashes mid-window. How does it avoid double counting after restart?
3. How would you count unique daily visitors across 1B events cheaply?
