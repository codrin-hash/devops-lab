# ADR-0007: Host ports assigned by Docker

- Status: Accepted
- Date: 2026-09-29

## Context

Each app container needs a reachable host port without collisions.

## Decision

Publish the container port without a fixed host port. Read the assigned port from `inspect` and store it in `deployments.host_port`.

## Alternatives considered

- **Platform-managed port pool.** Reimplements what Docker already does.
- **Traefik with hostname routing** (`<app>.localhost`). Closer to Kubernetes Ingress. Deferred.

## Consequences

- The port changes on every deploy.
- There is no stable URL until a reverse proxy or Ingress is introduced.
