"""Jupyter generator wrapper that declares runtime dependencies explicitly."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from notebook_workflow.generators.concrete import JupyterGenerator
from notebook_workflow.models import ProjectPlan, ProjectRequest


class SafeJupyterGenerator(JupyterGenerator):
    """Generate the standard notebook plus its required Jupyter dependency."""

    def generate(self, request: ProjectRequest, plan: ProjectPlan, output_dir: Path) -> Iterable[str]:
        written = list(super().generate(request, plan, output_dir))
        requirements = output_dir / "requirements.txt"
        requirements.write_text("jupyter>=1,<2\n", encoding="utf-8")
        written.append("requirements.txt")
        return written
