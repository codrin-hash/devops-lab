# Tech debt and known gaps

## Tech debt

Accepted shortcuts with a planned fix.

| ID | Item | Risk | Planned fix |
|----|------|------|-------------|
| TD-001 | `docker.sock` mounted in the worker | High: host root if the worker is compromised | Stage 2: rootless builds |
| TD-002 | `create_all`, no migrations | Medium: schema changes do not apply to an existing database | Alembic at the first schema change |
| TD-003 | No API authentication | High: anyone with port access can deploy | Stage 5 |
| TD-004 | Static credentials in `.env` | Medium: no rotation | Stage 5: Vault |
| TD-005 | Deprecated `@app.on_event("startup")` | Low | IDP-2: migrate to `lifespan` |

## Known gaps

Unhandled failure modes, left open on purpose.

| ID | Gap |
|----|-----|
| GAP-001 | Jobs stuck in `idp:processing`, or deployments stuck in `cloning` or `building`, after a worker crash |
| GAP-002 | Concurrent deploys of the same application |
| GAP-003 | No limits on build duration, image size or container resources |
