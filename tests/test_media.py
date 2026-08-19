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


def test_camera_info():
    fake = [{"id": "0", "facing": "back"}]
    with patch("termux_toolbox.commands.media.run_termux_api", return_value=fake) as mock_run:
        result = runner.invoke(app, ["camera", "info"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-camera-info")


def test_media_play_no_file_resumes():
    with patch("termux_toolbox.commands.media.run_termux_api", return_value="") as mock_run:
        result = runner.invoke(app, ["media", "play"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-media-player", args=["play"])


def test_media_pause():
    with patch("termux_toolbox.commands.media.run_termux_api", return_value="") as mock_run:
        runner.invoke(app, ["media", "pause"])
    mock_run.assert_called_once_with("termux-media-player", args=["pause"])


def test_media_stop():
    with patch("termux_toolbox.commands.media.run_termux_api", return_value="") as mock_run:
        runner.invoke(app, ["media", "stop"])
    mock_run.assert_called_once_with("termux-media-player", args=["stop"])


def test_media_info():
    fake = {"title": "Song", "playing": True}
    with patch("termux_toolbox.commands.media.run_termux_api", return_value=fake) as mock_run:
        result = runner.invoke(app, ["media", "info"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-media-player", args=["info"])


def test_media_scan_single_file():
    with patch("termux_toolbox.commands.media.run_termux_api", return_value="") as mock_run:
        runner.invoke(app, ["media", "scan", "/sdcard/pic.jpg"])
    mock_run.assert_called_once_with(
        "termux-media-scan", args=["/sdcard/pic.jpg"], timeout=30.0
    )


def test_media_scan_recursive_verbose_multiple_files():
    with patch("termux_toolbox.commands.media.run_termux_api", return_value="") as mock_run:
        runner.invoke(
            app, ["media", "scan", "/sdcard/dir1", "/sdcard/dir2", "--recursive", "--verbose"]
        )
    mock_run.assert_called_once_with(
        "termux-media-scan", args=["-r", "-v", "/sdcard/dir1", "/sdcard/dir2"], timeout=30.0
    )


def test_camera_photo_accepts_raw_camera_id():
    with patch("termux_toolbox.commands.media.run_termux_api", return_value="") as mock_run:
        result = runner.invoke(app, ["camera", "photo", "/sdcard/a.jpg", "--camera", "2"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with(
        "termux-camera-photo", args=["-c", "2", "/sdcard/a.jpg"]
    )


def test_mic_record_encoding_options():
    with patch("termux_toolbox.commands.media.run_termux_api", return_value="") as mock_run:
        result = runner.invoke(
            app,
            [
                "mic",
                "record",
                "/sdcard/a.m4a",
                "--duration",
                "0",
                "--encoder",
                "opus",
                "--bitrate",
                "128",
                "--sample-rate",
                "44100",
                "--channels",
                "2",
            ],
        )
    assert result.exit_code == 0
    mock_run.assert_called_once_with(
        "termux-microphone-record",
        args=[
            "-f",
            "/sdcard/a.m4a",
            "-l",
            "0",
            "-e",
            "opus",
            "-b",
            "128",
            "-r",
            "44100",
            "-c",
            "2",
        ],
    )


def test_mic_record_without_path_uses_defaults():
    with patch("termux_toolbox.commands.media.run_termux_api", return_value="") as mock_run:
        result = runner.invoke(app, ["mic", "record"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-microphone-record", args=["-d", "-l", "10"])


def test_mic_info():
    with patch("termux_toolbox.commands.media.run_termux_api", return_value={}) as mock_run:
        result = runner.invoke(app, ["mic", "info"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-microphone-record", args=["-i"])


def test_mic_stop():
    with patch("termux_toolbox.commands.media.run_termux_api", return_value="") as mock_run:
        result = runner.invoke(app, ["mic", "stop"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-microphone-record", args=["-q"])
