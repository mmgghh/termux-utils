from unittest.mock import patch

from typer.testing import CliRunner

from termux_toolbox.cli import app

runner = CliRunner()


def test_storage_get():
    with patch("termux_toolbox.commands.storage.run_termux_api", return_value="") as mock_run:
        result = runner.invoke(app, ["storage-get", "/sdcard/picked.pdf"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with(
        "termux-storage-get", args=["/sdcard/picked.pdf"], timeout=120.0
    )


def test_saf_dirs():
    fake = [{"name": "Documents", "uri": "content://tree/1"}]
    with patch("termux_toolbox.commands.storage.run_termux_api", return_value=fake) as mock_run:
        result = runner.invoke(app, ["saf", "dirs"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-saf-dirs")


def test_saf_managedir():
    with patch("termux_toolbox.commands.storage.run_termux_api", return_value="content://tree/2") as mock_run:
        result = runner.invoke(app, ["saf", "managedir"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-saf-managedir", timeout=120.0)


def test_saf_ls():
    fake = [{"name": "a.txt", "uri": "content://doc/1", "type": "text/plain"}]
    with patch("termux_toolbox.commands.storage.run_termux_api", return_value=fake) as mock_run:
        result = runner.invoke(app, ["saf", "ls", "content://tree/1"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-saf-ls", args=["content://tree/1"])


def test_saf_create_without_mime():
    with patch("termux_toolbox.commands.storage.run_termux_api", return_value="content://doc/2") as mock_run:
        runner.invoke(app, ["saf", "create", "content://tree/1", "new.txt"])
    mock_run.assert_called_once_with("termux-saf-create", args=["content://tree/1", "new.txt"])


def test_saf_create_with_mime():
    with patch("termux_toolbox.commands.storage.run_termux_api", return_value="content://doc/2") as mock_run:
        runner.invoke(
            app, ["saf", "create", "content://tree/1", "new.mp4", "--mime-type", "video/mp4"]
        )
    mock_run.assert_called_once_with(
        "termux-saf-create", args=["-t", "video/mp4", "content://tree/1", "new.mp4"]
    )


def test_saf_mkdir():
    with patch("termux_toolbox.commands.storage.run_termux_api", return_value="content://doc/3") as mock_run:
        runner.invoke(app, ["saf", "mkdir", "content://tree/1", "subfolder"])
    mock_run.assert_called_once_with("termux-saf-mkdir", args=["content://tree/1", "subfolder"])


def test_saf_stat():
    fake = {"name": "a.txt", "uri": "content://doc/1", "length": 42}
    with patch("termux_toolbox.commands.storage.run_termux_api", return_value=fake) as mock_run:
        result = runner.invoke(app, ["saf", "stat", "content://doc/1"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-saf-stat", args=["content://doc/1"])
