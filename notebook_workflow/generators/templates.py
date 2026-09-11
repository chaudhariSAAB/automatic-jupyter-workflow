"""Dependency-light starter generators for supported project types."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from notebook_workflow.generators.base import ProjectGenerator
from notebook_workflow.models import ProjectPlan, ProjectRequest, ProjectType


class TemplateGenerator(ProjectGenerator):
    """Generate a runnable, inspectable starter project for one project type."""

    def __init__(self, project_type: ProjectType) -> None:
        self.project_type = project_type

    def generate(self, request: ProjectRequest, plan: ProjectPlan, output_dir: Path) -> Iterable[str]:
        output_dir.mkdir(parents=True, exist_ok=True)
        files = {
            "README.md": self._readme(request, plan),
            "project.json": json.dumps({
                "name": request.name,
                "project_type": plan.project_type.value,
                "description": request.description,
                "features": list(request.features),
                "commands": list(plan.commands),
                "preview_command": list(plan.preview_command) if plan.preview_command else None,
            }, indent=2) + "\n",
            "src/main.py": self._main(plan),
            "tests/test_smoke.py": "def test_project_smoke():\n    assert True\n",
        }
        written: list[str] = []
        for relative, content in files.items():
            path = output_dir / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            written.append(relative)
        return written

    @staticmethod
    def _readme(request: ProjectRequest, plan: ProjectPlan) -> str:
        commands = "\n".join(f"- `{cmd}`" for cmd in plan.commands) or "- No execution command configured"
        return (
            f"# {request.name}\n\n"
            f"**Type:** {plan.project_type.value}\n\n"
            f"{request.description or 'Generated starter project.'}\n\n"
            "## Features\n"
            + "\n".join(f"- {feature}" for feature in request.features)
            + "\n\n## Commands\n" + commands + "\n"
        )

    @staticmethod
    def _main(plan: ProjectPlan) -> str:
        return (
            "\"\"\"Generated project entry point.\"\"\"\n\n"
            f"PROJECT_TYPE = {plan.project_type.value!r}\n\n"
            "def main() -> None:\n"
            "    print(f'Universal workflow project: {PROJECT_TYPE}')\n\n\n"
            "if __name__ == '__main__':\n"
            "    main()\n"
        )


def default_registry_generators() -> list[ProjectGenerator]:
    """Return all built-in generators; no API key is required."""
    return [TemplateGenerator(project_type) for project_type in ProjectType if project_type is not ProjectType.UNKNOWN]
