"""Build a conservative execution plan from a project request."""

from __future__ import annotations

from notebook_workflow.analysis.detector import detect_project_type
from notebook_workflow.models import ProjectPlan, ProjectRequest, ProjectType
from notebook_workflow.references import load_reference, reference_hints

_DEFAULTS: dict[ProjectType, dict[str, object]] = {
    ProjectType.JUPYTER: {"commands": ("python -m pytest",), "preview": "jupyter lab"},
    ProjectType.DATA_SCIENCE: {"commands": ("python -m pytest",), "preview": None},
    ProjectType.MACHINE_LEARNING: {"commands": ("python -m pytest",), "preview": None},
    ProjectType.AI: {"commands": ("python -m pytest",), "preview": None},
    ProjectType.CODING: {"commands": ("python -m pytest",), "preview": None},
    ProjectType.WEB: {"commands": ("python -m pytest",), "preview": "python -m http.server 8000"},
    ProjectType.APP: {"commands": ("python -m pytest",), "preview": None},
    ProjectType.UNKNOWN: {"commands": (), "preview": None},
}


def build_plan(request: ProjectRequest) -> ProjectPlan:
    """Create a plan without executing anything, using optional reference hints."""
    reference_text = load_reference(request.reference)
    hints = reference_hints(reference_text)
    kind = request.project_type if request.project_type is not ProjectType.UNKNOWN else detect_project_type(request.prompt + " " + " ".join(hints))
    defaults = _DEFAULTS[kind]
    metadata = {"reference_hints": hints, "reference_loaded": bool(reference_text)}
    return ProjectPlan(
        project_type=kind,
        goals=(request.prompt,),
        commands=tuple(defaults["commands"]),
        preview_command=defaults["preview"],
        metadata=metadata,
    )
