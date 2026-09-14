"""Small, safe repair primitives used before optional AI repair."""
from __future__ import annotations

import ast
import re
from pathlib import Path

_SKIP_PARTS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache"}

# Import name -> conservative version range. Only these packages may be added automatically.
_ALLOWLISTED_DEPENDENCIES = {
    "numpy": "numpy>=2,<3",
    "pandas": "pandas>=2,<3",
    "matplotlib": "matplotlib>=3,<4",
    "seaborn": "seaborn>=0.13,<1",
    "sklearn": "scikit-learn>=1,<2",
    "scipy": "scipy>=1,<2",
    "requests": "requests>=2,<3",
    "PIL": "Pillow>=10,<12",
}


class RepairEngine:
    """Attempt only deterministic, low-risk repairs; never execute repaired code."""

    def repair_python_trailing_whitespace(self, root: Path) -> list[str]:
        repaired: list[str] = []
        for path in root.rglob("*.py"):
            if any(part in _SKIP_PARTS for part in path.parts):
                continue
            text = path.read_text(encoding="utf-8")
            cleaned = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
            if cleaned != text:
                path.write_text(cleaned, encoding="utf-8")
                repaired.append(str(path.relative_to(root)))
        return repaired

    def repair_missing_python_package_markers(self, root: Path) -> list[str]:
        repaired: list[str] = []
        for directory in sorted({path.parent for path in root.rglob("*.py")}):
            if directory == root or any(part in _SKIP_PARTS for part in directory.parts):
                continue
            marker = directory / "__init__.py"
            if marker.exists():
                continue
            py_files = [p for p in directory.glob("*.py") if p.name != "__init__.py"]
            if py_files:
                marker.write_text('"""Generated package marker."""\n', encoding="utf-8")
                repaired.append(str(marker.relative_to(root)))
        return repaired

    def repair_missing_dependency(self, root: Path, module: str) -> list[str]:
        """Add only an allowlisted dependency to requirements.txt."""
        requirement = _ALLOWLISTED_DEPENDENCIES.get(module)
        if requirement is None:
            return []
        req = root / "requirements.txt"
        existing = req.read_text(encoding="utf-8") if req.exists() else ""
        package_name = requirement.split(">=", 1)[0].lower()
        if any(line.strip().lower().startswith(package_name) for line in existing.splitlines()):
            return []
        req.write_text(existing.rstrip() + ("\n" if existing.strip() else "") + requirement + "\n", encoding="utf-8")
        return [f"requirements.txt:{package_name}"]

    def repair_from_errors(self, root: Path, errors: tuple[str, ...] | list[str]) -> list[str]:
        """Apply only a tiny allowlisted set of repairs inferred from failure text."""
        text = "\n".join(errors)
        repaired: list[str] = []
        if re.search(r"No module named ['\"]src['\"]", text):
            repaired.extend(self.repair_missing_python_package_markers(root))
        if "jupyter: command not found" in text or "No module named 'jupyter'" in text:
            req = root / "requirements.txt"
            existing = req.read_text(encoding="utf-8") if req.exists() else ""
            if "jupyter" not in existing.lower():
                req.write_text(existing.rstrip() + ("\n" if existing.strip() else "") + "jupyter>=1,<2\n", encoding="utf-8")
                repaired.append("requirements.txt:jupyter")
        match = re.search(r"No module named ['\"]([^'\"]+)['\"]", text)
        if match:
            repaired.extend(self.repair_missing_dependency(root, match.group(1)))
        return repaired

    def validate_python(self, root: Path) -> list[str]:
        errors: list[str] = []
        for path in root.rglob("*.py"):
            if any(part in _SKIP_PARTS for part in path.parts):
                continue
            try:
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except (SyntaxError, UnicodeDecodeError) as exc:
                errors.append(f"{path}: {exc}")
        return errors
