# Repository Write Transaction Boundary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a shared local-filesystem write boundary for ABH JSON/Markdown record pairs so representative partial-write failures are avoided or rolled back coherently.

**Architecture:** Keep the boundary local and synchronous. Add a storage-layer helper that locks both target files, writes both temporary files before replacing either target, and rolls back already-replaced targets if a later replace fails. Apply that helper to the existing plan, audit, memory, drift, and attractor save paths without changing object schemas.

**Tech Stack:** Python standard library, existing ABH storage helpers, `unittest`, local filesystem atomic `os.replace`.

---

## File Structure

- Modify `abh/storage.py`: add pair locking, temporary-file preparation, rollback helpers, and `write_json_markdown_pair()`.
- Modify `abh/plans.py`: use `write_json_markdown_pair()` when `save_plan(..., write_doc=True)` writes the plan Markdown and JSON pair.
- Modify `abh/audits.py`: use `write_json_markdown_pair()` for audit Markdown and JSON saves.
- Modify `abh/memory.py`: use `write_json_markdown_pair()` for memory Markdown and JSON saves.
- Modify `abh/drift.py`: use `write_json_markdown_pair()` for drift Markdown and JSON saves.
- Modify `abh/attractors.py`: use `write_json_markdown_pair()` for attractor Markdown and JSON saves.
- Modify `abh/navigation.py`: treat blocked/deferred historical plans as non-active so `abh next` can materialize the next queued roadmap item.
- Modify `tests/test_cli.py`: add focused storage failure-mode tests and keep existing CLI regression coverage.
- Modify docs: update `docs/development-roadmap.md` and `docs/task-board.md` with the `plan-045` status and transaction-boundary guarantee.

## Task 0: Re-Planning Gate

- [ ] **Step 1: Add the failing navigation test**

Add a test that creates a blocked plan plus a queued roadmap item, then asserts `abh next --json` recommends `materialize_roadmap_item` for that queued roadmap item and reports the blocked plan in `source.blocked_plan_ids`.

- [ ] **Step 2: Update `abh/navigation.py`**

Split open plans into active plans and blocked plans. Prioritize active plans; when only blocked plans remain and a queued roadmap item exists, recommend materializing the queued item. If no queued roadmap item exists, recommend inspecting the blocked plan.

- [ ] **Step 3: Run focused navigation test**

Run:

```bash
python3 -m unittest tests.test_cli.CliTests.test_next_json_skips_blocked_plan_for_queued_roadmap_item -v
```

Expected: pass.

## Task 1: Red Tests For Pair Write Boundary

- [ ] **Step 1: Add a successful pair-write test**

Add this test to `tests/test_cli.py` in a storage-focused section:

```python
    def test_storage_write_json_markdown_pair_writes_both_targets(self) -> None:
        from abh.storage import write_json_markdown_pair

        json_path = self.root / ".abh" / "plans" / "plan-pair.json"
        doc_path = self.root / "docs" / "plans" / "plan-pair.md"

        write_json_markdown_pair(json_path, {"schema_version": "1", "id": "plan-pair"}, doc_path, "# Plan\n")

        self.assertEqual(json.loads(json_path.read_text(encoding="utf-8"))["id"], "plan-pair")
        self.assertEqual(doc_path.read_text(encoding="utf-8"), "# Plan\n")
```

- [ ] **Step 2: Add rollback coverage for second replace failure**

Add this test to `tests/test_cli.py`:

```python
    def test_storage_write_json_markdown_pair_rolls_back_first_replace_on_second_replace_failure(self) -> None:
        from unittest import mock

        from abh import storage

        json_path = self.root / ".abh" / "plans" / "plan-pair.json"
        doc_path = self.root / "docs" / "plans" / "plan-pair.md"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        doc_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text('{"schema_version": "1", "id": "old"}\n', encoding="utf-8")
        doc_path.write_text("# Old\n", encoding="utf-8")
        real_replace = storage.os.replace
        calls = []

        def replace_then_fail(src: Path, dst: Path) -> None:
            calls.append(Path(dst))
            if Path(dst) == json_path:
                raise OSError("injected json replace failure")
            real_replace(src, dst)

        with mock.patch.object(storage.os, "replace", side_effect=replace_then_fail):
            with self.assertRaises(OSError):
                storage.write_json_markdown_pair(json_path, {"schema_version": "1", "id": "new"}, doc_path, "# New\n")

        self.assertEqual(json_path.read_text(encoding="utf-8"), '{"schema_version": "1", "id": "old"}\n')
        self.assertEqual(doc_path.read_text(encoding="utf-8"), "# Old\n")
        self.assertIn(doc_path, calls)
        self.assertIn(json_path, calls)
```

