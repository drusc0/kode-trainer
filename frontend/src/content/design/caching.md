## Why it matters

Caching is the cheapest way to make a read-heavy system fast. Memory is ~1,000× faster than a disk-backed database round trip, and a 95% hit rate removes 95% of the database load. Almost every design question has a caching deep dive.

## Key ideas

**Where caches live**: client/browser → CDN → API gateway → application (in-process) → distributed cache (Redis, Memcached) → database buffer pool.

**Read and write strategies**

| Strategy | How it works | Use when |
|---|---|---|
| Cache-aside (lazy loading) | App reads cache; on miss reads DB and fills cache | Default choice for reads |
| Read-through | Cache library loads from DB on miss | Same idea, less app code |
| Write-through | Write to cache and DB together | Reads right after writes must be fresh |
| Write-behind (write-back) | Write to cache, flush to DB later | Very high write rates, can tolerate loss |
| Write-around | Write to DB only, cache fills on read | Data written once, rarely read |

**Eviction**: LRU (most common), LFU (keeps popular items), TTL expiry. Memory is finite, so size the cache for the **working set**, not all data.

**Invalidation** is the hard part:

- TTLs bound staleness with no coordination.
- Delete the key on write (not update) to avoid racing writers putting stale values back.
- Change data capture (CDC) from the database log can invalidate caches reliably.

## Failure modes to name

- **Thundering herd / cache stampede**: a hot key expires and thousands of requests hit the DB at once. Fixes: request coalescing (single flight), a lock per key, early refresh before expiry, jittered TTLs.
- **Hot keys**: one key (a celebrity profile) overwhelms a single cache node. Fixes: replicate hot keys, add a small in-process cache in front, split the key (`key#1..key#N`).
- **Cache penetration**: requests for keys that don't exist always miss. Cache the "not found" result briefly, or use a Bloom filter.
- **Cold start**: an empty cache after a restart sends full load to the DB. Warm it up or ramp traffic gradually.

## Redis beyond key-value

Sorted sets (leaderboards, rate limit windows), lists (timelines), hashes, `INCR` with `EXPIRE` (counters), pub/sub, GEO commands (nearby search), Lua scripts for atomic multi-step operations. Redis Cluster shards keys across 16,384 hash slots.

## Trade-offs to talk through

- Every cache adds a consistency problem: how stale can the data be? Say the number ("up to 60 seconds is fine for view counts").
- Caches are not durable storage. If losing the cache would lose data, it's a database, so design it like one.

## Use it in an interview

- Put a cache on the read path once you've shown the read QPS.
- Say what is cached, the key, the TTL, the eviction policy and the expected hit rate.

## Check yourself

1. Why delete a cache key on update instead of writing the new value into the cache?
2. A product page key expires during a flash sale and the DB falls over. What happened and how do you prevent it?
3. When would write-behind caching be unacceptable?
