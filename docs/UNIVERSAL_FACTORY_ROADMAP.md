# Universal Project Automation Factory — v1.1

The factory now has a deterministic, API-key-free core plus optional AI metadata providers.

## Completed in this hardening pass

- Automatic project-type classification now exposes confidence, scores, and matched keywords.
- Ambiguous `unknown` requests use a safe `coding` fallback instead of dead-ending.
- Factory reports now include schema version and detection/provenance metadata.
- Deterministic repair can add missing Python package markers before a bounded retry.
- Optional AI providers now bound response size, normalize provider failures, and avoid placing Gemini keys in URLs.
- A seven-way GitHub Actions regression matrix runs Jupyter, Data Science, ML, AI, Coding, Web, and App in parallel.
- The regression matrix uses immutable action SHAs and safe Python module execution.

## Next expansion targets

1. Add dependency-aware adapters for Python, Node/Expo, and notebook environments.
2. Add richer repair strategies keyed to observed test failures while keeping an explicit allowlist.
3. Add deterministic artifact manifests with file hashes and generated-project metadata.
4. Add optional SBOM generation for generated projects.
5. Add a reusable `workflow_call` entry point for other repositories.
6. Add a small mobile-friendly control layer that only dispatches GitHub Actions and never stores project secrets.
7. Add long-running stress tests for repeated generation and bounded retries.

## Security rule

AI output remains metadata-only. It is never executed as shell commands and never writes secrets. Generated projects are scanned before packaging, and packaged artifacts are sanitized.
