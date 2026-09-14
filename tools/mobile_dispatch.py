"""Small standard-library GitHub Actions client for phone/Termux use.

Environment:
  GITHUB_TOKEN  fine-grained token with Actions:write/read
  GITHUB_REPO   owner/repo (defaults to chaudhariSAAB/automatic-jupyter-workflow)

Examples:
  python tools/mobile_dispatch.py "build a pandas sales analysis" --type data_science
  python tools/mobile_dispatch.py status --run-id 123456789
  python tools/mobile_dispatch.py artifacts --run-id 123456789
"""
from __future__ import annotations

import argparse
import json
import os
import urllib.parse
import urllib.request

DEFAULT_REPO = "chaudhariSAAB/automatic-jupyter-workflow"
API = "https://api.github.com"
HEADERS_BASE = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2026-03-10",
    "Content-Type": "application/json",
}


def _request(path: str, *, token: str, method: str = "GET", payload: dict | None = None) -> dict:
    data = json.dumps(payload).encode() if payload is not None else None
    headers = dict(HEADERS_BASE)
    headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(f"{API}{path}", data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read().decode("utf-8")
        return json.loads(body) if body else {"status": response.status}


def _credentials() -> tuple[str, str]:
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise SystemExit("GITHUB_TOKEN is required")
    return token, os.environ.get("GITHUB_REPO", DEFAULT_REPO)


def dispatch(prompt: str, project_type: str, ai_provider: str = "none", max_attempts: str = "2") -> dict:
    token, repo = _credentials()
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
    return _request(f"/repos/{repo}/actions/workflows/automation.yml/dispatches", token=token, method="POST", payload=payload)


def workflow_status(run_id: int | None = None, limit: int = 5) -> dict:
    token, repo = _credentials()
    if run_id is not None:
        run = _request(f"/repos/{repo}/actions/runs/{run_id}", token=token)
        jobs = _request(f"/repos/{repo}/actions/runs/{run_id}/jobs?per_page=100", token=token)
        return {"run": run, "jobs": jobs.get("jobs", [])}
    query = urllib.parse.urlencode({"branch": "main", "per_page": max(1, min(limit, 20))})
    return _request(f"/repos/{repo}/actions/runs?{query}", token=token)


def workflow_artifacts(run_id: int) -> dict:
    token, repo = _credentials()
    return _request(f"/repos/{repo}/actions/runs/{run_id}/artifacts?per_page=100", token=token)


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command")

    run_parser = sub.add_parser("run")
    run_parser.add_argument("prompt")
    run_parser.add_argument("--type", default="unknown", choices=["unknown", "jupyter", "data_science", "machine_learning", "ai", "coding", "web", "app"])
    run_parser.add_argument("--ai-provider", default="none", choices=["none", "openai", "openrouter", "gemini"])
    run_parser.add_argument("--max-attempts", default="2")

    status_parser = sub.add_parser("status")
    status_parser.add_argument("--run-id", type=int)
    status_parser.add_argument("--limit", type=int, default=5)

    artifact_parser = sub.add_parser("artifacts")
    artifact_parser.add_argument("--run-id", type=int, required=True)

    parser.add_argument("prompt", nargs="?")
    parser.add_argument("--type", default="unknown", choices=["unknown", "jupyter", "data_science", "machine_learning", "ai", "coding", "web", "app"])
    parser.add_argument("--ai-provider", default="none", choices=["none", "openai", "openrouter", "gemini"])
    parser.add_argument("--max-attempts", default="2")
    args = parser.parse_args()

    if args.command == "status":
        print(json.dumps(workflow_status(args.run_id, args.limit), indent=2))
    elif args.command == "artifacts":
        print(json.dumps(workflow_artifacts(args.run_id), indent=2))
    elif args.command == "run":
        print(json.dumps(dispatch(args.prompt, args.type, args.ai_provider, args.max_attempts), indent=2))
    elif args.prompt:
        print(json.dumps(dispatch(args.prompt, args.type, args.ai_provider, args.max_attempts), indent=2))
    else:
        parser.error("provide a prompt, status, or artifacts command")


if __name__ == "__main__":
    main()
