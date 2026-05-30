# Project Health Report Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `abh report health --json` as a read-only semantic pressure report for `plan-042-project-health-report`.

**Architecture:** Add a focused `abh/reporting.py` module that reads existing ABH records and returns one stable health payload. CLI, command contract, and MCP adapters should only translate that payload into the existing JSON envelope and MCP tool result shapes. The report is product-quality-first: it aggregates ordinary metrics and semantic pressure signals, but it does not block close, call models, or write repository state.

**Tech Stack:** Python dataclasses/dicts, existing ABH storage/domain modules, argparse CLI, Agent-First command contracts, MCP stdio adapter, `unittest`.

---

## File Structure

- Create `abh/reporting.py`: read-only health aggregation. It owns metric calculation, semantic pressure signal construction, posture selection, top-risk sorting, and recommended inspections.
- Modify `abh/cli.py`: add `report health --json` and a concise human output.
- Modify `abh/commands.py`: register read-only `report.health` with output key `health_report` and MCP tool `abh_report_health`.
- Modify `abh/mcp_server.py`: expose `abh_report_health` by calling `project_health_report()`.
- Modify `abh/core.py`: re-export `project_health_report` only if tests or existing import style need it.
- Modify `tests/test_cli.py`: add red-green tests for command contract, CLI JSON, empty workspace, repeated drift, stale verification, semantic pressure signals, and MCP tool exposure.
- Modify docs: `README.md`, `docs/architecture/quality-signals.md`, `docs/development-roadmap.md`, `docs/task-board.md`, `docs/architecture/agent-protocol.md`, `docs/context/codebase-map.md`, and `docs/plans/plan-042-project-health-report.md`.

## Payload Shape

`project_health_report()` should return:

```python
{
    "schema_version": "1",
    "posture": "healthy" | "watch" | "at_risk" | "blocked",
    "summary": "short human-readable summary",
    "metrics": {
        "plans": {
            "total": 0,
            "open": 0,
            "closed": 0,
            "close_rate": 0.0,
            "stale_latest_verifications": 0,
        },
        "verification": {
            "latest_pass": 0,
            "latest_fail_or_partial": 0,
            "stale_latest": 0,
            "failure_classifications": {},
        },
        "audit": {
            "total": 0,
            "pass": 0,
            "fail": 0,
            "partial": 0,
            "need_info": 0,
            "independent_pass": 0,
        },
        "drift": {
            "reports": 0,
            "findings": 0,
            "by_type": {},
            "high_or_critical": 0,
        },
        "memory": {
            "total": 0,
            "active": 0,
            "orphaned_active": 0,
            "superseded": 0,
        },
        "doctor": {
            "issues": 0,
        },
        "roadmap": {
            "queued": 0,
            "materialized": 0,
        },
    },
    "semantic_pressure": [
        {
            "id": "pressure-stale-proof-plan-001",
            "kind": "health",
            "type": "stale_proof",
            "severity": "high",
            "confidence": "high",
            "status": "active",
            "summary": "plan-001 latest verification is stale",
            "evidence_refs": ["plan-001", "ver-001"],
            "related_plan_ids": ["plan-001"],
            "related_audit_ids": [],
            "related_memory_ids": [],
            "related_drift_ids": [],
            "recommendation": "Run fresh verification before audit or close.",
        }
    ],
    "top_risks": [],
    "recommended_inspections": [],
}
```

Keep fields present even when lists are empty. Use only JSON-serializable primitives.

## Task 1: Command Contract Red Test

**Files:**
- Modify: `tests/test_cli.py`
- Modify later: `abh/commands.py`

- [ ] **Step 1: Add the failing command contract assertions**

Add this block inside `test_agent_first_command_contract_describes_existing_agent_commands`, after the `audit_bundle` assertions:

