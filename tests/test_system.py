from unittest.mock import patch

from typer.testing import CliRunner

from termux_toolbox.cli import app

runner = CliRunner()


def test_job_list():
    with patch("termux_toolbox.commands.system.run_termux_api", return_value=[]) as mock_run:
        result = runner.invoke(app, ["job", "list"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-job-scheduler", args=["--pending"])


def test_job_cancel():
    with patch("termux_toolbox.commands.system.run_termux_api", return_value="") as mock_run:
        result = runner.invoke(app, ["job", "cancel", "7"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with(
        "termux-job-scheduler", args=["--cancel", "--job-id", "7"]
    )


def test_job_cancel_all():
    with patch("termux_toolbox.commands.system.run_termux_api", return_value="") as mock_run:
        result = runner.invoke(app, ["job", "cancel-all"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-job-scheduler", args=["--cancel-all"])


def test_job_schedule_minimal():
    with patch("termux_toolbox.commands.system.run_termux_api", return_value="") as mock_run:
        result = runner.invoke(app, ["job", "schedule", "/data/backup.sh"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with(
        "termux-job-scheduler", args=["--script", "/data/backup.sh"]
    )


def test_job_schedule_full():
    with patch("termux_toolbox.commands.system.run_termux_api", return_value="") as mock_run:
        result = runner.invoke(
            app,
            [
                "job",
                "schedule",
                "/data/backup.sh",
                "--job-id",
                "3",
                "--period-ms",
                "900000",
                "--network",
                "unmetered",
                "--charging",
                "--persisted",
                "--no-battery-not-low",
                "--storage-not-low",
                "--trigger-content-uri",
                "content://media",
                "--trigger-content-flag",
                "1",
            ],
        )
    assert result.exit_code == 0
    mock_run.assert_called_once_with(
        "termux-job-scheduler",
        args=[
            "--script",
            "/data/backup.sh",
            "--job-id",
            "3",
            "--period-ms",
            "900000",
            "--network",
            "unmetered",
            "--battery-not-low",
            "false",
            "--storage-not-low",
            "true",
            "--charging",
            "true",
            "--persisted",
            "true",
            "--trigger-content-uri",
            "content://media",
            "--trigger-content-flag",
            "1",
        ],
    )


def test_keystore_list():
    with patch("termux_toolbox.commands.system.run_termux_api", return_value=[]) as mock_run:
        result = runner.invoke(app, ["keystore", "list"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-keystore", args=["list"])


def test_keystore_list_detailed():
    with patch("termux_toolbox.commands.system.run_termux_api", return_value=[]) as mock_run:
        result = runner.invoke(app, ["keystore", "list", "--detailed"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-keystore", args=["list", "-d"])


def test_keystore_generate():
    with patch("termux_toolbox.commands.system.run_termux_api", return_value="") as mock_run:
        result = runner.invoke(
            app,
            ["keystore", "generate", "mykey", "--algorithm", "EC", "--size", "384", "--validity", "60"],
        )
    assert result.exit_code == 0
    mock_run.assert_called_once_with(
        "termux-keystore", args=["generate", "mykey", "-a", "EC", "-s", "384", "-u", "60"]
    )


def test_keystore_delete():
    with patch("termux_toolbox.commands.system.run_termux_api", return_value="") as mock_run:
        result = runner.invoke(app, ["keystore", "delete", "mykey"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-keystore", args=["delete", "mykey"])


def test_keystore_sign_writes_raw_signature():
    with patch(
        "termux_toolbox.commands.system.run_termux_api_bytes", return_value=b"\x00sig"
    ) as mock_run:
        result = runner.invoke(app, ["keystore", "sign", "mykey", "SHA256withRSA"], input=b"data")
    assert result.exit_code == 0
    mock_run.assert_called_once_with(
        "termux-keystore",
        args=["sign", "mykey", "SHA256withRSA"],
        input_bytes=b"data",
        timeout=60.0,
    )


def test_keystore_verify():
    with patch(
        "termux_toolbox.commands.system.run_termux_api_bytes", return_value=b"true\n"
    ) as mock_run:
        result = runner.invoke(
            app, ["keystore", "verify", "mykey", "SHA256withRSA", "/tmp/sig"], input=b"data"
        )
    assert result.exit_code == 0
    assert "true" in result.output
    mock_run.assert_called_once_with(
        "termux-keystore",
        args=["verify", "mykey", "SHA256withRSA", "/tmp/sig"],
        input_bytes=b"data",
        timeout=60.0,
    )


def test_api_start():
    with patch("termux_toolbox.commands.system.run_termux_api", return_value="") as mock_run:
        result = runner.invoke(app, ["api", "start"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-api-start")


def test_api_stop():
    with patch("termux_toolbox.commands.system.run_termux_api", return_value="") as mock_run:
        result = runner.invoke(app, ["api", "stop"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-api-stop")
