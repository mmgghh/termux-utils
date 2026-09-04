from typer.testing import CliRunner

from termux_toolbox.cli import app

runner = CliRunner()


def test_help_shows_json_flag():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "--json" in result.output


def test_interactive_is_registered_and_requires_a_terminal():
    # CliRunner's stdin/stdout are never a real tty, so this exercises the
    # interactive command's own terminal guard end-to-end.
    result = runner.invoke(app, ["interactive"])
    assert result.exit_code == 1
    assert "terminal" in result.output
