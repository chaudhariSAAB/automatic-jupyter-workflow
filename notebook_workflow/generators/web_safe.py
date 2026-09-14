"""Safety wrapper for the built-in web generator."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from notebook_workflow.generators.concrete import WebGenerator
from notebook_workflow.models import ProjectPlan, ProjectRequest


class SafeWebGenerator(WebGenerator):
    """Wrap the web scaffold and normalize its generated Python smoke test."""

    def generate(
        self,
        request: ProjectRequest,
        plan: ProjectPlan,
        output_dir: Path,
    ) -> Iterable[str]:
        written = list(super().generate(request, plan, output_dir))
        test_path = output_dir / "tests" / "test_web_files.py"
        test_path.write_text(
            "from pathlib import Path\n\n"
            "\n"
            "def test_web_project_is_complete():\n"
            "    root = Path(__file__).parents[1]\n"
            "    for name in ('index.html', 'style.css', 'app.js'):\n"
            "        assert (root / name).is_file()\n"
            "    html = (root / 'index.html').read_text(encoding='utf-8')\n"
            "    assert \"<meta name='viewport'\" in html\n"
            "    assert 'style.css' in html and 'app.js' in html\n",
            encoding="utf-8",
        )
        if "tests/test_web_files.py" not in written:
            written.append("tests/test_web_files.py")
        return written
