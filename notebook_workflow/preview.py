"""Preview metadata for supported project types."""

from __future__ import annotations

from pathlib import Path

from notebook_workflow.models import ProjectType


def preview_metadata(project_type: ProjectType, root: Path) -> dict[str, str | None]:
    if project_type is ProjectType.WEB:
        candidates = (root / "src" / "index.html", root / "index.html")
        entry = next((p.name for p in candidates if p.is_file()), None)
        return {"command": "python -m http.server 8000", "url": "http://127.0.0.1:8000", "entrypoint": entry}
    if project_type is ProjectType.APP:
        return {"command": "npx expo start --web", "url": "http://localhost:8081", "entrypoint": "App.js"}
    if project_type is ProjectType.JUPYTER:
        return {"command": "jupyter lab", "url": "http://localhost:8888", "entrypoint": None}
    return {"command": None, "url": None, "entrypoint": None}
