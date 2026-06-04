from __future__ import annotations

import json
import os
import time
import uuid
from contextlib import ExitStack, contextmanager
from pathlib import Path
from typing import Any


LOCK_TIMEOUT_SECONDS = 30.0
LOCK_POLL_SECONDS = 0.05


def root_dir(cwd: Path | None = None) -> Path:
    return Path.cwd() if cwd is None else Path(cwd)


def abh_dir(cwd: Path | None = None) -> Path:
    return root_dir(cwd) / ".abh"


def plans_dir(cwd: Path | None = None) -> Path:
    return abh_dir(cwd) / "plans"


def verifications_dir(cwd: Path | None = None) -> Path:
    return abh_dir(cwd) / "verifications"


def audits_dir(cwd: Path | None = None) -> Path:
    return abh_dir(cwd) / "audits"


def attractors_dir(cwd: Path | None = None) -> Path:
    return abh_dir(cwd) / "attractors"


def memory_dir(cwd: Path | None = None) -> Path:
    return abh_dir(cwd) / "memory"


def drift_dir(cwd: Path | None = None) -> Path:
    return abh_dir(cwd) / "drift"


def roadmap_path(cwd: Path | None = None) -> Path:
    return abh_dir(cwd) / "roadmap.json"


def docs_dir(cwd: Path | None = None) -> Path:
    return root_dir(cwd) / "docs"


def docs_plans_dir(cwd: Path | None = None) -> Path:
    return docs_dir(cwd) / "plans"


def docs_audits_dir(cwd: Path | None = None) -> Path:
    return docs_dir(cwd) / "audits"


def docs_memory_dir(cwd: Path | None = None) -> Path:
    return docs_dir(cwd) / "memory"


def docs_drift_dir(cwd: Path | None = None) -> Path:
    return docs_dir(cwd) / "drift"


def docs_attractors_dir(cwd: Path | None = None) -> Path:
    return docs_dir(cwd) / "architecture" / "attractors"


def plan_json_path(plan_id: str, cwd: Path | None = None) -> Path:
    return plans_dir(cwd) / f"{plan_id}.json"


def plan_doc_path(plan_id: str, cwd: Path | None = None) -> Path:
    return docs_plans_dir(cwd) / f"{plan_id}.md"


def verification_path(run_id: str, cwd: Path | None = None) -> Path:
    return verifications_dir(cwd) / f"{run_id}.json"


def audit_json_path(audit_id: str, cwd: Path | None = None) -> Path:
    return audits_dir(cwd) / f"{audit_id}.json"


def audit_doc_path(audit_id: str, cwd: Path | None = None) -> Path:
    return docs_audits_dir(cwd) / f"{audit_id}.md"


def attractor_json_path(attractor_id: str, cwd: Path | None = None) -> Path:
    return attractors_dir(cwd) / f"{attractor_id}.json"


def attractor_doc_path(attractor_id: str, cwd: Path | None = None) -> Path:
    return docs_attractors_dir(cwd) / f"{attractor_id}.md"


def memory_json_path(memory_id: str, cwd: Path | None = None) -> Path:
    return memory_dir(cwd) / f"{memory_id}.json"


def memory_doc_path(memory_id: str, cwd: Path | None = None) -> Path:
    return docs_memory_dir(cwd) / f"{memory_id}.md"


def drift_json_path(drift_id: str, cwd: Path | None = None) -> Path:
    return drift_dir(cwd) / f"{drift_id}.json"


def drift_doc_path(drift_id: str, cwd: Path | None = None) -> Path:
    return docs_drift_dir(cwd) / f"{drift_id}.md"


def ensure_workspace(cwd: Path | None = None) -> None:
    for directory in (
        abh_dir(cwd),
        plans_dir(cwd),
        verifications_dir(cwd),
        audits_dir(cwd),
        attractors_dir(cwd),
        memory_dir(cwd),
        drift_dir(cwd),
        docs_plans_dir(cwd),
        docs_audits_dir(cwd),
        docs_attractors_dir(cwd),
        docs_memory_dir(cwd),
        docs_drift_dir(cwd),
    ):
        directory.mkdir(parents=True, exist_ok=True)


