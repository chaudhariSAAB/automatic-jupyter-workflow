from pathlib import Path

from notebook_workflow.models import ProjectRequest, ProjectType
from notebook_workflow.workflow import UniversalWorkflow


class FakeGenerator:
    project_type = ProjectType.CODING

    def generate(self, request, plan, output_dir):
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "main.py").write_text("print('generated')\n", encoding="utf-8")
        return ("main.py",)


def test_workflow_generates_and_validates(tmp_path: Path):
    workflow = UniversalWorkflow()
    workflow.registry.register(FakeGenerator())
    result = workflow.run(ProjectRequest(prompt="create coding project"), output_dir=tmp_path)
    assert result.success is True
    assert result.project_type is ProjectType.CODING
    assert (tmp_path / "main.py").exists()


def test_workflow_fails_cleanly_without_generator(tmp_path: Path):
    result = UniversalWorkflow().run(ProjectRequest(prompt="create an AI project"), output_dir=tmp_path)
    assert result.success is False
    assert result.validation.errors
