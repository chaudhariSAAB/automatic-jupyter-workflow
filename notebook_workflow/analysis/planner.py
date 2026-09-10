"""Build a conservative execution plan from a project request."""

from __future__ import annotations

from notebook_workflow.analysis.detector import detect_project_type
from notebook_workflow.models import ProjectPlan, ProjectRequest, ProjectType


_DEFAULTS: dict[ProjectType, dict[str, object]] = {
    ProjectType.JUPYTER: {"commands": ("jupyter nbconvert --execute",), "preview": "jupyter lab"},
    ProjectType.DATA_SCIENCE: {"commands": ("python -m pytest",), "preview": None},
    ProjectType.MACHINE_LEARNING: {"commands": ("python -m pytest",), "preview": None},
    ProjectType.AI: {"commands": ("python -m pytest",), "preview": None},
    ProjectType.CODING: {"commands": ("python -m pytest",), "preview": None},
    ProjectType.WEB: {"commands": ("npm test",), "preview": "npm run dev"},
    ProjectType.APP: {"commands": ("npx expo test",), "preview": "npx expo start"},
    ProjectType.UNKNOWN: {"commands": (), "preview": None},
}


def build_plan(request: ProjectRequest) -> ProjectPlan:
    """Create a plan without executing anything."""
    kind = request.project_type if request.project_type is not ProjectType.UNKNOWN else detect_project_type(request.prompt)
    defaults = _DEFAULTS[kind]
    return ProjectPlan(
        project_type=kind,
        goals=(request.prompt,),
        commands=tuple(defaults["commands"]),
        preview_command=defaults["preview"],
    )
