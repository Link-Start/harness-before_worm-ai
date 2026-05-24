# Plan: Memory Drift Routing Module Split

## Metadata

- ID: plan-024-memory-drift-routing-module-split
- Status: closed
- Attractor: docs/architecture/attractors/abh-core-attractor.md
- Baseline: Stage 3 core module split has moved plan, audit, verification, and shared errors out of core.py; memory, drift, and routing behavior still live in core.py and keep the module larger than its intended orchestration role.
- Owner: platform
- Created: 2026-05-24T13:35:16.531231+00:00
- Updated: 2026-05-24T13:51:38.793791+00:00

## Goals

- Move memory behavior from core.py into a focused abh/memory.py module while preserving abh.core compatibility exports.
- Move drift behavior from core.py into a focused abh/drift.py module while preserving CLI and MCP behavior.
- Move routing behavior from core.py into a focused abh/routing.py module while preserving route output semantics.
- Keep this slice behavior-preserving: no new user-visible commands, no schema changes, and no algorithm upgrades.

## Non-Goals

- Do not improve drift detection quality, memory indexing, route ranking, or object graph semantics in this slice.
- Do not modify CLI/MCP contracts, plan/audit/verification behavior, close gates, stale semantics, or storage format.
- Do not split doctor or storage behavior in this slice.

## Exit Criteria

- abh.core re-exports memory, drift, and routing functions from their new domain modules.
- CLI memory, drift, route commands behave as before and existing tests pass.
- MCP memory, drift, route tools behave as before and existing MCP tests pass.
- core.py no longer contains the full memory, drift, or routing implementations.
- python3 -m unittest tests/test_cli.py -v passes.
- python3 -m abh doctor passes.

## Validation Checklist

- python3 -m unittest tests/test_cli.py -v
- python3 -m abh doctor

## Closure Evidence

- abh/memory.py
- abh/drift.py
- abh/routing.py
- tests/test_cli.py module split coverage
- docs synchronized for plan-024
- .abh/verifications/ver-d88dc5cfe2f1.json
- docs/plans/plan-024-memory-drift-routing-module-split.md
- audit-024-memory-drift-routing-module-split

## Verification Runs

- ver-d88dc5cfe2f1
- ver-7fcca1aa2a0a
- ver-e44f2ac2dc7a
- ver-58e2fba0ff70

## Audits

- audit-024-memory-drift-routing-module-split
