# Configuration

## Environment variables

| Variable | Consumer | Defined in |
|----------|----------|------------|
| `POSTGRES_USER` | postgres, compose interpolation | `.env` |
| `POSTGRES_PASSWORD` | postgres, compose interpolation | `.env` |
| `POSTGRES_DB` | postgres, compose interpolation | `.env` |
| `DATABASE_URL` | api, worker | `compose.yaml`, built from `POSTGRES_*` |
| `REDIS_URL` | api, worker | `compose.yaml` |
| `WORKSPACE_DIR` | worker | Default `/workspace` in `common/config.py` |

`.env` is excluded from git and from the build context. `.env.example` is the committed template.

## Two mechanisms, one file

- `${VAR}` in `compose.yaml` is interpolated by Compose on the host, from `.env` next to the file.
- `env_file: .env` injects the variables into the container environment.

## Worker settings

| Setting | Value | Location | Reason |
|---------|-------|----------|--------|
| `command` | `python -m worker.main` | `compose.yaml` | Same image as api, different entrypoint |
| `init` | `true` | `compose.yaml` | tini as PID 1: signal forwarding, orphan reaping |
| `stop_grace_period` | `30s` | `compose.yaml` | Drain window on stop ([ADR-0011](../adr/0011-worker-graceful-shutdown.md)) |
| `pull_policy` | `never` | `compose.yaml` | Image is built locally by the api service |
| `CLONE_TIMEOUT` | 120 s | `worker/main.py` | Upper bound for `git clone` |
| Dequeue timeout | 1 s | `common/queue.py` | Bounds the time to notice a stop request |

## Redis keys

| Key | Type | Content |
|-----|------|---------|
| `idp:queue` | list | Deployment ids waiting to be processed |
| `idp:processing` | list | Deployment ids taken by a worker and not yet acknowledged |
