from unittest.mock import patch

from typer.testing import CliRunner

from termux_toolbox.cli import app

runner = CliRunner()


def test_clipboard_get():
    with patch("termux_toolbox.commands.feedback.run_termux_api", return_value="copied text"):
        result = runner.invoke(app, ["clipboard", "get"])
    assert result.exit_code == 0
    assert "copied text" in result.output


def test_clipboard_set():
    with patch("termux_toolbox.commands.feedback.run_termux_api", return_value="") as mock_run:
        runner.invoke(app, ["clipboard", "set", "new text"])
    mock_run.assert_called_once_with("termux-clipboard-set", args=["new text"])


def test_notify():
    with patch("termux_toolbox.commands.feedback.run_termux_api", return_value="") as mock_run:
        runner.invoke(app, ["notify", "Title", "Body text"])
    mock_run.assert_called_once_with("termux-notification", args=["-t", "Title", "-c", "Body text"])


def test_toast():
    with patch("termux_toolbox.commands.feedback.run_termux_api", return_value="") as mock_run:
        runner.invoke(app, ["toast", "hi there"])
    mock_run.assert_called_once_with("termux-toast", args=["hi there"])


def test_vibrate_default_duration():
    with patch("termux_toolbox.commands.feedback.run_termux_api", return_value="") as mock_run:
        runner.invoke(app, ["vibrate"])
    mock_run.assert_called_once_with("termux-vibrate", args=["-d", "1000"])


def test_vibrate_custom_duration():
    with patch("termux_toolbox.commands.feedback.run_termux_api", return_value="") as mock_run:
        runner.invoke(app, ["vibrate", "--duration-ms", "250"])
    mock_run.assert_called_once_with("termux-vibrate", args=["-d", "250"])


def test_speak():
    with patch("termux_toolbox.commands.feedback.run_termux_api", return_value="") as mock_run:
        runner.invoke(app, ["speak", "hello world"])
    mock_run.assert_called_once_with("termux-tts-speak", args=["hello world"])
