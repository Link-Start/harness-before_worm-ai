# Codex ABH Toggle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `abh codex on/off/status` so this repository can explicitly enable or disable ABH-guided Codex desktop behavior through a managed `.codex/config.toml`.

**Architecture:** Add a dedicated Codex config management module that mirrors the existing `hooks` pattern: preview by default, confirmed writes only, explicit managed-marker ownership, and structured status payloads. Wire that module into command contracts and CLI handlers, then document the feature in the existing Codex and README guidance.

**Tech Stack:** Python standard library, existing ABH CLI/command contract helpers, repository-local file writes, `unittest`.

---

### Task 1: Define command contracts

**Files:**
- Modify: `abh/commands.py`
- Test: `tests/test_command_contracts.py`

- [ ] **Step 1: Write the failing contract tests**

```python
        codex_status = command_contract("codex.status")
        self.assertEqual(codex_status.cli_command, "codex status")
        self.assertTrue(codex_status.read_only)
        self.assertEqual(codex_status.confirmation, "none")
        self.assertEqual(codex_status.output_keys, ["codex"])

        codex_on = command_contract("codex.on")
        self.assertEqual(codex_on.cli_command, "codex on")
        self.assertFalse(codex_on.read_only)
        self.assertEqual(codex_on.confirmation, "--write --confirm")
        self.assertIn("write", codex_on.input_schema["properties"])
        self.assertIn("confirm", codex_on.input_schema["properties"])
        self.assertIn("write .codex/config.toml", codex_on.side_effects)

        codex_off = command_contract("codex.off")
        self.assertEqual(codex_off.cli_command, "codex off")
        self.assertFalse(codex_off.read_only)
        self.assertEqual(codex_off.confirmation, "--write --confirm")
        self.assertIn("write .codex/config.toml", codex_off.side_effects)
```

- [ ] **Step 2: Run the contract test to verify it fails**

Run: `python -m unittest tests.test_command_contracts.CommandContractTests.test_agent_first_command_contract_describes_existing_agent_commands -v`

Expected: FAIL because `codex.status`, `codex.on`, and `codex.off` are not yet defined in `abh/commands.py`.

- [ ] **Step 3: Add the new command contracts**

```python
    CommandContract(
        id="codex.status",
        cli_command="codex status",
        read_only=True,
        confirmation="none",
        side_effects=[],
        output_keys=["codex"],
        input_schema={"type": "object", "properties": {}},
    ),
    CommandContract(
        id="codex.on",
        cli_command="codex on",
        read_only=False,
        confirmation="--write --confirm",
        side_effects=["write .codex/config.toml"],
        output_keys=["codex"],
        input_schema={
            "type": "object",
            "properties": {
                "write": {"type": "boolean"},
                "confirm": {"type": "boolean"},
            },
        },
    ),
    CommandContract(
        id="codex.off",
        cli_command="codex off",
        read_only=False,
        confirmation="--write --confirm",
        side_effects=["write .codex/config.toml"],
        output_keys=["codex"],
        input_schema={
            "type": "object",
            "properties": {
                "write": {"type": "boolean"},
                "confirm": {"type": "boolean"},
            },
        },
    ),
```

- [ ] **Step 4: Run the contract tests to verify they pass**

Run: `python -m unittest tests.test_command_contracts -v`

Expected: PASS with the new Codex command metadata present.

- [ ] **Step 5: Commit**

```bash
git add abh/commands.py tests/test_command_contracts.py
git commit -m "feat: define codex toggle command contracts"
```

### Task 2: Add Codex config management module with managed preview/write semantics

