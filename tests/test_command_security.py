import pytest

from notebook_workflow.workflow import _safe_command


def test_safe_command_allows_pytest():
    assert _safe_command("python -m pytest") == ("python", "-m", "pytest")


def test_safe_command_allows_http_preview_port():
    assert _safe_command("python -m http.server 8000")[-1] == "8000"


def test_safe_command_allows_notebook_execution():
    assert _safe_command(
        "jupyter nbconvert --to notebook --execute --inplace demo.ipynb"
    ) == (
        "jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace", "demo.ipynb"
    )


@pytest.mark.parametrize("command", [
    "python -c 'print(1)'",
    "python -m pip install requests",
    "npm install evil-package",
    "npx something",
    "python -m http.server 99999",
    "jupyter nbconvert --execute arbitrary.py",
])
def test_safe_command_blocks_untrusted_commands(command):
    with pytest.raises(ValueError):
        _safe_command(command)
