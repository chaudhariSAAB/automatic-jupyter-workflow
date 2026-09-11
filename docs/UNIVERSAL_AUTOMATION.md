# Universal Project Automation

This project turns a natural-language requirement into a generated, validated and testable project.

## Supported project types

- Jupyter / notebook workflows
- Data Science
- Machine Learning
- AI
- General Python coding
- Web projects
- App projects

## Pipeline

`Requirement/reference -> type detection -> plan -> generate -> security scan -> structural validation -> tests -> bounded repair -> package -> preview metadata`

## Preview

Web projects use a local Python HTTP server on port 8000. Jupyter projects use JupyterLab on port 8888. App projects expose the Expo web preview command (`npx expo start --web`) and expected local URL (`http://localhost:8081`). Preview metadata does not claim that a remote deployment exists.

## Cloud / phone workflow

GitHub Actions can run the core generation workflow from a phone or browser. The repository workflow accepts a prompt, project type, repair-attempt limit and packaging option, then uploads the generated project as an Actions artifact.

The core engine does not require an AI API key. Optional AI providers can be added later for richer generated content.

## Security

Generated commands are allowlisted; arbitrary shell commands are not executed. Secrets, private-key files, environment files and symlinks are rejected by the security scanner.
