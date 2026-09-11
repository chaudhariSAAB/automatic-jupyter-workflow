import json
from pathlib import Path

from notebook_workflow.generators.concrete import default_concrete_generators
from notebook_workflow.models import ProjectPlan, ProjectRequest, ProjectType


def test_all_concrete_generators_emit_expected_files(tmp_path: Path):
    request = ProjectRequest(prompt="build a useful project")
    for generator in default_concrete_generators():
        plan = ProjectPlan(project_type=generator.project_type)
        target = tmp_path / generator.project_type.value
        written = set(generator.generate(request, plan, target))
        assert "README.md" in written
        assert (target / "project.json").exists()
        assert (target / "tests/test_smoke.py").exists()


def test_jupyter_generator_emits_valid_notebook(tmp_path: Path):
    generator = next(g for g in default_concrete_generators() if g.project_type is ProjectType.JUPYTER)
    target = tmp_path / "notebook"
    generator.generate(ProjectRequest(prompt="civil engineering lab"), ProjectPlan(ProjectType.JUPYTER), target)
    notebook = json.loads((target / "notebook.ipynb").read_text(encoding="utf-8"))
    assert notebook["nbformat"] == 4
    assert any(cell["cell_type"] == "code" for cell in notebook["cells"])
