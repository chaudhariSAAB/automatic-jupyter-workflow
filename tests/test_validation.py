from pathlib import Path

from notebook_workflow.validation.files import validate_project_files


def test_validation_passes_for_valid_python_project(tmp_path: Path):
    (tmp_path / "main.py").write_text("print('hello')\n", encoding="utf-8")
    result = validate_project_files(tmp_path)
    assert result.passed is True
    assert "main.py" in result.checks


def test_validation_rejects_empty_project(tmp_path: Path):
    result = validate_project_files(tmp_path)
    assert result.passed is False
    assert result.errors
