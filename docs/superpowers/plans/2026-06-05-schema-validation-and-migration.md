# Schema Validation and Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add first-slice schema validation for core `.abh` JSON record families so malformed records are visible through `abh doctor` while legacy readable records remain loadable.

**Architecture:** Keep validation in `abh.models` next to the dataclass record definitions and keep migration policy explicit but non-invasive. `from_dict()` remains backward-compatible for legacy readable records; `doctor()` becomes the enforcement surface for missing required fields, unknown fields, and schema version issues.

**Tech Stack:** Python standard library, dataclasses, existing ABH doctor, `unittest`.

---

## File Structure

- Modify `abh/models.py`: add schema specs for plan, audit, attractor, memory, and drift records; add `validate_record_schema()` and `schema_issue_messages()`.
- Modify `abh/core.py`: call schema validation from `doctor()` for every core JSON record before existing JSON/Markdown pairing checks.
- Modify `abh/roadmap.py`: make plan numbering checks read raw plan ids so malformed plan records do not crash doctor before schema issues are reported.
- Modify `tests/test_cli.py`: add tests for missing required fields, unknown fields, invalid schema versions, and legacy readable records.
- Modify planning docs: update `docs/development-roadmap.md`, `docs/task-board.md`, and `docs/superpowers/plans/2026-06-05-schema-validation-and-migration.md`.

## Task 1: Red Tests For Doctor Schema Validation

- [ ] **Step 1: Add missing-required-field doctor test**

Add this test near existing doctor tests in `tests/test_cli.py`:

```python
    def test_doctor_reports_missing_required_record_fields(self) -> None:
        self.run_cli(
            "plan",
            "create",
            "--id",
            "plan-doctor-required",
            "--title",
            "Required Field",
            "--attractor",
            "docs/architecture/attractors/abh-core-attractor.md",
            "--baseline",
            "baseline",
        )
        plan_path = self.root / ".abh" / "plans" / "plan-doctor-required.json"
        data = json.loads(plan_path.read_text(encoding="utf-8"))
        data.pop("title")
        plan_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

        code, out, err = self.run_cli("doctor")

        self.assertEqual(code, 1)
        self.assertEqual(err, "")
        self.assertIn("missing required field for plan plan-doctor-required: title", out)
```

- [ ] **Step 2: Add unknown-field doctor test**

Add this test near the same doctor tests:

```python
    def test_doctor_reports_unknown_record_fields(self) -> None:
        self.run_cli(
            "plan",
            "create",
            "--id",
            "plan-doctor-unknown",
            "--title",
            "Unknown Field",
            "--attractor",
            "docs/architecture/attractors/abh-core-attractor.md",
            "--baseline",
            "baseline",
        )
        plan_path = self.root / ".abh" / "plans" / "plan-doctor-unknown.json"
        data = json.loads(plan_path.read_text(encoding="utf-8"))
        data["surprise"] = "not in schema"
        plan_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

        code, out, err = self.run_cli("doctor")

        self.assertEqual(code, 1)
        self.assertEqual(err, "")
        self.assertIn("unknown field for plan plan-doctor-unknown: surprise", out)
```

- [ ] **Step 3: Add invalid-schema-version doctor test**

Add this test:

```python
    def test_doctor_reports_invalid_schema_version(self) -> None:
        self.run_cli(
            "plan",
            "create",
            "--id",
            "plan-doctor-version",
            "--title",
            "Version Field",
            "--attractor",
            "docs/architecture/attractors/abh-core-attractor.md",
            "--baseline",
            "baseline",
        )
        plan_path = self.root / ".abh" / "plans" / "plan-doctor-version.json"
        data = json.loads(plan_path.read_text(encoding="utf-8"))
        data["schema_version"] = "999"
        plan_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

        code, out, err = self.run_cli("doctor")

        self.assertEqual(code, 1)
        self.assertEqual(err, "")
        self.assertIn("unsupported schema_version for plan plan-doctor-version: 999", out)
```

- [ ] **Step 4: Add legacy readable record test**

Extend the existing model legacy test so missing `schema_version` still deserializes through `PlanRecord.from_dict()` and serializes back to schema version `1`.

- [ ] **Step 5: Run focused tests and verify RED**

Run:

```bash
python3 -m unittest tests.test_cli.CliTests.test_doctor_reports_missing_required_record_fields tests.test_cli.CliTests.test_doctor_reports_unknown_record_fields tests.test_cli.CliTests.test_doctor_reports_invalid_schema_version tests.test_cli.CliTests.test_model_deserialization_allows_missing_schema_version -v
```

Expected: the new doctor tests fail because doctor does not yet validate required fields, unknown fields, or unsupported schema versions.

## Task 2: Model Schema Helper

- [ ] **Step 1: Add schema specs to `abh/models.py`**

Add `RECORD_SCHEMAS` after `SCHEMA_VERSION`:

