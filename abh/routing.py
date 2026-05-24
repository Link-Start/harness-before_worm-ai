from __future__ import annotations

from .memory import list_memories
from .plans import list_plans


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
            plans = list_plans()
            active = [p for p in plans if p.status in ("running", "blocked")]
            if active:
                reading_order.append("docs/plans/ (active plans)")
                for p in active:
                    reading_order.append(f"  -> {p.id} [{p.status}]")
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
