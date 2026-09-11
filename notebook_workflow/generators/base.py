"""Base interface implemented by all project generators."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable

from notebook_workflow.models import ProjectPlan, ProjectRequest, ProjectType


class ProjectGenerator(ABC):
    """Small, dependency-light contract for a project generator."""

    project_type: ProjectType

    @abstractmethod
    def generate(
        self,
        request: ProjectRequest,
        plan: ProjectPlan,
        output_dir: Path,
    ) -> Iterable[str]:
        """Generate project files and return their relative paths."""
        raise NotImplementedError
