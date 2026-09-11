from pathlib import Path

from notebook_workflow.security import security_scan


def test_security_scan_passes_clean_project(tmp_path: Path):
    (tmp_path / "main.py").write_text("print('hello')\n", encoding="utf-8")
    passed, errors, warnings = security_scan(tmp_path)
    assert passed is True
    assert errors == ()
    assert warnings == ()


def test_security_scan_blocks_hard_coded_secret(tmp_path: Path):
    (tmp_path / "config.py").write_text("API_KEY = 'sk-12345678901234567890'\n", encoding="utf-8")
    passed, errors, _ = security_scan(tmp_path)
    assert passed is False
    assert any("secret" in error.lower() for error in errors)


def test_security_scan_blocks_env_file(tmp_path: Path):
    (tmp_path / ".env").write_text("TOKEN=value\n", encoding="utf-8")
    passed, errors, _ = security_scan(tmp_path)
    assert passed is False
    assert any("sensitive file" in error.lower() for error in errors)
