# Runbook

Run all commands from `idp/`, in a WSL shell. PowerShell aliases `curl` and parses quotes differently.

## Lifecycle

| Task | Command |
|------|---------|
| Start or rebuild | `docker compose up -d --build` |
| Status, including exited containers | `docker compose ps -a` |
| Follow logs | `docker compose logs -f <service>` |
| Stop, keep data | `docker compose down` |
| Stop and delete data | `docker compose down -v` |
| Validate compose file | `docker compose config --quiet` |

## Inspection

| Task | Command |
|------|---------|
| Database shell | `docker compose exec postgres psql -U idp -d idp` |
| Postgres readiness | `docker compose exec postgres pg_isready -U idp -d idp` |
| PID 1 of a container | `docker compose exec <service> cat /proc/1/cmdline \| tr '\0' ' '` |
| Signal handlers of PID 1 | `docker compose exec <service> grep -E 'SigCgt\|SigBlk' /proc/1/status` |
| Processes, host view | `docker compose top <service>` |

## Queue and worker

| Task | Command |
|------|---------|
| Pending jobs | `docker compose exec redis redis-cli LRANGE idp:queue 0 -1` |
| Jobs in progress | `docker compose exec redis redis-cli LRANGE idp:processing 0 -1` |
| Deployment status | `curl -s localhost:8000/deploys/<id> \| jq` |
| Workspace content | `docker compose exec worker ls -la /workspace` |
| Workspace while worker is down | `docker compose run --rm --entrypoint ls worker -la /workspace` |

## Stuck deployment

A deployment that stays in `cloning` or `building` with no worker activity was interrupted by a crash (GAP-001). Check that its id is in `idp:processing`, then either retry or fail it.

Retry:

```bash
docker compose exec redis redis-cli LREM idp:processing 1 <id>
docker compose exec postgres psql -U idp -d idp -c "UPDATE deployments SET status='queued' WHERE id='<id>';"
docker compose exec redis redis-cli LPUSH idp:queue <id>
```

Fail:

```bash
docker compose exec redis redis-cli LREM idp:processing 1 <id>
docker compose exec postgres psql -U idp -d idp -c "UPDATE deployments SET status='failed', error='manually failed after worker crash' WHERE id='<id>';"
```

Only do this when no worker is processing the job. With a live worker the job would run twice.
