"""Build a conservative execution plan from a project request."""

from __future__ import annotations

from notebook_workflow.analysis.detector import classify_project_type
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
    ProjectType.UNKNOWN: {"commands": ("python -m pytest",), "preview": None},
}


def build_plan(request: ProjectRequest) -> ProjectPlan:
    """Create a plan without executing anything, using optional reference hints."""
    reference_text = load_reference(request.reference)
    hints = reference_hints(reference_text)
    detection_text = request.prompt + " " + " ".join(hints)
    if request.project_type is ProjectType.UNKNOWN:
        classification = classify_project_type(detection_text)
        detected = classification.project_type
        # A universal factory should not dead-end on an ambiguous request.
        # Coding is the safest dependency-light fallback and remains fully testable.
        kind = detected if detected is not ProjectType.UNKNOWN else ProjectType.CODING
        detection_metadata = {
            "requested_type": ProjectType.UNKNOWN.value,
            "detected_type": detected.value,
            "detection_confidence": classification.confidence,
            "detection_scores": classification.scores,
            "matched_keywords": list(classification.matched_keywords),
            "fallback_used": detected is ProjectType.UNKNOWN,
            "fallback_type": ProjectType.CODING.value if detected is ProjectType.UNKNOWN else None,
        }
    else:
        kind = request.project_type
        detection_metadata = {
            "requested_type": request.project_type.value,
            "detected_type": request.project_type.value,
            "detection_confidence": 1.0,
            "detection_scores": {},
            "matched_keywords": [],
            "fallback_used": False,
            "fallback_type": None,
        }
    defaults = _DEFAULTS[kind]
    metadata = {"reference_hints": hints, "reference_loaded": bool(reference_text), **detection_metadata}
    return ProjectPlan(
        project_type=kind,
        goals=(request.prompt,),
        commands=tuple(defaults["commands"]),
        preview_command=defaults["preview"],
        metadata=metadata,
    )
