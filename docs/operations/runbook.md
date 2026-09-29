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

## Inspection

| Task | Command |
|------|---------|
| Database shell | `docker compose exec postgres psql -U idp -d idp` |
| Postgres readiness | `docker compose exec postgres pg_isready -U idp -d idp` |
| PID 1 of a container | `docker compose exec <service> cat /proc/1/cmdline \| tr '\0' ' '` |
| Processes, host view | `docker compose top <service>` |
