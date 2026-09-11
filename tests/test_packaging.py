from pathlib import Path
from zipfile import ZipFile

from notebook_workflow.packaging import package_project


def test_package_project_excludes_sensitive_and_cache_files(tmp_path: Path):
    root = tmp_path / "project"
    root.mkdir()
    (root / "main.py").write_text("print('ok')\n", encoding="utf-8")
    (root / ".env").write_text("SECRET=x\n", encoding="utf-8")
    (root / ".pytest_cache").mkdir()
    (root / ".pytest_cache" / "x").write_text("cache", encoding="utf-8")
    archive = package_project(root)
    with ZipFile(archive) as zf:
        names = set(zf.namelist())
    assert "main.py" in names
    assert ".env" not in names
    assert all(".pytest_cache" not in name for name in names)
