# Plan: Owner Doc Stable Commitments

## Metadata

- ID: plan-051-owner-doc-stable-commitments
- Status: draft
- Attractor: docs/architecture/attractors/abh-core-attractor.md
- Baseline: ABH has source-of-truth precedence and active attractor invariants, but most owner docs do not yet separate stable commitments, allowed variation, drift/leakage signals, and correction paths.
- Owner: platform
- Created: 2026-06-05T10:30:13.996764+00:00
- Updated: 2026-06-05T10:30:13.999274+00:00

## Goals

- Update owner-doc templates and key ABH owner docs with Stable Commitments, Allowed Variation, Drift / Leakage Signals, and Correction Path sections.
- Document how these owner-doc sections support plan Reference Sets, audit semantic conservation, health reports, and future drift detection.
- Keep the first slice docs-first so the structure can dogfood before JSON fields or doctor checks are added.
- Align docs/index and source-of-truth guidance with the stable-commitments structure.

## Non-Goals

- Do not add new AttractorRecord fields or doctor consistency gates in the first slice.
- Do not rewrite every historical document.
- Do not introduce team policy, release blockers, or external services.

## Exit Criteria

- Key owner docs and templates include stable commitments, allowed variation, drift/leakage signals, and correction path sections.
- docs/index and source-of-truth docs explain when agents should consult the stable-commitments sections.
- Quality signal docs explain how owner-doc stable commitments feed future health and drift checks.
- Tests or doctor-compatible checks confirm the updated docs exist and roadmap consistency remains clean.

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

- python3 -m unittest tests/test_cli.py -v
- python3 -m abh doctor
- git diff --check
- python3 -m abh roadmap check --json

## Closure Evidence

- docs/index.md
- docs/context/source-of-truth.md
- docs/context/project-context.md
- docs/context/codebase-map.md
- docs/architecture/templates/attractor-template.md
- docs/architecture/quality-signals.md
- docs/development-roadmap.md
- docs/task-board.md

## Verification Runs

- 

## Audits

- 
