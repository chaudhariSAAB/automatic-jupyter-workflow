"""Dependency-free structural and syntax validation for generated projects."""

from __future__ import annotations

import ast
import json
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

    errors: list[str] = []
    checks = [str(p.relative_to(root)) for p in files]
    for path in files:
        relative = path.relative_to(root)
        if path.suffix == ".py":
            try:
                ast.parse(path.read_text(encoding="utf-8"), filename=str(relative))
            except (SyntaxError, UnicodeDecodeError) as exc:
                errors.append(f"Python syntax error in {relative}: {exc}")
        elif path.suffix == ".ipynb":
            try:
                notebook = json.loads(path.read_text(encoding="utf-8"))
                if notebook.get("nbformat") != 4 or not isinstance(notebook.get("cells"), list):
                    errors.append(f"Invalid notebook structure: {relative}")
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                errors.append(f"Invalid notebook JSON in {relative}: {exc}")

    return ValidationResult(not errors, errors=tuple(errors), checks=tuple(checks))
