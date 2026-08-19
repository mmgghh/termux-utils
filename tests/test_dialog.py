from unittest.mock import patch

from typer.testing import CliRunner

from termux_toolbox.cli import app

runner = CliRunner()

DIALOG_TIMEOUT = 300.0


def test_dialog_text_defaults():
    with patch("termux_toolbox.commands.dialog.run_termux_api", return_value={}) as mock_run:
        result = runner.invoke(app, ["dialog", "text"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with(
        "termux-dialog", args=["text"], timeout=DIALOG_TIMEOUT
    )


def test_dialog_text_all_options():
    with patch("termux_toolbox.commands.dialog.run_termux_api", return_value={}) as mock_run:
        result = runner.invoke(
            app,
            ["dialog", "text", "--title", "Name", "--hint", "First name", "--multiline"],
        )
    assert result.exit_code == 0
    mock_run.assert_called_once_with(
        "termux-dialog",
        args=["text", "-t", "Name", "-i", "First name", "-m"],
        timeout=DIALOG_TIMEOUT,
    )


def test_dialog_text_password_and_numeric():
    with patch("termux_toolbox.commands.dialog.run_termux_api", return_value={}) as mock_run:
        result = runner.invoke(app, ["dialog", "text", "--password", "--numeric"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with(
        "termux-dialog", args=["text", "-n", "-p"], timeout=DIALOG_TIMEOUT
    )


def test_dialog_text_rejects_multiline_with_numeric():
    with patch("termux_toolbox.commands.dialog.run_termux_api", return_value={}) as mock_run:
        result = runner.invoke(app, ["dialog", "text", "--multiline", "--numeric"])
    assert result.exit_code == 1
    assert "--multiline" in result.output
    mock_run.assert_not_called()


def test_dialog_confirm():
    with patch("termux_toolbox.commands.dialog.run_termux_api", return_value={}) as mock_run:
        result = runner.invoke(app, ["dialog", "confirm", "--title", "Sure?", "--hint", "yes/no"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with(
        "termux-dialog",
        args=["confirm", "-t", "Sure?", "-i", "yes/no"],
        timeout=DIALOG_TIMEOUT,
    )


def test_dialog_checkbox_joins_values():
    with patch("termux_toolbox.commands.dialog.run_termux_api", return_value={}) as mock_run:
        result = runner.invoke(app, ["dialog", "checkbox", "one", "two", "three", "--title", "Pick"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with(
        "termux-dialog",
        args=["checkbox", "-t", "Pick", "-v", "one,two,three"],
        timeout=DIALOG_TIMEOUT,
    )


def test_dialog_radio_values():
    with patch("termux_toolbox.commands.dialog.run_termux_api", return_value={}) as mock_run:
        result = runner.invoke(app, ["dialog", "radio", "a", "b"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with(
        "termux-dialog", args=["radio", "-v", "a,b"], timeout=DIALOG_TIMEOUT
    )


def test_dialog_sheet_values():
    with patch("termux_toolbox.commands.dialog.run_termux_api", return_value={}) as mock_run:
        result = runner.invoke(app, ["dialog", "sheet", "a", "b"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with(
        "termux-dialog", args=["sheet", "-v", "a,b"], timeout=DIALOG_TIMEOUT
    )


def test_dialog_spinner_values():
    with patch("termux_toolbox.commands.dialog.run_termux_api", return_value={}) as mock_run:
        result = runner.invoke(app, ["dialog", "spinner", "a", "b"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with(
        "termux-dialog", args=["spinner", "-v", "a,b"], timeout=DIALOG_TIMEOUT
    )


def test_dialog_counter_range():
    with patch("termux_toolbox.commands.dialog.run_termux_api", return_value={}) as mock_run:
        result = runner.invoke(app, ["dialog", "counter", "--range", "1,100,50"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with(
        "termux-dialog", args=["counter", "-r", "1,100,50"], timeout=DIALOG_TIMEOUT
    )


def test_dialog_date_format():
    with patch("termux_toolbox.commands.dialog.run_termux_api", return_value={}) as mock_run:
        result = runner.invoke(app, ["dialog", "date", "--date-format", "dd-MM-yyyy"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with(
        "termux-dialog", args=["date", "-d", "dd-MM-yyyy"], timeout=DIALOG_TIMEOUT
    )


def test_dialog_time():
    with patch("termux_toolbox.commands.dialog.run_termux_api", return_value={}) as mock_run:
        result = runner.invoke(app, ["dialog", "time", "--title", "When?"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with(
        "termux-dialog", args=["time", "-t", "When?"], timeout=DIALOG_TIMEOUT
    )


def test_dialog_speech():
    with patch("termux_toolbox.commands.dialog.run_termux_api", return_value={}) as mock_run:
        result = runner.invoke(app, ["dialog", "speech", "--hint", "Speak now"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with(
        "termux-dialog", args=["speech", "-i", "Speak now"], timeout=DIALOG_TIMEOUT
    )
