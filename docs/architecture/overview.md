# Architecture overview — Stage 1

## Scope

Stage 1 runs locally on Docker Engine. No Kubernetes, no UI.

**Exit criterion:** an application registered through the API is running and serving on a host port within seconds of a deploy request.

## System context

```mermaid
flowchart LR
    dev([Developer])

    subgraph compose["docker compose: idp"]
        api["api<br/>FastAPI"]
        pg[("postgres")]
        redis[("redis")]
        worker["worker"]
    end

    engine["Docker Engine"]
    app["app container<br/>idp/APP:SHA"]

    dev -->|"HTTP :8000"| api
    api -->|state| pg
    api -->|enqueue id| redis
    redis -->|BLMOVE| worker
    worker -->|status| pg
    worker -->|docker.sock| engine
    engine -->|build + run| app
    dev -->|"HTTP :ephemeral"| app

    classDef planned stroke-dasharray: 5 5
    class worker,engine,app planned
```

Dashed: planned.

## Components

| Component | Responsibility | Exposure | Docker access | Status |
|-----------|----------------|----------|---------------|--------|
| api | Accepts requests, persists state, enqueues jobs | Host `:8000` | No | Implemented |
| worker | Consumes jobs: clone, build, run, health check | None | Yes, via socket | Planned |
| postgres | Source of truth for apps and deployments | Internal network | — | Implemented |
| redis | Job transport; later, log streams | Internal network | — | Implemented |
| app container | User workload, created by the worker outside the compose project | Host, ephemeral port | — | Planned |

`api` and `worker` share one image with different entrypoints.

## Trust boundaries

- `api` is the only network-facing platform component and holds no Docker privileges ([ADR-0005](../adr/0005-docker-access-worker-only.md)).
- `worker` holds root-equivalent access to the host through `docker.sock` ([ADR-0006](../adr/0006-docker-socket-mount.md), [TD-001](../tech-debt.md)).
- `postgres` and `redis` publish no host ports.
- Platform containers run as non-root (UID 10001).
- User input reaching `git clone` is restricted to `https://` URLs ([API reference](../reference/api.md#validation)).

## Storage

| Data | Location | Reason |
|------|----------|--------|
| Source code | `/mnt/c/...` (Windows filesystem) | Read only at build time |
| Postgres data | Named volume `pgdata` | ext4 inside WSL; `/mnt/c` is slow and unreliable for fsync-heavy workloads |
| Worker workspace | Named volume (planned) | Same as above |

The worker must not create bind mounts for app containers: paths passed through `docker.sock` resolve on the host, not inside the worker container.
