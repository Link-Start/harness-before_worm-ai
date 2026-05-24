# Plan: Core Module Split

## Metadata

- ID: plan-018-core-module-split
- Status: closed
- Attractor: docs/architecture/attractors/abh-core-attractor.md
- Baseline: docs/development-roadmap.md
- Owner: platform
- Created: 2026-05-24T09:10:36.060018+00:00
- Updated: 2026-05-24T10:17:14.556038+00:00

## Goals

- 在不改变 CLI、MCP、JSON schema 或 Markdown 输出行为的前提下，将 core.py 中稳定的 plan/audit/verification 逻辑拆分到更小的领域模块
- 保持现有 public core import surface 可用，避免破坏 cli.py 和 mcp_server.py 调用方
- 用 TDD/现有回归测试证明拆分前后行为一致

## Non-Goals

- 不新增用户可见功能或命令
- 不修改 plan 状态机、audit 关闭门禁、verification 结果语义或 MCP contract
- 不在本切片拆分 route、drift、memory 的行为实现

## Exit Criteria

- core.py 不再直接承载 plan/audit/verification 的完整实现，而是通过领域模块导出或委托
- cli.py 与 mcp_server.py 现有命令和工具行为保持兼容
- python3 -m unittest tests/test_cli.py -v 通过
- python3 -m abh doctor 通过
- roadmap 和 task-board 同步 plan-018 状态

## Validation Checklist

- python3 -m unittest tests/test_cli.py -v
- python3 -m abh doctor

## Closure Evidence

- abh/core.py
- tests/test_cli.py
- docs/development-roadmap.md
- docs/task-board.md
- abh/plans.py
- abh/audits.py
- abh/verifications.py
- abh/errors.py
- .abh/verifications/ver-24273b6df810.json
- docs/plans/plan-018-core-module-split.md
- audit-018-core-module-split

## Verification Runs

- ver-24273b6df810

## Audits

- audit-018-core-module-split
