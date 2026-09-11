from notebook_workflow.cli import build_parser


def test_cli_parser_accepts_project_type_and_output():
    args = build_parser().parse_args(["build a data science project", "--type", "data_science", "--output", "out"])
    assert args.prompt == "build a data science project"
    assert args.type == "data_science"
    assert args.output == "out"
