# ABH Command Flow Reference

## Common Commands

Use the local virtual environment on Windows when present:

```powershell
.venv\Scripts\python.exe -m abh next --json
.venv\Scripts\python.exe -m abh plan status <plan-id> --json
.venv\Scripts\python.exe -m abh verify run <plan-id> --json
.venv\Scripts\python.exe -m abh audit bundle <plan-id> --json
.venv\Scripts\python.exe -m abh doctor --json
.venv\Scripts\python.exe -m abh roadmap check --json
```

Use generic Python elsewhere:

```bash
python -m abh next --json
python -m abh plan status <plan-id> --json
python -m abh verify run <plan-id> --json
python -m abh audit bundle <plan-id> --json
python -m abh doctor --json
python -m abh roadmap check --json
```

## Decision Table

| ABH state | Action |
| --- | --- |
| No ABH workspace | Run or preview `abh init`; ask before writes. |
| Draft plan | Complete plan definition before implementation. |
| Ready/running plan without verification | Run `abh verify run <plan-id> --json`. |
| Failed verification | Debug failed checks; do not request audit. |
| Fresh passing verification, no audit | Request audit and generate audit bundle. |
| Audit requested | Give prompt to independent reviewer; do not self-sign. |
| Audit fail/partial | Record result, then fix evidence or block/defer. |
| Independent pass tied to latest verification | Run `abh close <plan-id>`. |

## Audit Handoff Template

```text
Independent audit only. Do not modify files.

Repo: <repo path>
Audit <plan-id> against goals, non-goals, exit criteria, docs, code, and verification evidence.

Evidence:
<plan markdown>
<plan json>
<latest verification json>
<audit request json/markdown>
<closure evidence>

Return exactly:

Result: pass|fail|partial|need_info
Rationale: ...
Findings:
Severity|Title|Evidence|Recommendation

If no findings:
Findings:
none
```
