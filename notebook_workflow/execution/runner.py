"""Subprocess runner with timeout and captured output."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class CommandResult:
    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False

    @property
    def failed(self) -> bool:
        return self.timed_out or self.returncode != 0


class CommandRunner:
    """Run an already-tokenized command without invoking a shell."""

    def run(
        self,
        command: Sequence[str],
        *,
        cwd: Path | str | None = None,
        timeout: float = 120.0,
    ) -> CommandResult:
        tokens = tuple(str(part) for part in command)
        if not tokens:
            raise ValueError("command must not be empty")
        try:
            completed = subprocess.run(
                tokens,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
            return CommandResult(tokens, completed.returncode, completed.stdout, completed.stderr)
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout or ""
            stderr = exc.stderr or ""
            if isinstance(stdout, bytes):
                stdout = stdout.decode(errors="replace")
            if isinstance(stderr, bytes):
                stderr = stderr.decode(errors="replace")
            return CommandResult(tokens, -1, stdout, stderr, timed_out=True)
