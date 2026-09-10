from notebook_workflow.execution.runner import CommandRunner


def test_runner_executes_successful_command():
    result = CommandRunner().run(["python", "-c", "print('ok')"])
    assert result.returncode == 0
    assert "ok" in result.stdout
    assert result.timed_out is False


def test_runner_captures_failed_command():
    result = CommandRunner().run(["python", "-c", "raise SystemExit(3)"])
    assert result.returncode == 3
    assert result.failed is True
