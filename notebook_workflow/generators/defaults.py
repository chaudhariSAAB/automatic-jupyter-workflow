"""Built-in generator registry factory."""

from notebook_workflow.generators.registry import GeneratorRegistry
from notebook_workflow.generators.templates import default_registry_generators


def build_default_registry() -> GeneratorRegistry:
    registry = GeneratorRegistry()
    for generator in default_registry_generators():
        registry.register(generator)
    return registry
