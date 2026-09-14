# Automatic Jupyter Workflow → Universal Project Automation Factory v1.2

This repository has evolved from an automatic Jupyter workflow into a universal, security-first project automation factory.

## Pipeline

`Requirement/reference → detection → confidence → planning → generation → dependency setup → security scan → validation → safe execution → bounded repair/retry → tests → provenance/SBOM → sanitized ZIP → checksum → artifact attestation`

The deterministic core is **local-first and API-key-free**. Optional AI providers are isolated and metadata-only.

## Supported project types

| Type | E2E | Output |
|---|---:|---|
| Jupyter | ✅ | Executable `.ipynb` |
| Data Science | ✅ | Analysis, metrics, visualizations, report |
| Machine Learning | ✅ | Training/evaluation pipeline |
| AI | ✅ | Local-first AI classification + evaluation |
| General Coding | ✅ | Python project, CLI, tests, README |
| Web | ✅ | HTML/CSS/JS project |
| App | ✅ | Expo/React Native starter |

## Universal detection

When `project_type` is `unknown`, the factory scores the request and reference hints, records confidence and matched keywords, and falls back to a safe dependency-light Coding generator when the request is genuinely ambiguous.

## Security boundary

- Detects common API keys, tokens, passwords, secrets, private keys, and GitHub tokens.
- Blocks sensitive filenames such as `.env` and common private-key files.
- Rejects symlinks in generated projects.
- Validates Python syntax and notebook structure.
- Tokenizes commands with `shlex`; no `shell=True`.
- Uses an explicit command allowlist.
- Bounded retries prevent infinite repair loops.
- Deterministic repair can normalize Python whitespace, add missing package markers, and apply a tiny allowlist of failure-aware fixes.
- Generated projects are never automatically deployed.
- Generated ZIPs exclude repository metadata, virtual environments, caches, Node modules, and known secret filenames.

## Provenance and SBOM

Every packaged factory run now generates a deterministic `sbom.spdx.json` inventory with SHA-256 file hashes. The GitHub workflow stages the SBOM with the final artifact and can create an attestation for both the ZIP and SBOM. GitHub documents artifact attestations as cryptographically signed provenance/integrity claims and supports SBOM-associated attestations. citeturn2search0turn2search1

## Optional AI providers

AI providers are metadata-only. Provider output is size-limited and schema-validated before it can influence the workflow. Provider HTTP errors do not expose response bodies. Gemini API keys are sent through a request header instead of a URL.

## CI / E2E

- `.github/workflows/tests.yml` — regression suite.
- `.github/workflows/automation.yml` — universal manual/reusable factory.
- `.github/workflows/universal-regression.yml` — seven project types in parallel.
- `.github/workflows/universal-stress.yml` — 3 rounds × 7 project types with bounded retries and `fail-fast: false`.

The universal factory uses a reusable workflow entry point through `workflow_call`, which GitHub supports specifically for reusable automation and matrix callers. citeturn0search0turn0search1

## Mobile control

GitHub supports triggering `workflow_dispatch` through the Actions UI, CLI, or REST API. The repository now includes `tools/mobile_dispatch.py`, a standard-library client intended for trusted mobile terminals such as Termux. It reads `GITHUB_TOKEN` from the environment and sends only workflow inputs; it never writes the token into generated projects. citeturn1search0turn1search2

## Current hardening status

The v1.2 pass adds:

- confidence-aware detection
- safe ambiguity fallback
- machine-readable provenance
- failure-aware deterministic repair
- hardened optional providers
- parallel seven-project regression
- repeated universal stress matrix
- deterministic SPDX-style SBOM
- SBOM + artifact attestation hooks
- reusable workflow support
- mobile dispatch helper

See `docs/UNIVERSAL_FACTORY_ROADMAP.md` and `docs/MOBILE_CONTROL.md` for the architecture and operating model.
