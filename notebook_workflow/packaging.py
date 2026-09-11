"""Package generated projects without caches or sensitive files."""
from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

_EXCLUDED_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache"}
_EXCLUDED_NAMES = {".env", ".env.local", ".env.production", "id_rsa", "id_ed25519"}


def package_project(project_dir: Path | str, archive: Path | str | None = None) -> Path:
    root = Path(project_dir).resolve()
    if not root.is_dir():
        raise ValueError(f"Project directory does not exist: {root}")
    target = Path(archive) if archive else root.with_suffix(".zip")
    target.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(target, "w", compression=ZIP_DEFLATED) as zf:
        for path in root.rglob("*"):
            if not path.is_file() or path.resolve() == target.resolve():
                continue
            if any(part in _EXCLUDED_DIRS for part in path.parts) or path.name in _EXCLUDED_NAMES:
                continue
            zf.write(path, path.relative_to(root))
    return target
