# Plan: ABH Next and Onboarding Check

## Metadata

- ID: plan-035-abh-next-and-onboarding-check
- Status: closed
- Attractor: docs/architecture/attractors/abh-core-attractor.md
- Baseline: Expose the next recommended ABH action and check whether a repository is ABH-ready.
- Owner: platform
- Created: 2026-05-27T16:29:57.389147+00:00
- Updated: 2026-05-28T04:55:32.844757+00:00

## Goals

- Add shared Agent-First command contract entries for abh next and abh onboarding check.
- Expose abh next --json as a read-only navigation command that recommends the next safe ABH action from repository state.
- Expose abh onboarding check --json as a read-only ABH readiness report for active attractor, AGE owner docs, agent setup export, hook guardrail availability, and closed-loop evidence.
- Keep recommendations grounded in existing local records: active attractor, roadmap queue, open plans, verification summaries, audits, doctor issues, and known Stage 4 command availability.
- Document next/onboarding MVP behavior in README, Agent Protocol, roadmap, task-board, and codebase map.

## Non-Goals

- Do not implement onboarding writes, agent config writes, hook installation, quickstart recipes, package distribution, or team policy in this slice.
- Do not change plan, verification, audit, close, doctor, hook, init, agent setup, or MCP write semantics.
- Do not build a ranking engine, LLM planner, route replacement, or external service.
- Do not require a perfectly clean working tree for next/onboarding read-only output.

## Exit Criteria

- abh next --json returns next_action, recommended_command, requires_confirmation, rationale, and alternatives.
- With no open plans and queued roadmap items, abh next --json recommends materializing the next queued roadmap key.
- With a draft plan, abh next --json recommends completing or transitioning that plan before materializing new work.
- abh onboarding check --json returns checks with status, ok boolean, ready boolean, and recommended actions.
- On the current repository, onboarding check reports active attractor, owner docs, agent setup export, hook guardrail commands, doctor, and closed-loop evidence as available.
- Command contracts are registered in abh.commands before or alongside CLI adapters.
- With a running plan whose latest verification is fresh pass and no audit exists, abh next --json recommends requesting independent audit evidence.

## Validation Checklist

- python3 -m unittest tests/test_cli.py -v
- python3 -m abh doctor
- git diff --check
- python3 -m abh roadmap check --json
- python3 -m abh next --json
- python3 -m abh onboarding check --json
- python3 -m abh plan status plan-035-abh-next-and-onboarding-check --json

## Closure Evidence

- README.md
- docs/development-roadmap.md
- docs/task-board.md
- docs/architecture/agent-protocol.md
- docs/context/codebase-map.md
- abh/navigation.py
- abh/cli.py
- abh/commands.py
- tests/test_cli.py
- audit-035-abh-next-and-onboarding-check

## Verification Runs

- ver-368cbd12dd77
- ver-26001e78ac41
- ver-d5198ed53668
- ver-19a53c3ffd10

## Audits

- audit-035-abh-next-and-onboarding-check
