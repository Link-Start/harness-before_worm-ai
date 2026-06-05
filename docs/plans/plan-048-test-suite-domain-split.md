# Plan: Test Suite Domain Split

## Metadata

- ID: plan-048-test-suite-domain-split
- Status: draft
- Attractor: docs/architecture/attractors/abh-core-attractor.md
- Baseline: tests/test_cli.py covers broad CLI, MCP, storage, roadmap, doctor, reporting, and domain behavior. Coverage is strong, but the monolithic file raises review and maintenance cost.
- Owner: platform
- Created: 2026-06-05T02:36:46.023921+00:00
- Updated: 2026-06-05T02:36:46.026737+00:00

## Goals

- Split tests by responsibility into focused modules.
- Keep representative end-to-end CLI and MCP flows.
- Preserve the current unittest-based zero-dependency test stack.
- Document the new test organization in the codebase map.

## Non-Goals

- Do not switch test frameworks in this slice.
- Do not reduce behavior coverage.
- Do not rewrite production code solely to fit the test split.

## Exit Criteria

- Focused test modules cover command contracts, MCP, storage/doctor, roadmap, reporting, and core domain flows.
- Full unittest discovery passes.
- The old monolithic file is reduced or clearly limited to end-to-end CLI coverage.
- docs/context/codebase-map.md describes the new test surface.

## Validation Checklist

- python3 -m unittest discover -v
- python3 -m abh doctor
- git diff --check
- python3 -m abh roadmap check --json

## Closure Evidence

- tests/
- docs/context/codebase-map.md
- docs/development-roadmap.md
- docs/task-board.md

## Verification Runs

- 

## Audits

- 
