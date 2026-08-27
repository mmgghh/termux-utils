import contextlib
import datetime as dt
import fcntl
import json
import os
import re
import time
import uuid
from pathlib import Path

MAX_ATTEMPTS = 3

_DURATION_UNITS = {"d": 86400, "h": 3600, "m": 60, "s": 1}
_DURATION_TOKEN = re.compile(r"(\d+)([dhms])")

_AT_FORMATS = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M")


def state_dir() -> Path:
    override = os.environ.get("TERMUX_TOOLBOX_STATE_DIR")
    base = Path(override) if override else Path(
        os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local" / "state"))
    ) / "termux-toolbox"
    base.mkdir(parents=True, exist_ok=True)
    return base


def _state_path() -> Path:
    return state_dir() / "scheduled_sms.json"


def parse_duration_seconds(text: str) -> int:
    total = 0
    pos = 0
    for match in _DURATION_TOKEN.finditer(text):
        if match.start() != pos:
            raise ValueError(f"invalid duration {text!r}")
        total += int(match.group(1)) * _DURATION_UNITS[match.group(2)]
        pos = match.end()
    if pos == 0 or pos != len(text):
        raise ValueError(f"invalid duration {text!r}")
    return total


def _parse_at(at_text: str) -> float:
    for fmt in _AT_FORMATS:
        try:
            return dt.datetime.strptime(at_text, fmt).timestamp()
        except ValueError:
            continue
    raise ValueError(f"invalid --at value {at_text!r} (expected 'YYYY-MM-DD HH:MM')")


def resolve_target_epoch(at: str | None, in_: str | None, now: float) -> float:
    if (at is None) == (in_ is None):
        raise ValueError("provide exactly one of --at or --in")

    target = _parse_at(at) if at is not None else now + parse_duration_seconds(in_)

    if target <= now:
        raise ValueError("--at/--in must resolve to a future time")
    return target


@contextlib.contextmanager
def _locked_entries():
    path = _state_path()
    lock_path = path.with_suffix(path.suffix + ".lock")
    with open(lock_path, "w") as lock_file:
        fcntl.flock(lock_file, fcntl.LOCK_EX)
        try:
            if path.exists() and path.read_text().strip():
                entries = json.loads(path.read_text())
            else:
                entries = []
            yield entries
            path.write_text(json.dumps(entries, indent=2))
        finally:
            fcntl.flock(lock_file, fcntl.LOCK_UN)


def add(
    number: str,
    message: str,
    send_at_epoch: float,
    slot: int | None = None,
    now: float | None = None,
) -> str:
    entry_id = uuid.uuid4().hex[:8]
    with _locked_entries() as entries:
        entries.append(
            {
                "id": entry_id,
                "number": number,
                "message": message,
                "slot": slot,
                "send_at_epoch": send_at_epoch,
                "created_at_epoch": now if now is not None else time.time(),
                "attempts": 0,
                "status": "pending",
                "last_error": None,
            }
        )
    return entry_id


def list_entries() -> list[dict]:
    with _locked_entries() as entries:
        return list(entries)


def cancel(entry_id: str) -> bool:
    with _locked_entries() as entries:
        for index, entry in enumerate(entries):
            if entry["id"] == entry_id:
                del entries[index]
                return True
        return False


def pop_due(now: float) -> list[dict]:
    with _locked_entries() as entries:
        due = [e for e in entries if e["status"] == "pending" and e["send_at_epoch"] <= now]
        due_ids = {e["id"] for e in due}
        entries[:] = [e for e in entries if e["id"] not in due_ids]
        return due


def record_failure(entry: dict, error: str) -> dict:
    updated = dict(entry)
    updated["attempts"] += 1
    updated["last_error"] = error
    if updated["attempts"] >= MAX_ATTEMPTS:
        updated["status"] = "failed"
    with _locked_entries() as entries:
        entries.append(updated)
    return updated
