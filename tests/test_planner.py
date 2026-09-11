from notebook_workflow.analysis.planner import build_plan
from notebook_workflow.models import ProjectRequest, ProjectType


def test_planner_uses_explicit_type():
    plan = build_plan(ProjectRequest(prompt="build it", project_type=ProjectType.WEB))
    assert plan.project_type is ProjectType.WEB
    assert plan.preview_command == "python -m http.server 8000"


def test_planner_detects_type_when_unknown():
    plan = build_plan(ProjectRequest(prompt="Analyze a dataset with pandas"))
    assert plan.project_type is ProjectType.DATA_SCIENCE
