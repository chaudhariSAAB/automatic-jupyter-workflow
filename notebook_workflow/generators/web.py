"""Zero-build web project generator for free local and cloud preview."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from notebook_workflow.generators.base import ProjectGenerator
from notebook_workflow.models import ProjectPlan, ProjectRequest, ProjectType


class WebGenerator(ProjectGenerator):
    project_type = ProjectType.WEB

    def generate(self, request: ProjectRequest, plan: ProjectPlan, output_dir: Path) -> Iterable[str]:
        output_dir.mkdir(parents=True, exist_ok=True)
        files = {
            "README.md": f"# {request.name}\n\n{request.description or 'Zero-build web starter generated automatically.'}\n",
            "index.html": """<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>Universal Project</title><link rel=\"stylesheet\" href=\"style.css\"></head><body><main><h1>Universal Project Automation</h1><p id=\"status\">Ready.</p><button id=\"run\">Run check</button></main><script src=\"app.js\"></script></body></html>\n""",
            "style.css": "body{font-family:system-ui,sans-serif;max-width:760px;margin:10vh auto;padding:2rem}button{padding:.7rem 1rem}\n",
            "app.js": "document.querySelector('#run').addEventListener('click',()=>{document.querySelector('#status').textContent='Browser check passed.'});\n",
            "tests/test_web.py": "from pathlib import Path\n\ndef test_web_files_exist():\n    root = Path(__file__).parents[1]\n    for name in ('index.html','style.css','app.js'):\n        assert (root / name).is_file()\n",
        }
        written = []
        for relative, content in files.items():
            path = output_dir / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            written.append(relative)
        return written
