# Plan: README Zero Python Skill Onboarding

## Metadata

- ID: plan-056-readme-zero-python-skill-onboarding
- Status: closed
- Attractor: docs/architecture/attractors/abh-core-attractor.md
- Baseline: README currently documents uvx installation but the beginner path and abh-workflow skill usage are not prominent enough for users without Python.
- Owner: platform
- Created: 2026-06-08T07:39:29.390387+00:00
- Updated: 2026-06-08T07:47:03.151868+00:00

## Goals

- Add a prominent README quickstart for zero-Python users that starts with installing uv, running or installing abh, and using the abh-workflow skill from Codex.
- Provide copy/paste commands for Windows PowerShell, macOS, and Linux users without requiring prior Python knowledge.
- Document the simplest Codex prompt that points to skills/abh-workflow and explains what the skill will do.

## Non-Goals

- Do not change ABH CLI runtime behavior, package publishing, PyPI status, or multi-repo sharing.
- Do not claim uvx abh works as a bare package name before package publication.

## Exit Criteria

- README top section contains a zero-Python beginner path before the detailed feature list.
- README includes copy/paste uv install, uvx run, uv tool install, and Codex abh-workflow usage prompts.
- Tests assert the README keeps the beginner install and skill usage entry visible.

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

- git diff --check
- .venv\\Scripts\\python.exe -m unittest tests.test_command_contracts.CommandContractTests.test_readme_exposes_zero_python_skill_onboarding -v
- .venv\\Scripts\\python.exe -m unittest discover -v
- .venv\\Scripts\\python.exe -m abh doctor --json
- .venv\\Scripts\\python.exe -m abh roadmap check --json
- .venv\\Scripts\\python.exe -m abh next --json

## Closure Evidence

- README.md
- tests/test_command_contracts.py
- audit-056-readme-zero-python-skill-onboarding

## Verification Runs

- ver-1e3ba21f383c

## Audits

- audit-056-readme-zero-python-skill-onboarding
