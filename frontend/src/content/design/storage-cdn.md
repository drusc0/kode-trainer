## Why it matters

Photos, videos, documents, backups and logs are large, immutable blobs. They don't belong in a database row. Object storage plus a CDN is the standard way to store them cheaply and serve them fast worldwide.

## Key ideas

**Storage types**

- **Block storage** (EBS, local SSD): a raw disk for one machine; databases run on it.
- **File storage** (NFS, EFS): a shared filesystem with directories and locks.
- **Object storage** (S3, GCS, Azure Blob): a flat namespace of keys to immutable objects with metadata. Practically unlimited, 11 nines of durability through replication or erasure coding, cheap, accessed over HTTP. Higher latency than a disk, no in-place edits.

**The standard pattern**: keep **metadata** (owner, size, status, chunk list) in a database and the **bytes** in object storage, referenced by key.

**Uploads**

- **Presigned URLs**: the API authorises the upload and returns a time-limited URL; the client uploads straight to object storage, so large files never pass through your servers.
- **Multipart / resumable uploads**: split into parts (e.g. 5–100 MB), upload in parallel, retry only failed parts.
- After upload, an event (S3 notification → queue) triggers processing: thumbnails, transcoding, virus scanning.

**Chunking and deduplication**: split files into chunks addressed by their content hash. Identical chunks are stored once, and a small edit re-uploads only the changed chunks. **Content-defined chunking** (rolling hash) keeps boundaries stable when bytes are inserted.

**CDN (content delivery network)**: edge servers near users cache content.

- **Pull CDN**: the edge fetches from your origin on a miss. **Push**: you upload to the CDN ahead of time.
- Control caching with `Cache-Control` headers and **versioned URLs** (`app.3f2a.js`) instead of purging.
- **Origin shield**: a middle cache layer so a miss storm doesn't hit the origin from every edge.
- Signed URLs/cookies for private content.

**Video specifics**: transcode into several bitrates/resolutions, split into 2–10 second segments with a manifest (HLS/DASH). The player picks the bitrate per segment based on measured bandwidth (adaptive bitrate streaming).

**Storage tiers**: hot (standard), infrequent access, archive (Glacier). Lifecycle rules move old objects to cheaper tiers.

## Trade-offs to talk through

- CDN cost vs latency: long-tail content may not be worth caching at the edge.
- Replication (fast reads, 3× storage) vs erasure coding (~1.5× storage, slower reconstruction).
- Strongly consistent metadata vs eventually consistent object listings in some stores.

## Use it in an interview

- Never send large files through your app servers; draw presigned uploads.
- Separate the metadata service from blob storage on the diagram.
- Put a CDN in front of anything users download repeatedly.

## Check yourself

1. Why use presigned URLs rather than streaming uploads through the API servers?
2. A user edits one line in a 2 GB file. How do you avoid re-uploading 2 GB?
3. You deploy a new version of `logo.png` and users keep seeing the old one. Why, and what's the better approach?
