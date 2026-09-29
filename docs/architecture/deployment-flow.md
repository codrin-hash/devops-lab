# Deployment flow

Status: planned (IDP-2, IDP-3).

```mermaid
sequenceDiagram
    actor Dev as Developer
    participant API
    participant PG as Postgres
    participant R as Redis
    participant W as Worker
    participant D as Docker Engine

    Dev->>API: POST /apps/{id}/deploys
    API->>PG: INSERT deployment (queued)
    API->>R: LPUSH idp:queue {deployment_id}
    API-->>Dev: 202 Accepted

    W->>R: BLMOVE idp:queue → idp:processing
    W->>PG: status = cloning
    W->>W: git clone --depth 1
    W->>PG: status = building, commit_sha
    W->>D: build idp/{app}:{sha}
    W->>PG: status = starting
    W->>D: run (labels, ephemeral port)
    W->>D: inspect → host port
    W->>W: health check
    W->>PG: status = running, host_port
    W->>D: stop previous container
    W->>R: LREM idp:processing {deployment_id}
```

## Delivery semantics

- **At-least-once.** A job is removed from `idp:processing` only after completion. A worker crash in between causes reprocessing, so every step must be idempotent ([ADR-0002](../adr/0002-redis-reliable-queue.md)).
- **Build context.** Sent to the engine as a tarball through the Docker SDK. No shared filesystem between the worker and the engine is required.

## Redeploy

The new container must pass its health check before the previous one is stopped. The stop sends SIGTERM, then SIGKILL after the grace period ([ADR-0009](../adr/0009-start-before-stop-redeploy.md)).
