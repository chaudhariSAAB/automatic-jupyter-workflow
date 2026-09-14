from pathlib import Path
import re


ROOT = Path(__file__).parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "automation.yml"
REGRESSION = ROOT / ".github" / "workflows" / "universal-regression.yml"
STRESS = ROOT / ".github" / "workflows" / "universal-stress.yml"


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
    assert "Generate deterministic SBOM" in text
    assert re.search(r"actions/upload-artifact@[0-9a-f]{40}\b", text)


def test_automation_workflow_uploads_only_staged_final_artifacts():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "name: Stage final artifact only" in text
    assert "mkdir -p artifact_output" in text
    assert "path: artifact_output/" in text
    assert "project_manifest.json" in text
    assert "sbom.spdx.json" in text
    assert "path: |\n            generated_projects/" not in text


def test_automation_workflow_is_reusable():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "workflow_call:" in text
    assert "type: boolean" in text
    assert "type: string" in text


def test_parallel_regression_matrix_is_present_and_pinned():
    text = REGRESSION.read_text(encoding="utf-8")
    assert "fail-fast: false" in text
    for project_type in ("jupyter", "data_science", "machine_learning", "ai", "coding", "web", "app"):
        assert project_type in text
    assert re.search(r"actions/checkout@[0-9a-f]{40}\b", text)
    assert re.search(r"actions/setup-python@[0-9a-f]{40}\b", text)
    assert "python -m jupyter nbconvert" in text
    assert "python -m src.train" in text


def test_stress_matrix_is_parallel_and_bounded():
    text = STRESS.read_text(encoding="utf-8")
    assert "fail-fast: false" in text
    assert "round: [1, 2, 3]" in text
    assert "--max-attempts 3" in text
