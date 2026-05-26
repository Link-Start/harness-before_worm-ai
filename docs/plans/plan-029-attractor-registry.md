# Plan: Attractor Registry MVP

## Metadata

- ID: plan-029-attractor-registry
- Status: closed
- Attractor: docs/architecture/attractors/abh-core-attractor.md
- Baseline: Stage 4 has a shared Agent-First command contract, but active attractor is still only a markdown convention and not a CLI/MCP-readable ABH object.
- Owner: platform
- Created: 2026-05-26T09:14:14.946650+00:00
- Updated: 2026-05-26T10:34:00.050594+00:00

## Goals

- Introduce AttractorRecord and a local attractor registry backed by .abh/attractors JSON plus docs/architecture/attractors Markdown.
- Add agent-facing CLI commands for attractor list/show/active/create/supersede with JSON output and shared command contract metadata.
- Expose read-only MCP tools for attractor list/show/active through the shared command contract.
- Require ready plans to reference the current active attractor by id or path.
- Synchronize Stage 4 docs so plan-029 is the active attractor registry implementation slice.

## Non-Goals

- Do not implement abh init, agent setup, hooks, abh next, onboarding check, distribution, or team policy in this slice.
- Do not support multiple simultaneous active attractors or distributed registry locking.
- Do not redesign existing plan/audit/verification state machines, close gates, stale semantics, storage format, or verification execution semantics.
- Do not change route/drift behavior beyond leaving extension points for future active-attractor-aware work.

## Exit Criteria

- AttractorRecord serializes with schema_version and legacy-safe defaults where appropriate.
- abh attractor list/show/active/create/supersede work from CLI; JSON responses use the shared envelope and command ids are represented in abh.commands.
- MCP exposes read-only abh_attractor_list, abh_attractor_show, and abh_attractor_active tools generated from command contract metadata.
- Creating or transitioning a ready plan rejects a non-active attractor reference and accepts the current active attractor id or path.
- Superseding an attractor records old/new relationship, marks the old attractor inactive, and makes exactly one active attractor visible.
- python3 -m unittest tests/test_cli.py -v passes.
- python3 -m abh doctor passes.

## Validation Checklist

- python3 -m unittest tests/test_cli.py -v
- python3 -m abh doctor
- git diff --check
- python3 -m abh attractor active --json
- python3 -m abh plan status plan-029-attractor-registry --json

## Closure Evidence

- docs/plans/plan-029-attractor-registry.md
- abh/attractors.py
- abh/models.py
- abh/storage.py
- abh/commands.py
- abh/cli.py
- abh/mcp_server.py
- tests/test_cli.py
- docs/architecture/agent-protocol.md
- audit-029-attractor-registry

## Verification Runs

- ver-fa01cb98606d
- ver-f78e28aa4d40
- ver-ed85ce8d3ae8
- ver-f915109808c6

## Audits

- audit-029-attractor-registry
