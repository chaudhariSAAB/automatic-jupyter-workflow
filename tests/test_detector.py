from notebook_workflow.analysis.detector import classify_project_type, detect_project_type
from notebook_workflow.analysis.planner import build_plan
from notebook_workflow.models import ProjectRequest, ProjectType


def test_detect_jupyter_notebook():
    assert detect_project_type("Create a Jupyter notebook for Task 5 Matplotlib") is ProjectType.JUPYTER


def test_detect_machine_learning():
    assert detect_project_type("Build a machine learning classification model") is ProjectType.MACHINE_LEARNING


def test_detect_web_app():
    assert detect_project_type("Build a React web app with a backend API") is ProjectType.WEB


def test_detect_mobile_app():
    assert detect_project_type("Create a React Native Expo mobile app") is ProjectType.APP


def test_unknown_request():
    assert detect_project_type("make something useful") is ProjectType.UNKNOWN


def test_classifier_exposes_confidence_and_matches():
    result = classify_project_type("Build a pandas data analysis with matplotlib")
    assert result.project_type is ProjectType.DATA_SCIENCE
    assert result.confidence > 0.5
    assert "pandas" in result.matched_keywords


def test_planner_uses_coding_fallback_for_ambiguous_request():
    plan = build_plan(ProjectRequest(prompt="make something useful"))
    assert plan.project_type is ProjectType.CODING
    assert plan.metadata["fallback_used"] is True
    assert plan.metadata["fallback_type"] == "coding"
