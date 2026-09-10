# Automatic Jupyter Workflow → Universal Project Automation

This repository is being expanded from the original Jupyter notebook workflow into a universal project automation system.

## Current workflow

`Requirement/reference → project-type detection → plan → generation → security scan → syntax/structure validation → safe execution checks → bounded retry → result`

The core workflow is **local-first and API-key-free**. Optional AI providers can be layered on later; they are not required for the deterministic foundation.

## Supported project types

- Jupyter notebooks (`.ipynb` generation + notebook structure validation)
- Data Science (CSV analysis starter)
- Machine Learning (dependency-light training/prediction starter)
- AI (dependency-free intent classification starter)
- General Coding
- Web (HTML/CSS/JS preview-ready starter)
- App (Expo/React Native starter)

## Security-first behavior

- Generated files are scanned for common hard-coded API keys, tokens, passwords, and secrets.
- Sensitive files such as `.env` and private-key filenames are blocked from generated projects.
- Python files are parsed with `ast` and notebooks are checked as JSON with Jupyter v4 structure.
- Planned commands are tokenized with `shlex`, executed without a shell, and restricted to an explicit executable allowlist.
- Execution retries are bounded to prevent infinite loops.
- Generated projects are not automatically deployed.

## CLI

Generate a project from a requirement:

```bash
python -m notebook_workflow.cli "build a data science project for concrete strength analysis" --type data_science --output generated_projects/concrete --max-attempts 2
```

The CLI prints a JSON result containing success status, detected type, validation checks, security warnings/errors, attempts, and an optional preview command.

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

The Phase 1 branch now contains the universal core, concrete generators, security scanning, syntax/structure validation, safe command execution, CLI controls, tests, and GitHub Actions CI.

Further work will add richer reference-aware Jupyter/DS/ML generation, real dependency-aware web/app adapters, automatic repair based on captured failures, live preview orchestration, ZIP packaging, optional LLM provider adapters, and cloud/mobile execution paths.
