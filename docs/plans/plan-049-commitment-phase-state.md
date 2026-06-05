# Plan: Commitment Phase State

## Metadata

- ID: plan-049-commitment-phase-state
- Status: closed
- Attractor: docs/architecture/attractors/abh-core-attractor.md
- Baseline: Plans currently express baseline, goals, non-goals, exit criteria, and closure evidence, but they do not explicitly model the difference between stable commitments and active change obligations.
- Owner: platform
- Created: 2026-06-05T04:26:46.930084+00:00
- Updated: 2026-06-05T09:12:34.004779+00:00

## Goals

- Add an optional Commitment Phase State structure to plan JSON and Markdown rendering with backward-compatible defaults.
- Represent stable state now, active change pressure, target stable state after closure, conversion proof, and residual pressure with non-blocking rationale.
- Expose Commitment Phase State through plan status JSON and plan templates.
- Document how audit bundles and future close review can inspect p-to-q conversion without adding automatic close blockers in this slice.

## Non-Goals

- Do not make Commitment Phase State mandatory for ready plans in the first slice.
- Do not automatically infer semantic commitments with an LLM or external service.
- Do not change close gates beyond documentation and optional reporting surfaces.

## Exit Criteria

- New plans can carry Commitment Phase State in JSON and Markdown while legacy plans read with empty defaults.
- Plan status JSON exposes the Commitment Phase State.
- Plan templates explain stable state, active pressure, target state, conversion proof, and residual pressure.
- Tests cover legacy reads, new state rendering, JSON output, and plan update or creation behavior.

## Commitment Phase State

### Stable State Now

- 

### Active Change Pressure

- 

### Target Stable State

- 

### Conversion Proof

- 

### Residual Pressure

- 

## Validation Checklist

- python3 -m abh doctor
- git diff --check
- python3 -m abh roadmap check --json
- python3 -m unittest discover -v

## Closure Evidence

- abh/models.py
- abh/plans.py
- abh/cli.py
- tests/test_cli.py
- docs/plans/templates/plan-template.md
- docs/architecture/quality-signals.md
- docs/development-roadmap.md
- docs/task-board.md
- docs/context/codebase-map.md
- docs/superpowers/plans/2026-06-05-commitment-phase-state.md
- audit-049-commitment-phase-state

## Verification Runs

- ver-27d8eb073013
- ver-f038c30d2662
- ver-26ded140fecb
- ver-0cd1c44d69b4

## Audits

- audit-049-commitment-phase-state
