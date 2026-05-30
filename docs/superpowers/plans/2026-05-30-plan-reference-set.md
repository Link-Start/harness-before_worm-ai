# Plan Reference Set Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add optional plan Reference Sets so each plan can name the owner docs, code routes, tests, known issues, external contracts, and plan/audit evidence that agents must read beyond the plan itself.

**Architecture:** Extend `PlanRecord` and `RoadmapItem` with a normalized `reference_set: dict[str, list[str]]` field that defaults to stable empty categories for legacy records. Keep all behavior local and explicit: CLI/MCP write paths accept repeated `KEY=VALUE` entries, plan status and roadmap materialization expose the structured field, and Markdown rendering shows the same categories humans see.

**Tech Stack:** Python dataclasses, argparse, existing ABH JSON/Markdown storage helpers, MCP stdio adapter, `unittest`.

---

## File Structure

- Modify `abh/models.py`: define `REFERENCE_SET_KEYS`, `empty_reference_set()`, `normalize_reference_set()`, and add `reference_set` to `PlanRecord` and `RoadmapItem`.
- Modify `abh/plans.py`: accept `reference_set` in create/update flows, include it in verification hashing, and render a `## Reference Set` Markdown section.
- Modify `abh/roadmap.py`: pass roadmap item Reference Sets into materialized plans.
- Modify `abh/cli.py`: add repeatable `--reference-set KEY=VALUE` to `plan create` and `plan update`, parse it through a shared helper, and surface validation errors through existing ABH error handling.
- Modify `abh/commands.py`: document `reference_set` in `plan.create` command contract input schema.
- Modify `abh/mcp_server.py`: allow MCP `abh_plan_create` to pass a structured `reference_set` object to core create logic.
- Modify `tests/test_cli.py`: add red-green coverage for legacy defaults, CLI create/update, roadmap materialization, command contract schema, and MCP plan create.
- Modify docs: `docs/plans/templates/plan-template.md`, `README.md`, `docs/architecture/quality-signals.md`, `docs/development-roadmap.md`, `docs/task-board.md`, and `docs/context/codebase-map.md`.

## Reference Set Shape

Every plan JSON should serialize all keys, even when empty:

```python
{
    "context_routing": [],
    "active_owner_docs": [],
    "live_code_routes": [],
    "tests_baseline": [],
    "known_issues": [],
    "external_contracts": [],
    "plan_audit_evidence": [],
}
```

`normalize_reference_set()` should ignore missing keys by filling them with `[]`, preserve known keys in the order above, coerce list values to lists of strings, and reject unknown keys only on write-path parsing. Legacy JSON reads should never fail just because `reference_set` is absent.

## Task 1: Red Tests For Legacy Defaults And Status JSON

**Files:**
- Modify `tests/test_cli.py`
- Modify later `abh/models.py`

- [ ] **Step 1: Add a legacy default test**

Add this test near existing plan serialization/status tests:

```python
    def test_plan_status_json_includes_reference_set_legacy_defaults(self) -> None:
        (self.root / ".abh" / "plans").mkdir(parents=True, exist_ok=True)
        write_json(
            self.root / ".abh" / "plans" / "plan-109-legacy-reference.json",
            {
                "schema_version": "1",
                "id": "plan-109-legacy-reference",
                "title": "Legacy Reference",
                "attractor": "docs/architecture/attractors/abh-core-attractor.md",
                "baseline": "baseline",
                "owner": "platform",
                "status": "draft",
                "goals": ["goal"],
                "non_goals": ["non-goal"],
                "exit_criteria": ["exit"],
                "validation_checklist": ["python3 -m abh doctor"],
                "closure_evidence": ["tests/test_cli.py"],
                "verification_runs": [],
                "audit_ids": [],
            },
        )

        code, out, err = self.run_cli("plan", "status", "plan-109-legacy-reference", "--json")

        self.assertEqual(code, 0, err)
        reference_set = json.loads(out)["data"]["plan"]["reference_set"]
        self.assertEqual(
            reference_set,
            {
                "context_routing": [],
                "active_owner_docs": [],
                "live_code_routes": [],
                "tests_baseline": [],
                "known_issues": [],
                "external_contracts": [],
                "plan_audit_evidence": [],
            },
        )
```

