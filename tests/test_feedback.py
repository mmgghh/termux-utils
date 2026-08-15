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


def test_tts_engines():
    fake = [{"name": "com.google.android.tts", "default": True}]
    with patch("termux_toolbox.commands.feedback.run_termux_api", return_value=fake) as mock_run:
        result = runner.invoke(app, ["tts-engines"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-tts-engines")


def test_speech_to_text_default():
    with patch("termux_toolbox.commands.feedback.run_termux_api", return_value="hello") as mock_run:
        result = runner.invoke(app, ["speech-to-text"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-speech-to-text", args=[], timeout=60.0)


def test_speech_to_text_progress():
    with patch("termux_toolbox.commands.feedback.run_termux_api", return_value="hello") as mock_run:
        runner.invoke(app, ["speech-to-text", "--progress"])
    mock_run.assert_called_once_with("termux-speech-to-text", args=["-p"], timeout=60.0)


def test_download_url_only():
    with patch("termux_toolbox.commands.feedback.run_termux_api", return_value="") as mock_run:
        runner.invoke(app, ["download", "https://example.com/file.zip"])
    mock_run.assert_called_once_with("termux-download", args=["https://example.com/file.zip"])


def test_download_all_options():
    with patch("termux_toolbox.commands.feedback.run_termux_api", return_value="") as mock_run:
        runner.invoke(
            app,
            [
                "download",
                "https://example.com/file.zip",
                "--description", "desc",
                "--title", "title",
                "--path", "/sdcard/file.zip",
            ],
        )
    mock_run.assert_called_once_with(
        "termux-download",
        args=["-d", "desc", "-t", "title", "-p", "/sdcard/file.zip", "https://example.com/file.zip"],
    )


def test_share_file_default_action():
    with patch("termux_toolbox.commands.feedback.run_termux_api", return_value="") as mock_run:
        runner.invoke(app, ["share", "/sdcard/pic.jpg"])
    mock_run.assert_called_once_with("termux-share", args=["-a", "view", "/sdcard/pic.jpg"])


def test_share_stdin_with_options():
    with patch("termux_toolbox.commands.feedback.run_termux_api", return_value="") as mock_run:
        runner.invoke(
            app,
            [
                "share",
                "--action", "send",
                "--content-type", "text/plain",
                "--default-receiver",
                "--title", "Note",
            ],
        )
    mock_run.assert_called_once_with(
        "termux-share",
        args=["-a", "send", "-c", "text/plain", "-d", "-t", "Note"],
    )


def test_notification_list():
    fake = [{"id": "1", "title": "Test"}]
    with patch("termux_toolbox.commands.feedback.run_termux_api", return_value=fake) as mock_run:
        result = runner.invoke(app, ["notification", "list"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-notification-list")


def test_notification_remove():
    with patch("termux_toolbox.commands.feedback.run_termux_api", return_value="") as mock_run:
        runner.invoke(app, ["notification", "remove", "42"])
    mock_run.assert_called_once_with("termux-notification-remove", args=["42"])


def test_notification_channel_create():
    with patch("termux_toolbox.commands.feedback.run_termux_api", return_value="") as mock_run:
        runner.invoke(app, ["notification", "channel", "create", "updates", "Updates"])
    mock_run.assert_called_once_with("termux-notification-channel", args=["updates", "Updates"])


def test_notification_channel_delete():
    with patch("termux_toolbox.commands.feedback.run_termux_api", return_value="") as mock_run:
        runner.invoke(app, ["notification", "channel", "delete", "updates"])
    mock_run.assert_called_once_with("termux-notification-channel", args=["-d", "updates"])
