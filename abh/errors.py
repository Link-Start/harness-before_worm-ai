from __future__ import annotations

import re
from pathlib import Path


class AbhError(RuntimeError):
    pass


def validate_identifier(value: str, label: str = "identifier") -> None:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", value):
        raise AbhError(f"invalid {label}: {value!r}")


def require_existing_path(path_text: str, label: str) -> None:
    path = Path(path_text)
    if not path.exists():
        raise AbhError(f"{label} not found: {path_text}")
