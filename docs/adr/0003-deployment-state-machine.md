# ADR-0003: Explicit deployment state machine

- Status: Accepted
- Date: 2026-09-29

## Context

A deployment spans several slow, failure-prone steps. Operators need to see where it is and where it failed.

## Decision

`queued → cloning → building → starting → running`, with `failed` reachable from any active state. The status is a Postgres enum, and each transition updates `updated_at`.

## Alternatives considered

- **Boolean `done` flag or free-text status.** No enforced vocabulary and no measurable phases.

## Consequences

- Per-phase durations become measurable, which feeds stage 4 metrics.
- Adding a state requires a schema change.
