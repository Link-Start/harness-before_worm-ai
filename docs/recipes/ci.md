# CI Template Recipe

Use the GitHub Actions workflow in `.github/workflows/ci.yml` as the current ABH CI template for pull requests and `main` pushes.

## Checks

The template installs the package in editable mode, then runs these local checks:

- `python3 -m unittest discover -v`
- `python3 -m abh doctor --json`
- `python3 -m abh roadmap check --json`
- `git diff --check`
- `python3 -m abh report health --json`

## Gating Boundary

Gating checks: the unittest, doctor, roadmap, and diff checks are gating CI checks. Failures indicate the repository is inconsistent, the code does not satisfy the local test contract, roadmap state drifted, or whitespace drift was introduced.

Informational checks: `python3 -m abh report health --json` is informational. The health report is read-only posture evidence. It surfaces stale proof, drift, memory, and semantic-pressure signals for review, but the workflow does not fail solely because historical semantic pressure exists, and this template does not turn historical health pressure into a release blocker or team policy.

## Non-Goals

This recipe does not configure branch protection, required status checks, deployment, package publishing, signing, release automation, remote runners, or team policy. Those remain later Stage 7 work.
