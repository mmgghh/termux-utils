from unittest.mock import patch

from typer.testing import CliRunner

from termux_toolbox.cli import app

runner = CliRunner()


def test_battery_text_output():
    fake = {"percentage": 87, "status": "CHARGING"}
    with patch("termux_toolbox.commands.sensors.run_termux_api", return_value=fake):
        result = runner.invoke(app, ["battery"])
    assert result.exit_code == 0
    assert "percentage: 87" in result.output


def test_battery_json_output():
    fake = {"percentage": 87}
    with patch("termux_toolbox.commands.sensors.run_termux_api", return_value=fake):
        result = runner.invoke(app, ["--json", "battery"])
    assert result.exit_code == 0
    assert result.output.strip() == '{"percentage": 87}'


def test_battery_prints_clean_error_on_command_failed():
    from termux_toolbox.core.errors import CommandFailed

    with patch(
        "termux_toolbox.commands.sensors.run_termux_api",
        side_effect=CommandFailed("termux-battery-status", "boom", 1),
    ):
        result = runner.invoke(app, ["battery"])
    assert result.exit_code == 1
    assert "Error:" in result.output


def test_location_passes_provider_option():
    with patch("termux_toolbox.commands.sensors.run_termux_api", return_value={}) as mock_run:
        runner.invoke(app, ["location", "--provider", "network"])
    mock_run.assert_called_once_with(
        "termux-location", args=["-p", "network", "-r", "once"], timeout=60.0
    )


def test_location_defaults_to_gps():
    with patch("termux_toolbox.commands.sensors.run_termux_api", return_value={}) as mock_run:
        runner.invoke(app, ["location"])
    mock_run.assert_called_once_with(
        "termux-location", args=["-p", "gps", "-r", "once"], timeout=60.0
    )


def test_sensor_list():
    fake = ["Accelerometer", "Gyroscope"]
    with patch("termux_toolbox.commands.sensors.run_termux_api", return_value=fake):
        result = runner.invoke(app, ["sensor", "list"])
    assert result.exit_code == 0
    assert "Accelerometer" in result.output


def test_sensor_read_builds_expected_args():
    with patch("termux_toolbox.commands.sensors.run_termux_api", return_value={}) as mock_run:
        runner.invoke(app, ["sensor", "read", "Accelerometer", "--delay-ms", "500", "--limit", "3"])
    mock_run.assert_called_once_with(
        "termux-sensor", args=["-s", "Accelerometer", "-d", "500", "-n", "3"], timeout=15.0
    )


def test_sensor_read_timeout_scales_with_delay_and_limit():
    with patch("termux_toolbox.commands.sensors.run_termux_api", return_value={}) as mock_run:
        runner.invoke(
            app, ["sensor", "read", "Accelerometer", "--delay-ms", "10000", "--limit", "5"]
        )
    mock_run.assert_called_once_with(
        "termux-sensor", args=["-s", "Accelerometer", "-d", "10000", "-n", "5"], timeout=55.0
    )
