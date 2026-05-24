# Plan: Atomic ABH Writes

## Metadata

- ID: plan-023-atomic-abh-writes
- Status: closed
- Attractor: docs/architecture/attractors/abh-core-attractor.md
- Baseline: Stage 3 dogfood found ABH can corrupt JSON/Markdown when multiple write commands target related records concurrently; storage currently writes files directly with Path.write_text.
- Owner: platform
- Created: 2026-05-24T12:57:16.393294+00:00
- Updated: 2026-05-24T13:27:55.603925+00:00

## Goals

- Make ABH JSON and Markdown writes atomic at the single-file level so interrupted writes do not leave partial files.
- Add per-file lock protection around ABH writes to reduce same-file concurrent writer corruption across local processes.
- Route plan, audit, memory, drift, and verification persistence through the shared safe write helpers.
- Keep existing CLI output, JSON schema, plan state machine, verification semantics, and doctor behavior compatible.

## Non-Goals

- Do not implement CI execution, isolated verification, distributed locking, stale gate enforcement, or close gate changes in this slice.
- Do not redesign storage layout or introduce external runtime dependencies.
- Do not make multi-file JSON/Markdown object saves transactional across files.

## Exit Criteria

- write_json writes via an atomic temp-file replace and leaves the previous file intact if replacement fails before commit.
- ABH text/Markdown writes use the same atomic write helper instead of direct Path.write_text in save paths.
- Concurrent same-file write attempts are serialized by a local lock file and no .tmp/.lock files remain after successful writes.
- plan/audit/memory/drift/verification save paths continue to produce JSON and Markdown accepted by abh doctor.
- python3 -m unittest tests/test_cli.py -v passes.
- python3 -m abh doctor passes.

## Validation Checklist

- python3 -m unittest tests/test_cli.py -v
- python3 -m abh doctor

## Closure Evidence

- tests/test_cli.py atomic write coverage
- abh/storage.py
- docs synchronized for plan-023
- .abh/verifications/ver-3d44705cc11c.json
- docs/plans/plan-023-atomic-abh-writes.md
- .abh/verifications/ver-eca84c85ac93.json
- audit-023-atomic-abh-writes

## Verification Runs

- ver-3d44705cc11c
- ver-eca84c85ac93
- ver-a0fa5d1ef738
- ver-889f8cddf60c
- ver-a67d48470745

## Audits

- audit-023-atomic-abh-writes
