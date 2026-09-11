from pathlib import Path

from notebook_workflow.execution.notebook import NotebookExecutionResult, execute_notebook


def test_execute_notebook_uses_safe_jupyter_command(monkeypatch, tmp_path: Path):
    notebook = tmp_path / "demo.ipynb"
    notebook.write_text('{"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 5}', encoding="utf-8")
    captured = {}

    class FakeRunner:
        def run(self, command, *, cwd=None, timeout=120.0):
            captured["command"] = tuple(command)
            captured["cwd"] = cwd
            return type("Result", (), {"returncode": 0, "stdout": "ok", "stderr": "", "timed_out": False, "failed": False})()

    monkeypatch.setattr("notebook_workflow.execution.notebook.CommandRunner", lambda: FakeRunner())
    result = execute_notebook(notebook)

    assert isinstance(result, NotebookExecutionResult)
    assert result.success is True
    assert captured["command"] == (
        "jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace", "demo.ipynb"
    )
    assert captured["cwd"] == tmp_path


def test_execute_notebook_rejects_missing_file(tmp_path: Path):
    result = execute_notebook(tmp_path / "missing.ipynb")
    assert result.success is False
    assert "does not exist" in result.error.lower()
