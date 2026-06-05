# Commitment Phase State Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an optional Commitment Phase State structure to plans so ABH can distinguish current stable commitments, active change pressure, target stable state, conversion proof, and residual non-blocking pressure without breaking legacy plans.

**Architecture:** Extend `PlanRecord` with a small nested structure that defaults empty on legacy reads, render it into plan Markdown and templates, and expose it through plan status JSON. Keep the first slice additive and backward-compatible: no new ready/close blockers, no inference engine, and no semantic automation beyond explicit user-provided plan fields.

**Tech Stack:** Python standard library, existing ABH plan/model/CLI stack, `unittest`.

---

## File Structure

- Modify `abh/models.py`: add Commitment Phase State data structures, serialization, defaults, and legacy read behavior.
- Modify `abh/plans.py`: render the new structure in plan Markdown and include it in plan verification payloads as appropriate.
- Modify `abh/cli.py`: accept optional Commitment Phase State fields on plan create/update and expose them in JSON output.
- Modify `tests/test_cli.py`: add RED/GREEN coverage for legacy reads, create/update flows, JSON output, and Markdown rendering.
- Modify `docs/plans/templates/plan-template.md`: explain the new structure in plan authoring.
- Modify `docs/architecture/quality-signals.md`: align terminology with stable state, active pressure, target state, conversion proof, and residual pressure.
- Modify `docs/development-roadmap.md`, `docs/task-board.md`, and `docs/context/codebase-map.md`: reflect the active slice and where the new structure lives.

## Task 1: Plan State And Documentation

- [ ] **Step 1: Add implementation plan as closure evidence**

Run:

```bash
python3 -m abh plan update plan-049-commitment-phase-state --closure-evidence docs/superpowers/plans/2026-06-05-commitment-phase-state.md --json
```

Expected: `plan-049` closure evidence includes this implementation plan.

- [ ] **Step 2: Update roadmap/task board sprint state**

Add Sprint 45 tracking in `docs/task-board.md` and make `plan-049` the explicit active Stage 6 slice in planning docs.

- [ ] **Step 3: Transition `plan-049` to running**

Run:

```bash
python3 -m abh plan transition plan-049-commitment-phase-state --to ready
python3 -m abh plan transition plan-049-commitment-phase-state --to running
```

Expected: both transitions succeed.

## Task 2: RED Tests For Legacy Defaults And JSON Shape

- [ ] **Step 1: Add legacy read default test**

Add a test showing a legacy `PlanRecord.from_dict()` without Commitment Phase State fields still reads successfully with empty defaults.

- [ ] **Step 2: Add create/status JSON test**

Add a test that creates a plan with explicit Commitment Phase State fields and asserts `plan status --json` returns them in machine-readable form.

- [ ] **Step 3: Run focused tests and verify RED**

Run:

```bash
python3 -m unittest tests.test_cli.CliTests.test_plan_commitment_phase_state_legacy_defaults tests.test_cli.CliTests.test_plan_status_json_exposes_commitment_phase_state -v
```

Expected: fail because the fields do not exist yet.

## Task 3: Model And Rendering Implementation

- [ ] **Step 1: Add Commitment Phase State model fields**

Extend `PlanRecord` with additive fields for:

- stable state now
- active change pressure
- target stable state
- conversion proof
- residual pressure

Use empty-list/string defaults so legacy reads remain valid.

- [ ] **Step 2: Add serialization and legacy read defaults**

Update `to_dict()` / `from_dict()` to round-trip the new fields and default missing legacy values cleanly.

- [ ] **Step 3: Render Commitment Phase State in plan Markdown**

Update `render_plan_markdown()` to include a dedicated Commitment Phase State section that stays readable when fields are empty.

- [ ] **Step 4: Include the new fields in plan templates**

Extend `docs/plans/templates/plan-template.md` with a brief authoring section for the new structure.

## Task 4: CLI Surface

- [ ] **Step 1: Add create/update CLI arguments**

Extend `plan create` and `plan update` to accept additive Commitment Phase State arguments without making them mandatory.

- [ ] **Step 2: Surface the fields in JSON outputs**

Ensure `plan status --json`, `plan create --json`, and `plan update --json` include the new structure.

- [ ] **Step 3: Add Markdown rendering and update coverage**

Add tests that assert plan Markdown includes the Commitment Phase State section and the new values after create/update flows.

## Task 5: Docs And Verification

- [ ] **Step 1: Align quality-signals vocabulary**

Update `docs/architecture/quality-signals.md` so Commitment Phase State terminology matches the implemented field names.

- [ ] **Step 2: Update codebase map**

Document where Commitment Phase State lives in runtime modules and tests.

- [ ] **Step 3: Run full verification**

Run:

```bash
python3 -m unittest tests/test_cli.py -v
python3 -m abh doctor
git diff --check
python3 -m abh roadmap check --json
python3 -m abh verify run plan-049-commitment-phase-state --json
```

Expected: all commands pass.
