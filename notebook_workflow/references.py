"""Safe, dependency-light reference material ingestion."""
from __future__ import annotations

import json
from pathlib import Path

MAX_REFERENCE_BYTES = 5 * 1024 * 1024
SUPPORTED_SUFFIXES = {".txt", ".md", ".json", ".csv", ".ipynb"}


def load_reference(reference: str | Path | None) -> str:
    """Load supported local reference text with strict size and path checks."""
    if reference is None:
        return ""
    path = Path(reference).expanduser()
    if not path.is_file():
        raise FileNotFoundError(f"Reference file not found: {path}")
    if path.is_symlink():
        raise ValueError("Symlink references are not allowed")
    if path.stat().st_size > MAX_REFERENCE_BYTES:
        raise ValueError(f"Reference exceeds {MAX_REFERENCE_BYTES} byte limit")
    if path.suffix.lower() not in SUPPORTED_SUFFIXES:
        raise ValueError(f"Unsupported reference format: {path.suffix or '<none>'}")
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".json", ".ipynb"}:
        try:
            return json.dumps(json.loads(raw), ensure_ascii=False, indent=2)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON reference: {exc}") from exc
    return raw


def reference_hints(reference_text: str) -> tuple[str, ...]:
    """Extract lightweight, non-AI hints useful for deterministic planning."""
    text = reference_text.lower()
    hints: list[str] = []
    for term in ("jupyter", "notebook", "pandas", "numpy", "matplotlib", "seaborn", "machine learning", "deep learning", "ai", "react", "react native", "expo", "html", "css", "javascript", "fastapi", "flask"):
        if term in text:
            hints.append(term)
    return tuple(hints)
