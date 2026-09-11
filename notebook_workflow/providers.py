"""Optional AI provider boundary.

The universal core never needs an API key. Providers can implement this small
interface later (OpenAI, OpenRouter, Gemini, local Ollama, etc.).
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class AIProvider(ABC):
    """Minimal interface for optional model-assisted generation/repair."""

    name: str

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Return generated text for a prompt."""
        raise NotImplementedError


class NoOpProvider(AIProvider):
    """Explicit provider used when no API key/model is configured."""

    name = "none"

    def generate(self, prompt: str) -> str:
        raise RuntimeError("No AI provider configured; use deterministic generation or configure an optional provider.")
