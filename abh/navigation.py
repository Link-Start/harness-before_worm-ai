from __future__ import annotations

from pathlib import Path

from .agent_setup import agent_setup_bundle
from .audits import load_audit
from .attractors import active_attractor
from .core import doctor
from .hooks import hook_profile
from .plans import list_plans, verification_freshness_summary
from .roadmap import list_roadmap_items


OWNER_DOCS = (
    "docs/index.md",
    "docs/context/source-of-truth.md",
    "docs/context/project-context.md",
    "docs/context/conventions.md",
    "docs/context/codebase-map.md",
)


def _audit_id_for_plan(plan_id: str) -> str:
    if plan_id.startswith("plan-"):
        return f"audit-{plan_id.removeprefix('plan-')}"
    return f"audit-{plan_id}"


def _audit_request_command(plan_id: str, verification_id: str) -> str:
    audit_id = _audit_id_for_plan(plan_id)
    return (
        f'abh audit request {plan_id} --id {audit_id} --auditor human-independent-review '
        f'--scope "Independent audit of {plan_id}" '
        f"--evidence docs/plans/{plan_id}.md --evidence .abh/verifications/{verification_id}.json"
    )


def recommend_next_action(*, cwd: Path | None = None) -> dict[str, object]:
    plans = list_plans(cwd)
    open_plans = [plan for plan in plans if plan.status != "closed"]
    open_plans.sort(key=lambda plan: plan.created_at)
    active_plans = [plan for plan in open_plans if plan.status != "blocked"]
    blocked_plans = [plan for plan in open_plans if plan.status == "blocked"]

    if active_plans:
        plan = active_plans[0]
        if plan.status == "draft":
            return {
                "next_action": "complete_plan_definition",
                "recommended_command": f"abh plan status {plan.id} --json",
                "requires_confirmation": False,
                "rationale": f"open draft plan {plan.id} should be completed or transitioned before materializing new work",
                "source": {"plan_id": plan.id, "plan_status": plan.status},
                "alternatives": ["abh plan update <plan-id> --json", "abh plan transition <plan-id> --to ready"],
            }
        if plan.status in {"ready", "running"}:
            verification = verification_freshness_summary(plan, cwd)
            if verification["result"] == "pass" and not verification["stale"]:
                latest_verification = str(verification["latest_id"])
                if not plan.audit_ids:
                    return {
                        "next_action": "request_audit",
                        "recommended_command": _audit_request_command(plan.id, latest_verification),
                        "requires_confirmation": False,
                        "rationale": f"plan {plan.id} has fresh passing verification and needs independent audit evidence",
                        "source": {
                            "plan_id": plan.id,
                            "plan_status": plan.status,
                            "latest_verification": latest_verification,
                            "verification_trust_level": verification["trust_level"],
                        },
                        "alternatives": [f"abh plan status {plan.id} --json", f"abh verify run {plan.id} --json"],
                    }
                try:
                    audit = load_audit(plan.audit_ids[-1], cwd)
                    if audit.status == "complete" and audit.result == "pass":
                        return {
                            "next_action": "transition_closing",
                            "recommended_command": f"abh plan transition {plan.id} --to closing",
                            "requires_confirmation": False,
                            "rationale": f"plan {plan.id} has fresh passing verification and passing audit evidence",
                            "source": {
                                "plan_id": plan.id,
                                "plan_status": plan.status,
                                "latest_verification": latest_verification,
                                "latest_audit": audit.id,
                            },
                            "alternatives": [f"abh plan status {plan.id} --json", f"abh close {plan.id}"],
                        }
                    return {
                        "next_action": "record_audit",
                        "recommended_command": f"abh audit record {audit.id} --result pass --rationale <rationale>",
                        "requires_confirmation": False,
                        "rationale": f"plan {plan.id} has an audit request that needs an independent verdict",
                        "source": {
                            "plan_id": plan.id,
                            "plan_status": plan.status,
                            "latest_verification": latest_verification,
                            "latest_audit": audit.id,
                            "audit_status": audit.status,
                            "audit_result": audit.result,
                        },
                        "alternatives": [f"abh plan status {plan.id} --json", f"abh audit list --json"],
                    }
                except Exception:
                    return {
                        "next_action": "inspect_audit",
                        "recommended_command": f"abh plan status {plan.id} --json",
                        "requires_confirmation": False,
                        "rationale": f"plan {plan.id} references audit evidence that could not be loaded",
                        "source": {
                            "plan_id": plan.id,
                            "plan_status": plan.status,
                            "latest_verification": latest_verification,
                            "audit_ids": list(plan.audit_ids),
                        },
                        "alternatives": [f"abh audit list --json", f"abh verify run {plan.id} --json"],
                    }
            return {
                "next_action": "run_verification",
                "recommended_command": f"abh verify run {plan.id} --json",
                "requires_confirmation": False,
                "rationale": f"open {plan.status} plan {plan.id} should gather fresh local verification evidence",
                "source": {"plan_id": plan.id, "plan_status": plan.status},
                "alternatives": [f"abh plan status {plan.id} --json", "abh audit request <plan-id> --id <audit-id>"],
            }
        if plan.status == "closing":
            return {
                "next_action": "close_plan",
                "recommended_command": f"abh close {plan.id}",
                "requires_confirmation": False,
                "rationale": f"plan {plan.id} is already closing; close after confirming passing audit evidence",
                "source": {"plan_id": plan.id, "plan_status": plan.status},
                "alternatives": [f"abh plan status {plan.id} --json", "abh audit list --json"],
            }

    queued = [item for item in list_roadmap_items(cwd) if item.status == "queued" and item.plan_id is None]
    if queued:
        item = queued[0]
        source: dict[str, object] = {"roadmap_key": item.key, "stage": item.stage, "title": item.title}
        rationale = f"no open plans; next queued roadmap item is {item.key}"
        if blocked_plans:
            source["blocked_plan_ids"] = [plan.id for plan in blocked_plans]
            rationale = f"no active open plans; next queued roadmap item is {item.key}"
        return {
            "next_action": "materialize_roadmap_item",
            "recommended_command": f"abh roadmap materialize {item.key} --json",
            "requires_confirmation": False,
            "rationale": rationale,
            "source": source,
            "alternatives": ["abh roadmap list --json", "abh roadmap next-id --json"],
        }

    if blocked_plans:
        plan = blocked_plans[0]
        return {
            "next_action": "inspect_blocked_plan",
            "recommended_command": f"abh plan status {plan.id} --json",
            "requires_confirmation": False,
            "rationale": f"blocked plan {plan.id} is deferred until explicitly resumed",
            "source": {"plan_id": plan.id, "plan_status": plan.status},
            "alternatives": [f"abh plan transition {plan.id} --to running", "abh roadmap list --json"],
        }

    return {
        "next_action": "inspect_status",
        "recommended_command": "abh plan list --json",
        "requires_confirmation": False,
        "rationale": "no open plans or queued roadmap items were found",
        "source": {},
        "alternatives": ["abh doctor --json", "abh roadmap list --json"],
    }


