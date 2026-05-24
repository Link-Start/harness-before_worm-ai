from __future__ import annotations

import shlex
import subprocess
import time
import uuid
from pathlib import Path

from .errors import AbhError
from .models import VERIFICATION_RESULTS, VerificationRun
from .plans import load_plan, save_plan
from .storage import ensure_workspace, read_json, verification_path, write_json


def load_verification(run_id: str, cwd: Path | None = None) -> VerificationRun:
    path = verification_path(run_id, cwd)
    if not path.exists():
        raise AbhError(f"verification run not found: {run_id}")
    return VerificationRun.from_dict(read_json(path))


def record_verification(
    *,
    plan_id: str,
    command: str,
    result: str,
    artifacts: list[str] | None = None,
    failed_checks: list[str] | None = None,
    cwd: Path | None = None,
) -> VerificationRun:
    if result not in VERIFICATION_RESULTS:
        raise AbhError(f"invalid verification result: {result}")
    if not command.strip():
        raise AbhError("verification command is required")
    plan = load_plan(plan_id, cwd)
    ensure_workspace(cwd)
    run = VerificationRun(
        id=f"ver-{uuid.uuid4().hex[:12]}",
        plan_id=plan_id,
        command=command,
        result=result,
        artifacts=list(artifacts or []),
        failed_checks=list(failed_checks or []),
    )
    write_json(verification_path(run.id, cwd), run.to_dict())
    plan.verification_runs.append(run.id)
    if result in {"fail", "partial"} and plan.status in {"ready", "running"}:
        plan.status = "blocked"
    save_plan(plan, cwd)
    return run


def is_recursive_verify_command(command: str, plan_id: str) -> bool:
    try:
        parts = shlex.split(command)
    except ValueError:
        return False
    if len(parts) < 5:
        return False
    for index in range(len(parts) - 4):
        if parts[index:index + 4] == ["python3", "-m", "abh", "verify"] and "run" in parts[index + 4:]:
            return plan_id in parts[index + 4:]
        if parts[index:index + 4] == ["python", "-m", "abh", "verify"] and "run" in parts[index + 4:]:
            return plan_id in parts[index + 4:]
    return False


def run_verification(
    *,
    plan_id: str,
    timeout_seconds: int = 120,
    cwd: Path | None = None,
) -> VerificationRun:
    plan = load_plan(plan_id, cwd)
    if not plan.validation_checklist:
        raise AbhError("plan has no validation checklist")
    if timeout_seconds <= 0:
        raise AbhError("timeout must be greater than zero")

    root = Path.cwd() if cwd is None else Path(cwd)
    artifacts: list[str] = []
    failed_checks: list[str] = []
    commands = list(plan.validation_checklist)

    for command in commands:
        if is_recursive_verify_command(command, plan_id):
            artifacts.append(f"command={command!r}; exit_code=recursive_verify_guard")
            failed_checks.append(command)
            continue
        started = time.perf_counter()
        try:
            completed = subprocess.run(
                command,
                cwd=root,
                shell=True,
                text=True,
                capture_output=True,
                timeout=timeout_seconds,
                check=False,
            )
            duration = time.perf_counter() - started
            stdout = completed.stdout.strip().replace("\n", "\\n")[:500]
            stderr = completed.stderr.strip().replace("\n", "\\n")[:500]
            artifacts.append(
                f"command={command!r}; exit_code={completed.returncode}; duration_seconds={duration:.3f}; "
                f"stdout={stdout!r}; stderr={stderr!r}"
            )
            if completed.returncode != 0:
                failed_checks.append(command)
        except subprocess.TimeoutExpired as exc:
            duration = time.perf_counter() - started
            stdout = (exc.stdout or "").strip().replace("\n", "\\n")[:500] if isinstance(exc.stdout, str) else ""
            stderr = (exc.stderr or "").strip().replace("\n", "\\n")[:500] if isinstance(exc.stderr, str) else ""
            artifacts.append(
                f"command={command!r}; exit_code=timeout; duration_seconds={duration:.3f}; "
                f"timeout_seconds={timeout_seconds}; stdout={stdout!r}; stderr={stderr!r}"
            )
            failed_checks.append(command)

    result = "pass" if not failed_checks else "fail"
    return record_verification(
        plan_id=plan_id,
        command=" && ".join(commands),
        result=result,
        artifacts=artifacts,
        failed_checks=failed_checks,
        cwd=cwd,
    )
