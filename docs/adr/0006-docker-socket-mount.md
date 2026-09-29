# ADR-0006: Worker reaches Docker through a mounted socket

- Status: Accepted, temporary
- Date: 2026-09-29

## Context

The worker runs in a container and must build images and run containers.

## Decision

Mount `/var/run/docker.sock` into the worker.

## Alternatives considered

- **Docker-in-Docker.** Requires a privileged container and a separate layer cache.
- **Worker on the host.** Leaves the compose project and breaks environment parity.

## Consequences

- Root-equivalent access for the worker ([TD-001](../tech-debt.md)).
- Replaced in stage 2 by rootless builds (Kaniko or BuildKit rootless).
