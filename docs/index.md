# ABH Documentation Index

This index routes Agent and maintainer questions to the owner docs that should answer them. It is the first file to read after the active attractor when entering this repository.

## Required Reading Order

1. `docs/architecture/attractors/abh-core-attractor.md` — current active attractor and high-level invariants.
2. `docs/context/project-context.md` — current project purpose, scope, and operating model.
3. `docs/context/source-of-truth.md` — source-of-truth precedence and conflict resolution rules.
4. `docs/context/conventions.md` — repository conventions for plans, verification, audit, memory, and docs.
5. `docs/context/codebase-map.md` — current module map and command surface.
6. `docs/development-roadmap.md` — historical execution line and future roadmap queue discipline.
7. `docs/architecture/agent-protocol.md` — Agent-facing command contract, MCP, and navigation baseline.
8. `docs/quickstart.md` — five-minute path into the Agent-First ABH loop.

## Question Routing

| Question | Primary owner doc | Supporting evidence |
| --- | --- | --- |
| What should ABH converge toward? | `docs/architecture/attractors/abh-core-attractor.md` | `docs/attractor-before-harness-*.md` |
| What is the current project context? | `docs/context/project-context.md` | `README.md`, `docs/development-roadmap.md` |
| Which source wins when docs disagree? | `docs/context/source-of-truth.md` | active attractor, code, tests, plan/audit records |
| How should an Agent behave in this repo? | `docs/architecture/agent-protocol.md` | `docs/context/conventions.md`, `abh/commands.py` |
| How do I start using ABH quickly? | `docs/quickstart.md` | `docs/recipes/` |
| What should be built next? | `.abh/roadmap.json` | `docs/development-roadmap.md`, `docs/task-board.md` |
| How should a specific change close? | `docs/plans/<plan-id>.md` | `.abh/plans/<plan-id>.json`, verification records, audit records |
| Did the change really complete? | `docs/audits/<audit-id>.md` | verification artifacts, code, tests, plan exit criteria |
| What failure should future sessions remember? | `docs/memory/<memory-id>.md` | linked plan, audit, verification, or drift evidence |

## AGE Owner-Doc Baseline

ABH adopts the AGE distinction between stable attractors and control mechanisms:

- Stable owner docs: `docs/context/`, `docs/requirements/`, `docs/design/`, `docs/architecture/`.
- Control records: `docs/plans/`, `docs/audits/`, `docs/memory/`, `docs/drift/`, future `docs/logs/`.

`abh init` seeds this index in new workspaces. `abh agent setup` consumes it when exporting setup bundles. `abh next` and `abh onboarding check` help Agents stay inside this reading order rather than inventing separate workflow rules.

## Stable-Commitments Consultation

Agents should consult the Stable Commitments, Allowed Variation, Drift / Leakage Signals, and Correction Path sections when work depends on durable owner-doc meaning rather than ordinary progress evidence.

- During plan scoping, read Stable Commitments to preserve the invariant, Allowed Variation to avoid over-scoping harmless changes, and Correction Path to choose the owner doc or plan evidence that must be updated.
- During semantic conservation audit, compare plan goals, non-goals, implementation, verification, and closure evidence against Stable Commitments and Drift / Leakage Signals to detect commitments that disappeared, weakened, or moved to non-authoritative artifacts.
- During health or drift review, use Drift / Leakage Signals as inspection triggers and Correction Path as the recommended repair route before routing Agents to new work.
- During owner-doc conflict resolution, use Stable Commitments to identify the commitment at risk, Allowed Variation to separate acceptable wording or implementation change from semantic drift, and `docs/context/source-of-truth.md` to decide which artifact owns the correction.

## Stable Commitments

- This file is the first owner-doc routing surface after the active attractor.
- Required reading order must keep active attractor, project context, source-of-truth, conventions, codebase map, roadmap, agent protocol, and quickstart discoverable.
- Question routing must point Agents to owner docs and executable evidence rather than asking them to infer authority from chat history.
- Future roadmap intent stays in `.abh/roadmap.json`; concrete plan ids only appear after materialization.

## Allowed Variation

- New owner docs may be added to the reading order when they become durable source-of-truth surfaces.
- Supporting evidence columns may change as ABH adds new local artifacts.
- Control-record directories may expand as long as stable owner docs remain distinguishable from per-plan evidence.

## Drift / Leakage Signals

- Agents start from roadmap, task-board, or chat context without reading the active attractor and this index.
- A question route names a stale or non-authoritative file as the primary owner doc.
- Future queue items are documented with preassigned plan ids before materialization.
- New owner-doc families are added elsewhere but not routed here.

## Correction Path

- Update this index in the same plan that introduces or changes an owner-doc family.
- If routing conflicts with source-of-truth precedence, update `docs/context/source-of-truth.md` and this file together.
- If a control record becomes durable guidance, promote the durable guidance into an owner doc and route it here.
