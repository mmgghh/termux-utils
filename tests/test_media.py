from unittest.mock import patch

from typer.testing import CliRunner

from termux_toolbox.cli import app

runner = CliRunner()


def test_camera_photo_defaults_to_back():
    with patch("termux_toolbox.commands.media.run_termux_api", return_value="") as mock_run:
        runner.invoke(app, ["camera", "photo", "/sdcard/out.jpg"])
    mock_run.assert_called_once_with("termux-camera-photo", args=["-c", "0", "/sdcard/out.jpg"])


def test_camera_photo_front():
    with patch("termux_toolbox.commands.media.run_termux_api", return_value="") as mock_run:
        runner.invoke(app, ["camera", "photo", "/sdcard/out.jpg", "--camera", "front"])
    mock_run.assert_called_once_with("termux-camera-photo", args=["-c", "1", "/sdcard/out.jpg"])


def test_media_play():
    with patch("termux_toolbox.commands.media.run_termux_api", return_value="") as mock_run:
        runner.invoke(app, ["media", "play", "/sdcard/song.mp3"])
    mock_run.assert_called_once_with("termux-media-player", args=["play", "/sdcard/song.mp3"])


def test_mic_record_default_duration():
    with patch("termux_toolbox.commands.media.run_termux_api", return_value="") as mock_run:
        runner.invoke(app, ["mic", "record", "/sdcard/audio.m4a"])
    mock_run.assert_called_once_with(
        "termux-microphone-record", args=["-f", "/sdcard/audio.m4a", "-l", "10"]
    )


def test_mic_record_custom_duration():
    with patch("termux_toolbox.commands.media.run_termux_api", return_value="") as mock_run:
        runner.invoke(app, ["mic", "record", "/sdcard/audio.m4a", "--duration", "30"])
    mock_run.assert_called_once_with(
        "termux-microphone-record", args=["-f", "/sdcard/audio.m4a", "-l", "30"]
    )
