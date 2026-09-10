"""Security checks for generated projects.

These checks are intentionally conservative and dependency-free. They block
obvious credential leakage and dangerous project artifacts before packaging.
"""
from __future__ import annotations

import re
from pathlib import Path

_SECRET_PATTERNS = (
    re.compile(r"(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bAIza[0-9A-Za-z_-]{20,}\b"),
)
_BLOCKED_NAMES = {".env", ".env.local", ".env.production", "id_rsa", "id_ed25519"}
_SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache"}


def security_scan(root: Path) -> tuple[bool, tuple[str, ...], tuple[str, ...]]:
    """Return (passed, errors, warnings) for a generated project tree."""
    errors: list[str] = []
    warnings: list[str] = []
    if not root.exists():
        return False, ("Project directory does not exist.",), ()
    for path in root.rglob("*"):
        if any(part in _SKIP_DIRS for part in path.parts):
            continue
        if path.name in _BLOCKED_NAMES:
            errors.append(f"Sensitive file detected: {path.relative_to(root)}")
            continue
        if not path.is_file() or path.stat().st_size > 1_000_000:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            warnings.append(f"Skipped non-text file: {path.relative_to(root)}")
            continue
        for pattern in _SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"Possible hard-coded secret in: {path.relative_to(root)}")
                break
    return not errors, tuple(errors), tuple(warnings)
