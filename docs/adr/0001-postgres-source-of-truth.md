# ADR-0001: Postgres is the source of truth, Redis is transport

- Status: Accepted
- Date: 2026-09-29

## Context

API and worker need shared deployment state and a way to hand off work.

## Decision

All state lives in Postgres. Redis carries only deployment IDs.

## Alternatives considered

- **Queue in Postgres** (`SELECT ... FOR UPDATE SKIP LOCKED`). One service fewer and fully viable at this scale. Rejected because Redis is also needed for log streams.
- **State in Redis.** Weaker durability, no relational queries. Rejected.

## Consequences

- Losing Redis is recoverable: re-enqueue every deployment with `status = 'queued'`.
- A single store serves queries, history and future metrics.
- One more service to operate.
