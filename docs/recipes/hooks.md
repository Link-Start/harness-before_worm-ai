# Hooks Recipe

ABH hook guardrails protect local consistency checks before commit.

## Preview

```bash
abh hooks profile --json
abh hooks install --json
```

Preview is the default. It reports the managed hook path, commands, invariants, and write policy without changing `.git/hooks/pre-commit`.

## Install

```bash
abh hooks install --write --confirm --json
```

The default managed hook runs:

```bash
python3 -m abh doctor
python3 -m abh roadmap check --json
git diff --check
```

## Boundaries

The installer only creates or refreshes `.git/hooks/pre-commit` when it contains the ABH managed marker or does not already exist. Existing unmanaged hooks are blockers. Team policy, remote distribution, pre-push hooks, and release automation are not part of this Stage 4 recipe.
