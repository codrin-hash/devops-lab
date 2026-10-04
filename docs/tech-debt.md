# Tech debt and known gaps

## Tech debt

| ID | Item | Risk | Planned fix |
|----|------|------|-------------|
| TD-001 | `docker.sock` mounted in the worker (from IDP-3) | High: host root if the worker is compromised | Stage 2: rootless builds |
| TD-002 | `create_all`, no migrations | Medium: schema changes do not apply to an existing database | Alembic at the first schema change |
| TD-003 | No API authentication | High: anyone with port access can deploy | Stage 5 |
| TD-004 | Static credentials in `.env` | Medium: no rotation | Stage 5: Vault |
| TD-006 | Shared image ships git to the api container | Low: +105 MB and a larger attack surface on the network-facing service | Multi-stage build with `api` and `worker` targets |
| TD-007 | `stop_grace_period` (30 s) shorter than `CLONE_TIMEOUT` (120 s) | Medium: long jobs are killed on stop and stay stuck | Lease-based recovery (GAP-001); revisit with build timeouts in IDP-3 |

## Resolved

| ID | Item | Resolved in |
|----|------|-------------|
| TD-005 | Deprecated `@app.on_event("startup")` | IDP-2: migrated to `lifespan` |

## Known gaps

Unhandled failure modes, left open on purpose.

| ID | Gap |
|----|-----|
| GAP-001 | Jobs stuck in `idp:processing`, and deployments stuck in `cloning` or `building`, after a worker crash. Reproduced in [IDP-2 verification](verification/IDP-2.md#crash-during-clone) |
| GAP-002 | Concurrent deploys of the same application |
| GAP-003 | No limits on build duration, image size or container resources |
| GAP-004 | Workspace clones are never removed; disk usage grows with every deployment |
