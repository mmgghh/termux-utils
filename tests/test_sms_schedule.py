from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from termux_toolbox.cli import app
from termux_toolbox.core import scheduled_sms
from termux_toolbox.core.errors import CommandFailed, TermuxApiNotFound

runner = CliRunner()

FIXED_NOW = 1_800_000_000.0


@pytest.fixture(autouse=True)
def isolated_state(tmp_path, monkeypatch):
    monkeypatch.setenv("TERMUX_TOOLBOX_STATE_DIR", str(tmp_path))
    monkeypatch.setattr("termux_toolbox.commands.messaging.time.time", lambda: FIXED_NOW)


def _script_path():
    return str(scheduled_sms.state_dir() / "run-due.sh")


def test_sms_schedule_requires_exactly_one_of_at_or_in():
    with patch("termux_toolbox.commands.messaging.run_termux_api") as mock_run:
        result = runner.invoke(app, ["sms", "schedule", "5551234", "hi"])
    assert result.exit_code == 1
    assert "--at" in result.output and "--in" in result.output
    mock_run.assert_not_called()
    assert scheduled_sms.list_entries() == []


def test_sms_schedule_rejects_past_time():
    with patch("termux_toolbox.commands.messaging.run_termux_api") as mock_run:
        result = runner.invoke(
            app, ["sms", "schedule", "5551234", "hi", "--at", "2020-01-01 00:00"]
        )
    assert result.exit_code == 1
    assert "future" in result.output.lower()
    mock_run.assert_not_called()
    assert scheduled_sms.list_entries() == []


def test_sms_schedule_with_in_creates_entry_and_registers_job():
    with patch("termux_toolbox.commands.messaging.run_termux_api", return_value="") as mock_run:
        result = runner.invoke(app, ["sms", "schedule", "5551234", "hello", "--in", "2h"])

    assert result.exit_code == 0
    entries = scheduled_sms.list_entries()
    assert len(entries) == 1
    assert entries[0]["number"] == "5551234"
    assert entries[0]["message"] == "hello"
    assert entries[0]["send_at_epoch"] == FIXED_NOW + 7200
    assert entries[0]["id"] in result.output

    mock_run.assert_called_once_with(
        "termux-job-scheduler",
        args=[
            "--script", _script_path(),
            "--job-id", "999001",
            "--period-ms", "900000",
            "--persisted", "true",
        ],
    )


def test_sms_schedule_with_slot_is_stored():
    with patch("termux_toolbox.commands.messaging.run_termux_api", return_value=""):
        runner.invoke(app, ["sms", "schedule", "5551234", "hi", "--in", "1h", "--slot", "1"])
    assert scheduled_sms.list_entries()[0]["slot"] == 1


def test_sms_schedule_warns_but_keeps_entry_when_job_registration_fails():
    with patch(
        "termux_toolbox.commands.messaging.run_termux_api",
        side_effect=TermuxApiNotFound("termux-job-scheduler"),
    ):
        result = runner.invoke(app, ["sms", "schedule", "5551234", "hi", "--in", "1h"])

    assert result.exit_code == 0
    assert "warning" in result.output.lower()
    assert len(scheduled_sms.list_entries()) == 1


def test_scheduled_list_renders_pending_entries_without_calling_termux_api():
    scheduled_sms.add("5551234", "hello", send_at_epoch=FIXED_NOW + 100)
    with patch("termux_toolbox.commands.messaging.run_termux_api") as mock_run:
        result = runner.invoke(app, ["sms", "scheduled", "list"])
    assert result.exit_code == 0
    assert "5551234" in result.output
    mock_run.assert_not_called()


def test_scheduled_cancel_removes_entry():
    entry_id = scheduled_sms.add("5551234", "hello", send_at_epoch=FIXED_NOW + 100)
    result = runner.invoke(app, ["sms", "scheduled", "cancel", entry_id])
    assert result.exit_code == 0
    assert scheduled_sms.list_entries() == []


def test_scheduled_cancel_unknown_id_errors():
    result = runner.invoke(app, ["sms", "scheduled", "cancel", "doesnotexist"])
    assert result.exit_code == 1
    assert "doesnotexist" in result.output


def test_scheduled_run_due_sends_and_removes_due_entry():
    scheduled_sms.add("5551234", "hello", send_at_epoch=FIXED_NOW - 10)
    with patch("termux_toolbox.commands.messaging.run_termux_api", return_value="") as mock_run:
        result = runner.invoke(app, ["sms", "scheduled", "run-due"])
    assert result.exit_code == 0
    mock_run.assert_called_once_with("termux-sms-send", args=["-n", "5551234", "hello"])
    assert scheduled_sms.list_entries() == []


def test_scheduled_run_due_ignores_future_entries():
    scheduled_sms.add("5551234", "hello", send_at_epoch=FIXED_NOW + 1000)
    with patch("termux_toolbox.commands.messaging.run_termux_api") as mock_run:
        result = runner.invoke(app, ["sms", "scheduled", "run-due"])
    assert result.exit_code == 0
    mock_run.assert_not_called()
    assert len(scheduled_sms.list_entries()) == 1


def test_scheduled_run_due_records_failure_and_requeues_entry():
    scheduled_sms.add("5551234", "hello", send_at_epoch=FIXED_NOW - 10)
    with patch(
        "termux_toolbox.commands.messaging.run_termux_api",
        side_effect=CommandFailed("termux-sms-send", "no signal", 1),
    ):
        result = runner.invoke(app, ["sms", "scheduled", "run-due"])
    assert result.exit_code == 0
    entries = scheduled_sms.list_entries()
    assert len(entries) == 1
    assert entries[0]["attempts"] == 1
    assert entries[0]["status"] == "pending"
    assert "no signal" in entries[0]["last_error"]


def test_scheduled_run_due_marks_failed_after_max_attempts():
    scheduled_sms.add("5551234", "hello", send_at_epoch=FIXED_NOW - 10)
    with patch(
        "termux_toolbox.commands.messaging.run_termux_api",
        side_effect=CommandFailed("termux-sms-send", "no signal", 1),
    ):
        for _ in range(scheduled_sms.MAX_ATTEMPTS):
            runner.invoke(app, ["sms", "scheduled", "run-due"])

    entries = scheduled_sms.list_entries()
    assert len(entries) == 1
    assert entries[0]["status"] == "failed"
    assert entries[0]["attempts"] == scheduled_sms.MAX_ATTEMPTS
