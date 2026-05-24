# Plan: JSON Output and Structured Errors

## Metadata

- ID: plan-013-json-output-and-errors
- Status: closed
- Attractor: docs/architecture/attractors/abh-core-attractor.md
- Baseline: docs/development-roadmap.md
- Owner: platform
- Created: 2026-05-24T02:12:45.522156+00:00
- Updated: 2026-05-24T02:27:37.951199+00:00

## Goals

- 为核心读命令增加显式 JSON 输出模式
- 为 ABH 业务错误增加结构化 JSON 错误输出
- 保留现有人类可读默认输出和现有返回码

## Non-Goals

- 不实现 MCP Server
- 不开放 Agent 写操作
- 不实现 verify run
- 不改变默认自然文本输出

## Exit Criteria

- plan status/list、audit list、memory list/search、route、doctor 支持 --json 并输出统一 envelope
- --json 模式下 AbhError 输出结构化 errors，返回码仍为 2
- doctor --json 在发现问题时返回码 1 且 data.issues 可解析
- 新增 CLI contract 测试覆盖成功和错误 JSON 输出，现有测试保持通过

## Validation Checklist

- python3 -m unittest tests/test_cli.py -v
- python3 -m abh doctor
- python3 -m abh plan list

## Closure Evidence

- abh/cli.py
- tests/test_cli.py
- docs/plans/plan-013-json-output-and-errors.md
- docs/development-roadmap.md
- docs/task-board.md
- audit-013-json-output-and-errors

## Verification Runs

- ver-e829d1a51d40
- ver-abf4fff7ac18
- ver-fb3c8a98b7f5
- ver-6bc2695b5e39
- ver-8711c81908cc

## Audits

- audit-013-json-output-and-errors
