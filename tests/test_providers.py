from notebook_workflow.providers import build_provider


def test_noop_provider_is_default():
    provider = build_provider("none")
    assert provider.name == "none"


def test_provider_names_are_case_insensitive():
    assert build_provider("OPENROUTER").name == "openrouter"
    assert build_provider("OpenAI").name == "openai"
    assert build_provider("gemini").name == "gemini"


def test_unknown_provider_fails_fast():
    try:
        build_provider("unknown")
    except ValueError as exc:
        assert "Unknown AI provider" in str(exc)
    else:
        raise AssertionError("unknown provider should fail")