- [ ] **Step 2: Run the failing focused test**

Run:

```bash
python3 -m unittest tests.test_cli.CliTests.test_plan_status_json_includes_reference_set_legacy_defaults -v
```

Expected: fail with missing `reference_set`.

- [ ] **Step 3: Add model helpers and PlanRecord field**

In `abh/models.py`, near the constants:

```python
REFERENCE_SET_KEYS = (
    "context_routing",
    "active_owner_docs",
    "live_code_routes",
    "tests_baseline",
    "known_issues",
    "external_contracts",
    "plan_audit_evidence",
)


def empty_reference_set() -> dict[str, list[str]]:
    return {key: [] for key in REFERENCE_SET_KEYS}


def normalize_reference_set(value: dict[str, Any] | None) -> dict[str, list[str]]:
    normalized = empty_reference_set()
    if not isinstance(value, dict):
        return normalized
    for key in REFERENCE_SET_KEYS:
        raw_items = value.get(key, [])
        if isinstance(raw_items, list):
            normalized[key] = [str(item) for item in raw_items]
    return normalized
```

Add the field to `PlanRecord` after `closure_evidence`:

```python
    reference_set: dict[str, list[str]] = field(default_factory=empty_reference_set)
```

Add to `PlanRecord.to_dict()` after `closure_evidence`:

```python
            "reference_set": normalize_reference_set(self.reference_set),
```

Add to `PlanRecord.from_dict()`:

```python
            reference_set=normalize_reference_set(data.get("reference_set")),
```

- [ ] **Step 4: Re-run the focused test**

Run:

```bash
python3 -m unittest tests.test_cli.CliTests.test_plan_status_json_includes_reference_set_legacy_defaults -v
```

Expected: pass.

## Task 2: Markdown Rendering And Verification Hashing

**Files:**
- Modify `tests/test_cli.py`
- Modify `abh/plans.py`
- Modify `docs/plans/templates/plan-template.md`

- [ ] **Step 1: Add create/status/Markdown red test**

Add this test near `test_plan_update_appends_fields_deduplicates_and_syncs_markdown`:

```python
    def test_plan_create_and_update_reference_set_json_and_markdown(self) -> None:
        code, out, err = self.run_cli(
            "plan",
            "create",
            "--id",
            "plan-110-reference-set",
            "--title",
            "Reference Set",
            "--attractor",
            "docs/architecture/attractors/abh-core-attractor.md",
            "--baseline",
            "baseline",
            "--goal",
            "bind context",
            "--non-goal",
            "mandatory policy",
            "--exit-criterion",
            "reference set is visible",
            "--validation",
            "python3 -m abh doctor",
            "--closure-evidence",
            "tests/test_cli.py",
            "--reference-set",
            "active_owner_docs=docs/context/source-of-truth.md",
            "--reference-set",
            "live_code_routes=abh/plans.py",
            "--reference-set",
            "tests_baseline=tests/test_cli.py",
        )
        self.assertEqual(code, 0, err)

        code, out, err = self.run_cli(
            "plan",
            "update",
            "plan-110-reference-set",
            "--reference-set",
            "known_issues=mem-post-close-doc-sync-001",
            "--reference-set",
            "plan_audit_evidence=docs/audits/audit-042-project-health-report.md",
            "--json",
        )
        self.assertEqual(code, 0, err)
        plan = json.loads(out)["data"]["plan"]
        self.assertEqual(plan["reference_set"]["active_owner_docs"], ["docs/context/source-of-truth.md"])
        self.assertEqual(plan["reference_set"]["live_code_routes"], ["abh/plans.py"])
        self.assertEqual(plan["reference_set"]["tests_baseline"], ["tests/test_cli.py"])
        self.assertEqual(plan["reference_set"]["known_issues"], ["mem-post-close-doc-sync-001"])
        self.assertEqual(plan["reference_set"]["plan_audit_evidence"], ["docs/audits/audit-042-project-health-report.md"])

        doc = (self.root / "docs" / "plans" / "plan-110-reference-set.md").read_text(encoding="utf-8")
        self.assertIn("## Reference Set", doc)
        self.assertIn("### Active Owner Docs", doc)
        self.assertIn("- docs/context/source-of-truth.md", doc)
        self.assertIn("### Live Code Routes", doc)
        self.assertIn("- abh/plans.py", doc)
        self.assertIn("### Known Issues", doc)
        self.assertIn("- mem-post-close-doc-sync-001", doc)
```

