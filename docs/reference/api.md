# API reference

Base URL: `http://localhost:8000`. No authentication yet ([TD-003](../tech-debt.md)).

## Endpoints

| Method | Path | Success | Errors | Status |
|--------|------|---------|--------|--------|
| `GET` | `/healthz` | `200` | `503` when the database is unreachable | Implemented |
| `POST` | `/apps` | `201` | `409` duplicate name, `422` invalid input | Implemented |
| `GET` | `/apps` | `200` | — | Implemented |
| `GET` | `/apps/{id}` | `200` | `404` | Implemented |
| `POST` | `/apps/{id}/deploys` | `202` | `404` | Planned (IDP-2) |

## Register an application

```http
POST /apps
Content-Type: application/json

{"name": "hello", "repo_url": "https://github.com/org/repo", "branch": "main"}
```

```json
{"id": "…", "name": "hello", "repo_url": "https://github.com/org/repo", "branch": "main", "created_at": "…"}
```

## Validation

| Field | Rule | Reason |
|-------|------|--------|
| `name` | `^[a-z][a-z0-9-]{1,30}[a-z0-9]$` | Becomes a Kubernetes namespace and a hostname |
| `repo_url` | `https://` only | Schemes such as `file://` or `ext::` let `git clone` read or execute local resources |
| `branch` | 1–255 characters, default `main` | |
