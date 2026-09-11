"""Safe execution helpers for generated Jupyter notebooks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from notebook_workflow.execution.runner import CommandRunner


@dataclass(frozen=True)
class NotebookExecutionResult:
    success: bool
    notebook: Path
    stdout: str = ""
    stderr: str = ""
    error: str = ""
    timed_out: bool = False


def execute_notebook(
    notebook: Path,
    *,
    timeout: float = 300.0,
    runner: CommandRunner | None = None,
) -> NotebookExecutionResult:
    """Execute a notebook in place using Jupyter without invoking a shell."""
    notebook = Path(notebook)
    if not notebook.is_file():
        return NotebookExecutionResult(False, notebook, error=f"Notebook does not exist: {notebook}")
    if notebook.suffix.lower() != ".ipynb":
        return NotebookExecutionResult(False, notebook, error="Notebook path must end with .ipynb")

    command = (
        "jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace", notebook.name
    )
    result = (runner or CommandRunner()).run(command, cwd=notebook.parent, timeout=timeout)
    return NotebookExecutionResult(
        success=not result.failed,
        notebook=notebook,
        stdout=result.stdout,
        stderr=result.stderr,
        error=result.stderr if result.failed else "",
        timed_out=result.timed_out,
    )