```python
        health_report = command_contract("report.health")
        self.assertEqual(health_report.cli_command, "report health")
        self.assertEqual(health_report.mcp_tool, "abh_report_health")
        self.assertTrue(health_report.read_only)
        self.assertEqual(health_report.confirmation, "none")
        self.assertEqual(health_report.side_effects, [])
        self.assertEqual(health_report.output_keys, ["health_report"])
```

- [ ] **Step 2: Run the focused failing test**

Run:

```bash
python3 -m unittest tests.test_cli.CliTests.test_agent_first_command_contract_describes_existing_agent_commands -v
```

Expected: fail with `KeyError` or `AbhError` for missing `report.health`.

- [ ] **Step 3: Register the command contract**

In `abh/commands.py`, add a `CommandContract` near other read-only navigation/reporting commands:

```python
    CommandContract(
        id="report.health",
        cli_command="report health",
        mcp_tool="abh_report_health",
        read_only=True,
        confirmation="none",
        side_effects=[],
        description="Aggregate ABH quality signals into a read-only project health and semantic pressure report.",
        input_schema=input_schema({}),
        output_keys=["health_report"],
        failure_categories=["consistency", "system"],
    ),
```

- [ ] **Step 4: Re-run the focused test**

Run:

```bash
python3 -m unittest tests.test_cli.CliTests.test_agent_first_command_contract_describes_existing_agent_commands -v
```

Expected: pass.

## Task 2: Empty Health Report Red Test

**Files:**
- Modify: `tests/test_cli.py`
- Create later: `abh/reporting.py`

- [ ] **Step 1: Add a CLI JSON test for an empty ABH workspace**

Add this test near the drift/memory/report tests:

```python
    def test_report_health_json_empty_workspace(self) -> None:
        code, out, err = self.run_cli("report", "health", "--json")

        self.assertEqual(code, 0, err)
        payload = json.loads(out)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["command"], "report health")
        report = payload["data"]["health_report"]
        self.assertEqual(report["schema_version"], "1")
        self.assertEqual(report["posture"], "healthy")
        self.assertEqual(report["metrics"]["plans"]["total"], 0)
        self.assertEqual(report["metrics"]["doctor"]["issues"], 0)
        self.assertEqual(report["semantic_pressure"], [])
        self.assertEqual(report["top_risks"], [])
        self.assertIn("no unresolved", report["summary"].lower())
```

- [ ] **Step 2: Run the failing test**

Run:

```bash
python3 -m unittest tests.test_cli.CliTests.test_report_health_json_empty_workspace -v
```

Expected: fail because `report` is not a valid command.

- [ ] **Step 3: Add the CLI parser shell**

In `abh/cli.py`, import the report function:

```python
from .reporting import project_health_report
```

Add `"report_command"` to `command_name()`:

```python
        "report_command",
```

Add this parser block before `doctor_parser`:

```python
    report_parser = subparsers.add_parser("report", help="generate ABH reports")
    report_sub = report_parser.add_subparsers(dest="report_command", required=True)

    report_health = report_sub.add_parser("health", help="report project health and semantic pressure")
    add_json_argument(report_health)
    report_health.set_defaults(handler=handle_report_health)
```

Add the handler near other read-only handlers:

```python
def handle_report_health(args: argparse.Namespace) -> int:
    report = project_health_report()
    if args.json:
        print_json_envelope(ok=True, command=command_name(args), data={"health_report": report})
        return 0
    print(f"health: {report['posture']}")
    print(report["summary"])
    return 0
```

- [ ] **Step 4: Create minimal reporting implementation**

Create `abh/reporting.py`:

