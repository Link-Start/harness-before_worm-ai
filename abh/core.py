from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from .audits import (
    list_audits,
    load_audit,
    parse_finding,
    record_audit,
    render_audit_markdown,
    request_audit,
    save_audit,
)
from .errors import AbhError, validate_identifier
from .models import (
    DRIFT_TYPES,
    MEMORY_TYPES,
    DriftFinding,
    DriftReport,
    MemoryRecord,
    utc_now,
)
from .plans import (
    ALLOWED_TRANSITIONS,
    append_unique,
    close_plan,
    create_plan,
    list_plans,
    load_plan,
    plan_status_line,
    render_plan_markdown,
    save_plan,
    transition_plan,
    update_plan_record,
    validate_plan_ready,
)
from .storage import (
    audits_dir,
    drift_dir,
    drift_doc_path,
    drift_json_path,
    docs_audits_dir,
    docs_drift_dir,
    docs_memory_dir,
    docs_plans_dir,
    ensure_workspace,
    memory_doc_path,
    memory_json_path,
    memory_dir,
    plans_dir,
    read_json,
    write_json,
)
from .verifications import is_recursive_verify_command, load_verification, record_verification, run_verification


# Verification runs are JSON-only execution evidence today, so doctor excludes
# them from JSON/Markdown consistency checks until they get a document model.
DOCTOR_OBJECTS: tuple[tuple[str, str, Callable[[Path | None], Path], Callable[[Path | None], Path]], ...] = (
    ("plan", "plan-", plans_dir, docs_plans_dir),
    ("audit", "audit-", audits_dir, docs_audits_dir),
    ("memory", "mem-", memory_dir, docs_memory_dir),
    ("drift", "drift-", drift_dir, docs_drift_dir),
)


def doctor(cwd: Path | None = None) -> list[str]:
    issues: list[str] = []
    for label, prefix, json_dir_factory, docs_dir_factory in DOCTOR_OBJECTS:
        json_dir = json_dir_factory(cwd)
        docs_dir = docs_dir_factory(cwd)
        json_ids = {path.stem for path in json_dir.glob("*.json")} if json_dir.exists() else set()
        if json_dir.exists():
            for path in sorted(json_dir.glob("*.json")):
                data = read_json(path)
                if data.get("schema_version") != "1":
                    issues.append(f"missing schema_version for {label} {path.stem}")
        doc_ids = set()
        if docs_dir.exists():
            doc_ids = {
                path.stem
                for path in docs_dir.glob("*.md")
                if path.name != "README.md" and path.stem.startswith(prefix)
            }
        for object_id in sorted(json_ids - doc_ids):
            issues.append(f"missing markdown for {label} {object_id}")
        for object_id in sorted(doc_ids - json_ids):
            issues.append(f"orphan markdown for {label} {object_id}")
    return issues


def load_memory(memory_id: str, cwd: Path | None = None) -> MemoryRecord:
    validate_identifier(memory_id, "memory id")
    path = memory_json_path(memory_id, cwd)
    if not path.exists():
        raise AbhError(f"memory not found: {memory_id}")
    return MemoryRecord.from_dict(read_json(path))


def save_memory(memory: MemoryRecord, cwd: Path | None = None, write_doc: bool = True) -> MemoryRecord:
    ensure_workspace(cwd)
    memory.updated_at = utc_now()
    if write_doc:
        doc_path = memory.doc_path or str(memory_doc_path(memory.id, cwd))
        memory.doc_path = doc_path
        doc_file = Path(doc_path)
        doc_file.parent.mkdir(parents=True, exist_ok=True)
        doc_file.write_text(render_memory_markdown(memory), encoding="utf-8")
    write_json(memory_json_path(memory.id, cwd), memory.to_dict())
    return memory


def add_memory(
    *,
    memory_id: str,
    memory_type: str,
    summary: str,
    context: str,
    implication: str,
    evidence: list[str] | None = None,
    related: list[str] | None = None,
    deprecation_policy: str | None = None,
    cwd: Path | None = None,
) -> MemoryRecord:
    ensure_workspace(cwd)
    validate_identifier(memory_id, "memory id")
    if memory_type not in MEMORY_TYPES:
        raise AbhError(f"invalid memory type: {memory_type}")
    if memory_json_path(memory_id, cwd).exists():
        raise AbhError(f"memory already exists: {memory_id}")
    evidence_items = list(evidence or [])
    if not evidence_items:
        raise AbhError("memory requires at least one evidence item")
    memory = MemoryRecord(
        id=memory_id,
        memory_type=memory_type,
        summary=summary,
        context=context,
        implication=implication,
        related=list(related or []),
        evidence=evidence_items,
        deprecation_policy=deprecation_policy or "Mark deprecated when evidence no longer applies.",
        doc_path=str(memory_doc_path(memory_id, cwd)),
    )
    return save_memory(memory, cwd)


