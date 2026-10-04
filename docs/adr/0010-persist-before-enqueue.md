# ADR-0010: Persist before enqueue

- Status: Accepted
- Date: 2026-10-04

## Context

A deploy request writes a row to Postgres and pushes its id to Redis. The two writes are not atomic.

## Decision

Commit the deployment row first, then `LPUSH` the id.

## Alternatives considered

- **Enqueue first.** The worker can pop the id before the row is visible, drop the job, and leave the deployment in `queued` forever. Intermittent and hard to reproduce.
- **Transactional outbox.** Write the job to an outbox table in the same transaction and relay it to Redis asynchronously. Correct, but adds a relay process.
- **Postgres as the queue** (`SELECT ... FOR UPDATE SKIP LOCKED`). Removes the dual write entirely; Redis is kept for log streams in later stages.

## Consequences

- A Redis failure after commit returns 500 but leaves a `queued` row in Postgres. State is visible and recoverable because Postgres is the source of truth.
- Recovery is not implemented. Planned: a reconciler that re-enqueues `queued` deployments older than N seconds.