```python
from __future__ import annotations

from pathlib import Path
from typing import Any

from .models import SCHEMA_VERSION


def empty_metrics() -> dict[str, Any]:
    return {
        "plans": {"total": 0, "open": 0, "closed": 0, "close_rate": 0.0, "stale_latest_verifications": 0},
        "verification": {"latest_pass": 0, "latest_fail_or_partial": 0, "stale_latest": 0, "failure_classifications": {}},
        "audit": {"total": 0, "pass": 0, "fail": 0, "partial": 0, "need_info": 0, "independent_pass": 0},
        "drift": {"reports": 0, "findings": 0, "by_type": {}, "high_or_critical": 0},
        "memory": {"total": 0, "active": 0, "orphaned_active": 0, "superseded": 0},
        "doctor": {"issues": 0},
        "roadmap": {"queued": 0, "materialized": 0},
    }


def project_health_report(cwd: Path | None = None) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "posture": "healthy",
        "summary": "No unresolved quality risks found.",
        "metrics": empty_metrics(),
        "semantic_pressure": [],
        "top_risks": [],
        "recommended_inspections": [],
    }
```

- [ ] **Step 5: Re-run the focused test**

Run:

```bash
python3 -m unittest tests.test_cli.CliTests.test_report_health_json_empty_workspace -v
```

Expected: pass.

## Task 3: Plan And Verification Metrics

**Files:**
- Modify: `tests/test_cli.py`
- Modify: `abh/reporting.py`

- [ ] **Step 1: Add a stale verification semantic pressure test**

Add:

```python
    def test_report_health_flags_stale_verification_pressure(self) -> None:
        self.run_cli(
            "plan", "create",
            "--id", "plan-health-stale",
            "--title", "Health Stale",
            "--attractor", "docs/architecture/attractors/abh-core-attractor.md",
            "--baseline", "baseline",
            "--status", "ready",
            "--goal", "ship behavior",
            "--non-goal", "web ui",
            "--exit-criterion", "tests pass",
            "--validation", "python3 -m unittest tests/test_cli.py -v",
            "--closure-evidence", "tests/test_cli.py",
        )
        self.run_cli(
            "verify",
            "record",
            "plan-health-stale",
            "--command",
            "old command",
            "--result",
            "pass",
        )

        code, out, err = self.run_cli("report", "health", "--json")

        self.assertEqual(code, 0, err)
        report = json.loads(out)["data"]["health_report"]
        self.assertEqual(report["metrics"]["plans"]["total"], 1)
        self.assertEqual(report["metrics"]["plans"]["open"], 1)
        self.assertEqual(report["metrics"]["verification"]["latest_pass"], 1)
        self.assertEqual(report["metrics"]["verification"]["stale_latest"], 1)
        stale = [item for item in report["semantic_pressure"] if item["type"] == "stale_proof"]
        self.assertEqual(len(stale), 1)
        self.assertEqual(stale[0]["related_plan_ids"], ["plan-health-stale"])
        self.assertEqual(stale[0]["severity"], "high")
        self.assertIn("Run fresh verification", stale[0]["recommendation"])
        self.assertEqual(report["posture"], "at_risk")
```

- [ ] **Step 2: Run the failing test**

Run:

```bash
python3 -m unittest tests.test_cli.CliTests.test_report_health_flags_stale_verification_pressure -v
```

Expected: fail because metrics are still zero.

- [ ] **Step 3: Implement plan and verification aggregation**

Update `abh/reporting.py`:

```python
from .plans import list_plans, verification_freshness_summary
from .verifications import load_verification
```

Add helpers:

```python
SEVERITY_RANK = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}


def pressure_signal(
    *,
    signal_id: str,
    signal_type: str,
    severity: str,
    confidence: str,
    summary: str,
    evidence_refs: list[str],
    recommendation: str,
    related_plan_ids: list[str] | None = None,
    related_audit_ids: list[str] | None = None,
    related_memory_ids: list[str] | None = None,
    related_drift_ids: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "id": signal_id,
        "kind": "health",
        "type": signal_type,
        "severity": severity,
        "confidence": confidence,
        "status": "active",
        "summary": summary,
        "evidence_refs": evidence_refs,
        "related_plan_ids": list(related_plan_ids or []),
        "related_audit_ids": list(related_audit_ids or []),
        "related_memory_ids": list(related_memory_ids or []),
        "related_drift_ids": list(related_drift_ids or []),
        "recommendation": recommendation,
    }


def sorted_risks(signals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(signals, key=lambda item: (-SEVERITY_RANK.get(str(item["severity"]), 0), str(item["id"])))
```