def search_memory(
    *,
    memory_type: str | None = None,
    query: str | None = None,
    cwd: Path | None = None,
) -> list[MemoryRecord]:
    if memory_type and memory_type not in MEMORY_TYPES:
        raise AbhError(f"invalid memory type: {memory_type}")
    directory = memory_dir(cwd)
    if not directory.exists():
        return []
    normalized_query = (query or "").strip().lower()
    results: list[MemoryRecord] = []
    for path in sorted(directory.glob("*.json")):
        memory = MemoryRecord.from_dict(read_json(path))
        if memory_type and memory.memory_type != memory_type:
            continue
        searchable = "\n".join(
            [
                memory.id,
                memory.memory_type,
                memory.summary,
                memory.context,
                memory.implication,
                "\n".join(memory.related),
                "\n".join(memory.evidence),
            ]
        ).lower()
        if normalized_query and normalized_query not in searchable:
            continue
        results.append(memory)
    return results


def list_memories(cwd: Path | None = None) -> list[MemoryRecord]:
    directory = memory_dir(cwd)
    if not directory.exists():
        return []
    memories: list[MemoryRecord] = []
    for path in sorted(directory.glob("*.json")):
        memories.append(MemoryRecord.from_dict(read_json(path)))
    return memories


def render_memory_markdown(memory: MemoryRecord) -> str:
    def bullet_lines(values: list[str]) -> str:
        if not values:
            return "- "
        return "\n".join(f"- {value}" for value in values)

    return (
        f"# Memory: {memory.summary}\n\n"
        "## Metadata\n\n"
        f"- ID: {memory.id}\n"
        f"- Type: {memory.memory_type}\n"
        f"- Status: {memory.status}\n"
        f"- Created: {memory.created_at}\n"
        f"- Updated: {memory.updated_at}\n"
        f"- Related: {', '.join(memory.related)}\n\n"
        "## Summary\n\n"
        f"{memory.summary}\n\n"
        "## Context\n\n"
        f"{memory.context}\n\n"
        "## Evidence\n\n"
        f"{bullet_lines(memory.evidence)}\n\n"
        "## Implication\n\n"
        f"{memory.implication}\n\n"
        "## Deprecation Policy\n\n"
        f"{memory.deprecation_policy}\n"
    )


ROUTES: dict[str, dict[str, object]] = {
    "completion_audit": {
        "keywords": ("close", "closed", "completion", "完成", "关闭", "验收", "审计", "audit"),
        "reading_order": [
            "docs/plans/",
            "docs/audits/",
            "docs/memory/",
            "tests/",
            "abh/",
        ],
        "rationale": "Completion questions are decided by plan criteria, independent audit, memory, tests, and code evidence.",
    },
    "implementation": {
        "keywords": ("implement", "code", "cli", "命令", "实现", "开发"),
        "reading_order": [
            "docs/architecture/attractors/",
            "docs/plans/",
            "abh/",
            "tests/",
        ],
        "rationale": "Implementation questions should start from attractor and plan intent, then inspect code and tests.",
    },
    "drift": {
        "keywords": ("drift", "偏离", "漂移", "scope", "boundary", "dependency", "术语"),
        "reading_order": [
            "docs/architecture/attractors/",
            "docs/plans/",
            "docs/memory/",
            "docs/drift/",
            "abh/",
        ],
        "rationale": "Drift questions compare the attractor and plan against observed changes and prior memory.",
    },
}


def route_question(question: str) -> dict[str, object]:
    text = question.lower()
    for route_name, route in ROUTES.items():
        if any(keyword.lower() in text for keyword in route["keywords"]):
            reading_order = list(route["reading_order"])
            # inject active plans
            plans = list_plans()
            active = [p for p in plans if p.status in ("running", "blocked")]
            if active:
                reading_order.append("docs/plans/ (active plans)")
                for p in active:
                    reading_order.append(f"  -> {p.id} [{p.status}]")
            # inject recent memories
            memories = list_memories()
            question_words = set(text.split())
            relevant = []
            for m in memories:
                mem_text = f"{m.summary} {m.context} {m.implication}".lower()
                if any(w in mem_text for w in question_words if len(w) > 2):
                    relevant.append(m)
            if relevant:
                reading_order.append("docs/memory/ (relevant memories)")
                for m in relevant[:5]:
                    reading_order.append(f"  -> {m.id} [{m.memory_type}]")

            return {
                "route": route_name,
                "reading_order": reading_order,
                "active_plans": len(active),
                "rationale": route["rationale"],
            }
    return {
        "route": "general",
        "reading_order": [
            "docs/architecture/attractors/",
            "docs/plans/",
            "docs/audits/",
            "docs/memory/",
            "abh/",
            "tests/",
        ],
        "rationale": "General questions should be grounded in attractor, plan, audit, memory, code, and tests.",
    }


