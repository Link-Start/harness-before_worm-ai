# Plan: Project Health Report

## Metadata

- ID: plan-042-project-health-report
- Status: closed
- Attractor: docs/architecture/attractors/abh-core-attractor.md
- Baseline: After drift and memory emit structured quality signals, ABH should summarize project health as semantic pressure: where quality is degrading, which commitments remain unbound, which risks repeat, and what an agent should inspect next.
- Owner: platform
- Created: 2026-05-30T11:01:13.582322+00:00
- Updated: 2026-05-30T12:02:06.144491+00:00

## Goals

- Add a read-only project health report command that aggregates plan, verification, audit, drift, memory, doctor, and roadmap signals into a semantic pressure report.
- Report plan close rate, stale verification count, audit rejection/need-info count, repeated drift, reusable memory hits, and top unresolved quality risks.
- Surface unbound commitment pressure, stale proof, semantic leakage, J-flow-only evidence, orphaned memory, and repeated leakage where local evidence supports them.
- Distinguish routed commitments from reduced uncertainty in the report vocabulary without introducing close or release blockers.
- Keep the primary health posture product-quality-first, with agent navigation as a secondary consumer.
- Expose health report data through JSON and document how abh next may consume top risks later.

## Non-Goals

- Do not add a Web UI, external dashboard, database, LLM scorer, or team policy engine.
- Do not make health score automatically block close or release.
- Do not implement plan Reference Set fields, Commitment Phase State fields, audit flow classification fields, or owner-doc Stable Commitments in this slice.
- Do not implement Stage 7 CI templates or release automation in this slice.

## Exit Criteria

- abh report health --json returns health summary, metrics, semantic pressure signals, top risks, and recommended inspections.
- The report uses structured drift and memory quality signals when present and degrades gracefully when absent.
- The report can identify J-flow-only or semantic-leakage risks from existing local records without claiming automated semantic proof.
- The command is read-only and registered in the Agent-First command contract.
- Tests cover empty repositories, the current repository shape, repeated drift, stale verification, J-flow-only/semantic-leakage risk, and JSON envelope output.

## Validation Checklist

- python3 -m unittest tests/test_cli.py -v
- python3 -m abh doctor
- git diff --check
- python3 -m abh roadmap check --json

## Closure Evidence

- abh/reporting.py
- abh/cli.py
- abh/commands.py
- abh/mcp_server.py
- tests/test_cli.py
- README.md
- docs/architecture/quality-signals.md
- docs/development-roadmap.md
- docs/task-board.md
- docs/context/codebase-map.md
- audit-042-project-health-report

## Verification Runs

- ver-cf7f716040e6
- ver-9c38caf953aa

## Audits

- audit-042-project-health-report
