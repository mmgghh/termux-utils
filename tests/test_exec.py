import subprocess
from unittest.mock import patch

import pytest

from termux_toolbox.core.errors import CommandFailed, PermissionDenied, TermuxApiNotFound
from termux_toolbox.core.exec import run_termux_api


def _completed(stdout="", stderr="", returncode=0):
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


def test_raises_termux_api_not_found_when_binary_missing():
    with patch("termux_toolbox.core.exec.shutil.which", return_value=None):
        with pytest.raises(TermuxApiNotFound):
            run_termux_api("termux-battery-status")


def test_returns_parsed_json_on_success():
    fake_json = '{"percentage": 87, "status": "CHARGING"}'
    with patch("termux_toolbox.core.exec.shutil.which", return_value="/usr/bin/termux-battery-status"), \
         patch("termux_toolbox.core.exec.subprocess.run", return_value=_completed(stdout=fake_json)):
        result = run_termux_api("termux-battery-status")
    assert result == {"percentage": 87, "status": "CHARGING"}


def test_returns_raw_text_when_stdout_is_not_json():
    with patch("termux_toolbox.core.exec.shutil.which", return_value="/usr/bin/termux-clipboard-get"), \
         patch("termux_toolbox.core.exec.subprocess.run", return_value=_completed(stdout="hello clipboard")):
        result = run_termux_api("termux-clipboard-get")
    assert result == "hello clipboard"


def test_returns_empty_string_when_stdout_is_blank():
    with patch("termux_toolbox.core.exec.shutil.which", return_value="/usr/bin/termux-torch"), \
         patch("termux_toolbox.core.exec.subprocess.run", return_value=_completed(stdout="")):
        result = run_termux_api("termux-torch", args=["on"])
    assert result == ""


def test_raises_permission_denied_when_stderr_mentions_permission():
    with patch("termux_toolbox.core.exec.shutil.which", return_value="/usr/bin/termux-sms-list"), \
         patch("termux_toolbox.core.exec.subprocess.run",
               return_value=_completed(stderr="Permission denied", returncode=1)):
        with pytest.raises(PermissionDenied):
            run_termux_api("termux-sms-list")


def test_raises_command_failed_on_other_nonzero_exit():
    with patch("termux_toolbox.core.exec.shutil.which", return_value="/usr/bin/termux-sms-send"), \
         patch("termux_toolbox.core.exec.subprocess.run",
               return_value=_completed(stderr="invalid number", returncode=2)):
        with pytest.raises(CommandFailed):
            run_termux_api("termux-sms-send", args=["not-a-number", "hi"])


def test_raises_command_failed_on_timeout():
    with patch("termux_toolbox.core.exec.shutil.which", return_value="/usr/bin/termux-location"), \
         patch("termux_toolbox.core.exec.subprocess.run",
               side_effect=subprocess.TimeoutExpired(cmd="termux-location", timeout=15.0)):
        with pytest.raises(CommandFailed):
            run_termux_api("termux-location")


def test_passes_args_and_input_data_through_to_subprocess():
    with patch("termux_toolbox.core.exec.shutil.which", return_value="/usr/bin/termux-sms-send"), \
         patch("termux_toolbox.core.exec.subprocess.run", return_value=_completed()) as mock_run:
        run_termux_api("termux-sms-send", args=["-n", "555", "hi"], input_data="stdin-data")
    mock_run.assert_called_once_with(
        ["termux-sms-send", "-n", "555", "hi"],
        input="stdin-data",
        capture_output=True,
        text=True,
        timeout=15.0,
    )
