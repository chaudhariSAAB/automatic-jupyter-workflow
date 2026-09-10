"""Dependency-free structural validation for generated projects."""

from __future__ import annotations

from pathlib import Path

from notebook_workflow.models import ValidationResult


_IGNORED = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "node_modules"}


def validate_project_files(project_dir: Path | str) -> ValidationResult:
    root = Path(project_dir)
    if not root.exists() or not root.is_dir():
        return ValidationResult(False, errors=(f"Project directory does not exist: {root}",))

    files = [p for p in root.rglob("*") if p.is_file() and not any(part in _IGNORED for part in p.parts)]
    if not files:
        return ValidationResult(False, errors=("Project contains no usable files.",))

    checks = tuple(str(p.relative_to(root)) for p in files)
    return ValidationResult(True, checks=checks)
