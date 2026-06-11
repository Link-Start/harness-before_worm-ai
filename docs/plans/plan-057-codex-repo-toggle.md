# Plan: Codex Repository ABH Toggle

## Metadata

- ID: plan-057-codex-repo-toggle
- Status: closed
- Attractor: docs/architecture/attractors/abh-core-attractor.md
- Baseline: docs/development-roadmap.md
- Owner: platform
- Created: 2026-06-11T03:31:22.622485+00:00
- Updated: 2026-06-11T05:49:48.356046+00:00

## Goals

- Add abh codex on/off/status for repository-local Codex ABH mode.
- Write and remove a managed .codex/config.toml with ABH Codex developer instructions.
- Keep the feature preview-first and confirmed-write-only, matching existing ABH write boundaries.

## Non-Goals

- Do not implement temporary Codex CLI profile switching.
- Do not implement Claude Code or generic MCP toggles.
- Do not merge into unmanaged .codex/config.toml files.

## Exit Criteria

- abh codex status --json reports disabled when no managed config exists and enabled after a managed write.
- abh codex on --write requires --confirm and does not overwrite unmanaged .codex/config.toml.
- abh codex off removes only ABH-managed Codex config.
- README and Codex recipe document the managed toggle workflow.

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

- python -m unittest tests.test_cli tests.test_command_contracts -v
- python -m abh doctor --json
- python -m abh roadmap check --json

## Closure Evidence

- docs/superpowers/specs/2026-06-11-codex-abh-toggle-design.md
- docs/superpowers/plans/2026-06-11-codex-abh-toggle.md
- audit-057-codex-repo-toggle

## Verification Runs

- ver-a844733aa3be
- ver-2a08c7c59afa

## Audits

- audit-057-codex-repo-toggle