- [ ] **Step 2: Add invalid key red test**

Add:

```python
    def test_plan_reference_set_rejects_unknown_keys(self) -> None:
        code, out, err = self.run_cli(
            "plan",
            "create",
            "--id",
            "plan-111-bad-reference",
            "--title",
            "Bad Reference",
            "--attractor",
            "docs/architecture/attractors/abh-core-attractor.md",
            "--baseline",
            "baseline",
            "--reference-set",
            "random_key=docs/context/source-of-truth.md",
        )

        self.assertNotEqual(code, 0)
        self.assertIn("invalid reference set key", err)
```

- [ ] **Step 3: Run both focused tests and confirm failure**

Run:

```bash
python3 -m unittest tests.test_cli.CliTests.test_plan_create_and_update_reference_set_json_and_markdown tests.test_cli.CliTests.test_plan_reference_set_rejects_unknown_keys -v
```

Expected: fail because CLI flags and update support do not exist.

- [ ] **Step 4: Implement plan create/update plumbing**

In `abh/plans.py`, import the helpers:

```python
from .models import PLAN_STATUSES, PlanRecord, normalize_reference_set, utc_now
```

Add `"reference_set"` to `PLAN_VERIFICATION_FIELDS`.

Update `create_plan()` signature:

```python
    reference_set: dict[str, list[str]] | None = None,
```

Pass it into `PlanRecord`:

```python
        reference_set=normalize_reference_set(reference_set),
```

Update `update_plan_record()` signature:

```python
    reference_set: dict[str, list[str]] | None = None,
```

Include it in the empty-update check and merge by key:

```python
    if not any((goals, non_goals, exit_criteria, validation_checklist, remove_validation_checklist, closure_evidence, reference_set)):
        raise AbhError("plan update requires at least one field to append")
    if reference_set:
        current = normalize_reference_set(plan.reference_set)
        additions = normalize_reference_set(reference_set)
        for key, values in additions.items():
            current[key] = append_unique(current[key], values)
        plan.reference_set = current
```

- [ ] **Step 5: Render Reference Set Markdown**

In `render_plan_markdown()`, add helper functions:

```python
    def heading_for(key: str) -> str:
        return key.replace("_", " ").title()

    def reference_set_markdown() -> str:
        sections: list[str] = []
        for key, values in normalize_reference_set(plan.reference_set).items():
            sections.append(f"### {heading_for(key)}\n\n{bullet_lines(values)}")
        return "\n\n".join(sections)
```

Insert the rendered section after `## Closure Evidence`:

```python
        "## Reference Set\n\n"
        f"{reference_set_markdown()}\n\n"
```

- [ ] **Step 6: Update the plan template**

In `docs/plans/templates/plan-template.md`, add after `## Closure Evidence`:

```markdown
## Reference Set

### Context Routing

-

### Active Owner Docs

-

### Live Code Routes

-

### Tests Baseline

-

### Known Issues

-

### External Contracts

-

### Plan Audit Evidence

-
```

- [ ] **Step 7: Re-run focused tests**

Run:

```bash
python3 -m unittest tests.test_cli.CliTests.test_plan_create_and_update_reference_set_json_and_markdown tests.test_cli.CliTests.test_plan_reference_set_rejects_unknown_keys -v
```

Expected: pass.

## Task 3: CLI Parser And Command Contract

**Files:**
- Modify `abh/cli.py`
- Modify `abh/commands.py`
- Modify `tests/test_cli.py`

- [ ] **Step 1: Add command contract assertion**

In `test_agent_first_command_contract_describes_existing_agent_commands`, extend the `plan.create` assertions:

```python
        self.assertIn("reference_set", plan_create.input_schema["properties"])
```

- [ ] **Step 2: Implement parser helper**

In `abh/cli.py`, import:

```python
from .models import MEMORY_STATUSES, REFERENCE_SET_KEYS, empty_reference_set
```

Add:

