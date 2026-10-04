# API reference

Base URL: `http://localhost:8000`. No authentication yet ([TD-003](../tech-debt.md)).

## Endpoints

| Method | Path | Success | Errors | Status |
|--------|------|---------|--------|--------|
| `GET` | `/healthz` | `200` | `503` when the database is unreachable | Implemented |
| `POST` | `/apps` | `201` | `409` duplicate name, `422` invalid input | Implemented |
| `GET` | `/apps` | `200` | — | Implemented |
| `GET` | `/apps/{id}` | `200` | `404` | Implemented |
| `POST` | `/apps/{id}/deploys` | `202` | `404` unknown app, `422` invalid id | Implemented |
| `GET` | `/apps/{id}/deploys` | `200` | `404` unknown app | Implemented |
| `GET` | `/deploys/{id}` | `200` | `404` | Implemented |

## Register an application

```http
POST /apps
Content-Type: application/json

{"name": "hello", "repo_url": "https://github.com/org/repo", "branch": "main"}
```

```json
{"id": "…", "name": "hello", "repo_url": "https://github.com/org/repo", "branch": "main", "created_at": "…"}
```

## Deploy an application

```http
POST /apps/{id}/deploys
```

Returns `202 Accepted` once the deployment is persisted and enqueued. Processing is asynchronous; poll `GET /deploys/{id}`.

```json
{
  "id": "…",
  "app_id": "…",
  "status": "queued",
  "commit_sha": null,
  "image": null,
  "host_port": null,
  "error": null,
  "created_at": "…",
  "updated_at": "…"
}
```

| Field | Set when |
|-------|----------|
| `status` | Every transition, see [state machine](../architecture/data-model.md#deployment-state-machine) |
| `commit_sha` | After clone |
| `image`, `host_port` | After run (IDP-3) |
| `error` | On `failed`: git stderr or `<ExceptionType>: <message>`, truncated to 2000 characters |

In IDP-2 the pipeline stops at `building`. Build and run are added in IDP-3.

`GET /apps/{id}/deploys` returns deployments newest first.

## Validation

| Field | Rule | Reason |
|-------|------|--------|
| `name` | `^[a-z][a-z0-9-]{1,30}[a-z0-9]$` | Becomes a Kubernetes namespace and a hostname |
| `repo_url` | `https://` only | Schemes such as `file://` or `ext::` let `git clone` read or execute local resources |
| `branch` | 1–255 characters, default `main` | Passed as `--branch=<value>`, so a leading `-` cannot be parsed as an option |

GitHub answers a nonexistent repository and a private one identically, by requesting credentials. Both fail with `could not read Username`.
