"""Small, safe repair primitives used before optional AI repair."""
from __future__ import annotations

import ast
from pathlib import Path


class RepairEngine:
    """Attempt only deterministic, low-risk repairs; never execute repaired code."""

    def repair_python_trailing_whitespace(self, root: Path) -> list[str]:
        repaired: list[str] = []
        for path in root.rglob("*.py"):
            if any(part in {".git", ".venv", "venv", "node_modules"} for part in path.parts):
                continue
            text = path.read_text(encoding="utf-8")
            cleaned = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
            if cleaned != text:
                path.write_text(cleaned, encoding="utf-8")
                repaired.append(str(path.relative_to(root)))
        return repaired

    def validate_python(self, root: Path) -> list[str]:
        errors: list[str] = []
        for path in root.rglob("*.py"):
            if any(part in {".git", ".venv", "venv", "node_modules"} for part in path.parts):
                continue
            try:
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except (SyntaxError, UnicodeDecodeError) as exc:
                errors.append(f"{path}: {exc}")
        return errors
