# Command Contract Runtime Registry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Start the architecture hardening queue by reducing duplicated command-protocol facts between CLI, MCP, and shared command metadata.

**Architecture:** Keep this first slice deliberately small: do not regenerate argparse or rewrite MCP dispatch yet. Move shared error envelope helpers into `abh.commands`, make CLI and MCP import those helpers from the shared protocol layer, and add tests that lock the adapter dependency direction.

**Tech Stack:** Python standard library, argparse, existing ABH command contract helpers, MCP stdio adapter, `unittest`.

---

## File Structure

- Modify `abh/commands.py`: add shared ABH error categorization and error payload helpers next to JSON envelope helpers.
- Modify `abh/cli.py`: import `abh_error_payload` from `abh.commands` and remove local duplicate helper definitions.
- Modify `abh/mcp_server.py`: import `abh_error_payload` and `make_envelope` from `abh.commands`, not `abh.cli`.
- Modify `tests/test_cli.py`: add a focused protocol-layer regression test.
- Modify planning docs: `.abh/roadmap.json`, `.abh/plans/plan-044-command-contract-runtime-registry.json`, `docs/plans/plan-044-command-contract-runtime-registry.md`, `docs/development-roadmap.md`, and `docs/task-board.md`.

## Task 1: Planning Artifacts

- [ ] **Step 1: Add Stage 6 architecture hardening queue items**

Update `.abh/roadmap.json` with `stage6.command-contract-runtime-registry` as materialized to `plan-044-command-contract-runtime-registry`, followed by queued items for repository write transactions, schema validation/migration, verification runner trust policy, and test suite domain split.

- [ ] **Step 2: Add plan-044 JSON and Markdown**

Create `.abh/plans/plan-044-command-contract-runtime-registry.json` and `docs/plans/plan-044-command-contract-runtime-registry.md` with goals, non-goals, exit criteria, validation checklist, and closure evidence for the first architecture-hardening slice.

- [ ] **Step 3: Update roadmap and task board docs**

Update `docs/development-roadmap.md` and `docs/task-board.md` so future agents can see why these architecture hardening items exist and where they sit relative to `plan-043`.

## Task 2: Red Test For Adapter Dependency Direction

- [ ] **Step 1: Add the failing test**

Add this test in the MCP test area of `tests/test_cli.py`:

```python
    def test_mcp_server_uses_shared_command_error_payload(self) -> None:
        from abh import commands, mcp_server

        self.assertIs(mcp_server.abh_error_payload, commands.abh_error_payload)
```

- [ ] **Step 2: Run the focused test and verify RED**

Run:

```bash
python3 -m unittest tests.test_cli.McpServerTests.test_mcp_server_uses_shared_command_error_payload -v
```

Expected: fail because `abh.commands` does not yet export `abh_error_payload`.

## Task 3: Shared Error Payload Implementation

- [ ] **Step 1: Move helpers into `abh.commands`**

Add `categorize_abh_error()` and `abh_error_payload()` to `abh/commands.py`. Import `AbhError` from `abh.errors`.

- [ ] **Step 2: Update CLI imports**

Change `abh/cli.py` to import `abh_error_payload` from `abh.commands` and remove its local `categorize_abh_error()` and `abh_error_payload()` definitions.

- [ ] **Step 3: Update MCP imports**

Change `abh/mcp_server.py` to import `abh_error_payload` and `make_envelope` from `abh.commands` and remove the dependency on `abh.cli`.

- [ ] **Step 4: Run the focused test and verify GREEN**

Run:

```bash
python3 -m unittest tests.test_cli.McpServerTests.test_mcp_server_uses_shared_command_error_payload -v
```

Expected: pass.

## Task 4: Full Verification

- [ ] **Step 1: Run the main regression suite**

Run:

```bash
python3 -m unittest tests/test_cli.py -v
```

Expected: pass.

- [ ] **Step 2: Run ABH consistency checks**

Run:

```bash
python3 -m abh doctor
python3 -m abh roadmap check --json
git diff --check
```

Expected: doctor reports no issues, roadmap check returns no issues, and diff check is clean.