**Files:**
- Create: `abh/codex_setup.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write the failing CLI tests**

```python
    def test_codex_status_json_reports_disabled_when_no_config_exists(self) -> None:
        code, out, err = self.run_cli("codex", "status", "--json")
        self.assertEqual(code, 0, err)
        payload = json.loads(out)
        codex = payload["data"]["codex"]
        self.assertFalse(codex["enabled"])
        self.assertEqual(codex["path"], ".codex/config.toml")

    def test_codex_on_json_previews_managed_write_without_creating_files(self) -> None:
        code, out, err = self.run_cli("codex", "on", "--json")
        self.assertEqual(code, 0, err)
        payload = json.loads(out)
        codex = payload["data"]["codex"]
        self.assertEqual(codex["mode"], "preview")
        self.assertEqual(codex["writes"][0]["path"], ".codex/config.toml")
        self.assertFalse((self.root / ".codex" / "config.toml").exists())

    def test_codex_on_write_requires_confirm(self) -> None:
        code, out, err = self.run_cli("codex", "on", "--write", "--json")
        self.assertEqual(code, 1)
        self.assertFalse((self.root / ".codex" / "config.toml").exists())

    def test_codex_on_write_confirm_creates_managed_config(self) -> None:
        code, out, err = self.run_cli("codex", "on", "--write", "--confirm", "--json")
        self.assertEqual(code, 0, err)
        config_path = self.root / ".codex" / "config.toml"
        self.assertTrue(config_path.exists())
        content = config_path.read_text(encoding="utf-8")
        self.assertIn("ABH MANAGED CODEX CONFIG", content)
        self.assertIn("developer_instructions", content)
        self.assertIn("abh onboarding check --json", content)

    def test_codex_on_does_not_overwrite_unmanaged_config(self) -> None:
        config_path = self.root / ".codex" / "config.toml"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text("model = \"gpt-5\"\n", encoding="utf-8")
        code, out, err = self.run_cli("codex", "on", "--write", "--confirm", "--json")
        self.assertEqual(code, 1)
        self.assertEqual(config_path.read_text(encoding="utf-8"), "model = \"gpt-5\"\n")
```

- [ ] **Step 2: Run the new CLI tests to verify they fail**

Run: `python -m unittest tests.test_cli.CliTests.test_codex_status_json_reports_disabled_when_no_config_exists -v`

Expected: FAIL because `codex` is not yet a CLI command family.

- [ ] **Step 3: Implement the Codex config manager**

```python
CODEX_CONFIG_PATH = ".codex/config.toml"
MANAGED_MARKER = "ABH MANAGED CODEX CONFIG"

def codex_status(*, cwd: Path | None = None) -> dict[str, object]:
    ...

def preview_codex_on(*, cwd: Path | None = None, write: bool = False, confirmed: bool = False) -> dict[str, object]:
    ...

def codex_on(*, cwd: Path | None = None, write: bool = False, confirmed: bool = False) -> dict[str, object]:
    ...

def preview_codex_off(*, cwd: Path | None = None, write: bool = False, confirmed: bool = False) -> dict[str, object]:
    ...

def codex_off(*, cwd: Path | None = None, write: bool = False, confirmed: bool = False) -> dict[str, object]:
    ...
```

Implementation rules:

- Reuse `root_dir()` and `write_text()` from storage helpers.
- Write a full managed `.codex/config.toml`.
- Include `skills/abh-workflow` guidance and required initial ABH checks in `developer_instructions`.
- Block unmanaged `.codex/config.toml`.
- Never delete unmanaged config.
- Only require confirmation in write mode.

- [ ] **Step 4: Run the focused CLI tests to verify they pass**

Run: `python -m unittest tests.test_cli -v`

Expected: PASS for the new Codex command coverage and existing CLI regressions remain green.

- [ ] **Step 5: Commit**

```bash
git add abh/codex_setup.py tests/test_cli.py
git commit -m "feat: add managed codex abh toggle surface"
```

### Task 3: Wire argparse and handlers

**Files:**
- Modify: `abh/cli.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write failing assertions for parser/handler behavior**

```python
        code, out, err = self.run_cli("codex", "off", "--json")
        self.assertEqual(code, 0, err)
        payload = json.loads(out)
        self.assertEqual(payload["command"], "codex off")

        code, out, err = self.run_cli("codex", "status", "--json")
        self.assertEqual(code, 0, err)
        payload = json.loads(out)
        self.assertEqual(payload["command"], "codex status")
```

- [ ] **Step 2: Run a focused CLI test to verify it fails**

Run: `python -m unittest tests.test_cli.CliTests.test_codex_on_json_previews_managed_write_without_creating_files -v`

Expected: FAIL because `build_parser()` does not yet know the `codex` command family.

- [ ] **Step 3: Add the parser family and handlers**

