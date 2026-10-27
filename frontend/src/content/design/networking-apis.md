## Why it matters

Every design starts with clients talking to servers. The protocol, the shape of the API and how traffic is spread across machines decide latency, how you scale out and how real-time features work.

## Key ideas

**Load balancers** spread requests across identical, stateless servers.

- **L4** (TCP level) is fast and protocol-agnostic. **L7** (HTTP level) can route by path, header or cookie, terminate TLS and retry.
- Algorithms: round robin, least connections, consistent hashing (sticky by user or document id).
- Health checks remove dead servers. Run a pair of load balancers, or a managed one, so it isn't a single point of failure.
- **Stateless servers** keep session data in a shared store (Redis, DB, signed token), so any server can serve any request and scaling out is just adding servers.

**API styles**

| Style | Good for | Watch out for |
|---|---|---|
| REST over HTTP + JSON | Public APIs, CRUD on resources | Over/under-fetching, many round trips |
| gRPC (HTTP/2 + Protobuf) | Service-to-service, low latency, streaming | Browser support needs a proxy |
| GraphQL | Clients that need flexible shapes (mobile) | Caching and expensive queries |

**Real-time delivery** from server to client:

- **Short polling**: client asks every N seconds. Simple, wasteful, slow.
- **Long polling**: server holds the request open until there's data. Works everywhere.
- **Server-Sent Events (SSE)**: one-way stream over HTTP. Great for feeds and notifications.
- **WebSockets**: full-duplex, persistent connection. Chat, games, collaboration. Connections are stateful, so you need a registry of which gateway holds which user.

**API gateway**: one entry point that does auth, rate limiting, routing and request shaping before traffic reaches services.

**API design details interviewers like**

- Pagination with a **cursor** (`?after=<id>`) rather than offset: stable when new items arrive and cheap for the database.
- **Idempotency keys** on POSTs that create money or messages, so retries are safe.
- Versioning (`/v1/`), proper status codes (429 for rate limits, 409 for conflicts).

## Trade-offs to talk through

- Persistent connections (WebSockets) give low latency but make deploys, load balancing and failover harder: a server restart drops thousands of connections that must reconnect with backoff.
- L7 load balancing is smarter but costs more CPU than L4.
- Sticky routing helps caching and stateful protocols but creates hot spots and uneven load.

## Use it in an interview

- Write 3–5 key endpoints early with request and response shapes.
- Say which protocol real-time features use and why.
- Draw a load balancer in front of every horizontally scaled tier.

## Check yourself

1. 10M users hold WebSocket connections. How do you deliver a message to user B when user A is connected to a different gateway server?
2. Why is offset pagination a problem for an infinite-scroll feed?
3. When would you choose SSE over WebSockets?
