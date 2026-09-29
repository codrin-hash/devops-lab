# Configuration

| Variable | Consumer | Defined in |
|----------|----------|------------|
| `POSTGRES_USER` | postgres, compose interpolation | `.env` |
| `POSTGRES_PASSWORD` | postgres, compose interpolation | `.env` |
| `POSTGRES_DB` | postgres, compose interpolation | `.env` |
| `DATABASE_URL` | api | `compose.yaml`, built from `POSTGRES_*` |
| `REDIS_URL` | api | `compose.yaml` |

`.env` is excluded from git and from the build context. `.env.example` is the committed template.

## Two mechanisms, one file

- `${VAR}` in `compose.yaml` is interpolated by Compose on the host, from `.env` next to the file.
- `env_file: .env` injects the variables into the container environment.
