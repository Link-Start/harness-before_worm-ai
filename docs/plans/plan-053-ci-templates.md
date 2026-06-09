# Plan: CI Templates

## Metadata

- ID: plan-053-ci-templates
- Status: closed
- Attractor: docs/architecture/attractors/abh-core-attractor.md
- Baseline: Stage 7 starts with reusable CI entry points. The repository already has a basic GitHub Actions workflow from earlier governance hardening, but it only runs the thin CLI test module, doctor, help, and plan list. ABH now has full unittest discovery, roadmap checks, diff whitespace checks, and health/drift reporting that should be represented in PR-oriented CI templates without introducing release automation or remote runner policy.
- Owner: platform
- Created: 2026-06-06T10:04:50.177525+00:00
- Updated: 2026-06-06T13:39:42.334257+00:00

## Goals

- Upgrade the GitHub Actions CI workflow so pull requests run editable install, full unittest discovery, ABH doctor, roadmap consistency, git diff whitespace checks, and a read-only health report.
- Document the CI template boundary for other repositories, including which checks are gating and which are informational.
- Keep CI templates aligned with ABH local validation semantics and trusted local verification policy.
- Synchronize README, development roadmap, task board, and codebase map with the Stage 7 CI template slice.

## Non-Goals

- Do not implement release automation, publishing, signing, deployment, or package registry workflows.
- Do not introduce team policy, required status checks, GitHub branch protection, or remote runner governance.
- Do not add external services, third-party CI actions beyond existing GitHub setup actions, or network-dependent tests beyond package installation.
- Do not make historical health-report semantic pressure block this CI template slice.

## Exit Criteria

- .github/workflows/ci.yml runs full unittest discovery instead of only the thin CLI smoke module.
- CI runs python -m abh doctor, python -m abh roadmap check --json, git diff --check, and python -m abh report health --json.
- Docs explain how to reuse the CI template and distinguish gating checks from informational health/drift reporting.
- Roadmap, task-board, README, and codebase map reflect plan-053 as the active Stage 7 CI template slice.
- Tests or contract checks cover the CI workflow command list so future edits do not silently drop ABH gates.

## Commitment Phase State

### Stable State Now

- ABH has local validation commands and a basic repository CI workflow.

### Active Change Pressure

- Stage 7 needs reusable CI templates that expose ABH governance checks in pull requests.

### Target Stable State

- Pull-request CI templates run ABH consistency gates and surface health/drift posture without claiming release automation.

### Conversion Proof

- Workflow contract tests and a fresh verification run prove the CI command list and docs stay aligned.

### Residual Pressure

- Team policy and release automation | Non-blocking rationale: Non-blocking because this slice only provides reusable CI checks, while team enforcement and release automation remain queued Stage 7 work.

## Validation Checklist

- git diff --check
- .venv\Scripts\python.exe -m unittest discover -v
- .venv\Scripts\python.exe -m abh doctor --json
- .venv\Scripts\python.exe -m abh roadmap check --json
- .venv\Scripts\python.exe -m abh report health --json

## Closure Evidence

- .github/workflows/ci.yml
- tests/test_command_contracts.py
- README.md
- docs/recipes/ci.md
- docs/development-roadmap.md
- docs/task-board.md
- docs/context/codebase-map.md
- audit-053-ci-templates

## Verification Runs

- ver-bea39c230f77
- ver-f07a468169c6

## Audits

- audit-053-ci-templates