```python
def parse_reference_set_entries(values: list[str]) -> dict[str, list[str]]:
    reference_set = empty_reference_set()
    for raw in values:
        if "=" not in raw:
            raise AbhError("invalid reference set entry; expected KEY=VALUE")
        key, value = raw.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key not in REFERENCE_SET_KEYS:
            raise AbhError(f"invalid reference set key: {key}")
        if value and value not in reference_set[key]:
            reference_set[key].append(value)
    return reference_set
```

- [ ] **Step 3: Add parser flags**

In `build_parser()`, add to both plan create and plan update parsers:

```python
    create.add_argument("--reference-set", action="append", default=[], metavar="KEY=VALUE")
```

```python
    update.add_argument("--reference-set", action="append", default=[], metavar="KEY=VALUE")
```

- [ ] **Step 4: Pass parsed data into handlers**

In `handle_plan_create()`:

```python
        reference_set=parse_reference_set_entries(args.reference_set),
```

In `handle_plan_update()`:

```python
        reference_set=parse_reference_set_entries(args.reference_set),
```

- [ ] **Step 5: Update command contract schema**

In `abh/commands.py`, add an object property helper:

```python
def object_property(description: str) -> dict[str, Any]:
    return {"type": "object", "description": description, "additionalProperties": {"type": "array", "items": {"type": "string"}}}
```

Add to `plan.create` input schema:

```python
                "reference_set": object_property("Optional plan Reference Set grouped by stable category key."),
```

- [ ] **Step 6: Run focused contract and CLI tests**

Run:

```bash
python3 -m unittest tests.test_cli.CliTests.test_agent_first_command_contract_describes_existing_agent_commands tests.test_cli.CliTests.test_plan_create_and_update_reference_set_json_and_markdown tests.test_cli.CliTests.test_plan_reference_set_rejects_unknown_keys -v
```

Expected: pass.

## Task 4: Roadmap Materialization And MCP Create Support

**Files:**
- Modify `abh/models.py`
- Modify `abh/roadmap.py`
- Modify `abh/mcp_server.py`
- Modify `tests/test_cli.py`

- [ ] **Step 1: Add roadmap materialization test**

Add near roadmap materialization tests:

```python
    def test_roadmap_materialize_carries_reference_set(self) -> None:
        (self.root / ".abh").mkdir(parents=True, exist_ok=True)
        write_json(
            self.root / ".abh" / "roadmap.json",
            {
                "schema_version": "1",
                "items": [
                    {
                        "key": "stage6.reference-alpha",
                        "title": "Reference Alpha",
                        "stage": "stage6",
                        "summary": "Reference alpha",
                        "attractor": "docs/architecture/attractors/abh-core-attractor.md",
                        "baseline": "baseline",
                        "goals": ["goal"],
                        "non_goals": ["non-goal"],
                        "exit_criteria": ["exit"],
                        "validation_checklist": ["python3 -m abh doctor"],
                        "closure_evidence": ["tests/test_cli.py"],
                        "reference_set": {
                            "active_owner_docs": ["docs/context/source-of-truth.md"],
                            "live_code_routes": ["abh/roadmap.py"],
                        },
                        "status": "queued",
                        "plan_id": None,
                    }
                ],
            },
        )

        code, out, err = self.run_cli("roadmap", "materialize", "stage6.reference-alpha", "--json")

        self.assertEqual(code, 0, err)
        plan = json.loads(out)["data"]["plan"]
        self.assertEqual(plan["reference_set"]["active_owner_docs"], ["docs/context/source-of-truth.md"])
        self.assertEqual(plan["reference_set"]["live_code_routes"], ["abh/roadmap.py"])
```

- [ ] **Step 2: Add MCP create test**

Add near MCP controlled write tests:

```python
    def test_mcp_plan_create_accepts_reference_set(self) -> None:
        from abh.mcp_server import TOOL_HANDLERS

        with Chdir(self.root):
            result = TOOL_HANDLERS["abh_plan_create"](
                {
                    "confirm": True,
                    "plan_id": "plan-mcp-reference",
                    "title": "MCP Reference",
                    "attractor": "docs/architecture/attractors/abh-core-attractor.md",
                    "baseline": "baseline",
                    "goals": ["goal"],
                    "non_goals": ["non-goal"],
                    "exit_criteria": ["exit"],
                    "validation_checklist": ["python3 -m abh doctor"],
                    "closure_evidence": ["tests/test_cli.py"],
                    "reference_set": {
                        "context_routing": ["docs/index.md"],
                        "tests_baseline": ["tests/test_cli.py"],
                    },
                }
            )

        reference_set = result["plan"]["reference_set"]
        self.assertEqual(reference_set["context_routing"], ["docs/index.md"])
        self.assertEqual(reference_set["tests_baseline"], ["tests/test_cli.py"])
```