Replace `project_health_report()` with logic that:

```python
    metrics = empty_metrics()
    pressure: list[dict[str, Any]] = []
    plans = list_plans(cwd)
    metrics["plans"]["total"] = len(plans)
    metrics["plans"]["closed"] = len([plan for plan in plans if plan.status == "closed"])
    metrics["plans"]["open"] = metrics["plans"]["total"] - metrics["plans"]["closed"]
    if metrics["plans"]["total"]:
        metrics["plans"]["close_rate"] = metrics["plans"]["closed"] / metrics["plans"]["total"]

    for plan in plans:
        summary = verification_freshness_summary(plan, cwd)
        if summary.get("latest_id"):
            if summary.get("result") == "pass":
                metrics["verification"]["latest_pass"] += 1
            else:
                metrics["verification"]["latest_fail_or_partial"] += 1
        if summary.get("stale"):
            metrics["plans"]["stale_latest_verifications"] += 1
            metrics["verification"]["stale_latest"] += 1
            evidence = [plan.id]
            latest_id = summary.get("latest_id")
            if latest_id:
                evidence.append(str(latest_id))
            pressure.append(
                pressure_signal(
                    signal_id=f"pressure-stale-proof-{plan.id}",
                    signal_type="stale_proof",
                    severity="high",
                    confidence="high",
                    summary=f"{plan.id} latest verification is stale.",
                    evidence_refs=evidence,
                    related_plan_ids=[plan.id],
                    recommendation="Run fresh verification before audit or close.",
                )
            )
        if summary.get("latest_id"):
            run = load_verification(str(summary["latest_id"]), cwd)
            for item in run.failure_classifications:
                category = str(item.get("category", "unknown"))
                counts = metrics["verification"]["failure_classifications"]
                counts[category] = counts.get(category, 0) + 1
```

At the end:

```python
    top_risks = sorted_risks(pressure)[:5]
    posture = "healthy"
    if any(item["severity"] in {"critical", "high"} for item in pressure):
        posture = "at_risk"
    elif pressure:
        posture = "watch"
    summary_text = "No unresolved quality risks found." if not pressure else f"{len(pressure)} unresolved semantic pressure signal(s)."
    return {...}
```

- [ ] **Step 4: Re-run the focused test**

Run:

```bash
python3 -m unittest tests.test_cli.CliTests.test_report_health_flags_stale_verification_pressure -v
```

Expected: pass.

## Task 4: Audit, Drift, Memory, Doctor, And Roadmap Metrics

**Files:**
- Modify: `tests/test_cli.py`
- Modify: `abh/reporting.py`

- [ ] **Step 1: Add a semantic pressure and repeated drift test**

Add:

```python
    def test_report_health_aggregates_drift_memory_and_semantic_pressure(self) -> None:
        drift_source_a = self.root / "drift-a.txt"
        drift_source_b = self.root / "drift-b.txt"
        drift_source_a.write_text("Skipped tests and added external database dependency.\n", encoding="utf-8")
        drift_source_b.write_text("Skipped tests and added another database dependency.\n", encoding="utf-8")

        self.run_cli("drift", "analyze", "--id", "drift-a", "--source", str(drift_source_a), "--json")
        self.run_cli("drift", "analyze", "--id", "drift-b", "--source", str(drift_source_b), "--json")
        self.run_cli(
            "memory",
            "add",
            "--id",
            "mem-orphaned",
            "--type",
            "divergent_pattern",
            "--summary",
            "Orphaned active memory",
            "--context",
            "No typed relationships.",
            "--implication",
            "Future agents cannot reuse it reliably.",
            "--evidence",
            "docs/memory/mem-orphaned.md",
        )

        code, out, err = self.run_cli("report", "health", "--json")

        self.assertEqual(code, 0, err)
        report = json.loads(out)["data"]["health_report"]
        self.assertEqual(report["metrics"]["drift"]["reports"], 2)
        self.assertGreaterEqual(report["metrics"]["drift"]["findings"], 2)
        self.assertGreaterEqual(report["metrics"]["drift"]["by_type"]["dependency_drift"], 2)
        self.assertEqual(report["metrics"]["memory"]["orphaned_active"], 1)
        pressure_types = {item["type"] for item in report["semantic_pressure"]}
        self.assertIn("repeated_leakage", pressure_types)
        self.assertIn("orphaned_memory", pressure_types)
        self.assertIn("j_flow_only_evidence", pressure_types)
        self.assertTrue(report["recommended_inspections"])
```

