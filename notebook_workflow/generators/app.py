"""Mobile app starter adapter using a dependency-free preview fallback."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from notebook_workflow.generators.base import ProjectGenerator
from notebook_workflow.models import ProjectPlan, ProjectRequest, ProjectType


class AppGenerator(ProjectGenerator):
    project_type = ProjectType.APP

    def generate(self, request: ProjectRequest, plan: ProjectPlan, output_dir: Path) -> Iterable[str]:
        output_dir.mkdir(parents=True, exist_ok=True)
        files = {
            "README.md": f"# {request.name}\n\n{request.description or 'Mobile app starter generated automatically.'}\n\nThe core foundation is toolchain-neutral. An Expo/React Native adapter can be selected when that toolchain is available.\n",
            "app_spec.json": '{\n  "framework": "expo-react-native",\n  "preview_fallback": true,\n  "api_key_required": false\n}\n',
            "preview.html": "<!doctype html><html><body><h1>App Preview</h1><p>Mobile app specification generated successfully.</p></body></html>\n",
            "tests/test_app.py": "from pathlib import Path\n\ndef test_app_spec_exists():\n    root = Path(__file__).parents[1]\n    assert (root / 'app_spec.json').is_file()\n",
        }
        written = []
        for relative, content in files.items():
            path = output_dir / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            written.append(relative)
        return written
