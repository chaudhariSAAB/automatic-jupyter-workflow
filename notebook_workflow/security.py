"""Conservative security checks for generated project trees."""
from __future__ import annotations

import re
from pathlib import Path

_SECRET_PATTERNS = (
    re.compile(r"(?i)(api[_-]?key|secret|password|token|access[_-]?key)\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"),
    re.compile(r"\bAIza[0-9A-Za-z_-]{20,}\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?i)github_pat_[A-Za-z0-9_]{20,}"),
)
_BLOCKED_NAMES = {".env", ".env.local", ".env.production", "id_rsa", "id_ed25519"}
_SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", ".mypy_cache"}
_MAX_TEXT_BYTES = 1_000_000


def security_scan(root: Path) -> tuple[bool, tuple[str, ...], tuple[str, ...]]:
    """Return (passed, errors, warnings); never follow symlinks outside the tree."""
    errors: list[str] = []
    warnings: list[str] = []
    if not root.exists() or not root.is_dir():
        return False, ("Project directory does not exist.",), ()
    root = root.resolve()
    for path in root.rglob("*"):
        if any(part in _SKIP_DIRS for part in path.parts):
            continue
        relative = path.relative_to(root)
        if path.is_symlink():
            errors.append(f"Symlink rejected: {relative}")
            continue
        if path.name in _BLOCKED_NAMES:
            errors.append(f"Sensitive file detected: {relative}")
            continue
        if not path.is_file():
            continue
        if path.stat().st_size > _MAX_TEXT_BYTES:
            warnings.append(f"Skipped large file: {relative}")
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            warnings.append(f"Skipped non-text file: {relative}")
            continue
        for pattern in _SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"Possible hard-coded secret in: {relative}")
                break
    return not errors, tuple(errors), tuple(warnings)
