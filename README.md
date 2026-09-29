# IDP — Internal Developer Platform

A self-hosted, Heroku-style platform: register a Git repository, get a running application.
Built incrementally, from a local Docker core to a Kubernetes platform with GitOps.

```
git repo → API → queue → worker → clone → build → run → URL
```

## Roadmap

| Stage | Scope | Status |
|-------|-------|--------|
| 1 | Local core: FastAPI, worker, Postgres, Redis, Docker | In progress |
| 2 | Kubernetes (k3s), namespace per application | Planned |
| 3 | Infrastructure as code: Terraform, Helm | Planned |
| 4 | Observability: Prometheus, Grafana, logs | Planned |
| 5 | Security: image scanning, policies, Vault, tenant isolation | Planned |
| 6 | GitOps, CI/CD, preview environments | Planned |

## Quick start

```bash
cp .env.example .env
docker compose up -d --build
curl -X POST localhost:8000/apps -H 'Content-Type: application/json' \
  -d '{"name":"hello","repo_url":"https://github.com/docker/welcome-to-docker"}'
```

## Documentation

Start at [docs/](docs/readme.md).