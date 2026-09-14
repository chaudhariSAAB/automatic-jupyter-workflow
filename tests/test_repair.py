from pathlib import Path

from notebook_workflow.repair import RepairEngine


def test_repair_removes_trailing_whitespace(tmp_path: Path):
    path = tmp_path / "main.py"
    path.write_text("x = 1   \nprint(x)\n", encoding="utf-8")
    repaired = RepairEngine().repair_python_trailing_whitespace(tmp_path)
    assert repaired == ["main.py"]
    assert path.read_text(encoding="utf-8") == "x = 1\nprint(x)\n"


def test_repair_adds_package_marker_for_python_module_dir(tmp_path: Path):
    package = tmp_path / "src"
    package.mkdir()
    (package / "train.py").write_text("print('ok')\n", encoding="utf-8")
    repaired = RepairEngine().repair_missing_python_package_markers(tmp_path)
    assert repaired == ["src/__init__.py"]
    assert (package / "__init__.py").is_file()


def test_repair_does_not_create_marker_in_empty_directory(tmp_path: Path):
    (tmp_path / "assets").mkdir()
    assert RepairEngine().repair_missing_python_package_markers(tmp_path) == []


def test_repair_does_not_hide_python_syntax_errors(tmp_path: Path):
    (tmp_path / "bad.py").write_text("if True print('x')\n", encoding="utf-8")
    errors = RepairEngine().validate_python(tmp_path)
    assert errors
