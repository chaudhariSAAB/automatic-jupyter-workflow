from pathlib import Path


WORKFLOW = Path(__file__).parents[1] / ".github" / "workflows" / "automation.yml"


def test_automation_workflow_runs_generated_tests_from_project_root():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "working-directory: generated_projects" in text
    assert "run: python -m pytest -q tests" in text
    assert "run: python -m pytest -q generated_projects/tests" not in text


def test_automation_workflow_executes_all_generated_notebooks():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "find notebooks -maxdepth 1 -type f -name '*.ipynb'" in text
    assert "for notebook in \"${notebooks[@]}\"; do" in text
    assert "concrete_strength_analysis.ipynb" not in text


def test_automation_workflow_keeps_security_and_packaging_after_validation():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "security_scan" in text
    assert "package_project" in text
    assert "actions/upload-artifact@v6" in text
