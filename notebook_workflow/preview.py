from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .models import ProjectType


@dataclass(frozen=True)
class PreviewInfo:
    project_type: ProjectType
    command: str | None
    url: str | None
    entrypoint: str | None


def preview_info(project_type: ProjectType, output_dir: str | Path) -> PreviewInfo:
    root = Path(output_dir)
    if project_type is ProjectType.WEB:
        entry = next((p.name for p in (root / "src", root).glob("index.html") if p.is_file()), None)
        return PreviewInfo(project_type, "python -m http.server 8000", "http://127.0.0.1:8000", entry)
    if project_type is ProjectType.APP:
        return PreviewInfo(project_type, "npx expo start --web", "http://localhost:8081", "App.js")
    if project_type is ProjectType.JUPYTER:
        return PreviewInfo(project_type, "jupyter lab", "http://localhost:8888", None)
    return PreviewInfo(project_type, None, None, None)
