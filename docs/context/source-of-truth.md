# Source of Truth

This file defines ABH source-of-truth precedence. It answers which artifact should be trusted for each question type and how conflicts are resolved.

## Core Rule

Repository files are the truth surface, but no single file answers every question. Choose the owner doc or executable artifact by question type.

## Precedence by Question

| Question | Primary truth source | Secondary evidence | Conflict rule |
| --- | --- | --- | --- |
| What should ABH converge toward? | Active attractor | architecture docs, audits | If a plan conflicts with the active attractor, update the plan or supersede the attractor through an explicit attractor change. |
| What should this slice deliver? | Plan goals, non-goals, exit criteria | roadmap queue item, user request | If roadmap and plan disagree after materialization, the plan controls the slice and roadmap must be updated. |
| What is the current implementation? | Code and tests | README, architecture docs | If docs and code disagree, treat it as implementation drift or stale docs; do not silently choose one. |
| What is the command contract? | `abh/commands.py` and JSON/MCP tests | `docs/architecture/agent-protocol.md` | If protocol docs and command metadata disagree, update docs or contract in the plan that owns the change. |
| What validation actually ran? | `.abh/verifications/*.json` | plan validation checklist, CI logs | A passing verification proves command execution only; audit decides whether it covers exit criteria. |
| Is a plan complete? | Passing independent audit plus plan closure evidence | verification records, code, docs | Verification pass alone is never completion. |
| What should future Agents remember? | Active memory records | audits, drift reports, plans | Memory records should preserve reusable failure knowledge, not ordinary progress logs. |
| What should be built next? | `.abh/roadmap.json` queue | development roadmap, task board | Queue keys are stable future intent; concrete `plan-NNN-*` ids only exist after materialization. |

## Conflict Resolution

- Requirements and design disagree: decide whether the baseline changes, then update the owner docs in the same plan.
- Design and architecture disagree: decide whether it is product behavior or technical structure; update `docs/design/` or `docs/architecture/` accordingly.
- Code and documentation disagree: classify as implementation drift or stale documentation before closing the plan.
- Plan and verification disagree: update the plan validation checklist or rerun verification; do not reinterpret a failed check as success.
- Audit and implementation claim disagree: audit wins for closure, but findings must cite repository evidence.
- Memory and current facts disagree: deprecate or supersede the memory record; do not delete historical evidence casually.

## AGE Layers

`abh init` seeds these source layers in new repositories, and `abh agent setup` reads them into setup bundles:

- `docs/context/` for Agent-readable repository context and precedence
- `docs/requirements/` for implementation-ready requirements
- `docs/design/` for application behavior and workflow design
- `docs/architecture/` for technical structure and attractors

## Stable-Commitments Consultation

Stable-commitments sections are consulted when precedence alone is not enough to decide whether a change preserves or weakens an owner-doc commitment.

- During plan scoping, use the authoritative owner doc's Stable Commitments to define what must survive the slice, Allowed Variation to avoid treating acceptable implementation changes as scope changes, and Correction Path to identify required documentation or evidence updates.
- During semantic conservation audit, compare the plan, implementation, verification, audit evidence, and closure evidence against Stable Commitments and Drift / Leakage Signals before deciding whether R-flow evidence actually reduced uncertainty.
- During health or drift review, treat Drift / Leakage Signals as local evidence hints and use Correction Path to route repairs to the correct owner doc, plan, memory, audit, or roadmap item.
- During owner-doc conflict resolution, first choose the owner artifact by the precedence table, then use its Stable Commitments and Allowed Variation to determine whether the conflict is semantic drift, stale wording, or acceptable variation.

## Stable Commitments

- Repository files are the truth surface; chat context can request changes but does not outrank committed owner docs, records, code, or tests.
- Authority is chosen by question type, not by recency alone.
- Plan goals, non-goals, exit criteria, validation, and closure evidence control one materialized slice.
- Passing verification is execution evidence only; independent audit is the completion judgment for closure.
- `.abh/roadmap.json` owns future queue intent before a concrete plan id exists.

## Allowed Variation

- New artifact families may be added to the precedence table when ABH gains durable local evidence types.
- Conflict rules may become more specific as plans, audits, memory, drift, and health records mature.
- Historical records may remain incomplete if readers treat missing fields as unknown instead of invalid.

## Drift / Leakage Signals

- A plan, doc, or Agent instruction treats verification pass as plan completion.
- A materialized plan contradicts its roadmap queue item without updating the plan or roadmap.
- A future queue item is given a concrete `plan-NNN-*` id before materialization.
- Memory or audit findings are ignored when they conflict with current implementation claims.

## Correction Path

- Classify disagreements by question type, then update the owner doc or executable artifact that owns that question.
- Preserve historical evidence when superseding memory, audits, or plans; do not delete records to hide disagreement.
- When precedence itself changes, update this file and route the change through an audited plan.
