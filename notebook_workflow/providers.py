"""Optional model providers.

The deterministic workflow never needs an API key. These adapters are opt-in and
read credentials only from environment variables; secrets are never written to
project files or logs by this module.
"""
from __future__ import annotations

import json
import os
import urllib.request
from abc import ABC, abstractmethod


class AIProvider(ABC):
    name: str

    @abstractmethod
    def generate(self, prompt: str) -> str:
        raise NotImplementedError


class NoOpProvider(AIProvider):
    name = "none"

    def generate(self, prompt: str) -> str:
        raise RuntimeError("No AI provider configured; use deterministic generation or configure an optional provider.")


def _post_json(url: str, headers: dict[str, str], payload: dict, timeout: float = 60.0) -> dict:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=data, headers={**headers, "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


class OpenAIProvider(AIProvider):
    name = "openai"

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-5-mini")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required for the OpenAI provider")

    def generate(self, prompt: str) -> str:
        payload = {"model": self.model, "input": prompt}
        data = _post_json("https://api.openai.com/v1/responses", {"Authorization": f"Bearer {self.api_key}"}, payload)
        output = data.get("output", [])
        texts = [item.get("text", "") for item in output if isinstance(item, dict) for item in item.get("content", []) if isinstance(item, dict)]
        text = "".join(texts).strip()
        if not text:
            raise RuntimeError("OpenAI provider returned no text")
        return text


class OpenRouterProvider(AIProvider):
    name = "openrouter"

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model or os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is required for the OpenRouter provider")

    def generate(self, prompt: str) -> str:
        payload = {"model": self.model, "messages": [{"role": "user", "content": prompt}]}
        data = _post_json("https://openrouter.ai/api/v1/chat/completions", {"Authorization": f"Bearer {self.api_key}"}, payload)
        return str(data["choices"][0]["message"]["content"])


class GeminiProvider(AIProvider):
    name = "gemini"

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required for the Gemini provider")

    def generate(self, prompt: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        data = _post_json(url, {}, payload)
        return str(data["candidates"][0]["content"]["parts"][0]["text"])


def build_provider(name: str | None = None) -> AIProvider:
    selected = (name or os.getenv("NOTEBOOK_WORKFLOW_AI_PROVIDER", "none")).strip().lower()
    if selected in {"", "none", "noop"}:
        return NoOpProvider()
    if selected == "openai":
        return OpenAIProvider()
    if selected == "openrouter":
        return OpenRouterProvider()
    if selected in {"gemini", "google"}:
        return GeminiProvider()
    raise ValueError(f"Unknown AI provider: {name}")
