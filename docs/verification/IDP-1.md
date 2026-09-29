# IDP-1 — Platform skeleton and app registration

- Status: Done
- Date: 2026-09-29

## Acceptance criteria

| # | Criterion | Expected | Result |
|---|-----------|----------|--------|
| 1 | Register a valid app | `201` | Pass |
| 2 | Register a duplicate name | `409` | Pass |
| 3 | Invalid name or non-https URL | `422` | Pass |
| 4 | List apps; get an unknown id | `200`; `404` | Pass |
| 5 | Data survives `down` + `up` | App still listed | Pass |
| 6 | `/healthz` with Postgres up and down | `200` / `503` | Pass |
| 7 | `docker compose stop api` | Under 1 s | Pass (0.67 s) |

## Commands

```bash
curl -i -X POST localhost:8000/apps -H 'Content-Type: application/json' \
  -d '{"name":"hello","repo_url":"https://github.com/docker/welcome-to-docker"}'   # 1, then 2
curl -i -X POST localhost:8000/apps -H 'Content-Type: application/json' \
  -d '{"name":"Hello_App","repo_url":"https://github.com/x/y"}'                    # 3
curl -i -X POST localhost:8000/apps -H 'Content-Type: application/json' \
  -d '{"name":"hello2","repo_url":"http://github.com/x/y"}'                        # 3
curl -s localhost:8000/apps                                                         # 4
curl -i localhost:8000/apps/00000000-0000-0000-0000-000000000000                    # 4
docker compose down && docker compose up -d && curl -s localhost:8000/apps          # 5
docker compose stop postgres && curl -i localhost:8000/healthz                      # 6
docker compose start postgres
time docker compose stop api                                                        # 7
```
