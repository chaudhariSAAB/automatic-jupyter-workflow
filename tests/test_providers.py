import pytest

from notebook_workflow import providers


def test_noop_provider_is_default(monkeypatch):
    monkeypatch.delenv("NOTEBOOK_WORKFLOW_AI_PROVIDER", raising=False)
    provider = providers.build_provider()
    assert provider.name == "none"


def test_provider_names_are_case_insensitive(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    assert providers.build_provider("OPENROUTER").name == "openrouter"
    assert providers.build_provider("OpenAI").name == "openai"
    assert providers.build_provider("gemini").name == "gemini"


def test_provider_requires_credentials(monkeypatch):
    for variable, factory in (
        ("OPENROUTER_API_KEY", providers.OpenRouterProvider),
        ("OPENAI_API_KEY", providers.OpenAIProvider),
        ("GEMINI_API_KEY", providers.GeminiProvider),
    ):
        monkeypatch.delenv(variable, raising=False)
        with pytest.raises(ValueError, match=variable):
            factory()


def test_unknown_provider_fails_fast():
    with pytest.raises(ValueError, match="Unknown AI provider"):
        providers.build_provider("unknown")


def test_openrouter_response_is_extracted(monkeypatch):
    monkeypatch.setattr(
        providers,
        "_post_json",
        lambda *args, **kwargs: {"choices": [{"message": {"content": "generated"}}]},
    )
    provider = providers.OpenRouterProvider(api_key="test-key")
    assert provider.generate("hello") == "generated"
