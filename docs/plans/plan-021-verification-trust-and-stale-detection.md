# Plan: Verification Trust and Stale Detection

## Metadata

- ID: plan-021-verification-trust-and-stale-detection
- Status: closed
- Attractor: docs/architecture/attractors/abh-core-attractor.md
- Baseline: Stage 3 verify run records environment metadata, but verification records do not yet express trust level or whether the latest evidence may be stale after plan/checklist/git changes.
- Owner: platform
- Created: 2026-05-24T12:00:10.216515+00:00
- Updated: 2026-05-24T12:26:57.784028+00:00

## Goals

- Persist a trust_level on verification records, defaulting manual records to manual_record and verify run records to local_shell.
- Keep old verification JSON readable by defaulting missing trust_level to unknown.
- Compute latest verification freshness for plan status JSON using plan updated time, validation checklist command match, and available git environment metadata.
- Expose latest verification trust/stale summary in plan status --json without changing human status output.

## Non-Goals

- Do not add CI execution, isolated execution, trust policy enforcement, or close gate changes in this slice.
- Do not change pass/fail/partial verification result semantics or blocked-plan behavior.
- Do not make stale verification automatically block plan close.
- Do not implement failure classification or atomic write/file locking in this slice.

## Exit Criteria

- Manual verify record persists trust_level=manual_record and remains visible in JSON output.
- verify run persists trust_level=local_shell and latest plan status JSON reports it.
- plan status --json marks the latest verification stale=false immediately after a matching verify run and stale=true after validation checklist changes.
- Existing verification JSON without trust_level and environment still loads successfully.
- python3 -m unittest tests/test_cli.py -v passes.
- python3 -m abh doctor passes.

## Validation Checklist

- python3 -m unittest tests/test_cli.py -v
- python3 -m abh doctor

## Closure Evidence

- tests/test_cli.py trust and stale coverage
- docs synchronized for plan-021
- git status hash stale detection coverage
- audit-021-verification-trust-and-stale-detection
- .abh/verifications/ver-4b7d7719a801.json

## Verification Runs

- ver-e40f4bb1b752
- ver-77a326a3ed82
- ver-c460a59d99aa
- ver-4b7d7719a801
- ver-983c54f842cf

## Audits

- audit-021-verification-trust-and-stale-detection
