# Automatic Jupyter Workflow → Universal Project Automation

This repository is being expanded from the original Jupyter notebook workflow into a universal project automation system.

## Current workflow

`Requirement/reference → project-type detection → plan → generation → validation → execution checks → result`

The core workflow is **local-first and API-key-free**. Optional AI providers will be added later; they are not required for the deterministic foundation.

## Supported project types

- Jupyter
- Data Science
- Machine Learning
- AI
- General Coding
- Web
- App

## CLI

Generate a starter project from a requirement:

```bash
python -m notebook_workflow.cli "build a data science project for concrete strength analysis" --type data_science --output generated_projects/concrete
```

The CLI prints a JSON result containing success status, detected type, validation checks, errors/warnings, attempts, and an optional preview command.

## Programmatic usage

```python
from pathlib import Path
from notebook_workflow.models import ProjectRequest
from notebook_workflow.workflow import UniversalWorkflow

result = UniversalWorkflow().run(
    ProjectRequest(
        prompt="Build a machine learning project for concrete strength prediction",
        output_dir=Path("generated_projects/concrete_ml"),
    )
)
print(result.success)
```

## Development status

Phase 1 establishes the shared models, deterministic detector/planner, generator registry, dependency-light starter generators, command runner, structural validation, universal orchestrator, CLI, tests, and GitHub Actions test workflow.

Next phases add richer Jupyter/DS/ML/AI generators, real web/app project adapters, bounded auto-repair, previews, packaging, and optional AI-provider integrations while preserving the no-key core path.
