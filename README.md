# Automatic Jupyter Workflow → Universal Project Automation Factory v1.1

This repository has evolved from an automatic Jupyter workflow into a universal, security-first project automation factory.

## Pipeline

`Requirement/reference → detection → confidence → planning → generation → dependency setup → security scan → validation → safe execution → bounded repair/retry → tests → report → sanitized ZIP → checksum → artifact attestation`

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

All seven supported project types have passed end-to-end workflow testing. A parallel regression matrix is also available under `.github/workflows/universal-regression.yml`.

## Universal detection

When `project_type` is `unknown`, the factory deterministically scores the request and reference hints, records confidence and matched keywords, and falls back to a safe dependency-light Coding generator when the request is genuinely ambiguous. This prevents a universal request from failing simply because classification is uncertain.

## Security boundary

- Scans generated text for common API keys, tokens, passwords, secrets, private keys, and GitHub tokens.
- Blocks sensitive filenames such as `.env` and common private-key files.
- Rejects symlinks in generated projects.
- Validates Python syntax with `ast` and notebook structure as JSON/Jupyter v4.
- Tokenizes commands with `shlex`, never uses `shell=True`, and restricts execution to an explicit executable allowlist.
- Retries are bounded to prevent infinite repair loops.
- Deterministic repair can normalize Python whitespace and add missing `__init__.py` markers only where Python modules already exist.
- Generated projects are never automatically deployed.
- Generated ZIPs exclude repository metadata, virtual environments, caches, Node modules, and known secret filenames.
- Final ZIPs receive a SHA-256 checksum and, when packaging is enabled in GitHub Actions, a signed artifact attestation.

## Optional AI providers

AI providers are **metadata-only** in the factory. Provider output is size-limited and schema-validated before it can influence the workflow. Provider HTTP errors are normalized without logging response bodies. Gemini API keys are sent through a request header instead of a URL.

## CLI

```bash
python -m notebook_workflow.cli "build a data science project for concrete strength analysis" --type data_science --output generated_projects/concrete
```

Automatic type detection:

```bash
python -m notebook_workflow.cli "build a mobile app for tracking engineering attendance" --factory
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

- `.github/workflows/tests.yml` runs the pytest regression suite across Python versions.
- `.github/workflows/automation.yml` provides the manual Universal Project Automation workflow.
- `.github/workflows/universal-regression.yml` runs the seven supported project types in parallel with `fail-fast: false`.
- The automation workflow performs preflight tests, generation, dependency installation, execution, standalone generated tests, notebook execution, final security scanning, ZIP hygiene validation, checksum creation, and artifact upload.
- Packaged outputs can receive GitHub artifact attestations for provenance/integrity verification.

## Mobile control

GitHub's Actions UI and workflow-dispatch API allow the same factory to be started remotely without the user's PC running. The recommended mobile-control architecture is a thin authenticated dispatcher that submits a workflow request and reads run status/artifacts; project secrets stay in GitHub Actions secrets and are never placed in the generated project.

## v1.1 hardening status

The v1.1 hardening pass adds confidence-aware automatic detection, safe ambiguity fallback, richer machine-readable provenance, deterministic package-marker repair, hardened optional providers, and a parallel seven-project regression matrix.

See `docs/UNIVERSAL_FACTORY_ROADMAP.md` for the remaining expansion plan.
