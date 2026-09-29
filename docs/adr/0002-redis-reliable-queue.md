# ADR-0002: Custom reliable queue on Redis lists

- Status: Accepted
- Date: 2026-09-29

## Context

Deployments are long-running and must not block the API. Jobs must survive a worker crash.

## Decision

Reliable queue pattern:

1. The API enqueues with `LPUSH idp:queue <id>`.
2. The worker takes a job with `BLMOVE idp:queue idp:processing`, atomically.
3. On completion, the worker removes it with `LREM idp:processing <id>`.

## Alternatives considered

- **Celery.** Heavy, and it hides delivery semantics that are central to this project.
- **RQ.** Lighter, but the same objection.
- **Redis Streams with consumer groups.** Candidate if multiple consumer types appear.

## Consequences

- At-least-once delivery: handlers must be idempotent.
- Jobs stuck in `idp:processing` after a crash need a recovery mechanism ([GAP-001](../tech-debt.md)).
- About 50 lines of owned code.