```python
    codex_parser = subparsers.add_parser("codex", help="manage repository-local Codex ABH guidance")
    codex_sub = codex_parser.add_subparsers(dest="codex_command", required=True)

    codex_status_parser = codex_sub.add_parser("status", help="show Codex ABH status for this repository")
    add_json_argument(codex_status_parser)
    codex_status_parser.set_defaults(handler=handle_codex_status)

    codex_on_parser = codex_sub.add_parser("on", help="preview or write managed Codex ABH config")
    codex_on_parser.add_argument("--write", action="store_true", help="write the managed Codex config")
    codex_on_parser.add_argument("--confirm", action="store_true", help="confirm Codex config writes")
    add_json_argument(codex_on_parser)
    codex_on_parser.set_defaults(handler=handle_codex_on)

    codex_off_parser = codex_sub.add_parser("off", help="preview or remove managed Codex ABH config")
    codex_off_parser.add_argument("--write", action="store_true", help="remove the managed Codex config")
    codex_off_parser.add_argument("--confirm", action="store_true", help="confirm Codex config removal")
    add_json_argument(codex_off_parser)
    codex_off_parser.set_defaults(handler=handle_codex_off)
```

- [ ] **Step 4: Run CLI tests to verify they pass**

Run: `python -m unittest tests.test_cli -v`

Expected: PASS with JSON envelopes and human-readable handlers for `codex on/off/status`.

- [ ] **Step 5: Commit**

```bash
git add abh/cli.py tests/test_cli.py
git commit -m "feat: wire codex toggle cli commands"
```

### Task 4: Update docs and repository governance surfaces

**Files:**
- Modify: `README.md`
- Modify: `docs/recipes/codex.md`
- Modify: `docs/context/codebase-map.md`
- Modify: `docs/development-roadmap.md`
- Modify: `docs/task-board.md`
- Test: `tests/test_command_contracts.py`

- [ ] **Step 1: Write failing documentation contract tests**

```python
    def test_readme_documents_codex_toggle_commands(self) -> None:
        readme = Path("README.md").read_text(encoding="utf-8")
        self.assertIn("abh codex on --write --confirm --json", readme)
        self.assertIn("abh codex off --write --confirm --json", readme)

    def test_codex_recipe_mentions_managed_repo_config_toggle(self) -> None:
        recipe = Path("docs/recipes/codex.md").read_text(encoding="utf-8")
        self.assertIn(".codex/config.toml", recipe)
        self.assertIn("abh codex on --write --confirm --json", recipe)
        self.assertIn("abh codex off --write --confirm --json", recipe)
```

- [ ] **Step 2: Run the focused docs test to verify it fails**

Run: `python -m unittest tests.test_command_contracts.CommandContractTests.test_readme_documents_codex_toggle_commands -v`

Expected: FAIL because the docs do not yet mention the new Codex toggle flow.

- [ ] **Step 3: Update docs**

Required content:

- README install/usage section mentions the Codex repository toggle commands.
- Codex recipe explains that `abh codex on --write --confirm --json` writes a managed `.codex/config.toml`.
- Codebase map mentions the new Codex config management module and command family.
- Roadmap and task-board record the completed slice at the same level as other Stage 7 updates.

- [ ] **Step 4: Run docs contract tests to verify they pass**

Run: `python -m unittest tests.test_command_contracts -v`

Expected: PASS with updated docs references and command expectations.

- [ ] **Step 5: Commit**

```bash
git add README.md docs/recipes/codex.md docs/context/codebase-map.md docs/development-roadmap.md docs/task-board.md tests/test_command_contracts.py
git commit -m "docs: describe codex abh toggle workflow"
```

### Task 5: Final verification and ABH evidence update

**Files:**
- Modify: `.abh/plans/plan-057-codex-repo-toggle.json`
- Modify: `docs/plans/plan-057-codex-repo-toggle.md`

- [ ] **Step 1: Transition the ABH plan to running if not already**

Run: `abh plan transition plan-057-codex-repo-toggle --to running`

Expected: plan enters `running`.

- [ ] **Step 2: Run focused feature verification**

Run: `python -m unittest tests.test_cli tests.test_command_contracts -v`

Expected: PASS with Codex toggle and contract coverage green.

- [ ] **Step 3: Run repository governance verification**

Run: `python -m abh doctor --json`
Expected: `"issues": []`

Run: `python -m abh roadmap check --json`
Expected: `"issues": []`

- [ ] **Step 4: Record verification-ready evidence in the ABH plan**

Use:

```bash
abh plan update plan-057-codex-repo-toggle \
  --closure-evidence "docs/superpowers/specs/2026-06-11-codex-abh-toggle-design.md" \
  --closure-evidence "docs/superpowers/plans/2026-06-11-codex-abh-toggle.md"
```

- [ ] **Step 5: Commit**

```bash
git add .abh/plans/plan-057-codex-repo-toggle.json docs/plans/plan-057-codex-repo-toggle.md
git commit -m "chore: update plan-057 implementation evidence"
```
