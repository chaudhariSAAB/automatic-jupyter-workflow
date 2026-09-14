"""Deterministic, dependency-file SBOM generation for generated projects."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def generate_sbom(root: Path, output: Path | None = None) -> Path:
    """Create an SPDX 2.3-compatible lightweight inventory of generated files.

    This is intentionally dependency-file based and deterministic: it does not
    execute package managers or arbitrary project code.
    """
    root = Path(root)
    output = output or root / "sbom.spdx.json"
    files = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or output.resolve() == path.resolve():
            continue
        if any(part in {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache"} for part in path.parts):
            continue
        rel = path.relative_to(root).as_posix()
        files.append({
            "SPDXID": "SPDXRef-File-" + hashlib.sha1(rel.encode()).hexdigest()[:16],
            "fileName": rel,
            "checksums": [{"algorithm": "SHA256", "checksumValue": _sha256(path)}],
        })

    packages = []
    for name in ("requirements.txt", "pyproject.toml", "package.json", "package-lock.json"):
        path = root / name
        if path.is_file():
            packages.append({
                "SPDXID": "SPDXRef-Package-" + name.replace(".", "-").replace("/", "-"),
                "name": name,
                "downloadLocation": "NOASSERTION",
                "filesAnalyzed": False,
                "versionInfo": "NOASSERTION",
            })

    document = {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": root.name + " SBOM",
        "documentNamespace": "https://example.invalid/spdx/" + hashlib.sha256(str(root.resolve()).encode()).hexdigest(),
        "creationInfo": {"creators": ["Tool: Universal Project Automation Factory"]},
        "packages": packages,
        "files": files,
    }
    output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    return output
