# Documentation

| Section | Contents |
|---------|----------|
| [Architecture](architecture/) | [Overview](architecture/overview.md), [data model](architecture/data-model.md), [deployment flow](architecture/deployment-flow.md) |
| [Decisions](adr/README.md) | Architecture Decision Records |
| [Reference](reference/) | [API](reference/api.md), [application contract](reference/app-contract.md), [configuration](reference/configuration.md) |
| [Operations](operations/) | [Runbook](operations/runbook.md), [troubleshooting](operations/troubleshooting.md) |
| [Verification](verification/) | Acceptance results per ticket |
| [Tech debt](tech-debt.md) | Known debt and intentional gaps |

## Conventions

- Every ticket updates the affected docs in the same commit as the code.
- Every non-trivial decision gets an ADR. ADRs are immutable; a changed decision gets a new ADR that supersedes the old one.
- Every ticket gets a verification file with acceptance criteria and measured results.
- Planned components are marked as such until implemented.
