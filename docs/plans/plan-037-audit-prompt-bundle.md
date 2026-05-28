# Plan: Audit Prompt Bundle

## Metadata

- ID: plan-037-audit-prompt-bundle
- Status: closed
- Attractor: docs/architecture/attractors/abh-core-attractor.md
- Baseline: Stage 5 starts by helping humans and independent agents request audits consistently. ABH should generate a read-only audit prompt and evidence bundle from an existing plan state, without recording a verdict, calling an LLM, or weakening the independent audit close gate.
- Owner: platform
- Created: 2026-05-28T07:10:36.119008+00:00
- Updated: 2026-05-28T07:27:05.951646+00:00

## Goals

- Add a read-only audit bundle surface that can generate an independent audit prompt from a plan id.
- Include plan metadata, latest verification summary, audit status, closure evidence paths, and key non-goal reminders in the bundle.
- Register the command in the Agent-First command contract and expose JSON output suitable for opencode or another independent reviewer.
- Document Stage 5 audit prompt bundle behavior in README, Agent Protocol, roadmap, task-board, and codebase map.

## Non-Goals

- Do not call opencode, DeepSeek, OpenAI, network services, or any LLM from the ABH command.
- Do not record audit results, create or complete audit records, transition plans, close plans, or change verification freshness rules.
- Do not implement the later independent audit gate, auditor identity enforcement, or close-time independence policy in this slice.

## Exit Criteria

- abh audit bundle <plan-id> --json returns a stable envelope with an audit_bundle payload.
- The bundle includes a copyable prompt that tells the reviewer to audit independently, avoid file edits, check goals/non-goals/exit criteria, inspect verification freshness, and return Result/Rationale/Findings.
- The bundle includes structured evidence paths for the plan document, plan JSON, latest verification JSON when available, requested audits, and closure evidence paths.
- The bundle reports latest verification result, trust level, stale flag, and stale reasons using the existing plan status freshness logic.
- The command is read-only, has no confirmation requirement, and is registered in abh.commands.
- README, Agent Protocol, roadmap, task-board, and codebase map describe the read-only boundary without claiming automated audit execution or close-gate enforcement.

## Validation Checklist

- python3 -m unittest tests/test_cli.py -v
- python3 -m abh doctor
- git diff --check
- python3 -m abh roadmap check --json
- python3 -m abh audit bundle plan-037-audit-prompt-bundle --json
- python3 -m abh plan status plan-037-audit-prompt-bundle --json

## Closure Evidence

- abh/audit_bundle.py
- abh/cli.py
- abh/commands.py
- tests/test_cli.py
- README.md
- docs/development-roadmap.md
- docs/task-board.md
- docs/architecture/agent-protocol.md
- docs/context/codebase-map.md
- docs/plans/plan-037-audit-prompt-bundle.md
- audit-037-audit-prompt-bundle

## Verification Runs

- ver-50e2563a529c
- ver-80899a7722f2
- ver-c2ca10dab0eb
- ver-6b88f5ddd727

## Audits

- audit-037-audit-prompt-bundle
