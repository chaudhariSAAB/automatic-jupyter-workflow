"""Deterministic project-type detection with transparent confidence scoring."""

from __future__ import annotations

import re
from dataclasses import dataclass

from notebook_workflow.models import ProjectType


@dataclass(frozen=True)
class ProjectClassification:
    project_type: ProjectType
    confidence: float
    scores: dict[str, int]
    matched_keywords: tuple[str, ...] = ()


_PATTERNS: dict[ProjectType, tuple[str, ...]] = {
    ProjectType.JUPYTER: ("jupyter", "notebook", ".ipynb", "jupyterlab"),
    ProjectType.DATA_SCIENCE: ("data science", "pandas", "data analysis", "dataset", "visualization", "matplotlib", "seaborn"),
    ProjectType.MACHINE_LEARNING: ("machine learning", "ml model", "classification", "regression", "scikit-learn", "sklearn", "training model"),
    ProjectType.AI: ("artificial intelligence", " ai ", "llm", "nlp", "computer vision", "neural network", "generative ai"),
    ProjectType.WEB: ("website", "web app", "frontend", "backend", "react", "next.js", "html/css", "api", "dashboard"),
    ProjectType.APP: ("mobile app", "android app", "ios app", "react native", "expo", "flutter", "apk"),
    ProjectType.CODING: ("coding", "python", "javascript", "typescript", "program", "software", "algorithm", "cli", "script"),
}

# Prefer the more specific project classes when scores tie.
_PRIORITY = (
    ProjectType.APP,
    ProjectType.MACHINE_LEARNING,
    ProjectType.AI,
    ProjectType.JUPYTER,
    ProjectType.DATA_SCIENCE,
    ProjectType.WEB,
    ProjectType.CODING,
)


def classify_project_type(prompt: str) -> ProjectClassification:
    """Classify a request without network access or an API key."""
    normalized = re.sub(r"\s+", " ", prompt.lower()).strip()
    text = " " + normalized + " "
    scores: dict[ProjectType, int] = {
        kind: sum(1 for pattern in patterns if pattern in text)
        for kind, patterns in _PATTERNS.items()
    }
    best_score = max(scores.values(), default=0)
    if best_score == 0:
        return ProjectClassification(ProjectType.UNKNOWN, 0.0, {k.value: v for k, v in scores.items()})
    candidates = {kind for kind, score in scores.items() if score == best_score}
    best = next(kind for kind in _PRIORITY if kind in candidates)
    total = sum(scores.values()) or 1
    confidence = min(1.0, 0.5 + (best_score / total) * 0.5)
    matched = tuple(pattern for pattern in _PATTERNS[best] if pattern in text)
    return ProjectClassification(best, round(confidence, 3), {k.value: v for k, v in scores.items()}, matched)


def detect_project_type(prompt: str) -> ProjectType:
    """Backward-compatible classifier returning only the project type."""
    return classify_project_type(prompt).project_type
