import json
from pathlib import Path

from notebook_workflow.sbom import generate_sbom


def test_generate_sbom_is_deterministic_and_hashed(tmp_path: Path):
    (tmp_path / "main.py").write_text("print('ok')\n", encoding="utf-8")
    (tmp_path / "requirements.txt").write_text("pytest>=9,<10\n", encoding="utf-8")
    output = generate_sbom(tmp_path)
    document = json.loads(output.read_text(encoding="utf-8"))
    assert document["spdxVersion"] == "SPDX-2.3"
    assert document["files"]
    assert document["packages"]
    assert document["files"][0]["checksums"][0]["algorithm"] == "SHA256"
