# Plan: ABH Workflow Skill Packaging MVP

## Metadata

- ID: plan-055-abh-workflow-skill
- Status: closed
- Attractor: docs/architecture/attractors/abh-core-attractor.md
- Baseline: Package existing ABH CLI workflow into a dumb/simple Codex skill without implementing Stage 7 multi-repo sharing.
- Owner: platform
- Created: 2026-06-08T02:37:39.044625+00:00
- Updated: 2026-06-08T03:11:03.485190+00:00

## Goals

- Create a concise Codex skill that guides agents through the existing ABH workflow: onboarding check, next, plan definition, verification, audit bundle, audit record, close, doctor, and health reporting.
- Keep the skill as command orchestration and decision rules over existing ABH CLI behavior, not a replacement for ABH state machines or evidence gates.
- Document installation and fallback assumptions for using ABH from this repository or a git-based uvx/uv tool install path.
- Validate that the skill content is small, triggerable, and does not claim independent audit or completion on behalf of the implementation session.

## Non-Goals

- Do not implement multi-repo sharing, import/export bundles, team policy, release automation, or package publishing in this slice.
- Do not change ABH CLI/MCP runtime behavior unless a packaging-specific blocker is found and separately justified.
- Do not embed the full ABH repository docs into the skill; keep detailed references external and loaded only when needed.
- Do not allow the skill to bypass verification, independent audit, close gates, or doctor/roadmap consistency checks.

## Exit Criteria

- A skill directory exists with SKILL.md frontmatter that triggers for ABH workflow, plan, verification, audit, close, and onboarding requests.
- The skill body provides a short deterministic command flow for first use, daily use, blocked plans, verification failures, audit handoff, and close readiness.
- The skill explicitly states that independent audit must be performed in a separate context and cannot be self-signed by the implementation session.
- Skill validation passes and repository ABH checks remain clean.

## Commitment Phase State

### Stable State Now

- ABH already provides the CLI, MCP, verification, audit, next, onboarding, doctor, and health surfaces needed for a workflow skill.

### Active Change Pressure

- The current product need is simplifying ABH usage through a skill, not expanding Stage 7 multi-repo sharing.

### Target Stable State

- A small ABH workflow skill can guide agents through existing ABH gates without weakening repository-backed evidence semantics.

### Conversion Proof

- Skill validation, ABH verification, and an independent audit confirm the skill routes users through existing ABH commands and preserves verification/audit separation.

### Residual Pressure

- Stage 7 multi-repo sharing remains blocked/deferred until there is an explicit multi-repository reuse need and implementation plan. | Non-blocking rationale: The skill packaging slice can proceed while multi-repo sharing remains blocked because it only orchestrates existing ABH commands.

## Validation Checklist

- git diff --check
- .venv\\Scripts\\python.exe -m unittest discover -v
- .venv\\Scripts\\python.exe -m abh doctor --json
- .venv\\Scripts\\python.exe -m abh roadmap check --json
- .venv\\Scripts\\python.exe -m abh next --json
- .venv\Scripts\python.exe C:/Users/1003584/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/abh-workflow

## Closure Evidence

- skills or .codex skill directory for abh-workflow
- docs/development-roadmap.md
- docs/task-board.md
- docs/context/codebase-map.md
- tests/ or validation transcript
- skills/abh-workflow/SKILL.md
- skills/abh-workflow/references/command-flow.md
- skills/abh-workflow/agents/openai.yaml
- tests/test_command_contracts.py
- audit-055-abh-workflow-skill

## Verification Runs

- ver-11a517ed7312

## Audits

- audit-055-abh-workflow-skill
