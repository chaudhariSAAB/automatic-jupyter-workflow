"""Command-line entry point for universal project automation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from notebook_workflow.models import ProjectRequest, ProjectType
from notebook_workflow.workflow import UniversalWorkflow


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate and validate a project from a prompt.")
    parser.add_argument("prompt", nargs="?", help="Project requirement or task description")
    parser.add_argument("--type", choices=[item.value for item in ProjectType if item is not ProjectType.UNKNOWN])
    parser.add_argument("--reference")
    parser.add_argument("--output", default="generated_projects")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    prompt = args.prompt or input("Project requirement: ").strip()
    kind = ProjectType(args.type) if args.type else ProjectType.UNKNOWN
    request = ProjectRequest(prompt=prompt, reference=args.reference, project_type=kind, output_dir=Path(args.output))
    result = UniversalWorkflow().run(request)
    print(json.dumps({
        "success": result.success,
        "project_type": result.project_type.value,
        "output_dir": str(result.output_dir),
        "attempts": result.attempts,
        "message": result.message,
        "errors": list(result.validation.errors),
        "warnings": list(result.validation.warnings),
        "checks": list(result.validation.checks),
        "preview_command": result.preview_command,
    }, indent=2))
    return 0 if result.success else 1


if __name__ == "__main__":
    raise SystemExit(main())
