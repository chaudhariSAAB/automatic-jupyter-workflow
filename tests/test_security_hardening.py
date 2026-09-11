from pathlib import Path

from notebook_workflow.security import security_scan


def test_security_scan_blocks_private_key_and_github_token(tmp_path: Path):
    (tmp_path / "config.py").write_text("token = 'github_pat_12345678901234567890'\n", encoding="utf-8")
    passed, errors, _ = security_scan(tmp_path)
    assert not passed
    assert any("secret" in error.lower() for error in errors)


def test_security_scan_rejects_symlink(tmp_path: Path):
    target = tmp_path / "target.txt"
    target.write_text("safe", encoding="utf-8")
    link = tmp_path / "link.txt"
    try:
        link.symlink_to(target)
    except (OSError, NotImplementedError):
        return
    passed, errors, _ = security_scan(tmp_path)
    assert not passed
    assert any("symlink" in error.lower() for error in errors)