DRIFT_RULES: dict[str, dict[str, object]] = {
    "boundary_drift": {
        "keywords": ("boundary", "module boundary", "moved", "mixed", "plan manager", "audit logic", "边界", "混入"),
        "recommendation": "Create a follow-up to restore ownership boundaries or update the attractor if the boundary changed intentionally.",
    },
    "dependency_drift": {
        "keywords": ("dependency", "database", "remote", "external", "service", "package", "依赖", "数据库", "外部"),
        "recommendation": "Review plan non-goals and dependency rules before accepting the new dependency.",
    },
    "test_drift": {
        "keywords": ("skip test", "skipped tests", "without tests", "no test", "测试跳过", "未测试"),
        "recommendation": "Add or restore verification coverage before closing the plan.",
    },
    "terminology_drift": {
        "keywords": ("renamed", "terminology", "term", "prepared", "ready", "术语", "重命名"),
        "recommendation": "Align terminology with canonical docs or record an explicit migration.",
    },
}


def analyze_drift_text(text: str) -> list[DriftFinding]:
    lowered = text.lower()
    findings: list[DriftFinding] = []
    for drift_type, rule in DRIFT_RULES.items():
        matched = [keyword for keyword in rule["keywords"] if keyword.lower() in lowered]
        if matched:
            findings.append(
                DriftFinding(
                    drift_type=drift_type,
                    evidence=f"matched keywords: {', '.join(matched)}",
                    recommendation=str(rule["recommendation"]),
                )
            )
    return findings


def save_drift_report(report: DriftReport, cwd: Path | None = None, write_doc: bool = True) -> DriftReport:
    ensure_workspace(cwd)
    report.updated_at = utc_now()
    if write_doc:
        doc_path = report.doc_path or str(drift_doc_path(report.id, cwd))
        report.doc_path = doc_path
        doc_file = Path(doc_path)
        doc_file.parent.mkdir(parents=True, exist_ok=True)
        doc_file.write_text(render_drift_markdown(report), encoding="utf-8")
    write_json(drift_json_path(report.id, cwd), report.to_dict())
    return report


def analyze_drift(
    *,
    drift_id: str,
    source: str,
    evidence: list[str] | None = None,
    memory_id: str | None = None,
    plan_id: str | None = None,
    cwd: Path | None = None,
) -> DriftReport:
    validate_identifier(drift_id, "drift id")
    source_path = Path(source)
    if not source_path.exists():
        raise AbhError(f"drift source not found: {source}")
    source_text = source_path.read_text(encoding="utf-8")
    findings = analyze_drift_text(source_text)
    # plan-based drift detection
    if plan_id:
        plan = load_plan(plan_id, cwd)
        negation_prefixes = ("不", "不要", "无需", "禁止", "避免", "no ", "not ")
        lowered = source_text.lower()
        for non_goal in plan.non_goals:
            clean = non_goal.lower()
            for prefix in negation_prefixes:
                if clean.startswith(prefix):
                    clean = clean[len(prefix):]
                    break
            keywords = [clean] if len(clean) > 2 else []
            keywords += [w for w in clean.split() if len(w) > 2 and w not in keywords]
            if not keywords:
                continue
            matched = [kw for kw in keywords if kw in lowered]
            if matched:
                existing_types = {f.drift_type for f in findings}
                for dt in DRIFT_TYPES:
                    if dt not in existing_types:
                        findings.append(
                            DriftFinding(
                                drift_type=dt,
                                evidence=f"plan non-goal violation: '{non_goal}' matched keywords {matched}",
                                recommendation=f"Review plan '{plan_id}' non-goal: {non_goal}. Consider updating plan or source.",
                            )
                        )
                        break
    follow_ups = [finding.recommendation for finding in findings]
    report = DriftReport(
        id=drift_id,
        source=source,
        findings=findings,
        evidence=list(evidence or [source]),
        follow_ups=follow_ups,
        doc_path=str(drift_doc_path(drift_id, cwd)),
    )
    save_drift_report(report, cwd)
    if memory_id:
        if not findings:
            raise AbhError("cannot write drift memory without drift findings")
        add_memory(
            memory_id=memory_id,
            memory_type="divergent_pattern",
            summary=f"Drift report {drift_id}: {', '.join(finding.drift_type for finding in findings)}",
            context=f"Drift source: {source}",
            implication="Use these drift patterns to route follow-up plans before closure.",
            evidence=[str(drift_doc_path(drift_id, cwd))],
            related=[drift_id],
            cwd=cwd,
        )
    return report


def render_drift_markdown(report: DriftReport) -> str:
    def bullet_lines(values: list[str]) -> str:
        if not values:
            return "- "
        return "\n".join(f"- {value}" for value in values)

    if report.findings:
        finding_lines = "\n".join(
            f"| {finding.drift_type} | {finding.evidence} | {finding.recommendation} |"
            for finding in report.findings
        )
    else:
        finding_lines = "|  |  |  |"
    return (
        f"# Drift: {report.id}\n\n"
        "## Metadata\n\n"
        f"- ID: {report.id}\n"
        f"- Source: {report.source}\n"
        f"- Created: {report.created_at}\n"
        f"- Updated: {report.updated_at}\n\n"
        "## Evidence\n\n"
        f"{bullet_lines(report.evidence)}\n\n"
        "## Findings\n\n"
        "| Type | Evidence | Recommendation |\n"
        "| --- | --- | --- |\n"
        f"{finding_lines}\n\n"
        "## Follow-Ups\n\n"
        f"{bullet_lines(report.follow_ups)}\n"
    )
