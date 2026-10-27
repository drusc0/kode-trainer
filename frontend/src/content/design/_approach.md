A system design interview is a 45–60 minute conversation, not a quiz. The interviewer wants to see how you scope an ambiguous problem, build something that works, then reason about where it breaks. Use the same six steps every time so you never freeze.

## 1. Requirements (5 min)

- **Functional**: the 3–5 things users can do. Say out loud what you're leaving out ("no search, no ads for now").
- **Non-functional**: latency, availability, consistency, durability, security. Turn adjectives into targets: "fast" becomes "p99 under 200 ms".
- Ask who the users are and what matters most. A payment system values correctness; a feed values latency.

## 2. Estimates (3–5 min)

Only the numbers that change the design: requests per second (average and peak), read/write ratio, storage growth per year, bandwidth. Round aggressively. See **Back-of-envelope estimation**.

## 3. API and data model (5 min)

- List the main endpoints with their inputs and outputs, for example `POST /links {long_url} → {code}`.
- Sketch the main entities and their keys. The access pattern decides the storage engine and the shard key.

## 4. High-level design (10–15 min)

Draw the request path end to end: client → load balancer → services → caches → databases → queues → workers. Make the simple version work first. Walk one write and one read through the diagram.

## 5. Deep dives (15–20 min)

Pick the 2–3 hardest parts, or let the interviewer pick. Typical ones: the hot path at peak load, a consistency guarantee, a failure scenario, a data model at scale. For each, offer two options, compare them and choose.

## 6. Wrap up (2–3 min)

Bottlenecks you'd watch, what you'd monitor, how you'd evolve the design at 10x scale.

## Habits that score well

- **Think out loud.** Silence reads as stuck.
- **Name trade-offs.** "Option A is simpler but X; I'll pick B because of requirement Y."
- **Start simple, then scale.** Don't open with Kafka, Kubernetes and twelve microservices.
- **Use numbers.** "That's 40k QPS, too much for one Postgres primary, so…"
- **Check in.** "Does this level of detail work, or should I go deeper on storage?"

## Drawing tips for the whiteboard

- Boxes for services, cylinders for databases, a pipe or queue shape for queues, a cloud for the CDN.
- Label every arrow with what flows: `POST /links`, `click event`, `cache miss`.
- Number the steps of the main flow (1, 2, 3…) so the reviewer can follow it.
- Keep notes (requirements, estimates, API) in the notes panel or in a text box beside the diagram.