- [ ] **Step 2: Run the failing test**

Run:

```bash
python3 -m unittest tests.test_cli.CliTests.test_report_health_aggregates_drift_memory_and_semantic_pressure -v
```

Expected: fail because drift/memory metrics are missing.

- [ ] **Step 3: Implement aggregation**

In `abh/reporting.py`, import:

```python
from .audits import list_audits
from .core import doctor
from .memory import list_memories
from .mcp_server import list_drift_reports
from .roadmap import list_roadmap_items
```

If importing `list_drift_reports` from `mcp_server` creates a dependency smell, move that helper into `abh/drift.py` and update `mcp_server.py` to import it from there.

Add these behaviors:

- Audit metrics: count `result` values and `independent_pass`.
- Drift metrics: count reports, findings, `by_type`, and high/critical findings.
- Repeated leakage: when a drift type appears at least twice, add `repeated_leakage` with `severity="medium"`, related drift ids, and recommendation `"Review repeated drift family before starting related roadmap work."`
- J-flow-only evidence: when a drift report has findings but no related memory records or plan references, add `j_flow_only_evidence` with `severity="medium"`, because the finding is routed into a report but not connected to reusable memory or plan pressure.
- Memory metrics: count total, active, superseded, and active records where `tags`, `related_plan_ids`, `related_audit_ids`, and `related_drift_ids` are all empty. Add `orphaned_memory` pressure for each orphaned active memory.
- Doctor metrics: `len(doctor())`.
- Roadmap metrics: queued/materialized counts from `list_roadmap_items()`.

- [ ] **Step 4: Add recommended inspections**

Generate recommendations from top risks:

```python
recommended_inspections = [
    {
        "reason": risk["summary"],
        "command": "abh memory search --status active --json" if risk["type"] == "orphaned_memory" else "abh drift list --json",
        "risk_id": risk["id"],
    }
    for risk in top_risks
]
```

- [ ] **Step 5: Re-run the focused test**

Run:

```bash
python3 -m unittest tests.test_cli.CliTests.test_report_health_aggregates_drift_memory_and_semantic_pressure -v
```

Expected: pass.

## Task 5: MCP Exposure

**Files:**
- Modify: `tests/test_cli.py`
- Modify: `abh/mcp_server.py`

- [ ] **Step 1: Add MCP tool definition and call assertions**

Add to an existing MCP command-contract/tool test, or create:

```python
    def test_mcp_exposes_report_health_tool(self) -> None:
        from abh.commands import mcp_tool_names
        from abh.mcp_server import TOOL_HANDLERS

        self.assertIn("abh_report_health", mcp_tool_names())
        self.assertIn("abh_report_health", TOOL_HANDLERS)
        with Chdir(self.root):
            result = TOOL_HANDLERS["abh_report_health"]({})
        self.assertIn("health_report", result)
        self.assertEqual(result["health_report"]["schema_version"], "1")
```

- [ ] **Step 2: Run the failing test**

Run:

```bash
python3 -m unittest tests.test_cli.CliTests.test_mcp_exposes_report_health_tool -v
```

Expected: fail because the handler is not registered.

- [ ] **Step 3: Register MCP handler**

In `abh/mcp_server.py`, import:

