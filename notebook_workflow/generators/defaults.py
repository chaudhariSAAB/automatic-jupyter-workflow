"""Built-in generator registry factory."""

from notebook_workflow.generators.concrete import default_concrete_generators
from notebook_workflow.generators.data_science_runner import ExecutableDataScienceGenerator
from notebook_workflow.generators.registry import GeneratorRegistry
from notebook_workflow.generators.web_safe import SafeWebGenerator


def build_default_registry() -> GeneratorRegistry:
    registry = GeneratorRegistry()
    for generator in default_concrete_generators():
        registry.register(generator)
    # Replace the legacy web scaffold with the syntax-safe wrapper.
    registry.register(SafeWebGenerator())
    # Register last so the execution-aware DS generator overrides the basic scaffold.
    registry.register(ExecutableDataScienceGenerator())
    return registry
