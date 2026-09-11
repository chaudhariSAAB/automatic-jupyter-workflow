"""Registry for project generators."""

from __future__ import annotations

from notebook_workflow.generators.base import ProjectGenerator
from notebook_workflow.models import ProjectType


class GeneratorRegistry:
    """Maps project types to generators without coupling the orchestrator to them."""

    def __init__(self) -> None:
        self._generators: dict[ProjectType, ProjectGenerator] = {}

    def register(self, generator: ProjectGenerator) -> None:
        if not isinstance(generator.project_type, ProjectType):
            raise TypeError("generator.project_type must be a ProjectType")
        self._generators[generator.project_type] = generator

    def resolve(self, project_type: ProjectType) -> ProjectGenerator | None:
        return self._generators.get(project_type)

    def all(self) -> tuple[ProjectGenerator, ...]:
        return tuple(self._generators.values())
