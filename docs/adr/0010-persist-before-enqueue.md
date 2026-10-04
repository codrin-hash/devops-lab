# ADR-0010: Persist before enqueue

Status: Accepted

## Context

A deploy request writes a row to Postgres and pushes its id to Redis. The two writes are not atomic.

## Decision

Commit the deployment row first, then `LPUSH` the id.

## Consequences

- Reverse order is a race: the worker can pop the id before the row is visible, drop the job, and leave the deployment in `queued` forever. Intermittent and hard to reproduce.
- With this order, a Redis failure after commit returns 500 but leaves a `queued` row in Postgres. State is visible and recoverable because Postgres is the source of truth.
- Recovery is not implemented. Planned: a reconciler that re-enqueues `queued` deployments older than N seconds (GAP-001).

## Alternatives

- Transactional outbox: write the job to an outbox table in the same transaction, relay to Redis asynchronously.
- Postgres as the queue (`SELECT ... FOR UPDATE SKIP LOCKED`): removes the dual write entirely.