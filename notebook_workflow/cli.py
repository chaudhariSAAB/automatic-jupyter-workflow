"""Command-line entry point for universal project automation."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from notebook_workflow.analysis.planner import build_plan
from notebook_workflow.factory import FactoryConfig, ProjectFactory
from notebook_workflow.models import ProjectRequest, ProjectType
from notebook_workflow.packaging import package_project
from notebook_workflow.workflow import UniversalWorkflow


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate, security-scan, execute, validate, and package a project from a prompt.")
    parser.add_argument("prompt", nargs="?", help="Project requirement or task description")
    parser.add_argument("--type", choices=[item.value for item in ProjectType if item is not ProjectType.UNKNOWN])
    parser.add_argument("--reference")
    parser.add_argument("--output", default="generated_projects")
    parser.add_argument("--max-attempts", type=int, default=2, choices=range(1, 6))
    parser.add_argument("--dry-run", action="store_true", help="Only analyze and show the plan")
    parser.add_argument("--package", action="store_true", help="Create a sanitized ZIP after a successful run")
    parser.add_argument("--factory", action="store_true", help="Use the bounded autonomous project factory")
    parser.add_argument("--report", help="Write the JSON result report to this path")
    parser.add_argument("--ai-provider", choices=["none", "openai", "openrouter", "gemini"], default=None, help="Optional AI metadata provider")
    return parser


def _print_or_write(payload: dict, report: str | None) -> None:
    text = json.dumps(payload, indent=2)
    print(text)
    if report:
        path = Path(report)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    prompt = args.prompt or input("Project requirement: ").strip()
    kind = ProjectType(args.type) if args.type else ProjectType.UNKNOWN

    if args.dry_run:
        request = ProjectRequest(prompt=prompt, reference=args.reference, project_type=kind, output_dir=Path(args.output))
        plan = build_plan(request)
        payload = {"dry_run": True, "project_type": plan.project_type.value, "goals": list(plan.goals), "commands": list(plan.commands), "preview_command": plan.preview_command, "metadata": plan.metadata}
        _print_or_write(payload, args.report)
        return 0

    provider_name = args.ai_provider or "none"
    if args.factory:
        result = ProjectFactory(FactoryConfig(max_attempts=args.max_attempts, ai_provider=provider_name)).run(
            prompt,
            project_type=kind,
            output_dir=Path(args.output),
        )
    else:
        if args.ai_provider is not None:
            os.environ["NOTEBOOK_WORKFLOW_AI_PROVIDER"] = args.ai_provider
        request = ProjectRequest(prompt=prompt, reference=args.reference, project_type=kind, output_dir=Path(args.output))
        result = UniversalWorkflow().run(request, max_attempts=args.max_attempts)

    payload = {
        "success": result.success,
        "project_type": result.project_type.value,
        "output_dir": str(result.output_dir),
        "attempts": result.attempts,
        "message": result.message,
        "errors": list(result.validation.errors),
        "warnings": list(result.validation.warnings),
        "checks": list(result.validation.checks),
        "preview_command": result.preview_command,
    }
    if args.package and result.success:
        archive = package_project(result.output_dir)
        payload["package"] = str(archive)
    _print_or_write(payload, args.report)
    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
