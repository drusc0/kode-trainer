## Why it matters

A primary key lookup is easy; "find posts containing *kafka*", "complete *syst…*" and "drivers within 2 km" are not. Each needs a specialised index. These come up in search, autocomplete, maps and ride-sharing questions.

## Key ideas

**Inverted index** (Lucene, Elasticsearch, OpenSearch): for each term, a sorted list of document IDs (postings) that contain it. A query intersects posting lists. Text is analysed first: tokenise, lowercase, remove stop words, stem ("running" → "run").

- **Ranking**: TF-IDF / BM25 for relevance, plus signals like recency and popularity.
- **Sharding**: by **document** (each shard indexes a subset of docs; every query fans out to all shards and merges top results) or by **term** (a query touches only shards for its terms, but writes and big posting lists are harder). Document sharding is the common choice.
- Search indexes are usually **derived data**: the database is the source of truth and changes flow to the index through CDC or a queue, so the index is eventually consistent.
- Near-real-time indexing: new segments become searchable after a refresh interval (around 1 second).

**Tries for prefixes**: a tree of characters where each path is a prefix. For autocomplete, store the **top-k completions at each node** so a lookup is O(prefix length) with no subtree scan. Build it offline from logs, ship it to serving nodes, swap versions atomically. Shard by prefix if it doesn't fit in memory.

**Geospatial indexes**: "nearby" means 2D proximity, which a normal B-tree on latitude or longitude can't answer efficiently.

- **Geohash**: interleave latitude and longitude bits into a base-32 string; nearby points share prefixes. Search the cell plus its 8 neighbours. Edge cases at cell boundaries.
- **Quadtree**: recursively split a region into four until each cell holds at most K points. Adapts to density (more cells in cities). Usually in memory.
- **S2 (Google) / H3 (Uber)**: hierarchical cells on a sphere (squares projected onto a cube / hexagons). Hexagons have uniform neighbour distances, which suits ride-sharing.
- Ready-made: Redis GEO (geohash in a sorted set), PostGIS (R-tree), Elasticsearch geo queries.
- **Static vs moving objects**: restaurants change rarely, so a precomputed index is fine; drivers move every few seconds, so keep locations in memory with frequent overwrites and avoid indexes that are expensive to update.

## Trade-offs to talk through

- Search freshness vs indexing cost (refresh interval, bulk indexing).
- Fan-out to all shards hurts tail latency; replicas of each shard spread query load.
- Geohash precision: cells too small mean many lookups, too big mean many candidates to filter.

## Use it in an interview

- Put Elasticsearch next to the primary DB, fed by CDC, and say it's eventually consistent.
- For "nearby" questions, name the cell scheme, the cell size and how you query neighbours.

## Check yourself

1. Why does a search for "kafka streams" fan out to every shard in a document-sharded index?
2. How does storing top-k at each trie node change query cost and update cost?
3. 5M drivers update their location every 4 seconds. Why is a quadtree rebuilt from scratch a poor fit, and what would you do?
