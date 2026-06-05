from __future__ import annotations

import io
import os
import tempfile
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import TestCase

from abh.cli import main


class Chdir:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.previous: Path | None = None

    def __enter__(self):
        self.previous = Path.cwd()
        os.chdir(self.path)
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.previous is not None:
            os.chdir(self.previous)


class WorkspaceCliTestCase(TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "docs" / "architecture" / "attractors").mkdir(parents=True, exist_ok=True)
        (self.root / "docs" / "architecture" / "attractors" / "abh-core-attractor.md").write_text(
            "# Attractor\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def run_cli(self, *args: str) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with Chdir(self.root), redirect_stdout(stdout), redirect_stderr(stderr):
            code = main(list(args))
        return code, stdout.getvalue(), stderr.getvalue()

    def create_ready_plan(
        self,
        plan_id: str = "plan-200-audit",
        *,
        title: str = "Audited Plan",
        goal: str = "ship audited close",
        non_goal: str = "remote service",
        exit_criterion: str = "audit passes",
        validation: str = "unit tests pass",
        closure_evidence: str = "docs/audits/audit-200-audit.md",
    ) -> None:
        code, out, err = self.run_cli(
            "plan",
            "create",
            "--id",
            plan_id,
            "--title",
            title,
            "--attractor",
            "docs/architecture/attractors/abh-core-attractor.md",
            "--baseline",
            "baseline",
            "--status",
            "ready",
            "--goal",
            goal,
            "--non-goal",
            non_goal,
            "--exit-criterion",
            exit_criterion,
            "--validation",
            validation,
            "--closure-evidence",
            closure_evidence,
        )
        self.assertEqual(code, 0, err)


class WorkspaceMcpTestCase(WorkspaceCliTestCase):
    def create_ready_plan(self, plan_id: str = "plan-mcp-contract") -> None:
        code, out, err = self.run_cli(
            "plan",
            "create",
            "--id",
            plan_id,
            "--title",
            "MCP Contract Plan",
            "--attractor",
            "docs/architecture/attractors/abh-core-attractor.md",
            "--baseline",
            "baseline",
            "--status",
            "ready",
            "--goal",
            "expose readonly mcp",
            "--non-goal",
            "write tools",
            "--exit-criterion",
            "mcp tests pass",
            "--validation",
            "unit tests pass",
            "--closure-evidence",
            "tests/test_mcp_server.py",
        )
        self.assertEqual(code, 0, err)

    def call_mcp(self, message: dict[str, object]) -> dict[str, object]:
        from abh.mcp_server import handle_message

        with Chdir(self.root):
            response = handle_message(message)
        self.assertIsNotNone(response)
        assert response is not None
        return response
