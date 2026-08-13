import typer
from typer.testing import CliRunner

from termux_toolbox.core.errors import (
    CommandFailed,
    PermissionDenied,
    TermuxApiNotFound,
    handle_errors,
)

runner = CliRunner()


def test_termux_api_not_found_message():
    exc = TermuxApiNotFound("termux-battery-status")
    assert "termux-battery-status" in str(exc)
    assert "f-droid" in str(exc).lower()


def test_permission_denied_message_and_attributes():
    exc = PermissionDenied("termux-sms-list", "Permission denied")
    assert "termux-sms-list" in str(exc)
    assert exc.command == "termux-sms-list"
    assert exc.stderr == "Permission denied"


def test_command_failed_message_and_attributes():
    exc = CommandFailed("termux-sms-send", "invalid number", 2)
    assert "exit 2" in str(exc)
    assert "invalid number" in str(exc)
    assert exc.returncode == 2


def test_handle_errors_prints_clean_message_and_exits_1():
    app = typer.Typer()

    @app.command()
    @handle_errors
    def boom() -> None:
        raise CommandFailed("termux-torch", "boom", 1)

    result = runner.invoke(app, [])
    assert result.exit_code == 1
    assert "Error:" in result.output
    assert "boom" in result.output


def test_handle_errors_lets_success_through():
    app = typer.Typer()

    @app.command()
    @handle_errors
    def ok() -> None:
        typer.echo("fine")

    result = runner.invoke(app, [])
    assert result.exit_code == 0
    assert "fine" in result.output
