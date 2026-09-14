# Mobile control

The factory can run on GitHub-hosted runners, so the user's PC does not need to stay powered on for a workflow run. GitHub supports manual workflow dispatch from the Actions UI and REST API. The dispatch API requires Actions write permission. citeturn1search0turn1search2

## Phone-friendly option

Use `tools/mobile_dispatch.py` from a trusted mobile terminal such as Termux.

Set:

```bash
export GITHUB_TOKEN='YOUR_FINE_GRAINED_TOKEN'
export GITHUB_REPO='chaudhariSAAB/automatic-jupyter-workflow'
```

Then:

```bash
python tools/mobile_dispatch.py "build a sales dashboard" --type data_science
```

The script sends only the workflow inputs to GitHub. It does not write the token to the generated project or artifact.

## Token rule

Use the minimum repository permission needed for workflow dispatch (`Actions: write`). Never put the token inside source code, notebooks, generated projects, ZIP files, or prompts. GitHub recommends using the built-in `GITHUB_TOKEN` for workflows themselves where possible. citeturn1search4turn1search11

## Reusable factory

`automation.yml` supports `workflow_call`, so another workflow can invoke the factory without copying the implementation. GitHub documents reusable workflows and matrix calls as the supported mechanism for this architecture. citeturn0search0turn0search1
