from unittest.mock import patch

from typer.testing import CliRunner

from termux_toolbox.cli import app

runner = CliRunner()


def test_sms_list_default_limit():
    with patch("termux_toolbox.commands.messaging.run_termux_api", return_value=[]) as mock_run:
        runner.invoke(app, ["sms", "list"])
    mock_run.assert_called_once_with("termux-sms-list", args=["-l", "10"])


def test_sms_list_custom_limit():
    with patch("termux_toolbox.commands.messaging.run_termux_api", return_value=[]) as mock_run:
        runner.invoke(app, ["sms", "list", "--limit", "5"])
    mock_run.assert_called_once_with("termux-sms-list", args=["-l", "5"])


def test_sms_send():
    with patch("termux_toolbox.commands.messaging.run_termux_api", return_value="") as mock_run:
        result = runner.invoke(app, ["sms", "send", "5551234", "hello there"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-sms-send", args=["-n", "5551234", "hello there"])


def test_call():
    with patch("termux_toolbox.commands.messaging.run_termux_api", return_value="") as mock_run:
        result = runner.invoke(app, ["call", "5551234"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-telephony-call", args=["5551234"])


def test_contacts_list():
    fake = [{"name": "Bob", "number": "555"}]
    with patch("termux_toolbox.commands.messaging.run_termux_api", return_value=fake):
        result = runner.invoke(app, ["contacts", "list"])
    assert result.exit_code == 0
    assert "name=Bob" in result.output
