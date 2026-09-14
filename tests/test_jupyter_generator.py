from pathlib import Path

from notebook_workflow.generators.defaults import build_default_registry
from notebook_workflow.models import ProjectPlan, ProjectRequest, ProjectType


def test_jupyter_generator_declares_runtime_dependency(tmp_path: Path):
    output = tmp_path / "jupyter"
    request = ProjectRequest(
        prompt="Build a student marks analysis notebook",
        project_type=ProjectType.JUPYTER,
        output_dir=output,
    )
    generator = build_default_registry().resolve(ProjectType.JUPYTER)
    assert generator is not None
    generator.generate(request, ProjectPlan(ProjectType.JUPYTER), output)

    assert (output / "notebooks" / "notebook.ipynb").is_file()
    assert (output / "requirements.txt").read_text(encoding="utf-8") == "jupyter>=1,<2\n"
