from notebook_workflow.cli import build_parser


def test_cli_parser_accepts_project_type_and_output():
    args = build_parser().parse_args(["build a data science project", "--type", "data_science", "--output", "out"])
    assert args.prompt == "build a data science project"
    assert args.type == "data_science"
    assert args.output == "out"


def test_cli_parser_accepts_optional_ai_provider():
    args = build_parser().parse_args(["build an ai project", "--ai-provider", "openrouter"])
    assert args.ai_provider == "openrouter"


def test_cli_parser_accepts_factory_mode():
    args = build_parser().parse_args(["build a project", "--factory"])
    assert args.factory is True
