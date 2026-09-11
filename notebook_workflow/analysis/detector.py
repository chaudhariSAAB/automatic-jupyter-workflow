"""Deterministic project-type detection with no AI/API dependency."""

from __future__ import annotations

import re

from notebook_workflow.models import ProjectType


_PATTERNS: dict[ProjectType, tuple[str, ...]] = {
    ProjectType.JUPYTER: ("jupyter", "notebook", ".ipynb", "jupyterlab"),
    ProjectType.DATA_SCIENCE: ("data science", "pandas", "data analysis", "dataset", "visualization"),
    ProjectType.MACHINE_LEARNING: ("machine learning", "ml model", "classification", "regression", "scikit-learn"),
    ProjectType.AI: ("artificial intelligence", " ai ", "llm", "nlp", "computer vision", "neural network"),
    ProjectType.WEB: ("website", "web app", "frontend", "backend", "react", "next.js", "html/css", "api"),
    ProjectType.APP: ("mobile app", "android app", "ios app", "react native", "expo", "flutter"),
    ProjectType.CODING: ("coding", "python", "javascript", "typescript", "program", "software", "algorithm"),
}


def detect_project_type(prompt: str) -> ProjectType:
    """Infer the most likely project type using transparent keyword scoring."""
    text = f" {re.sub(r'\\s+', ' ', prompt.lower()).strip()} "
    scores = {kind: sum(1 for pattern in patterns if pattern in text) for kind, patterns in _PATTERNS.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] else ProjectType.UNKNOWN
