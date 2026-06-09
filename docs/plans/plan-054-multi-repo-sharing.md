# Plan: Multi Repo Sharing

## Metadata

- ID: plan-054-multi-repo-sharing
- Status: blocked
- Attractor: docs/architecture/attractors/abh-core-attractor.md
- Baseline: Support importing and exporting attractor and memory context across repositories.
- Owner: platform
- Created: 2026-06-06T13:42:47.679267+00:00
- Updated: 2026-06-08T02:37:11.466572+00:00

## Goals

- Add a local-first import/export surface for sharing ABH attractor and memory context between repositories.
- Represent exported context as repository-owned artifacts that can be inspected before import.
- Preserve active attractor, memory relationship metadata, and source-of-truth boundaries when context moves across repositories.
- Expose the sharing workflow through Agent-First command contracts and non-interactive JSON output.

## Non-Goals

- Do not build cloud sync, remote services, external databases, or background daemons in this slice.
- Do not implement team policy, release automation, package publishing, or branch protection.
- Do not silently overwrite local active attractors, memory records, or owner docs during import.
- Do not claim imported context is automatically trusted without local review and ABH evidence.

## Exit Criteria

- A user can export the active attractor and selected active memory context into a local bundle artifact.
- A user can preview importing a bundle in another repository and see conflicts, planned writes, and required confirmation.
- Confirmed imports preserve source repository metadata and avoid silent overwrite of existing local records.
- Command contracts, CLI JSON output, docs, and tests describe the local-first sharing boundary.

## Commitment Phase State

### Stable State Now

- ABH stores active attractor, memory, plans, audits, drift, and roadmap state as local repository files.
- Stage 7 CI templates are closed; multi-repo sharing has a defined plan but is blocked/deferred after independent audit found no R-flow implementation evidence.

### Active Change Pressure

- Repositories need a controlled way to reuse attractor and memory context without copying stale or unreviewed governance state by hand.

### Target Stable State

- ABH can export and preview/import selected attractor and memory context through local-first, confirmed workflows.

### Conversion Proof

- Tests and docs show export, preview import, conflict handling, and confirmed import behavior without bypassing ABH source-of-truth rules.

### Residual Pressure

- Trust semantics for imported context remain local and review-based; team-wide policy and release automation stay queued for a later Stage 7 slice. | Non-blocking rationale: This slice can define local sharing mechanics without making imported context authoritative across teams.

## Validation Checklist

- git diff --check
- .venv\\Scripts\\python.exe -m unittest discover -v
- .venv\\Scripts\\python.exe -m abh doctor --json
- .venv\\Scripts\\python.exe -m abh roadmap check --json
- .venv\\Scripts\\python.exe -m abh next --json

## Closure Evidence

- abh/commands.py
- abh/cli.py
- abh/models.py
- abh/storage.py
- tests/
- README.md
- docs/development-roadmap.md
- docs/task-board.md
- docs/context/codebase-map.md

## Verification Runs

- ver-0f5cac0555aa
- ver-9279d3bb35df

## Audits

- audit-054-multi-repo-sharing
