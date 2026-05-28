# Memory: Use DeepSeek V4 Pro or V4 Flash for opencode independent audits

## Metadata

- ID: mem-opencode-deepseek-audit-models
- Type: divergent_pattern
- Status: active
- Created: 2026-05-28T14:06:38.534202+00:00
- Updated: 2026-05-28T14:06:38.534897+00:00
- Related: plan-038-independent-audit-gate

## Summary

Use DeepSeek V4 Pro or V4 Flash for opencode independent audits

## Context

During plan-038 independent audit dogfooding, opencode run failed because the default model was zhipuai-coding-plan/glm-5 and the provider reported ProviderModelNotFoundError. User clarified that opencode independent audits should use DeepSeek V4 Pro or DeepSeek V4 Flash explicitly.

## Evidence

- docs/plans/plan-038-independent-audit-gate.md
- docs/audits/audit-038-independent-audit-gate.md

## Implication

When using opencode for ABH independent audits, pass an explicit DeepSeek V4 Pro model first, or DeepSeek V4 Flash as fallback, and record that model/source in audit auditor_context.

## Deprecation Policy

Mark deprecated when evidence no longer applies.
