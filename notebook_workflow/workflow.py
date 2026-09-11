"""High-level orchestration for analyze -> generate -> execute -> validate."""

from __future__ import annotations

import shlex
from pathlib import Path

from notebook_workflow.analysis.planner import build_plan
from notebook_workflow.execution.runner import CommandRunner
from notebook_workflow.generators.defaults import build_default_registry
from notebook_workflow.generators.registry import GeneratorRegistry
from notebook_workflow.models import ProjectRequest, ValidationResult, WorkflowResult
from notebook_workflow.repair import RepairEngine
from notebook_workflow.security import security_scan
from notebook_workflow.validation.files import validate_project_files

_ALLOWED_COMMANDS = {
    ("python", "-m", "pytest"),
    ("python3", "-m", "pytest"),
    ("pytest",),
    ("jupyter", "lab"),
    ("jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace"),
    ("python", "-m", "http.server"),
    ("python3", "-m", "http.server"),
}


def _safe_command(command: str) -> tuple[str, ...]:
    tokens = tuple(shlex.split(command))
    if not tokens:
        raise ValueError("Blocked empty command")
    notebook_prefix = ("jupyter", "nbconvert", "--to", "notebook", "--execute", "--inplace")
    if tokens[:6] == notebook_prefix:
        if len(tokens) != 7 or not tokens[6].endswith(".ipynb") or "/" in tokens[6] or "\\" in tokens[6]:
            raise ValueError("Blocked invalid notebook execution target")
        return tokens
    prefix = tokens[:3] if len(tokens) >= 3 else tokens
    if prefix in _ALLOWED_COMMANDS:
        if prefix[-1] == "http.server":
            if len(tokens) != 4 or not tokens[3].isdigit() or not 1 <= int(tokens[3]) <= 65535:
                raise ValueError("Blocked invalid HTTP preview port")
        elif len(tokens) != len(prefix):
            raise ValueError("Blocked unexpected command arguments")
        return tokens
    if tokens == ("pytest",):
        return tokens
    raise ValueError(f"Blocked command: {command}")


class UniversalWorkflow:
    """Coordinate planning, generation, safe execution, repair, and validation."""

    def __init__(self, registry: GeneratorRegistry | None = None, runner: CommandRunner | None = None, repairer: RepairEngine | None = None) -> None:
        self.registry = registry or build_default_registry()
        self.runner = runner or CommandRunner()
        self.repairer = repairer or RepairEngine()

    def _safe_command(self, command: str) -> tuple[str, ...]:
        return _safe_command(command)

    def _validate(self, target: Path) -> ValidationResult:
        structural = validate_project_files(target)
        secure, security_errors, security_warnings = security_scan(target)
        return ValidationResult(
            structural.passed and secure,
            errors=structural.errors + security_errors,
            warnings=structural.warnings + security_warnings,
            checks=structural.checks + ("security scan",),
        )

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
        validation = self._validate(target)
        if not validation.passed:
            return WorkflowResult(False, plan.project_type, target, validation, attempts=1, preview_command=plan.preview_command, message="Project failed pre-execution validation")

        last_errors: tuple[str, ...] = ()
        repair_notes: list[str] = []
        for attempt in range(1, max_attempts + 1):
            if attempt > 1:
                repaired = self.repairer.repair_python_trailing_whitespace(target)
                if repaired:
                    repair_notes.extend(repaired)
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
                post_validation = self._validate(target)
                if post_validation.passed:
                    warnings = post_validation.warnings + tuple(f"deterministic repair: {item}" for item in repair_notes)
                    final = ValidationResult(True, warnings=warnings, checks=post_validation.checks + ("planned commands", "post-execution validation"))
                    return WorkflowResult(True, plan.project_type, target, final, attempts=attempt, preview_command=plan.preview_command, message="Project generated, security-scanned, executed, repaired if needed, and validated")
                errors.extend(post_validation.errors)
            last_errors = tuple(errors)

        final = ValidationResult(False, errors=last_errors, warnings=validation.warnings + tuple(f"deterministic repair: {item}" for item in repair_notes), checks=validation.checks + ("planned commands", "post-execution validation"))
        return WorkflowResult(False, plan.project_type, target, final, attempts=max_attempts, preview_command=plan.preview_command, message="Execution checks failed after bounded retries")
