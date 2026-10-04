# Troubleshooting

## `no configuration file provided: not found`

**Cause:** the command was run outside `idp/`.

## A service is missing from `docker ps`

**Cause:** the container started and exited.
**Check:** `docker compose ps -a` shows the exit code, and `docker compose logs <service>` shows the reason.

## `ModuleNotFoundError: No module named 'app'`

**Cause:** wrong uvicorn target. The format is `<module>:<variable>`, relative to `WORKDIR`.
**Fix:** use `api.main:app`.

## `No module named 'worker'`

**Cause:** the package is not copied into the image.
**Check:** `docker compose run --rm --entrypoint ls api /app`
**Fix:** `COPY worker/ worker/` in the Dockerfile.

## Container exits with `exec: "CMD": executable file not found`

**Cause:** `command` in compose is the argv of the process; the first element is the executable. `CMD` and `CMD-SHELL` are type markers valid only in `healthcheck.test`, where Docker interprets them (`CMD`: exec directly, `CMD-SHELL`: run via `/bin/sh -c`, `NONE`: disable).
**Fix:** `command: ["python", "-m", "worker.main"]`.

## `pull access denied for idp/platform`

**Cause:** a service with `image:` and no `build:` is pulled before the build runs. `idp/platform` resolves to `docker.io/idp/platform`.
**Fix:** `pull_policy: never` on services that reuse the locally built image. Without it, an image published under that name on Docker Hub would be pulled.

## `docker stop` takes about 10 seconds

**Cause:** the process does not handle SIGTERM. Either a shell-form `CMD` makes `sh` PID 1, which does not forward signals, or PID 1 has no SIGTERM handler: the kernel drops signals with default disposition for a namespace init process. Docker then waits for the grace period and sends SIGKILL.
**Check:**
- `docker compose exec <service> cat /proc/1/cmdline | tr '\0' ' '`
- `docker compose exec <service> grep SigCgt /proc/1/status`; SIGTERM is bit `0x4000`
**Fix:** exec-form `CMD`, plus a SIGTERM handler in the process or `init: true`.

## Deployment fails with `FileNotFoundError: ... 'git'`

**Cause:** `python:3.12-slim` ships without git.
**Fix:** install git in the image (`apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*`, in one `RUN`).

## Deployment fails with `could not create work tree dir ... Permission denied`

**Cause:** `/workspace` does not exist in the image, so the mount point is created as root; the worker runs as UID 10001.
**Check:** `docker compose exec worker ls -ld /workspace`
**Fix:** create the directory in the image, owned by `idp`, before `USER`. If the volume already exists with root ownership, remove it: `docker compose down && docker volume rm idp_workspace`.

## Deployment fails with `could not read Username for 'https://github.com'`

**Cause:** the repository does not exist or is private. GitHub answers both by requesting credentials, and the worker disables prompts (`GIT_TERMINAL_PROMPT=0`).
**Fix:** check `repo_url`. Private repositories are not supported yet.

## Deployment stuck in `cloning` or `building`

**Cause:** the worker was killed while processing the job (GAP-001).
**Fix:** see [Stuck deployment](runbook.md#stuck-deployment).
