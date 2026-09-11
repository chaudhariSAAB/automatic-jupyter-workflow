from pathlib import Path

from notebook_workflow.repair import RepairEngine


def test_repair_removes_trailing_whitespace(tmp_path: Path):
    path = tmp_path / "main.py"
    path.write_text("x = 1   \nprint(x)\n", encoding="utf-8")
    repaired = RepairEngine().repair_python_trailing_whitespace(tmp_path)
    assert repaired == ["main.py"]
    assert path.read_text(encoding="utf-8") == "x = 1\nprint(x)\n"


def test_repair_does_not_hide_python_syntax_errors(tmp_path: Path):
    (tmp_path / "bad.py").write_text("if True print('x')\n", encoding="utf-8")
    errors = RepairEngine().validate_python(tmp_path)
    assert errors
