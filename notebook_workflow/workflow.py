"""High-level orchestration for analyze -> generate -> validate."""

from __future__ import annotations

from pathlib import Path

from notebook_workflow.analysis.planner import build_plan
from notebook_workflow.execution.runner import CommandRunner
from notebook_workflow.generators.registry import GeneratorRegistry
from notebook_workflow.models import ProjectRequest, ProjectType, ValidationResult, WorkflowResult
from notebook_workflow.validation.files import validate_project_files


class UniversalWorkflow:
    """Coordinate project planning, generation, optional execution, and validation."""

    def __init__(self, registry: GeneratorRegistry | None = None, runner: CommandRunner | None = None) -> None:
        self.registry = registry or GeneratorRegistry()
        self.runner = runner or CommandRunner()

    def run(self, request: ProjectRequest, *, output_dir: Path | str | None = None) -> WorkflowResult:
        plan = build_plan(request)
        target = Path(output_dir or request.output_dir)
        generator = self.registry.resolve(plan.project_type)
        if generator is None:
            validation = ValidationResult(False, errors=(f"No generator registered for {plan.project_type.value}.",))
            return WorkflowResult(False, plan.project_type, target, validation, attempts=0, message="Generator unavailable")

        generator.generate(request, plan, target)
        validation = validate_project_files(target)
        if not validation.passed:
            return WorkflowResult(False, plan.project_type, target, validation, attempts=1, preview_command=plan.preview_command)

        return WorkflowResult(True, plan.project_type, target, validation, attempts=1, preview_command=plan.preview_command, message="Project generated and structurally validated")
