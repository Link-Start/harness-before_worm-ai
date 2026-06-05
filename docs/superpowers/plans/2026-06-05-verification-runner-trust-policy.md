# Verification Runner Trust Policy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make ABH verify-runner local shell trust semantics explicit in metadata and docs, while strengthening recursive verify guard detection.

**Architecture:** Keep the runner local and synchronous. Do not add a sandbox or change checklist execution; instead, expose the current mode as `trusted_local_shell`, record policy metadata in verification environment snapshots, and broaden recursive guard parsing to catch both Python module invocations and ABH console-script invocations.

**Tech Stack:** Python standard library, existing ABH verification runner, `unittest`.

---

## File Structure

- Modify `abh/verifications.py`: add runner policy constants, policy metadata in `environment_snapshot()`, and stronger recursive verify command detection.
- Modify `tests/test_cli.py`: add recursive guard tests for ABH console scripts and Python executable paths; add environment policy metadata assertions.
- Modify `README.md`: clarify `local_shell` and `trusted_local_shell` semantics and non-guarantees.
- Modify planning docs: update `docs/development-roadmap.md`, `docs/task-board.md`, and this implementation plan.

## Task 1: Red Tests For Runner Policy Metadata

- [x] **Step 1: Add policy metadata assertion**

Extend `test_verify_run_records_environment_metadata` in `tests/test_cli.py` to assert:

```python
self.assertEqual(environment["runner"]["execution_policy"], "trusted_local_shell")
self.assertEqual(environment["runner"]["trust_level"], "local_shell")
self.assertEqual(environment["runner"]["command_source"], "plan_validation_checklist")
self.assertEqual(environment["runner"]["isolation"], "none")
```

- [x] **Step 2: Run focused test and verify RED**

Run:

```bash
python3 -m unittest tests.test_cli.CliTests.test_verify_run_records_environment_metadata -v
```

Expected: fail because `environment["runner"]` does not yet include policy metadata.

## Task 2: Red Tests For Stronger Recursive Guard

- [x] **Step 1: Extend recursive command parser tests**

Extend `test_verify_run_detects_recursive_self_invocation_command` with:

```python
self.assertTrue(is_recursive_verify_command("abh verify run plan-recursive-guard", "plan-recursive-guard"))
self.assertTrue(is_recursive_verify_command(".venv/Scripts/python.exe -m abh verify run plan-recursive-guard", "plan-recursive-guard"))
self.assertTrue(is_recursive_verify_command("py -m abh verify run plan-recursive-guard", "plan-recursive-guard"))
self.assertFalse(is_recursive_verify_command("abh verify run another-plan", "plan-recursive-guard"))
```

- [x] **Step 2: Run focused test and verify RED**

Run:

```bash
python3 -m unittest tests.test_cli.CliTests.test_verify_run_detects_recursive_self_invocation_command -v
```

Expected: fail for at least `abh verify run` and Python executable path forms.

## Task 3: Implementation

- [x] **Step 1: Add policy constants**

In `abh/verifications.py`, add:

```python
RUNNER_EXECUTION_POLICY = "trusted_local_shell"
RUNNER_COMMAND_SOURCE = "plan_validation_checklist"
RUNNER_ISOLATION = "none"
```

- [x] **Step 2: Add policy metadata to environment snapshot**

Extend `environment_snapshot()["runner"]` with:

```python
"execution_policy": RUNNER_EXECUTION_POLICY,
"trust_level": "local_shell",
"command_source": RUNNER_COMMAND_SOURCE,
"isolation": RUNNER_ISOLATION,
```

- [x] **Step 3: Strengthen recursive guard parsing**

Refactor `is_recursive_verify_command()` so it returns true for:

- `python -m abh verify run <plan>`
- `python3 -m abh verify run <plan>`
- `py -m abh verify run <plan>`
- path-like Python executables ending in `python`, `python3`, `python.exe`, or `python3.exe`
- `abh verify run <plan>`

Keep it false for other plan ids and malformed shell strings.

- [x] **Step 4: Run focused tests and verify GREEN**

Run:

```bash
python3 -m unittest tests.test_cli.CliTests.test_verify_run_records_environment_metadata tests.test_cli.CliTests.test_verify_run_detects_recursive_self_invocation_command -v
```

Expected: pass.

## Task 4: Documentation And Plan State

- [x] **Step 1: Update README trust semantics**

Update the `verify run` documentation to state that:

- `local_shell` means ABH executed the checklist through the local shell in the current workspace.
- `trusted_local_shell` means commands are assumed to come from the plan's trusted validation checklist.
- The result is not tamper-proof, not isolated, not a CI attestation, and not safe for unreviewed external commands.

- [x] **Step 2: Add implementation plan closure evidence**

Run:

```bash
python3 -m abh plan update plan-047-verification-runner-trust-policy --closure-evidence docs/superpowers/plans/2026-06-05-verification-runner-trust-policy.md --json
```

- [x] **Step 3: Update roadmap/task board**

Update `docs/development-roadmap.md` and `docs/task-board.md` to show `plan-047-verification-runner-trust-policy` as the active Stage 6 slice.

- [x] **Step 4: Transition plan to running**

Run:

```bash
python3 -m abh plan transition plan-047-verification-runner-trust-policy --to ready
python3 -m abh plan transition plan-047-verification-runner-trust-policy --to running
```

Expected: both transitions succeed.

## Task 5: Full Verification

- [ ] **Step 1: Run full regression suite**

Run:

```bash
python3 -m unittest tests/test_cli.py -v
```

Expected: pass.

- [ ] **Step 2: Run ABH consistency checks**

Run:

```bash
python3 -m abh doctor
git diff --check
python3 -m abh roadmap check --json
```

Expected: doctor reports no issues, diff check is clean, and roadmap check reports no consistency errors.

- [ ] **Step 3: Run plan verification**

Run:

```bash
python3 -m abh verify run plan-047-verification-runner-trust-policy --json
```

Expected: verification result is `pass`.
