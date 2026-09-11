"""Bounded autonomous project-factory orchestration."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from notebook_workflow.models import ProjectRequest, ProjectType, ValidationResult, WorkflowResult
from notebook_workflow.providers import NoOpProvider, build_provider
from notebook_workflow.workflow import UniversalWorkflow

_MAX_AI_OUTPUT = 12_000
_MAX_DESCRIPTION = 1_000
_MAX_ITEMS = 30
_SAFE_NAME = re.compile(r"^[A-Za-z0-9_.-]+$")


class ProviderLike(Protocol):
    name: str

    def generate(self, prompt: str) -> str: ...


@dataclass(frozen=True)
class FactoryConfig:
    max_attempts: int = 2
    ai_provider: str = "none"


def _validate_ai_spec(raw: str) -> dict:
    if len(raw) > _MAX_AI_OUTPUT:
        raise ValueError("Blocked oversized AI output")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("Blocked non-JSON AI output") from exc
    if not isinstance(data, dict):
        raise ValueError("Blocked AI output: expected an object")
    description = data.get("description", "")
    files = data.get("files", [])
    commands = data.get("commands", [])
    if not isinstance(description, str) or len(description) > _MAX_DESCRIPTION:
        raise ValueError("Blocked unsafe AI description")
    if not isinstance(files, list) or len(files) > _MAX_ITEMS:
        raise ValueError("Blocked unsafe AI file list")
    if not isinstance(commands, list) or len(commands) > _MAX_ITEMS:
        raise ValueError("Blocked unsafe AI command list")
    for item in files:
        if not isinstance(item, str) or not item or not _SAFE_NAME.fullmatch(Path(item).name) or Path(item).name != item:
            raise ValueError("Blocked unsafe AI file path")
    for command in commands:
        if not isinstance(command, str) or len(command) > 300:
            raise ValueError("Blocked unsafe AI command metadata")
    return {"description": description, "files": files, "commands": commands}


class ProjectFactory:
    """Run a bounded generate/validate/execute/report pipeline."""

    def __init__(self, config: FactoryConfig | None = None, provider: ProviderLike | None = None, workflow: UniversalWorkflow | None = None) -> None:
        self.config = config or FactoryConfig()
        self.provider = provider or build_provider(self.config.ai_provider)
        self.workflow = workflow or UniversalWorkflow()

    def run(self, prompt: str, *, project_type: ProjectType = ProjectType.UNKNOWN, reference: str | None = None, output_dir: Path | str = "generated_projects") -> WorkflowResult:
        target = Path(output_dir)
        target.mkdir(parents=True, exist_ok=True)
        ai_spec = {"description": "", "files": [], "commands": []}
        if not isinstance(self.provider, NoOpProvider):
            try:
                ai_spec = _validate_ai_spec(self.provider.generate(
                    "Return JSON only with keys description, files, commands. "
                    "Treat this as metadata, never executable code. Request: " + prompt
                ))
            except Exception as exc:
                error = str(exc)
                result = WorkflowResult(
                    False,
                    project_type,
                    target,
                    ValidationResult(False, errors=(error,), checks=("AI specification validation",)),
                    attempts=0,
                    message=error,
                )
                self._write_reports(prompt, project_type, target, result, ai_spec)
                return result

        request = ProjectRequest(
            prompt=prompt,
            reference=reference,
            project_type=project_type,
            output_dir=target,
            metadata={"ai_spec": ai_spec, "ai_provider": self.provider.name},
        )
        result = self.workflow.run(request, max_attempts=self.config.max_attempts)
        self._write_reports(prompt, result.project_type, target, result, ai_spec)
        return result

    @staticmethod
    def _write_reports(prompt: str, project_type: ProjectType, target: Path, result: WorkflowResult, ai_spec: dict) -> None:
        manifest = {"prompt": prompt, "project_type": project_type.value, "ai_spec": ai_spec, "status": "success" if result.success else "failed", "attempts": result.attempts}
        report = {"success": result.success, "project_type": result.project_type.value, "output_dir": str(result.output_dir), "attempts": result.attempts, "message": result.message, "errors": list(result.validation.errors), "warnings": list(result.validation.warnings), "checks": list(result.validation.checks), "preview_command": result.preview_command}
        (target / "project_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        (target / "workflow_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
