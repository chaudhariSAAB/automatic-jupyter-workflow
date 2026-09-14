# Automatic Jupyter Workflow → Universal Project Automation Factory v1.0

This repository has evolved from an automatic Jupyter workflow into a universal, security-first project automation factory.

## Pipeline

`Requirement/reference → detection → planning → generation → dependency setup → security scan → validation → safe execution → bounded repair/retry → tests → report → sanitized ZIP → checksum → artifact attestation`

The deterministic core is **local-first and API-key-free**. Optional AI providers can be layered on later.

## Supported project types

| Type | E2E | Output |
|---|---|---|
| Jupyter | ✅ | Executable `.ipynb` |
| Data Science | ✅ | Analysis, metrics, visualizations, report |
| Machine Learning | ✅ | Training/evaluation pipeline, cross-validation, report |
| AI | ✅ | Local-first AI classification + evaluation |
| General Coding | ✅ | Python project, CLI, tests, README |
| Web | ✅ | HTML/CSS/JS project |
| App | ✅ | Expo/React Native starter |

All seven supported project types have passed end-to-end workflow testing.

## Security boundary

- Scans generated text for common API keys, tokens, passwords, secrets, private keys, and GitHub tokens.
- Blocks sensitive filenames such as `.env` and common private-key files.
- Rejects symlinks in generated projects.
- Validates Python syntax with `ast` and notebook structure as JSON/Jupyter v4.
- Tokenizes commands with `shlex`, never uses `shell=True`, and restricts execution to an explicit executable allowlist.
- Retries are bounded to prevent infinite repair loops.
- Generated projects are never automatically deployed.
- Generated ZIPs exclude repository metadata, virtual environments, caches, Node modules, and known secret filenames.
- Final ZIPs receive a SHA-256 checksum and, when packaging is enabled in GitHub Actions, a signed artifact attestation.

GitHub artifact attestations provide provenance and integrity information linking an artifact to its repository, workflow, commit, and triggering event. citeturn1search0turn1search2

## Reference input

The planner safely ingests `.txt`, `.md`, `.json`, `.csv`, and `.ipynb` references. Reference files are size-limited, parsed safely, and converted into deterministic planning hints. Unsupported, missing, oversized, malformed, or symlink references fail explicitly rather than being guessed.

## CLI

```bash
python -m notebook_workflow.cli "build a data science project for concrete strength analysis" --type data_science --output generated_projects/concrete
```

Preview without generation/execution:

```bash
python -m notebook_workflow.cli "build a web dashboard" --dry-run
```

Create a sanitized ZIP and JSON report:

```bash
python -m notebook_workflow.cli "build a coding project" --package --report generated_projects/report.json
```

## CI / E2E

- `.github/workflows/tests.yml` runs the pytest regression suite across Python 3.10–3.13.
- `.github/workflows/automation.yml` provides the manual Universal Project Automation workflow.
- The automation workflow performs preflight tests, generation, dependency installation, execution, standalone generated tests, notebook execution, final security scanning, ZIP hygiene validation, checksum creation, and artifact upload.
- Packaged outputs can receive GitHub artifact attestations for provenance/integrity verification. citeturn1search1turn1search2

## v1.0 readiness

The v1.0 foundation is complete: universal models, deterministic detection/planning, concrete generators, reference ingestion, security scanning, structural validation, safe execution, bounded repair, CLI controls, packaging, regression tests, CI, seven successful E2E project types, sanitized artifacts, checksums, and artifact provenance support.

Future expansion areas are richer task-specific generation, dependency-aware adapters, live preview orchestration, optional LLM adapters, and cloud/mobile execution.
