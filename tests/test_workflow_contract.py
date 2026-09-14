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


def test_automation_workflow_supports_non_datascience_projects():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "Run generated project pipeline when available" in text
    assert "elif [ -f src/main.py ]; then" in text
    assert "elif [ -f src/train.py ]; then" in text
    assert "No standalone Python pipeline entrypoint; relying on generated tests." in text


def test_automation_workflow_keeps_security_and_packaging_after_validation():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "security_scan" in text
    assert "package_project" in text
    assert "actions/upload-artifact@v6" in text


def test_automation_workflow_uploads_only_staged_final_artifacts():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "name: Stage final artifact only" in text
    assert "mkdir -p artifact_output" in text
    assert "path: artifact_output/" in text
    assert "path: |\n            generated_projects/" not in text
