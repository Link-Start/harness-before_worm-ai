# Distribution Recipe

Stage 4 supports git-based and local editable distribution paths. PyPI publication remains future work.

## Git-Based Use

Run without persistent install:

```bash
uvx --from git+https://github.com/worm-ai/harness-before.git abh --help
```

Install as a persistent tool:

```bash
uv tool install --from git+https://github.com/worm-ai/harness-before.git abh
abh --help
```

## Local Development Install

```bash
python3 -m venv /private/tmp/abh-smoke
/private/tmp/abh-smoke/bin/python -m pip install -e .
/private/tmp/abh-smoke/bin/abh --help
```

This smoke path validates the console entry point from the local checkout without using network package publication.

## Boundaries

Do not claim `pip install abh` or `uvx abh` from PyPI until a release plan publishes and verifies that package. Release automation, CI templates, signing, and team distribution policy belong to later stages.
