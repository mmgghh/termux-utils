from typer.testing import CliRunner

from termux_toolbox.cli import app

runner = CliRunner()


def test_help_shows_json_flag():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "--json" in result.output
