# ABH Quickstart

This quickstart gets an Agent or maintainer from a fresh checkout to the first ABH-controlled action without inventing a workflow outside the repository.

## 1. Run ABH

From a published git source:

```bash
uvx --from git+https://github.com/worm-ai/harness-before.git abh --help
```

From this repository:

```bash
python3 -m pip install -e .
abh --help
```

The project is not published to PyPI in this stage. Use the git or editable install paths above.

## 2. Read The Baseline

```bash
abh attractor active --json
abh onboarding check --json
abh agent setup codex --json
```

Read the active attractor first, then follow `docs/index.md` for owner docs. `abh onboarding check --json` should report whether the workspace has active attractor, owner docs, setup export, hook profile commands, doctor, and closed-loop evidence.

## 3. Ask For The Next Action

```bash
abh next --json
```

The `next` command is read-only. It does not create a plan, install hooks, write Agent config, publish packages, or replace audit judgment.

## 4. Work Through The Loop

For an existing plan, use the command returned by `abh next --json`. A typical loop is:

```bash
abh plan status <plan-id> --json
abh verify run <plan-id> --json
abh audit request <plan-id> --id <audit-id> --auditor human-independent-review --scope "Independent audit of <plan-id>" --evidence docs/plans/<plan-id>.md
abh audit record <audit-id> --result pass --rationale "Reviewed evidence and exit criteria."
abh plan transition <plan-id> --to closing
abh close <plan-id>
```

For independent audit in this repository, use `opencode run --pure -m deepseek/deepseek-chat` unless a more specific DeepSeek v4 flash model is configured locally.

## 5. Optional Guardrails

Preview the default local hook:

```bash
abh hooks profile --json
abh hooks install --json
```

Install only after explicit confirmation:

```bash
abh hooks install --write --confirm --json
```

The managed hook only owns `.git/hooks/pre-commit` files containing the ABH managed marker. It does not overwrite unmanaged hooks.