```python
from .reporting import project_health_report
```

Add:

```python
def call_report_health(arguments: dict[str, Any]) -> dict[str, Any]:
    return {"health_report": project_health_report()}
```

Add to `TOOL_HANDLERS`:

```python
    "abh_report_health": call_report_health,
```

- [ ] **Step 4: Re-run MCP focused test**

Run:

```bash
python3 -m unittest tests.test_cli.CliTests.test_mcp_exposes_report_health_tool -v
```

Expected: pass.

## Task 6: Documentation And Plan Closure Prep

**Files:**
- Modify: `README.md`
- Modify: `docs/architecture/quality-signals.md`
- Modify: `docs/architecture/agent-protocol.md`
- Modify: `docs/context/codebase-map.md`
- Modify: `docs/development-roadmap.md`
- Modify: `docs/task-board.md`
- Modify: `docs/plans/plan-042-project-health-report.md`

- [ ] **Step 1: Update README command docs**

Add a short `abh report health --json` section near drift/memory docs:

```markdown
### Project Health Report

`abh report health --json` is read-only. It aggregates plan, verification, audit, drift, memory, doctor, and roadmap signals into a semantic pressure report. The report highlights top quality risks such as stale proof, repeated drift, orphaned memory, J-flow-only evidence, and semantic leakage, but it does not block close or release by itself.
```

- [ ] **Step 2: Update quality signal docs**

Ensure `docs/architecture/quality-signals.md` documents the exact signal types implemented:

```markdown
- `stale_proof`
- `repeated_leakage`
- `orphaned_memory`
- `j_flow_only_evidence`
```

If `semantic_leakage` or `unbound_commitment_pressure` are not implemented in this slice, state that they are reserved future signal types.

- [ ] **Step 3: Update Agent Protocol and codebase map**

Record that `report.health` is read-only, has MCP tool `abh_report_health`, and is an agent-navigation input, not a close gate.

- [ ] **Step 4: Update plan-042 closure evidence**

After implementation, make sure `docs/plans/plan-042-project-health-report.md` closure evidence includes all touched runtime/docs files and the eventual audit id.

## Task 7: Full Verification

**Files:**
- All touched files

- [ ] **Step 1: Run the full test suite**

Run:

```bash
python3 -m unittest tests/test_cli.py -v
```

Expected: all tests pass.

- [ ] **Step 2: Run ABH consistency checks**

Run:

```bash
python3 -m abh doctor
python3 -m abh roadmap check --json
git diff --check
python3 -m abh report health --json
python3 -m abh plan status plan-042-project-health-report --json
```

Expected:

- `doctor: ok`
- roadmap JSON has `"issues": []`
- diff check has no output
- report health returns a JSON envelope with `data.health_report`
- plan status returns `plan-042-project-health-report`

- [ ] **Step 3: Record verification through ABH**

Run:

```bash
python3 -m abh verify run plan-042-project-health-report --json
```

Expected: pass verification record is written and linked to the plan.

- [ ] **Step 4: Request independent audit**

Run:

```bash
python3 -m abh audit bundle plan-042-project-health-report --json
```

Use the generated bundle with an independent reviewer. Record the resulting audit with `--independence independent` and the latest verification id.

- [ ] **Step 5: Close through ABH**

After a fresh independent pass audit:

```bash
python3 -m abh plan transition plan-042-project-health-report --to closing
python3 -m abh close plan-042-project-health-report
```

Expected: plan closes only if independent/fresh audit gate is satisfied.

## Self-Review Notes

- Spec coverage: the plan covers read-only report command, metrics, semantic pressure signals, command contract, MCP exposure, docs, and ABH verification/audit/close.
- Scope control: Reference Set, Commitment Phase State, Audit Semantic Conservation, and Owner Doc Stable Commitments stay in queued follow-up items and are not implemented here.
- Type consistency: the output key is always `health_report`; the command id is `report.health`; the MCP tool is `abh_report_health`; the CLI command is `report health`.
