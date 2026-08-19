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


def test_fingerprint_no_options():
    fake = {"auth_result": "AUTH_RESULT_SUCCESS"}
    with patch("termux_toolbox.commands.sensors.run_termux_api", return_value=fake) as mock_run:
        result = runner.invoke(app, ["fingerprint"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-fingerprint", args=[], timeout=30.0)


def test_fingerprint_all_options():
    with patch("termux_toolbox.commands.sensors.run_termux_api", return_value={}) as mock_run:
        runner.invoke(
            app,
            [
                "fingerprint",
                "--title", "Confirm",
                "--description", "Please scan",
                "--subtitle", "Sub",
                "--cancel", "Nope",
            ],
        )
    mock_run.assert_called_once_with(
        "termux-fingerprint",
        args=["-t", "Confirm", "-d", "Please scan", "-s", "Sub", "-c", "Nope"],
        timeout=30.0,
    )


def test_infrared_frequencies():
    fake = [30000, 33000, 36000, 38000, 40000, 56000]
    with patch("termux_toolbox.commands.sensors.run_termux_api", return_value=fake) as mock_run:
        result = runner.invoke(app, ["infrared", "frequencies"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-infrared-frequencies")


def test_infrared_transmit():
    with patch("termux_toolbox.commands.sensors.run_termux_api", return_value="") as mock_run:
        result = runner.invoke(app, ["infrared", "transmit", "20,50,20,30", "--frequency", "38000"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with(
        "termux-infrared-transmit", args=["-f", "38000", "20,50,20,30"]
    )


def test_location_request_kind():
    with patch("termux_toolbox.commands.sensors.run_termux_api", return_value={}) as mock_run:
        runner.invoke(app, ["location", "--request", "last"])
    mock_run.assert_called_once_with(
        "termux-location", args=["-p", "gps", "-r", "last"], timeout=60.0
    )


def test_sensor_read_multiple_sensors():
    with patch("termux_toolbox.commands.sensors.run_termux_api", return_value={}) as mock_run:
        runner.invoke(app, ["sensor", "read", "Accelerometer", "Gyroscope"])
    args = mock_run.call_args.kwargs["args"]
    assert args[:2] == ["-s", "Accelerometer,Gyroscope"]


def test_sensor_all():
    with patch("termux_toolbox.commands.sensors.run_termux_api", return_value={}) as mock_run:
        runner.invoke(app, ["sensor", "all", "--delay-ms", "500", "--limit", "2"])
    args = mock_run.call_args.kwargs["args"]
    assert args == ["-a", "-d", "500", "-n", "2"]


def test_sensor_cleanup():
    with patch("termux_toolbox.commands.sensors.run_termux_api", return_value="") as mock_run:
        result = runner.invoke(app, ["sensor", "cleanup"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-sensor", args=["-c"])
