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

## Work

- If `abh next --json` points to a draft plan, complete or transition that plan before creating more work.
- If it points to verification, run the returned command and keep the verification id.
- If it points to audit, request or record independent audit evidence before close.
- If it points to a roadmap item, materialize that item before implementation.

## Boundaries

Codex must not treat setup export as permission to write `AGENTS.md`, install hooks, publish packages, or skip independent audit. Those require their own confirmed-write slices or human review.
