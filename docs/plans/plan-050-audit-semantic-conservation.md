# Plan: Audit Semantic Conservation

## Metadata

- ID: plan-050-audit-semantic-conservation
- Status: closed
- Attractor: docs/architecture/attractors/abh-core-attractor.md
- Baseline: Audit bundle currently asks independent reviewers to check goals, non-goals, exit criteria, verification freshness, and evidence paths, but it does not explicitly ask whether in-scope commitments disappeared, weakened, or moved to non-authoritative artifacts.
- Owner: platform
- Created: 2026-06-05T09:37:57.860501+00:00
- Updated: 2026-06-05T10:26:16.075364+00:00

## Goals

- Update audit bundle prompts to ask semantic conservation questions for in-scope commitments.
- Ask reviewers to distinguish J-flow-only routing from R-flow uncertainty reduction using local evidence.
- Document semantic conservation guidance in audit templates and Stage 6 quality signal vocabulary.
- Keep audit execution independent and read-only; ABH still prepares prompts and records results but does not call an auditor model.

## Non-Goals

- Do not add automated semantic proof, LLM scoring, or external audit execution.
- Do not make flow classification mandatory on historical audit records.
- Do not alter independent audit close gates beyond preserving existing freshness and independence rules.

## Exit Criteria

- abh audit bundle <plan-id> --json includes semantic conservation and J-flow/R-flow review prompts.
- Audit templates and docs include semantic conservation guidance.
- Existing audit records remain readable with no migration.
- Tests cover audit bundle prompt content and JSON envelope output.

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
- python -m unittest tests/test_cli.py -v
- python -m abh doctor
- python -m abh roadmap check --json
- python -m unittest tests.test_verifications_and_audits.VerificationAndAuditTests.test_audit_bundle_json_returns_prompt_and_structured_evidence tests.test_verifications_and_audits.VerificationAndAuditTests.test_audit_docs_document_semantic_conservation_review tests.test_verifications_and_audits.VerificationAndAuditTests.test_audit_request_markdown_includes_semantic_conservation_review -v

## Closure Evidence

- abh/audit_bundle.py
- tests/test_cli.py
- docs/audits/templates/audit-template.md
- docs/audits/README.md
- docs/architecture/quality-signals.md
- docs/development-roadmap.md
- docs/task-board.md
- docs/context/codebase-map.md
- tests/test_verifications_and_audits.py
- audit-050-audit-semantic-conservation-r2

## Verification Runs

- ver-d86f9957fad1
- ver-ba625b64a0ad
- ver-850d3e65452b

## Audits

- audit-050-audit-semantic-conservation
- audit-050-audit-semantic-conservation-r2
