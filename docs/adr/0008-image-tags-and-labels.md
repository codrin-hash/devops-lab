# ADR-0008: Commit-based image tags, label-based discovery

- Status: Accepted
- Date: 2026-09-29

## Context

Deploys must be reproducible, and the platform must find its own containers reliably.

## Decision

- Images are tagged `idp/<app>:<git-sha>`.
- Containers carry the labels `idp.app_id` and `idp.deployment_id`.

## Alternatives considered

- **`latest` tag.** Not reproducible, and rollback is ambiguous.
- **Name-based discovery.** Fragile under renames and collisions.

## Consequences

- Rollback means redeploying an existing tag.
- Old images accumulate, so a cleanup policy is required later.
