"""Built-in generator registry factory."""

from notebook_workflow.generators.concrete import default_concrete_generators
from notebook_workflow.generators.data_science_rich import PromptAwareDataScienceGenerator
from notebook_workflow.generators.registry import GeneratorRegistry


def build_default_registry() -> GeneratorRegistry:
    registry = GeneratorRegistry()
    for generator in default_concrete_generators():
        registry.register(generator)
    # Register last so the prompt-aware DS generator overrides the basic scaffold.
    registry.register(PromptAwareDataScienceGenerator())
    return registry
