# Application contract

Requirements for a repository deployed on IDP.

| Requirement | Detail |
|-------------|--------|
| Dockerfile | At repository root |
| Listen address | `0.0.0.0`. `localhost` is unreachable from outside the container |
| Port | Read from `$PORT`. The platform sets `8000` |
| Shutdown | Exit on SIGTERM within the grace period. The app process must be PID 1 (exec-form `CMD`) or run under an init that forwards signals |

Rationale: [ADR-0004](../adr/0004-app-contract.md).
