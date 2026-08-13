from unittest.mock import patch

from typer.testing import CliRunner

from termux_toolbox.cli import app

runner = CliRunner()


def test_torch_on():
    with patch("termux_toolbox.commands.device.run_termux_api", return_value="") as mock_run:
        result = runner.invoke(app, ["torch", "on"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-torch", args=["on"])


def test_torch_rejects_invalid_state():
    result = runner.invoke(app, ["torch", "sideways"])
    assert result.exit_code == 1
    assert "on" in result.output and "off" in result.output


def test_volume_no_args_queries_all_streams():
    fake = [{"stream": "music", "volume": 5, "max_volume": 15}]
    with patch("termux_toolbox.commands.device.run_termux_api", return_value=fake) as mock_run:
        result = runner.invoke(app, ["volume"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-volume", args=[])


def test_volume_sets_stream_level():
    with patch("termux_toolbox.commands.device.run_termux_api", return_value="") as mock_run:
        result = runner.invoke(app, ["volume", "music", "8"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-volume", args=["music", "8"])


def test_volume_rejects_stream_without_level():
    result = runner.invoke(app, ["volume", "music"])
    assert result.exit_code == 1
    assert "Error:" in result.output


def test_brightness():
    with patch("termux_toolbox.commands.device.run_termux_api", return_value="") as mock_run:
        runner.invoke(app, ["brightness", "128"])
    mock_run.assert_called_once_with("termux-brightness", args=["128"])


def test_wifi_info():
    fake = {"ssid": "MyNetwork", "ip": "192.168.1.5"}
    with patch("termux_toolbox.commands.device.run_termux_api", return_value=fake):
        result = runner.invoke(app, ["wifi", "info"])
    assert result.exit_code == 0
    assert "ssid: MyNetwork" in result.output


def test_wifi_enable():
    with patch("termux_toolbox.commands.device.run_termux_api", return_value="") as mock_run:
        runner.invoke(app, ["wifi", "enable"])
    mock_run.assert_called_once_with("termux-wifi-enable", args=["true"])


def test_wifi_disable():
    with patch("termux_toolbox.commands.device.run_termux_api", return_value="") as mock_run:
        runner.invoke(app, ["wifi", "disable"])
    mock_run.assert_called_once_with("termux-wifi-enable", args=["false"])
