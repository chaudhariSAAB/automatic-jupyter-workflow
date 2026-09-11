import json

from notebook_workflow.generators.ai import AIGenerator as LegacyAIGenerator
from notebook_workflow.generators.base import ProjectGenerator
from notebook_workflow.generators.concrete import AIGenerator
from notebook_workflow.generators.registry import GeneratorRegistry
from notebook_workflow.models import ProjectPlan, ProjectRequest, ProjectType


class DummyGenerator(ProjectGenerator):
    project_type = ProjectType.CODING

    def generate(self, request, plan, output_dir):
        return ()


def test_registry_registers_and_resolves_generator():
    registry = GeneratorRegistry()
    generator = DummyGenerator()
    registry.register(generator)
    assert registry.resolve(ProjectType.CODING) is generator


def test_registry_reports_missing_generator():
    registry = GeneratorRegistry()
    assert registry.resolve(ProjectType.AI) is None


def test_concrete_ai_generator_accepts_provider_metadata(tmp_path):
    class FakeProvider:
        name = "fake"

        def generate(self, prompt: str) -> str:
            assert "Return ONLY JSON" in prompt
            return json.dumps({"description": "A study assistant", "features": ["flashcards", "search"]})

    request = ProjectRequest(prompt="Build a study assistant", project_type=ProjectType.AI, output_dir=tmp_path)
    plan = ProjectPlan(project_type=ProjectType.AI, goals=("generate",), commands=("python -m pytest",), preview_command=None, metadata={})
    AIGenerator(provider=FakeProvider()).generate(request, plan, tmp_path)
    manifest = json.loads((tmp_path / "project.json").read_text(encoding="utf-8"))
    assert manifest["ai_assisted"] is True
    assert manifest["ai_metadata"]["features"] == ["flashcards", "search"]


def test_concrete_ai_generator_does_not_require_provider(tmp_path):
    request = ProjectRequest(prompt="Build an AI starter", project_type=ProjectType.AI, output_dir=tmp_path)
    plan = ProjectPlan(project_type=ProjectType.AI, goals=("generate",), commands=("python -m pytest",), preview_command=None, metadata={})
    # Legacy deterministic generator is still importable; the concrete generator is API-key-free by default.
    LegacyAIGenerator().generate(request, plan, tmp_path)
    assert (tmp_path / "src" / "ai.py").is_file()
