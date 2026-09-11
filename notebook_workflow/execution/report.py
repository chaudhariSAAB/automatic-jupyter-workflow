"""Serializable execution reporting for universal automation runs."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class CommandReport:
    command: str
    returncode: int | None
    stdout: str
    stderr: str
    timed_out: bool = False


def write_report(path: Path | str, *, success: bool, project_type: str, output_dir: Path | str, attempts: int, commands: list[CommandReport], errors: tuple[str, ...] = (), warnings: tuple[str, ...] = ()) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "success": success,
        "project_type": project_type,
        "output_dir": str(output_dir),
        "attempts": attempts,
        "commands": [asdict(item) for item in commands],
        "errors": list(errors),
        "warnings": list(warnings),
    }
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return target
