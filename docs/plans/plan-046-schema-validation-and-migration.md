# Plan: Schema Validation and Migration

## Metadata

- ID: plan-046-schema-validation-and-migration
- Status: closed
- Attractor: docs/architecture/attractors/abh-core-attractor.md
- Baseline: Current dataclass from_dict paths provide backward-compatible defaults for some fields, while doctor mainly checks schema_version presence and doc pairing. Future fields need a clearer validation and migration boundary.
- Owner: platform
- Created: 2026-06-05T00:47:26.962069+00:00
- Updated: 2026-06-05T01:19:30.314330+00:00

## Goals

- Add version-aware validation helpers for core ABH record types.
- Define how unknown fields, missing required fields, and deprecated fields are handled.
- Expose validation failures through doctor without breaking legacy readable records unnecessarily.
- Document schema migration rules for future Stage 6 and Stage 7 fields.

## Non-Goals

- Do not require a third-party schema library in the first slice.
- Do not migrate every historical object unless the validation rules require it.
- Do not change user-facing command output shape except for clearer doctor issues.

## Exit Criteria

- Record validation helpers exist for the core object families.
- Doctor can report malformed records with actionable categories.
- Legacy valid records remain readable.
- Tests cover missing fields, unknown fields, and schema_version handling.

## Validation Checklist

- python3 -m unittest tests/test_cli.py -v
- python3 -m abh doctor
- git diff --check
- python3 -m abh roadmap check --json

## Closure Evidence

- abh/models.py
- abh/core.py
- tests/test_cli.py
- docs/development-roadmap.md
- docs/task-board.md
- docs/superpowers/plans/2026-06-05-schema-validation-and-migration.md
- abh/roadmap.py
- audit-046-schema-validation-and-migration-r2

## Verification Runs

- ver-e0541e7abf40
- ver-d4be20596e20

## Audits

- audit-046-schema-validation-and-migration
- audit-046-schema-validation-and-migration-r2
