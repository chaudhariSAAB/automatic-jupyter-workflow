"""Tiny standard-library GitHub Actions dispatcher for phone/Termux use.

Environment:
  GITHUB_TOKEN  fine-grained token with Actions:write
  GITHUB_REPO   owner/repo (defaults to chaudhariSAAB/automatic-jupyter-workflow)

Usage:
  python tools/mobile_dispatch.py "build a pandas sales analysis" --type data_science
"""
from __future__ import annotations

import argparse
import json
import os
import urllib.request

DEFAULT_REPO = "chaudhariSAAB/automatic-jupyter-workflow"


def dispatch(prompt: str, project_type: str, ai_provider: str = "none", max_attempts: str = "2") -> dict:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("GITHUB_TOKEN is required")
    repo = os.environ.get("GITHUB_REPO", DEFAULT_REPO)
    payload = {
        "ref": "main",
        "inputs": {
            "prompt": prompt,
            "project_type": project_type,
            "ai_provider": ai_provider,
            "max_attempts": max_attempts,
            "package": "true",
        },
    }
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/actions/workflows/automation.yml/dispatches",
        data=json.dumps(payload).encode(),
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2026-03-10",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read().decode("utf-8")
        return {"status": response.status, "response": body}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt")
    parser.add_argument("--type", default="unknown", choices=["unknown", "jupyter", "data_science", "machine_learning", "ai", "coding", "web", "app"])
    parser.add_argument("--ai-provider", default="none", choices=["none", "openai", "openrouter", "gemini"])
    parser.add_argument("--max-attempts", default="2")
    args = parser.parse_args()
    print(json.dumps(dispatch(args.prompt, args.type, args.ai_provider, args.max_attempts), indent=2))


if __name__ == "__main__":
    main()