```python
RECORD_SCHEMAS: dict[str, dict[str, set[str]]] = {
    "plan": {
        "required": {"schema_version", "id", "title", "attractor", "baseline"},
        "optional": {"owner", "status", "goals", "non_goals", "exit_criteria", "validation_checklist", "closure_evidence", "verification_runs", "audit_ids", "created_at", "updated_at", "doc_path"},
    },
    "audit": {
        "required": {"schema_version", "id", "plan_id", "auditor", "scope"},
        "optional": {"auditor_context", "independence", "verification_id", "status", "result", "rationale", "evidence", "findings", "follow_ups", "created_at", "updated_at", "doc_path"},
    },
    "attractor": {
        "required": {"schema_version", "id", "title", "version", "path", "intent"},
        "optional": {"status", "owner", "supersedes", "reason", "impact", "migration_strategy", "invariants", "created_at", "updated_at", "doc_path"},
    },
    "memory": {
        "required": {"schema_version", "id", "type", "summary", "context", "implication"},
        "optional": {"status", "related", "evidence", "tags", "related_plan_ids", "related_audit_ids", "related_drift_ids", "superseded_by", "deprecation_policy", "created_at", "updated_at", "doc_path"},
    },
    "drift": {
        "required": {"schema_version", "id", "source"},
        "optional": {"findings", "evidence", "follow_ups", "created_at", "updated_at", "doc_path"},
    },
}
```

- [ ] **Step 2: Add `validate_record_schema()`**

Add:

```python
def validate_record_schema(record_type: str, data: dict[str, Any]) -> list[dict[str, str]]:
    schema = RECORD_SCHEMAS.get(record_type)
    if schema is None:
        return []
    required = schema["required"]
    allowed = required | schema["optional"]
    issues: list[dict[str, str]] = []
    if "schema_version" not in data:
        issues.append({"category": "missing_schema_version", "field": "schema_version", "value": ""})
    elif str(data["schema_version"]) != SCHEMA_VERSION:
        issues.append({"category": "unsupported_schema_version", "field": "schema_version", "value": str(data["schema_version"])})
    for field_name in sorted(required - set(data)):
        if field_name == "schema_version":
            continue
        issues.append({"category": "missing_required_field", "field": field_name, "value": ""})
    for field_name in sorted(set(data) - allowed):
        issues.append({"category": "unknown_field", "field": field_name, "value": ""})
    return issues
```

- [ ] **Step 3: Add `schema_issue_messages()`**

Add:

```python
def schema_issue_messages(record_type: str, record_id: str, data: dict[str, Any]) -> list[str]:
    messages: list[str] = []
    for issue in validate_record_schema(record_type, data):
        category = issue["category"]
        field = issue["field"]
        if category == "missing_schema_version":
            messages.append(f"missing schema_version for {record_type} {record_id}")
        elif category == "unsupported_schema_version":
            messages.append(f"unsupported schema_version for {record_type} {record_id}: {issue['value']}")
        elif category == "missing_required_field":
            messages.append(f"missing required field for {record_type} {record_id}: {field}")
        elif category == "unknown_field":
            messages.append(f"unknown field for {record_type} {record_id}: {field}")
    return messages
```

## Task 3: Doctor Integration

- [ ] **Step 1: Import `schema_issue_messages` in `abh/core.py`**

Change the models import to include:

```python
from .models import PlanRecord, schema_issue_messages
```

- [ ] **Step 2: Replace direct schema version check**

In `doctor()`, replace:

```python
if data.get("schema_version") != "1":
    issues.append(f"missing schema_version for {label} {path.stem}")
```

with:

```python
issues.extend(schema_issue_messages(label, path.stem, data))
```

- [ ] **Step 3: Run focused tests and verify GREEN**

Run:

```bash
python3 -m unittest tests.test_cli.CliTests.test_doctor_reports_missing_required_record_fields tests.test_cli.CliTests.test_doctor_reports_unknown_record_fields tests.test_cli.CliTests.test_doctor_reports_invalid_schema_version tests.test_cli.CliTests.test_doctor_reports_missing_schema_version -v
```

Expected: pass.

- [ ] **Step 4: Add core-family helper coverage**

Add a model-level test that calls `validate_record_schema()` for plan, audit, attractor, memory, and drift records. Expected: valid records return `[]`, and adding an unknown field returns a single `unknown_field` issue.

- [ ] **Step 5: Add deprecated-field coverage**

Add tests that inject the deprecated plan field `prepared_at` into a plan record. Expected: `validate_record_schema("plan", data)` returns a `deprecated_field` issue, `abh doctor` reports `deprecated field for plan <id>: prepared_at`, and the same field is not reported as `unknown_field`.

- [ ] **Step 6: Keep plan numbering tolerant of malformed records**

Update `abh/roadmap.py` so `check_plan_numbering()` reads raw JSON `id` fields instead of deserializing every plan into `PlanRecord`. Expected: doctor can report malformed plan schema issues without crashing during duplicate-number checks.

## Task 4: Docs And Plan State

- [ ] **Step 1: Add implementation plan closure evidence**

Run:

```bash
python3 -m abh plan update plan-046-schema-validation-and-migration --closure-evidence docs/superpowers/plans/2026-06-05-schema-validation-and-migration.md --json
```

Expected: JSON output includes the new closure evidence path.

- [ ] **Step 2: Update roadmap docs**

Update `docs/development-roadmap.md` and `docs/task-board.md` to show `plan-046-schema-validation-and-migration` as the active Stage 6 slice after `plan-045`.

- [ ] **Step 3: Transition plan to running**

Run:

```bash
python3 -m abh plan transition plan-046-schema-validation-and-migration --to ready
python3 -m abh plan transition plan-046-schema-validation-and-migration --to running
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
python3 -m abh verify run plan-046-schema-validation-and-migration --json
```

Expected: verification result is `pass`.
