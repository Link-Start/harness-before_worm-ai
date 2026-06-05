from __future__ import annotations

import json

from abh.models import DriftReport
from abh.storage import drift_json_path, write_json
from tests.support import Chdir, WorkspaceCliTestCase


class MemoryDriftReportingTests(WorkspaceCliTestCase):
    def test_memory_add_and_search_by_type_and_keyword(self) -> None:
        code, out, err = self.run_cli(
            "memory",
            "add",
            "--id",
            "mem-001",
            "--type",
            "overturned_completion",
            "--summary",
            "Audit overturned a premature close",
            "--context",
            "Close was attempted without evidence.",
            "--evidence",
            "docs/audits/audit-200-audit.md",
            "--related",
            "plan-200-audit",
            "--implication",
            "Require pass audit before close.",
        )
        self.assertEqual(code, 0, err)
        self.assertIn("recorded memory mem-001", out)
        self.assertTrue((self.root / ".abh" / "memory" / "mem-001.json").exists())
        self.assertTrue((self.root / "docs" / "memory" / "mem-001.md").exists())

        code, out, err = self.run_cli(
            "memory",
            "search",
            "--type",
            "overturned_completion",
            "--query",
            "premature",
        )
        self.assertEqual(code, 0, err)
        self.assertIn("mem-001 [overturned_completion]", out)
        self.assertIn("Audit overturned a premature close", out)

    def test_memory_metadata_is_recorded_searchable_and_rendered(self) -> None:
        code, out, err = self.run_cli(
            "memory",
            "add",
            "--id",
            "mem-quality-001",
            "--type",
            "false_assumption",
            "--summary",
            "Quality metadata makes memory reusable",
            "--context",
            "A plan repeated a previously rejected shortcut.",
            "--evidence",
            "docs/audits/audit-040-drift-quality.md",
            "--tag",
            "quality-signal",
            "--tag",
            "audit",
            "--status",
            "active",
            "--related-plan",
            "plan-040-drift-quality",
            "--related-audit",
            "audit-040-drift-quality",
            "--related-drift",
            "drift-quality-001",
            "--superseded-by",
            "mem-quality-002",
            "--related",
            "plan-040-drift-quality",
            "--implication",
            "Route and audit flows should surface reusable memory.",
        )

        self.assertEqual(code, 0, err)
        payload = json.loads((self.root / ".abh" / "memory" / "mem-quality-001.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["tags"], ["quality-signal", "audit"])
        self.assertEqual(payload["status"], "active")
        self.assertEqual(payload["related_plan_ids"], ["plan-040-drift-quality"])
        self.assertEqual(payload["related_audit_ids"], ["audit-040-drift-quality"])
        self.assertEqual(payload["related_drift_ids"], ["drift-quality-001"])
        self.assertEqual(payload["superseded_by"], "mem-quality-002")

        markdown = (self.root / "docs" / "memory" / "mem-quality-001.md").read_text(encoding="utf-8")
        self.assertIn("- Tags: quality-signal, audit", markdown)
        self.assertIn("- Related Plans: plan-040-drift-quality", markdown)
        self.assertIn("- Related Audits: audit-040-drift-quality", markdown)
        self.assertIn("- Related Drift Reports: drift-quality-001", markdown)
        self.assertIn("- Superseded By: mem-quality-002", markdown)

        code, out, err = self.run_cli(
            "memory",
            "search",
            "--status",
            "active",
            "--related-plan",
            "plan-040-drift-quality",
            "--tag",
            "quality-signal",
            "--json",
        )
        self.assertEqual(code, 0, err)
        result = json.loads(out)["data"]["memories"]
        self.assertEqual([memory["id"] for memory in result], ["mem-quality-001"])
        self.assertEqual(result[0]["related_plan_ids"], ["plan-040-drift-quality"])

    def test_memory_legacy_records_get_metadata_defaults(self) -> None:
        (self.root / ".abh" / "memory").mkdir(parents=True, exist_ok=True)
        write_json(
            self.root / ".abh" / "memory" / "mem-legacy.json",
            {
                "schema_version": "1",
                "id": "mem-legacy",
                "type": "rejected_path",
                "summary": "legacy memory",
                "context": "created before memory index",
                "implication": "legacy reads still work",
                "related": ["plan-old"],
                "evidence": ["docs/memory/mem-legacy.md"],
            },
        )

        code, out, err = self.run_cli("memory", "list", "--json")

        self.assertEqual(code, 0, err)
        memory = json.loads(out)["data"]["memories"][0]
        self.assertEqual(memory["id"], "mem-legacy")
        self.assertEqual(memory["status"], "active")
        self.assertEqual(memory["tags"], [])
        self.assertEqual(memory["related_plan_ids"], [])
        self.assertEqual(memory["related_audit_ids"], [])
        self.assertEqual(memory["related_drift_ids"], [])
        self.assertEqual(memory["superseded_by"], "")

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

    def test_report_health_flags_stale_verification_pressure(self) -> None:
        self.run_cli(
            "plan",
            "create",
            "--id",
            "plan-health-stale",
            "--title",
            "Health Stale",
            "--attractor",
            "docs/architecture/attractors/abh-core-attractor.md",
            "--baseline",
            "baseline",
            "--status",
            "ready",
            "--goal",
            "ship behavior",
            "--non-goal",
            "web ui",
            "--exit-criterion",
            "tests pass",
            "--validation",
            "python3 -m unittest tests/test_cli.py -v",
            "--closure-evidence",
            "tests/test_memory_drift_reporting.py",
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

    def test_mcp_exposes_report_health_tool(self) -> None:
        from abh.commands import mcp_tool_names
        from abh.mcp_server import TOOL_HANDLERS

        self.assertIn("abh_report_health", mcp_tool_names())
        self.assertIn("abh_report_health", TOOL_HANDLERS)
        with Chdir(self.root):
            result = TOOL_HANDLERS["abh_report_health"]({})
        self.assertIn("health_report", result)
        self.assertEqual(result["health_report"]["schema_version"], "1")

    def test_route_recommends_reading_order_for_close_question(self) -> None:
        code, out, err = self.run_cli(
            "route",
            "--question",
            "Can we close this plan after the implementation claims completion?",
        )
        self.assertEqual(code, 0, err)
        self.assertIn("Route: completion_audit", out)
        self.assertIn("docs/plans/", out)
        self.assertIn("docs/audits/", out)
        self.assertIn("docs/memory/", out)

    def test_drift_analyze_detects_patterns_and_can_write_memory(self) -> None:
        drift_source = self.root / "drift-source.txt"
        drift_source.write_text(
            "\n".join(
                [
                    "Imported a remote database dependency even though the plan said no external database.",
                    "Moved audit logic into the plan manager boundary.",
                    "Skipped tests and renamed ready to prepared in documentation.",
                ]
            ),
            encoding="utf-8",
        )

        code, out, err = self.run_cli(
            "drift",
            "analyze",
            "--id",
            "drift-001",
            "--source",
            str(drift_source),
            "--evidence",
            "drift-source.txt",
            "--memory-id",
            "mem-drift-001",
        )
        self.assertEqual(code, 0, err)
        self.assertIn("drift-001", out)
        self.assertIn("boundary_drift", out)
        self.assertIn("dependency_drift", out)
        self.assertIn("test_drift", out)
        self.assertIn("terminology_drift", out)
        self.assertTrue((self.root / ".abh" / "drift" / "drift-001.json").exists())
        self.assertTrue((self.root / "docs" / "drift" / "drift-001.md").exists())
        self.assertTrue((self.root / ".abh" / "memory" / "mem-drift-001.json").exists())

        code, out, err = self.run_cli(
            "memory",
            "search",
            "--type",
            "divergent_pattern",
            "--query",
            "dependency_drift",
        )
        self.assertEqual(code, 0, err)
        self.assertIn("mem-drift-001 [divergent_pattern]", out)

    def test_drift_analyze_json_returns_quality_signal_metadata(self) -> None:
        drift_source = self.root / "drift-quality.txt"
        drift_source.write_text(
            "Imported a remote database dependency even though the plan said no external database.\n",
            encoding="utf-8",
        )

        code, out, err = self.run_cli(
            "drift",
            "analyze",
            "--id",
            "drift-quality-001",
            "--source",
            str(drift_source),
            "--evidence",
            "drift-quality.txt",
            "--json",
        )

        self.assertEqual(code, 0, err)
        payload = json.loads(out)
        finding = payload["data"]["drift_report"]["findings"][0]
        self.assertEqual(finding["type"], "dependency_drift")
        self.assertEqual(finding["severity"], "high")
        self.assertEqual(finding["confidence"], "high")
        self.assertEqual(finding["rule_id"], "dependency_drift")
        self.assertEqual(finding["evidence_path"], "drift-quality.txt")
        self.assertEqual(finding["matched_span"]["text"], "database")
        self.assertIn("remote database dependency", finding["source_excerpt"])
        self.assertIn("Review plan non-goals", finding["recommendation"])

    def test_drift_report_legacy_findings_remain_readable(self) -> None:
        with Chdir(self.root):
            write_json(
                drift_json_path("drift-legacy"),
                {
                    "schema_version": "1",
                    "id": "drift-legacy",
                    "source": "legacy.txt",
                    "findings": [
                        {
                            "type": "dependency_drift",
                            "evidence": "matched keywords: database",
                            "recommendation": "Review dependency drift.",
                        }
                    ],
                    "evidence": [],
                    "follow_ups": [],
                    "created_at": "2026-01-01T00:00:00+00:00",
                    "updated_at": "2026-01-01T00:00:00+00:00",
                    "doc_path": "",
                },
            )

        code, out, err = self.run_cli("drift", "analyze", "--id", "drift-new", "--source", __file__, "--json")
        self.assertEqual(code, 0, err)

        legacy_data = json.loads((self.root / ".abh" / "drift" / "drift-legacy.json").read_text(encoding="utf-8"))
        legacy_report = DriftReport.from_dict(legacy_data)
        finding = legacy_report.to_dict()["findings"][0]
        self.assertEqual(finding["type"], "dependency_drift")
        self.assertEqual(finding["severity"], "unknown")
        self.assertEqual(finding["confidence"], "unknown")

    def test_memory_list_returns_all_memories(self) -> None:
        self.run_cli(
            "memory", "add",
            "--id", "mem-list-a",
            "--type", "false_assumption",
            "--summary", "list test assumption",
            "--context", "testing memory list",
            "--implication", "list works",
            "--evidence", "tests/test_memory_drift_reporting.py",
        )
        self.run_cli(
            "memory", "add",
            "--id", "mem-list-b",
            "--type", "rejected_path",
            "--summary", "another list test",
            "--context", "testing memory list again",
            "--implication", "list works twice",
            "--evidence", "tests/test_memory_drift_reporting.py",
        )
        code, out, err = self.run_cli("memory", "list")
        self.assertEqual(code, 0, err)
        self.assertIn("mem-list-a  [false_assumption]  list test assumption", out)
        self.assertIn("mem-list-b  [rejected_path]  another list test", out)
        self.assertIn("total: 2 memory record(s)", out)

    def test_route_injects_active_plans(self) -> None:
        self.run_cli(
            "plan", "create",
            "--id", "plan-route-active",
            "--title", "Active Plan",
            "--attractor", "docs/architecture/attractors/abh-core-attractor.md",
            "--baseline", "baseline",
            "--status", "ready",
            "--goal", "test route injection",
            "--non-goal", "web ui",
            "--exit-criterion", "route test passes",
            "--validation", "unit tests pass",
            "--closure-evidence", "tests/test_memory_drift_reporting.py",
        )
        self.run_cli(
            "verify", "record",
            "plan-route-active",
            "--command", "python -m pytest",
            "--result", "pass",
        )
        self.run_cli(
            "plan", "transition", "plan-route-active", "--to", "running",
        )
        code, out, err = self.run_cli("route", "--question", "Can we close this plan?")
        self.assertEqual(code, 0, err)
        self.assertIn("Route: completion_audit", out)
        self.assertIn("active plans", out.lower())
        self.assertIn("plan-route-active", out)

    def test_drift_with_plan_detects_non_goal_violation(self) -> None:
        drift_source = self.root / "drift-plan.txt"
        drift_source.write_text("重构存储层并引入外部服务\n", encoding="utf-8")
        self.run_cli(
            "plan", "create",
            "--id", "plan-drift-baseline",
            "--title", "Drift Baseline Plan",
            "--attractor", "docs/architecture/attractors/abh-core-attractor.md",
            "--baseline", "baseline",
            "--status", "ready",
            "--goal", "cli commands",
            "--non-goal", "不重构存储层",
            "--exit-criterion", "drift test passes",
            "--validation", "unit tests pass",
            "--closure-evidence", "tests/test_memory_drift_reporting.py",
        )
        code, out, err = self.run_cli(
            "drift", "analyze",
            "--id", "drift-plan-001",
            "--source", str(drift_source),
            "--plan", "plan-drift-baseline",
        )
        self.assertEqual(code, 0, err)
        self.assertIn("boundary_drift", out)
        self.assertIn("plan non-goal violation", out)

        report = json.loads((self.root / ".abh" / "drift" / "drift-plan-001.json").read_text(encoding="utf-8"))
        finding = next(item for item in report["findings"] if item["rule_id"] == "plan_non_goal:plan-drift-baseline")
        self.assertEqual(finding["severity"], "high")
        self.assertEqual(finding["confidence"], "high")
        self.assertEqual(finding["evidence_path"], str(drift_source))
