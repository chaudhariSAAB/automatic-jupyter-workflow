from pathlib import Path

from notebook_workflow.repair import RepairEngine


def test_repair_python_trailing_whitespace_is_bounded_and_deterministic(tmp_path: Path):
    root = tmp_path / "project"
    root.mkdir()
    source = root / "main.py"
    source.write_text("value = 1   \nprint(value)\t\n", encoding="utf-8")

    repaired = RepairEngine().repair_python_trailing_whitespace(root)

    assert repaired == ["main.py"]
    assert source.read_text(encoding="utf-8") == "value = 1\nprint(value)\n"
    assert RepairEngine().validate_python(root) == []
    assert RepairEngine().repair_python_trailing_whitespace(root) == []
