# Project Context

## Purpose

Attractor Before Harness is a Git-native, evidence-first governance layer for AI-assisted software development. Its job is to keep long-running Agent work converging around explicit attractors instead of temporary chat context.

ABH is not a general project management platform. It is a local-first control plane for plans, verification, audit, memory, drift detection, roadmap queueing, and Agent-facing command contracts.

## Current Product Shape

- CLI package: `abh`
- Storage: `.abh/` JSON records as machine-readable state
- Human-readable mirror: `docs/` Markdown records
- Agent interfaces: explicit JSON CLI envelopes and MCP stdio tools
- Current release line: v0.3 Verify Runner complete; Stage 4 Agent-First attractor entry in progress

## Current Active Attractor

The active attractor is `docs/architecture/attractors/abh-core-attractor.md`. Every executable plan must bind to the current active attractor by id or path before it can become ready.

## Current Stage

Stage 4 makes ABH agent-first:

- active attractor is CLI/MCP readable
- command metadata is shared through `abh.commands`
- future repository initialization must bind new workspaces to the active attractor
- future Agent navigation should answer what to do next, not only what to read

## Non-Goals

- Do not replace Git as the source of truth.
- Do not replace independent audit with local verification.
- Do not weaken the plan close audit gate for convenience.
- Do not build a Web UI before the CLI, JSON, MCP, and init/onboarding path are stable.

## Stable Commitments

- ABH is a Git-native, evidence-first governance layer for AI-assisted development.
- ABH is local-first and stores machine-readable state under `.abh/` with Markdown mirrors under `docs/`.
- Every executable plan must bind to the active attractor before it can become ready.
- Verification records are evidence, while independent audit remains the closure decision layer.
- Stage 6 remains product-quality-first and agent-navigation-second.

## Allowed Variation

- The current stage description may advance as roadmap items close.
- Release-line wording may change when release preparation or packaging plans complete.
- Agent interfaces may expand if new commands preserve explicit JSON envelopes and audited write boundaries.

## Drift / Leakage Signals

- ABH is described as a general project management platform or Web UI-first product.
- A workflow bypasses plan, verification, or independent audit for convenience.
- Agent navigation starts optimizing recommendations before product-quality signals are locally inspectable.
- Current-stage text lags behind closed plans enough to misroute new work.

## Correction Path

- Update this file when a plan changes project scope, stage, release posture, or operating model.
- If implementation contradicts this context, classify the gap as stale docs or implementation drift before closing.
- Route scope expansions through roadmap materialization and independent audit rather than ad hoc doc edits.
