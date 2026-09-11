import json
from pathlib import Path

from notebook_workflow.factory import FactoryConfig, ProjectFactory
from notebook_workflow.models import ProjectType


def test_factory_writes_manifest_and_report(tmp_path: Path):
    result = ProjectFactory(FactoryConfig(max_attempts=1)).run(
        "make a simple Python coding project",
        project_type=ProjectType.CODING,
        output_dir=tmp_path / "project",
    )
    assert result.success
    manifest = json.loads((tmp_path / "project" / "project_manifest.json").read_text())
    assert manifest["project_type"] == "coding"
    assert manifest["status"] == "success"
    assert (tmp_path / "project" / "workflow_report.json").is_file()


def test_factory_rejects_unsafe_provider_output(tmp_path: Path):
    class BadProvider:
        name = "test"

        def generate(self, prompt: str) -> str:
            return '{"description":"x","files":["../../secret"],"commands":["rm -rf /"]}'

    result = ProjectFactory(FactoryConfig(max_attempts=1), provider=BadProvider()).run(
        "make a project",
        project_type=ProjectType.CODING,
        output_dir=tmp_path / "project",
    )
    assert not result.success
    assert any("unsafe" in error.lower() or "blocked" in error.lower() for error in result.validation.errors)
