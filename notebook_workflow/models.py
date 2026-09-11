"""Core data models for universal project automation."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class ProjectType(str, Enum):
    JUPYTER = "jupyter"
    DATA_SCIENCE = "data_science"
    MACHINE_LEARNING = "machine_learning"
    AI = "ai"
    CODING = "coding"
    WEB = "web"
    APP = "app"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ProjectRequest:
    """Normalized user request used by the orchestrator."""

    prompt: str
    reference: str | None = None
    project_type: ProjectType = ProjectType.UNKNOWN
    output_dir: Path = Path("generated_projects")
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProjectPlan:
    """Execution plan produced after project analysis."""

    project_type: ProjectType
    goals: tuple[str, ...] = ()
    files: tuple[str, ...] = ()
    commands: tuple[str, ...] = ()
    tests: tuple[str, ...] = ()
    preview_command: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ValidationResult:
    """Result of a generated project's validation pass."""

    passed: bool
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    checks: tuple[str, ...] = ()


@dataclass(frozen=True)
class WorkflowResult:
    """Final result returned by the universal workflow."""

    success: bool
    project_type: ProjectType
    output_dir: Path
    validation: ValidationResult
    attempts: int = 1
    preview_command: str | None = None
    message: str = ""