- [ ] **Step 3: Run focused tests and verify RED**

Run:

```bash
python3 -m unittest tests.test_cli.CliTests.test_storage_write_json_markdown_pair_writes_both_targets tests.test_cli.CliTests.test_storage_write_json_markdown_pair_rolls_back_first_replace_on_second_replace_failure -v
```

Expected: fail because `write_json_markdown_pair` does not exist.

## Task 2: Storage Helper Implementation

- [ ] **Step 1: Add deterministic pair locking**

In `abh/storage.py`, add a helper that locks target paths in sorted path order with `contextlib.ExitStack` so callers never acquire the same two locks in different orders:

```python
@contextmanager
def file_locks(paths: list[Path]):
    with ExitStack() as stack:
        for path in sorted(paths, key=lambda item: str(item)):
            stack.enter_context(file_lock(path))
        yield
```

- [ ] **Step 2: Add temporary write and target restore helpers**

In `abh/storage.py`, add private helpers that write bytes to a temp file with fsync, snapshot existing targets, and restore old target bytes during rollback:

```python
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
```

```python
def _snapshot_target(path: Path) -> tuple[bool, bytes]:
    if not path.exists():
        return False, b""
    return True, path.read_bytes()


def _restore_target(path: Path, existed: bool, content: bytes) -> None:
    if existed:
        temp_path = _write_temp_bytes(path, content)
        os.replace(temp_path, path)
        return
    try:
        path.unlink()
    except FileNotFoundError:
        pass
```

- [ ] **Step 3: Add `write_json_markdown_pair()`**

In `abh/storage.py`, add the public helper:

```python
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
```

- [ ] **Step 4: Run focused tests and verify GREEN**

Run:

```bash
python3 -m unittest tests.test_cli.CliTests.test_storage_write_json_markdown_pair_writes_both_targets tests.test_cli.CliTests.test_storage_write_json_markdown_pair_rolls_back_first_replace_on_second_replace_failure -v
```

Expected: pass.

## Task 3: Apply Helper To ABH Save Paths

- [ ] **Step 1: Update `save_plan()`**

Change `abh/plans.py` so `write_doc=True` renders Markdown and calls:

```python
write_json_markdown_pair(plan_json_path(plan.id, cwd), plan.to_dict(), doc_file, doc)
```

Keep the existing `write_json(...)` path when `write_doc=False`.

- [ ] **Step 2: Update audit, memory, drift, and attractor save paths**

Apply the same pattern to `save_audit()`, `save_memory()`, `save_drift_report()`, and `save_attractor()`: pair-write when Markdown is written, JSON-only write when `write_doc=False`.

- [ ] **Step 3: Run representative CLI save tests**

Run:

```bash
python3 -m unittest tests.test_cli.CliTests.test_plan_create_status_transition_and_verify tests.test_cli.CliTests.test_memory_add_list_and_route tests.test_cli.CliTests.test_drift_analyze_records_report tests.test_cli.CliTests.test_attractor_active_check_and_list -v
```

Expected: pass. If any listed test name does not exist, replace it with the closest existing test for that save path found by `rg -n "memory|drift|attractor" tests/test_cli.py`.

## Task 4: Docs And Plan State

- [ ] **Step 1: Update planning docs**

Update `docs/development-roadmap.md` and `docs/task-board.md` to show `plan-045-repository-write-transaction-boundary` as the active Stage 6 slice after `plan-044`.

- [ ] **Step 2: Update plan closure evidence**

Run:

```bash
python3 -m abh plan update plan-045-repository-write-transaction-boundary --closure-evidence docs/superpowers/plans/2026-06-04-repository-write-transaction-boundary.md --json
```

Expected: JSON output includes the new closure evidence path.

- [ ] **Step 3: Transition plan to running**

Run:

```bash
python3 -m abh plan transition plan-045-repository-write-transaction-boundary --to ready
python3 -m abh plan transition plan-045-repository-write-transaction-boundary --to running
```

Expected: both transitions succeed.

## Task 5: Full Verification

- [ ] **Step 1: Run full regression suite**

Run:

```bash
python3 -m unittest tests/test_cli.py -v
```

Expected: pass.

- [ ] **Step 2: Run ABH consistency checks**

Run:

```bash
python3 -m abh doctor
git diff --check
python3 -m abh roadmap check --json
```

Expected: doctor reports no issues, diff check is clean, and roadmap check reports no consistency errors.

- [ ] **Step 3: Run plan verification**

Run:

```bash
python3 -m abh verify run plan-045-repository-write-transaction-boundary --json
```

Expected: verification result is `pass`.
