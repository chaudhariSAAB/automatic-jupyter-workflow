"""Prompt-aware, dependency-free data science generator for concrete strength analysis."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable

from notebook_workflow.generators.base import ProjectGenerator
from notebook_workflow.generators.concrete import DataScienceGenerator as BasicDataScienceGenerator
from notebook_workflow.models import ProjectPlan, ProjectRequest, ProjectType


CSV_HEADER = [
    "cement", "slag", "fly_ash", "water", "superplasticizer",
    "coarse_aggregate", "fine_aggregate", "age_days", "strength_mpa",
]


def _dataset() -> str:
    rows = []
    for i in range(1, 41):
        cement = 220 + (i % 10) * 18
        slag = (i % 7) * 12
        fly_ash = (i % 5) * 10
        water = 160 + (i % 6) * 5
        superplasticizer = round(2 + (i % 4) * 0.7, 2)
        coarse = 900 + (i % 8) * 18
        fine = 650 + (i % 9) * 15
        age = [3, 7, 14, 28, 56][i % 5]
        strength = (
            0.055 * cement + 0.018 * slag + 0.012 * fly_ash
            - 0.11 * water + 1.1 * superplasticizer + 0.12 * age
            + 0.006 * (fine - 650) - 0.002 * (coarse - 900) + 18
        )
        rows.append([cement, slag, fly_ash, water, superplasticizer, coarse, fine, age, round(strength, 2)])
    lines = [",".join(CSV_HEADER)]
    lines.extend(",".join(str(value) for value in row) for row in rows)
    return "\n".join(lines) + "\n"


PIPELINE = r'''"""End-to-end concrete strength analysis using only the Python standard library."""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

FEATURES = ["cement", "slag", "fly_ash", "water", "superplasticizer", "coarse_aggregate", "fine_aggregate", "age_days"]
TARGET = "strength_mpa"


def load_clean_rows(path: Path) -> list[dict[str, float]]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = []
        for raw in csv.DictReader(handle):
            try:
                row = {key: float(raw[key]) for key in FEATURES + [TARGET]}
            except (KeyError, TypeError, ValueError):
                continue
            if all(math.isfinite(value) for value in row.values()):
                rows.append(row)
    if len(rows) < 10:
        raise ValueError("at least 10 valid rows are required")
    return rows


def split_rows(rows: list[dict[str, float]], ratio: float = 0.75):
    cut = max(1, min(len(rows) - 1, int(len(rows) * ratio)))
    return rows[:cut], rows[cut:]


def _scale(train, rows):
    mins = {feature: min(row[feature] for row in train) for feature in FEATURES}
    spans = {feature: max(row[feature] for row in train) - mins[feature] or 1.0 for feature in FEATURES}
    return [[(row[feature] - mins[feature]) / spans[feature] for feature in FEATURES] for row in rows], mins, spans


def fit_linear_regression(train_rows, iterations=3000, learning_rate=0.08):
    x, mins, spans = _scale(train_rows, train_rows)
    y = [row[TARGET] for row in train_rows]
    weights = [0.0] * len(FEATURES)
    bias = sum(y) / len(y)
    n = float(len(x))
    for _ in range(iterations):
        predictions = [bias + sum(weight * value for weight, value in zip(weights, values)) for values in x]
        errors = [prediction - actual for prediction, actual in zip(predictions, y)]
        gradients = [sum(error * values[index] for error, values in zip(errors, x)) / n for index in range(len(FEATURES))]
        bias -= learning_rate * sum(errors) / n
        for index, gradient in enumerate(gradients):
            weights[index] -= learning_rate * gradient
    return {"weights": weights, "bias": bias, "mins": mins, "spans": spans}


def predict(model, rows):
    predictions = []
    for row in rows:
        values = [(row[feature] - model["mins"][feature]) / model["spans"][feature] for feature in FEATURES]
        predictions.append(model["bias"] + sum(weight * value for weight, value in zip(model["weights"], values)))
    return predictions


def evaluate(actual, predicted):
    errors = [prediction - target for prediction, target in zip(predicted, actual)]
    mae = sum(abs(error) for error in errors) / len(errors)
    rmse = math.sqrt(sum(error * error for error in errors) / len(errors))
    mean_actual = sum(actual) / len(actual)
    ss_res = sum(error * error for error in errors)
    ss_tot = sum((target - mean_actual) ** 2 for target in actual) or 1.0
    return {"mae_mpa": round(mae, 4), "rmse_mpa": round(rmse, 4), "r2": round(1 - ss_res / ss_tot, 4)}


def summarize(rows):
    summary = {"row_count": len(rows)}
    for key in FEATURES + [TARGET]:
        values = [row[key] for row in rows]
        summary[key] = {"min": round(min(values), 3), "mean": round(sum(values) / len(values), 3), "max": round(max(values), 3)}
    return summary


def _svg_scatter(rows, path: Path):
    width, height, pad = 760, 460, 55
    xs = [row["cement"] for row in rows]
    ys = [row[TARGET] for row in rows]
    xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)
    def px(value): return pad + (value - xmin) / (xmax - xmin or 1) * (width - 2 * pad)
    def py(value): return height - pad - (value - ymin) / (ymax - ymin or 1) * (height - 2 * pad)
    circles = "".join(f'<circle cx="{px(x):.1f}" cy="{py(y):.1f}" r="4" fill="steelblue"/>' for x, y in zip(xs, ys))
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"><rect width="100%" height="100%" fill="white"/><text x="{pad}" y="28" font-size="20">Concrete strength vs cement</text><line x1="{pad}" y1="{height-pad}" x2="{width-pad}" y2="{height-pad}" stroke="black"/><line x1="{pad}" y1="{pad}" x2="{pad}" y2="{height-pad}" stroke="black"/>{circles}<text x="{width//2-40}" y="{height-12}" font-size="14">cement</text><text x="12" y="{height//2}" font-size="14" transform="rotate(-90 12 {height//2})">strength (MPa)</text></svg>'
    path.write_text(svg, encoding="utf-8")


def _svg_age(rows, path: Path):
    groups = {}
    for row in rows:
        groups.setdefault(int(row["age_days"]), []).append(row[TARGET])
    width, height, pad = 760, 460, 55
    ages = sorted(groups)
    means = [sum(groups[age]) / len(groups[age]) for age in ages]
    ymin, ymax = min(means) * 0.95, max(means) * 1.05
    def px(index): return pad + index * ((width - 2 * pad) / max(1, len(ages) - 1))
    def py(value): return height - pad - (value - ymin) / (ymax - ymin or 1) * (height - 2 * pad)
    points = " ".join(f"{px(i):.1f},{py(value):.1f}" for i, value in enumerate(means))
    labels = "".join(f'<text x="{px(i):.1f}" y="{height-pad+24}" text-anchor="middle" font-size="12">{age}</text>' for i, age in enumerate(ages))
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"><rect width="100%" height="100%" fill="white"/><text x="{pad}" y="28" font-size="20">Average strength by curing age</text><line x1="{pad}" y1="{height-pad}" x2="{width-pad}" y2="{height-pad}" stroke="black"/><line x1="{pad}" y1="{pad}" x2="{pad}" y2="{height-pad}" stroke="black"/><polyline points="{points}" fill="none" stroke="darkgreen" stroke-width="3"/>{labels}<text x="{width//2-45}" y="{height-12}" font-size="14">age (days)</text></svg>'
    path.write_text(svg, encoding="utf-8")


def run_analysis(project_root: Path):
    data_path = project_root / "data" / "concrete_strength.csv"
    report_dir = project_root / "reports"
    figure_dir = report_dir / "figures"
    report_dir.mkdir(parents=True, exist_ok=True)
    figure_dir.mkdir(parents=True, exist_ok=True)
    rows = load_clean_rows(data_path)
    train, test = split_rows(rows)
    model = fit_linear_regression(train)
    predictions = predict(model, test)
    metrics = evaluate([row[TARGET] for row in test], predictions)
    summary = summarize(rows)
    _svg_scatter(rows, figure_dir / "strength_vs_cement.svg")
    _svg_age(rows, figure_dir / "strength_by_age.svg")
    (report_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (report_dir / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    return {"metrics": metrics, "summary": summary, "train_rows": len(train), "test_rows": len(test)}
'''

DATA_CLEANING = r'''"""Data cleaning helpers for the concrete strength project."""
from __future__ import annotations

from pathlib import Path

from src.pipeline import load_clean_rows


def clean_dataset(path: Path):
    """Load numeric rows and discard malformed records deterministically."""
    return load_clean_rows(path)
'''

EDA = r'''"""Exploratory data analysis helpers."""
from __future__ import annotations


def describe(rows):
    if not rows:
        raise ValueError("rows must not be empty")
    result = {}
    for key in rows[0]:
        values = [row[key] for row in rows]
        result[key] = {"min": min(values), "mean": sum(values) / len(values), "max": max(values)}
    return result
'''

MODEL = r'''"""Simple, reproducible linear regression implementation."""
from src.pipeline import fit_linear_regression, predict

__all__ = ["fit_linear_regression", "predict"]
'''

EVALUATE = r'''"""Model evaluation helpers."""
from src.pipeline import evaluate

__all__ = ["evaluate"]
'''

VIS = r'''"""Visualization helpers."""
from src.pipeline import _svg_age, _svg_scatter

__all__ = ["_svg_age", "_svg_scatter"]
'''

TEST = r'''import json
from pathlib import Path


def test_concrete_project_files_and_notebook_are_valid():
    root = Path(__file__).parents[1]
    expected = ["data/concrete_strength.csv", "notebooks/concrete_strength_analysis.ipynb", "src/data_cleaning.py", "src/eda.py", "src/model.py", "src/evaluate.py", "src/visualization.py", "src/pipeline.py", "README.md", "requirements.txt"]
    for relative in expected:
        assert (root / relative).is_file(), relative
    notebook = json.loads((root / "notebooks/concrete_strength_analysis.ipynb").read_text(encoding="utf-8"))
    assert notebook["nbformat"] == 4
    assert len(notebook["cells"]) >= 12
    assert any("prediction" in "".join(cell.get("source", [])).lower() for cell in notebook["cells"])
    assert any("visual" in "".join(cell.get("source", [])).lower() for cell in notebook["cells"])


def test_dataset_has_expected_shape_and_columns():
    lines = (Path(__file__).parents[1] / "data" / "concrete_strength.csv").read_text(encoding="utf-8").strip().splitlines()
    assert lines[0].split(",")[-1] == "strength_mpa"
    assert len(lines) == 41
'''

NOTEBOOK = {
    "cells": [
        {"cell_type": "markdown", "metadata": {}, "source": ["# Concrete Strength Analysis\n", "\n", "Beginner-friendly end-to-end data science project generated automatically.\n"]},
        {"cell_type": "markdown", "metadata": {}, "source": ["## Problem statement\n", "Predict concrete compressive strength (MPa) from mix composition and curing age.\n"]},
        {"cell_type": "markdown", "metadata": {}, "source": ["## 1. Imports and setup\n", "We use the project modules and keep the analysis reproducible.\n"]},
        {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": ["from pathlib import Path\n", "import sys\n", "sys.path.append('..')\n", "from IPython.display import SVG, display\n", "from src.pipeline import load_clean_rows, summarize, fit_linear_regression, predict, evaluate\n"]},
        {"cell_type": "markdown", "metadata": {}, "source": ["## 2. Load and clean data\n", "Malformed or non-numeric rows are skipped by the cleaning function.\n"]},
        {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": ["rows = load_clean_rows(Path('../data/concrete_strength.csv'))\n", "print('Rows:', len(rows))\n", "print('Columns:', list(rows[0]))\n", "print('First row:', rows[0])\n"]},
        {"cell_type": "markdown", "metadata": {}, "source": ["## 3. Exploratory data analysis\n", "Compare ingredients, curing age, and compressive strength using summary statistics.\n"]},
        {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": ["summary = summarize(rows)\n", "summary['strength_mpa']\n"]},
        {"cell_type": "markdown", "metadata": {}, "source": ["## 4. Visual analysis\n", "The pipeline creates SVG charts for cement vs strength and average strength by curing age.\n"]},
        {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": ["display(SVG('../reports/figures/strength_vs_cement.svg'))\n", "display(SVG('../reports/figures/strength_by_age.svg'))\n"]},
        {"cell_type": "markdown", "metadata": {}, "source": ["## 5. Train the regression model\n", "The model uses the concrete mix features and curing age to predict compressive strength.\n"]},
        {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": ["train, test = rows[:30], rows[30:]\n", "model = fit_linear_regression(train)\n", "predictions = predict(model, test)\n", "print('Training rows:', len(train), 'Test rows:', len(test))\n"]},
        {"cell_type": "markdown", "metadata": {}, "source": ["## 6. Model evaluation\n", "MAE and RMSE measure prediction error; R² measures explained variance.\n"]},
        {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": ["metrics = evaluate([row['strength_mpa'] for row in test], predictions)\n", "metrics\n"]},
        {"cell_type": "markdown", "metadata": {}, "source": ["## 7. Prediction examples\n", "The following examples show actual strength versus the model prediction for test samples.\n"]},
        {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": ["for row, predicted in list(zip(test, predictions))[:5]:\n", "    print({'age_days': int(row['age_days']), 'actual_mpa': row['strength_mpa'], 'predicted_mpa': round(predicted, 2)})\n"]},
        {"cell_type": "markdown", "metadata": {}, "source": ["## 8. Interpretation and reproducibility\n", "The dataset is synthetic and educational. The project requires no API key and can regenerate its reports and figures deterministically.\n"]},
    ],
    "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python", "version": "3"}},
    "nbformat": 4,
    "nbformat_minor": 5,
}


class ConcreteStrengthGenerator(ProjectGenerator):
    project_type = ProjectType.DATA_SCIENCE

    def _write(self, root: Path, files: dict[str, str]) -> list[str]:
        written = []
        for relative, content in files.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            written.append(relative)
        return written

    def generate(self, request: ProjectRequest, plan: ProjectPlan, output_dir: Path) -> Iterable[str]:
        files = {
            "README.md": """# Concrete Strength Analysis\n\nA beginner-friendly, reproducible Data Science project that analyzes a synthetic concrete mix dataset and predicts compressive strength in MPa.\n\n## Workflow\n1. Load and clean the dataset.\n2. Explore descriptive statistics and ingredient/age relationships.\n3. Create meaningful SVG visualizations.\n4. Train a deterministic multiple linear regression model.\n5. Evaluate with MAE, RMSE, and R².\n6. Generate prediction examples.\n7. Save machine-readable reports.\n\n## Run\n```bash\npip install -r requirements.txt\npython -c \"from pathlib import Path; from src.pipeline import run_analysis; print(run_analysis(Path('.')))\"\npytest -q\n```\n\n## Project structure\n- `data/concrete_strength.csv` — reproducible sample dataset.\n- `notebooks/concrete_strength_analysis.ipynb` — guided Jupyter analysis.\n- `src/` — cleaning, EDA, modeling, evaluation, visualization, and pipeline modules.\n- `reports/` — generated metrics, summary, and SVG figures after execution.\n- `tests/` — standalone automated tests.\n\n## Reproducibility\nThe analysis code itself uses only the Python standard library. Jupyter and pytest are included as tools for the notebook and tests. No API keys, internet access, or external AI services are required.\n\n## Important\nThe dataset is synthetic and educational. It must not be used as an engineering design basis.\n""",
            "requirements.txt": "pytest>=8,<10\njupyter>=1,<2\n",
            "data/concrete_strength.csv": _dataset(),
            "src/__init__.py": "",
            "src/data_cleaning.py": DATA_CLEANING,
            "src/eda.py": EDA,
            "src/model.py": MODEL,
            "src/evaluate.py": EVALUATE,
            "src/visualization.py": VIS,
            "src/pipeline.py": PIPELINE,
            "tests/test_concrete_project.py": TEST,
            "notebooks/concrete_strength_analysis.ipynb": json.dumps(NOTEBOOK, indent=2) + "\n",
            "project.json": json.dumps({"name": "concrete-strength-analysis", "project_type": "data_science", "description": request.prompt, "features": ["data cleaning", "EDA", "visualizations", "linear regression", "model evaluation", "prediction examples", "Jupyter notebook", "automated tests", "JSON reports"], "dependencies": ["pytest", "jupyter"]}, indent=2) + "\n",
        }
        return self._write(output_dir, files)


class PromptAwareDataScienceGenerator(ProjectGenerator):
    project_type = ProjectType.DATA_SCIENCE

    def __init__(self) -> None:
        self.basic = BasicDataScienceGenerator()
        self.concrete = ConcreteStrengthGenerator()

    def generate(self, request: ProjectRequest, plan: ProjectPlan, output_dir: Path) -> Iterable[str]:
        prompt = request.prompt.lower()
        if any(term in prompt for term in ("concrete", "cement", "compressive strength", "concrete strength")):
            return self.concrete.generate(request, plan, output_dir)
        return self.basic.generate(request, plan, output_dir)
