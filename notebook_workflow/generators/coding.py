"""General-purpose Python coding project generator."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from notebook_workflow.generators.base import ProjectGenerator
from notebook_workflow.models import ProjectPlan, ProjectRequest, ProjectType


class CodingGenerator(ProjectGenerator):
    project_type = ProjectType.CODING

    def generate(self, request: ProjectRequest, plan: ProjectPlan, output_dir: Path) -> Iterable[str]:
        output_dir.mkdir(parents=True, exist_ok=True)
        files = {
            "README.md": f"# {request.name}\n\n{request.description or 'General coding starter generated automatically.'}\n",
            "src/main.py": "def main() -> None:\n    print('Hello from Universal Project Automation')\n\nif __name__ == '__main__':\n    main()\n",
            "tests/test_main.py": "from src.main import main\n\ndef test_main_exists():\n    assert callable(main)\n",
        }
        written = []
        for relative, content in files.items():
            path = output_dir / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            written.append(relative)
        return written
