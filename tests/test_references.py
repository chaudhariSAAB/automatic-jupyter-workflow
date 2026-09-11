from pathlib import Path

import pytest

from notebook_workflow.models import ProjectRequest, ProjectType
from notebook_workflow.references import load_reference, reference_hints
from notebook_workflow.analysis.planner import build_plan


def test_load_text_reference(tmp_path: Path):
    path = tmp_path / "task.md"
    path.write_text("Build a Jupyter notebook with pandas and matplotlib", encoding="utf-8")
    text = load_reference(path)
    assert "pandas" in text
    assert "matplotlib" in reference_hints(text)


def test_missing_reference_is_explicit(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_reference(tmp_path / "missing.md")


def test_planner_uses_reference_hints(tmp_path: Path):
    path = tmp_path / "task.txt"
    path.write_text("Create a Jupyter notebook for data analysis", encoding="utf-8")
    plan = build_plan(ProjectRequest(prompt="Create a project", reference=str(path), project_type=ProjectType.UNKNOWN))
    assert plan.project_type is ProjectType.JUPYTER
    assert plan.metadata["reference_loaded"] is True
