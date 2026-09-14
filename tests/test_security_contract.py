from pathlib import Path
import re

ROOT = Path(__file__).parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
SHA_USE = re.compile(r"^\s*-?\s*uses:\s+([^@\s]+)@([^\s#]+)", re.MULTILINE)


def test_all_workflow_actions_are_pinned_to_full_sha():
    offenders = []
    for path in WORKFLOWS.glob("*.y*ml"):
        text = path.read_text(encoding="utf-8")
        for match in SHA_USE.finditer(text):
            if not re.fullmatch(r"[0-9a-f]{40}", match.group(2)):
                offenders.append(f"{path}:{match.group(1)}@{match.group(2)}")
    assert not offenders, offenders


def test_workflows_do_not_use_persistent_checkout_credentials():
    offenders = []
    for path in WORKFLOWS.glob("*.y*ml"):
        text = path.read_text(encoding="utf-8")
        if "persist-credentials: true" in text:
            offenders.append(str(path))
    assert not offenders, offenders
