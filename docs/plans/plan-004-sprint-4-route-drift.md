# Plan: Sprint 4 Route Drift

## Metadata

- ID: plan-004-sprint-4-route-drift
- Status: closed
- Attractor: `docs/architecture/attractors/abh-core-attractor.md`
- Baseline: Sprint 3 audit, close, and memory loop
- Owner: platform
- Created: 2026-05-22

## Goals

- 支持 `abh route` 根据问题输出建议阅读顺序。
- 支持 `abh drift analyze` 识别基础漂移类型。
- 支持漂移分析结果落盘为 JSON 和 Markdown。
- 支持漂移发现转成 memory 条目。

## Non-Goals

- 不实现复杂语义模型或 LLM 分类。
- 不实现 CI 自动触发 drift analyze。
- 不实现 Web UI。
- 不实现 Sprint 4 范围以外的新能力。

## Exit Criteria

- `abh route` 能输出 route name、reading order 和 rationale。
- `abh drift analyze` 能识别 `boundary_drift`。
- `abh drift analyze` 能识别 `dependency_drift`。
- `abh drift analyze` 能识别 `test_drift`。
- `abh drift analyze` 能识别 `terminology_drift`。
- drift report 可写入 `.abh/drift/*.json` 与 `docs/drift/*.md`。
- drift finding 可通过 `--memory-id` 转成 `divergent_pattern` memory。
- `tests/test_cli.py` 可通过。

## Validation Checklist

- CLI help 展示 `route` 和 `drift`。
- route 输出建议阅读顺序。
- drift analyze 输出四类 drift finding。
- drift report 同步写入本地元数据和文档。
- drift memory 可被 `abh memory search` 检索。

## Closure Evidence

- `abh/cli.py`
- `abh/core.py`
- `abh/models.py`
- `abh/storage.py`
- `tests/test_cli.py`
- `docs/audits/audit-004-sprint-4-route-drift.md`
- Live verification: `python3 -m abh --help`
- Live verification: `python3 -m abh route --question ...`
- Live verification: isolated `drift analyze --memory-id`
- Independent review: `docs/audits/audit-004-sprint-4-route-drift.md`

## Audit Requirement

关闭前需要独立审计确认：

- route 命令是否输出符合计划的阅读顺序。
- drift analyze 是否识别四类漂移。
- drift report 和 memory 是否正确落盘。

## Tasks

| ID | Task | Status | Evidence |
| --- | --- | --- | --- |
| S4-001 | 路由规则设计 | Done | `ROUTES` |
| S4-002 | Route 命令 | Done | `abh route` |
| S4-003 | 漂移分类规则 | Done | `DRIFT_RULES` |
| S4-004 | Drift 分析命令 | Done | `abh drift analyze` |
| S4-005 | 漂移转 follow-up | Done | drift report follow-ups |
| S4-006 | 漂移转 memory | Done | `--memory-id` |

## Notes

- 当前 drift 分析是透明关键词规则，适合最小闭环。
- 本计划已通过独立会话审计并关闭。