@contextmanager
def file_lock(path: Path):
    lock_path = path.with_suffix(path.suffix + ".lock")
    path.parent.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + LOCK_TIMEOUT_SECONDS
    fd: int | None = None
    acquired = False
    try:
        while True:
            try:
                fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, f"{os.getpid()}\n".encode("utf-8"))
                acquired = True
                break
            except FileExistsError:
                if time.monotonic() >= deadline:
                    raise TimeoutError(f"timed out waiting for write lock: {lock_path}")
                time.sleep(LOCK_POLL_SECONDS)
        yield
    finally:
        if fd is not None:
            os.close(fd)
        if acquired:
            try:
                lock_path.unlink()
            except FileNotFoundError:
                pass


@contextmanager
def file_locks(paths: list[Path]):
    with ExitStack() as stack:
        for path in sorted(paths, key=lambda item: str(item)):
            stack.enter_context(file_lock(path))
        yield


def _cleanup_temp(path: Path, exc_type: type[BaseException] | None) -> None:
    if exc_type is not None:
        try:
            path.unlink()
        except FileNotFoundError:
            pass


def _write_temp_bytes(target: Path, content: bytes) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    temp_path = target.with_name(f"{target.name}.{uuid.uuid4().hex}.tmp")
    temp_file = temp_path.open("wb")
    exc_type: type[BaseException] | None = None
    try:
        with temp_file:
            temp_file.write(content)
            temp_file.flush()
            os.fsync(temp_file.fileno())
        return temp_path
    except BaseException as exc:
        exc_type = type(exc)
        raise
    finally:
        _cleanup_temp(temp_path, exc_type)


def _snapshot_target(path: Path) -> tuple[bool, bytes]:
    if not path.exists():
        return False, b""
    return True, path.read_bytes()


def _restore_target(path: Path, existed: bool, content: bytes) -> None:
    if existed:
        temp_path = _write_temp_bytes(path, content)
        try:
            os.replace(temp_path, path)
        finally:
            _cleanup_temp(temp_path, BaseException)
        return
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f"{path.name}.{uuid.uuid4().hex}.tmp")
    with file_lock(path):
        temp_file = temp_path.open("w", encoding="utf-8")
        exc_type: type[BaseException] | None = None
        try:
            with temp_file:
                temp_file.write(content)
                temp_file.flush()
                os.fsync(temp_file.fileno())
            os.replace(temp_path, path)
        except BaseException as exc:
            exc_type = type(exc)
            raise
        finally:
            _cleanup_temp(temp_path, exc_type)


def write_json(path: Path, data: dict[str, Any]) -> None:
    write_text(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def write_json_markdown_pair(json_path: Path, data: dict[str, Any], markdown_path: Path, markdown: str) -> None:
    json_payload = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8") + b"\n"
    markdown_payload = markdown.encode("utf-8")
    with file_locks([json_path, markdown_path]):
        snapshots = {
            markdown_path: _snapshot_target(markdown_path),
            json_path: _snapshot_target(json_path),
        }
        temp_markdown = _write_temp_bytes(markdown_path, markdown_payload)
        temp_json = _write_temp_bytes(json_path, json_payload)
        replaced: list[Path] = []
        try:
            os.replace(temp_markdown, markdown_path)
            replaced.append(markdown_path)
            os.replace(temp_json, json_path)
            replaced.append(json_path)
        except BaseException:
            for path in reversed(replaced):
                existed, content = snapshots[path]
                _restore_target(path, existed, content)
            raise
        finally:
            _cleanup_temp(temp_markdown, BaseException)
            _cleanup_temp(temp_json, BaseException)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))
