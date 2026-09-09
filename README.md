# automatic-jupyter-workflow
An automated Jupyter Notebook workflow for generating, processing, and managing notebooks using Python. Includes content generation, reference analysis, task processing, API integration, notebook generation, CLI tools, tests, and documentation.
# Automatic Jupyter Notebook Workflow

This project converts structured task material into a validated Jupyter Notebook without manual copy-paste.

## Workflow

Reference/task material -> analysis -> original content -> validation -> `.ipynb` -> JupyterLab

Each topic contains:
- Explanation
- New Example
- Code
- Expected Output
- Notes

## Run

```bash
python -m notebook_workflow.cli
```

Programmatic usage:

```python
from notebook_workflow.cli import run_workflow
run_workflow("task.json", "generated_notebooks")
```

The project is designed to scale from Task 1 to Task 4 and future tasks.