def _check(check_id: str, label: str, passed: bool, details: dict[str, object], action: str) -> dict[str, object]:
    return {
        "id": check_id,
        "label": label,
        "status": "pass" if passed else "fail",
        "ok": passed,
        "details": details,
        "recommended_action": "" if passed else action,
    }


def onboarding_check(*, cwd: Path | None = None) -> dict[str, object]:
    checks: list[dict[str, object]] = []
    try:
        attractor = active_attractor(cwd)
        checks.append(
            _check(
                "active_attractor",
                "Active attractor is available",
                True,
                {"id": attractor.id, "path": attractor.path},
                "abh attractor active --json",
            )
        )
    except Exception as exc:
        checks.append(_check("active_attractor", "Active attractor is available", False, {"error": str(exc)}, "abh attractor active --json"))

    root = Path.cwd() if cwd is None else Path(cwd)
    missing_owner_docs = [path for path in OWNER_DOCS if not (root / path).exists()]
    checks.append(
        _check(
            "owner_docs",
            "AGE owner docs are present",
            not missing_owner_docs,
            {"required": list(OWNER_DOCS), "missing": missing_owner_docs},
            "abh init --write --confirm --json",
        )
    )

    try:
        setup = agent_setup_bundle("codex", cwd=cwd)
        checks.append(
            _check(
                "agent_setup_export",
                "Agent setup export is available",
                True,
                {"agent": setup["agent"], "commands": setup["commands"]},
                "abh agent setup codex --json",
            )
        )
    except Exception as exc:
        checks.append(_check("agent_setup_export", "Agent setup export is available", False, {"error": str(exc)}, "abh agent setup codex --json"))

    profile = hook_profile()
    checks.append(
        _check(
            "hook_guardrails",
            "Hook guardrail commands are available",
            bool(profile.get("commands")),
            {"profile": profile["name"], "commands": profile["commands"]},
            "abh hooks profile --json",
        )
    )

    doctor_issues = doctor(cwd)
    checks.append(
        _check(
            "doctor",
            "Doctor consistency check passes",
            not doctor_issues,
            {"issues": doctor_issues},
            "abh doctor",
        )
    )

    closed_plans = [plan.id for plan in list_plans(cwd) if plan.status == "closed" and plan.verification_runs and plan.audit_ids]
    checks.append(
        _check(
            "closed_loop_evidence",
            "At least one verified and audited plan is closed",
            bool(closed_plans),
            {"closed_plans": closed_plans[:5], "total": len(closed_plans)},
            "complete one plan through verify, audit, and close",
        )
    )

    recommended_actions = [str(check["recommended_action"]) for check in checks if not check["ok"]]
    return {"ready": not recommended_actions, "checks": checks, "recommended_actions": recommended_actions}
