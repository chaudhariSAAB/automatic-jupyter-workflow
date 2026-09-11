from notebook_workflow.analysis.detector import detect_project_type
from notebook_workflow.models import ProjectType


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
