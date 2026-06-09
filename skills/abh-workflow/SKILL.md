---
name: abh-workflow
description: Guide Codex through Attractor Before Harness (ABH) planning, verification, audit, close, onboarding, doctor, roadmap, and health-report workflows. Use when the user asks to manage a task with ABH, create or update plans, decide the next ABH action, run verification, prepare an audit handoff, record an independent audit, close a plan, check ABH readiness, or package existing ABH behavior into a simple agent workflow.
---

# ABH Workflow

## Core Rule

Use ABH as the source of workflow truth. Do not replace ABH state machines with chat judgment.

Always preserve this separation:

- Plan defines the slice.
- Verification proves commands ran.
- Audit judges completion.
- Close requires independent passing audit evidence.
- Memory records reusable failures or false assumptions.

## First Step

From the repository root, check whether ABH is available:

```bash
python -m abh --help
```

On Windows repositories with a local virtual environment, prefer:

```powershell
.venv\Scripts\python.exe -m abh --help
```

If ABH is not installed, use the repository source with `python -m abh` or ask the user whether to install with the project documented `uvx --from git+...` / editable path.

## Default Workflow

Run these commands before choosing work:

```bash
python -m abh onboarding check --json
python -m abh next --json
python -m abh doctor --json
python -m abh roadmap check --json
```

Follow `abh next --json` unless there is a concrete reason not to. If it recommends completing a draft plan, do not implement code first.

## Plan Rules

Before implementation, the active plan must have:

- Active attractor binding.
- Baseline.
- Goals.
- Non-goals.
- Exit criteria.
- Validation checklist.
- Closure evidence.

If any are missing, use `abh plan update <plan-id>` or create a new focused plan. Do not treat a materialized but empty plan as executable.

## Verification Rules

Run:

```bash
python -m abh verify run <plan-id> --json
```

If verification fails, inspect `failed_checks` and `failure_classifications`. Fix the root cause or narrow the plan. Do not request audit until latest verification is passing and fresh.

## Audit Rules

When latest verification is fresh pass, request or prepare audit:

```bash
python -m abh audit bundle <plan-id> --json
python -m abh audit request <plan-id> --id <audit-id> --auditor human-independent-review --scope "<scope>" --evidence <path>
```

Implementation sessions must not self-sign independent audit. Give the user the audit bundle prompt for a separate window or reviewer.

Only record an audit verdict after receiving an independent result:

```bash
python -m abh audit record <audit-id> --result pass|fail|partial|need_info --rationale "<rationale>" --auditor-context "<context>" --independence independent --verification-id <verification-id>
```

## Close Rules

Close only after ABH has a fresh passing verification and an independent passing audit tied to that verification:

```bash
python -m abh close <plan-id>
```

If audit fails, record the fail result first, then either implement the missing evidence or block/defer the plan and create a narrower plan.

## Blocked Or Deferred Work

Use blocked/deferred posture when a plan is valid but not worth implementing now, or when audit proves the plan should not be treated as complete.

Document the reason in the plan, audit, roadmap, or task-board owner docs. Prefer creating a smaller plan over weakening a broad plan just to close it.

## References

For command examples and decision details, read `references/command-flow.md` only when needed.
