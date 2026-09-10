# Automatic Jupyter Workflow → Universal Project Automation

This repository is expanding the original Jupyter workflow into a universal, security-first project automation system.

## Pipeline

`Requirement/reference → detection → planning → generation → security scan → validation → safe execution → bounded repair/retry → report → optional ZIP package`

The deterministic core is **local-first and API-key-free**. Optional AI providers can be layered on later.

## Supported project types

- Jupyter notebooks (`.ipynb`)
- Data Science
- Machine Learning
- AI
- General Coding
- Web (HTML/CSS/JS)
- App (Expo/React Native starter)

## Reference input

The planner can safely ingest `.txt`, `.md`, `.json`, `.csv`, and `.ipynb` references. Reference files are size-limited, parsed safely, and converted into deterministic planning hints. Unsupported, missing, oversized, malformed, or symlink references fail explicitly rather than being guessed.

## Security

- Scans generated text for common API keys, tokens, passwords, secrets, private keys, and GitHub tokens.
- Blocks sensitive filenames such as `.env` and common private-key files.
- Rejects symlinks in generated projects.
- Validates Python syntax with `ast` and notebook structure as JSON/Jupyter v4.
- Tokenizes commands with `shlex`, never uses `shell=True`, and restricts execution to an explicit executable allowlist.
- Retries are bounded to prevent infinite repair loops.
- Generated projects are never automatically deployed.

## CLI

Generate and validate:

```bash
python -m notebook_workflow.cli "build a data science project for concrete strength analysis" --type data_science --output generated_projects/concrete
```

Preview the plan without generation/execution:

```bash
python -m notebook_workflow.cli "build a web dashboard" --dry-run
```

Write a JSON report and create a sanitized ZIP after success:

```bash
python -m notebook_workflow.cli "build a coding project" --package --report generated_projects/report.json
```

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

## CI

GitHub Actions runs the pytest suite from `.github/workflows/tests.yml`. The connector session cannot claim local test execution, so CI results must be treated as the verification source when available.

## Development roadmap

The foundation now includes universal models, deterministic detection/planning, concrete generators, reference ingestion, security scanning, validation, safe execution, bounded repair, CLI controls, packaging, tests, and CI. Next layers are richer task-specific generation, dependency-aware web/app adapters, live preview orchestration, optional LLM adapters, and cloud/mobile execution.
