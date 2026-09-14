"""Execution-aware wrapper for prompt-driven Data Science generation."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from notebook_workflow.generators.base import ProjectGenerator
from notebook_workflow.generators.data_science_rich import PromptAwareDataScienceGenerator
from notebook_workflow.models import ProjectPlan, ProjectRequest, ProjectType


class ExecutableDataScienceGenerator(ProjectGenerator):
    """Generate the project and add a self-contained pipeline execution test."""

    project_type = ProjectType.DATA_SCIENCE

    def __init__(self) -> None:
        self.inner = PromptAwareDataScienceGenerator()

    def generate(self, request: ProjectRequest, plan: ProjectPlan, output_dir: Path) -> Iterable[str]:
        written = list(self.inner.generate(request, plan, output_dir))
        concrete_prompt = any(
            term in request.prompt.lower()
            for term in ("concrete", "cement", "compressive strength", "concrete strength")
        )
        if concrete_prompt:
            test_path = output_dir / "tests" / "test_pipeline_execution.py"
            test_path.parent.mkdir(parents=True, exist_ok=True)
            test_path.write_text(
                """from pathlib import Path\n\nfrom src.pipeline import run_analysis\n\n\ndef test_pipeline_generates_reports_and_visualizations():\n    root = Path(__file__).parents[1]\n    result = run_analysis(root)\n    assert result['train_rows'] > 0\n    assert result['test_rows'] > 0\n    assert result['metrics']['mae_mpa'] >= 0\n    assert result['metrics']['rmse_mpa'] >= 0\n    assert -1 <= result['metrics']['r2'] <= 1\n    assert (root / 'reports' / 'metrics.json').is_file()\n    assert (root / 'reports' / 'summary.json').is_file()\n    assert (root / 'reports' / 'figures' / 'strength_vs_cement.svg').is_file()\n    assert (root / 'reports' / 'figures' / 'strength_by_age.svg').is_file()\n""",
                encoding="utf-8",
            )
            written.append("tests/test_pipeline_execution.py")
        return written
