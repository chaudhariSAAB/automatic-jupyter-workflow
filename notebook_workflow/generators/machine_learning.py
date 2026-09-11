"""Machine learning starter generator with a dependency-light smoke path."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from notebook_workflow.generators.base import ProjectGenerator
from notebook_workflow.models import ProjectPlan, ProjectRequest, ProjectType


class MachineLearningGenerator(ProjectGenerator):
    project_type = ProjectType.MACHINE_LEARNING

    def generate(self, request: ProjectRequest, plan: ProjectPlan, output_dir: Path) -> Iterable[str]:
        output_dir.mkdir(parents=True, exist_ok=True)
        files = {
            "README.md": f"# {request.name}\n\n{request.description or 'Machine learning starter generated automatically.'}\n",
            "requirements.txt": "scikit-learn\n",
            "src/model.py": '''from __future__ import annotations\n\n\ndef predict_mean(values: list[float]) -> float:\n    if not values:\n        raise ValueError("values must not be empty")\n    return sum(values) / len(values)\n\n\nif __name__ == "__main__":\n    print(predict_mean([10, 20, 30]))\n''',
            "tests/test_model.py": "from src.model import predict_mean\n\n\ndef test_predict_mean():\n    assert predict_mean([2, 4, 6]) == 4\n",
        }
        written = []
        for relative, content in files.items():
            path = output_dir / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            written.append(relative)
        return written
