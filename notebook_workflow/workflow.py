"""High-level orchestration for analyze -> generate -> execute -> validate."""

from __future__ import annotations

import shlex
from pathlib import Path

from notebook_workflow.analysis.planner import build_plan
from notebook_workflow.execution.runner import CommandRunner
from notebook_workflow.generators.defaults import build_default_registry
from notebook_workflow.generators.registry import GeneratorRegistry
from notebook_workflow.models import ProjectRequest, ValidationResult, WorkflowResult
from notebook_workflow.validation.files import validate_project_files


class UniversalWorkflow:
    """Coordinate planning, generation, checks, and structural validation."""

    def __init__(self, registry: GeneratorRegistry | None = None, runner: CommandRunner | None = None) -> None:
        self.registry = registry or build_default_registry()
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

        errors: list[str] = []
        for command in plan.commands:
            result = self.runner.run(shlex.split(command), cwd=target)
            if result.failed:
                detail = result.stderr.strip() or result.stdout.strip() or f"exit code {result.returncode}"
                errors.append(f"{command}: {detail}")

        if errors:
            validation = ValidationResult(False, errors=tuple(errors), warnings=validation.warnings, checks=validation.checks + ("planned commands",))
            return WorkflowResult(False, plan.project_type, target, validation, attempts=1, preview_command=plan.preview_command, message="Project generated but execution checks failed")

        validation = ValidationResult(True, warnings=validation.warnings, checks=validation.checks + (("planned commands",) if plan.commands else ()))
        return WorkflowResult(True, plan.project_type, target, validation, attempts=1, preview_command=plan.preview_command, message="Project generated, checked, and structurally validated")
