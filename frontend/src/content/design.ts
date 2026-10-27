export interface Fundamental {
  slug: string;
  title: string;
  summary: string;
}

// Slugs must match FUNDAMENTALS in backend/app/designs.py, which design questions link to.
export const FUNDAMENTALS: Fundamental[] = [
  {
    slug: "estimation",
    title: "Back-of-envelope estimation",
    summary: "Turn users into QPS, storage and bandwidth in a minute, and know the latency numbers by heart.",
  },
  {
    slug: "networking-apis",
    title: "Networking, APIs & load balancing",
    summary: "REST vs gRPC, WebSockets vs SSE vs long polling, L4/L7 load balancers and stateless servers.",
  },
  {
    slug: "caching",
    title: "Caching",
    summary: "Cache-aside and write strategies, eviction, invalidation, stampedes and hot keys, and Redis.",
  },
  {
    slug: "databases",
    title: "Databases & data modelling",
    summary: "SQL vs NoSQL families, B-trees vs LSM trees, transactions, isolation and designing for queries.",
  },
  {
    slug: "replication-partitioning",
    title: "Replication & sharding",
    summary: "Leader, multi-leader and leaderless replication, shard keys, consistent hashing and hot partitions.",
  },
  {
    slug: "consistency",
    title: "Consistency, consensus & transactions",
    summary: "CAP and PACELC, quorums, Raft, locks with fencing, sagas, the outbox pattern and idempotency.",
  },
  {
    slug: "messaging",
    title: "Queues, logs & Kafka",
    summary: "Queues vs logs, partitions and consumer groups, delivery semantics, retries and dead-letter queues.",
  },
  {
    slug: "stream-batch",
    title: "Stream & batch processing",
    summary: "Spark vs Flink, windows and watermarks, exactly-once, lambda vs kappa and probabilistic counters.",
  },
  {
    slug: "storage-cdn",
    title: "Blob storage & CDNs",
    summary: "Object storage, presigned and multipart uploads, chunking and dedup, CDNs and video streaming.",
  },
  {
    slug: "search-geo",
    title: "Search, tries & geospatial indexes",
    summary: "Inverted indexes and sharding, tries for autocomplete, and geohash, quadtrees, S2 and H3.",
  },
  {
    slug: "reliability",
    title: "Reliability & rate limiting",
    summary: "Rate limiting algorithms, retries with jitter, circuit breakers, load shedding and observability.",
  },
];

const bodies = import.meta.glob("./design/*.md", { query: "?raw", import: "default", eager: true }) as Record<
  string,
  string
>;

export const fundamentalBody = (slug: string): string => bodies[`./design/${slug}.md`] ?? "";
export const DESIGN_APPROACH: string = bodies["./design/_approach.md"] ?? "";
export const fundamentalTitle = (slug: string): string => FUNDAMENTALS.find((f) => f.slug === slug)?.title ?? slug;
