## Why it matters

Numbers tell you which problems are real. 100 writes per second fit on a laptop; 1 million need sharding. A quick estimate at the start keeps you from over-building a small system or under-building a big one.

## Key ideas

**Requests per second.** A day has ~86,400 seconds; round to **100k** (10⁵).

- 1M per day ≈ 12 per second
- 100M per day ≈ 1,200 per second
- 1B per day ≈ 12,000 per second
- Peak is usually **2–10×** the average.

**Storage.** records per day × size × retention × replication factor (usually 3).

**Bandwidth.** requests per second × payload size.

**Servers.** One modern app server handles roughly 1k–10k simple requests per second; a single relational primary roughly 5k–20k simple writes per second; a Redis node ~100k+ operations per second.

## Numbers worth knowing

| Operation | Time |
|---|---|
| L1 cache / main memory reference | 1 ns / 100 ns |
| Read 1 MB sequentially from memory | ~3 µs |
| Read 1 MB sequentially from SSD | ~50 µs |
| Random SSD read | ~100 µs |
| Round trip inside a data centre | ~0.5 ms |
| Disk seek (spinning) | ~10 ms |
| Round trip US ↔ Europe | ~80–150 ms |

| Unit | Bytes |
|---|---|
| Thousand / million / billion / trillion | KB / MB / GB / TB |
| A UUID or SHA-256 hex | 16 B binary / 64 B hex |
| A short text row (tweet + metadata) | ~1 KB |
| A photo / a minute of HD video | ~200 KB–2 MB / ~50–100 MB |

Powers of two: 2¹⁰ ≈ 1 thousand, 2²⁰ ≈ 1 million, 2³⁰ ≈ 1 billion, 2³² ≈ 4 billion.

Availability: 99.9% ≈ 8.8 hours down per year; 99.99% ≈ 53 minutes; 99.999% ≈ 5 minutes.

## Worked example

A URL shortener with 100M new links per month and 100 reads per write:

```text
writes: 100M / 30 days / 100k s  ≈ 40 per second
reads:  40 × 100                 ≈ 4,000 per second (peak ~20k)
storage: 100M × 12 months × 5 years × 500 B ≈ 3 TB
```

Conclusion: writes are trivial, reads dominate, the data fits on a few machines. Caching matters more than write sharding.

## Use it in an interview

- State assumptions before computing ("I'll assume 10% of users are daily active").
- Round to one significant figure. Precision doesn't matter; the order of magnitude does.
- Always say what the number **means** for the design.

## Check yourself

1. 500M daily users each load the feed 10 times a day. What's the average and the peak read QPS?
2. You store 1 KB per event at 10k events per second for a year with 3× replication. How much disk?
3. How many 4,000-QPS servers do you need for 50k peak QPS with headroom for one data centre failing?
