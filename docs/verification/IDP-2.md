# IDP-2 verification

Status: in progress

| # | Criterion | Result | Evidence |
|---|-----------|--------|----------|
| 1 | Deploy returns 202 `queued`; unknown app returns 404 | Pass | |
| 2 | `building` with SHA matching `git ls-remote` | Pass | `68c1b9f8`, 1.28 s from request to `building` |
| 3 | Nonexistent repo fails with git stderr, worker survives | Pass | GitHub asks for credentials; private and nonexistent repos are indistinguishable |
| 4 | Nonexistent branch fails with clear error | Pass | `Remote branch nope not found` |
| 5 | Clones present in workspace volume | Pass | |
| 6 | Idle worker stops in under 2 s | Pass | 0.58 s (was 10.37 s); tini as PID 1, SIGTERM handled with drain |
| 7 | Kill during clone leaves observable state (GAP-001) | Documented | Deployment stuck in `cloning`; id left in `idp:processing`; partial `.git` in workspace; restarted worker does not recover the job |
| 8 | No `on_event` deprecation warning | Pass | |

## Issues found during implementation

| Symptom | Cause | Fix |
|---------|-------|-----|
| `No module named 'worker'` | `worker/` not copied into the image | `COPY worker/ worker/` |
| `No such file or directory: 'git'` | `python:3.12-slim` ships without git | apt install; image 302 MB to 442 MB (+105 MB layer) |
| `Permission denied` on `/workspace` | Mount point created as root; worker runs as UID 10001 | Directory pre-created in image, owned by `idp` |
| `pull access denied for idp/platform` | Worker has `image:` only; compose tries Docker Hub | `pull_policy: never` |