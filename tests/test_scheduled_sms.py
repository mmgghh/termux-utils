import datetime as dt

import pytest

from termux_toolbox.core import scheduled_sms


@pytest.fixture(autouse=True)
def isolated_state(tmp_path, monkeypatch):
    monkeypatch.setenv("TERMUX_TOOLBOX_STATE_DIR", str(tmp_path))


def test_parse_duration_seconds_simple_hours():
    assert scheduled_sms.parse_duration_seconds("2h") == 7200


def test_parse_duration_seconds_combo():
    assert scheduled_sms.parse_duration_seconds("1h30m") == 5400


def test_parse_duration_seconds_minutes_and_seconds():
    assert scheduled_sms.parse_duration_seconds("45m") == 2700
    assert scheduled_sms.parse_duration_seconds("90s") == 90


def test_parse_duration_seconds_invalid_raises():
    with pytest.raises(ValueError):
        scheduled_sms.parse_duration_seconds("tomorrow")


def test_parse_duration_seconds_rejects_leftover_characters():
    with pytest.raises(ValueError):
        scheduled_sms.parse_duration_seconds("2hx")


def test_resolve_target_epoch_requires_exactly_one_of_at_or_in():
    with pytest.raises(ValueError):
        scheduled_sms.resolve_target_epoch(None, None, now=1000)
    with pytest.raises(ValueError):
        scheduled_sms.resolve_target_epoch("2099-01-01 00:00", "1h", now=1000)


def test_resolve_target_epoch_with_relative_delay():
    result = scheduled_sms.resolve_target_epoch(None, "1h", now=1000)
    assert result == 1000 + 3600


def test_resolve_target_epoch_with_absolute_time():
    now = dt.datetime(2026, 1, 1).timestamp()
    result = scheduled_sms.resolve_target_epoch("2026-06-15 09:30", None, now=now)
    expected = dt.datetime(2026, 6, 15, 9, 30).timestamp()
    assert result == expected


def test_resolve_target_epoch_rejects_past_time():
    now = dt.datetime(2026, 6, 15, 9, 30).timestamp()
    with pytest.raises(ValueError):
        scheduled_sms.resolve_target_epoch("2020-01-01 00:00", None, now=now)


def test_resolve_target_epoch_invalid_at_format_raises():
    with pytest.raises(ValueError):
        scheduled_sms.resolve_target_epoch("not-a-date", None, now=1000)


def test_add_creates_pending_entry_returned_by_list_entries():
    entry_id = scheduled_sms.add("5551234", "hello", send_at_epoch=5000, slot=None, now=1000)
    entries = scheduled_sms.list_entries()
    assert len(entries) == 1
    entry = entries[0]
    assert entry["id"] == entry_id
    assert entry["number"] == "5551234"
    assert entry["message"] == "hello"
    assert entry["slot"] is None
    assert entry["send_at_epoch"] == 5000
    assert entry["created_at_epoch"] == 1000
    assert entry["attempts"] == 0
    assert entry["status"] == "pending"
    assert entry["last_error"] is None


def test_add_with_slot_is_stored():
    scheduled_sms.add("5551234", "hi", send_at_epoch=5000, slot=1)
    entry = scheduled_sms.list_entries()[0]
    assert entry["slot"] == 1


def test_add_twice_both_visible_in_list_entries():
    id1 = scheduled_sms.add("111", "a", send_at_epoch=5000)
    id2 = scheduled_sms.add("222", "b", send_at_epoch=6000)
    ids = {e["id"] for e in scheduled_sms.list_entries()}
    assert ids == {id1, id2}


def test_cancel_removes_matching_entry():
    entry_id = scheduled_sms.add("111", "a", send_at_epoch=5000)
    assert scheduled_sms.cancel(entry_id) is True
    assert scheduled_sms.list_entries() == []


def test_cancel_unknown_id_returns_false():
    assert scheduled_sms.cancel("doesnotexist") is False


def test_pop_due_returns_and_removes_only_due_pending_entries():
    due_id = scheduled_sms.add("111", "due", send_at_epoch=1000)
    future_id = scheduled_sms.add("222", "future", send_at_epoch=9999)
    due = scheduled_sms.pop_due(now=5000)
    assert [e["id"] for e in due] == [due_id]
    remaining = {e["id"] for e in scheduled_sms.list_entries()}
    assert remaining == {future_id}


def test_record_failure_increments_attempts_and_stays_pending():
    scheduled_sms.add("111", "a", send_at_epoch=1000)
    [entry] = scheduled_sms.pop_due(now=5000)
    updated = scheduled_sms.record_failure(entry, "boom")
    assert updated["attempts"] == 1
    assert updated["status"] == "pending"
    assert updated["last_error"] == "boom"
    stored = scheduled_sms.list_entries()[0]
    assert stored["attempts"] == 1


def test_record_failure_marks_failed_after_max_attempts_and_stops_being_due():
    scheduled_sms.add("111", "a", send_at_epoch=1000)
    entry = scheduled_sms.pop_due(now=5000)[0]
    for attempt in range(1, scheduled_sms.MAX_ATTEMPTS + 1):
        entry = scheduled_sms.record_failure(entry, "boom")
        if attempt < scheduled_sms.MAX_ATTEMPTS:
            [entry] = scheduled_sms.pop_due(now=5000)

    assert entry["attempts"] == scheduled_sms.MAX_ATTEMPTS
    assert entry["status"] == "failed"
    assert scheduled_sms.pop_due(now=5000) == []
    assert scheduled_sms.list_entries()[0]["status"] == "failed"
