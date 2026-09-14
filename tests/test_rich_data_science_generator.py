from pathlib import Path

from notebook_workflow.generators.data_science_rich import PromptAwareDataScienceGenerator
from notebook_workflow.models import ProjectPlan, ProjectRequest, ProjectType
from notebook_workflow.validation.files import validate_project_files


def test_concrete_prompt_generates_complete_data_science_project(tmp_path: Path):
    prompt = "Create a complete beginner-friendly Data Science project for concrete strength analysis."
    request = ProjectRequest(prompt=prompt, project_type=ProjectType.DATA_SCIENCE, output_dir=tmp_path)
    plan = ProjectPlan(project_type=ProjectType.DATA_SCIENCE, goals=(prompt,))

    written = list(PromptAwareDataScienceGenerator().generate(request, plan, tmp_path))

    required = {
        "data/concrete_strength.csv",
        "notebooks/concrete_strength_analysis.ipynb",
        "src/data_cleaning.py",
        "src/eda.py",
        "src/model.py",
        "src/evaluate.py",
        "src/visualization.py",
        "src/pipeline.py",
        "tests/test_concrete_project.py",
        "reports/metrics.json",
    }
    # reports/metrics.json is created by execution, not generation; all other required
    # project components must already be present.
    assert required - {"reports/metrics.json"} <= set(written)
    result = validate_project_files(tmp_path)
    assert result.passed, result.errors
    assert len((tmp_path / "data/concrete_strength.csv").read_text(encoding="utf-8").splitlines()) == 41


def test_non_concrete_data_science_prompt_keeps_basic_generator(tmp_path: Path):
    request = ProjectRequest(
        prompt="Create a basic customer churn analysis project.",
        project_type=ProjectType.DATA_SCIENCE,
        output_dir=tmp_path,
    )
    plan = ProjectPlan(project_type=ProjectType.DATA_SCIENCE)
    PromptAwareDataScienceGenerator().generate(request, plan, tmp_path)
    assert (tmp_path / "src/main.py").is_file()
    assert (tmp_path / "data/sample.csv").is_file()
    assert not (tmp_path / "data/concrete_strength.csv").exists()
