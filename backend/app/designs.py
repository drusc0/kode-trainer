"""System design questions. `rubric` is hidden from the UI: it steers the AI interviewer's deep dives."""

from dataclasses import dataclass
from typing import Literal

# Slugs of the fundamentals guides in frontend/src/content/design/*.md.
FUNDAMENTALS = (
    "estimation",
    "networking-apis",
    "caching",
    "databases",
    "replication-partitioning",
    "consistency",
    "messaging",
    "stream-batch",
    "storage-cdn",
    "search-geo",
    "reliability",
)


@dataclass(frozen=True)
class Design:
    slug: str
    title: str
    difficulty: Literal["Easy", "Medium", "Hard"]
    tags: list[str]
    summary: str
    prompt: str
    functional: list[str]
    non_functional: list[str]
    scale: list[str]
    fundamentals: list[str]
    rubric: list[str]


DESIGNS: list[Design] = [
    Design(
        slug="url-shortener",
        title="URL shortener",
        difficulty="Easy",
        tags=["key-value store", "caching", "ID generation"],
        summary="Turn long URLs into short links and redirect billions of clicks with low latency.",
        prompt="Design a service like bit.ly. Users submit a long URL and get back a short link; anyone visiting "
        "the short link is redirected to the original URL.",
        functional=[
            "Create a short link for a long URL, optionally with a custom alias and an expiry",
            "Redirect a short link to its long URL",
            "Basic click counts per link",
        ],
        non_functional=[
            "Redirects are very low latency (p99 < 50 ms)",
            "Highly available: a broken redirect breaks someone else's website",
            "Short codes must be unique and hard to enumerate",
        ],
        scale=["100M new links per month", "Read:write ratio around 100:1", "Links kept for 5 years by default"],
        fundamentals=["estimation", "databases", "caching", "replication-partitioning"],
        rubric=[
            "Short code generation: hash + collision handling vs counter + base62 vs pre-generated key pool; "
            "how many characters are needed for the volume (62^7 ≈ 3.5 trillion)",
            "Avoiding a single counter bottleneck: ranges handed to each app server, Snowflake-style IDs",
            "301 vs 302 redirect and its effect on analytics and caching",
            "Read path: cache-aside in Redis/CDN for hot links, cache hit ratio, what happens on a miss storm",
            "Storage choice: a key-value or wide-column store sharded by short code; size estimate",
            "Custom alias uniqueness under concurrency (conditional put / unique constraint)",
            "Click analytics without slowing redirects: async events to a queue",
            "Expiry and cleanup; abuse prevention (rate limits, malware URL checks)",
        ],
    ),
    Design(
        slug="rate-limiter",
        title="Distributed rate limiter",
        difficulty="Medium",
        tags=["Redis", "algorithms", "API gateway"],
        summary="Throttle clients across a fleet of API servers so one tenant can't take the service down.",
        prompt="Design a rate limiter that sits in front of a public API served by hundreds of stateless servers. "
        "Limits are defined per API key and per endpoint, for example 100 requests per minute.",
        functional=[
            "Allow or reject each request according to configurable rules",
            "Return 429 with headers telling the client when to retry",
            "Rules can change without a deploy",
        ],
        non_functional=[
            "Adds at most a few milliseconds to each request",
            "Accurate enough that a client can't exceed its limit by a large factor",
            "If the limiter fails, the API keeps serving (fail open) or protects itself (fail closed): justify",
        ],
        scale=["1M requests per second at peak", "10M distinct API keys", "Hundreds of API servers"],
        fundamentals=["reliability", "caching", "consistency", "networking-apis"],
        rubric=[
            "Algorithms compared: fixed window (burst at edges), sliding log (memory), sliding window counter, "
            "token bucket and leaky bucket; which fits which goal",
            "Where it runs: client, API gateway / sidecar, or inside the service",
            "Shared state in Redis: atomic check-and-increment with Lua or INCR + EXPIRE; race conditions with "
            "naive get-then-set",
            "Reducing Redis round trips: local token caching / batching, accepting slight over-admission",
            "Sharding counters by key; hot keys from one huge tenant",
            "Multi-region: global vs per-region limits and the accuracy trade-off",
            "Failure mode of Redis: fail open vs closed, timeouts, circuit breaker",
            "Rule storage and propagation; response headers (X-RateLimit-Remaining, Retry-After)",
        ],
    ),
    Design(
        slug="news-feed",
        title="Social news feed",
        difficulty="Medium",
        tags=["fan-out", "caching", "timelines"],
        summary="Build each user's home timeline from the posts of the people they follow.",
        prompt="Design the home feed of a social network like Twitter/X or Instagram. Users follow other users "
        "and see a reverse-chronological feed of posts from the accounts they follow.",
        functional=[
            "Publish a post (text plus optional media)",
            "Follow and unfollow users",
            "Read a paginated home feed of followed accounts' posts, newest first",
        ],
        non_functional=[
            "Feed loads in under 200 ms",
            "A new post appears in followers' feeds within a few seconds (eventual consistency is fine)",
            "Read-heavy: feeds are read far more than posts are written",
        ],
        scale=["500M daily active users", "Average 200 followees; some accounts have 100M followers", "50M posts/day"],
        fundamentals=["caching", "messaging", "databases", "replication-partitioning"],
        rubric=[
            "Fan-out on write (push to follower timelines) vs fan-out on read (pull and merge); cost of each",
            "Celebrity problem: hybrid model where celebrity posts are merged in at read time",
            "Timeline cache structure (e.g. Redis list of post IDs per user, capped length) and hydration of posts",
            "Async fan-out workers fed by a queue; back-pressure when a celebrity posts",
            "Cursor-based pagination vs offset; stable ordering with Snowflake IDs",
            "Data model: posts table, follow graph storage and sharding key",
            "Inactive users: skip pre-computing feeds for them",
            "Media goes to object storage + CDN, not the feed path",
        ],
    ),
    Design(
        slug="chat-app",
        title="Chat / messaging app",
        difficulty="Medium",
        tags=["WebSockets", "Cassandra", "presence"],
        summary="One-to-one and group messaging with delivery receipts and online presence.",
        prompt="Design a messaging service like WhatsApp or Messenger with 1:1 chats, small group chats, "
        "delivery/read receipts and online indicators.",
        functional=[
            "Send and receive messages in real time in 1:1 and group chats (up to 200 members)",
            "Messages sent while a recipient is offline are delivered when they reconnect",
            "Sent / delivered / read receipts and online / last-seen presence",
            "Message history syncs across a user's devices",
        ],
        non_functional=[
            "End-to-end delivery latency under 500 ms for online users",
            "No message is lost once the sender sees it as sent",
            "Messages in a chat appear in a consistent order",
        ],
        scale=["1B users, 100M concurrent connections", "50B messages per day"],
        fundamentals=["networking-apis", "databases", "messaging", "consistency"],
        rubric=[
            "Connection protocol: WebSockets vs long polling vs SSE; connection gateway servers",
            "Routing a message to the gateway holding the recipient's connection (session registry in Redis, "
            "pub/sub between gateways)",
            "Durable write before ack; offline inbox and sync on reconnect with a per-device cursor",
            "Ordering: per-chat sequence numbers vs timestamps; clock skew",
            "Storage: wide-column store (Cassandra/HBase) partitioned by chat_id, clustered by message id",
            "Group fan-out: write once per group vs per member",
            "Presence via heartbeats with TTL; fan-out cost of presence updates and how to limit it",
            "Idempotent sends with client-generated message IDs to dedupe retries",
            "Push notifications for offline mobile clients",
        ],
    ),
    Design(
        slug="notification-service",
        title="Notification service",
        difficulty="Medium",
        tags=["queues", "retries", "idempotency"],
        summary="Send email, SMS and push notifications reliably on behalf of many internal services.",
        prompt="Design a central notification platform. Internal services call it to notify users over push, "
        "SMS or email, through third-party providers like APNs, Twilio and SendGrid.",
        functional=[
            "Send a notification to a user on one or more channels, immediately or scheduled",
            "Respect user preferences, opt-outs and quiet hours",
            "Templates with per-user variables; track delivery status",
        ],
        non_functional=[
            "At-least-once delivery without spamming duplicates",
            "A slow or failing provider must not block other channels",
            "Bursts of 10x normal traffic (e.g. a marketing campaign) are absorbed",
        ],
        scale=["1B notifications per day", "Peak 100k per second"],
        fundamentals=["messaging", "reliability", "databases"],
        rubric=[
            "API accepts and persists the request, then enqueues; separate queues/topics per channel",
            "Workers per channel with provider-specific rate limits and retries with exponential backoff + jitter",
            "Dead-letter queue and alerting for poison messages",
            "Idempotency key per notification to dedupe retries; at-least-once vs exactly-once effects",
            "Priority: transactional (OTP) vs marketing traffic isolation",
            "Preference and rate checks before sending; fatigue limits",
            "Scheduled sends: delay queue or a scheduler scanning a time-indexed table",
            "Provider failover and circuit breakers; tracking delivery via provider webhooks",
        ],
    ),
    Design(
        slug="web-crawler",
        title="Web crawler",
        difficulty="Medium",
        tags=["distributed queue", "Bloom filter", "politeness"],
        summary="Crawl billions of pages politely, without fetching the same page twice.",
        prompt="Design a web crawler that downloads a large share of the public web to feed a search index. "
        "Start from a set of seed URLs and keep discovering new pages.",
        functional=[
            "Fetch pages, extract links and add new URLs to crawl",
            "Store raw page content for the indexer",
            "Re-crawl pages periodically based on how often they change",
        ],
        non_functional=[
            "Polite: obey robots.txt and never overload a single host",
            "Scales horizontally; survives worker crashes without losing the frontier",
            "Avoids traps (infinite calendars, session-id URLs) and duplicate content",
        ],
        scale=["1B pages per week", "Average page 500 KB"],
        fundamentals=["estimation", "messaging", "storage-cdn", "replication-partitioning"],
        rubric=[
            "Back-of-envelope: pages/sec, bandwidth, storage per week",
            "URL frontier design: priority queues plus per-host queues to enforce politeness delays",
            "Partitioning the frontier by host hash so one worker owns a host",
            "URL dedup with a Bloom filter or a seen-set store; content dedup with checksums / SimHash",
            "DNS resolution caching as a hidden bottleneck",
            "robots.txt fetching and caching",
            "Crawler trap detection: depth limits, URL normalization, per-host page caps",
            "Storing content in object storage (e.g. S3/WARC files) and metadata in a DB",
            "Checkpointing frontier state for fault tolerance",
        ],
    ),
    Design(
        slug="video-streaming",
        title="Video streaming platform",
        difficulty="Hard",
        tags=["object storage", "CDN", "transcoding pipeline"],
        summary="Upload, transcode and stream video to millions of viewers on any device.",
        prompt="Design a video platform like YouTube. Creators upload videos; viewers watch them on phones, "
        "laptops and TVs with smooth playback on varying network speeds.",
        functional=[
            "Upload large video files (up to several GB) with resumable uploads",
            "Transcode into multiple resolutions and formats",
            "Stream with adaptive bitrate; show view counts",
        ],
        non_functional=[
            "Playback starts in under 2 seconds and rarely buffers",
            "Uploads never lose data; processing can take minutes",
            "Cost-efficient storage and bandwidth",
        ],
        scale=["500 hours of video uploaded per minute", "1B hours watched per day"],
        fundamentals=["storage-cdn", "messaging", "estimation", "databases"],
        rubric=[
            "Upload path: presigned URLs straight to object storage, multipart / resumable chunks",
            "Transcoding as a DAG of tasks (split into segments, transcode in parallel, merge); workers fed by a queue",
            "HLS/DASH segments + manifests and adaptive bitrate on the client",
            "CDN for delivery; origin shielding; popular vs long-tail content placement and cost",
            "Metadata DB (video, channel, status state machine) separate from blob storage",
            "View counting at scale: aggregate counters asynchronously",
            "Storage tiers for cold videos; estimate of storage per minute of video across renditions",
            "Failure handling in the pipeline: retries, idempotent tasks, status tracking",
        ],
    ),
    Design(
        slug="ride-sharing",
        title="Ride-sharing dispatch",
        difficulty="Hard",
        tags=["geospatial index", "real-time location", "matching"],
        summary="Match riders with nearby drivers using live location updates from millions of phones.",
        prompt="Design the core of a ride-hailing app like Uber or Lyft: riders request a ride, nearby drivers "
        "are offered the trip, and both see each other's position live.",
        functional=[
            "Drivers send their location every few seconds while online",
            "Rider requests a ride and gets matched with a nearby available driver",
            "A driver receives at most one offer at a time and can accept or decline",
            "Both parties track each other in real time during the trip",
        ],
        non_functional=[
            "Matching completes within seconds",
            "A driver is never assigned to two rides at once",
            "Location writes are very high volume; slightly stale positions are acceptable",
        ],
        scale=["5M active drivers sending updates every 4 s", "1M ride requests per hour at peak"],
        fundamentals=["search-geo", "consistency", "caching", "networking-apis"],
        rubric=[
            "Write volume estimate for location updates (~1.25M writes/sec) and why a relational DB per update "
            "doesn't fit",
            "Geospatial indexing: geohash, quadtree, Uber's H3 / Google S2; querying neighbouring cells",
            "Keeping live locations in memory (Redis GEO or sharded in-memory index by region)",
            "Matching flow: find candidates, rank by ETA, offer to one driver with a timeout, then the next",
            "Preventing double assignment: distributed lock or conditional update on driver status",
            "Real-time channel to driver and rider apps (WebSockets / push)",
            "Sharding by city/region; hot spots like airports and stadiums",
            "Trip state machine durability and payments handled asynchronously",
        ],
    ),
    Design(
        slug="key-value-store",
        title="Distributed key-value store",
        difficulty="Hard",
        tags=["consistent hashing", "quorums", "gossip"],
        summary="Build a Dynamo-style store that stays available through node and network failures.",
        prompt="Design a distributed key-value store (think Amazon Dynamo or Cassandra) offering put(key, value) "
        "and get(key) across a cluster of commodity machines.",
        functional=["put(key, value) and get(key)", "Values up to 1 MB", "Tunable consistency per request"],
        non_functional=[
            "Always writable, even during node failures and network partitions",
            "Scales out by adding nodes with minimal data movement",
            "Single-digit millisecond latency",
        ],
        scale=["Petabytes of data", "Thousands of nodes", "Millions of operations per second"],
        fundamentals=["replication-partitioning", "consistency", "databases", "reliability"],
        rubric=[
            "Partitioning with consistent hashing and virtual nodes; why plain mod-N hashing fails on resize",
            "Replication to N successors on the ring; preference list",
            "Quorums: N, R, W and when R + W > N gives read-your-writes; sloppy quorums",
            "Conflict resolution: last-write-wins vs vector clocks with client-side merge",
            "Hinted handoff for temporary failures; anti-entropy with Merkle trees",
            "Failure detection and membership via gossip",
            "Storage engine: write-ahead log + memtable + SSTables (LSM tree), compaction, Bloom filters",
            "CAP trade-off: choosing AP and what that costs the application",
        ],
    ),
    Design(
        slug="typeahead",
        title="Search autocomplete",
        difficulty="Medium",
        tags=["trie", "top-k", "offline aggregation"],
        summary="Suggest the most popular completions as the user types each character.",
        prompt="Design the autocomplete box of a search engine: as the user types, show the top 5 most popular "
        "queries that start with the current prefix.",
        functional=[
            "Return the top 5 suggestions for a prefix",
            "Suggestions reflect query popularity, updated at least daily",
            "Filter out offensive or blocked terms",
        ],
        non_functional=["Response under 100 ms including network, as the user types", "Highly available"],
        scale=["10M daily active users, ~10 searches each, ~20 keystroke requests per search"],
        fundamentals=["search-geo", "caching", "stream-batch", "estimation"],
        rubric=[
            "Trie with top-k completions cached at each node vs scanning subtree at query time",
            "Building the trie offline from query logs (batch job), with optional time decay; swapping versions",
            "Serving: trie in memory, sharded by prefix range; handling uneven prefix distribution",
            "Caching results for short prefixes in CDN / browser; client debouncing",
            "Estimating QPS from keystrokes",
            "Real-time trending: streaming counts merged with batch results",
            "Blocklist filtering at build time and serving time",
        ],
    ),
    Design(
        slug="ticket-booking",
        title="Event ticket booking",
        difficulty="Hard",
        tags=["strong consistency", "reservations", "virtual queue"],
        summary="Sell seats for a hot concert to millions of fans without double-booking.",
        prompt="Design a ticketing system like Ticketmaster. Users browse events, pick specific seats, hold them "
        "for a few minutes while paying, and receive tickets.",
        functional=[
            "Search and view events with a live seat map",
            "Reserve specific seats for 10 minutes while checking out",
            "Complete purchase via a payment provider; release seats if payment fails or times out",
        ],
        non_functional=[
            "A seat can never be sold twice",
            "Survive flash crowds of millions of users when popular events open",
            "Fair access during sales",
        ],
        scale=["Popular events: 10M users arriving within minutes for 50k seats", "Normal load: 1k bookings/s"],
        fundamentals=["consistency", "databases", "caching", "reliability"],
        rubric=[
            "Reservation model: seat status with hold expiry; conditional update / SELECT ... FOR UPDATE / "
            "optimistic version checks",
            "Distributed lock with TTL (Redis) vs DB row lock; what happens when a lock expires mid-payment",
            "Releasing expired holds: TTL keys vs a sweeper job",
            "Virtual waiting room / queue to admit users at a controlled rate",
            "Seat map reads from cache with short TTL vs strongly consistent booking path",
            "Payment idempotency and the order state machine (reserved → paid → ticketed)",
            "Search via Elasticsearch, kept in sync with CDC",
            "Bot protection and per-user limits",
        ],
    ),
    Design(
        slug="payment-system",
        title="Payment system",
        difficulty="Hard",
        tags=["idempotency", "ledger", "sagas"],
        summary="Charge customers and pay sellers for an e-commerce site with zero money lost.",
        prompt="Design the payment backend for an online marketplace. Buyers pay with cards via an external "
        "payment service provider (PSP); the marketplace pays out sellers later.",
        functional=[
            "Accept a payment for an order through a PSP like Stripe or Adyen",
            "Record money movement in a ledger; support refunds",
            "Pay out sellers on a schedule; reconcile with PSP and bank reports",
        ],
        non_functional=[
            "Never charge twice and never lose a payment record",
            "Strong consistency and a complete audit trail",
            "Throughput is modest; correctness matters more than latency",
        ],
        scale=["10M transactions per day", "Peak 1k per second"],
        fundamentals=["consistency", "messaging", "databases", "reliability"],
        rubric=[
            "Idempotency keys end to end: client → payment service → PSP; storing request + response",
            "Payment state machine and what to do with unknown outcomes (timeouts) from the PSP",
            "Double-entry ledger, append-only; balances derived from entries",
            "Hosted payment page / tokenization to avoid handling card numbers (PCI scope)",
            "Async processing: PSP webhooks, retries with backoff, dead-letter queue",
            "Transactional outbox or saga to coordinate order, payment and ledger services without 2PC",
            "Daily reconciliation against PSP settlement files and handling mismatches",
            "Exactly-once effects from at-least-once delivery",
        ],
    ),
    Design(
        slug="metrics-monitoring",
        title="Metrics and alerting platform",
        difficulty="Hard",
        tags=["time-series DB", "Kafka", "downsampling"],
        summary="Collect, store, query and alert on metrics from a fleet of 100k servers.",
        prompt="Design a monitoring system like Datadog or Prometheus at scale: agents on every host emit "
        "metrics, engineers build dashboards and define alert rules.",
        functional=[
            "Ingest metrics (name, tags, timestamp, value) from agents",
            "Query time series with aggregation over tags and time ranges for dashboards",
            "Evaluate alert rules and notify on-call engineers",
        ],
        non_functional=[
            "Ingestion never drops data during bursts",
            "Recent data queries return in under a second",
            "Keep raw data 7 days, rolled-up data 1 year",
        ],
        scale=["100k hosts × 1,000 metrics every 10 s = 10M data points per second"],
        fundamentals=["stream-batch", "messaging", "databases", "estimation"],
        rubric=[
            "Push vs pull collection and the trade-offs",
            "Buffering ingestion through Kafka to absorb bursts and decouple storage",
            "Time-series storage: columnar chunks, delta-of-delta and XOR (Gorilla) compression",
            "Data model: series identified by metric + tags; cardinality explosion from high-cardinality tags",
            "Downsampling / rollups and retention tiers (hot SSD, cold object storage)",
            "Query path: sharding by series hash and time, fan-out and merge",
            "Alerting: a separate evaluator reading streams vs polling the DB; avoiding flapping; "
            "alerting on the alerting system",
        ],
    ),
    Design(
        slug="collaborative-editor",
        title="Collaborative document editor",
        difficulty="Hard",
        tags=["OT / CRDT", "WebSockets", "versioning"],
        summary="Several people edit the same document at once and always converge to the same text.",
        prompt="Design a real-time collaborative editor like Google Docs. Multiple users edit a document "
        "simultaneously and see each other's changes and cursors live.",
        functional=[
            "Concurrent editing with changes visible to others within a second",
            "Show collaborators' cursors and presence",
            "Version history; offline edits merge when reconnecting",
        ],
        non_functional=[
            "All replicas converge to the same document",
            "No edit is lost",
            "Documents with up to 100 simultaneous editors",
        ],
        scale=["10M documents edited per day", "Typical session: 2–5 editors"],
        fundamentals=["consistency", "networking-apis", "databases", "replication-partitioning"],
        rubric=[
            "Why naive last-write-wins or locking fails for concurrent text edits",
            "Operational transformation with a central server ordering operations vs CRDTs (e.g. RGA, Yjs)",
            "Routing all editors of a document to the same collaboration server (sticky by doc id)",
            "Operation log + periodic snapshots for storage and version history",
            "WebSocket connections; cursor/presence updates as ephemeral, lossy messages",
            "Offline edits and reconnection catch-up from a version number",
            "Failover of the collaboration server owning a document",
        ],
    ),
    Design(
        slug="ad-click-aggregation",
        title="Ad click aggregator",
        difficulty="Hard",
        tags=["Flink", "exactly-once", "windowing"],
        summary="Count billions of ad clicks per minute for billing and real-time dashboards.",
        prompt="Design a system that ingests ad click events and lets advertisers query click counts per ad "
        "over time, accurately enough to bill them.",
        functional=[
            "Ingest click events and redirect the user to the advertiser's site",
            "Advertisers query clicks per ad at 1-minute granularity over arbitrary ranges",
            "Filter fraudulent and duplicate clicks",
        ],
        non_functional=[
            "Counts must be accurate for billing (no double counting, no loss)",
            "Dashboard data is at most a minute or two behind",
            "Late events (up to minutes late) are still counted",
        ],
        scale=["10k clicks per second average, 50k at peak", "10M active ads"],
        fundamentals=["stream-batch", "messaging", "databases", "reliability"],
        rubric=[
            "Ingest to Kafka partitioned by ad id; click redirect path stays fast",
            "Stream processing (Flink/Spark Streaming) with tumbling windows, event time and watermarks",
            "Exactly-once: checkpointing, idempotent sinks / transactional writes",
            "Dedup with click IDs (impression id signed by the server)",
            "OLAP store for aggregated results (e.g. Druid, ClickHouse, Pinot)",
            "Reconciliation: periodic batch job over raw events in object storage (lambda) vs kappa reprocessing",
            "Hot ads: key salting / pre-aggregation",
        ],
    ),
    Design(
        slug="file-sync",
        title="File sync and storage",
        difficulty="Hard",
        tags=["chunking", "deduplication", "metadata DB"],
        summary="Keep a folder of files in sync across a user's devices, like Dropbox.",
        prompt="Design a cloud file storage and sync service like Dropbox or Google Drive. Files placed in a "
        "folder on one device appear on the user's other devices and can be shared.",
        functional=[
            "Upload, download and delete files of up to 50 GB",
            "Sync changes automatically across devices",
            "Share files and folders with other users; keep file version history",
        ],
        non_functional=[
            "No data loss; files are durable",
            "Efficient on bandwidth: only changed parts are uploaded",
            "Changes show up on other devices within seconds",
        ],
        scale=["500M users, 100M daily active", "Average 200 files per user, average 1 MB"],
        fundamentals=["storage-cdn", "databases", "consistency", "messaging"],
        rubric=[
            "Chunking files (e.g. 4 MB blocks, or content-defined chunking) and content-hash addressing",
            "Upload only changed chunks; dedup identical chunks across users",
            "Metadata DB (files, versions, chunk lists, namespaces) strongly consistent, separate from block storage",
            "Presigned URLs for direct block upload to object storage",
            "Change notification: long polling / WebSockets per device + a per-namespace change journal with cursors",
            "Conflict handling when two devices edit offline: conflicted copies",
            "Sharding metadata by user/namespace; sharing across namespaces",
        ],
    ),
    Design(
        slug="message-queue",
        title="Distributed message queue",
        difficulty="Hard",
        tags=["append-only log", "partitions", "replication"],
        summary="Build a Kafka-like durable log that many producers write to and many consumers read from.",
        prompt="Design a distributed commit log / message broker like Apache Kafka. Producers publish messages "
        "to topics; consumer groups read them in order and can replay from any point.",
        functional=[
            "Publish messages to a topic; consume them in order within a partition",
            "Consumer groups share work; each tracks its own offset",
            "Retain messages for a configurable time and allow replay",
        ],
        non_functional=[
            "Durable: acknowledged messages survive broker failures",
            "Very high throughput (millions of messages per second)",
            "Horizontal scalability by adding brokers",
        ],
        scale=["1M messages per second, 1 KB average", "7-day retention"],
        fundamentals=["messaging", "replication-partitioning", "consistency", "storage-cdn"],
        rubric=[
            "Topic → partitions as append-only segment files; why sequential IO and the page cache make it fast",
            "Partition leader + followers, in-sync replicas (ISR), acks=all and min.insync.replicas",
            "Leader election and the controller / metadata quorum (ZooKeeper vs KRaft / Raft)",
            "Producer partitioning by key for ordering; batching and compression",
            "Consumer groups, partition assignment, rebalancing, committed offsets",
            "Delivery semantics: at-most / at-least / exactly-once with idempotent producers and transactions",
            "Retention by time/size and log compaction",
            "Storage estimate for 7 days with replication factor 3",
        ],
    ),
]

BY_SLUG = {d.slug: d for d in DESIGNS}
