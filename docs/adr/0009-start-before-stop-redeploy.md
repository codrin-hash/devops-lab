# ADR-0009: Start-before-stop redeploy

- Status: Accepted
- Date: 2026-09-29

## Context

Redeploying must not cause downtime.

## Decision

The new container starts and passes its health check before the previous container is stopped with `docker stop` (SIGTERM, then SIGKILL after the grace period).

## Alternatives considered

- **Stop-then-start.** Simpler, but guarantees downtime.

## Consequences

- Two containers briefly coexist, so resources must allow it.
- Applications must handle SIGTERM, otherwise every redeploy waits for the full grace period.
