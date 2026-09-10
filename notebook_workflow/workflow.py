"""High-level orchestration for analyze -> generate -> execute -> validate."""

from __future__ import annotations

import shlex
from pathlib import Path

from notebook_workflow.analysis.planner import build_plan
from notebook_workflow.execution.runner import CommandRunner
from notebook_workflow.generators.defaults import build_default_registry
from notebook_workflow.generators.registry import GeneratorRegistry
from notebook_workflow.models import ProjectRequest, ValidationResult, WorkflowResult
from notebook_workflow.security import security_scan
from notebook_workflow.validation.files import validate_project_files

_ALLOWED_EXECUTABLES = {"python", "python3", "pytest", "jupyter", "node", "npm", "npx", "expo"}


class UniversalWorkflow:
    """Coordinate planning, generation, safe execution, and validation."""

    def __init__(self, registry: GeneratorRegistry | None = None, runner: CommandRunner | None = None) -> None:
        self.registry = registry or build_default_registry()
        self.runner = runner or CommandRunner()

    def _safe_command(self, command: str) -> tuple[str, ...]:
        tokens = tuple(shlex.split(command))
        if not tokens or tokens[0] not in _ALLOWED_EXECUTABLES:
            raise ValueError(f"Blocked executable: {tokens[0] if tokens else '<empty>'}")
        return tokens

    def run(self, request: ProjectRequest, *, output_dir: Path | str | None = None, max_attempts: int = 2) -> WorkflowResult:
        if max_attempts < 1 or max_attempts > 5:
            raise ValueError("max_attempts must be between 1 and 5")
        plan = build_plan(request)
        target = Path(output_dir or request.output_dir)
        generator = self.registry.resolve(plan.project_type)
        if generator is None:
            validation = ValidationResult(False, errors=(f"No generator registered for {plan.project_type.value}.",))
            return WorkflowResult(False, plan.project_type, target, validation, attempts=0, message="Generator unavailable")

        generator.generate(request, plan, target)
        validation = validate_project_files(target)
        secure, security_errors, security_warnings = security_scan(target)
        validation = ValidationResult(
            validation.passed and secure,
            errors=validation.errors + security_errors,
            warnings=validation.warnings + security_warnings,
            checks=validation.checks + ("security scan",),
        )
        if not validation.passed:
            return WorkflowResult(False, plan.project_type, target, validation, attempts=1, preview_command=plan.preview_command, message="Project failed pre-execution validation")

        last_errors: tuple[str, ...] = ()
        for attempt in range(1, max_attempts + 1):
            errors: list[str] = []
            for command in plan.commands:
                try:
                    tokens = self._safe_command(command)
                except ValueError as exc:
                    errors.append(str(exc))
                    continue
                result = self.runner.run(tokens, cwd=target)
                if result.failed:
                    detail = result.stderr.strip() or result.stdout.strip() or f"exit code {result.returncode}"
                    errors.append(f"{command}: {detail}")
            if not errors:
                final = ValidationResult(True, warnings=validation.warnings, checks=validation.checks + ("planned commands",))
                return WorkflowResult(True, plan.project_type, target, final, attempts=attempt, preview_command=plan.preview_command, message="Project generated, security-scanned, executed, and validated")
            last_errors = tuple(errors)

        final = ValidationResult(False, errors=last_errors, warnings=validation.warnings, checks=validation.checks + ("planned commands",))
        return WorkflowResult(False, plan.project_type, target, final, attempts=max_attempts, preview_command=plan.preview_command, message="Execution checks failed after bounded retries")
