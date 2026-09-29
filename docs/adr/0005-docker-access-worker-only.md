# ADR-0005: Docker access restricted to the worker

- Status: Accepted
- Date: 2026-09-29

## Context

`docker.sock` has no fine-grained permissions. Access to it is equivalent to root on the host.

## Decision

Only the worker mounts the socket. The API never talks to Docker. Reads that need Docker, such as logs, go through the worker: it tails container logs into Redis Streams, and the API reads from Redis.

## Alternatives considered

- **API with direct socket access.** Simpler reads, but any API vulnerability becomes host compromise.

## Consequences

- The network-facing component is unprivileged.
- Synchronous reads need an intermediate store.
- On Kubernetes this constraint relaxes: the API can get a ServiceAccount with minimal RBAC (`get pods/log`). To be revisited in stage 2.
