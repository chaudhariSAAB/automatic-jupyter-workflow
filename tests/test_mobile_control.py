from pathlib import Path

ROOT = Path(__file__).parents[1]
MOBILE = ROOT / "tools" / "mobile_dispatch.py"


def test_mobile_tool_exposes_dispatch_status_and_artifacts():
    text = MOBILE.read_text(encoding="utf-8")
    assert "def dispatch(" in text
    assert "def workflow_status(" in text
    assert "def workflow_artifacts(" in text
    assert "actions/runs" in text
    assert "actions/artifacts" in text
    assert "workflow_dispatch" in text


def test_mobile_tool_does_not_print_or_persist_token():
    text = MOBILE.read_text(encoding="utf-8")
    assert "print(token)" not in text
    assert "write_text(token" not in text
    assert "GITHUB_TOKEN" in text


def test_mobile_cli_supports_status_and_artifacts_commands():
    text = MOBILE.read_text(encoding="utf-8")
    assert "status" in text
    assert "artifacts" in text
    assert "--run-id" in text
