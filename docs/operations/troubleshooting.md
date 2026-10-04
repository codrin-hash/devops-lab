# Troubleshooting

## `no configuration file provided: not found`

**Cause:** the command was run outside `idp/`.

## A service is missing from `docker ps`

**Cause:** the container started and exited.
**Check:** `docker compose ps -a` shows the exit code, and `docker compose logs <service>` shows the reason.

## `ModuleNotFoundError: No module named 'app'`

**Cause:** wrong uvicorn target. The format is `<module>:<variable>`, relative to `WORKDIR`.
**Fix:** use `api.main:app`.

## `docker stop` takes about 10 seconds

**Cause:** the app process does not receive SIGTERM, typically because of a shell-form `CMD` (`sh` becomes PID 1 and does not forward signals). Docker then waits for the grace period and sends SIGKILL.
**Check:** `docker compose exec <service> cat /proc/1/cmdline | tr '\0' ' '`
**Fix:** use exec-form `CMD ["python3", "-m", "uvicorn", ...]`.

## `ps: executable file not found`

**Cause:** slim images do not ship `procps`.
**Fix:** use `/proc/1/cmdline` or `docker compose top`. Do not add debug tools to runtime images.

## PIDs differ between `docker compose top` and the container

**Cause:** PID namespace. `top` shows host PIDs, while inside the container the same process is PID 1. Its host parent is `containerd-shim`.

## `healthcheck.test must start either by "CMD", "CMD-SHELL" or "NONE"`

**Cause:** `test` is empty or lacks the executor prefix.
- `CMD` runs without a shell, so there is no variable expansion.
- `CMD-SHELL` runs through `/bin/sh -c`. Use `$$VAR` to defer expansion from Compose to the container.

## Container exits with `exec: "CMD": executable file not found`

`command` in compose is the argv of the process; the first element is the executable. `CMD` and `CMD-SHELL` are type markers valid only in `healthcheck.test`, where Docker interprets them (`CMD`: exec directly, `CMD-SHELL`: run via `/bin/sh -c`, `NONE`: disable).

## `docker compose stop worker` takes 10 s

PID 1 in a PID namespace does not receive signals it has no handler for. Python installs a handler only for SIGINT, so SIGTERM is dropped and Docker sends SIGKILL after the grace period. Check with `grep SigCgt /proc/1/status` (SIGTERM is bit `0x4000`). Fixed by a SIGTERM handler in the worker and `init: true` in compose.
