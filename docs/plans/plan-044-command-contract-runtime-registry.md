# Plan: Command Contract Runtime Registry

## Metadata

- ID: plan-044-command-contract-runtime-registry
- Status: closed
- Attractor: docs/architecture/attractors/abh-core-attractor.md
- Baseline: Architecture review found that command metadata, CLI parser definitions, MCP handlers, and shared protocol helpers still carry duplicated facts. This creates drift risk as ABH adds more agent-facing commands.
- Owner: platform
- Created: 2026-06-04T03:00:00+00:00
- Updated: 2026-06-04T07:47:25.366042+00:00

## Goals

- Record the architecture hardening queue in roadmap and task-board planning artifacts.
- Start command contract hardening by moving shared ABH error payload helpers into the command protocol layer.
- Make MCP depend on shared command helpers instead of importing protocol helpers from the CLI adapter.
- Add regression coverage that locks the MCP-to-command-layer dependency direction.

## Non-Goals

- Do not rewrite argparse generation or MCP dispatch in this first slice.
- Do not change JSON envelope shape, MCP tool names, command contracts, or user-facing CLI behavior.
- Do not implement repository write transactions, schema migrations, verification runner policy changes, or test-suite splitting in this slice.

## Exit Criteria

- Architecture hardening items are visible in .abh roadmap queue, development roadmap, and task board.
- abh.commands exports ABH error payload helpers used by both CLI and MCP adapters.
- abh.mcp_server no longer imports protocol helper functions from abh.cli.
- Tests cover the MCP adapter using the shared command-layer error payload helper.

## Validation Checklist

- python3 -m unittest tests/test_cli.py -v
- python3 -m abh doctor
- git diff --check
- python3 -m abh roadmap check --json

## Closure Evidence

- .abh/roadmap.json
- docs/development-roadmap.md
- docs/task-board.md
- docs/superpowers/plans/2026-06-04-command-contract-runtime-registry.md
- abh/commands.py
- abh/cli.py
- abh/mcp_server.py
- tests/test_cli.py
- audit-044-command-contract-runtime-registry

## Verification Runs

- ver-1a1bbf356998

## Audits

- audit-044-command-contract-runtime-registry
