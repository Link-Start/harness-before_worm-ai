# Plan: Roadmap Queue and Plan Numbering

## Metadata

- ID: plan-030-roadmap-queue-and-plan-numbering
- Status: closed
- Attractor: docs/architecture/attractors/abh-core-attractor.md
- Baseline: Stage 4 roadmap currently prewrites concrete future plan ids in multiple docs. Inserting a checkpoint or urgent slice forces manual renumbering across roadmap, stage plan, task board, protocol docs, and README, which creates avoidable drift risk. ABH needs a queue/materialization model so future work is addressed by stable roadmap keys until a plan is actually created.
- Owner: platform
- Created: 2026-05-27T01:23:20.671142+00:00
- Updated: 2026-05-27T03:16:34.094257+00:00

## Goals

- Introduce a machine-readable roadmap queue where future work uses stable keys instead of preassigned plan numbers.
- Add commands to inspect the next plan number and materialize a roadmap queue item into the next available plan id.
- Update docs so unmaterialized future work is referenced by roadmap keys, while concrete plan ids are only used for existing plans.
- Add doctor or validation coverage that catches duplicate plan numbers and future-doc preassigned plan-id drift.

## Non-Goals

- Do not renumber historical plans or rewrite closed plan/audit/verification facts.
- Do not implement abh init, agent setup, hooks, abh next, onboarding check, or distribution in this slice.
- Do not introduce a database, server, or external dependency.

## Exit Criteria

- A roadmap queue data file exists with stable Stage 4/5/6/7 future work keys and no preassigned concrete plan ids for unmaterialized items.
- ABH exposes a machine-readable next-plan-id or materialization path that allocates the next available plan number without hand-editing multiple docs.
- Docs explain that future roadmap items use stable queue keys and materialized plans use concrete plan ids.
- Doctor or tests detect duplicate plan numbers and/or stale preassigned future plan references.
- python3 -m unittest tests/test_cli.py -v passes.
- python3 -m abh doctor passes.

## Validation Checklist

- python3 -m unittest tests/test_cli.py -v
- python3 -m abh doctor
- git diff --check
- python3 -m abh plan status plan-030-roadmap-queue-and-plan-numbering --json
- python3 -m abh roadmap check --json
- python3 -m abh roadmap next-id --json
- python3 -m abh roadmap list --json

## Closure Evidence

- docs/plans/plan-030-roadmap-queue-and-plan-numbering.md
- README.md
- docs/development-roadmap.md
- docs/阶段规划.md
- docs/task-board.md
- .abh/roadmap.json
- abh/roadmap.py
- abh/cli.py
- abh/commands.py
- abh/mcp_server.py
- abh/core.py
- tests/test_cli.py
- audit-030-roadmap-queue-and-plan-numbering

## Verification Runs

- ver-c6e1829e98f2
- ver-eed9cb6e5610
- ver-a0b6d2d0b937
- ver-c06d41ddaf41

## Audits

- audit-030-roadmap-queue-and-plan-numbering
