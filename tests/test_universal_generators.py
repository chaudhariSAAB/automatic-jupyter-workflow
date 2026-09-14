from pathlib import Path

import pytest

from notebook_workflow.generators.defaults import build_default_registry
from notebook_workflow.models import ProjectPlan, ProjectRequest, ProjectType
from notebook_workflow.security import security_scan
from notebook_workflow.validation.files import validate_project_files


@pytest.mark.parametrize("project_type", list(ProjectType))
def test_every_project_type_has_a_safe_generator(tmp_path: Path, project_type: ProjectType):
    if project_type is ProjectType.UNKNOWN:
        pytest.skip("unknown is resolved by planning, not generated directly")

    output = tmp_path / project_type.value
    request = ProjectRequest(
        prompt=f"Build a {project_type.value} starter project",
        project_type=project_type,
        output_dir=output,
    )
    generator = build_default_registry().resolve(project_type)
    assert generator is not None
    plan = ProjectPlan(project_type=project_type)
    generator.generate(request, plan, output)

    structural = validate_project_files(output)
    secure, errors, _ = security_scan(output)
    assert structural.passed, structural.errors
    assert secure, errors
    assert (output / "project.json").is_file()
    assert (output / "tests" / "test_smoke.py").is_file()
