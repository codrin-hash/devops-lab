# IDP-2 verification

- Ticket: deploy endpoint, Redis queue, worker with git clone
- Status: Done
- Date: 2026-10-04
- Environment: WSL2 Ubuntu, Docker Engine (BuildKit, containerd image store)

## Acceptance criteria

| # | Criterion | Result | Evidence |
|---|-----------|--------|----------|
| 1 | `POST /apps/{id}/deploys` returns 202 with `queued`; unknown app returns 404 | Pass | 202 `queued`; 404 for `00000000-0000-0000-0000-000000000000` |
| 2 | Deployment reaches `building` with a SHA matching `git ls-remote` | Pass | `68c1b9f87c41fb3fef2667e27149865c2f42d1eb` from both; 1.28 s from request to `building` |
| 3 | Nonexistent repository fails with git stderr; worker survives | Pass | `could not read Username for 'https://github.com': terminal prompts disabled`; next deploy reached `building` |
| 4 | Nonexistent branch fails with a clear error | Pass | `Remote branch nope not found in upstream origin` |
| 5 | Clones present in the workspace volume | Pass | `/workspace/<deployment_id>`, owned by `idp` |
| 6 | Idle worker stops in under 2 s | Pass | 0.58 s (10.37 s before the fix); log shows `received SIGTERM` then `worker stopped` |
| 7 | Kill during clone leaves observable state | Documented | See [Crash during clone](#crash-during-clone) |
| 8 | No `on_event` deprecation warning | Pass | `grep -iE 'deprecat\|on_event'` empty; `Application startup complete` |

## Measurements

| Metric | Value |
|--------|-------|
| Request to `building`, small repository | 1.28 s |
| Idle worker stop, before / after fix | 10.37 s / 0.58 s |
| Platform image on disk, before / after git | 302 MB / 442 MB |
| Platform image compressed, before / after git | 72 MB / 107 MB |
| git layer | 105 MB |

## Crash during clone

`docker compose kill worker` (SIGKILL) while cloning `kubernetes/kubernetes`:

| Observation | Cause |
|-------------|-------|
| Deployment stays in `cloning`; `updated_at` frozen | SIGKILL skips `except` and `finally`; no further status update |
| Id remains in `idp:processing`; `idp:queue` empty | `BLMOVE` moved it atomically; `ack()` never ran |
| Partial `.git` left in `/workspace/<deployment_id>` | git killed with the container; `clone()` removes it on retry |
| Restarted worker does not pick the job up | Worker reads only `idp:queue`; nothing scans `idp:processing` |

The job is not lost, but it is not recovered either. Tracked as [GAP-001](../tech-debt.md#known-gaps).

## Issues found during implementation

| Symptom | Cause | Fix |
|---------|-------|-----|
| `pull access denied for idp/platform` | Worker uses `image:` without `build:`; Compose tries Docker Hub first | `pull_policy: never` |
| `exec: "CMD": executable file not found` | `CMD` marker copied from `healthcheck.test` into `command` | `command: ["python", "-m", "worker.main"]` |
| `No module named 'worker'` | `worker/` not copied into the image | `COPY worker/ worker/` |
| `No such file or directory: 'git'` | `python:3.12-slim` ships without git | apt install in a single layer |
| `Permission denied` on `/workspace` | Mount point created as root; worker runs as UID 10001 | Directory created in the image, owned by `idp` |
| `docker compose stop worker` takes 10 s | Python as PID 1 has no SIGTERM handler; signal dropped | SIGTERM handler, `init: true` ([ADR-0011](../adr/0011-worker-graceful-shutdown.md)) |
| API started before Postgres accepted connections | `depends_on` used `service_started` (IDP-1 regression) | `service_healthy` |
