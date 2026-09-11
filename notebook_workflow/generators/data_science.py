"""Dependency-light data science project generator."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from notebook_workflow.generators.base import ProjectGenerator
from notebook_workflow.models import ProjectPlan, ProjectRequest, ProjectType


class DataScienceGenerator(ProjectGenerator):
    project_type = ProjectType.DATA_SCIENCE

    def generate(self, request: ProjectRequest, plan: ProjectPlan, output_dir: Path) -> Iterable[str]:
        output_dir.mkdir(parents=True, exist_ok=True)
        files = {
            "README.md": f"# {request.name}\n\n{request.description or 'Data science starter generated automatically.'}\n",
            "requirements.txt": "pandas\nmatplotlib\nseaborn\n",
            "src/analysis.py": '''from __future__ import annotations\n\nfrom statistics import mean\n\n\ndef summarize(values: list[float]) -> dict[str, float]:\n    if not values:\n        raise ValueError("values must not be empty")\n    return {"count": float(len(values)), "mean": mean(values), "minimum": min(values), "maximum": max(values)}\n\n\nif __name__ == "__main__":\n    print(summarize([10, 20, 30, 40]))\n''',
            "tests/test_analysis.py": "from src.analysis import summarize\n\n\ndef test_summarize():\n    result = summarize([1, 2, 3])\n    assert result['count'] == 3\n    assert result['mean'] == 2\n",
        }
        written = []
        for relative, content in files.items():
            path = output_dir / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            written.append(relative)
        return written
