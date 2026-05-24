from __future__ import annotations

from pathlib import Path

from .errors import AbhError, validate_identifier
from .models import MEMORY_TYPES, MemoryRecord, utc_now
from .storage import ensure_workspace, memory_doc_path, memory_json_path, memory_dir, read_json, write_json, write_text


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
        write_text(Path(doc_path), render_memory_markdown(memory))
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
