# Codex Recipe

Use this recipe when Codex enters an ABH repository.

## Read

```bash
abh attractor active --json
abh agent setup codex --json
abh onboarding check --json
abh next --json
```

Read the active attractor and `docs/index.md` before implementation. Treat `abh agent setup codex --json` as an instruction bundle, not as a file writer.

## Enable Repository ABH Mode

If you want Codex desktop to reopen this repository with ABH guidance already attached, write the ABH-managed repository config:

```bash
abh codex status --json
abh codex on --write --confirm --json
```

This command writes an ABH-managed `.codex/config.toml` for the current repository. It adds Codex `developer_instructions` that point the agent at `skills/abh-workflow` and require these initial checks:

```bash
abh onboarding check --json
abh next --json
abh doctor --json
abh roadmap check --json
```

To remove the ABH-managed repository toggle later:

```bash
abh codex off --write --confirm --json
```

`abh codex on` and `abh codex off` only manage ABH-managed config. If `.codex/config.toml` already exists and is not ABH-managed, the command reports a blocker and does not overwrite user-authored Codex config.

## Work

- If `abh next --json` points to a draft plan, complete or transition that plan before creating more work.
- If it points to verification, run the returned command and keep the verification id.
- If it points to audit, request or record independent audit evidence before close.
- If it points to a roadmap item, materialize that item before implementation.

## Boundaries

Codex must not treat setup export as permission to write `AGENTS.md`, install hooks, publish packages, or skip independent audit. `abh codex on --write --confirm --json` is the confirmed-write slice for ABH-managed repository Codex config only; it does not authorize writes outside `.codex/config.toml`.
