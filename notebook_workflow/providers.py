"""Optional model providers.

The deterministic workflow never needs an API key. These adapters are opt-in and
read credentials only from environment variables; secrets are never written to
project files or logs by this module.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from abc import ABC, abstractmethod

_MAX_PROVIDER_TEXT = 12_000


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
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read()
    except urllib.error.HTTPError as exc:
        # Never include response bodies because providers can echo sensitive request data.
        raise RuntimeError(f"AI provider HTTP error {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError("AI provider network error") from exc
    try:
        result = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("AI provider returned invalid JSON") from exc
    if not isinstance(result, dict):
        raise RuntimeError("AI provider returned an invalid response object")
    return result


def _bounded_text(value: object, provider: str) -> str:
    text = str(value).strip()
    if not text:
        raise RuntimeError(f"{provider} provider returned no text")
    if len(text) > _MAX_PROVIDER_TEXT:
        raise RuntimeError(f"{provider} provider returned oversized text")
    return text


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
        texts: list[str] = []
        for item in output if isinstance(output, list) else []:
            for content in item.get("content", []) if isinstance(item, dict) else []:
                if isinstance(content, dict) and isinstance(content.get("text"), str):
                    texts.append(content["text"])
        return _bounded_text("".join(texts), self.name)


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
        try:
            content = data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("OpenRouter provider returned an unexpected response") from exc
        return _bounded_text(content, self.name)


class GeminiProvider(AIProvider):
    name = "gemini"

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required for the Gemini provider")

    def generate(self, prompt: str) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        data = _post_json(url, {"x-goog-api-key": self.api_key}, payload)
        try:
            content = data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError("Gemini provider returned an unexpected response") from exc
        return _bounded_text(content, self.name)


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
