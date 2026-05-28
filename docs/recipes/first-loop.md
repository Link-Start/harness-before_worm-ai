# First Loop Recipe

This recipe demonstrates the smallest ABH-controlled loop for a real change.

## Navigate

```bash
abh onboarding check --json
abh next --json
```

If `next` returns a queued roadmap item, materialize it:

```bash
abh roadmap materialize <roadmap-key> --json
```

If it returns an existing plan, inspect the plan:

```bash
abh plan status <plan-id> --json
```

## Verify

After implementation:

```bash
abh verify run <plan-id> --json
```

Verification is evidence, not completion. If the plan or working tree changes after verification, refresh verification before close.

## Audit And Close

```bash
abh audit request <plan-id> --id <audit-id> --auditor human-independent-review --scope "Independent audit of <plan-id>" --evidence docs/plans/<plan-id>.md
abh audit record <audit-id> --result pass --rationale "Reviewed evidence and exit criteria."
abh plan transition <plan-id> --to closing
abh close <plan-id>
```

In this repository, independent Agent audit should use:

```bash
opencode run --pure -m deepseek/deepseek-chat "<audit prompt>"
```

The configured `deepseek-chat` model is the local DeepSeek v4 Pro route.
