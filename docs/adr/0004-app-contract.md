# ADR-0004: Application contract — Dockerfile and `$PORT`

- Status: Accepted
- Date: 2026-09-29

## Context

The platform must build and run arbitrary repositories without language-specific logic.

## Decision

Repositories provide a `Dockerfile` at the root. Applications listen on `0.0.0.0:$PORT`. Full contract: [reference/app-contract.md](../reference/app-contract.md).

## Alternatives considered

- **Cloud Native Buildpacks.** Language detection without a Dockerfile. Deferred, as it adds complexity without teaching value at this stage.

## Consequences

- The platform stays language-agnostic.
- Users must write a correct Dockerfile, including signal handling.
