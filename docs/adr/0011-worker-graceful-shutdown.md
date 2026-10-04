# ADR-0011: Worker graceful shutdown

- Status: Accepted
- Date: 2026-10-04

## Context

The worker ran as PID 1 with exec-form `command`, yet `docker compose stop worker` took 10.37 s. Python installs a handler only for SIGINT (`SigCgt` 0x2). The kernel does not deliver signals with default disposition to the init process of a PID namespace, so SIGTERM was dropped and Docker sent SIGKILL after the grace period. A killed worker leaves its job stuck (GAP-001).

The worker also spawns git, which spawns helpers such as `git-remote-https`. If git is killed on timeout, the helpers are orphaned and reparented to PID 1, which does not reap them.

## Decision

- SIGTERM and SIGINT set a stop flag. The worker finishes the current job, acknowledges it, and exits.
- `init: true`: tini runs as PID 1, forwards signals, and reaps orphans.
- `stop_grace_period: 30s`.

## Alternatives considered

- **`init: true` only.** Stops instantly, but the default SIGTERM action kills the worker mid-job.
- **Handler only.** Graceful, but orphaned processes become zombies.
- **Grace period equal to the longest job** (120 s clone, minutes of build in IDP-3). Every `docker compose down` with a running job would wait that long.

## Consequences

- Idle stop takes about 0.6 s.
- Jobs longer than 30 s are killed on stop and stay stuck until GAP-001 is resolved ([TD-007](../tech-debt.md)).
- The same mechanism applies on Kubernetes: SIGTERM, then SIGKILL after `terminationGracePeriodSeconds`.