- [ ] **Step 3: Run focused tests and confirm failure**

Run:

```bash
python3 -m unittest tests.test_cli.CliTests.test_roadmap_materialize_carries_reference_set tests.test_cli.McpServerTests.test_mcp_plan_create_accepts_reference_set -v
```

Expected: fail until roadmap and MCP support are implemented.

- [ ] **Step 4: Add RoadmapItem field**

In `RoadmapItem`, add:

```python
    reference_set: dict[str, list[str]] = field(default_factory=empty_reference_set)
```

Add to `to_dict()`:

```python
            "reference_set": normalize_reference_set(self.reference_set),
```

Add to `from_dict()`:

```python
            reference_set=normalize_reference_set(data.get("reference_set")),
```

- [ ] **Step 5: Pass reference_set during materialization**

In `abh/roadmap.py`, pass:

```python
                reference_set=item.reference_set,
```

to `create_plan()`.

- [ ] **Step 6: Add MCP argument normalization**

In `abh/mcp_server.py`, import:

```python
from .models import REFERENCE_SET_KEYS, normalize_reference_set
```

Add:

```python
def optional_reference_set(arguments: dict[str, Any]) -> dict[str, list[str]] | None:
    value = arguments.get("reference_set")
    if value is None:
        return None
    if not isinstance(value, dict):
        raise AbhError("invalid tool argument: reference_set must be an object")
    unknown = sorted(set(value) - set(REFERENCE_SET_KEYS))
    if unknown:
        raise AbhError(f"invalid reference set key: {unknown[0]}")
    return normalize_reference_set(value)
```

Pass it in `call_plan_create()`:

```python
        reference_set=optional_reference_set(arguments),
```

- [ ] **Step 7: Re-run focused tests**

Run:

```bash
python3 -m unittest tests.test_cli.CliTests.test_roadmap_materialize_carries_reference_set tests.test_cli.McpServerTests.test_mcp_plan_create_accepts_reference_set -v
```

Expected: pass.

## Task 5: Docs Sync

**Files:**
- Modify `README.md`
- Modify `docs/architecture/quality-signals.md`
- Modify `docs/context/codebase-map.md`
- Modify `docs/development-roadmap.md`
- Modify `docs/task-board.md`
- Modify `docs/plans/plan-043-plan-reference-set.md`

- [ ] **Step 1: Update user-facing command docs**

In `README.md`, add a short subsection under plan management showing:

```bash
abh plan create \
  --id plan-043-example \
  --title "Example" \
  --attractor docs/architecture/attractors/abh-core-attractor.md \
  --baseline "baseline" \
  --reference-set active_owner_docs=docs/context/source-of-truth.md \
  --reference-set live_code_routes=abh/plans.py
```

State that `reference_set` is optional and read-only consumers should treat it as routing context, not proof of completion.

- [ ] **Step 2: Update quality signal docs**

In `docs/architecture/quality-signals.md`, under Semantic Commitment Roadmap, explain that Reference Sets are J-flow routing metadata until audit/verification converts them into R-flow evidence.

- [ ] **Step 3: Update codebase map**

In `docs/context/codebase-map.md`, add `reference_set` ownership notes for `abh/models.py`, `abh/plans.py`, `abh/roadmap.py`, `abh/cli.py`, and `abh/mcp_server.py`.

- [ ] **Step 4: Update roadmap and task-board**

In `docs/development-roadmap.md`, mark `plan-043-plan-reference-set` as the current plan once it transitions to running.

In `docs/task-board.md`, add Sprint 39:

