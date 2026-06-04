# Plan: Repository Write Transaction Boundary

## Metadata

- ID: plan-045-repository-write-transaction-boundary
- Status: closed
- Attractor: docs/architecture/attractors/abh-core-attractor.md
- Baseline: ABH has per-file atomic writes and local file locks, but plan, audit, memory, drift, and attractor saves still write Markdown and JSON as separate operations. Doctor can detect split state after the fact, but the write boundary itself is not transactional.
- Owner: platform
- Created: 2026-06-04T10:50:57.111020+00:00
- Updated: 2026-06-04T12:32:40.819735+00:00

## Goals

- Design a shared repository write helper for JSON/Markdown pairs.
- Apply the helper to plan, audit, memory, drift, and attractor save paths.
- Add failure-mode tests that prove partial writes are detected or avoided.
- Document the transaction boundary and remaining local-filesystem assumptions.
- Record the scheduling prerequisite for re-planning plan-043: blocked/deferred plans do not prevent materializing the next queued roadmap item.

## Non-Goals

- Do not introduce an external database, background service, or remote lock manager.
- Do not change ABH object schemas in this slice.
- Do not rewrite historical records unless a migration is explicitly planned.

## Exit Criteria

- Core ABH object save paths use a shared write-pair boundary.
- Tests cover representative JSON/Markdown partial-write failure scenarios.
- Doctor remains clean on the current repository.
- Docs explain what consistency the local write boundary guarantees.
- abh next recommends the next queued roadmap item when the only older open plans are blocked/deferred.

## Validation Checklist

- python3 -m unittest tests/test_cli.py -v
- python3 -m abh doctor
- git diff --check
- python3 -m abh roadmap check --json

## Closure Evidence

- abh/storage.py
- abh/plans.py
- abh/audits.py
- abh/memory.py
- abh/drift.py
- abh/attractors.py
- tests/test_cli.py
- docs/development-roadmap.md
- docs/task-board.md
- docs/superpowers/plans/2026-06-04-repository-write-transaction-boundary.md
- abh/navigation.py
- audit-045-repository-write-transaction-boundary-r2

## Verification Runs

- ver-60c4c288037e
- ver-3f470aa8d592

## Audits

- audit-045-repository-write-transaction-boundary
- audit-045-repository-write-transaction-boundary-r2
