# Plan: Owner Doc Stable Commitments

## Metadata

- ID: plan-051-owner-doc-stable-commitments
- Status: closed
- Attractor: docs/architecture/attractors/abh-core-attractor.md
- Baseline: ABH has source-of-truth precedence and active attractor invariants, but most owner docs do not yet separate stable commitments, allowed variation, drift/leakage signals, and correction paths.
- Owner: platform
- Created: 2026-06-05T10:30:13.996764+00:00
- Updated: 2026-06-06T08:00:54.141453+00:00

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

- ABH already has source-of-truth precedence, owner-doc routing, active attractor invariants, audit semantic conservation, and commitment phase state records.

### Active Change Pressure

- Key owner docs still mix durable commitments with mutable guidance, making future Agents guess which statements must remain invariant.

### Target Stable State

- Important owner docs and templates expose Stable Commitments, Allowed Variation, Drift / Leakage Signals, and Correction Path sections that future audits and health checks can inspect.

### Conversion Proof

- Tests assert stable commitment sections exist in current owner docs, templates, init seed docs, and quality signal guidance.

### Residual Pressure

- Doctor gate for owner-doc section completeness | Non-blocking rationale: Non-blocking because this first slice is docs-first and explicitly avoids new doctor consistency gates.

## Validation Checklist

- git diff --check
- .venv\Scripts\python.exe -m unittest discover -v
- .venv\Scripts\python.exe -m abh doctor --json
- .venv\Scripts\python.exe -m abh roadmap check --json

## Closure Evidence

- docs/index.md
- docs/context/source-of-truth.md
- docs/context/project-context.md
- docs/context/codebase-map.md
- docs/architecture/templates/attractor-template.md
- docs/architecture/quality-signals.md
- docs/development-roadmap.md
- docs/task-board.md
- audit-051-owner-doc-stable-commitments

## Verification Runs

- ver-893f633822b8
- ver-726c18a5135b

## Audits

- audit-051-owner-doc-stable-commitments
