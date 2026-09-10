"""Built-in generator registry factory."""

from notebook_workflow.generators.concrete import default_concrete_generators
from notebook_workflow.generators.registry import GeneratorRegistry


def build_default_registry() -> GeneratorRegistry:
    registry = GeneratorRegistry()
    for generator in default_concrete_generators():
        registry.register(generator)
    return registry
