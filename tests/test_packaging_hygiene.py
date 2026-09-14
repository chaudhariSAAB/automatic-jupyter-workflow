from pathlib import Path
from zipfile import ZipFile

from notebook_workflow.packaging import package_project


def test_package_project_excludes_caches_and_sensitive_files(tmp_path: Path):
    root = tmp_path / "project"
    (root / "src").mkdir(parents=True)
    (root / "__pycache__").mkdir()
    (root / ".git").mkdir()
    (root / "node_modules").mkdir()
    (root / "src" / "main.py").write_text("print('ok')\n", encoding="utf-8")
    (root / "src" / ".env").write_text("TOKEN=secret\n", encoding="utf-8")
    (root / "__pycache__" / "cache.pyc").write_bytes(b"cache")
    (root / ".git" / "config").write_text("secret-ish", encoding="utf-8")
    (root / "node_modules" / "module.js").write_text("bad", encoding="utf-8")

    archive = package_project(root)

    with ZipFile(archive) as zf:
        names = set(zf.namelist())

    assert "src/main.py" in names
    assert "src/.env" not in names
    assert all("__pycache__" not in name for name in names)
    assert all(".git" not in name.split("/") for name in names)
    assert all("node_modules" not in name.split("/") for name in names)
