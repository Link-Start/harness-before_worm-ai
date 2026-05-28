# Claude Code Recipe

Use this recipe when Claude Code enters an ABH repository.

## Read

```bash
abh attractor active --json
abh agent setup claude-code --json
abh onboarding check --json
abh next --json
```

The setup bundle is read-only. It describes required reading, workflow rules, useful commands, and write boundaries; it does not write `CLAUDE.md`.

## Work

Follow the same loop as other Agents:

1. Read active attractor and owner docs.
2. Use `abh next --json` for the next safe command.
3. Run verification before claiming completion.
4. Record independent audit before closing.
5. Close only after passing audit evidence.

## Boundaries

Do not install hooks, write Agent config, or publish distribution artifacts from this recipe. Use the hook and distribution recipes for the currently supported manual paths.
