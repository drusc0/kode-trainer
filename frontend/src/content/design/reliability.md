## Why it matters

At scale, something is always broken: a disk, a node, a dependency, a whole zone. Senior-level answers show how the system keeps working (or degrades gracefully) when parts fail, how it protects itself from overload, and how you'd know something is wrong.

## Key ideas

**Redundancy**: no single points of failure. At least two of everything, spread across availability zones; multi-region for the most critical paths (active-passive is simpler; active-active is faster and harder).

**Rate limiting algorithms**

| Algorithm | Idea | Note |
|---|---|---|
| Fixed window counter | Count per calendar minute | Allows 2× bursts at window edges |
| Sliding window log | Store each request timestamp | Exact, memory-heavy |
| Sliding window counter | Weighted mix of current and previous window | Good approximation, cheap |
| Token bucket | Tokens refill at rate r up to capacity b; each request takes one | Allows bursts up to b; very common |
| Leaky bucket | Queue drains at a fixed rate | Smooths output |

Distributed limits keep counters in Redis and update them atomically (Lua script or `INCR` + `EXPIRE`).

**Timeouts, retries and backoff**: every network call has a timeout. Retry only idempotent operations, with **exponential backoff plus jitter**, and a retry budget so retries don't multiply load during an outage (retry storms).

**Circuit breaker**: after repeated failures, stop calling a dependency for a while (open), then let a few test requests through (half-open). Fail fast instead of piling up threads.

**Bulkheads**: separate thread pools, queues or clusters per dependency or tenant, so one slow thing can't exhaust shared resources.

**Load shedding and graceful degradation**: under overload, drop low-priority work first, serve cached or partial results (a feed without recommendations), return 429/503 early.

**Health checks and failover**: liveness vs readiness checks; automatic failover with leader election; avoid split brain with quorums and fencing.

**Observability**

- **Metrics** (counters, gauges, histograms): the four golden signals are latency, traffic, errors and saturation.
- **Logs**: structured, with a request ID.
- **Traces**: one request followed across services (OpenTelemetry).
- **SLI / SLO / SLA**: what you measure (p99 latency), the target (99.9% under 300 ms) and the contract. An **error budget** is how much failure the SLO allows.

**Safe deploys**: canary releases, feature flags, automatic rollback on SLO regressions; backward-compatible schema changes (expand, migrate, contract).

**Disaster recovery**: backups that you've tested restoring; RPO (how much data you can lose) and RTO (how long recovery may take).

## Trade-offs to talk through

- Fail open vs fail closed when a protective component (rate limiter, auth cache) is down.
- Multi-region active-active improves availability and latency but forces you to handle conflicting writes.
- More retries improve the success rate for transient errors and worsen outages.

## Use it in an interview

- For each component, ask "what happens if this dies?" and answer it before the interviewer does.
- Mention what you'd monitor and alert on for the main flow.

## Check yourself

1. Why add jitter to exponential backoff?
2. Implement a token bucket in your head: what state is stored per client, and how do you update it on each request?
3. A payment dependency starts timing out after 30 seconds. What happens to your service without timeouts and circuit breakers?
