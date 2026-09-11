from notebook_workflow.generators.base import ProjectGenerator
from notebook_workflow.generators.registry import GeneratorRegistry
from notebook_workflow.models import ProjectType


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
