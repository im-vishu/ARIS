from app.tools.command_runner import run_command

def test_run_command_success():
    result = run_command("echo hello")
    assert result.success is True
    assert "hello" in result.stdout.lower()

def test_run_command_failure():
    result = run_command("some_non_existing_command_123")
    assert result.success is False