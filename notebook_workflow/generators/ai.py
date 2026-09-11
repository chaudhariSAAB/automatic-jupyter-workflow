"""API-free AI project generator."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from notebook_workflow.generators.base import ProjectGenerator
from notebook_workflow.models import ProjectPlan, ProjectRequest, ProjectType


class AIGenerator(ProjectGenerator):
    project_type = ProjectType.AI

    def generate(self, request: ProjectRequest, plan: ProjectPlan, output_dir: Path) -> Iterable[str]:
        output_dir.mkdir(parents=True, exist_ok=True)
        description = request.metadata.get("description") or "API-free AI starter generated automatically."
        name = request.metadata.get("name") or "AI Starter"
        files = {
            "README.md": f"# {name}\n\n{description}\n",
            "src/ai.py": '''from __future__ import annotations\n\n\ndef classify_text(text: str) -> str:\n    \"\"\"Deterministic baseline that requires no model or API key.\"\"\"\n    words = {word.strip('.,!?').lower() for word in text.split()}\n    if words & {"error", "fail", "failed", "problem"}:\n        return "issue"\n    if words & {"great", "good", "excellent", "success"}:\n        return "positive"\n    return "neutral"\n''',
            "tests/test_ai.py": "from src.ai import classify_text\n\n\ndef test_classify_text():\n    assert classify_text('great success') == 'positive'\n    assert classify_text('system failed') == 'issue'\n",
        }
        written = []
        for relative, content in files.items():
            path = output_dir / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            written.append(relative)
        return written
