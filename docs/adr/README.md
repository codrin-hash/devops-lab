# Architecture Decision Records

| ADR | Decision | Status |
|-----|----------|--------|
| [0001](0001-postgres-source-of-truth.md) | Postgres is the source of truth, Redis is transport | Accepted |
| [0002](0002-redis-reliable-queue.md) | Custom reliable queue on Redis lists | Accepted |
| [0003](0003-deployment-state-machine.md) | Explicit deployment state machine | Accepted |
| [0004](0004-app-contract.md) | Application contract: Dockerfile and `$PORT` | Accepted |
| [0005](0005-docker-access-worker-only.md) | Docker access restricted to the worker | Accepted |
| [0006](0006-docker-socket-mount.md) | Worker reaches Docker through a mounted socket | Accepted, temporary |
| [0007](0007-docker-assigned-ports.md) | Host ports assigned by Docker | Accepted |
| [0008](0008-image-tags-and-labels.md) | Commit-based image tags, label-based discovery | Accepted |
| [0009](0009-start-before-stop-redeploy.md) | Start-before-stop redeploy | Accepted |
| [0010](0010-persist-before-enqueue.md) | Persist before enqueue | Accepted |
| [0011](0011-worker-graceful-shutdown.md) | Worker graceful shutdown | Accepted |

## Template

```markdown
# ADR-NNNN: Title

- Status: Proposed | Accepted | Superseded by ADR-NNNN
- Date: YYYY-MM-DD

## Context
## Decision
## Alternatives considered
## Consequences
```
