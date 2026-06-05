# Test Suite Domain Split Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split the monolithic unittest regression suite into focused domain modules while keeping representative end-to-end CLI coverage and the existing zero-dependency test stack.

**Architecture:** Extract shared workspace test helpers into a small support module, move domain-specific test clusters into dedicated `tests/test_*.py` files, and leave `tests/test_cli.py` as a thin end-to-end CLI smoke layer. Preserve existing assertions and command flows as much as possible so the change is mostly organizational rather than behavioral.

**Tech Stack:** Python standard library, `unittest`, existing ABH CLI/MCP helpers.

---

## File Structure

- Create `tests/__init__.py`: make the `tests` package importable for shared support helpers.
- Create `tests/support.py`: shared temporary-workspace setup, `run_cli()`, and MCP helper base classes.
- Modify `tests/test_cli.py`: reduce to representative end-to-end CLI coverage only.
- Create focused test modules:
  - `tests/test_command_contracts.py`
  - `tests/test_navigation_and_roadmap.py`
  - `tests/test_verifications_and_audits.py`
  - `tests/test_memory_drift_reporting.py`
  - `tests/test_storage_and_doctor.py`
  - `tests/test_models.py`
  - `tests/test_mcp_server.py`
- Modify `docs/context/codebase-map.md`: describe the new test surface.
- Modify `docs/development-roadmap.md` and `docs/task-board.md`: mark `plan-048` as the active Stage 6 slice.

## Task 1: Plan State And Documentation

- [x] **Step 1: Add implementation plan as closure evidence**

Run:

```bash
python3 -m abh plan update plan-048-test-suite-domain-split --closure-evidence docs/superpowers/plans/2026-06-05-test-suite-domain-split.md --json
```

Expected: plan closure evidence includes this implementation plan.

- [x] **Step 2: Update roadmap/task board active focus**

Update `docs/development-roadmap.md` and `docs/task-board.md` so they reflect:

- `plan-047-verification-runner-trust-policy` is closed.
- `plan-048-test-suite-domain-split` is the current active Stage 6 slice.
- Sprint 44 tracks the test-suite split work.

- [x] **Step 3: Transition plan to running**

Run:

```bash
python3 -m abh plan transition plan-048-test-suite-domain-split --to ready
python3 -m abh plan transition plan-048-test-suite-domain-split --to running
```

Expected: both transitions succeed.

## Task 2: Shared Test Support Extraction

- [x] **Step 1: Create shared workspace test helpers**

Create `tests/support.py` with:

- `Chdir`
- `WorkspaceCliTestCase`
- `WorkspaceMcpTestCase`
- shared `run_cli()` and `create_ready_plan()` helpers

Keep the helper API aligned with the existing `CliTests` and `McpServerTests` methods so migrated tests can move without semantic changes.

- [x] **Step 2: Add `tests/__init__.py`**

Create an empty or comment-only `tests/__init__.py` so `tests.support` is importable under unittest discovery.

- [x] **Step 3: Run focused smoke checks**

Run:

```bash
python3 -m unittest tests.test_cli -v
python3 -m unittest tests.test_mcp_server -v
```

Expected: imports resolve and migrated helper classes work.

## Task 3: Move Focused Domain Suites

- [x] **Step 1: Extract MCP tests**

Move `McpServerTests` out of `tests/test_cli.py` into `tests/test_mcp_server.py`, preserving all assertions and helper flows.

- [x] **Step 2: Extract storage and doctor tests**

Move doctor/schema/atomic-write tests into `tests/test_storage_and_doctor.py`.

- [x] **Step 3: Extract model compatibility tests**

Move model serialization/schema/legacy-readability tests into `tests/test_models.py`.

- [x] **Step 4: Extract roadmap/navigation tests**

Move roadmap queue, `abh next`, onboarding, and related navigation tests into `tests/test_navigation_and_roadmap.py`.

- [x] **Step 5: Extract verification/audit tests**

Move verification runner, audit, and close-gate tests into `tests/test_verifications_and_audits.py`.

- [x] **Step 6: Extract reporting/memory/drift tests**

Move memory, drift, reporting, and route tests into `tests/test_memory_drift_reporting.py`.

- [x] **Step 7: Extract command-contract tests**

Move command-contract and JSON-envelope specific tests into `tests/test_command_contracts.py`.

## Task 4: Reduce The Legacy Monolithic File

- [x] **Step 1: Leave only end-to-end CLI smoke coverage in `tests/test_cli.py`**

Keep a compact set of representative flows in `tests/test_cli.py`, such as:

- CLI create/update/transition flow
- one verify-run smoke flow
- one close/audit gate flow
- one init/setup/hook smoke flow

Everything else should live in focused domain modules.

- [x] **Step 2: Update codebase map**

Document the new test surface in `docs/context/codebase-map.md`, replacing the single-file description with module-level responsibilities.

## Task 5: Verification

- [x] **Step 1: Run focused module checks during the split**

Run targeted commands as each module lands, for example:

```bash
python3 -m unittest tests.test_mcp_server -v
python3 -m unittest tests.test_storage_and_doctor -v
python3 -m unittest tests.test_models -v
```

Expected: each migrated module passes independently.

- [x] **Step 2: Run full unittest discovery**

Run:

```bash
python3 -m unittest discover -v
```

Expected: all discovered test modules pass.

- [x] **Step 3: Run repository consistency checks**

Run:

```bash
python3 -m abh doctor
git diff --check
python3 -m abh roadmap check --json
```

Expected: doctor passes, diff check is clean, roadmap check reports no issues.

- [ ] **Step 4: Run plan verification**

Run:

```bash
python3 -m abh verify run plan-048-test-suite-domain-split --json
```

Expected: verification result is `pass`.
