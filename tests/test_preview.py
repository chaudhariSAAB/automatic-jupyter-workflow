from pathlib import Path

from notebook_workflow.models import ProjectType
from notebook_workflow.preview import preview_info


def test_web_preview_metadata(tmp_path: Path):
    (tmp_path / "index.html").write_text("<h1>demo</h1>", encoding="utf-8")
    info = preview_info(ProjectType.WEB, tmp_path)
    assert info.command == "python -m http.server 8000"
    assert info.url == "http://127.0.0.1:8000"
    assert info.entrypoint == "index.html"


def test_app_preview_metadata(tmp_path: Path):
    info = preview_info(ProjectType.APP, tmp_path)
    assert info.command == "npx expo start --web"
    assert info.url == "http://localhost:8081"


def test_jupyter_preview_metadata(tmp_path: Path):
    info = preview_info(ProjectType.JUPYTER, tmp_path)
    assert info.command == "jupyter lab"
    assert info.url == "http://localhost:8888"
