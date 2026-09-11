# Cloud / Mobile Automation

The repository can run the universal workflow on GitHub Actions, so the user's PC does not need to stay on.

## Run from a phone

1. Open the repository on GitHub.
2. Open **Actions**.
3. Select **Universal Project Automation**.
4. Select **Run workflow**.
5. Enter the project prompt.
6. Optionally choose the project type and repair attempts.
7. Start the workflow.
8. When it finishes, download the `generated-project` artifact.

The core workflow does not require an AI API key. AI-provider keys are optional and should be added only as repository secrets when an AI-backed generator is explicitly enabled.

## Current scope

- Jupyter, data science, machine learning, AI, coding, web, and app project generation.
- Validation and bounded repair attempts.
- Generated-project artifact upload.

This workflow is for generation/testing and artifact delivery. It does not deploy applications automatically.