```markdown
## Sprint 39

目标：把 `stage6.plan-reference-set` dogfood 成 `plan-043-plan-reference-set`，让 plan 明确声明本轮工作必须参考的事实星座。

| ID | 任务 | 状态 | 产出 |
| --- | --- | --- | --- |
| S39-001 | materialize Plan Reference Set 计划 | Done | `stage6.plan-reference-set` -> `docs/plans/plan-043-plan-reference-set.md` |
| S39-002 | 定义 Reference Set 红灯测试 | Todo | `tests/test_cli.py` |
| S39-003 | 实现 PlanRecord/RoadmapItem Reference Set 模型与渲染 | Todo | `abh/models.py`, `abh/plans.py`, `abh/roadmap.py` |
| S39-004 | 接入 CLI、Agent-First command contract 和 MCP create flow | Todo | `abh/cli.py`, `abh/commands.py`, `abh/mcp_server.py` |
| S39-005 | 同步 README、plan template、quality signals、roadmap、task-board 和 codebase map | Todo | `README.md`, `docs/plans/templates/plan-template.md`, `docs/architecture/quality-signals.md`, `docs/development-roadmap.md`, `docs/task-board.md`, `docs/context/codebase-map.md` |
| S39-006 | plan-043 验证、独立审计和关闭 | Todo | `.abh/verifications/`, `docs/audits/audit-043-plan-reference-set.md`, `docs/plans/plan-043-plan-reference-set.md` |
```

- [ ] **Step 5: Update plan closure evidence if needed**

If the implementation touches `abh/commands.py` and `abh/mcp_server.py`, run:

```bash
python3 -m abh plan update plan-043-plan-reference-set --closure-evidence abh/commands.py --closure-evidence abh/mcp_server.py --closure-evidence README.md --closure-evidence docs/architecture/agent-protocol.md
```

Expected: the plan Markdown and JSON include the added evidence paths.

## Task 6: Verification, Audit, And Close

**Files:**
- Writes `.abh/verifications/`
- Writes `.abh/audits/audit-043-plan-reference-set.json`
- Writes `docs/audits/audit-043-plan-reference-set.md`
- Updates `docs/plans/plan-043-plan-reference-set.md`

- [ ] **Step 1: Run the full validation checklist**

Run:

```bash
python3 -m unittest tests/test_cli.py -v
python3 -m abh doctor
git diff --check
python3 -m abh roadmap check --json
```

Expected: all commands pass and roadmap issues are `[]`.

- [ ] **Step 2: Record ABH verification**

Run:

```bash
python3 -m abh verify run plan-043-plan-reference-set --json
```

Expected: JSON envelope has `ok: true`, `verification.result: pass`, and `trust_level: local_shell`.

- [ ] **Step 3: Generate audit bundle**

Run:

```bash
python3 -m abh audit bundle plan-043-plan-reference-set --json
```

Expected: bundle names the latest verification id and all closure evidence paths.

- [ ] **Step 4: Run independent audit**

Use opencode or another independent reviewer with the bundle prompt. The reviewer must not edit files. Required return format:

```text
Result: pass or fail or partial or need_info
Rationale: concise
Findings: none
```

- [ ] **Step 5: Record audit and close if pass**

Replace `<verification-id>` with the fresh pass id:

```bash
python3 -m abh audit request plan-043-plan-reference-set --id audit-043-plan-reference-set --auditor opencode-deepseek-chat --scope "Independent audit of plan-043 Plan Reference Set" --evidence docs/plans/plan-043-plan-reference-set.md --evidence .abh/plans/plan-043-plan-reference-set.json --evidence .abh/verifications/<verification-id>.json
python3 -m abh audit record audit-043-plan-reference-set --result pass --rationale "Independent audit passed for plan-043; findings none." --auditor-context "opencode run --pure --model deepseek/deepseek-chat; independent read-only audit" --independence independent --verification-id <verification-id>
python3 -m abh plan transition plan-043-plan-reference-set --to closing
python3 -m abh close plan-043-plan-reference-set
```

Expected: `close` succeeds only if the audit is independent and tied to the latest fresh passing verification.

- [ ] **Step 6: Post-close sanity**

Run:

```bash
python3 -m unittest tests/test_cli.py -v
python3 -m abh doctor
git diff --check
python3 -m abh roadmap check --json
python3 -m abh report health --json
```

Expected: tests pass, doctor ok, roadmap issues `[]`, and health report remains read-only even if it reports known historical semantic pressure.
